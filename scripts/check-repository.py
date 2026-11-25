"""Check the retained repository's local links, dependencies and entry points.

This stdlib-only check reads intended source, never ignored caches or private inputs.
It complements real Terraform validation, actionlint, scanners and browser tests.
"""
import json,pathlib,re,subprocess,sys
from urllib.parse import unquote,urlsplit

CANONICAL_DOCUMENTS={
 'README.md','SPEC.md','AGENTS.md','PROMPT.md','requirements/RESUME_CONTENT.md',
 'docs/ARCHITECTURE.md','docs/DEPLOYMENT.md','docs/SECURITY.md','docs/SDD_WORKFLOW.md',
 'docs/VERIFICATION.md','docs/decisions/001-linux-first-terraform.md'}
ENTRYPOINTS={
 '.github/workflows/ci.yml','package.json','package-lock.json','playwright.config.mjs',
 'requirements-tools.txt','requirements/action-pins.json','.gitignore','.gitleaks.toml','.tflint.hcl',
 '.codex/agents/planner.toml','.codex/agents/builder.toml','.codex/agents/reviewer.toml',
 'site/index.html','infra/bootstrap/versions.tf','infra/bootstrap/.terraform.lock.hcl',
 'infra/site/versions.tf','infra/site/.terraform.lock.hcl'}
TEMPLATES={'workflow-templates/content.yml','workflow-templates/drift.yml','workflow-templates/infrastructure.yml'}
IGNORED_ROOTS={'.git','.tools','.local','node_modules','test-results','playwright-report','dist','__pycache__'}
GENERATED={'infra/bootstrap/backend.tf'}
SOURCE_PATH=re.compile(r'(?<![\w./-])((?:scripts|tests|site|infra|requirements|workflow-templates|docs)/[A-Za-z0-9_./-]+\.[A-Za-z0-9_.-]+)')


def source_files(root):
 result=subprocess.run(['git','ls-files','-z','--cached','--others','--exclude-standard'],cwd=root,capture_output=True,check=True)
 return {name for name in result.stdout.decode().split('\0') if name and ((root/name).is_file() or (root/name).is_symlink())}


def private_payload(name):
 path=pathlib.PurePosixPath(name)
 return (bool(set(path.parts)&(IGNORED_ROOTS|{'.terraform'}))
  or path.suffix in {'.plan','.pdf','.pem','.key','.log','.zip','.tar','.gz','.tgz','.7z','.enc','.stderr','.stdout','.trace','.dump'}
  or '.tfstate' in name or '.tfplan' in name or path.name.startswith('.env')
  or ('.tfbackend' in name and not name.endswith('.tfbackend.example'))
  or ('.tfvars' in name and not name.endswith('.example.tfvars'))
  or name in GENERATED)


