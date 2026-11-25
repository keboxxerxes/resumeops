import test from 'node:test';
import assert from 'node:assert/strict';
import {execFileSync} from 'node:child_process';
import {readFileSync,readdirSync} from 'node:fs';
import {seal,open,validatePlan} from '../scripts/plan-crypto.mjs';
import {verifyProtection} from '../scripts/gate.mjs';
import {validateRevision,ASSETS} from '../scripts/content.mjs';
import {confirmDestroy} from '../scripts/confirm.mjs';
import {driftStatus} from '../scripts/drift.mjs';
const environment={can_admins_bypass:false,protection_rules:[{type:'required_reviewers',prevent_self_review:true,reviewers:[{reviewer:{id:1}}]}],deployment_branch_policy:{custom_branch_policies:true,protected_branches:false}};
const policies={branch_policies:[{name:'main',type:'branch'}]};
const branch={enforce_admins:{enabled:true},required_pull_request_reviews:{required_approving_review_count:1,dismiss_stale_reviews:true,require_last_push_approval:true,bypass_pull_request_allowances:{users:[],teams:[],apps:[]}},required_status_checks:{strict:true,contexts:['verify']}};
test('actual protection checks reject every bypass and wrong branch',()=>{
 assert.doesNotThrow(()=>verifyProtection(environment,policies,branch));
 for(const edit of [e=>e.can_admins_bypass=true,e=>e.protection_rules[0].prevent_self_review=false,e=>e.protection_rules[0].reviewers=[],e=>e.deployment_branch_policy.protected_branches=true]) {
  const e=structuredClone(environment);edit(e);assert.throws(()=>verifyProtection(e,policies,branch));
 }
 for(const policy of [{branch_policies:[]},{branch_policies:[{name:'*',type:'branch'}]},{branch_policies:[{name:'main',type:'tag'}]}]) assert.throws(()=>verifyProtection(environment,policy,branch));
 const missing=structuredClone(branch);delete missing.required_pull_request_reviews.required_approving_review_count;assert.throws(()=>verifyProtection(environment,policies,missing));
 const b=structuredClone(branch);b.required_pull_request_reviews.bypass_pull_request_allowances.users=[{}];assert.throws(()=>verifyProtection(environment,policies,b));
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
