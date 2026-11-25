process.on('uncaughtException', () => { console.error('Operation failed; inspect privately without exposing command output'); process.exit(1); });
process.on('unhandledRejection', () => { console.error('Operation failed; inspect privately without exposing command output'); process.exit(1); });
export function driftStatus(code) {
  if (code === 0) return 'NO_DRIFT';
  if (code === 2) return 'DRIFT';
  throw new Error('Terraform plan failed; drift status unknown');
}
if (process.argv[1]?.endsWith('drift.mjs')) console.log(driftStatus(Number(process.argv[2])));
