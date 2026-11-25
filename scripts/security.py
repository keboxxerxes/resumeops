"""Fail-closed IaC and per-job workflow capability checks, complementing scanners."""
import importlib.util,json,pathlib,re,sys,yaml

class WorkflowLoader(yaml.SafeLoader):
    pass
WorkflowLoader.yaml_implicit_resolvers={key:[rule for rule in rules if rule[0]!='tag:yaml.org,2002:bool'] for key,rules in yaml.SafeLoader.yaml_implicit_resolvers.items()}
WorkflowLoader.add_implicit_resolver('tag:yaml.org,2002:bool',re.compile(r'^(?:true|false)$',re.I),list('tTfF'))
def unique_mapping(loader,node,deep=False):
    result={}
    for key_node,value_node in node.value:
        key=loader.construct_object(key_node,deep=deep)
        if not isinstance(key,str) or key in result:raise yaml.YAMLError('Non-string or duplicate workflow key')
        result[key]=loader.construct_object(value_node,deep=deep)
    return result
WorkflowLoader.add_constructor('tag:yaml.org,2002:map',unique_mapping)

def load_workflow(text):
    if any(isinstance(token,(yaml.tokens.AliasToken,yaml.tokens.AnchorToken)) for token in yaml.scan(text)):
        raise yaml.YAMLError('Workflow aliases are not part of the reviewed capabilities')
    return yaml.load(text,Loader=WorkflowLoader)

def same(actual,expected):
    if type(actual) is not type(expected):return False
    if isinstance(actual,dict):return actual.keys()==expected.keys() and all(same(actual[key],expected[key]) for key in actual)
    if isinstance(actual,list):return len(actual)==len(expected) and all(same(a,b) for a,b in zip(actual,expected))
    return actual==expected

WORKFLOW_NAMES={'ci.yml','preflight.yml','content.yml','drift.yml','infrastructure.yml'}
READ={'contents':'read'}
OIDC={'contents':'read','id-token':'write'}
TOKEN={'GH_PROTECTION_TOKEN':'${{ secrets.GH_PROTECTION_TOKEN }}'}
NODE={'node-version':'24.22.2'}
TF={'terraform_version':'1.17.2','terraform_wrapper':False}
MANUAL="github.event_name == 'workflow_dispatch' && github.ref == 'refs/heads/main'"
OPERATIONAL=MANUAL+" && vars.ALLOW_AWS_OPERATIONS == 'true'"
DRIFT_CONDITION="(github.event_name == 'workflow_dispatch' || github.event_name == 'schedule') && github.ref == 'refs/heads/main' && vars.ALLOW_AWS_OPERATIONS == 'true'"
OPS_ENV={'ALLOW_AWS_OPERATIONS':'${{ vars.ALLOW_AWS_OPERATIONS }}','TF_IN_AUTOMATION':'true','TF_INPUT':'false','TF_VAR_site_bucket':'${{ secrets.SITE_BUCKET }}','TF_VAR_region':'${{ vars.AWS_REGION }}'}
INIT_ENV={'STATE_BUCKET':'${{ secrets.STATE_BUCKET }}','AWS_REGION':'${{ vars.AWS_REGION }}'}
CRYPTO_ENV={'PLAN_ENCRYPTION_KEY':'${{ secrets.PLAN_ENCRYPTION_KEY }}'}
# Reviewed command capabilities. Exact bodies prevent a safe marker from masking an extra command.
PROGRAMS={}
PROGRAMS['INSTALL']="""
python3 scripts/install-tools.py
python3 -m venv .tools/venv
.tools/venv/bin/pip install -r requirements-tools.txt
npm ci --ignore-scripts
npx playwright install --with-deps chromium
""".strip()
PROGRAMS['CHECKS']="""
.tools/venv/bin/python scripts/run-checks.py
""".strip()
PROGRAMS['INIT']="""
set -euo pipefail
terraform -chdir=infra/site init -input=false -lockfile=readonly -backend-config="bucket=$STATE_BUCKET" -backend-config="region=$AWS_REGION" -backend-config='key=site/production/terraform.tfstate' -backend-config=encrypt=true -backend-config=use_lockfile=true > /dev/null 2>&1
""".strip()
PROGRAMS['DRIFT']="""
set -uo pipefail
if terraform -chdir=infra/site plan -input=false -lock-timeout=5m -detailed-exitcode -no-color > /dev/null 2>&1; then result=0; else result=$?; fi
node scripts/drift.mjs "$result" | tee -a "$GITHUB_STEP_SUMMARY"
if [ "$result" = 2 ]; then echo 'Drift requires operator review' >&2; exit 1; fi
exit "$result"
""".strip()
PROGRAMS['PLAN']="""
set -euo pipefail
umask 077
node scripts/confirm.mjs
trap 'rm -f infra/site/candidate.tfplan' EXIT
args=()
if [ "$OPERATION" = destroy ]; then args+=(-destroy); fi
terraform -chdir=infra/site plan -input=false -lock-timeout=5m -no-color "${args[@]}" -out=candidate.tfplan > /dev/null 2>&1
mkdir -p .local/handoff
node scripts/plan-crypto.mjs seal infra/site/candidate.tfplan .local/handoff/candidate.enc
""".strip()
PROGRAMS['APPLY']="""
set -euo pipefail
umask 077
node scripts/confirm.mjs
trap 'rm -f infra/site/candidate.tfplan .local/handoff/candidate.enc' EXIT
node scripts/plan-crypto.mjs open .local/handoff/candidate.enc infra/site/candidate.tfplan
terraform -chdir=infra/site apply -input=false -lock-timeout=5m -no-color candidate.tfplan > /dev/null 2>&1
echo 'Exact reviewed site plan applied; bootstrap retained.'
""".strip()
PROGRAMS['CONTENT_PREP']="""
set -euo pipefail
CONTENT_SHA="${REQUESTED_REVISION:-$GITHUB_SHA}"
export CONTENT_SHA
node scripts/content.mjs
echo "CONTENT_SHA=$CONTENT_SHA" >> "$GITHUB_ENV"
""".strip()
PROGRAMS['CONTENT_DEPLOY']="""
node scripts/deploy-content.mjs
node scripts/smoke.mjs
""".strip()
PROGRAMS['PREFLIGHT']="""
node --input-type=module -e "import { preflight } from './scripts/gate.mjs'; try { await preflight(); console.log('Read-only protection preflight passed'); } catch { console.error('Read-only protection preflight failed'); process.exit(1); }"
""".strip()


