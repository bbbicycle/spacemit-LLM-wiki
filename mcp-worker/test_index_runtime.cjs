// Compare both production transports using the actual published index.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const { execFileSync } = require('node:child_process');
const { stripTypeScriptTypes } = require('node:module');
const root = path.resolve(__dirname, '..');
const data = JSON.parse(fs.readFileSync(path.join(__dirname, 'src/data/wiki_graph.json')));
const requests = [
  ['search_wiki', { query: 'PMIC' }],
  ['search_wiki', { query: '' }],
  ['get_evidence_fact', { spec_name: 'K3' }],
  ['get_evidence_fact', { spec_name: 'K3_Pico_开发板快速上手向导' }],
  ['get_evidence_fact', { spec_name: 'k1_terminal_products_specs' }],
  ['get_evidence_fact', { spec_name: 'k3_ai_performance_data' }],
  ['search_raw_sources', { query: 'MUSE Paper', submodule: 'docs-product' }],
  ['read_raw_source_file', { file_path_or_url: 'docs-product/zh/k1_series/k1_muse_paper/root_overview.md', start_line: 39, end_line: 54 }],
  ['read_raw_source_file', { file_path_or_url: 'docs-ros/zh/k3/01-平台概览.md', start_line: 1, end_line: 5 }],
  ...Object.values(data.nodes).filter(x => x.type === 'evidence').map(x => ['get_evidence_fact', { spec_name: x.id }]),
];
const messages = requests.map(([name, args], i) => ({ jsonrpc: '2.0', id: i + 1, method: 'tools/call', params: { name, arguments: args } }));
const python = execFileSync('python3', ['-B', path.join(root, 'mcp/server.py')], { input: messages.map(x => JSON.stringify(x)).join('\n') + '\n', encoding: 'utf8' }).trim().split('\n').map(x => JSON.parse(x).result);
const sandbox = { console, Request, Response, URL, inputData: data, fetch: async url => {
  const item = data.raw_sources.find(x => new URL(x.raw_url).href === new URL(url).href);
  assert.ok(item, `unindexed fetch ${url}`);
  return new Response(fs.readFileSync(path.join(root, 'Sources', item.rel_path), 'utf8'));
}};
vm.createContext(sandbox);
let source = fs.readFileSync(path.join(__dirname, 'src/index.ts'), 'utf8').replace('import wikiData from "./data/wiki_graph.json";', 'const wikiData = globalThis.inputData;').replace('export default {', 'globalThis.worker = {');
vm.runInContext(stripTypeScriptTypes(source), sandbox);
(async () => {
  for (const [i, message] of messages.entries()) {
    const response = await sandbox.worker.fetch(new Request('https://test.invalid/', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(message) }), {});
    const worker = (await response.json()).result;
    assert.equal(!!worker.isError, !!python[i].isError, requests[i][0]);
    if (worker.isError) continue; // Error wording may differ; both must reject.
    const py = JSON.parse(python[i].content[0].text);
    const cf = JSON.parse(worker.content[0].text);
    if (requests[i][0] === 'read_raw_source_file') { delete py.origin; delete cf.origin; }
    assert.deepEqual(cf, py, JSON.stringify(requests[i]));
  }
  const ranked = JSON.parse(python[0].content[0].text);
  assert.ok(ranked.slice(0, 3).every(x => /PMIC|pmic/.test(x.id)), 'PMIC topics must outrank incidental mentions');
  const paper = JSON.parse(python[4].content[0].text);
  assert.equal(paper.verification_status, 'verified');
  assert.equal(paper.status, 'needs_review');
  assert.match(paper.full_table_content, /10\.95 寸 LCD/);
  assert.match(paper.full_table_content, /128 \/ 256 GB eMMC/);
  const ai = JSON.parse(python[5].content[0].text);
  assert.equal(ai.verification_status, 'unverified');
  assert.equal(ai.external_use, false);
  assert.match(ai.full_table_content, /12\.32/);
  assert.match(ai.full_table_content, /bianbu-4\.0rc3/);
  console.log(`Production index parity passed: ${messages.length} calls, all Evidence metadata, PMIC ranking, factual corrections, Chinese paths and pinned excerpts.`);
})().catch(error => { console.error(error); process.exitCode = 1; });
