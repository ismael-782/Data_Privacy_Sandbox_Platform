"""CLI entry-point for running quick checks."""

from __future__ import annotations

import argparse
from pathlib import Path

from app.core.logging import setup_logging
from app.privacy.algorithms.base import AlgorithmParams
from app.services.anonymization_service import AnonymizationService
from app.services.dataset_service import DatasetService


def run_cli(path: str, qi: list[str], sa: list[str]) -> None:
    setup_logging()
    dataset_service = DatasetService()
    anonymization_service = AnonymizationService()

    df = dataset_service.load(Path(path))
    validation = dataset_service.validate_dataset(df)
    if not validation.is_valid:
        raise SystemExit(f"Dataset invalid: {validation.errors}")

    params = AlgorithmParams(quasi_identifiers=qi, sensitive_attributes=sa, k=5, l=2, t=0.2)
    result = anonymization_service.run_pipeline(df, ["k-anonymity"], params)
    print(result.metrics)


def main() -> None:
    parser = argparse.ArgumentParser(description="Privacy Sandbox CLI")
    parser.add_argument("--path", required=True, help="Path to dataset")
    parser.add_argument("--qi", nargs="+", required=True, help="Quasi-identifiers")
    parser.add_argument("--sa", nargs="*", default=[], help="Sensitive attributes")
    args = parser.parse_args()
    run_cli(args.path, args.qi, args.sa)


if __name__ == "__main__":
    main()

