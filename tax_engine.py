"""Income tax calculation for Indian salaried employees — FY 2025-26 (AY 2026-27)."""

from __future__ import annotations

from dataclasses import dataclass

# Budget 2025-26 slabs (Section 115BAC — new regime)
NEW_REGIME_SLABS: list[tuple[int, float]] = [
    (400_000, 0.00),
    (800_000, 0.05),
    (1_200_000, 0.10),
    (1_600_000, 0.15),
    (2_000_000, 0.20),
    (2_400_000, 0.25),
    (10**12, 0.30),
]

# Old regime slabs (unchanged for FY 2025-26)
OLD_REGIME_SLABS: list[tuple[int, float]] = [
    (250_000, 0.00),
    (500_000, 0.05),
    (1_000_000, 0.20),
    (10**12, 0.30),
]

STATUTORY_STD_DED_NEW = 75_000
STATUTORY_STD_DED_OLD = 50_000
MAX_80C = 150_000
MAX_80CCD_1B = 50_000
CESS_RATE = 0.04

NEW_87A_LIMIT = 1_200_000
NEW_87A_REBATE = 60_000
OLD_87A_LIMIT = 500_000
OLD_87A_REBATE = 12_500


@dataclass(frozen=True)
class TaxBreakdown:
    gross_salary: float
    standard_deduction: float
    hra_exemption: float
    section_80c: float
    nps_80ccd_1b: float
    taxable_income: float
    tax_before_rebate: float
    rebate: float
    marginal_relief: float
    tax_after_rebate: float
    cess: float
    total_tax: float


def _slab_tax(income: float, slabs: list[tuple[int, float]]) -> float:
    if income <= 0:
        return 0.0

    tax = 0.0
    previous_limit = 0
    for limit, rate in slabs:
        if income <= previous_limit:
            break
        taxable_in_slab = min(income, limit) - previous_limit
        tax += taxable_in_slab * rate
        previous_limit = limit
    return tax


def _apply_new_regime_relief(taxable_income: float, tax_before_rebate: float) -> tuple[float, float, float]:
    """Return (rebate, marginal_relief, tax_after_rebate)."""
    if taxable_income <= NEW_87A_LIMIT:
        rebate = min(tax_before_rebate, NEW_87A_REBATE)
        return rebate, 0.0, max(tax_before_rebate - rebate, 0.0)

    excess_income = taxable_income - NEW_87A_LIMIT
    if tax_before_rebate > excess_income:
        marginal_relief = tax_before_rebate - excess_income
        return 0.0, marginal_relief, excess_income
    return 0.0, 0.0, tax_before_rebate


def _apply_old_regime_rebate(taxable_income: float, tax_before_rebate: float) -> tuple[float, float, float]:
    if taxable_income <= OLD_87A_LIMIT:
        rebate = min(tax_before_rebate, OLD_87A_REBATE)
        return rebate, 0.0, max(tax_before_rebate - rebate, 0.0)
    return 0.0, 0.0, tax_before_rebate


def _finalize(
    *,
    gross_salary: float,
    standard_deduction: float,
    hra_exemption: float,
    section_80c: float,
    nps_80ccd_1b: float,
    taxable_income: float,
    tax_before_rebate: float,
    rebate: float,
    marginal_relief: float,
    tax_after_rebate: float,
) -> TaxBreakdown:
    cess = tax_after_rebate * CESS_RATE
    return TaxBreakdown(
        gross_salary=gross_salary,
        standard_deduction=standard_deduction,
        hra_exemption=hra_exemption,
        section_80c=section_80c,
        nps_80ccd_1b=nps_80ccd_1b,
        taxable_income=max(taxable_income, 0.0),
        tax_before_rebate=tax_before_rebate,
        rebate=rebate,
        marginal_relief=marginal_relief,
        tax_after_rebate=tax_after_rebate,
        cess=cess,
        total_tax=tax_after_rebate + cess,
    )


def calculate_new_regime(
    gross_salary: float,
    standard_deduction: float,
) -> TaxBreakdown:
    """New regime: standard deduction only (no 80C / HRA)."""
    std_ded = min(max(standard_deduction, 0.0), STATUTORY_STD_DED_NEW)
    taxable_income = gross_salary - std_ded
    tax_before_rebate = _slab_tax(taxable_income, NEW_REGIME_SLABS)
    rebate, marginal_relief, tax_after_rebate = _apply_new_regime_relief(
        taxable_income, tax_before_rebate
    )
    return _finalize(
        gross_salary=gross_salary,
        standard_deduction=std_ded,
        hra_exemption=0.0,
        section_80c=0.0,
        nps_80ccd_1b=0.0,
        taxable_income=taxable_income,
        tax_before_rebate=tax_before_rebate,
        rebate=rebate,
        marginal_relief=marginal_relief,
        tax_after_rebate=tax_after_rebate,
    )


def calculate_old_regime(
    gross_salary: float,
    standard_deduction: float,
    hra_exemption: float,
    section_80c: float,
    nps_contribution: float,
) -> TaxBreakdown:
    """Old regime: standard deduction, HRA, 80C, and 80CCD(1B) NPS."""
    std_ded = min(max(standard_deduction, 0.0), STATUTORY_STD_DED_OLD)
    hra = max(hra_exemption, 0.0)
    ded_80c = min(max(section_80c, 0.0), MAX_80C)
    nps_1b = min(max(nps_contribution, 0.0), MAX_80CCD_1B)

    taxable_income = gross_salary - std_ded - hra - ded_80c - nps_1b
    tax_before_rebate = _slab_tax(taxable_income, OLD_REGIME_SLABS)
    rebate, marginal_relief, tax_after_rebate = _apply_old_regime_rebate(
        taxable_income, tax_before_rebate
    )
    return _finalize(
        gross_salary=gross_salary,
        standard_deduction=std_ded,
        hra_exemption=hra,
        section_80c=ded_80c,
        nps_80ccd_1b=nps_1b,
        taxable_income=taxable_income,
        tax_before_rebate=tax_before_rebate,
        rebate=rebate,
        marginal_relief=marginal_relief,
        tax_after_rebate=tax_after_rebate,
    )


def compare_regimes(
    gross_salary: float,
    standard_deduction: float,
    hra_exemption: float,
    section_80c: float,
    nps_contribution: float,
) -> tuple[TaxBreakdown, TaxBreakdown, str, float]:
    """Return both regime results, the better regime label, and savings amount."""
    new_result = calculate_new_regime(gross_salary, standard_deduction)
    old_result = calculate_old_regime(
        gross_salary, standard_deduction, hra_exemption, section_80c, nps_contribution
    )

    if new_result.total_tax < old_result.total_tax:
        return new_result, old_result, "New Regime", old_result.total_tax - new_result.total_tax
    if old_result.total_tax < new_result.total_tax:
        return new_result, old_result, "Old Regime", new_result.total_tax - old_result.total_tax
    return new_result, old_result, "Both are equal", 0.0
