"""Hook: blocks any call to the Power BI MCP server that mentions the production model."""
import json
import sys

PRODUCTION = "Sales [Prod]"

call = json.load(sys.stdin)
if PRODUCTION in json.dumps(call.get("tool_input", {})):
    print(f"Blocked: {PRODUCTION} is production. Work on Sales [Dev] or the PBIP files.",
          file=sys.stderr)
    sys.exit(2)  # 2 means: block the call, show the message to the agent
