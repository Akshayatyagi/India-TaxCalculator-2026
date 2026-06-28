"""Tests for FY 2025-26 tax engine."""

from tax_engine import (
    calculate_new_regime,
    calculate_old_regime,
    compare_regimes,
)


def test_new_regime_zero_tax_at_12_75_lakh_gross():
    # ₹12.75L gross − ₹75K std ded = ₹12L taxable → zero tax with 87A rebate
    result = calculate_new_regime(1_275_000, 75_000)
    assert result.taxable_income == 1_200_000
    assert result.total_tax == 0


def test_new_regime_marginal_relief():
    result = calculate_new_regime(1_285_000, 75_000)
    assert result.taxable_income == 1_210_000
    assert result.marginal_relief > 0
    assert result.tax_after_rebate == 10_000


def test_old_regime_with_deductions():
    result = calculate_old_regime(
        gross_salary=2_000_000,
        standard_deduction=50_000,
        hra_exemption=200_000,
        section_80c=150_000,
        nps_contribution=50_000,
    )
    assert result.taxable_income == 1_550_000
    assert result.total_tax > 0


def test_compare_regimes_returns_savings():
    new, old, better, savings = compare_regimes(
        gross_salary=1_000_000,
        standard_deduction=75_000,
        hra_exemption=0,
        section_80c=0,
        nps_contribution=0,
    )
    assert better in ("New Regime", "Old Regime", "Both are equal")
    assert savings >= 0
    assert new.total_tax <= old.total_tax or better == "Old Regime"
