process.on('uncaughtException', () => { console.error('Operation failed; inspect privately without exposing command output'); process.exit(1); });
process.on('unhandledRejection', () => { console.error('Operation failed; inspect privately without exposing command output'); process.exit(1); });
export function confirmDestroy(value,operation) {
  if (operation === 'destroy' && value !== 'DESTROY production SITE ONLY') throw new Error('Explicit site-only destruction confirmation required');
  if (!['apply','destroy'].includes(operation)) throw new Error('Unknown infrastructure operation');
}
if (process.argv[1]?.endsWith('confirm.mjs')) confirmDestroy(process.env.CONFIRMATION,process.env.OPERATION);
