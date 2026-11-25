"""Small repository guardrail checks, complementary to Checkov/actionlint, not replacements."""
import pathlib,re,sys

def inspect(files):
    errors=[]
    for path,text in files.items():
        if path.endswith(('.yml','.yaml')):
            if 'pull_request_target' in text: errors.append('unsafe privileged PR trigger')
            for value in re.findall(r'uses:\s*([^\s]+)',text):
                if not re.fullmatch(r'[A-Za-z0-9_./-]+@[a-f0-9]{40}',value): errors.append('unpinned action')
            if re.search(r'permissions:\s*(write-all|read-all)',text): errors.append('broad permissions')
            if 'id-token: write' in text:
                for marker in ['resumeops-production','cancel-in-progress: false','scripts/gate.mjs',"github.ref == 'refs/heads/main'",'environment: production-','timeout-minutes:']:
                    if marker not in text: errors.append('missing privileged workflow guard: '+marker)
                if 'pull_request:' in text: errors.append('PR credentials forbidden')
            if re.search(r'path:.*(tfplan|tfstate)',text): errors.append('plaintext state/plan artifact')
        if path.endswith('.tf'):
            for setting in ['block_public_acls','block_public_policy','ignore_public_acls','restrict_public_buckets']:
                if re.search(r'\b'+setting+r'\s*=\s*false',text): errors.append('public S3 control disabled')
            if 'viewer_protocol_policy' in text and 'redirect-to-https' not in text: errors.append('HTTPS redirect missing')
            if re.search(r'"token.actions.githubusercontent.com:sub"\s*=\s*"[^"\n]*\*',text): errors.append('wildcard OIDC trust')
            if re.search(r'Action\s*=\s*\[?\s*"(?:iam:\*|sts:AssumeRole|\*)"',text): errors.append('runtime escalation')
    return errors

if __name__=='__main__':
    active=list(pathlib.Path('.github/workflows').glob('*.yml'))+list(pathlib.Path('.github/workflows').glob('*.yaml'))
    if {p.name for p in active} != {'ci.yml'}:
        print('Verification stage permits only ci.yml as an executable workflow');sys.exit(1)
    active_text=active[0].read_text()
    if any(marker in active_text for marker in ['id-token:', 'secrets.', 'configure-aws-credentials', 'environment:', 'terraform apply', 'terraform destroy']):
        print('Verification CI must remain credential-free and cannot deploy');sys.exit(1)
    templates=list(pathlib.Path('workflow-templates').glob('*.yml'))
    if {p.name for p in templates} != {'content.yml','drift.yml','infrastructure.yml'}:
        print('Missing or unexpected archived workflow template');sys.exit(1)
    paths=list(pathlib.Path('infra').rglob('*.tf'))+active+templates
    errors=inspect({str(p):p.read_text() for p in paths if '.terraform' not in str(p)})
    if errors:
        print('\n'.join(sorted(set(errors))));sys.exit(1)
    print('Repository workflow/IaC guardrails passed')
