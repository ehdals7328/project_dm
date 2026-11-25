""" 
supervisor 에게는 LLM이 연결되지 않음. 판단은 Flask 내부의 로직으로
이루어지며 노드를 초기화하거나 다음 team 으로 분기하는 역할
"""

from typing import Any, Dict, Literal
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from modules.agent.state import ShipAgentState
from modules.agent.subgraphs.analysis import team1_subgraph
from modules.agent.subgraphs.search import team2_subgraph
from modules.agent.subgraphs.docgen import team3_subgraph

# 새로운 턴 시작시 직전 턴의 일회성 상태를 초기화. 
def top_supervisior_init_node(state: ShipAgentState) -> Dict[str, Any]:
    prev_commit = state.get("erp_commit_result") or {}
    was_already_committed = prev_commit.get("erp_transaction_status") == "COMMITTED"

    drafted_blocks = list(state.get("drafted_blocks_history") or [])
    drafted_workers = list(state.get("drafted_workers_history") or [])
    cleaned_params = dict(state.get("extracted_params") or {})

    prev_doc = state.get("generated_document") or {}
    if prev_doc.get("status") in ("DRAFT", "APPROVED"):
        prev_params = prev_doc.get("parameters") or {}
        p_blk = str(prev_params.get("block_id") or "").strip().upper()
        p_wrk = str(prev_params.get("worker_name") or "").strip()
        if p_blk and p_blk not in drafted_blocks:
            drafted_blocks.append(p_blk)
        if p_wrk and p_wrk not in drafted_workers:
            drafted_workers.append(p_wrk)