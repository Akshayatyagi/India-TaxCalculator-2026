"""Streamlit app — Indian income tax calculator FY 2025-26."""

from __future__ import annotations

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import streamlit as st

from tax_engine import (
    STATUTORY_STD_DED_NEW,
    STATUTORY_STD_DED_OLD,
    compare_regimes,
)

st.set_page_config(
    page_title="India Tax Calculator FY 2025-26",
    page_icon="🇮🇳",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    /* Light theme base */
    .stApp {
        background-color: #ffffff;
        color: #1a1a2e;
    }
    .main .block-container {
        max-width: 960px;
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }
    h1, h2, h3 {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        color: #1a1a2e;
        letter-spacing: -0.02em;
    }
    p, label, .stMarkdown {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        color: #444;
    }

    /* Top AI badge */
    .ai-badge {
        display: inline-block;
        background: #f0f4ff;
        color: #3d5afe;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.04em;
        text-transform: uppercase;
        padding: 0.35rem 0.75rem;
        border-radius: 999px;
        border: 1px solid #c5cae9;
        margin-bottom: 0.75rem;
    }

    /* Card containers */
    .section-card {
        background: #ffffff;
        border: 1px solid #e8eaf0;
        border-radius: 12px;
        padding: 1.25rem 1.5rem;
        margin-bottom: 1.25rem;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
    }
    .section-card h3 {
        margin-top: 0;
        margin-bottom: 0.75rem;
        font-size: 1.1rem;
    }

    /* Force light theme even if browser/OS prefers dark */
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background-color: #ffffff !important;
        color: #1a1a2e !important;
    }
    [data-testid="stSidebar"] {
        background-color: #f5f7fa !important;
    }
    div[data-testid="stNumberInput"] input {
        background-color: #ffffff !important;
        color: #1a1a2e !important;
    }
    .disclaimer-top {
        background-color: #fffbf0 !important;
        border: 1px solid #ffe082;
        border-radius: 8px;
        padding: 0.75rem 1rem;
        margin-bottom: 1rem;
        font-size: 0.9rem;
        color: #5d4037 !important;
    }
    .new-regime-banner {
        background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%) !important;
        border: 2px solid #43a047;
        border-radius: 10px;
        padding: 1rem 1.25rem;
        margin: 1rem 0 1.25rem 0;
        font-size: 1.05rem;
        color: #1b5e20 !important;
        font-weight: 500;
    }
    .new-regime-banner strong {
        color: #1b5e20;
        font-size: 1.15rem;
    }

    .recommendation-neutral {
        background: #f5f7fa;
        border: 1px solid #dde3ea;
        border-radius: 10px;
        padding: 1rem 1.25rem;
        margin: 1rem 0 1.25rem 0;
        color: #37474f;
    }

    .coming-soon-card {
        background: linear-gradient(135deg, #f8f9ff 0%, #eef1fb 100%);
        border: 1px dashed #9fa8da;
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        color: #3949ab;
    }
    .coming-soon-card h3 {
        color: #283593;
        margin-bottom: 0.5rem;
    }
    .coming-soon-card p {
        color: #5c6bc0;
        margin: 0;
        line-height: 1.6;
    }

    .site-footer {
        margin-top: 2.5rem;
        padding-top: 1.25rem;
        border-top: 1px solid #e8eaf0;
        font-size: 0.8rem;
        color: #9e9e9e;
        text-align: center;
        line-height: 1.5;
    }

    div[data-testid="stMetricValue"] {
        font-size: 1.35rem;
        font-weight: 600;
        color: #1a1a2e;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 0.85rem;
        color: #757575;
    }

    /* Mobile responsiveness */
    @media (max-width: 768px) {
        .main .block-container {
            padding: 0.75rem 1rem 1.5rem;
        }
        h1 {
            font-size: 1.6rem !important;
        }
        .section-card {
            padding: 1rem;
        }
        div[data-testid="stMetricValue"] {
            font-size: 1.1rem !important;
        }
        .new-regime-banner, .recommendation-neutral {
            font-size: 0.95rem;
            padding: 0.85rem 1rem;
        }
    }
    @media (max-width: 480px) {
        h1 {
            font-size: 1.35rem !important;
        }
        .ai-badge {
            font-size: 0.65rem;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

PF_RATE = 0.12


def format_inr(amount: float) -> str:
    return f"₹{amount:,.0f}"


def section_card():
    """Create a bordered card container for a page section."""
    return st.container(border=True)

def compute_annual_pf(annual_basic: float) -> float:
    return PF_RATE * annual_basic


def resolve_cash_salary(
    gross_salary: float,
    employer_pf: float,
    includes_employer_pf: bool,
) -> tuple[float, float]:
    """Return (cash salary for tax/in-hand, employer PF removed from CTC)."""
    if includes_employer_pf:
        removed = min(max(employer_pf, 0.0), gross_salary)
        return max(gross_salary - removed, 0.0), removed
    return gross_salary, 0.0


def compute_monthly_in_hand(
    cash_salary: float,
    total_tax: float,
    employee_pf: float,
) -> float:
    return max((cash_salary - total_tax - employee_pf) / 12, 0.0)


def render_tax_bar_chart(new_tax: float, old_tax: float) -> None:
    """Horizontal bar chart — green = lower tax, red = higher tax."""
    regimes = ["New Regime", "Old Regime"]
    taxes = [new_tax, old_tax]

    # Explicit per-regime colors so New Regime is green when it wins
    colors = [
        "#2e7d32" if new_tax <= old_tax else "#c62828",
        "#2e7d32" if old_tax <= new_tax else "#c62828",
    ]

    fig, ax = plt.subplots(figsize=(9, 2.4))
    fig.patch.set_facecolor("#ffffff")
    ax.set_facecolor("#ffffff")

    bars = ax.barh(regimes, taxes, color=colors, height=0.55, edgecolor="white", linewidth=1.5)
    ax.set_xlabel("Total tax payable (₹)", fontsize=10, color="#444")
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _p: f"₹{x:,.0f}"))
    ax.tick_params(axis="both", labelsize=9, colors="#444")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#ddd")
    ax.spines["bottom"].set_color("#ddd")

    max_tax = max(taxes) if max(taxes) > 0 else 1

    for i, (bar, tax) in enumerate(zip(bars, taxes)):
        ax.text(
            bar.get_width() + max_tax * 0.02,
            bar.get_y() + bar.get_height() / 2,
            f"₹{tax:,.0f}",
            va="center",
            ha="left",
            fontsize=10,
            fontweight="bold",
            color=colors[i],
        )

    ax.set_xlim(0, max_tax * 1.25)
    plt.tight_layout()
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)

    legend_col1, legend_col2 = st.columns(2)
    with legend_col1:
        st.markdown(
            '<span style="color:#2e7d32;font-weight:600;">■</span> Green = lower tax',
            unsafe_allow_html=True,
        )
    with legend_col2:
        st.markdown(
            '<span style="color:#c62828;font-weight:600;">■</span> Red = higher tax',
            unsafe_allow_html=True,
        )


