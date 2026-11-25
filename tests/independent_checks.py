"""Independent reviewer invariants and real unsafe-workflow scanner checks.
No AWS calls; fixtures are ephemeral ignored local files.
"""
import json,pathlib,re,subprocess,sys,tempfile


def action_tag_fixtures():
    """Exercise the real resolver with process fixtures; no network or credentials."""
    import importlib.util,os
    from unittest import mock
    module_path=pathlib.Path(__file__).resolve().parents[1]/'scripts/verify-provenance.py'
    specification=importlib.util.spec_from_file_location('upstream_provenance',module_path)
    module=importlib.util.module_from_spec(specification)
    with mock.patch('urllib.request.urlopen',side_effect=AssertionError('Import must not use network')):
        specification.loader.exec_module(module)
    expected='a'*40;tag='v1.2.3';literal='refs/tags/'+tag
    valid=expected+'\t'+literal+'\n'
    observed=[]
    def process(output=valid,code=0):
        def run(command,**kwargs):
            observed.append((command,kwargs))
            assert command[-3:]==['https://github.com/actions/checkout.git',literal,literal+'^{}']
            assert '--refs' not in command and '--tags' in command and '--exit-code' in command
            assert kwargs['shell'] is False and kwargs['timeout']==60
            assert kwargs['env']['GIT_TERMINAL_PROMPT']=='0' and kwargs['env']['GIT_CONFIG_NOSYSTEM']=='1'
            assert kwargs['env']['GIT_CONFIG_GLOBAL']==os.devnull and kwargs['env']['GIT_CONFIG_COUNT']=='0'
            assert kwargs['env']['HOME']==kwargs['cwd'] and kwargs['env']['USERPROFILE']==kwargs['cwd']
            assert 'GH_TOKEN' not in kwargs['env'] and 'GITHUB_TOKEN' not in kwargs['env'] and 'GIT_SSL_NO_VERIFY' not in kwargs['env']
            assert 'credential.helper=' in command and 'http.extraHeader=' in command
            return subprocess.CompletedProcess(command,code,output,'')
        return run
    def rejected(output=valid,code=0):
        with mock.patch.object(module.subprocess,'run',side_effect=process(output,code)):
            try:module.verify_action_tag('actions/checkout',tag,expected)
            except (ValueError,RuntimeError):return
            raise AssertionError('Unsafe upstream lookup fixture was accepted')
    with mock.patch.dict(os.environ,{'GH_TOKEN':'dummy-not-for-child','GITHUB_TOKEN':'dummy-not-for-child','GIT_SSL_NO_VERIFY':'1'}):
        for output in [valid,'b'*40+'\t'+literal+'\n'+expected+'\t'+literal+'^{}\n']:
            with mock.patch.object(module.subprocess,'run',side_effect=process(output)):
                module.verify_action_tag('actions/checkout',tag,expected)
    for output in ['',expected+'\t'+literal+'^{}\n',valid+valid,valid+expected+'\trefs/heads/main\n',valid+expected+'\trefs/tags/v9.9.9\n','bad\t'+literal+'\n','A'*40+'\t'+literal+'\n',expected+' '+literal+'\n','b'*40+'\t'+literal+'\n',valid+'b'*40+'\t'+literal+'^{}\n',valid+'\n']:
        rejected(output)
    for code in [1,2,128]:rejected(code=code)
    for error in [subprocess.TimeoutExpired('git',60),OSError('Dummy missing Git')]:
        with mock.patch.object(module.subprocess,'run',side_effect=error):
            try:module.verify_action_tag('actions/checkout',tag,expected)
            except RuntimeError:pass
            else:raise AssertionError('Failed process accepted')
    for repo,release,sha in [('https://github.com/actions/checkout',tag,expected),('actions/checkout;id',tag,expected),('actions/checkout','--help',expected),('actions/checkout','v1.2.3*',expected),('actions/checkout','v1.2.3^{}',expected),('actions/checkout','v1.2.3\nother',expected),('actions/checkout',tag,'a'*39),('actions/checkout',tag,'A'*40)]:
        with mock.patch.object(module.subprocess,'run',side_effect=AssertionError('Invalid input must not launch Git')):
            try:module.verify_action_tag(repo,release,sha)
            except ValueError:pass
            else:raise AssertionError('Invalid input accepted')
    print('PASS: anonymous Git action tag lightweight/peeled resolution and malformed/missing/duplicate/wrong/process/input negatives')


