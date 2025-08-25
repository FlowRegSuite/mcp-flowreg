# src/mcp_flowreg/server.py
import json
import logging
from pathlib import Path

from fastmcp import FastMCP, Context
from fastmcp.prompts.prompt import Message
from pydantic import Field

BASE = Path(__file__).resolve().parent
PROMPTS_DIR = BASE.parent / "prompts"

log = logging.getLogger("mcp_flowreg")


def load_prompt(name: str) -> str:
    return (PROMPTS_DIR / name).read_text(encoding="utf-8")


mcp = FastMCP("mcp-flowreg")


@mcp.prompt(name="parameter_suggest",
    description="Suggest parameters for variational flow-registration motion correction with quality preset policy.",
    tags={"flowreg", "optical-flow", "parameters", "microscopy", "rgb"},
    meta={"routing_hint": "flowreg.parameters.suggest", "quality_presets": ["fast", "balanced", "quality"],
          "backends": ["flowreg_variational", "opencv_dis"]})
def parameter_suggest(input_json: dict | str = Field(description="Input spec for the video and channels."),
        final_run: bool = Field(default=False,
                                description="If true, allow quality preset; otherwise default balanced.")) -> list[
    Message]:
    p = load_prompt("parameter_suggest.md")
    payload = input_json if isinstance(input_json, dict) else json.loads(input_json)
    payload["final_run"] = bool(final_run)
    return [Message(p, role="system"), Message(json.dumps({"input_json": payload}), role="user"), ]


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    mcp.run()