def render_tax_column(title: str, result, highlight: bool) -> None:
    with st.container(border=True):
        badge = " ✓ Lower tax" if highlight else ""
        st.markdown(f"**{title}**{badge}")

        st.metric("Taxable income", format_inr(result.taxable_income))
        st.metric("Tax (before cess)", format_inr(result.tax_after_rebate))
        st.metric("Cess (4%)", format_inr(result.cess))
        st.metric("Total tax payable", format_inr(result.total_tax))

        with st.expander("See calculation details"):
            st.write(f"**Gross salary:** {format_inr(result.gross_salary)}")
            st.write(f"**Standard deduction:** −{format_inr(result.standard_deduction)}")
            if result.hra_exemption:
                st.write(f"**HRA exemption:** −{format_inr(result.hra_exemption)}")
            if result.section_80c:
                st.write(f"**Section 80C:** −{format_inr(result.section_80c)}")
            if result.nps_80ccd_1b:
                st.write(f"**NPS (80CCD(1B)):** −{format_inr(result.nps_80ccd_1b)}")
            st.write(f"**Tax before rebate:** {format_inr(result.tax_before_rebate)}")
            if result.rebate:
                st.write(f"**Section 87A rebate:** −{format_inr(result.rebate)}")
            if result.marginal_relief:
                st.write(f"**Marginal relief:** −{format_inr(result.marginal_relief)}")


