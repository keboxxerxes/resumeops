"""Check committed runtime IAM action names against official AWS service metadata."""
import urllib.request,json,re,pathlib
text=pathlib.Path('infra/bootstrap/iam.tf').read_text()
for service in ['s3','cloudfront']:
    url='https://servicereference.us-east-1.amazonaws.com/v1/'+service+'/'+service+'.json'
    data=json.load(urllib.request.urlopen(url))
    known={action['Name'] for action in data['Actions']}
    names=set(re.findall('"'+service+':([A-Z][A-Za-z]+)"',text))
    unknown=sorted(names-known)
    assert not unknown,(service,unknown)
    print('PASS:',service,len(names),'IAM action names verified against official AWS metadata')
