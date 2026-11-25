"""Run every required local verification check and preserve individual exit codes.

No backend initialization, provider configuration, AWS authentication or deployment.
Failures do not hide later checks, and any failure makes the final result nonzero.
"""
import hashlib,json,os,pathlib,platform,re,shlex,subprocess,sys,time

if sys.platform != 'linux':
 print('Full Terraform verification is supported on Linux only. Use the credential-free Ubuntu CI workflow; Windows supports npm test and npm run preview for the website.',file=sys.stderr)
 raise SystemExit(2)

ROOT=pathlib.Path(__file__).resolve().parents[1]
os.chdir(ROOT)
TOOLS=ROOT/'.tools'
PYTHON=pathlib.Path(sys.executable)
TF=os.environ.get('RESUMEOPS_TERRAFORM','terraform')
CHECKOV=TOOLS/'venv'/'bin'/'checkov'
workflows=[ROOT/'.github/workflows/ci.yml',*(ROOT/'workflow-templates').glob('*.yml')]
locks=[ROOT/p/'.terraform.lock.hcl' for p in ['infra/bootstrap','infra/site']]
original={str(path):hashlib.sha256(path.read_bytes()).hexdigest() for path in locks}
environment={k:v for k,v in os.environ.items() if not k.startswith('AWS_')}
environment.update(AWS_EC2_METADATA_DISABLED='true',AWS_CONFIG_FILE=str(TOOLS/'no-aws-config'),AWS_SHARED_CREDENTIALS_FILE=str(TOOLS/'no-aws-credentials'),CHECKPOINT_DISABLE='1',TF_IN_AUTOMATION='true',TF_INPUT='false',CKV_ENABLE_EXTERNAL_MODULES='false',PYTHONUTF8='1')
checks=[('Terraform exact version',[TF,'version','-json']),('Terraform format',[TF,'fmt','-check','-recursive','infra'])]
for root in ['infra/bootstrap','infra/site']:
 checks += [(root+' readonly init',[TF,'-chdir='+root,'init','-backend=false','-input=false','-lockfile=readonly']),
            (root+' validate',[TF,'-chdir='+root,'validate','-no-color']),
            (root+' TFLint',[str(TOOLS/'tflint'),'--chdir='+root,'--config='+str(ROOT/'.tflint.hcl')])]
checks += [
 ('Checkov IaC',[str(PYTHON),str(CHECKOV),'-d','infra','--framework','terraform','--compact','--quiet','--skip-download']),
 ('Active and archived workflow syntax',[str(TOOLS/'actionlint'),*[str(path) for path in workflows]]),
 ('Source secret scan',[str(TOOLS/'gitleaks'),'dir','.','--redact','--no-banner']),
 ('Workflow and IaC guardrails',[str(PYTHON),'scripts/security.py']),
 ('Repository links and dependency integrity',[str(PYTHON),'scripts/check-repository.py']),
 ('Repository-integrity negative controls',[str(PYTHON),'tests/repository-integrity.py']),
 ('Official dependency and cross-platform lock provenance',[str(PYTHON),'scripts/verify-provenance.py']),
 ('Actual negative IaC scanner',[str(PYTHON),'tests/negative-scans.py']),
 ('Independent IAM and unsafe workflow scanner tests',[str(PYTHON),'tests/independent_checks.py']),
 ('Security unit and negative tests',['node','--test','tests/security.test.mjs']),
 ('Independent API and plan tests',['node','tests/additional-security.mjs']),
 ('Actual drift runner-shell tests',[str(PYTHON),'tests/drift-execution.py']),
 ('Browser, accessibility and local smoke tests',['npm','test'])]
results=[]
for name,command in checks:
 print('\nCHECK:',name,flush=True)
 print('COMMAND:',shlex.join([str(arg).replace(str(ROOT),'<workspace>') for arg in command]),flush=True)
 started=time.monotonic()
 try:
  if name=='Terraform exact version':
   completed=subprocess.run(command,env=environment,capture_output=True,text=True,timeout=120)
   code=completed.returncode
   if code==0:
    version=json.loads(completed.stdout).get('terraform_version')
    print('Terraform version:',version,flush=True)
    if version!='1.17.2':code=1
   else:print('Terraform version could not be established',flush=True)
  else:
   code=subprocess.run(command,env=environment,timeout=600).returncode
 except Exception as error:
  print('CHECK ERROR:',type(error).__name__,flush=True);code=1
 record={'name':name,'command':[str(arg).replace(str(ROOT),'.') for arg in command],'exit_code':code,'seconds':round(time.monotonic()-started,2)}
 results.append(record);print('EXIT:',code,flush=True)
unchanged=all(hashlib.sha256(path.read_bytes()).hexdigest()==original[str(path)] for path in locks)
results.append({'name':'Provider lockfiles unchanged','command':['internal SHA256 comparison of both committed provider locks before/after all checks'],'exit_code':0 if unchanged else 1})
output=ROOT/'.local/verification';output.mkdir(parents=True,exist_ok=True)
source_sha=environment.get('GITHUB_SHA','')
source_sha=source_sha if re.fullmatch(r'[a-f0-9]{40}',source_sha) else None
evidence={'schema_version':1,'source_sha':source_sha,'runner_os':platform.system(),'python_version':platform.python_version(),'working_directory':'repository root','checks':results}
(output/'results.json').write_text(json.dumps(evidence,indent=2)+'\n')
summary='\nVerified source SHA: `'+(source_sha or 'local uncommitted checkout')+'`\nRunner OS: `'+platform.system()+'`\n\n| Required check | Command | Exit code |\n|---|---|---|\n'+''.join('| '+record['name']+' | `'+shlex.join(record['command']).replace('`','')+'` | '+str(record['exit_code'])+' |\n' for record in results)
print(summary,flush=True)
if environment.get('GITHUB_STEP_SUMMARY'):
 with open(environment['GITHUB_STEP_SUMMARY'],'a',encoding='utf-8') as stream:stream.write(summary)
raise SystemExit(1 if any(record['exit_code']!=0 for record in results) else 0)
