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
  ...[{}, { start_line: 201 }, { start_line: 1, end_line: 100000 }, { start_line: 999999 }].map(options => ['read_raw_source_file', { file_path_or_url: 'docs-chip/zh/key_stone/k1/k1_hw/k1_hw_design_guide.md', ...options }]),
  ...Object.values(data.nodes).map(x => x.type === 'evidence' ? ['get_evidence_fact', { spec_name: x.id }] : x.type === 'knowledge_atom' ? ['read_knowledge_atom', { atom_name: x.id }] : ['get_developer_journey', { board_or_task: x.id }]),
];
const messages = requests.map(([name, args], i) => ({ jsonrpc: '2.0', id: i + 1, method: 'tools/call', params: { name, arguments: args } }));
const python = execFileSync('python3', ['-B', path.join(root, 'mcp/server.py')], { input: messages.map(x => JSON.stringify(x)).join('\n') + '\n', encoding: 'utf8' }).trim().split('\n').map(x => JSON.parse(x).result);
const sandbox = { console, Request, Response, URL, crypto, TextEncoder, inputData: data, fetch: async url => {
  const item = data.raw_sources.find(x => new URL(x.raw_url).href === new URL(url).href);
  assert.ok(item, `unindexed fetch ${url}`);
  const localFile = path.join(root, 'Sources', item.rel_path);
  if (fs.existsSync(localFile)) {
    return new Response(fs.readFileSync(localFile, 'utf8'));
  }
  return globalThis.fetch(url, { headers: { "User-Agent": "Spacemit-MCP-Worker" } });
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
  const noticeCases = JSON.parse(fs.readFileSync(path.join(root, 'mcp/notice_cases.json')));
  const pyNotices = JSON.parse(execFileSync('python3', ['-B', '-c',
    'import json,sys; sys.path.insert(0,"mcp"); from server import build_agent_notice; print(json.dumps([build_agent_notice(n) for n in json.load(sys.stdin)]))'],
    { cwd: root, input: JSON.stringify(noticeCases.map(c => c.metadata)), encoding: 'utf8' }));
  for (const [i, test] of noticeCases.entries()) {
    assert.deepEqual(JSON.parse(JSON.stringify(sandbox.buildAgentNotice(test.metadata))), pyNotices[i], test.id);
  }
  async function healthCase(change, env = {}) {
    const healthData = structuredClone(data);
    change(healthData);
    const isolated = { console, Request, Response, URL, crypto, TextEncoder, inputData: healthData };
    vm.createContext(isolated);
    vm.runInContext(stripTypeScriptTypes(source), isolated);
    return isolated.worker.fetch(new Request('https://test.invalid/health'), env);
  }
  const healthy = await healthCase(() => {}, { DB: {}, DEPLOYMENT_REF: 'test-deployment' });
  assert.equal(healthy.status, 200);
  const health = await healthy.json();
  assert.equal(health.status, 'ok');
  assert.equal(health.deployment_ref, 'test-deployment');
  assert.equal(health.d1_bound, true);
  assert.deepEqual(health.build_meta, data.build_meta);
  const unbound = await (await healthCase(() => {})).json();
  assert.equal(unbound.d1_bound, false);
  for (const corrupt of [
    d => { delete d.build_meta; },
    d => { d.build_meta.counts.total_nodes++; },
    d => { d.nodes[Object.keys(d.nodes)[0]].content += 'corrupt'; },
    d => { d.build_meta.sources_commits['docs-chip'] = 'bad'; },
    d => { d.source_versions = null; },
  ]) {
    const response = await healthCase(corrupt);
    assert.equal(response.status, 503);
    assert.equal((await response.json()).status, 'error');
  }
  const wrongMethod = await sandbox.worker.fetch(new Request('https://test.invalid/health', { method: 'POST' }), {});
  assert.equal(wrongMethod.status, 405);
  const listMessage = { jsonrpc: '2.0', id: 'schemas', method: 'tools/list', params: {} };
  const pyTools = JSON.parse(execFileSync('python3', ['-B', path.join(root, 'mcp/server.py')], { input: JSON.stringify(listMessage) + '\n', encoding: 'utf8' })).result.tools;
  const schemaResponse = await sandbox.worker.fetch(new Request('https://test.invalid/', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(listMessage) }), {});
  const cfTools = (await schemaResponse.json()).result.tools;
  for (const tool of pyTools) assert.deepEqual(cfTools.find(x => x.name === tool.name).inputSchema, tool.inputSchema, tool.name);
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
  console.log(`Production index parity passed: ${messages.length} calls, all node metadata/notices, health integrity, PMIC ranking, factual corrections, Chinese paths and pinned excerpts.`);
})().catch(error => { console.error(error); process.exitCode = 1; });
