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


# Explicit unit-only selection for hosts outside the supported Linux integration environment.
# Credential-free CI invokes this file without arguments and still runs every integration check.
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
print('PASS: independent IAM source invariants and five adversarial mutations (static source invariants; not rendered-policy or live IAM evaluation)')
action_tag_fixtures()
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

