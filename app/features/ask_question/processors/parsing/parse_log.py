# app/features/ask_question/processors/parsing/parse_log.py
from __future__ import annotations

import re


def _get_section_block(text: str, section_name: str) -> str | None:
    # [SECTION] ~ 다음 [SECTION] 전까지 추출
    pattern = rf"\[{re.escape(section_name)}\](.*?)(?=\n\s*\[|\Z)"
    match = re.search(pattern, text, re.DOTALL)
    return match.group(1) if match else None


def _get_section_block_any(text: str, section_names: list[str]) -> str | None:
    # 섹션명이 문서마다 다를 수 있어 후보 중 먼저 매칭되는 것 사용
    for name in section_names:
        block = _get_section_block(text, name)
        if block is not None:
            return block
    return None


def _extract_eq_value(text: str, section_names: list[str], key: str) -> str | None:
    block = _get_section_block_any(text, section_names)
    if block is None:
        return None

    pattern = rf"^\s*{re.escape(key)}\s*=\s*(.+?)\s*$"
    match = re.search(pattern, block, re.IGNORECASE | re.MULTILINE)
    if not match:
        return None

    raw_value = match.group(1).strip()

    # 값 뒤 단위 제거: 1.0000e+02 (W) -> 1.0000e+02
    unit_match = re.match(r"^(.+?)\s*\([^)]+\)\s*$", raw_value)
    if unit_match:
        return unit_match.group(1).strip()

    return raw_value


def _extract_table_value(text: str, section_names: list[str], row_key: str) -> str | None:
    block = _get_section_block_any(text, section_names)
    if block is None:
        return None

    pattern = rf"^\s*{re.escape(row_key)}\s+([^\s]+)\s*$"
    match = re.search(pattern, block, re.IGNORECASE | re.MULTILINE)
    return match.group(1).strip() if match else None


def parse_solver_log_text(text: str) -> dict[str, str | None]:
    if text is None or not text.strip():
        return {}

    pressure_sections = [
        "PRESSURE & INLET CONDITIONS",
        "PREASURE & INLET CONDITIONS",  # 로그 오타 호환
    ]

    values: dict[str, str | None] = {
        # SETTINGS
        "simulation_source": _extract_eq_value(text, ["SIMULATION OPTIONS"], "Source"),
        "simulation_heating": _extract_eq_value(text, ["SIMULATION OPTIONS"], "Heating"),
        "simulation_spulsing": _extract_eq_value(text, ["SIMULATION OPTIONS"], "SPulsing"),
        "simulation_bias": _extract_eq_value(text, ["SIMULATION OPTIONS"], "Bias"),
        "simulation_dtout": _extract_eq_value(text, ["SIMULATION OPTIONS"], "dtout"),

        "chamber_lp": _extract_eq_value(text, ["CHAMBER GEOMETRY"], "Lp"),
        "chamber_rp": _extract_eq_value(text, ["CHAMBER GEOMETRY"], "Rp"),
        "chamber_ls": _extract_eq_value(text, ["CHAMBER GEOMETRY"], "Ls"),
        "chamber_rsub": _extract_eq_value(text, ["CHAMBER GEOMETRY"], "Rsub"),

        "source_powerh": _extract_eq_value(text, ["SOURCE POWER CONDITIONS"], "PowerH"),
        "source_powerl": _extract_eq_value(text, ["SOURCE POWER CONDITIONS"], "PowerL"),
        "source_frequency": _extract_eq_value(text, ["SOURCE POWER CONDITIONS"], "Frequency"),

        "bias_power1h": _extract_eq_value(text, ["BIAS POWER CONDITIONS"], "Power1h"),
        "bias_frequency1": (
            _extract_eq_value(text, ["BIAS POWER CONDITIONS"], "Frequency_1")
            or _extract_eq_value(text, ["BIAS POWER CONDITIONS"], "Frequency1")
        ),

        "pressure_pressure": _extract_eq_value(text, pressure_sections, "Pressure"),
        "pressure_inlet_species": _extract_eq_value(text, pressure_sections, "Inlet species"),
        "pressure_q": _extract_eq_value(text, pressure_sections, "Q"),

        "considered_ar_star": _extract_table_value(text, ["CONSIDERED SPECIES"], "Ar*"),
        "considered_ar": _extract_table_value(text, ["CONSIDERED SPECIES"], "Ar"),
        "considered_ar_plus": _extract_table_value(text, ["CONSIDERED SPECIES"], "Ar+"),
        "considered_e": _extract_table_value(text, ["CONSIDERED SPECIES"], "E"),

        # OUTPUT
        "temperature_gas_temperature": _extract_eq_value(text, ["TEMPERATURE PARAMETERS"], "Gas Temp."),
        "temperature_electron_temperature": _extract_eq_value(text, ["TEMPERATURE PARAMETERS"], "Electron Temp."),
        "temperature_ion_temperature": _extract_eq_value(text, ["TEMPERATURE PARAMETERS"], "Ion Temp."),

        "heating_absorbed_power": _extract_eq_value(text, ["HEATING PARAMETERS"], "Absorbed power"),
        "heating_alpha": _extract_eq_value(text, ["HEATING PARAMETERS"], "alpha"),
        "heating_plasma_resistance": _extract_eq_value(text, ["HEATING PARAMETERS"], "Plasma resistance"),
        "heating_plasma_reactance": _extract_eq_value(text, ["HEATING PARAMETERS"], "Plasma reactance"),

        "bias_dc_offset": _extract_eq_value(text, ["BIAS PARAMETERS"], "dc-offset"),
        "bias_peak_to_peak": _extract_eq_value(text, ["BIAS PARAMETERS"], "peak-to-peak"),

        "sheath_j0h_h": _extract_eq_value(text, ["SHEATH PARAMETERS"], "J0h_h"),

        "number_density_ar_star": _extract_table_value(text, ["NUMBER DENSITY"], "Ar*"),
        "number_density_ar": _extract_table_value(text, ["NUMBER DENSITY"], "Ar"),
        "number_density_ar_plus": _extract_table_value(text, ["NUMBER DENSITY"], "Ar+"),
        "number_density_e": _extract_table_value(text, ["NUMBER DENSITY"], "E"),

        "ion_flux_ar_plus": _extract_table_value(text, ["ION FLUX AT THE SHEATH EDGE"], "Ar+"),

        "radical_flux_ar_star": _extract_table_value(text, ["RADICAL FLUX AT THE SHEATH EDGE"], "Ar*"),
        "radical_flux_ar": _extract_table_value(text, ["RADICAL FLUX AT THE SHEATH EDGE"], "Ar"),

        "avg_ion_energy_ar_plus": _extract_table_value(text, ["AVERAGE ION ENERGY AT THE SUBSTRATE"], "Ar+"),
    }

    return values