def workflow_activation_fixtures():
    """Mutate real valid workflow roles; never execute the fixture commands."""
    import copy,importlib.util,yaml
    root=pathlib.Path(__file__).resolve().parents[1]
    specification=importlib.util.spec_from_file_location('workflow_security',root/'scripts/security.py')
    policy=importlib.util.module_from_spec(specification);specification.loader.exec_module(policy)
    baseline={name:policy.load_workflow((root/'.github/workflows'/name).read_text()) for name in policy.WORKFLOW_NAMES}
    for name,document in baseline.items():
        assert not policy.inspect_workflow('.github/workflows/'+name,yaml.safe_dump(document,sort_keys=False)), 'Valid role rejected: '+name
    count=0
    def reject(name,path,value):
        nonlocal count
        changed=copy.deepcopy(baseline[name]);target=changed
        for key in path[:-1]:target=target[key]
        target[path[-1]]=value
        assert policy.inspect_workflow('.github/workflows/'+name,yaml.safe_dump(changed,sort_keys=False)), 'Unsafe capability accepted: '+name+' '+str(path)
        count+=1
    reject('ci.yml',['jobs','verify','permissions'],{'contents':'read','id-token':'write'})
    reject('ci.yml',['env'],{'GH_PROTECTION_TOKEN':'${{ secrets.GH_PROTECTION_TOKEN }}'})
    reject('ci.yml',['jobs','verify','steps',4,'run'],baseline['ci.yml']['jobs']['verify']['steps'][4]['run']+'\naws iam list-users')
    reject('ci.yml',['jobs','extra'],{'runs-on':'ubuntu-24.04','steps':[{'run':'aws sts get-caller-identity'}]})
    for name,key in [('content.yml','content'),('drift.yml','drift'),('infrastructure.yml','plan'),('infrastructure.yml','apply')]:
        job=['jobs',key]
        reject(name,['on'],{'pull_request':None})
        reject(name,job+['if'],"github.ref == 'refs/heads/main' || vars.ALLOW_AWS_OPERATIONS == 'true'")
        reject(name,job+['environment'],'production-plan' if key!='plan' else 'production-apply')
        reject(name,job+['steps',2,'if'],False)
        reject(name,job+['steps',2,'continue-on-error'],True)
        reject(name,job+['steps',2,'run'],"echo 'node scripts/gate.mjs is only a decoy'")
        reject(name,job+['steps',2,'run'],policy.PROGRAMS['PREFLIGHT'])
        reject(name,job+['env'],{'GH_PROTECTION_TOKEN':'${{ secrets.GH_PROTECTION_TOKEN }}'})
        aws_index=3 if name=='content.yml' else 4
        reject(name,job+['steps',aws_index,'if'],'always()')
        reject(name,job+['steps',aws_index,'continue-on-error'],True)
        credential=copy.deepcopy(baseline[name]['jobs'][key]['steps'][aws_index]['with']);credential['aws-access-key-id']='${{ secrets.AWS_ACCESS_KEY_ID }}'
        reject(name,job+['steps',aws_index,'with'],credential)
        reordered=copy.deepcopy(baseline[name]['jobs'][key]['steps']);reordered[2],reordered[aws_index]=reordered[aws_index],reordered[2]
        reject(name,job+['steps'],reordered)
    pre=['jobs','preflight']
    reject('preflight.yml',['on'],{'pull_request':None})
    reject('preflight.yml',pre+['permissions'],{'contents':'read','id-token':'write'})
    reject('preflight.yml',pre+['environment'],'production-content')
    reject('preflight.yml',pre+['if'],policy.OPERATIONAL)
    reject('preflight.yml',['env'],policy.TOKEN)
    reject('preflight.yml',pre+['env'],policy.TOKEN)
    reject('preflight.yml',pre+['steps',0,'env'],policy.TOKEN)
    reject('preflight.yml',pre+['steps',2,'run'],policy.PROGRAMS['PREFLIGHT']+'; curl https://example.invalid')
    reject('preflight.yml',pre+['steps'],baseline['preflight.yml']['jobs']['preflight']['steps']+[{'run':'terraform init'}])
    reject('preflight.yml',pre+['steps'],baseline['preflight.yml']['jobs']['preflight']['steps']+[baseline['ci.yml']['jobs']['verify']['steps'][-1]])
    reject('preflight.yml',pre+['steps',2,'env'],{'GH_PROTECTION_TOKEN':'${{ secrets.GH_PROTECTION_TOKEN }}','STATE_BUCKET':'${{ secrets.STATE_BUCKET }}'})
    reject('infrastructure.yml',['on'],{'schedule':[{'cron':'* * * * *'}],'workflow_dispatch':None})
    reject('infrastructure.yml',['jobs','apply','needs'],'unreviewed')
    reject('infrastructure.yml',['jobs','plan','steps',7,'with','path'],'infra/site/candidate.tfplan')
    reject('infrastructure.yml',['jobs','plan','steps',7,'with','retention-days'],True)
    reject('infrastructure.yml',['jobs','apply','steps',6,'with','name'],'other-plan')
    reject('infrastructure.yml',['on','workflow_dispatch','inputs','confirmation','default'],'DESTROY production SITE ONLY')
    reject('infrastructure.yml',['jobs','apply','steps',7,'run'],'terraform -chdir=infra/site apply -auto-approve')
    reject('drift.yml',['jobs','drift','steps',6,'run'],'terraform -chdir=infra/site apply -auto-approve')
    raw=(root/'.github/workflows/preflight.yml').read_text()
    assert policy.inspect_workflow('.github/workflows/preflight.yml',raw+'\npermissions: write-all\n'), 'Duplicate YAML key accepted'
    count+=1
    print('PASS: five valid workflow roles and',count,'semantic trigger/secret/token/order/approval/artifact negative mutations')


