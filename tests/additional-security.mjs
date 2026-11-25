import assert from 'node:assert/strict';
import {gate,verifyProtection} from '../scripts/gate.mjs';
import {seal,open,validatePlan} from '../scripts/plan-crypto.mjs';
const owner='owner';
const repositoryName='owner/independent';
let repositoryMetadata={id:2,name:'independent',full_name:repositoryName,owner:{id:1,login:owner,type:'User'}};
const environment={can_admins_bypass:false,protection_rules:[{type:'required_reviewers',prevent_self_review:false,reviewers:[{type:'User',reviewer:{id:1,login:owner}}]}],deployment_branch_policy:{custom_branch_policies:true,protected_branches:false}};
const policies={total_count:1,branch_policies:[{name:'main',type:'branch'}]};
const branch={enforce_admins:{enabled:true},required_pull_request_reviews:{required_approving_review_count:0,dismiss_stale_reviews:false,require_last_push_approval:false,require_code_owner_reviews:false},required_status_checks:{strict:true,contexts:['verify']},allow_force_pushes:{enabled:false},allow_deletions:{enabled:false},required_conversation_resolution:{enabled:true}};
process.env.ALLOW_AWS_OPERATIONS='true';process.env.GITHUB_REF='refs/heads/main';process.env.GITHUB_SHA='a'.repeat(40);process.env.GITHUB_REPOSITORY='owner/independent';process.env.GH_PROTECTION_TOKEN='dummy-local-test-value';
let status=200,metadataStatus=200,stale=false,invalidJson=false;
let requested=[];
globalThis.fetch=async url=>{
 requested.push(url);
 const metadataRequest=url.toLowerCase()==='https://api.github.com/repos/owner/independent';
 const responseStatus=metadataRequest?metadataStatus:status;
 return {ok:responseStatus===200,status:responseStatus,json:async()=>{
  if(invalidJson)throw new Error('Dummy malformed JSON response');
  if(metadataRequest)return repositoryMetadata;
  return url.endsWith('git/ref/heads/main')?{object:{sha:(stale?'b':'a').repeat(40)}}:url.endsWith('branches/main/protection')?branch:url.endsWith('deployment-branch-policies')?policies:environment;
 }};
};
await gate(['production-content']);
assert.equal(requested[0],'https://api.github.com/repos/owner/independent');
await gate(['production-plan','production-apply']);
branch.required_pull_request_reviews.dismiss_stale_reviews=true;await gate(['production-content']);branch.required_pull_request_reviews.dismiss_stale_reviews=false;
branch.required_pull_request_reviews.bypass_pull_request_allowances={users:[],teams:[],apps:[]};await gate(['production-content']);delete branch.required_pull_request_reviews.bypass_pull_request_allowances;
process.env.GITHUB_REPOSITORY='OWNER/independent';await gate(['production-content']);process.env.GITHUB_REPOSITORY='owner/independent';
process.env.GITHUB_REF='refs/pull/1/merge';await assert.rejects(()=>gate(['production-content']));process.env.GITHUB_REF='refs/heads/main';
stale=true;await assert.rejects(()=>gate(['production-content']));stale=false;
for(const code of [403,404]){status=code;await assert.rejects(()=>gate(['production-content']));}status=200;
invalidJson=true;await assert.rejects(()=>gate(['production-content']));invalidJson=false;
process.env.ALLOW_AWS_OPERATIONS='false';await assert.rejects(()=>gate(['production-content']));process.env.ALLOW_AWS_OPERATIONS='true';
for(const repository of [undefined,'','owner','owner/../bad','bad owner/repo','-owner/repo','owner/..']){
 if(repository===undefined)delete process.env.GITHUB_REPOSITORY;else process.env.GITHUB_REPOSITORY=repository;
 await assert.rejects(()=>gate(['production-content']));
}process.env.GITHUB_REPOSITORY='owner/independent';
for(const environments of [undefined,[],['production-content','production-content'],['other-environment'],'production-content'])await assert.rejects(()=>gate(environments));
environment.protection_rules[0].reviewers[0].reviewer.login='different';await assert.rejects(()=>gate(['production-content']));environment.protection_rules[0].reviewers[0].reviewer.login=owner;
const missing=structuredClone(branch);delete missing.required_pull_request_reviews.required_approving_review_count;assert.throws(()=>verifyProtection(environment,policies,missing,repositoryMetadata,repositoryName));
const codeOwners=structuredClone(branch);codeOwners.required_pull_request_reviews.require_code_owner_reviews=true;assert.throws(()=>verifyProtection(environment,policies,codeOwners,repositoryMetadata,repositoryName));
const savedMetadata=structuredClone(repositoryMetadata);
for(const invalidMetadata of [undefined,null,{},[],false,{...savedMetadata,owner:{...savedMetadata.owner,type:'Organization'}},{...savedMetadata,owner:{...savedMetadata.owner,type:'Unknown'}},{...savedMetadata,owner:null},{...savedMetadata,full_name:'owner/other'},{...savedMetadata,owner:{...savedMetadata.owner,login:'different'}},{...savedMetadata,name:'other'},{...savedMetadata,owner:{...savedMetadata.owner,id:'1'}},Object.create(savedMetadata)]){
 repositoryMetadata=invalidMetadata;requested=[];await assert.rejects(()=>gate(['production-content']));assert.equal(requested.length,1);
}repositoryMetadata=savedMetadata;
for(const code of [403,404,500]){metadataStatus=code;requested=[];await assert.rejects(()=>gate(['production-content']));assert.equal(requested.length,1);}metadataStatus=200;
for(const allowance of [undefined,null,false,'',{},[],{users:[],teams:[],apps:[],unknown:[]}]){
 branch.required_pull_request_reviews.bypass_pull_request_allowances=allowance;await assert.rejects(()=>gate(['production-content']));
}delete branch.required_pull_request_reviews.bypass_pull_request_allowances;
for(const staleValue of [undefined,null,'false',0]){
 branch.required_pull_request_reviews.dismiss_stale_reviews=staleValue;await assert.rejects(()=>gate(['production-content']));
}branch.required_pull_request_reviews.dismiss_stale_reviews=false;
delete process.env.GH_PROTECTION_TOKEN;await assert.rejects(()=>gate(['production-content']));
console.log('PASS: independent User-metadata-bound gate, personal omission compatibility and API/malformed/bypass negatives');
process.env.PLAN_ENCRYPTION_KEY=Buffer.alloc(32,7).toString('base64');const sha='a'.repeat(40), encrypted=seal(Buffer.from('dummy no-infrastructure bytes'),{sha,operation:'apply',created:new Date().toISOString()});
const p=open(encrypted);assert.throws(()=>validatePlan({...p,created:new Date(Date.now()+100000).toISOString()},sha,'apply'));
process.env.PLAN_ENCRYPTION_KEY=Buffer.alloc(32,8).toString('base64');assert.throws(()=>open(encrypted));
process.env.PLAN_ENCRYPTION_KEY='';assert.throws(()=>open(encrypted));
console.log('PASS: independent plan wrong-key/missing-key/future-date rejection');
