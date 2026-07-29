# Automatic Timetable Generator 

A constraint-satisfaction engine that generates conflict-free, optimized weekly
timetables for all 4 years of the CSIT program, for both the **Fall** and
**Spring** semesters, and exports each as a clean, human-readable Excel
workbook.

Given a course list, room inventory, and instructor assignments, the solver
finds a schedule where no room, section, or instructor is ever double-booked
— then picks the *best* such schedule out of several it finds, rather than
just the first one that works.

---

## What it does

- Builds one independent scheduling problem per semester (Fall and Spring
  never share timeslots, rooms, or course lists).
- Within each semester, schedules every year (1–4) and every section/track
  (`Y1-G1`…`Y4-BIF`) at once, so cross-year and cross-track room/instructor
  conflicts are caught automatically.
- Distinguishes session types per course — **Lecture** (shared by every
  section of a course, one variable), **Tutorial**, and **Lab** (parallel,
  one variable per section) — matching how the department actually runs
  classes.
- Enforces hard constraints: no room double-booked, no section double-booked,
  no instructor double-booked, and every room must be large enough for the
  section(s) assigned to it.
- Optimizes for schedule quality on top of feasibility: it explores several
  independent solutions and keeps the one with the fewest idle gap-periods
  in students' daily schedules.
- Independently re-verifies the final schedule against every hard constraint
  before exporting, and flags an incomplete schedule if one somehow occurs.
- Exports two Excel workbooks (one per semester), each with a separate,
  color-coded, day-by-day sheet per year.

---

## Project structure

```
.
├── data.py          # Course list, rooms, sections, instructors, timeslots
├── csp_solver.py     # Variable/domain construction, hard constraints,
│                      backtracking search, soft-constraint scoring
├── verify.py         # Independent post-solve validator
├── export.py          # Excel workbook generation
├── main.py            # Entry point — runs both semesters end to end
└── output/            # Generated .xlsx files land here (created on first run)
```

**Why it's split this way:** `data.py` is the only file you should ever need
to edit to update the curriculum — everything downstream (solving,
verifying, exporting) works generically off whatever it defines. The solver
knows nothing about Excel; the exporter knows nothing about constraints.

---

## How it works

1. **`data.py`** defines the source of truth: courses per semester (with
   their required session types), room inventory (type + capacity), section
   groupings per year, and instructor assignments.
2. **`csp_solver.py`** turns that into a CSP:
   - **Variables** — one per (course, session type, section/group) that
     needs a slot. A shared lecture is a single variable covering every
     section taking that course; tutorials and labs get one variable per
     parallel section.
   - **Domain** — every `(day, period, room)` combination where the room's
     type matches the session type and its capacity covers the attendees.
   - **Hard constraints** — no two variables sharing a room, a section, or a
     named instructor may land on the same `(day, period)`.
   - **Search** — randomized backtracking with restarts. Several independent
     complete solutions are generated; the one with the lowest soft-cost
     (fewest same-day gaps between a section's classes) is kept.
3. **`verify.py`** re-checks the winning solution from scratch — independent
   of the solver's own bookkeeping — and reports any room/section/instructor
   clash or incomplete placement.
4. **`export.py`** lays the result out as a day × time grid per year, with
   course, session type, instructor, and room in each cell, color-coded by
   session type.

---

## Requirements

- Python 3.9+
- [`openpyxl`](https://pypi.org/project/openpyxl/) (only external dependency)

```bash
pip install openpyxl
```

---

## Running it

```bash
python main.py
```

This solves and exports both semesters in a few seconds. Console output
looks like:

```
[Fall] variables=149 assigned=149 -> VALID - zero constraint violations
[Fall] complete solutions explored=20, best schedule-gap cost=97
[Fall] written -> output/CSIT_Timetable_Fall.xlsx
[Spring] variables=150 assigned=150 -> VALID - zero constraint violations
[Spring] complete solutions explored=20, best schedule-gap cost=99
[Spring] written -> output/CSIT_Timetable_Spring.xlsx
```

The generated workbooks (`output/CSIT_Timetable_Fall.xlsx` and
`CSIT_Timetable_Spring.xlsx`) each contain 4 sheets — one per year — with
days as row groups, timeslots as rows, and sections as columns.

---

## Current scope, at a glance

| | |
|---|---|
| Semesters | Fall, Spring (solved independently) |
| Years | 1–4 |
| Sections/tracks | Y1–Y2: 4 parallel groups · Y3–Y4: 4 specialization tracks (CNC / AID / CSC / BIF) |
| Days / periods | 5 days × 8 periods/day |
| Courses | 44 per semester |
| Rooms | 85, typed as theater / hall / tutorial / lab |

---

## Known limitations

- **Room capacities and some instructor names are reasonable assumptions,
  not verified source data** — the original curriculum/room dataset didn't
  record exact enrollment numbers or every TA's real name, so these were
  filled in consistently (documented inline in `data.py`) rather than left
  blank. Replace them in `data.py` if you have the authoritative figures.
- **Soft-constraint optimization currently scores one thing**: same-day gaps
  in a section's schedule. Early/late-slot avoidance and instructor workload
  balancing aren't factored in yet — `schedule_cost()` in `csp_solver.py` is
  the place to extend this.
- **Electives with multiple real options** (e.g., a student choosing between
  two language courses) are currently modeled as a single combined course
  rather than a real choice — fine for generating one valid master
  timetable, not yet suited to per-student registration.
- The search is randomized backtracking with restarts, not a solver with a
  formal optimality guarantee. It comfortably handles the current problem
  size (under 5 seconds for both semesters); a much larger course catalog
  may need a constraint-programming backend (e.g. OR-Tools CP-SAT) instead.

---
