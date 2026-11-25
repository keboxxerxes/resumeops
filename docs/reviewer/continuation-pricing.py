"""Read public AWS S3 regional price-list entries; never accesses an AWS account."""
import json,urllib.request,pathlib
url='https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonS3/current/us-east-1/index.json'
data=json.load(urllib.request.urlopen(url))
entries=[]
for sku,product in data['products'].items():
    attr=product['attributes']
    if attr.get('usagetype') not in ['TimedStorage-ByteHrs','Requests-Tier1','Requests-Tier2']:continue
    for term in data['terms']['OnDemand'].get(sku,{}).values():
        for dim in term['priceDimensions'].values():
            if dim['beginRange']=='0':entries.append({'usage_type':attr['usagetype'],'description':dim['description'],'unit':dim['unit'],'usd':dim['pricePerUnit']['USD'],'begin_range':dim['beginRange']})
assert {x['usage_type'] for x in entries}=={'TimedStorage-ByteHrs','Requests-Tier1','Requests-Tier2'}
record={'source':url,'publication_date':data['publicationDate'],'entries':entries}
pathlib.Path('docs/reviewer/continuation-pricing.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record,indent=2))
