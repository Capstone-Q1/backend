from __future__ import annotations
from typing import Any
from app.features.ask_question.schemas.ai import AiQuestionRequest


def _with_unit(value: str | None, unit: str | None = None) -> str | None:
    if value is None:
        return None
    if not unit:
        return value
    return f"{value} ({unit})"


def _pick(values: dict[str, str | None], *keys: str) -> str | None:
    for key in keys:
        v = values.get(key)
        if v is not None:
            return v
    return None


def build_ai_data(values: dict[str, str | None]) -> dict[str, Any]:
    # AI 모델에 전달할 데이터 구조를 구성하는 헬퍼 함수.
    # 이거 나중에 매핑 테이블로 바꿔도 될듯? 지금은 그냥 하드코딩으로 키 매핑.
    return {
        "SETTINGS": {
            "SIMULATION OPTIONS": {
                "Source": _pick(values, "simulation_source"),
                "Heating": _pick(values, "simulation_heating"),
                "SPulsing": _pick(values, "simulation_spulsing"),
                "Bias": _pick(values, "simulation_bias"),
                "dtout": _with_unit(_pick(values, "simulation_dtout"), "s"),
            },
            "CHAMBER GEOMETRY": {
                "Lp": _with_unit(_pick(values, "chamber_lp"), "cm"),
                "Rp": _with_unit(_pick(values, "chamber_rp"), "cm"),
                "Ls": _with_unit(_pick(values, "chamber_ls"), "cm"),
                "Rsub": _with_unit(_pick(values, "chamber_rsub"), "cm"),
            },
            "SOURCE POWER CONDITIONS": {
                "PowerH": _with_unit(_pick(values, "source_powerh"), "W"),
                "PowerL": _with_unit(_pick(values, "source_powerl"), "W"),
                "Frequency": _with_unit(_pick(values, "source_frequency"), "Hz"),
            },
            "BIAS POWER CONDITIONS": {
                "Power1h": _with_unit(_pick(values, "bias_power1h"), "W"),
                "Frequency1": _with_unit(_pick(values, "bias_frequency1"), "Hz"),
            },
            "PREASURE & INLET CONDITIONS": {
                "Pressure": _with_unit(_pick(values, "pressure_pressure", "preasure_pressure"), "mTorr"),
                "Inlet species": _pick(values, "pressure_inlet_species", "preasure_inlet"),
                "Q": _with_unit(_pick(values, "pressure_q", "preasure_q"), "sccm"),
            },
            "CONSIDERED SPECIES": {
                "Species": {
                    "Ar*": _with_unit(_pick(values, "considered_ar_star"), "g"),
                    "Ar": _with_unit(_pick(values, "considered_ar"), "g"),
                    "Ar+": _with_unit(_pick(values, "considered_ar_plus"), "g"),
                    "E": _with_unit(_pick(values, "considered_e"), "g"),
                }
            },
        },
        "OUTPUT LIST": {
            "TEMPERATURE PARAMETERS": {
                "Gas Temperature": _with_unit(_pick(values, "temperature_gas_temperature", "temperature_gas"), "eV"),
                "Electron Temperature": _with_unit(_pick(values, "temperature_electron_temperature", "temperature_electron"), "eV"),
                "Ion Temperature": _with_unit(_pick(values, "temperature_ion_temperature", "temperature_ion"), "eV"),
            },
            "HEATING PARAMETERS": {
                "Absorbed power": _with_unit(_pick(values, "heating_absorbed_power", "heating_absorbed"), "W"),
                "alpha": _with_unit(_pick(values, "heating_alpha"), "a.u."),
                "Plasma resistance": _with_unit(_pick(values, "heating_plasma_resistance", "heating_resistance"), "ohm"),
                "Plasma reactance": _with_unit(_pick(values, "heating_plasma_reactance", "heating_reactance"), "ohm"),
            },
            "BIAS PARAMETERS": {
                "dc-offset": _with_unit(_pick(values, "bias_dc_offset", "bias_dcoffset"), "V"),
                "peak-to-peak": _with_unit(_pick(values, "bias_peak_to_peak", "bias_peak2peak"), "V"),
            },
            "SHEATH PARAMETERS": {
                "J0h_h": _with_unit(_pick(values, "sheath_j0h_h"), "statampere/cm^2"),
            },
            "NUMBER DENSITY": {
                "Species": {
                    "Ar*": _with_unit(_pick(values, "number_density_ar_star", "number_ar_star"), "cm^3"),
                    "Ar": _with_unit(_pick(values, "number_density_ar", "number_ar"), "cm^3"),
                    "Ar+": _with_unit(_pick(values, "number_density_ar_plus", "number_ar_plus"), "cm^3"),
                    "E": _with_unit(_pick(values, "number_density_e", "number_e"), "cm^3"),
                }
            },
            "ION FLUX AT THE SHEATH EDGE": {
                "Species": {
                    "Ar+": _with_unit(_pick(values, "ion_flux_ar_plus", "ion_ar_plus"), "cm^2sec"),
                }
            },
            "RADICAL FLUX AT THE SHEATH EDGE": {
                "Species": {
                    "Ar*": _with_unit(_pick(values, "radical_flux_ar_star", "radical_ar_star"), "cm^2sec"),
                    "Ar": _with_unit(_pick(values, "radical_flux_ar", "radical_ar"), "cm^2sec"),
                }
            },
            "AVERAGE ION ENERGY AT THE SUBSTRATE": {
                "Species": {
                    "Ar+": _with_unit(_pick(values, "avg_ion_energy_ar_plus", "average_ar_plus"), "eV"),
                }
            },
        },
    }


