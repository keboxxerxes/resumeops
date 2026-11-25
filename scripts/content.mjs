process.on('uncaughtException', () => { console.error('Operation failed; inspect privately without exposing command output'); process.exit(1); });
process.on('unhandledRejection', () => { console.error('Operation failed; inspect privately without exposing command output'); process.exit(1); });
import {mkdirSync,writeFileSync,readFileSync,rmSync} from 'node:fs';
import {execFileSync} from 'node:child_process';
export const ASSETS = ['index.html','styles.css','app.js','deployment.json'];
export function validateRevision(sha) { if (!/^[a-f0-9]{40}$/.test(sha ?? '')) throw new Error('Exact revision required'); return sha; }
export function buildContent(sha,directory='dist') {
  validateRevision(sha);
  execFileSync('git',['merge-base','--is-ancestor',sha,'HEAD'],{stdio:'pipe'});
  mkdirSync(directory,{recursive:true,mode:0o700});
  for (const asset of ASSETS.filter(a=>a!=='deployment.json')) {
    const mode = execFileSync('git',['ls-tree',sha,`site/${asset}`],{encoding:'utf8'});
    if (!mode.startsWith('100644 ') && !mode.startsWith('100755 ')) throw new Error('Only regular approved assets permitted');
    writeFileSync(`${directory}/${asset}`,execFileSync('git',['show',`${sha}:site/${asset}`]),{mode:0o600});
  }
  writeFileSync(`${directory}/deployment.json`,JSON.stringify({sha,date:new Date().toISOString()})+'\n');
}
if (process.argv[1]?.endsWith('content.mjs')) buildContent(process.env.CONTENT_SHA);
