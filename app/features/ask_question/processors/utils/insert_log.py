from __future__ import annotations

import argparse
from pathlib import Path

from app.core.db import SessionLocal
from app.models.solver_result import SolverResult
from app.features.ask_question.processors.parsing.parse_log import parse_solver_log_text


OPTIONAL_NULL_FIELDS = {
    "bias_power1h",
    "bias_frequency1",
    "bias_dc_offset",
    "bias_peak_to_peak",
}

REQUIRED_FIELDS = [
    "simulation_source",
    "simulation_heating",
    "simulation_spulsing",
    "simulation_bias",
    "simulation_dtout",
    "chamber_lp",
    "chamber_rp",
    "chamber_ls",
    "chamber_rsub",
    "source_powerh",
    "source_powerl",
    "source_frequency",
    "pressure_pressure",
    "pressure_inlet_species",
    "pressure_q",
    "considered_ar_star",
    "considered_ar",
    "considered_ar_plus",
    "considered_e",
    "temperature_gas_temperature",
    "temperature_electron_temperature",
    "temperature_ion_temperature",
    "heating_absorbed_power",
    "heating_alpha",
    "heating_plasma_resistance",
    "heating_plasma_reactance",
    "sheath_j0h_h",
    "number_density_ar_star",
    "number_density_ar",
    "number_density_ar_plus",
    "number_density_e",
    "ion_flux_ar_plus",
    "radical_flux_ar_star",
    "radical_flux_ar",
    "avg_ion_energy_ar_plus",
]


def _normalize(parsed: dict[str, str | None]) -> dict[str, str | None]:
    normalized = dict(parsed)
    for key in OPTIONAL_NULL_FIELDS:
        if normalized.get(key) is None:
            normalized[key] = "null"
    return normalized


def _missing_required(parsed: dict[str, str | None]) -> list[str]:
    missing: list[str] = []
    for key in REQUIRED_FIELDS:
        value = parsed.get(key)
        if value is None or str(value).strip() == "":
            missing.append(key)
    return missing


def seed_solver_results(
    data_dir: Path,
    start_idx: int,
    end_idx: int,
    truncate: bool,
) -> None:
    db = SessionLocal()
    try:
        if truncate:
            db.query(SolverResult).delete()
            db.commit()

        inserted = 0
        skipped = 0

        for idx in range(start_idx, end_idx + 1):
            file_name = f"{idx:03}.log"
            file_path = data_dir / file_name

            if not file_path.exists():
                skipped += 1
                print(f"[SKIP] not found: {file_name}")
                continue

            text = file_path.read_text(encoding="utf-8")
            parsed = parse_solver_log_text(text)
            missing = _missing_required(parsed)
            if missing:
                skipped += 1
                print(f"[SKIP] missing required values: {file_name} -> {missing}")
                continue

            parsed = _normalize(parsed)

            exists = (
                db.query(SolverResult)
                .filter(SolverResult.log_file_name == file_name)
                .first()
            )
            if exists:
                skipped += 1
                print(f"[SKIP] already exists: {file_name}")
                continue

            row = SolverResult(
                log_file_name=file_name,
                simulation_source=parsed["simulation_source"],
                simulation_heating=parsed["simulation_heating"],
                simulation_spulsing=parsed["simulation_spulsing"],
                simulation_bias=parsed["simulation_bias"],
                simulation_dtout=parsed["simulation_dtout"],
                chamber_lp=parsed["chamber_lp"],
                chamber_rp=parsed["chamber_rp"],
                chamber_ls=parsed["chamber_ls"],
                chamber_rsub=parsed["chamber_rsub"],
                source_powerh=parsed["source_powerh"],
                source_powerl=parsed["source_powerl"],
                source_frequency=parsed["source_frequency"],
                bias_power1h=parsed["bias_power1h"],
                bias_frequency1=parsed["bias_frequency1"],
                pressure_pressure=parsed["pressure_pressure"],
                pressure_inlet_species=parsed["pressure_inlet_species"],
                pressure_q=parsed["pressure_q"],
                considered_ar_star=parsed["considered_ar_star"],
                considered_ar=parsed["considered_ar"],
                considered_ar_plus=parsed["considered_ar_plus"],
                considered_e=parsed["considered_e"],
                temperature_gas_temperature=parsed["temperature_gas_temperature"],
                temperature_electron_temperature=parsed["temperature_electron_temperature"],
                temperature_ion_temperature=parsed["temperature_ion_temperature"],
                heating_absorbed_power=parsed["heating_absorbed_power"],
                heating_alpha=parsed["heating_alpha"],
                heating_plasma_resistance=parsed["heating_plasma_resistance"],
                heating_plasma_reactance=parsed["heating_plasma_reactance"],
                bias_dc_offset=parsed["bias_dc_offset"],
                bias_peak_to_peak=parsed["bias_peak_to_peak"],
                sheath_j0h_h=parsed["sheath_j0h_h"],
                number_density_ar_star=parsed["number_density_ar_star"],
                number_density_ar=parsed["number_density_ar"],
                number_density_ar_plus=parsed["number_density_ar_plus"],
                number_density_e=parsed["number_density_e"],
                ion_flux_ar_plus=parsed["ion_flux_ar_plus"],
                radical_flux_ar_star=parsed["radical_flux_ar_star"],
                radical_flux_ar=parsed["radical_flux_ar"],
                avg_ion_energy_ar_plus=parsed["avg_ion_energy_ar_plus"],
            )
            db.add(row)
            inserted += 1

        db.commit()
        print(f"done: inserted={inserted}, skipped={skipped}")
    finally:
        db.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed solver_results from .log files")
    parser.add_argument("--data-dir", type=str, required=True, help="Directory containing 000.log~149.log")
    parser.add_argument("--start", type=int, default=0, help="Start index (default: 0)")
    parser.add_argument("--end", type=int, default=149, help="End index (default: 149)")
    parser.add_argument("--truncate", action="store_true", help="Delete all rows in solver_results before insert")
    args = parser.parse_args()

    seed_solver_results(
        data_dir=Path(args.data_dir),
        start_idx=args.start,
        end_idx=args.end,
        truncate=args.truncate,
    )


if __name__ == "__main__":
    main()
