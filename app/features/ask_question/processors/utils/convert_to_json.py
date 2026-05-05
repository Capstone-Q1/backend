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


def to_ai_request_payload(query_text: str, parsed_values: dict[str, str | None]) -> dict[str, Any]:
    req = AiQuestionRequest(
        query_text=query_text,
        data=build_ai_data(parsed_values),
    )
    return req.model_dump(by_alias=True, exclude_none=False)




## 프론트로 보낼 때 사용할 변환 메서드 추가 필요
