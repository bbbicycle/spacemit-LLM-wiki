-- Spacemit LLM Wiki - MCP 查询分析与错误反馈表结构
-- 1. 查询日志表 (记录每次工具调用、分类与是否命中)
CREATE TABLE IF NOT EXISTS mcp_query_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    tool_name TEXT NOT NULL,
    query_text TEXT,
    category TEXT DEFAULT 'general',
    status TEXT DEFAULT 'SUCCESS',  -- SUCCESS, MISS_NO_RESULT, ERROR
    matched_id TEXT,
    error_message TEXT,
    client_city TEXT,
    client_country TEXT
);

-- 2. 错误反馈与知识盲区表 (记录未命中的问题、文档勘误、死链反馈)
CREATE TABLE IF NOT EXISTS mcp_issue_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    topic TEXT NOT NULL,
    issue_type TEXT DEFAULT 'MISSING_DOC', -- MISSING_DOC (知识盲区), INCORRECT_SPEC (参数错误), BROKEN_LINK (死链), SUGGESTION (优化建议)
    description TEXT NOT NULL,
    reported_by TEXT DEFAULT 'ai_auto_detected', -- ai_auto_detected 或 user_explicit
    status TEXT DEFAULT 'pending' -- pending, resolved, ignored
);

-- 创建索引以加速 /stats 看板查询
CREATE INDEX IF NOT EXISTS idx_query_status ON mcp_query_logs(status);
CREATE INDEX IF NOT EXISTS idx_query_timestamp ON mcp_query_logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_query_tool ON mcp_query_logs(tool_name);
CREATE INDEX IF NOT EXISTS idx_issue_status ON mcp_issue_reports(status);