def inspect_workflow(path,text):
    errors=[]
    def require(ok,message):
        if not ok:errors.append(message)
    try:
        workflow=load_workflow(text)
        if not isinstance(workflow,dict):return ['Malformed workflow mapping']
        name=pathlib.PurePath(path).name
        require(name in WORKFLOW_NAMES,'Unapproved workflow role')
        require(not set(workflow)-{'name','on','permissions','concurrency','env','jobs'},'Unsupported workflow-level capability')
        require(same(workflow.get('permissions'),READ),'Workflow permissions must be contents read only')
        events=workflow.get('on')
        if isinstance(events,str):events={events:None}
        if not isinstance(events,dict):return errors+['Explicit workflow event map required']
        expected_events={'push','pull_request','workflow_dispatch'} if name=='ci.yml' else {'schedule','workflow_dispatch'} if name=='drift.yml' else {'workflow_dispatch'}
        require(set(events)==expected_events,'Workflow events violate role boundaries')
        if name=='ci.yml':
            require(same(events.get('push'),{'branches':['**']}) and events.get('pull_request') is None and events.get('workflow_dispatch') is None,'CI must retain credential-free branch/PR/manual verification without tags')
        elif name=='drift.yml':require(same(events.get('schedule'),[{'cron':'17 13 * * 1'}]) and events.get('workflow_dispatch') is None,'Drift must retain approved read-only schedule/manual events')
        elif name=='preflight.yml':require(events.get('workflow_dispatch') is None,'Preflight must be manual without caller-selected inputs')
        if name=='infrastructure.yml':
            inputs=events.get('workflow_dispatch',{}).get('inputs',{})
            require(set(inputs)=={'operation','confirmation'} and same(inputs.get('operation'),{'type':'choice','options':['apply','destroy'],'required':True}) and same(inputs.get('confirmation'),{'type':'string','description':'For destroy type: DESTROY production SITE ONLY','required':False}),'Infrastructure operation/typed-confirmation input contract changed')
        if name=='content.yml':
            inputs=events.get('workflow_dispatch',{}).get('inputs',{})
            require(set(inputs)=={'revision'} and same(inputs.get('revision'),{'type':'string','description':'Exact approved main-ancestor content SHA; blank uses current main','required':False}),'Content revision input contract changed')
        operational=name in {'content.yml','drift.yml','infrastructure.yml'}
        require(same(workflow.get('concurrency'),{'group':'resumeops-production','cancel-in-progress':False} if operational else None),'State/site operations require common noncanceling serialization')
        require(same(workflow.get('env'),{'ALLOW_AWS_OPERATIONS':'${{ vars.ALLOW_AWS_OPERATIONS }}'} if name=='content.yml' else OPS_ENV if operational else None),'Workflow environment exceeds its role')
        jobs=workflow.get('jobs')
        expected_jobs={'verify'} if name=='ci.yml' else {'preflight'} if name=='preflight.yml' else {'plan','apply'} if name=='infrastructure.yml' else {name[:-4]}
        if not isinstance(jobs,dict):return errors+['Explicit jobs required']
        require(set(jobs)==expected_jobs,'Unexpected workflow jobs')
        for job_name,job in jobs.items():
            if not isinstance(job,dict):errors.append('Malformed job');continue
            require(not set(job)-{'if','runs-on','timeout-minutes','environment','permissions','env','needs','steps'},'Unsupported job capability')
            require(job.get('runs-on')=='ubuntu-24.04','Jobs require the reviewed Ubuntu runner')
            require(type(job.get('timeout-minutes')) is int and 0<job['timeout-minutes']<=60,'Bounded job timeout required')
            require(job.get('if')==(DRIFT_CONDITION if name=='drift.yml' else OPERATIONAL if operational else MANUAL if name=='preflight.yml' else None),'Job must independently enforce its allowed event/main/activation condition')
            require(same(job.get('permissions'),OIDC if operational else READ if name=='preflight.yml' else None),'Job token permissions exceed its role')
            environment='production-'+job_name if operational else 'production-plan' if name=='preflight.yml' else None
            require(job.get('environment')==environment,'Protected environment does not match job role')
            require(job.get('needs')==('plan' if name=='infrastructure.yml' and job_name=='apply' else None),'Apply must follow the protected fresh-plan job')
            expected_env={'REQUESTED_REVISION':'${{ inputs.revision }}','SITE_BUCKET':'${{ secrets.SITE_BUCKET }}','CF_DISTRIBUTION_ID':'${{ secrets.CF_DISTRIBUTION_ID }}','SITE_HOST':'${{ secrets.SITE_HOST }}'} if name=='content.yml' else {'OPERATION':'${{ inputs.operation }}','CONFIRMATION':'${{ inputs.confirmation }}'} if name=='infrastructure.yml' else None
            require(same(job.get('env'),expected_env),'Job environment exceeds its role; tokens belong only to the protection step')
            gate='node scripts/gate.mjs '+('production-plan production-apply' if name=='infrastructure.yml' else 'production-'+job_name)
            expected=[('actions/checkout',None),('actions/setup-node',None)]
            if name=='ci.yml':expected += [('hashicorp/setup-terraform',None),(None,PROGRAMS['INSTALL']),(None,PROGRAMS['CHECKS']),('actions/upload-artifact',None)]
            elif name=='preflight.yml':expected += [(None,PROGRAMS['PREFLIGHT'])]
            else:
                expected += [(None,gate)]
                if name!='content.yml':expected += [('hashicorp/setup-terraform',None)]
                expected += [('aws-actions/configure-aws-credentials',None)]
                if name=='content.yml':expected += [(None,PROGRAMS['CONTENT_PREP']),(None,PROGRAMS['CONTENT_DEPLOY'])]
                elif name=='drift.yml':expected += [(None,PROGRAMS['INIT']),(None,PROGRAMS['DRIFT'])]
                elif job_name=='plan':expected += [(None,PROGRAMS['INIT']),(None,PROGRAMS['PLAN']),('actions/upload-artifact',None)]
                else:expected += [(None,PROGRAMS['INIT']),('actions/download-artifact',None),(None,PROGRAMS['APPLY'])]
            steps=job.get('steps')
            if not isinstance(steps,list):errors.append('Explicit job steps required');continue
            require(len(steps)==len(expected),'Unexpected/missing job steps or capability order')
            for step,(action,command) in zip(steps,expected):
                if not isinstance(step,dict):errors.append('Malformed step');continue
                require(not set(step)-{'name','uses','with','run','env','if'},'Unsupported step capability such as alternate shell or continued errors')
                artifact=name=='ci.yml' and action=='actions/upload-artifact'
                require(step.get('if')==('always()' if artifact else None),'A required step may not be skipped or failures bypassed')
                expected_step_env=TOKEN if command==gate or command==PROGRAMS['PREFLIGHT'] else INIT_ENV if command==PROGRAMS['INIT'] else CRYPTO_ENV if command in {PROGRAMS['PLAN'],PROGRAMS['APPLY']} else {'AWS_EC2_METADATA_DISABLED':'true','CHECKPOINT_DISABLE':'1','CKV_ENABLE_EXTERNAL_MODULES':'false'} if name=='ci.yml' and command==PROGRAMS['CHECKS'] else None
                require(same(step.get('env'),expected_step_env),'Step secrets/environment exceed capability')
                if action:
                    uses=step.get('uses','')
                    pins=json.loads((pathlib.Path(__file__).resolve().parents[1]/'requirements/action-pins.json').read_text())
                    require(uses==action+'@'+pins[action]['sha'],'Unexpected or unpinned action in capability order')
                    require('run' not in step,'Actions cannot hide an additional run command')
                    expected_with={'persist-credentials':False} if action=='actions/checkout' else NODE if action=='actions/setup-node' else TF if action=='hashicorp/setup-terraform' else None
                    if action=='actions/checkout' and name!='ci.yml':expected_with={**expected_with,'ref':'${{ github.sha }}',**({'fetch-depth':0} if name=='content.yml' else {})}
                    if action=='aws-actions/configure-aws-credentials':expected_with={'role-to-assume':'${{ secrets.'+('CONTENT_ROLE_ARN' if name=='content.yml' else 'APPLY_ROLE_ARN' if job_name=='apply' else 'PLAN_ROLE_ARN')+' }}','aws-region':'${{ vars.AWS_REGION }}','mask-aws-account-id':True,'role-duration-seconds':3600}
                    if action=='actions/upload-artifact':expected_with={'name':'verification-evidence','path':'.local/verification/results.json','include-hidden-files':True,'if-no-files-found':'warn','retention-days':3} if name=='ci.yml' else {'name':'encrypted-plan','path':'.local/handoff/candidate.enc','retention-days':1,'include-hidden-files':True,'if-no-files-found':'error'}
                    if action=='actions/download-artifact':expected_with={'name':'encrypted-plan','path':'.local/handoff'}
                    require(same(step.get('with'),expected_with),'Action inputs exceed approved capability; only ciphertext plans may be transferred')
                else:
                    require(step.get('run','').strip()==command and 'uses' not in step and 'with' not in step,'Unapproved command or protection/OIDC/plan order')
        return errors
    except (yaml.YAMLError,TypeError,KeyError,ValueError,AttributeError):
        return errors+['Malformed or ambiguous workflow structure']