def immutable_oidc_source_fixtures():
    import importlib.util
    root=pathlib.Path(__file__).resolve().parents[1]
    specification=importlib.util.spec_from_file_location('immutable_policy_guard',root/'scripts/security.py')
    policy=importlib.util.module_from_spec(specification);specification.loader.exec_module(policy)
    main=(root/'infra/bootstrap/main.tf').read_text();variables=(root/'infra/bootstrap/variables.tf').read_text()
    assert not policy.immutable_trust_errors(main,variables)
    for changed in [main.replace('@${var.repository_owner_id}',''),main.replace('@${var.repository_id}',''),main.replace('repo:${local.oidc_repository}:environment:${env}','repo:${var.repository}:environment:${env}')]:
        assert policy.immutable_trust_errors(changed,variables)
    for name in ['repository_owner_id','repository_id']:
        block=policy.immutable_id_block(variables,name)
        for changed in [block.replace('nullable    = false','nullable    = true'),block.replace('  type        = string','  default     = "1"\n  type        = string'),block.replace('^[1-9][0-9]*$','^[0-9]+$')]:
            assert policy.immutable_trust_errors(main,variables.replace(block.strip(),changed.strip()))
    print('PASS: immutable subject source invariants and nine legacy/missing-ID/default/validation mutations')


