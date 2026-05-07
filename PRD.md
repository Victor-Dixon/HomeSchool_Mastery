# Product Requirements Document

## Product

HomeSchool_Mastery is a local homeschool learning system focused on TEKS/STAAR skill mastery, daily lessons, adaptive review, vocabulary practice, and parent oversight.

## Users

- Students: complete lessons, practice, reviews, games, and mastery checks.
- Parent/Admin: monitors progress, assigns drills, reviews gaps, manages content and accounts.

## Core Requirements

1. Serve a LAN-accessible Flask learning app from lessons_lan/.
2. Track skill mastery and practice outcomes.
3. Support vocabulary and TEKS-aligned practice loops.
4. Provide student-safe navigation and parent/admin oversight.
5. Preserve local-first operation with testable behavior.

## Non-Goals

- Cloud dependency by default.
- Destructive cleanup of learner history.
- Untested route or mastery changes.
