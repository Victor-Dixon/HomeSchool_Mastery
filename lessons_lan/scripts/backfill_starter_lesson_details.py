"""
Project: Homeschool Lessons (Dream.OS)
File: scripts/backfill_starter_lesson_details.py
Purpose: Backfill details/notes for early seeded lessons that were created without content.
Owner: Local family deployment (homeschool)
"""

import os
import sqlite3


def main():
    db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "instance", "homeschool.db"))
    con = sqlite3.connect(db_path)
    cur = con.cursor()

    # Add details to Chris "Cells" lesson if it's empty.
    cur.execute(
        """
        UPDATE lessons
        SET notes = ?
        WHERE title LIKE 'Chapter 4: Cells%'
          AND subject = 'Science'
          AND (notes IS NULL OR TRIM(notes) = '')
        """,
        (
            "Goal: Understand basic cell parts and what they do.\n\n"
            "Quick notes:\n"
            "- Cell membrane: controls what enters/leaves\n"
            "- Cytoplasm: gel where parts float\n"
            "- Nucleus: control center; DNA\n"
            "- Mitochondria: energy (powerhouse)\n\n"
            "Questions:\n"
            "1) Which part is the 'control center' of the cell?\n"
            "2) What is the main job of the cell membrane?\n"
            "3) Why are mitochondria important?\n\n"
            "Challenge:\n"
            "Explain the difference between the nucleus and the cell membrane in 2 sentences."
        ,),
    )

    con.commit()
    con.close()
    print("backfilled")


if __name__ == "__main__":
    main()