def rendered_immutable_oidc_tests():
    """Evaluate actual trust JSON in an isolated public-source, all-mocked plan suite."""
    import importlib.util,os,shutil
    root=pathlib.Path.cwd()
    (root/'.local/reviewer').mkdir(parents=True,exist_ok=True)
    test_path=pathlib.Path('infra/bootstrap/tests/immutable_oidc.tftest.hcl')
    public=['infra/bootstrap/main.tf','infra/bootstrap/variables.tf','infra/bootstrap/iam.tf','infra/bootstrap/versions.tf','infra/bootstrap/.terraform.lock.hcl',test_path.as_posix()]
    tracked=set(subprocess.run(['git','ls-files','-z','--',*public],check=True,capture_output=True,text=True).stdout.split('\0'))
    assert set(public)<=tracked, 'Mock runner may copy only the explicitly tracked public fixture inventory'
    suite=hcl2.loads(test_path.read_text())
    assert len(suite.get('mock_provider',[]))==1 and set(suite['mock_provider'][0])=={'aws'} and 'alias' not in suite['mock_provider'][0]['aws']
    assert not suite.get('provider') and not suite.get('override_module'), 'No live provider or external module in mocked trust tests'
    runs={name:body for item in suite['run'] for name,body in item.items()}
    assert len(runs)==31 and all(body.get('command') in ['plan','${plan}'] and not body.get('providers') and not body.get('module') for body in runs.values())
    assert all(body.get('assert') for name,body in runs.items() if '_invalid_' not in name), 'Rendered trust assertions may not be removed'
    environment={key:value for key,value in os.environ.items() if not key.startswith(('AWS_','TF_'))}
    environment.update(AWS_EC2_METADATA_DISABLED='true',TF_INPUT='false',CHECKPOINT_DISABLE='1')
    terraform=environment.get('RESUMEOPS_TERRAFORM','terraform')
    specification=importlib.util.spec_from_file_location('immutable_input_guard',root/'scripts/security.py')
    policy=importlib.util.module_from_spec(specification);specification.loader.exec_module(policy)
    def execute(command,cwd):
        print('MOCK CHECK:', ' '.join(command).replace(str(cwd),'<isolated-public-fixture>'),flush=True)
        result=subprocess.run(command,cwd=cwd,env=environment,capture_output=True,text=True,timeout=240)
        print('MOCK EXIT:',result.returncode,flush=True)
        return result
    def events(result):
        records=[json.loads(line) for line in result.stdout.splitlines() if line.strip()]
        return records
    with tempfile.TemporaryDirectory(prefix='immutable-oidc-',dir=root/'.local/reviewer') as location:
        directory=pathlib.Path(location)
        (directory/'empty.tfrc').write_text('')
        environment.update(AWS_CONFIG_FILE=str(directory/'no-aws-config'),AWS_SHARED_CREDENTIALS_FILE=str(directory/'no-aws-credentials'),TF_CLI_CONFIG_FILE=str(directory/'empty.tfrc'))
        for name in public:
            target=directory/pathlib.Path(name).relative_to('infra/bootstrap');target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(root/name,target)
        lock=(directory/'.terraform.lock.hcl').read_bytes()
        init=execute([terraform,'init','-backend=false','-input=false','-lockfile=readonly','-no-color'],directory)
        if init.returncode!=0:print(init.stdout,init.stderr)
        assert init.returncode==0, 'Mock fixture readonly provider initialization failed'
        result=execute([terraform,'test','-json','-no-color','-filter='+str(test_path.relative_to('infra/bootstrap'))],directory)
        records=events(result);summaries=[r['test_summary'] for r in records if r.get('type')=='test_summary']
        completed=[r['test_run'] for r in records if r.get('type')=='test_run' and r['test_run'].get('progress')=='complete']
        if result.returncode!=0:
            for record in records:
                diagnostic=record.get('diagnostic')
                if diagnostic:print('MOCK DIAGNOSTIC:',diagnostic.get('summary',''),diagnostic.get('detail',''))
        for record in completed:print('MOCK RUN:',record.get('run'),record.get('status'))
        print('MOCK SUMMARY:',json.dumps(summaries))
        assert result.returncode==0 and len(summaries)==1 and summaries[0]=={'status':'pass','passed':31,'failed':0,'errored':0,'skipped':0}, 'Rendered mocked trust test did not fully pass'
        assert len(completed)==31 and {r['run'] for r in completed}==set(runs) and all(r.get('status')=='pass' for r in completed), 'No mocked run may be skipped'
        assert (directory/'.terraform.lock.hcl').read_bytes()==lock, 'Mock initialization must not mutate the committed lock'
        print('MOCK LOCK: unchanged')
        variable_source=(root/'infra/bootstrap/variables.tf').read_text()
        declarations=''.join(policy.immutable_id_block(variable_source,name) for name in ['repository_owner_id','repository_id'])
        for invalid in ['repository_owner_id','repository_id']:
            for mode in ['null','missing']:
                isolated=directory/(mode+'-'+invalid);isolated.mkdir();(isolated/'tests').mkdir()
                (isolated/'main.tf').write_text(declarations+'output "required_ids" { value = [var.repository_owner_id, var.repository_id] }\n')
                values='\n'.join('    '+name+' = '+('null' if name==invalid else '"12345"') for name in ['repository_owner_id','repository_id'] if not(mode=='missing' and name==invalid))
                (isolated/'tests'/'invalid.tftest.hcl').write_text('run "reject_required_input" {\n  command = plan\n  variables {\n'+values+'\n  }\n}\n')
                failed=execute([terraform,'test','-json','-no-color'],isolated)
                diagnostics=[r.get('diagnostic',{}) for r in events(failed) if r.get('type')=='diagnostic']
                assert failed.returncode!=0 and any(d.get('severity')=='error' and d.get('summary') in ['Required variable not set','No value for required variable'] and invalid in d.get('detail','') and (mode!='null' or 'null' in d.get('detail','').lower()) for d in diagnostics), 'Required-null/missing input must fail the actual Terraform type boundary'
                print('MOCK REQUIRED INPUT:',invalid,mode,'rejected')
    print('PASS: actual rendered mocked trust policies: 31 runs, 50 denied claims, four required-null/missing negatives; no AWS calls')