# --- Header ---
st.markdown('<p class="ai-badge">Powered by AI-assisted calculations</p>', unsafe_allow_html=True)
st.title("🇮🇳 Income Tax Calculator")
st.caption("FY 2025-26 (Assessment Year 2026-27) · Budget 2025 slabs · For salaried employees")

st.markdown(
    '<div class="disclaimer-top">'
    "<strong>Note:</strong> This calculator provides indicative estimates only. "
    "It is not financial, legal, or tax advice."
    "</div>",
    unsafe_allow_html=True,
)

# --- Inputs ---
with section_card():
    st.markdown("### Your salary details")
    col1, col2 = st.columns(2)

    with col1:
        gross_salary = st.number_input(
            "Annual gross salary (₹)",
            min_value=0,
            value=1_200_000,
            step=10_000,
            help=(
                "Cash salary before tax, OR full CTC if you tick the employer-PF box below. "
                "Employer PF is not taxable and is not paid into your bank account."
            ),
        )
        annual_basic = st.number_input(
            "Annual basic salary (₹)",
            min_value=0,
            value=int(1_200_000 * 0.4),
            step=10_000,
            help="Used to estimate employee & employer PF at 12% of basic each.",
        )
        hra_exemption = st.number_input(
            "HRA exemption (₹) — old regime only",
            min_value=0,
            value=0,
            step=5_000,
            help="Estimated HRA tax exemption. Not available under the new regime.",
        )
        section_80c = st.number_input(
            "Section 80C investments (₹)",
            min_value=0,
            max_value=150_000,
            value=0,
            step=5_000,
            help="PPF, ELSS, life insurance, EPF, etc. Maximum ₹1.5 lakh. Old regime only.",
        )

    with col2:
        nps_contribution = st.number_input(
            "Additional NPS contribution — 80CCD(1B) (₹)",
            min_value=0,
            max_value=50_000,
            value=0,
            step=5_000,
            help="Voluntary NPS over and above 80C. Max ₹50,000. Old regime only.",
        )
        standard_deduction = st.number_input(
            "Standard deduction (₹)",
            min_value=0,
            value=STATUTORY_STD_DED_NEW,
            step=5_000,
            help=(
                f"Statutory limits: ₹{STATUTORY_STD_DED_NEW:,} (new regime) and "
                f"₹{STATUTORY_STD_DED_OLD:,} (old regime)."
            ),
        )
        employer_pf = st.number_input(
            "Annual employer PF contribution (₹)",
            min_value=0,
            value=int(1_200_000 * 0.4 * PF_RATE),
            step=1_000,
            help="Employer's EPF share — typically 12% of basic. Not taxed and not part of in-hand pay.",
        )
        includes_employer_pf = st.checkbox(
            "My gross salary includes employer PF (CTC)",
            value=False,
            help=(
                "Tick if the amount above is CTC. We subtract employer PF before calculating "
                "tax and in-hand salary, since it never reaches your bank account."
            ),
        )

employee_pf = compute_annual_pf(annual_basic)
monthly_employee_pf = employee_pf / 12
monthly_employer_pf = employer_pf / 12

cash_salary, employer_pf_removed = resolve_cash_salary(
    gross_salary, employer_pf, includes_employer_pf
)

