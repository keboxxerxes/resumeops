process.on('uncaughtException', () => { console.error('Operation failed; inspect privately without exposing command output'); process.exit(1); });
process.on('unhandledRejection', () => { console.error('Operation failed; inspect privately without exposing command output'); process.exit(1); });
import {createCipheriv, createDecipheriv, randomBytes, createHash} from 'node:crypto';
import {readFileSync,writeFileSync,mkdirSync} from 'node:fs';
const hash = value => createHash('sha256').update(value).digest('hex');
function key() {
  const result = Buffer.from(process.env.PLAN_ENCRYPTION_KEY ?? '', 'base64');
  if (result.length !== 32) throw new Error('A 32-byte base64 plan encryption key is required');
  return result;
}
export function seal(bytes, metadata) {
  const nonce = randomBytes(12), cipher = createCipheriv('aes-256-gcm', key(), nonce);
  const payload = JSON.stringify({...metadata, digest: hash(bytes), plan: bytes.toString('base64')});
  return JSON.stringify({nonce: nonce.toString('base64'), tag: null, data: null, ...(() => {
    const data = Buffer.concat([cipher.update(payload), cipher.final()]);
    return {data: data.toString('base64'), tag: cipher.getAuthTag().toString('base64')};
  })()});
}
export function open(envelope) {
  const e = JSON.parse(envelope), decipher = createDecipheriv('aes-256-gcm', key(), Buffer.from(e.nonce,'base64'));
  decipher.setAuthTag(Buffer.from(e.tag,'base64'));
  const payload = JSON.parse(Buffer.concat([decipher.update(Buffer.from(e.data,'base64')),decipher.final()]).toString());
  const bytes = Buffer.from(payload.plan,'base64');
  if (hash(bytes) !== payload.digest) throw new Error('Plan integrity check failed');
  return {...payload,bytes};
}
export function validatePlan(p, sha, operation, now = Date.now()) {
  if (p.sha !== sha || p.operation !== operation || !['apply','destroy'].includes(operation)) throw new Error('Plan revision/operation mismatch');
  const age = now - Date.parse(p.created);
  if (!Number.isFinite(age) || age < 0 || age > 24*3600*1000) throw new Error('Plan expired');
}
if (process.argv[1]?.endsWith('plan-crypto.mjs')) {
  const [mode,input,output] = process.argv.slice(2);
  if (mode === 'seal') {
    const bytes = readFileSync(input);
    writeFileSync(output,seal(bytes,{sha:process.env.GITHUB_SHA,operation:process.env.OPERATION,created:new Date().toISOString()}),{mode:0o600});
    console.log(`Exact plan SHA256: ${hash(bytes)} (review substantive plan privately before approval)`);
  } else if (mode === 'open' || mode === 'review') {
    const p = open(readFileSync(input,'utf8'));
    validatePlan(p,process.env.GITHUB_SHA,process.env.OPERATION);
    writeFileSync(output,p.bytes,{mode:0o600});
    console.log(`Verified exact plan SHA256: ${p.digest}`);
  } else throw new Error('Use seal, open or review');
}