def inspect(root,files,documents=CANONICAL_DOCUMENTS,entrypoints=ENTRYPOINTS):
 root=root.resolve();errors=[];edges={name:set() for name in files}
 forbidden={name for name in files if private_payload(name)}
 if forbidden:errors.append('Intended source contains ignored/private payload; remove it from the source inventory')
 required=set(documents)|set(entrypoints)|TEMPLATES
 errors += ['Missing required source: '+name for name in sorted(required-files)]
 markdown={name for name in files if name.endswith('.md')}
 errors += ['Noncanonical Markdown file: '+name for name in sorted(markdown-set(documents))]
 active={name for name in files if name.startswith('.github/workflows/') and name.endswith(('.yml','.yaml'))}
 if active!={'.github/workflows/ci.yml'}:errors.append('Only ci.yml may be executable; operational workflows must remain inert')
 archived={name for name in files if name.startswith('workflow-templates/') and name.endswith(('.yml','.yaml'))}
 if archived!=TEMPLATES:errors.append('Missing or unexpected inert workflow template')
 for name in sorted(name for name in files if name.startswith('docs/evidence/')):
  if name in forbidden:continue
  if not name.endswith('.json'):errors.append('Evidence directory permits reviewed JSON records only: '+name)
  else:
   try:
    if not isinstance(json.loads((root/name).read_text(encoding='utf-8')), (dict,list)):errors.append('Evidence must be a structured JSON record: '+name)
   except (ValueError,OSError):errors.append('Invalid evidence JSON: '+name)
 site={name for name in files if name.startswith('site/')}
 if site and site!={'site/index.html','site/styles.css','site/app.js','site/deployment.json'}:errors.append('Missing or unexpected website asset outside the deployment allowlist')

 def reference(owner,target,relative=False):
  if not target or '${' in target or '{{' in target:return
  parsed=urlsplit(target)
  if parsed.scheme=='file':errors.append('Local-machine URL is not a repository dependency: '+owner);return
  if parsed.scheme or parsed.netloc or target.startswith('#'):return
  raw=unquote(parsed.path)
  if not raw:return
  candidate=(root/owner).parent/raw if relative and not raw.startswith('/') else root/raw.lstrip('/')
  resolved=candidate.resolve()
  if not resolved.is_relative_to(root):errors.append('Reference escapes repository: '+owner);return
  name=resolved.relative_to(root).as_posix()
  if any(part in IGNORED_ROOTS or part=='.terraform' for part in resolved.relative_to(root).parts):
   errors.append('Source links to ignored/private payload: '+owner+' -> '+name);return
  if name in GENERATED or pathlib.PurePosixPath(name).suffix in {'.tfplan','.tfstate','.tflock','.plan'}:
   if relative:errors.append('Document/import links to a generated private input: '+owner)
   return
  if name in files:edges[owner].add(name)
  elif not (name=='.' and files) and not any(item.startswith(name.rstrip('/')+'/') for item in files):errors.append('Missing local dependency: '+owner+' -> '+name)

 for name in sorted(files):
  if name in forbidden:continue
  path=root/name
  if path.is_symlink() or not path.resolve().is_relative_to(root):errors.append('Source symlink/outside target: '+name);continue
  if path.suffix not in {'.md','.py','.mjs','.js','.html','.css','.yml','.yaml','.tf','.json'}:continue
  text=path.read_text(encoding='utf-8')
  if name.endswith('.md'):
   for target in re.findall(r'!?\[[^\]]*\]\(([^)\n]+)\)',text):
    target=target.strip()
    if target.startswith('<'):target=target[1:target.index('>')]
    else:target=target.split()[0]
    reference(name,target,relative=True)
  if path.suffix in {'.mjs','.js'}:
   for target in re.findall(r'(?:from\s*|import\s*)[\'\"](\.[^\'\"]+)[\'\"]',text):reference(name,target,relative=True)
  if name=='playwright.config.mjs':
   # Playwright implicitly discovers the literal basename configured here.
   # Dynamic/glob configurations need an explicit checker change, not a blanket allow.
   test_directory=re.search(r"\btestDir\s*:\s*['\"]([^'\"]+)['\"]",text)
   test_match=re.search(r"\btestMatch\s*:\s*['\"]([A-Za-z0-9_.-]+)['\"]",text)
   if not test_directory or not test_match:errors.append('Unsupported Playwright discovery configuration')
   else:
    directory=(path.parent/test_directory.group(1)).resolve()
    if not directory.is_relative_to(root):errors.append('Playwright testDir escapes repository')
    else:
     prefix=directory.relative_to(root).as_posix().rstrip('/')+'/'
     discovered={item for item in files if item.startswith(prefix) and pathlib.PurePosixPath(item).name==test_match.group(1)}
     if not discovered:errors.append('Playwright discovery matches no retained test source')
     edges[name].update(discovered)
  if path.suffix=='.html':
   for target in re.findall(r'(?:src|href)\s*=\s*[\'\"]([^\'\"]+)[\'\"]',text):reference(name,target,relative=True)
  if path.suffix=='.tf':
   for target in re.findall(r'\bsource\s*=\s*"(\.[^"]+)"',text):
    directory=(path.parent/target).resolve()
    if not directory.is_relative_to(root):errors.append('Missing/unsafe local Terraform module: '+name+' -> '+target)
    else:
     relative=directory.relative_to(root).as_posix()
     module_files={item for item in files if pathlib.PurePosixPath(item).parent.as_posix()==relative and item.endswith('.tf')}
     if not module_files:errors.append('Missing/unsafe local Terraform module: '+name+' -> '+target)
     edges[name].update(module_files)

  # Explicit local command/data references, including script strings in the runner.
  if not (name.startswith('docs/evidence/') and name.endswith('.json')) and name != 'tests/repository-integrity.py':
   # The integrity harness contains deliberately nonexistent fixture-path strings.
   # Its real checker import is also independently referenced by the CI runner.
   for target in SOURCE_PATH.findall(text):reference(name,target.rstrip('.;,'))
 reached=set(required)&files
 while True:
  expanded=reached|{target for owner in reached for target in edges[owner]}
  if expanded==reached:break
  reached=expanded
 code={name for name in files if not (name.startswith('docs/evidence/') and name.endswith('.json')) and pathlib.PurePosixPath(name).suffix in {'.py','.mjs','.js','.html','.css','.yml','.yaml','.sh','.ps1','.json','.toml'}}
 errors += ['Orphan executable/asset source: '+name for name in sorted(code-reached)]
 return sorted(set(errors))


if __name__=='__main__':
 repository=pathlib.Path(__file__).resolve().parents[1]
 try:failures=inspect(repository,source_files(repository))
 except Exception as error:
  print('Repository integrity check could not complete:',type(error).__name__);raise SystemExit(1)
 if failures:
  print('\n'.join(failures));raise SystemExit(1)
 print('PASS: canonical documents, local dependencies, Terraform modules, inert workflows and source reachability')
