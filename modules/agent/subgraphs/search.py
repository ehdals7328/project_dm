# Team 2 search subgraph는 LLM이 스스로 필요한 도구를 호출하고
# 관찰하여 블록/작업자/자재/장비/규정/기상/비전/A2A 외주를 조율
# Team 3 거버넌스 게이트키퍼에서 차단 피드백이 돌아오면 자동 대안 탐색 및 재편성

import json
import re
from decimal import Decimal
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph
from pydantic import Field

from modules.agent.state import ShipAgentState
from modules.agent.tools.domain_tools import evaluate_environmental_safety
from modules.agent.tools.erp_tools import (
    check_hq_erp_resources,
    check_yard_materials_and_equipment,
    evaluate_heavy_lifting_capacity,
    find_eligible_workers,
    find_pending_blocks,
    get_branch_context_from_db,
    list_erp_workers,
    query_partner_erp_b2b,
)
from modules.agent.tools.partner_mcp_client import negotiate_partner_via_a2a
from modules.agent.tools.retriever_tools import search_knowledge_by_categories
from modules.agent.tools.vision_tools import (
    get_vision_inspection_status,
    get_vision_overview_for_qa,
)
from modules.agent.tools.weather_mcp_client import get_realtime_weather_from_mcp

MAX_REACT_STEPS = 4

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return int(obj) if obj % 1 == 0 else float(obj)
        if hasattr(obj, "isoformat"):
            return obj.isoformat()
        return super().default(obj)