"""Independent reviewer invariants and real unsafe-workflow scanner checks.
No AWS calls; fixtures are ephemeral ignored local files.
"""
import copy,json,os,pathlib,re,subprocess,sys,tempfile
import hcl2
ROOT=pathlib.Path.cwd()
(ROOT/'.local/reviewer').mkdir(parents=True,exist_ok=True)

def iam_invariants(main,iam):
    parsed=hcl2.loads(main)
    subjects=next(x['subjects'][0] for x in parsed['locals'] if 'subjects' in x)
    assert subjects=={'plan':['production-plan','production-drift'],'apply':['production-apply'],'content':['production-content']},'exact environment trust'
    assert '"token.actions.githubusercontent.com:aud" = "sts.amazonaws.com"' in main,'STS audience'
    assert 'StringEquals' in main and 'repo:${var.repository}:environment:${env}' in main,'exact repository subject'
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
print('PASS: independent IAM source invariants and five adversarial mutations (static; provider rendering unavailable)')
cli=ROOT/'.tools/venv'/('Scripts' if os.name=='nt' else 'bin')/'checkov'
with tempfile.TemporaryDirectory(prefix='unsafe-workflow-',dir=ROOT/'.local/reviewer') as temp:
    directory=pathlib.Path(temp); workflow=directory/'.github/workflows/unsafe.yml'; workflow.parent.mkdir(parents=True)
    workflow.write_text('name: Unsafe generated fixture\non: pull_request_target\npermissions: write-all\njobs:\n  unsafe:\n    runs-on: ubuntu-latest\n    steps:\n      - uses: actions/checkout@main\n      - run: echo "${{ github.event.pull_request.title }}"\n')
    result=subprocess.run([sys.executable,str(cli),'-d',str(directory),'--framework','github_actions','--check','CKV_GHA_2','--output','json','--quiet','--compact','--skip-download'],capture_output=True,text=True,timeout=180)
    report=json.loads(result.stdout)
    assert result.returncode==1 and any(x['check_id']=='CKV_GHA_2' for x in report['results']['failed_checks']), 'actual workflow scanner failed to reject injection'
    print('PASS: actual Checkov unsafe workflow injection rejected (scanner exit 1 CKV_GHA_2)')
    workflow.write_text('name: Invalid generated fixture\non: pull_request\njobs:\n  invalid:\n    runs-on: ubuntu-latest\n    forbidden: value\n    steps:\n      - run: echo safe\n')
    result=subprocess.run([str(ROOT/'.tools'/('actionlint.exe' if os.name=='nt' else 'actionlint')),str(workflow)],capture_output=True,text=True,timeout=30)
    assert result.returncode!=0 and 'unexpected key' in result.stdout+result.stderr,'actual actionlint did not reject invalid workflow'
    print('PASS: actual actionlint invalid workflow rejected (expected nonzero)')