def inspect(files):
    errors=[]
    for path,text in files.items():
        if path.endswith(('.yml','.yaml')):
            errors += [path+': '+error for error in inspect_workflow(path,text)]
            if 'pull_request_target' in text:errors.append('Unsafe privileged PR trigger')
        if path.endswith('.tf'):
            for setting in ['block_public_acls','block_public_policy','ignore_public_acls','restrict_public_buckets']:
                if re.search(r'\b'+setting+r'\s*=\s*false',text): errors.append('public S3 control disabled')
            if 'viewer_protocol_policy' in text and 'redirect-to-https' not in text: errors.append('HTTPS redirect missing')
            if re.search(r'"token.actions.githubusercontent.com:sub"\s*=\s*"[^"\n]*\*',text): errors.append('wildcard OIDC trust')
            if re.search(r'Action\s*=\s*\[?\s*"(?:iam:\*|sts:AssumeRole|\*)"',text): errors.append('runtime escalation')
    return errors


if __name__=='__main__':
    root=pathlib.Path.cwd()
    spec=importlib.util.spec_from_file_location('public_source',root/'scripts/check-repository.py')
    source=importlib.util.module_from_spec(spec);spec.loader.exec_module(source)
    intended=source.source_files(root)
    if any(source.private_payload(path) for path in intended):
        print('Private/ignored payload in intended source; no contents inspected');raise SystemExit(1)
    active={path for path in intended if path.startswith('.github/workflows/') and path.endswith(('.yml','.yaml'))}
    if {pathlib.PurePosixPath(path).name for path in active}!=WORKFLOW_NAMES or len(active)!=5:
        print('Exactly the five reviewed CI/preflight/operational workflows are required');raise SystemExit(1)
    files={path:(root/path).read_text(encoding='utf-8') for path in intended if path.endswith('.tf') or path in active}
    failures=inspect(files)
    if failures:print('\n'.join(sorted(set(failures))));raise SystemExit(1)
    print('PASS: intended-source IaC and five structurally isolated workflow roles')
