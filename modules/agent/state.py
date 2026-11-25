# state 를 정의해서 team 사이의 정보를 공유

from typing import Annotated, Any, Dict, List, Literal, Optional, TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

TaskType = Literal[
    "chat", # 일상 대화 또는 인사
    "vision_qa", # 비전 탐지 결과 DB 조회
    "erp_resource_qa", # ERP DB 조회
    "worker_qa", # 특정 작업자 자격증 유효기간 확인
    "worker_list_qa", # 작업자 전체 명단 DB 조회 (사내/하청/프리랜서)
    "scm_partner_qa", # 사외 협력사 질의 (DB 정보를 바탕으로)
    "knowledge_qa", # 사내 문서 질의 (RAG 정보를 바탕으로)
    "doc_generation", # 문서 작성
]

DocCategory = Literal[
    "manufacturing_tech", # 제조 기술 문서
    "safety_health", # 안전 문서
    "class_rules", # 선급 규정
    "heavy_equipment", # 중장비 문서
    "quality_inspection", # 품질검사 문서 (비파괴, 허용공차등)
    "work_weather", # 기상 정보
    "internal_docs", # 사내 문서 양식
]

SearchStatus = Literal["idle", "completed", "empty", "error"]
# Team 1 에서 "idle"로 설정해놓음, 일상 대화 ex)"chat" 와 같이 검색이 필요없을때는 즉시 "completed"로 전환
# Team 2 로 넘어왔을때 ChromaDB에서 관련문서를 검색한뒤 찾았으면 "completed", 검색 결과가 없으면 "empty"로 바꿈.
# Team 2 가 React 구조가 되면서 현재 상태 추적 및 디버깅용 메타데이터 역할중

class ShipAgentState(TypedDict, total=False): # total=False Optional 과 비슷한 의미
    # Supervisor 라우팅 제어
    next: Optional[str] # 다음으로 이동할 노드의 이름

    # 멀티턴 대화 히스토리, add_message 로 새 메세지를 이어붙임
    messages: Annotated[List[BaseMessage], add_messages]
    user_query: str # 현재 질문

    # 사용자 권한 및 작업오더 컨텍스트
    user_id: Optional[str]
    user_name: Optional[str]
    user_role: Optional[str] # worker/manager/admin
    user_type: Optional[str] # internal/external
    can_access_erp: Optional[str] # 'Y' | 'No'
    can_access_internal_rag: Optional[str] # 'Y' | 'No'
    can_control_robot: Optional[str] # 'Y' | 'No'
    default_workspace: Optional[str]
    branch_code: Optional[str]
    work_id: Optional[str]
    work_no: Optional[str]

    # Team 1 의 상태 / 질문을 해석해서 값을 채워넣고 전달
    task_type: Optional[TaskType]
    is_action_Requested: bool
    preferred_execution_mode: Optional[Literal["AUTO", "IN_HOUSE", "OUTSOURCED_B2B"]] # 알아서 / 본사 / 외주
    outsourcing_domain: Optional[
        Literal[
            "ALL_PARTNERS",
            "HEAVY_TRANSPORT",
            "WELDING_MATERIAL",
            "OUTSOURCED_WORKER",
            "NOT_APPLICABLE",
        ]
    ] # 외주가 필요하다면 어느 도메인 인지
    worker_scope: Optional[Literal["ALL",  "HQ_ONLY", "EXTERNAL_ONLY"]]

    # Agentic 자율편성 (사용자가 일일이 정보를 주지않아도 DB에서 조회후 결과 출력) / Self-Correction 제어 상태 

    auto_assign_node: bool # 사용자가 블록 작업자를 지정하지않아도 자율 탐색 배정을 허용하느냐
    replan_count: int # Team 3 Gatekeeper 차단후 자율 재편성 횟수
    replan_needed: bool # Team3 -> Team 2 복구 
    replan_feedback: Optional[str] # 차단 사유 및 재편성 지시 피드백
    excluded_blocks: List[str] # 불가 판정된 블록을 모아둔 리스트
    excluded_workers: List[str] # 불가 판정된 작업자를 모아둔 리스트
    agent_resoning_summary: Optional[str] # agent 의 판단 근거 (자율 선택,복구)
    tool_trace: List[Dict[str, Any]] # ReAct 도구 호출 이력
    drafted_blocks_history: List[str] # 초안 블록 목록
    drafted_Workers_history: List[str] # 초안 작업자 목록

    target_categories: List[DocCategory]
    need_weather: bool
    extracted_params: Dict[str, Any]
    is_param_complete: Optional[str] # 'yes' | 'no'
    doc_grade: Optional[str]
    retry_count: int
    weather_data: Optional[Dict[str, Any]]
    vision_data: Optional[Dict[str, Any]]

    # 4. SHIP_ERP & B2B SCM 연동 상태
    erp_resource_status: Optional[Dict[str, Any]]
    is_outsourcing_required: bool
    partner_erp_plan: Optional[Dict[str, Any]]
    erp_commit_result: Optional[Dict[str, Any]]
    hitl_approved: Optional[bool]

    # 5. Team 2 (ReAct 자율 탐색 에이전트) 수집 결과
    team2_plan: Optional[List[str]]
    search_status: SearchStatus
    retrieved_docs: List[Dict[str, Any]]
    doc_grade: Optional[str]                      # "yes" | "no"
    retry_count: int
    weather_data: Optional[Dict[str, Any]]
    vision_data: Optional[Dict[str, Any]]

    generated_document: Optional[Dict[str, Any]]
    final_answer: Optional[str]
    audit_saved: bool
    


