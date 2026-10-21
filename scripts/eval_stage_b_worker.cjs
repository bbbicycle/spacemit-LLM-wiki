// Execute the same evaluation calls against the production Worker core.
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const { stripTypeScriptTypes } = require('node:module');
const root = path.resolve(__dirname, '..');
const input = JSON.parse(fs.readFileSync(0, 'utf8'));
const data = JSON.parse(fs.readFileSync(path.join(root, 'mcp-worker/src/data/wiki_graph.json')));
const source = fs.readFileSync(path.join(root, 'mcp-worker/src/index.ts'), 'utf8')
  .replace('import wikiData from "./data/wiki_graph.json";', 'const wikiData = globalThis.inputData;')
  .replace('export default {', 'globalThis.worker = {');
(async () => {
  const results = [];
  for (const [i, call] of input.calls.entries()) {
    const snapshot = structuredClone(data);
    if (call.replay_node) snapshot.nodes[call.replay_node] = input.fixture.nodes[call.replay_node];
    const sandbox = { console, Request, Response, URL, crypto, TextEncoder, inputData: snapshot, fetch: async url => {
      const item = data.raw_sources.find(x => new URL(x.raw_url).href === new URL(url).href);
      if (!item) throw Error('Unindexed source: ' + url);
      return new Response(fs.readFileSync(path.join(root, 'Sources', item.rel_path), 'utf8'));
    }};
    vm.createContext(sandbox);
    vm.runInContext(stripTypeScriptTypes(source), sandbox);
    const response = await sandbox.worker.fetch(new Request('https://eval.invalid/', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ jsonrpc: '2.0', id: i + 1, method: 'tools/call', params: { name: call.name, arguments: call.arguments } }),
    }), {});
    results.push((await response.json()).result);
  }
  process.stdout.write(JSON.stringify(results));
})().catch(e => { console.error(e); process.exitCode = 1; });
