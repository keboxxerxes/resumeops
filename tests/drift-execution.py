"""Execute the actual drift step under runner-equivalent bash -e, stubbing Terraform.
The shell function returns synthetic exit codes; no Terraform or AWS call runs.
"""
import os,pathlib,shutil,subprocess,tempfile,yaml
root=pathlib.Path.cwd(); bash=shutil.which('bash')
(root/'.local/reviewer').mkdir(parents=True,exist_ok=True)
if os.name=='nt': bash='C:/Program Files/Git/bin/bash.exe'
workflow=yaml.safe_load((root/'workflow-templates/drift.yml').read_text())
block=next(s['run'] for s in workflow['jobs']['drift']['steps'] if s.get('name')=='Detect without applying')
with tempfile.TemporaryDirectory(dir=root/'.local/reviewer') as directory:
    for code,label,expected in [(0,'NO_DRIFT',0),(1,'Operation failed',1),(2,'DRIFT',1)]:
        env=os.environ.copy();env['SIMULATED_EXIT']=str(code);env['GITHUB_STEP_SUMMARY']=str(pathlib.Path(directory)/'summary.md')
        script='terraform() { return "$SIMULATED_EXIT"; }\n'+block
        result=subprocess.run([bash,'--noprofile','--norc','-e','-o','pipefail','-c',script],env=env,capture_output=True,text=True,timeout=30)
        assert result.returncode==expected and label in result.stdout+result.stderr,(code,result.returncode,result.stdout,result.stderr)
        print('PASS: actual drift shell step captured',code,'and returned',expected)