# Explicit unit-only selection for hosts outside the supported Linux integration environment.
# Credential-free CI invokes this file without arguments and still runs every integration check.
if sys.argv[1:]==['--immutable-source-fixtures-only']:
    immutable_oidc_source_fixtures()
    raise SystemExit(0)
if sys.argv[1:]==['--workflow-fixtures-only']:
    workflow_activation_fixtures()
    raise SystemExit(0)
if sys.argv[1:]==['--action-tag-fixtures-only']:
    action_tag_fixtures()
    raise SystemExit(0)

if sys.platform != 'linux':
    raise SystemExit('Infrastructure/security scanner integration tests require Linux; use Ubuntu CI.')
import hcl2
ROOT=pathlib.Path.cwd()
(ROOT/'.local/reviewer').mkdir(parents=True,exist_ok=True)

def iam_invariants(main,iam):
    parsed=hcl2.loads(main)
    subjects=next(x['subjects'][0] for x in parsed['locals'] if 'subjects' in x)
    assert subjects=={'plan':['production-plan','production-drift'],'apply':['production-apply'],'content':['production-content']},'exact environment trust'
    assert '"token.actions.githubusercontent.com:aud" = "sts.amazonaws.com"' in main,'STS audience'
    assert 'StringEquals' in main and 'repo:${local.oidc_repository}:environment:${env}' in main,'exact immutable repository subject'
    assert '${local.repository_owner}@${var.repository_owner_id}/${local.repository_name}@${var.repository_id}' in main,'immutable identity binding'
    data=hcl2.loads(iam); statements=data['locals'][0]['state_statements'][0]
    assert len(statements)==3
    assert statements[1]['Action']==['s3:GetObject'] and statements[1]['Resource']==['${local.state_arn}'],'plan state read only'
    assert set(statements[2]['Action'])=={'s3:GetObject','s3:PutObject','s3:DeleteObject'} and statements[2]['Resource']==['${local.lock_arn}'],'exact lockfile rights'
    for stmt in data['locals'][0]['read_statements'][0]:
        assert all(a.split(':')[1].startswith(('Get','List')) for a in stmt['Action']),'plan read actions'
    assert not re.search(r'Action\s*=\s*\[[^\]]*"(?:iam:[^"]+|sts:[^"]+|\*)"',iam),'no role escalation'
    assert not re.search(r'cloudfront:Create(?:Distribution|OriginAccessControl|ResponseHeadersPolicy)',iam),'no runtime CloudFront creation'
    assert not re.search(r'cloudfront::[^"\n]*|distribution/\*|origin-access-control/\*|response-headers-policy/\*',iam),'no wildcard CloudFront resources'
    content=iam.split('resource "aws_iam_role_policy" "content"')[1]
    assert 'Action = ["s3:PutObject"]' in content and 's3:DeleteObject' not in content,'content uploads only'
    assert '["index.html", "styles.css", "app.js", "deployment.json"]' in content,'fixed assets'

