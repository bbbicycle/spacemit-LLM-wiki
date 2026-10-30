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
  assert.deepEqual(result.map(x => x.score), [29.4, 29.4, 5.3]);
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
  const metadata = { verification_status: "unverified", external_use: false, source_file: ["Sources/docs-chip/example.md"], source_commit: "abc", source_section: "voltage", source_locator: "example.md:10-20", source_resolution: "partial", source_note: "measurement conditions need review", source_checked_at: "2026-10-13", source_related_file: "Sources/docs-chip/related.md", source_related_commit: "def", freshness: "stale", stale_paths: ["Sources/docs-chip/example.md"], unknown_paths: [], checked_against_commit: { "docs-chip": "new" }, source_freshness: [{ freshness: "stale" }], metric_source_resolution: "unresolved", thermal_source_resolution: "unresolved", chip: "K3", product: "test board", verified_at: "2026-10-01", conflicts: ["needs review"], source_origin: "GitHub", source_tier: "tier_1", effective_until: "2026-12-01" };
  data.nodes.fact = node("fact", "evidence", metadata);
  const factRes = await call("get_evidence_fact", { spec_name: "fact" });
  for (const [key, value] of Object.entries({ ...metadata, status: "needs_review" })) assert.deepEqual(factRes[key], value);
  const searchRes = (await call("search_wiki", { query: "fact" }))[0];
  for (const key of ["id", "title", "type", "domain", "score", "status", "freshness", "verification_status", "summary", "hint"]) {
    assert.ok(key in searchRes, `missing ${key}`);
  }
  assert.equal(searchRes.freshness, "stale");
  assert.equal(searchRes.source_freshness, undefined);
  assert.equal(searchRes.metric_source_resolution, undefined);
  assert.equal(searchRes.source_file, undefined);

  for (const id of Object.keys(data.nodes)) delete data.nodes[id];
  data.nodes.k3_strap = node("k3_strap", "evidence", { title: "K3 启动模式与 Strap 管脚配置", chip: "K3" });
  data.nodes.k1_strap = node("k1_strap", "evidence", { title: "K1 启动模式与 Strap 管脚配置", chip: "K1" });
  assert.equal((await call("search_wiki", { query: "K3 Strap 启动" }))[0].id, "k3_strap");
  assert.equal((await call("search_wiki", { query: "K1 启动模式" }))[0].id, "k1_strap");

  const noticeCases = JSON.parse(fs.readFileSync(path.join(__dirname, "../mcp/notice_cases.json"), "utf8"));
  for (const test of noticeCases) {
    for (const [kind, tool, parameter, content] of [
      ["evidence", "get_evidence_fact", "spec_name", "full_table_content"],
      ["knowledge_atom", "read_knowledge_atom", "atom_name", "full_markdown_content"],
      ["developer_journey", "get_developer_journey", "board_or_task", "full_markdown_content"],
    ]) {
      for (const id of Object.keys(data.nodes)) delete data.nodes[id];
      data.nodes[test.id] = node(test.id, kind, test.metadata);
      const detail = await call(tool, { [parameter]: test.id });
      assert.deepEqual(detail.agent_notice.map(n => n.code), test.codes, `${test.id}: ${kind}`);
      assert.equal(detail[content], "needle");
      assert.equal(detail.verification_status, test.metadata.verification_status);
      const summary = (await call("search_wiki", { query: test.id }))[0];
      for (const code of test.codes) assert.ok(summary.hint.includes(code));
      assert.equal(summary.agent_notice, undefined);
    }
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
  rawText = Array.from({ length: 1200 }, (_, i) => String(i + 1)).join("\n");
  result = await call("read_raw_source_file", { file_path_or_url: item.rel_path });
  assert.equal(result.content.split("\n").length, 200);
  assert.equal(result.has_more, true);
  assert.equal(result.next_start_line, 201);
  result = await call("read_raw_source_file", { file_path_or_url: item.rel_path, start_line: result.next_start_line });
  assert.equal(result.content.split("\n")[0], "201");
  assert.equal(result.end_line, 400);
  for (const options of [{ start_line: 10, end_line: 1200 }, { end_line: 1200 }]) {
    result = await call("read_raw_source_file", { file_path_or_url: item.rel_path, ...options });
    assert.equal(result.content.split("\n").length, 500);
    assert.equal(result.end_line, (options.start_line ?? 1) + 499);
    assert.equal(result.next_start_line, result.end_line + 1);
  }
  for (const [body, options, count, end, more] of [
    ["", {}, 0, 0, false], ["one\r\ntwo\rthree\n", {}, 3, 3, false],
    ["line\n".repeat(200), {}, 200, 200, false], ["line\n".repeat(201), {}, 200, 200, true],
    ["one\ntwo\n", { start_line: 3 }, 0, 2, false],
    ["line\n".repeat(800), { start_line: 2, end_line: 2 }, 1, 2, true],
  ]) {
    rawText = body;
    result = await call("read_raw_source_file", { file_path_or_url: item.rel_path, ...options });
    assert.equal(result.content ? result.content.split("\n").length : 0, count);
    assert.equal(result.end_line, end);
    assert.equal(result.has_more, more);
    assert.equal(result.next_start_line, more ? end + 1 : null);
  }

  // Populate sensitive rows so an accidental authorization bypass cannot pass
  // merely because the fixture returned no query or feedback details.
  for (const [label, configuredToken, suppliedToken, authorized] of [
    ["missing configuration", undefined, null, false],
    ["missing configuration with supplied token", undefined, "test-stats-token", false],
    ["empty configuration and empty supplied token", "", "", false],
    ["configured token absent from request", "test-stats-token", null, false],
    ["empty supplied token", "test-stats-token", "", false],
    ["incorrect token", "test-stats-token", "incorrect", false],
    ["correct token", "test-stats-token", "test-stats-token", true],
  ]) {
    const statements = [];
    const DB = { prepare(sql) {
      statements.push(sql);
      return {
        async first() {
          if (sql.includes("FROM mcp_issue_reports")) return { count: 2 };
          return { count: sql.includes("WHERE status") ? 7 : 42 };
        },
        async all() {
          if (sql.startsWith("SELECT category")) return { results: [{ category: "test category", count: 42 }] };
          if (sql.startsWith("SELECT query_text")) return { results: [{
            query_text: "PRIVATE_QUERY_SENTINEL", tool_name: "search_wiki", status: "ERROR",
            error_message: "PRIVATE_ERROR_SENTINEL", timestamp: "2026-10-30 00:00:00",
          }] };
          if (sql.startsWith("SELECT topic")) return { results: [{
            topic: "PRIVATE_TOPIC_SENTINEL", issue_type: "MISSING_DOC",
            description: "PRIVATE_FEEDBACK_SENTINEL", timestamp: "2026-10-30 00:00:00",
          }] };
          throw Error("Unexpected stats SQL: " + sql);
        },
      };
    } };
    const url = new URL("https://test.invalid/stats");
    if (suppliedToken !== null) url.searchParams.set("token", suppliedToken);
    const env = { DB, ...(configuredToken === undefined ? {} : { STATS_TOKEN: configuredToken }) };
    const response = await sandbox.worker.fetch(new Request(url), env);
    assert.equal(response.status, 200, label);
    const html = await response.text();
    assert.ok(html.includes("总查询调用次数") && html.includes(">42</div>"), label);
    assert.ok(html.includes("test category"), label);
    for (const sentinel of ["PRIVATE_QUERY_SENTINEL", "PRIVATE_ERROR_SENTINEL", "PRIVATE_TOPIC_SENTINEL", "PRIVATE_FEEDBACK_SENTINEL"]) {
      assert.equal(html.includes(sentinel), authorized, `${label}: ${sentinel}`);
    }
    assert.equal(statements.some(sql => sql.startsWith("SELECT query_text")), authorized, `${label}: query detail SQL`);
    assert.equal(statements.some(sql => sql.startsWith("SELECT topic")), authorized, `${label}: feedback detail SQL`);
    assert.equal(html.includes("明细查询日志已保护"), !authorized, label);
    assert.equal(html.includes("反馈明细已保护"), !authorized, label);
  }
  console.log("Worker runtime regression checks passed: ranking, types, ambiguity, metadata, pinned sources, URL encoding, bounded pages, continuation, EOF boundaries and stats access protection.");
})().catch(error => { console.error(error); process.exitCode = 1; });
