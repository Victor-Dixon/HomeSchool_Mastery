"""
questions.py — TEKS-Aligned Question Bank
Add new questions here anytime. Each dict maps to a TEKS skill.
Format:
    skill      — TEKS skill label (used for progress tracking)
    question   — What Chris sees
    answer     — Exact expected answer (lowercase, stripped)
    hint       — Optional one-line hint shown on wrong answer
"""

QUESTIONS = [
    # ── Number & Operations ──────────────────────────────────────────────
    {
        "skill": "Integer Addition",
        "question": "-4 + 9 = ?",
        "answer": "5",
        "hint": "Start at -4 on a number line and move 9 steps right."
    },
    {
        "skill": "Integer Subtraction",
        "question": "6 - 11 = ?",
        "answer": "-5",
        "hint": "Subtracting a bigger number from a smaller one gives a negative result."
    },
    {
        "skill": "Integer Multiplication",
        "question": "-3 × 4 = ?",
        "answer": "-12",
        "hint": "Negative × Positive = Negative."
    },
    {
        "skill": "Integer Division",
        "question": "12 ÷ -3 = ?",
        "answer": "-4",
        "hint": "Positive ÷ Negative = Negative."
    },

    # ── Fractions & Decimals ─────────────────────────────────────────────
    {
        "skill": "Fraction to Decimal",
        "question": "Convert 1/2 to a decimal.",
        "answer": "0.5",
        "hint": "Divide the top number by the bottom number: 1 ÷ 2."
    },
    {
        "skill": "Decimal to Percent",
        "question": "Convert 0.25 to a percent.",
        "answer": "25%",
        "hint": "Multiply the decimal by 100 and add the % sign."
    },
    {
        "skill": "Fraction to Percent",
        "question": "Convert 3/4 to a percent.",
        "answer": "75%",
        "hint": "3 ÷ 4 = 0.75 → × 100 = 75%."
    },

    # ── Expressions & Equations ──────────────────────────────────────────
    {
        "skill": "One-Step Equation",
        "question": "Solve: x + 5 = 12",
        "answer": "7",
        "hint": "Subtract 5 from both sides."
    },
    {
        "skill": "One-Step Equation",
        "question": "Solve: 2x = 10",
        "answer": "5",
        "hint": "Divide both sides by 2."
    },
    {
        "skill": "Two-Step Equation",
        "question": "Solve: 2x + 3 = 11",
        "answer": "4",
        "hint": "Subtract 3 first, then divide by 2."
    },

    # ── Percents & Financial Literacy ────────────────────────────────────
    {
        "skill": "Percent of a Number",
        "question": "What is 25% of 80?",
        "answer": "20",
        "hint": "Multiply 80 × 0.25."
    },
    {
        "skill": "Discount",
        "question": "A $20 game is 25% off. What is the sale price?",
        "answer": "$15",
        "hint": "Find 25% of $20, then subtract from $20."
    },
    {
        "skill": "Simple Interest",
        "question": "Simple interest: $100 at 5% for 2 years. How much interest?",
        "answer": "$10",
        "hint": "I = P × r × t → 100 × 0.05 × 2."
    },

    # ── Ratios & Proportions ─────────────────────────────────────────────
    {
        "skill": "Unit Rate",
        "question": "If you drive 120 miles in 2 hours, what is your speed in miles per hour?",
        "answer": "60",
        "hint": "Divide total miles by total hours."
    },
    {
        "skill": "Ratio",
        "question": "Simplify the ratio 8:12.",
        "answer": "2:3",
        "hint": "Divide both sides by the GCF (4)."
    },

    # ── Geometry ─────────────────────────────────────────────────────────
    {
        "skill": "Area of Triangle",
        "question": "Area of a triangle: base = 6, height = 4. What is the area?",
        "answer": "12",
        "hint": "A = ½ × base × height."
    },
    {
        "skill": "Area of Circle",
        "question": "Area of a circle with radius 7. Use π ≈ 3.14. Round to nearest whole number.",
        "answer": "154",
        "hint": "A = π × r² → 3.14 × 49."
    },

    # ── Data & Probability ───────────────────────────────────────────────
    {
        "skill": "Mean",
        "question": "Find the mean: 4, 8, 6, 10, 2",
        "answer": "6",
        "hint": "Add all numbers, then divide by how many there are."
    },
    {
        "skill": "Probability",
        "question": "A bag has 3 red and 7 blue marbles. What is the probability of picking red? (fraction)",
        "answer": "3/10",
        "hint": "Probability = favorable outcomes ÷ total outcomes."
    },
]


def get_questions_by_skill(skill_name: str) -> list:
    """Return all questions matching a specific skill."""
    return [q for q in QUESTIONS if q["skill"].lower() == skill_name.lower()]
