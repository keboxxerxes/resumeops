import http from 'node:http';
import { readFile } from 'node:fs/promises';
const types = { 'index.html': 'text/html; charset=utf-8', 'styles.css': 'text/css; charset=utf-8', 'app.js': 'text/javascript; charset=utf-8', 'deployment.json': 'application/json' };
export default async function () {
  const server = http.createServer(async (req, res) => {
    const name = req.url === '/' ? 'index.html' : req.url.slice(1);
    if (!Object.hasOwn(types, name)) { res.writeHead(404).end(); return; }
    try { const data = await readFile(new URL(`../site/${name}`, import.meta.url)); res.writeHead(200, { 'Content-Type': types[name] }); res.end(data); }
    catch { res.writeHead(500).end(); }
  });
  await new Promise((resolve, reject) => { server.once('error', reject); server.listen(4174, '127.0.0.1', resolve); });
  return async () => { server.closeAllConnections(); await new Promise(resolve => server.close(resolve)); };
}
