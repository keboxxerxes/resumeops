import test from 'node:test';
import assert from 'node:assert/strict';
import {execFileSync} from 'node:child_process';
import {readFileSync,readdirSync} from 'node:fs';
import {seal,open,validatePlan} from '../scripts/plan-crypto.mjs';
import {verifyProtection} from '../scripts/gate.mjs';
import {validateRevision,ASSETS} from '../scripts/content.mjs';
import {confirmDestroy} from '../scripts/confirm.mjs';
import {driftStatus} from '../scripts/drift.mjs';
const owner='owner';
const environment={can_admins_bypass:false,protection_rules:[{type:'required_reviewers',prevent_self_review:false,reviewers:[{type:'User',reviewer:{id:1,login:owner}}]}],deployment_branch_policy:{custom_branch_policies:true,protected_branches:false}};
const policies={total_count:1,branch_policies:[{name:'main',type:'branch'}]};
const branch={enforce_admins:{enabled:true},required_pull_request_reviews:{required_approving_review_count:0,dismiss_stale_reviews:true,require_last_push_approval:false,require_code_owner_reviews:false,bypass_pull_request_allowances:{users:[],teams:[],apps:[]}},required_status_checks:{strict:true,contexts:['verify']}};
const verify=(env=environment,policy=policies,protection=branch,expectedOwner=owner)=>verifyProtection(env,policy,protection,expectedOwner);

test('single-maintainer protection accepts owner approval and rejects malformed or permissive settings',()=>{
 assert.doesNotThrow(()=>verify());
 assert.doesNotThrow(()=>verify(environment,policies,branch,'OWNER'));
 const extra=structuredClone(environment);extra.protection_rules[0].reviewers.push({type:'Team',reviewer:{id:2,slug:'operators'}});assert.doesNotThrow(()=>verify(extra));
 for(const expectedOwner of [undefined,null,'','bad/owner','-owner','owner--name','owner name',42]) assert.throws(()=>verifyProtection(environment,policies,branch,expectedOwner));
 for(const edit of [e=>e.can_admins_bypass=true,e=>delete e.can_admins_bypass,e=>e.protection_rules[0].prevent_self_review=true,e=>delete e.protection_rules[0].prevent_self_review,e=>e.protection_rules[0].prevent_self_review='false',e=>e.protection_rules[0].reviewers=[],e=>e.protection_rules[0].reviewers='owner',e=>e.protection_rules[0].reviewers=[{}],e=>e.protection_rules[0].reviewers=[{type:'User',reviewer:{id:1,login:'different'}}],e=>e.protection_rules[0].reviewers=[{type:'Team',reviewer:{id:2,slug:'owner'}}],e=>e.protection_rules[0].reviewers[0].reviewer.id='1',e=>e.protection_rules[0].reviewers[0].reviewer.id=1e20,e=>e.protection_rules[0].reviewers[0].reviewer.id=0,e=>e.protection_rules[0].reviewers[0].type='App',e=>e.deployment_branch_policy.protected_branches=true,e=>e.protection_rules=null,e=>e.protection_rules.push(e.protection_rules[0])]) {
  const env=structuredClone(environment);edit(env);assert.throws(()=>verify(env));
 }
 for(const policy of [{total_count:0,branch_policies:[]},{total_count:1,branch_policies:[{name:'*',type:'branch'}]},{total_count:1,branch_policies:[{name:'main',type:'tag'}]},{total_count:2,branch_policies:[{name:'main',type:'branch'}]},{total_count:1,branch_policies:[{name:'main',type:'branch'},{name:'main',type:'tag'}]},{branch_policies:[{name:'main',type:'branch'}]},{total_count:'1',branch_policies:[{name:'main',type:'branch'}]}]) assert.throws(()=>verify(environment,policy));
 for(const count of [undefined,null,'0',-1,0.5,1]) {
  const protection=structuredClone(branch);if(count===undefined)delete protection.required_pull_request_reviews.required_approving_review_count;else protection.required_pull_request_reviews.required_approving_review_count=count;assert.throws(()=>verify(environment,policies,protection));
 }
 for(const edit of [b=>delete b.required_pull_request_reviews,b=>b.required_pull_request_reviews=null,b=>b.required_pull_request_reviews.require_last_push_approval=true,b=>delete b.required_pull_request_reviews.require_last_push_approval,b=>b.required_pull_request_reviews.require_code_owner_reviews=true,b=>delete b.required_pull_request_reviews.require_code_owner_reviews,b=>b.required_pull_request_reviews.dismiss_stale_reviews=false,b=>b.enforce_admins.enabled=false,b=>b.required_status_checks.strict=false,b=>b.required_status_checks.contexts=[],b=>b.required_status_checks.contexts='verify']) {
  const protection=structuredClone(branch);edit(protection);assert.throws(()=>verify(environment,policies,protection));
 }
 for(const kind of ['users','teams','apps']) {
  const protection=structuredClone(branch);protection.required_pull_request_reviews.bypass_pull_request_allowances[kind]=[{}];assert.throws(()=>verify(environment,policies,protection));
  protection.required_pull_request_reviews.bypass_pull_request_allowances[kind]=false;assert.throws(()=>verify(environment,policies,protection));
 }
 for(const allowances of [undefined,null,{},[],{users:[],teams:[],apps:[],unknown:[]}]) {
  const protection=structuredClone(branch);protection.required_pull_request_reviews.bypass_pull_request_allowances=allowances;assert.throws(()=>verify(environment,policies,protection));
 }
});

