"""Read-only public upstream provenance check; requires network, no credentials."""
import json,os,pathlib,re,subprocess,tempfile,urllib.request

OFFICIAL_ACTION_REPOSITORIES={'actions/checkout','actions/setup-node','hashicorp/setup-terraform','aws-actions/configure-aws-credentials','actions/upload-artifact','actions/download-artifact'}


def tag_reference(tag):
    if not isinstance(tag,str) or not re.fullmatch(r'v[0-9]+\.[0-9]+\.[0-9]+',tag):
        raise ValueError('Exact pinned release tag required')
    return 'refs/tags/'+tag


def parse_action_refs(output,tag):
    literal=tag_reference(tag)
    if not isinstance(output,str):raise ValueError('Malformed Git ref response')
    records={}
    for line in output.splitlines():
        record=re.fullmatch(r'([a-f0-9]{40})\t([^\s]+)',line)
        if not record:raise ValueError('Malformed Git ref record')
        sha,ref=record.groups()
        if ref not in {literal,literal+'^{}'} or ref in records:
            raise ValueError('Unexpected or duplicate Git ref')
        records[ref]=sha
    if literal not in records:raise ValueError('Pinned release tag missing')
    return records.get(literal+'^{}',records[literal])


def verify_action_tag(repo,tag,expected):
    if repo not in OFFICIAL_ACTION_REPOSITORIES or not isinstance(expected,str) or not re.fullmatch(r'[a-f0-9]{40}',expected):
        raise ValueError('Exact official repository and pinned commit required')
    literal=tag_reference(tag)
    command=['git','-c','credential.helper=','-c','core.askPass=','-c','http.extraHeader=',
             '-c','protocol.allow=never','-c','protocol.https.allow=always',
             'ls-remote','--tags','--exit-code','--','https://github.com/'+repo+'.git',literal,literal+'^{}']
    # Isolate credentials, user/repository Git configuration and URL rewrites.
    # No TLS overrides: verified HTTPS defaults remain enabled.
    with tempfile.TemporaryDirectory(prefix='resumeops-upstream-') as directory:
        environment={key:value for key,value in os.environ.items() if not key.startswith(('GIT_','GH_','GITHUB_','GCM_')) and key not in {'SSH_ASKPASS','NETRC'}}
        environment.update(GIT_TERMINAL_PROMPT='0',GIT_CONFIG_NOSYSTEM='1',GIT_CONFIG_SYSTEM=os.devnull,
            GIT_CONFIG_GLOBAL=os.devnull,GIT_CONFIG_COUNT='0',GIT_CEILING_DIRECTORIES=directory,
            HOME=directory,USERPROFILE=directory,XDG_CONFIG_HOME=directory)
        try:
            result=subprocess.run(command,cwd=directory,env=environment,capture_output=True,text=True,shell=False,timeout=60,check=False)
        except (OSError,subprocess.TimeoutExpired):
            raise RuntimeError('Anonymous upstream Git lookup unavailable') from None
    if result.returncode!=0:raise RuntimeError('Anonymous upstream Git lookup failed')
    if parse_action_refs(result.stdout,tag)!=expected:raise ValueError('Action release tag does not match pinned commit')


def get(url):
    return json.load(urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'ResumeOps-provenance'}),timeout=30))


def main():
    pins=json.loads(pathlib.Path('requirements/action-pins.json').read_text())
    assert set(pins)==OFFICIAL_ACTION_REPOSITORIES, 'Unexpected action repository inventory'
    for repo,pin in pins.items():
        verify_action_tag(repo,pin['version'],pin['sha'])
        print(repo,pin['version'],pin['sha'],'VERIFIED via anonymous Git HTTPS')
    for path in list(pathlib.Path('.github/workflows').glob('*.yml'))+list(pathlib.Path('workflow-templates').glob('*.yml')):
        for repo,sha in re.findall(r'uses:\s*([^\s@]+)@([a-f0-9]{40})',path.read_text()):
            assert pins[repo]['sha']==sha
    assert get('https://registry.terraform.io/v1/providers/hashicorp/aws/6.74.0')['version']=='6.74.0'
    assert get('https://pypi.org/pypi/checkov/3.4.11/json')['info']['version']=='3.4.11'
    for package,version in [('@playwright/test','1.65.1'),('@axe-core/playwright','4.14.1')]:
        assert get('https://registry.npmjs.org/'+package+'/'+version)['version']==version
    print('Provider, scanner and browser dependencies VERIFIED against official registries')

    # Cross-platform readonly init must be able to authenticate the Linux archive.
    manifest=urllib.request.urlopen('https://releases.hashicorp.com/terraform-provider-aws/6.74.0/terraform-provider-aws_6.74.0_SHA256SUMS',timeout=30).read().decode()
    checksums={line.split()[-1].lstrip('*'):line.split()[0] for line in manifest.splitlines() if len(line.split())==2}
    allowed={digest for filename,digest in checksums.items() if filename.endswith('.zip')}
    for root in ['infra/bootstrap','infra/site']:
        text=(pathlib.Path(root)/'.terraform.lock.hcl').read_text()
        assert re.search(r'version\s*=\s*"6\.74\.0"',text), 'Provider version changed'
        content_hashes=set(re.findall(r'"(h1:[^"\n]+)"',text))
        assert content_hashes == {'h1:BT+sqgXa/XnH4zgVgG2ZEda3WVr6wSJyJbcv64hBTtg=','h1:GX7SKlV247NJ8PMuI3qvO//dcXb6UZYTXxJhLB4Yx/g='}, 'Missing or unreviewed platform content hash'
        archived=set(re.findall(r'"zh:([a-f0-9]{64})"',text))
        assert archived == allowed and len(archived) == 15, 'Original official archive checksums must all be retained'
        for target in ['linux_amd64','windows_amd64']:
            assert checksums['terraform-provider-aws_6.74.0_'+target+'.zip'] in archived, 'Missing readonly target archive checksum'
    print('Both readonly lockfiles retain all15official archive hashes and both reviewed Linux/Windows AWS 6.74.0 content hashes VERIFIED')

    # Public service documentation only; this makes no account/IAM API request.
    iam=pathlib.Path('infra/bootstrap/iam.tf').read_text()
    for service in ['s3','cloudfront']:
        metadata=get('https://servicereference.us-east-1.amazonaws.com/v1/'+service+'/'+service+'.json')
        known={action['Name'] for action in metadata['Actions']}
        actions=set(re.findall(r'"'+service+r':([A-Z][A-Za-z]+)"',iam))
        assert actions and not actions-known, 'Unknown runtime IAM action name'
        print(service,len(actions),'runtime IAM action names VERIFIED against public AWS metadata')


if __name__=='__main__':
    main()