main=(ROOT/'infra/bootstrap/main.tf').read_text(); iam=(ROOT/'infra/bootstrap/iam.tf').read_text()
iam_invariants(main,iam)
mutations=[('wildcard environment trust',main.replace('"production-plan"','"*"'),iam),('plan state write',main,iam.replace('Action = ["s3:GetObject"], Resource = [local.state_arn]','Action = ["s3:GetObject", "s3:PutObject"], Resource = [local.state_arn]')),('cross-key lock mutation',main,iam.replace('Resource = [local.lock_arn]','Resource = ["*"]')),('broad CloudFront mutation',main,iam.replace('distribution/${coalesce(var.content_distribution_id, "NOTCONFIGURED")}','distribution/*')),('content delete',main,iam.replace('Action = ["s3:PutObject"], Resource = [for path','Action = ["s3:PutObject", "s3:DeleteObject"], Resource = [for path'))]
for name,m,i in mutations:
    try: iam_invariants(m,i)
    except AssertionError: pass
    else: raise AssertionError('Mutation not rejected: '+name)
print('PASS: independent IAM source invariants and five adversarial mutations (static source invariants; not rendered-policy or live IAM evaluation)')
action_tag_fixtures()
workflow_activation_fixtures()
immutable_oidc_source_fixtures()
rendered_immutable_oidc_tests()
cli=ROOT/'.tools/venv'/'bin'/'checkov'
with tempfile.TemporaryDirectory(prefix='unsafe-workflow-',dir=ROOT/'.local/reviewer') as temp:
    directory=pathlib.Path(temp); workflow=directory/'.github/workflows/unsafe.yml'; workflow.parent.mkdir(parents=True)
    workflow.write_text('name: Unsafe generated fixture\non: pull_request_target\npermissions: write-all\njobs:\n  unsafe:\n    runs-on: ubuntu-latest\n    steps:\n      - uses: actions/checkout@main\n      - run: echo "${{ github.event.pull_request.title }}"\n')
    result=subprocess.run([sys.executable,str(cli),'-d',str(directory),'--framework','github_actions','--check','CKV_GHA_2','--output','json','--quiet','--compact','--skip-download'],capture_output=True,text=True,timeout=180)
    report=json.loads(result.stdout)
    assert result.returncode==1 and any(x['check_id']=='CKV_GHA_2' for x in report['results']['failed_checks']), 'actual workflow scanner failed to reject injection'
    print('PASS: actual Checkov unsafe workflow injection rejected (scanner exit 1 CKV_GHA_2)')
    workflow.write_text('name: Invalid generated fixture\non: pull_request\njobs:\n  invalid:\n    runs-on: ubuntu-latest\n    forbidden: value\n    steps:\n      - run: echo safe\n')
    result=subprocess.run([str(ROOT/'.tools'/'actionlint'),str(workflow)],capture_output=True,text=True,timeout=30)
    assert result.returncode!=0 and 'unexpected key' in result.stdout+result.stderr,'actual actionlint did not reject invalid workflow'
    print('PASS: actual actionlint invalid workflow rejected (expected nonzero)')

