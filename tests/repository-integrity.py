"""Negative controls for real repository-integrity analysis; no cloud or tooling."""
import importlib.util,pathlib,tempfile,unittest
module_path=pathlib.Path(__file__).resolve().parents[1]/'scripts/check-repository.py'
spec=importlib.util.spec_from_file_location('repository_integrity',module_path)
checks=importlib.util.module_from_spec(spec);spec.loader.exec_module(checks)

class IntegrityTests(unittest.TestCase):
 def fixture(self,extra=None):
  temporary=tempfile.TemporaryDirectory();self.addCleanup(temporary.cleanup)
  root=pathlib.Path(temporary.name)
  contents={'README.md':'[Helper](scripts/required.py)\n','.github/workflows/ci.yml':'name: CI\n','scripts/required.py':'print("fixture")\n',**{name:'# Inert fixture\n' for name in checks.TEMPLATES},**(extra or {})}
  for name,text in contents.items():
   path=root/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_text(text,encoding='utf-8')
  return root,set(contents)
 def analyze(self,root,files):return checks.inspect(root,files,documents={'README.md'},entrypoints={'.github/workflows/ci.yml'}|({'playwright.config.mjs'} if 'playwright.config.mjs' in files else set()))
 def test_valid_dependency_graph(self):
  root,files=self.fixture();self.assertEqual(self.analyze(root,files),[])
 def test_broken_document_link(self):
  root,files=self.fixture({'README.md':'[Missing](docs/missing.md)\n[Helper](scripts/required.py)\n'})
  self.assertTrue(any('Missing local dependency' in error for error in self.analyze(root,files)))
 def test_missing_command_dependency(self):
  root,files=self.fixture({'.github/workflows/ci.yml':'run: python scripts/missing.py\n'})
  self.assertTrue(any('scripts/missing.py' in error for error in self.analyze(root,files)))
 def test_missing_terraform_module(self):
  root,files=self.fixture({'infra/site/main.tf':'module "fixture" { source = "../missing" }\n'})
  self.assertTrue(any('Terraform module' in error for error in self.analyze(root,files)))
 def test_activated_operational_workflow(self):
  root,files=self.fixture({'.github/workflows/deploy.yml':'name: Forbidden\n'})
  self.assertTrue(any('Only ci.yml' in error for error in self.analyze(root,files)))
 def test_orphan_script(self):
  root,files=self.fixture({'scripts/orphan.py':'print("unused")\n'})
  self.assertTrue(any('Orphan executable' in error and 'orphan.py' in error for error in self.analyze(root,files)))
 def test_private_payload_is_not_ignored_if_in_source_inventory(self):
  root,files=self.fixture({'.tools/private.tfstate':'dummy fixture, no real state'})
  self.assertTrue(any('ignored/private payload' in error for error in self.analyze(root,files)))
 def test_raw_diagnostics_archives_plans_and_private_inputs_rejected(self):
  for name in ['raw-diagnostic.log','provider.zip','candidate.enc','raw.stderr','private.tfvars','private.tfvars.json','private.tfbackend','infra/bootstrap/backend.tf']:
   with self.subTest(name=name):
    root,files=self.fixture({name:'dummy fixture only'})
    self.assertTrue(any('ignored/private payload' in error for error in self.analyze(root,files)))
 def test_committed_input_examples_allowed(self):
  root,files=self.fixture({'infra/site/production.s3.tfbackend.example':'bucket = "REPLACE"','infra/site/production.example.tfvars':'site_bucket = "REPLACE"'})
  self.assertEqual(self.analyze(root,files),[])
 def test_root_relative_document_link(self):
  root,files=self.fixture({'README.md':'[Helper](/scripts/required.py)\n'})
  self.assertEqual(self.analyze(root,files),[])
 def test_evidence_cannot_hide_executable_source(self):
  root,files=self.fixture({'docs/evidence/hidden.py':'print("fixture")'})
  self.assertTrue(any('Evidence directory' in error for error in self.analyze(root,files)))
 def test_historical_evidence_is_data_not_an_active_dependency(self):
  root,files=self.fixture({'docs/evidence/history.json':'{"command": ["python", "scripts/removed-helper.py"]}'})
  self.assertEqual(self.analyze(root,files),[])
 def test_document_cannot_link_to_generated_private_plan(self):
  root,files=self.fixture({'README.md':'[Plan](infra/site/candidate.tfplan)\n[Helper](scripts/required.py)'})
  self.assertTrue(any('generated private input' in error for error in self.analyze(root,files)))
 def test_playwright_literal_configuration_discovers_browser_spec(self):
  root,files=self.fixture({'playwright.config.mjs':"export default { testDir: './tests', testMatch: 'site.spec.mjs' };",'tests/site.spec.mjs':'// discovered fixture'})
  self.assertEqual(self.analyze(root,files),[])
 def test_playwright_discovery_does_not_allow_unmatched_orphan(self):
  root,files=self.fixture({'playwright.config.mjs':"export default { testDir: './tests', testMatch: 'site.spec.mjs' };",'tests/site.spec.mjs':'// discovered fixture','tests/unused.spec.mjs':'// orphan fixture'})
  self.assertTrue(any('Orphan' in error and 'unused.spec.mjs' in error for error in self.analyze(root,files)))
 def test_playwright_configured_spec_cannot_be_deleted(self):
  root,files=self.fixture({'playwright.config.mjs':"export default { testDir: './tests', testMatch: 'site.spec.mjs' };"})
  self.assertTrue(any('matches no retained test' in error for error in self.analyze(root,files)))
 def test_retired_directory_cannot_satisfy_projected_dependency(self):
  root,files=self.fixture({'README.md':'[Directory](retired/)\n[Helper](scripts/required.py)'})
  (root/'retired').mkdir()
  self.assertTrue(any('Missing local dependency' in error and 'retired' in error for error in self.analyze(root,files)))
 def test_retired_module_cannot_satisfy_projected_dependency(self):
  root,files=self.fixture({'infra/site/main.tf':'module "fixture" { source = "../retired" }'})
  module=root/'infra/retired';module.mkdir();(module/'main.tf').write_text('// physically present but excluded from retained projection')
  self.assertTrue(any('Terraform module' in error for error in self.analyze(root,files)))
 def test_escaping_document_reference(self):
  root,files=self.fixture({'README.md':'[Escape](../outside.md)\n[Helper](scripts/required.py)\n'})
  self.assertTrue(any('escapes repository' in error for error in self.analyze(root,files)))

if __name__=='__main__':unittest.main()