test('authenticated plan handoff rejects tampering, wrong source, wrong operation and stale plans',()=>{
 process.env.PLAN_ENCRYPTION_KEY=Buffer.alloc(32,7).toString('base64');
 const sha='a'.repeat(40), bytes=Buffer.from('dummy plan, no infrastructure');
 const encrypted=seal(bytes,{sha,operation:'apply',created:new Date().toISOString()});
 const result=open(encrypted);assert.deepEqual(result.bytes,bytes);assert.doesNotThrow(()=>validatePlan(result,sha,'apply'));
 const damaged=JSON.parse(encrypted);damaged.data=(damaged.data[0]==='A'?'B':'A')+damaged.data.slice(1);assert.throws(()=>open(JSON.stringify(damaged)));
 assert.throws(()=>validatePlan(result,'b'.repeat(40),'apply'));assert.throws(()=>validatePlan(result,sha,'destroy'));
 assert.throws(()=>validatePlan({...result,created:'2000-01-01'},sha,'apply'));
});
test('destroy requires exact explicit site-only phrase',()=>{
 assert.throws(()=>confirmDestroy('','destroy'));assert.throws(()=>confirmDestroy('DESTROY','destroy'));
 assert.doesNotThrow(()=>confirmDestroy('DESTROY production SITE ONLY','destroy'));
 assert.throws(()=>confirmDestroy('','other'));
});
test('drift classifies 0/1/2 distinctly and workflow captures nonzero under runner errexit',()=>{
 assert.equal(driftStatus(0),'NO_DRIFT');assert.equal(driftStatus(2),'DRIFT');assert.throws(()=>driftStatus(1));assert.throws(()=>driftStatus(127));
 const workflow=readFileSync('workflow-templates/drift.yml','utf8');
 assert.match(workflow,/if terraform[\s\S]*then result=0; else result=\$\?; fi/);
 assert.doesNotMatch(workflow,/terraform[^\n]*\bapply\b/);
});
test('content accepts exact commit only and fixed asset allowlist',()=>{
 for(const invalid of ['main','a'.repeat(39),'$(id)','../secret','a;echo secret']) assert.throws(()=>validateRevision(invalid));
 assert.equal(validateRevision('a'.repeat(40)),'a'.repeat(40));assert.deepEqual(ASSETS,['index.html','styles.css','app.js','deployment.json']);
});
test('repository policy rejects negative unsafe workflow and insecure IaC mutations',()=>{
 const python='.tools/venv/bin/python';
 const code=`from scripts.security import inspect\nassert inspect({'bad.yml':'on: pull_request_target\\npermissions: write-all\\nsteps:\\n - uses: actions/checkout@main'})\nassert inspect({'bad.tf':'block_public_acls = false'})\nassert inspect({'bad.tf':'"token.actions.githubusercontent.com:sub" = "repo:org/*"'})\nassert inspect({'bad.yml':'permissions:\\n  id-token: write\\non:\\n  pull_request:'})\nprint('negative unsafe workflow and IaC fixtures rejected')`;
 const result=execFileSync(python,['-c',code],{encoding:'utf8'});assert.match(result,/fixtures rejected/);
});

test('verification stage has exactly one credential-free executable workflow',()=>{
 const active=readdirSync('.github/workflows').filter(name=>/\.ya?ml$/.test(name));
 assert.deepEqual(active,['ci.yml']);
 const ci=readFileSync('.github/workflows/ci.yml','utf8');
 assert.doesNotMatch(ci,/id-token:|secrets\.|configure-aws-credentials|environment:|terraform (apply|destroy)/);
 assert.match(ci,/scripts\/run-checks\.py/);
 assert.deepEqual(readdirSync('workflow-templates').filter(name=>/\.ya?ml$/.test(name)).sort(),['content.yml','drift.yml','infrastructure.yml']);
});
