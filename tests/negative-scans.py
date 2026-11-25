"""Demonstrate real Checkov rejection of an unsafe generated IaC fixture."""
import json,pathlib,subprocess,sys,tempfile
if sys.platform != 'linux':
    raise SystemExit('Infrastructure/security scanner integration tests require Linux; use Ubuntu CI.')
root=pathlib.Path('.tools').resolve();root.mkdir(exist_ok=True)
with tempfile.TemporaryDirectory(prefix='negative-iac-',dir=root) as directory:
    fixture=pathlib.Path(directory)/'main.tf'
    fixture.write_text('resource "aws_s3_bucket" "unsafe_fixture" {\n  bucket = "resumeops-dummy-negative-fixture"\n  acl = "public-read"\n}\n')
    cli=root/'venv'/'bin'/'checkov'
    result=subprocess.run([sys.executable,str(cli),'-d',directory,'--framework','terraform','--check','CKV_AWS_20','--output','json','--quiet','--compact','--skip-download'],text=True,capture_output=True,timeout=180)
    try: report=json.loads(result.stdout)
    except Exception: raise SystemExit('Negative scanner fixture did not produce a valid report; NOT PASS')
    if result.returncode!=1 or not any(item['check_id']=='CKV_AWS_20' for item in report['results']['failed_checks']):
        raise SystemExit('Insecure public bucket was not rejected; NOT PASS')
    print('PASS: real Checkov rejected public-read bucket fixture (expected scanner exit 1)')