# parameters는 사용자가 선택한 셋업매뉴얼 기준 파라미터명 목록이다.
# solver_log가 없는 요청은 data를 null로 보내기 위해 include_data로 제어한다.
def to_ai_request_payload(
        query_text: str, 
        parsed_values: dict[str, str | None],
        *,
        parameters: list[str] | None = None,
        include_data: bool = True,
) -> dict[str, Any]:
    req = AiQuestionRequest(
        query_text=query_text,
        parameters=parameters or [],
        data=build_ai_data(parsed_values) if include_data else None,
    )
    return req.model_dump(by_alias=True, exclude_none=False) # json으로 변환




## 프론트로 보낼 때 사용할 변환 메서드 추가 필요
# ai에서 넘어온 유사 데이터를 조회하여 프론트엔드 스키마에 맞게 변환하는 메서드도 여기에 추가

import json
from app.features.ask_question.schemas.frontend import (
    AskQuestionResponse,
    SimilarLogData,
    DashboardSimilarLogData,
)
from app.models.solver_result import SolverResult

def to_query_solver_log_json(parsed_values: dict[str, str | None]) -> str:
    return json.dumps(parsed_values, ensure_ascii=False)

def _to_float(v: str | None) -> float:
    if v in (None, "", "null", "None"):
        return 0.0
    s = str(v).strip()
    if "(" in s:
        s = s.split("(", 1)[0].strip()
    return float(s)

def parsed_to_similar_log_data(
    parsed_values: dict[str, str | None],
    *,
    file_name: str = "uploaded_solver.log",
) -> SimilarLogData:

    # parseLog 결과를 프론트 응답 형태로 변환한다.

    #parseLog는 simulation_source, source_powerh 같은 내부 key를 반환한다.
    #하지만 프론트에서는 사용자가 업로드한 입력 데이터와 AI가 찾은 유사 데이터를
    #같은 key 구조로 비교해야 하므로, input_log_data도 similar_logs_data와
    #동일한 DTO와 alias를 사용하도록 변환한다.

    return SimilarLogData(
        file_name=file_name,
        source=parsed_values.get("simulation_source") or "",
        heating=parsed_values.get("simulation_heating") or "",
        spulsing=parsed_values.get("simulation_spulsing") or "",
        bias=parsed_values.get("simulation_bias") or "",
        dtout=_to_float(parsed_values.get("simulation_dtout")),
        lp=_to_float(parsed_values.get("chamber_lp")),
        rp=_to_float(parsed_values.get("chamber_rp")),
        ls=_to_float(parsed_values.get("chamber_ls")),
        rsub=_to_float(parsed_values.get("chamber_rsub")),
        power_h=_to_float(parsed_values.get("source_powerh")),
        power_l=_to_float(parsed_values.get("source_powerl")),
        frequency=_to_float(parsed_values.get("source_frequency")),
        pressure=_to_float(parsed_values.get("pressure_pressure")),
        inlet_species=parsed_values.get("pressure_inlet_species") or "",
        q=_to_float(parsed_values.get("pressure_q")),
        gas_temperature=_to_float(parsed_values.get("temperature_gas_temperature")),
        electron_temperature=_to_float(parsed_values.get("temperature_electron_temperature")),
        ion_temperature=_to_float(parsed_values.get("temperature_ion_temperature")),
        absorbed_power=_to_float(parsed_values.get("heating_absorbed_power")),
        alpha=_to_float(parsed_values.get("heating_alpha")),
        plasma_resistance=_to_float(parsed_values.get("heating_plasma_resistance")),
        plasma_reactance=_to_float(parsed_values.get("heating_plasma_reactance")),
        j0h_h=_to_float(parsed_values.get("sheath_j0h_h")),
        ar_star_density=_to_float(parsed_values.get("number_density_ar_star")),
        ar_density=_to_float(parsed_values.get("number_density_ar")),
        ar_plus_density=_to_float(parsed_values.get("number_density_ar_plus")),
        e_density=_to_float(parsed_values.get("number_density_e")),
        ar_plus_ion_flux=_to_float(parsed_values.get("ion_flux_ar_plus")),
        ar_star_radical_flux=_to_float(parsed_values.get("radical_flux_ar_star")),
        ar_radical_flux=_to_float(parsed_values.get("radical_flux_ar")),
        ar_plus_avg_ion_energy=_to_float(parsed_values.get("avg_ion_energy_ar_plus")),
    )


