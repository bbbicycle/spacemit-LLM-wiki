// Node 22.13+ regression tests execute the real Worker source without deploying.
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const { stripTypeScriptTypes } = require("node:module");

const node = (id, type = "evidence", metadata = {}) => ({ id, title: id, type, domain: "test", status: "needs_review", aliases: [], content: "needle", summary: "summary", outlinks: [], backlinks: [], target_audience: [], ...metadata });
const data = { nodes: {}, aliases: {}, raw_sources: [] };
let fetched = [];
let rawText = "one\ntwo\nthree\n";
const sandbox = { inputData: data, console, Request, Response, URL, fetch: async url => { fetched.push(url); return new Response(rawText); } };
let source = fs.readFileSync(path.join(__dirname, "src/index.ts"), "utf8")
  .replace('import wikiData from "./data/wiki_graph.json";', "const wikiData = globalThis.inputData;")
  .replace("export default {", "globalThis.worker = {");
vm.createContext(sandbox);
vm.runInContext(stripTypeScriptTypes(source), sandbox);

async function call(name, args, expectError = false) {
  const response = await sandbox.worker.fetch(new Request("https://test.invalid/", {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ jsonrpc: "2.0", id: 1, method: "tools/call", params: { name, arguments: args } })
  }), {});
  const { result } = await response.json();
  assert.equal(!!result.isError, expectError, JSON.stringify(result));
  return expectError ? result : JSON.parse(result.content[0].text);
}

(async () => {
  for (const id of ["incidental", "needle_second", "needle_first"]) data.nodes[id] = node(id);
  let result = await call("search_wiki", { query: "needle" });
  assert.deepEqual(result.map(x => x.id), ["needle_second", "needle_first", "incidental"]);
  assert.deepEqual(result.map(x => x.score), [13, 13, 3]);
  for (const name of ["incidental", "needle_second", "needle_first"]) data.raw_sources.push({ submodule: "docs-chip", file_name: name, rel_path: name, repo_path: name, title: name, headers: [], summary: "needle", raw_url: name });
  result = await call("search_raw_sources", { query: "needle" });
  assert.deepEqual(result.map(x => x.file_path), ["needle_second", "needle_first", "incidental"]);

  for (const id of Object.keys(data.nodes)) delete data.nodes[id];
  data.nodes.K3_journey = node("K3_journey", "developer_journey");
  data.nodes.K3_fact_a = node("K3_fact_a");
  data.nodes.K3_fact_b = node("K3_fact_b");
  for (const spec_name of ["K3", "K3_journey", "", " ", ".md"]) await call("get_evidence_fact", { spec_name }, true);
  assert.equal((await call("get_evidence_fact", { spec_name: "K3_fact_a.md" })).type, "evidence");
  for (const item of Object.values(data.nodes)) item.aliases = ["shared"];
  await call("get_evidence_fact", { spec_name: "shared" }, true);
  for (const id of Object.keys(data.nodes)) delete data.nodes[id];
  const metadata = { verification_status: "unverified", external_use: false, source_file: ["Sources/docs-chip/example.md"], source_commit: "abc", source_section: "voltage", source_locator: "example.md:10-20", source_resolution: "partial", source_note: "measurement conditions need review", source_checked_at: "2026-10-13", source_related_file: "Sources/docs-chip/related.md", source_related_commit: "def", metric_source_resolution: "unresolved", thermal_source_resolution: "unresolved", chip: "K3", product: "test board", verified_at: "2026-10-01", conflicts: ["needs review"], source_origin: "GitHub", source_tier: "tier_1", effective_until: "2026-12-01" };
  data.nodes.fact = node("fact", "evidence", metadata);
  for (const result of [await call("get_evidence_fact", { spec_name: "fact" }), (await call("search_wiki", { query: "fact" }))[0]]) {
    for (const [key, value] of Object.entries({ ...metadata, status: "needs_review" })) assert.deepEqual(result[key], value);
  }

  data.raw_sources.length = 0;
  const item = { submodule: "docs-ros", file_name: "平台 概览.md", rel_path: "docs-ros/zh/平台 概览.md", repo_path: "zh/平台 概览.md", source_commit: "a".repeat(40), raw_url: `https://raw.githubusercontent.com/spacemit-com/docs-ros/${"a".repeat(40)}/zh/平台 概览.md` };
  data.raw_sources.push(item);
  result = await call("read_raw_source_file", { file_path_or_url: item.raw_url.replace("a".repeat(40), "main"), start_line: 2, end_line: 2 });
  assert.equal(result.content, "two");
  assert.equal(result.source_commit, "a".repeat(40));
  assert.equal(result.origin, "github");
  assert.ok(fetched.at(-1).includes("%20"));
  assert.ok(fetched.at(-1).includes("%E5%B9%B3"));
  assert.ok(fetched.at(-1).includes(`/${"a".repeat(40)}/`));
  fetched = [];
  await call("read_raw_source_file", { file_path_or_url: "https://example.com/file" }, true);
  await call("read_raw_source_file", { file_path_or_url: "../AGENTS.md" }, true);
  for (const start_line of [0, -1, 1.5, true, null, "1"]) await call("read_raw_source_file", { file_path_or_url: item.rel_path, start_line }, true);
  await call("read_raw_source_file", { file_path_or_url: item.rel_path, start_line: 3, end_line: 2 }, true);
  assert.equal(fetched.length, 0);
  rawText = "line\n".repeat(300);
  result = await call("read_raw_source_file", { file_path_or_url: item.rel_path });
  assert.equal(result.content.split("\n").length, 300);
  console.log("Worker runtime regression checks passed: ranking, types, ambiguity, metadata, pinned sources, URL encoding, ranges, full-read compatibility.");
})().catch(error => { console.error(error); process.exitCode = 1; });
