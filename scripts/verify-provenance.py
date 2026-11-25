"""Read-only public upstream provenance check; requires network, no credentials."""
import json,pathlib,re,urllib.request

def get(url):
    return json.load(urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'ResumeOps-provenance'}),timeout=30))
pins=json.loads(pathlib.Path('requirements/action-pins.json').read_text())
for repo,pin in pins.items():
    base='https://api.github.com/repos/'+repo
    obj=get(base+'/git/ref/tags/'+pin['version'])['object']
    while obj['type']=='tag': obj=get(base+'/git/tags/'+obj['sha'])['object']
    assert obj['sha']==pin['sha'], 'Action tag mismatch'
    print(repo,pin['version'],pin['sha'],'VERIFIED')
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
allowed=set(checksums.values())
for root in ['infra/bootstrap','infra/site']:
    text=(pathlib.Path(root)/'.terraform.lock.hcl').read_text()
    assert re.search(r'version\s*=\s*"6\.74\.0"',text), 'Provider version changed'
    archived=set(re.findall(r'"zh:([a-f0-9]{64})"',text))
    assert archived and archived <= allowed, 'Unknown provider archive checksum'
    for target in ['linux_amd64','windows_amd64']:
        assert checksums['terraform-provider-aws_6.74.0_'+target+'.zip'] in archived, 'Missing readonly target archive checksum'
print('Both readonly lockfiles authenticate official Linux/Windows AWS 6.74.0 archives VERIFIED')