def row_to_similar_log_data(row: SolverResult) -> SimilarLogData:
    return SimilarLogData(
        file_name=row.log_file_name,
        source=row.simulation_source,
        heating=row.simulation_heating,
        spulsing=row.simulation_spulsing,
        bias=row.simulation_bias,
        dtout=_to_float(row.simulation_dtout),
        lp=_to_float(row.chamber_lp),
        rp=_to_float(row.chamber_rp),
        ls=_to_float(row.chamber_ls),
        rsub=_to_float(row.chamber_rsub),
        power_h=_to_float(row.source_powerh),
        power_l=_to_float(row.source_powerl),
        frequency=_to_float(row.source_frequency),
        pressure=_to_float(row.pressure_pressure),
        inlet_species=row.pressure_inlet_species,
        q=_to_float(row.pressure_q),
        gas_temperature=_to_float(row.temperature_gas_temperature),
        electron_temperature=_to_float(row.temperature_electron_temperature),
        ion_temperature=_to_float(row.temperature_ion_temperature),
        absorbed_power=_to_float(row.heating_absorbed_power),
        alpha=_to_float(row.heating_alpha),
        plasma_resistance=_to_float(row.heating_plasma_resistance),
        plasma_reactance=_to_float(row.heating_plasma_reactance),
        j0h_h=_to_float(row.sheath_j0h_h),
        ar_star_density=_to_float(row.number_density_ar_star),
        ar_density=_to_float(row.number_density_ar),
        ar_plus_density=_to_float(row.number_density_ar_plus),
        e_density=_to_float(row.number_density_e),
        ar_plus_ion_flux=_to_float(row.ion_flux_ar_plus),
        ar_star_radical_flux=_to_float(row.radical_flux_ar_star),
        ar_radical_flux=_to_float(row.radical_flux_ar),
        ar_plus_avg_ion_energy=_to_float(row.avg_ion_energy_ar_plus),
    )


def row_to_dashboard_similar_log_data(row: SolverResult) -> DashboardSimilarLogData:
    return DashboardSimilarLogData(
        id=row.id,
        log_file_name=row.log_file_name,
        simulation_source=row.simulation_source,
        simulation_heating=row.simulation_heating,
        simulation_spulsing=row.simulation_spulsing,
        simulation_bias=row.simulation_bias,
        simulation_dtout=row.simulation_dtout,
        chamber_lp=row.chamber_lp,
        chamber_rp=row.chamber_rp,
        chamber_ls=row.chamber_ls,
        chamber_rsub=row.chamber_rsub,
        source_powerh=row.source_powerh,
        source_powerl=row.source_powerl,
        source_frequency=row.source_frequency,
        bias_power1h=row.bias_power1h,
        bias_frequency1=row.bias_frequency1,
        pressure_pressure=row.pressure_pressure,
        pressure_inlet_species=row.pressure_inlet_species,
        pressure_q=row.pressure_q,
        considered_ar_star=row.considered_ar_star,
        considered_ar=row.considered_ar,
        considered_ar_plus=row.considered_ar_plus,
        considered_e=row.considered_e,
        temperature_gas_temperature=row.temperature_gas_temperature,
        temperature_electron_temperature=row.temperature_electron_temperature,
        temperature_ion_temperature=row.temperature_ion_temperature,
        heating_absorbed_power=row.heating_absorbed_power,
        heating_alpha=row.heating_alpha,
        heating_plasma_resistance=row.heating_plasma_resistance,
        heating_plasma_reactance=row.heating_plasma_reactance,
        bias_dc_offset=row.bias_dc_offset,
        bias_peak_to_peak=row.bias_peak_to_peak,
        sheath_j0h_h=row.sheath_j0h_h,
        number_density_ar_star=row.number_density_ar_star,
        number_density_ar=row.number_density_ar,
        number_density_ar_plus=row.number_density_ar_plus,
        number_density_e=row.number_density_e,
        ion_flux_ar_plus=row.ion_flux_ar_plus,
        radical_flux_ar_star=row.radical_flux_ar_star,
        radical_flux_ar=row.radical_flux_ar,
        avg_ion_energy_ar_plus=row.avg_ion_energy_ar_plus,
    )


# 최종적으로 프론트에 반환할 질의응답 성공 응답을 만든다.
def to_frontend_success_payload(
    session_id: int,
    log_id: int,
    chat_response: str,
    has_analysis: bool,
) -> dict:
    response = AskQuestionResponse(
        status="success",
        data={
            "session_id": session_id,
            "log_id": log_id,
            "chat_response": chat_response,
            "has_analysis": has_analysis,
        },
    )
    return response.model_dump(by_alias=True)
