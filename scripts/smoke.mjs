process.on('uncaughtException', () => { console.error('Operation failed; inspect privately without exposing command output'); process.exit(1); });
process.on('unhandledRejection', () => { console.error('Operation failed; inspect privately without exposing command output'); process.exit(1); });
const {SITE_HOST,CONTENT_SHA} = process.env;
if (!/^[a-z0-9]+\.cloudfront\.net$/.test(SITE_HOST ?? '')) throw new Error('Expected default CloudFront hostname');
for (let i=0;i<12;i++) {
  try {
    const response = await fetch(`https://${SITE_HOST}/`,{redirect:'error',signal:AbortSignal.timeout(15000)});
    if (!response.ok || !response.headers.get('content-security-policy') || !response.headers.get('strict-transport-security')) throw new Error('Missing HTTPS response/security headers');
    const meta = await fetch(`https://${SITE_HOST}/deployment.json`,{cache:'no-store',signal:AbortSignal.timeout(15000)}).then(r=>r.json());
    if (meta.sha !== CONTENT_SHA || !Number.isFinite(Date.parse(meta.date))) throw new Error('Metadata mismatch');
    console.log('HTTPS headers and deployed revision verified'); process.exit(0);
  } catch { if(i===11) throw new Error('HTTPS smoke verification failed'); await new Promise(r=>setTimeout(r,10000)); }
}