# --- Tax calculation (on cash salary; employer PF is tax-exempt) ---
new_result, old_result, better_regime, savings = compare_regimes(
    cash_salary,
    standard_deduction,
    hra_exemption,
    section_80c,
    nps_contribution,
)

monthly_in_hand_new = compute_monthly_in_hand(cash_salary, new_result.total_tax, employee_pf)
monthly_in_hand_old = compute_monthly_in_hand(cash_salary, old_result.total_tax, employee_pf)
monthly_savings = savings / 12

# --- Regime comparison ---
with section_card():
    st.markdown("### Tax comparison")

    if better_regime == "New Regime" and savings > 0:
        st.success(
            f"✅ New Regime saves you {format_inr(savings)} annually "
            f"— {format_inr(monthly_savings)} per month"
        )
    elif better_regime == "Old Regime" and savings > 0:
        st.markdown(
            f'<div class="recommendation-neutral">'
            f"<strong>Old Regime</strong> saves you {format_inr(savings)} annually "
            f"({format_inr(monthly_savings)} per month) compared to the new regime."
            f"</div>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="recommendation-neutral">'
            "Both regimes result in the <strong>same tax liability</strong> for your inputs."
            "</div>",
            unsafe_allow_html=True,
        )

    render_tax_bar_chart(new_result.total_tax, old_result.total_tax)

    result_col1, result_col2 = st.columns(2)
    with result_col1:
        render_tax_column(
            "New Regime (Budget 2025 slabs)",
            new_result,
            highlight=better_regime == "New Regime",
        )
    with result_col2:
        render_tax_column(
            "Old Regime",
            old_result,
            highlight=better_regime == "Old Regime",
        )

# --- Monthly in-hand salary ---
with section_card():
    st.markdown("### Estimated monthly in-hand salary")

    pf_note = (
        f"Employee PF: {format_inr(monthly_employee_pf)}/mo ({PF_RATE:.0%} of basic). "
    )
    if includes_employer_pf:
        pf_note += (
            f"Employer PF ({format_inr(monthly_employer_pf)}/mo) removed from CTC — "
            "it is not taxable and not paid to you. "
        )
    st.caption(
        pf_note + "Indicative only — excludes professional tax, insurance, and other deductions."
    )

    if includes_employer_pf:
        st.info(
            f"**CTC entered:** {format_inr(gross_salary)} → "
            f"**Cash salary used for tax:** {format_inr(cash_salary)} "
            f"(after removing employer PF {format_inr(employer_pf_removed)})"
        )

    in_hand_col1, in_hand_col2 = st.columns(2)
    with in_hand_col1:
        st.metric("New regime — monthly in-hand", format_inr(monthly_in_hand_new))
        st.caption(
            f"Cash salary: {format_inr(cash_salary)} · "
            f"Tax: {format_inr(new_result.total_tax)} · "
            f"Employee PF: {format_inr(employee_pf)}"
        )
    with in_hand_col2:
        st.metric("Old regime — monthly in-hand", format_inr(monthly_in_hand_old))
        st.caption(
            f"Cash salary: {format_inr(cash_salary)} · "
            f"Tax: {format_inr(old_result.total_tax)} · "
            f"Employee PF: {format_inr(employee_pf)}"
        )

# --- AI assistant placeholder ---
with section_card():
    st.markdown("### Tax help")
    st.markdown(
        '<div class="coming-soon-card">'
        "<h3>🤖 AI Tax Assistant — Coming Soon!</h3>"
        "<p>Have questions about deductions or which regime suits you? "
        "Our AI assistant will be available soon to help you in plain English.</p>"
        "</div>",
        unsafe_allow_html=True,
    )

# --- Footer ---
st.markdown(
    '<div class="site-footer">'
    "This calculator uses AI-assisted logic and standard tax mathematics for indicative purposes only. "
    "Results may vary. Please consult a tax professional for personalised advice."
    "</div>",
    unsafe_allow_html=True,
)
