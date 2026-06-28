# India Tax Calculator — FY 2025-26

A simple Streamlit app for Indian salaried employees to compare income tax under the **new** and **old** tax regimes using Budget 2025-26 slabs.

## Features

- Input annual salary, HRA, 80C, NPS, and standard deduction
- Side-by-side tax comparison with clear savings recommendation
- Horizontal bar chart comparing regime tax (green = lower, red = higher)
- Estimated monthly in-hand salary after tax and PF
- AI Tax Assistant placeholder (coming soon)
- Indicative-only disclaimer (not financial advice)

## Setup

```bash
cd ~/Projects/india-tax-calculator
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Tax rules implemented (FY 2025-26)

**New regime:** Slabs 0–4L (nil), 4–8L (5%), 8–12L (10%), 12–16L (15%), 16–20L (20%), 20–24L (25%), above 24L (30%). Standard deduction ₹75,000. Section 87A rebate up to ₹60,000 for taxable income ≤ ₹12 lakh, with marginal relief above.

**Old regime:** Slabs 0–2.5L (nil), 2.5–5L (5%), 5–10L (20%), above 10L (30%). Standard deduction ₹50,000. Deductions for HRA, 80C (max ₹1.5L), and 80CCD(1B) NPS (max ₹50K). Section 87A rebate up to ₹12,500 for taxable income ≤ ₹5 lakh.

Both regimes include 4% health & education cess.

## Disclaimer

This tool provides indicative estimates only and is not a substitute for professional tax advice.
