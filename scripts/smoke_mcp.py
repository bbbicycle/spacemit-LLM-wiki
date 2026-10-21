#!/usr/bin/env python3
"""Read-only deployment smoke test: health, SSE, MCP tools and pinned pages."""

import argparse
import json
import sys
from urllib.parse import urlsplit
from urllib.request import ProxyHandler, Request, build_opener


def smoke(url, expected_ref=None, index=None, proxy=None):
    origin = url.rstrip("/")
    opener = build_opener(ProxyHandler({"http": proxy, "https": proxy})) if proxy else build_opener()

    def request(path, body=None):
        data = json.dumps(body).encode() if body is not None else None
        return opener.open(Request(origin + path, data=data, headers={
            "Content-Type": "application/json", "User-Agent": "Spacemit-MCP-Smoke",
        }), timeout=30)

    with request("/health") as response:
        health = json.load(response)
    assert health["status"] == "ok", health
    assert isinstance(health["d1_bound"], bool), health
    if expected_ref:
        assert health["deployment_ref"] == expected_ref, "Unexpected deployed ref"
    if index:
        assert health["version"] == index["version"], "Unexpected index version"
        assert health["build_meta"] == index["build_meta"], "Deployed index differs from tested artifact"

    # Establish the advertised SSE transport, then use its announced endpoint.
    with request("/sse") as stream:
        assert stream.headers.get_content_type() == "text/event-stream"
        assert stream.readline().decode().strip() == "event: endpoint"
        endpoint = stream.readline().decode().strip()
        assert endpoint.startswith("data: "), endpoint
        endpoint_url = urlsplit(endpoint[6:])
        requested_url = urlsplit(origin)
        assert (endpoint_url.scheme, endpoint_url.netloc) == (requested_url.scheme, requested_url.netloc), "Unexpected SSE endpoint origin"
        endpoint_path = endpoint_url.path + "?" + endpoint_url.query
        sequence = 0

        def rpc(method, params=None):
            nonlocal sequence
            sequence += 1
            with request(endpoint_path, dict(jsonrpc="2.0", id=sequence, method=method, params=params or {})) as response:
                value = json.load(response)
            assert value.get("id") == sequence and "error" not in value, value
            return value["result"]

        def call(name, arguments):
            result = rpc("tools/call", dict(name=name, arguments=arguments))
            assert not result.get("isError"), result
            return json.loads(result["content"][0]["text"])

        initialized = rpc("initialize", dict(protocolVersion="2024-11-05", capabilities={},
                                             clientInfo=dict(name="deployment-smoke", version="1")))
        assert initialized["serverInfo"]["version"] == health["version"]
        with request(endpoint_path, dict(jsonrpc="2.0", method="notifications/initialized")) as response:
            assert response.status == 202
        core = {"search_wiki", "get_developer_journey", "read_knowledge_atom", "get_evidence_fact",
                "get_graph_relations", "search_raw_sources", "read_raw_source_file"}
        assert core <= {tool["name"] for tool in rpc("tools/list")["tools"]}
        matches = call("search_wiki", {"query": "Muse Pi"})
        assert matches and all("hint" in item and "freshness" in item for item in matches)
        fact = call("get_evidence_fact", {"spec_name": "muse_pi_vs_pi_pro_specs"})
        assert fact["full_table_content"].strip() and isinstance(fact["agent_notice"], list)
        raw = call("search_raw_sources", {"query": "k1_hw_design_guide", "submodule": "docs-chip"})
        assert raw, "No raw source found"
        path = raw[0]["file_path"]
        first = call("read_raw_source_file", {"file_path_or_url": path})
        assert first["source_commit"] == raw[0]["source_commit"]
        assert len(first["content"].splitlines()) <= 200
        assert first["has_more"] and first["next_start_line"] == 201
        second = call("read_raw_source_file", {"file_path_or_url": path, "start_line": 201, "end_line": 999999})
        assert second["source_commit"] == first["source_commit"]
        assert second["start_line"] == 201 and len(second["content"].splitlines()) <= 500
        assert second["end_line"] == min(first["total_lines"], 700)
    return {"status": "passed", "deployment_ref": health["deployment_ref"],
            "version": health["version"], "content_sha256": health["build_meta"]["content_sha256"],
            "d1_bound": health["d1_bound"], "checks": "health/SSE/initialize/tools/search/fact/raw-pages"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", required=True)
    parser.add_argument("--expected-ref")
    parser.add_argument("--index", help="Compare deployed metadata with this exact tested index")
    parser.add_argument("--proxy", help="Optional HTTP proxy URL")
    args = parser.parse_args()
    try:
        expected = None
        if args.index:
            with open(args.index, encoding="utf-8") as source:
                expected = json.load(source)
        print(json.dumps(smoke(args.url, args.expected_ref, expected, args.proxy), ensure_ascii=False))
    except Exception as exc:
        print(f"MCP smoke failed: {exc}", file=sys.stderr)
        sys.exit(1)
