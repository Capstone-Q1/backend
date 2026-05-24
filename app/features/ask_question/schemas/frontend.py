from pydantic import BaseModel, ConfigDict, Field
from typing import Literal
from datetime import datetime


# 유사한 로그 1건의 상세 데이터 스키마.
# 유사 로그 검색 결과를 API 응답으로 담을 때(파싱/검증/직렬화) 사용.
class SimilarLogData(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    file_name: str = Field(alias="file_name")
    source: str = Field(alias="Source")
    heating: str = Field(alias="Heating")
    spulsing: str = Field(alias="SPulsing")
    bias: str = Field(alias="Bias")
    dtout: float = Field(alias="dtout")
    lp: float = Field(alias="Lp")
    rp: float = Field(alias="Rp")
    ls: float = Field(alias="Ls")
    rsub: float = Field(alias="Rsub")
    power_h: float = Field(alias="PowerH")
    power_l: float = Field(alias="PowerL")
    frequency: float = Field(alias="Frequency")
    pressure: float = Field(alias="Pressure")
    inlet_species: str = Field(alias="Inlet_species")
    q: float = Field(alias="Q")
    gas_temperature: float = Field(alias="Gas_Temperature")
    electron_temperature: float = Field(alias="Electron_Temperature")
    ion_temperature: float = Field(alias="Ion_Temperature")
    absorbed_power: float = Field(alias="Absorbed_power")
    alpha: float = Field(alias="alpha")
    plasma_resistance: float = Field(alias="Plasma_resistance")
    plasma_reactance: float = Field(alias="Plasma_reactance")
    j0h_h: float = Field(alias="J0h_h")
    ar_star_density: float = Field(alias="Ar_star_density")
    ar_density: float = Field(alias="Ar_density")
    ar_plus_density: float = Field(alias="Ar_plus_density")
    e_density: float = Field(alias="E_density")
    ar_plus_ion_flux: float = Field(alias="Ar_plus_ion_flux")
    ar_star_radical_flux: float = Field(alias="Ar_star_radical_flux")
    ar_radical_flux: float = Field(alias="Ar_radical_flux")
    ar_plus_avg_ion_energy: float = Field(alias="Ar_plus_avg_ion_energy")


# ask_question 성공 응답의 data 본문 스키마.
# 질의 처리 후 핵심 결과(session/log/답변/유사로그 목록)를 묶어 반환할 때 사용.
class AskQuestionData(BaseModel):
    session_id: int
    log_id: int
    chat_response: str
    important_parameters: list[str] = Field(default_factory=list)
    # AI가 찾은 유사 로그가 있으면 true.
    # 프론트는 이 값으로 "분석 그래프 보기" 버튼 표시 여부를 판단한다.
    has_analysis: bool


# ask_question 성공 응답의 최상위 스키마.
# 라우터에서 정상 처리된 응답 형태(status + data)를 고정할 때 사용.
class AskQuestionResponse(BaseModel): #최종적으로 프론트엔드에 반환되는 응답 스키마
    status: Literal["success"]
    data: AskQuestionData


# 분석 그래프 조회 응답의 data 본문 스키마.
# 질의응답 API에서는 has_analysis만 내려주고,
# 프론트가 분석 그래프 보기 버튼을 누르면 log_id 기준으로 이 데이터를 조회한다.
class AnalysisData(BaseModel):
    log_id: int
    input_log_data: SimilarLogData
    similar_logs_data: list[SimilarLogData]


# 분석 그래프 조회 성공 응답 스키마.
# input_log_data는 사용자가 업로드했던 데이터이고,
# similar_logs_data는 AI가 찾은 유사 로그들의 상세 데이터이다.
class AnalysisResponse(BaseModel):
    status: Literal["success"] = "success"
    data: AnalysisData


class DashboardSimilarLogData(BaseModel):
    id: int
    log_file_name: str
    simulation_source: str
    simulation_heating: str
    simulation_spulsing: str
    simulation_bias: str
    simulation_dtout: str
    chamber_lp: str
    chamber_rp: str
    chamber_ls: str
    chamber_rsub: str
    source_powerh: str
    source_powerl: str
    source_frequency: str
    bias_power1h: str | None
    bias_frequency1: str | None
    pressure_pressure: str
    pressure_inlet_species: str
    pressure_q: str
    considered_ar_star: str
    considered_ar: str
    considered_ar_plus: str
    considered_e: str
    temperature_gas_temperature: str
    temperature_electron_temperature: str
    temperature_ion_temperature: str
    heating_absorbed_power: str
    heating_alpha: str
    heating_plasma_resistance: str
    heating_plasma_reactance: str
    bias_dc_offset: str | None
    bias_peak_to_peak: str | None
    sheath_j0h_h: str
    number_density_ar_star: str
    number_density_ar: str
    number_density_ar_plus: str
    number_density_e: str
    ion_flux_ar_plus: str
    radical_flux_ar_star: str
    radical_flux_ar: str
    avg_ion_energy_ar_plus: str


class DashboardResponse(BaseModel):
    status: Literal["success"] = "success"
    user_log: list[str]
    similar_log: list[DashboardSimilarLogData]


# ask_question 요청 바디 입력 스키마.
# 클라이언트가 보낸 session_id, query_text를 검증할 때 사용.
class AskQuestionForm(BaseModel):
    session_id: int | None = Field(default=None, description="기존 채팅방이면 전달")
    query_text: str = Field(min_length=1, description="사용자 자연어 질의")
    parameters: list[str] = Field(
        default_factory=list,
        description="사용자가 선택한 셋업매뉴얼 기준 파라미터명 목록",
    )

# 채팅방 목록 1건의 응답 스키마.
# 사이드바 대화 히스토리에 표시할 채팅방 id, 제목, 생성 시각, 마지막 대화 시각을 반환할 때 사용.
class ChatSessionListItem(BaseModel):
    session_id: int
    title: str
    created_at: datetime
    updated_at: datetime


# 채팅방 목록 조회 성공 응답의 최상위 스키마.
# 현재 로그인한 사용자의 채팅방 목록을 최신 대화순으로 반환할 때 사용.
class ChatSessionListResponse(BaseModel):
    status: Literal["success"] = "success"
    data: list[ChatSessionListItem]


# 채팅방 상세 조회에서 대화 1건을 표현하는 응답 스키마.
# query_response_log 1행을 프론트엔드 채팅 메시지 형태로 반환할 때 사용.
class ChatSessionDetailMessage(BaseModel):
    log_id: int
    query_text: str
    chat_response: str | None
    has_analysis: bool
    created_at: datetime
    response_at: datetime | None


# 채팅방 상세 조회 응답의 data 스키마.
# 채팅방 기본 정보와 해당 채팅방의 전체 질의응답 목록을 묶어 반환할 때 사용.
class ChatSessionDetailData(BaseModel):
    session_id: int
    title: str
    created_at: datetime
    messages: list[ChatSessionDetailMessage]


# 채팅방 상세 조회 성공 응답의 최상위 스키마.
# 사이드바에서 채팅방을 클릭했을 때 채팅 영역에 표시할 전체 대화 내역을 반환할 때 사용.
class ChatSessionDetailResponse(BaseModel):
    status: Literal["success"] = "success"
    data: ChatSessionDetailData


class ChatSessionDeleteResponse(BaseModel):
    status: Literal["success"] = "success"


# 에러 응답 공통 스키마.
# 실패/예외 상황에서 error_code, error_message를 일관되게 반환할 때 사용.
class ErrorResponse(BaseModel):
    error_code: str
    error_message: str
