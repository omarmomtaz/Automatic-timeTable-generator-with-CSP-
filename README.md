# Automatic TimeTable Generator (CSP / Backtracking + ILP/PuLP)

A simple timetable-scheduling project that generates class timetables from an Excel dataset using:
- **CSP (constraint satisfaction)** with **backtracking** (`python-constraint`)
- **ILP/LP** formulation using **PuLP**

The project exports the generated schedule to `timetable.xlsx`.

---

## Features

- Loads course, instructor, room, time slot, and section data from `CollegeDataset.xlsx`
- Builds session variables (per course/section/type)
- Enforces hard constraints (e.g., no instructor overlap and no room overlap)
- Supports a semester “half” split (`first` / `second`) for filtering sessions
- Exports a readable timetable grid to Excel

---

## Project Structure (main files)

- `DataLoader.py`
  - Reads `CollegeDataset.xlsx` sheets and converts them into dictionaries
  - Produces a `sessions` list used by solvers
- `CSP_model (Back Tracking).py`
  - CSP variable/domain generation + hard constraints
  - Uses backtracking to find a feasible assignment
- `timetable_pulp.py`, `timetable_pulp2.py`
  - ILP formulation with PuLP + objective with soft penalties
- `pulp_trial*.py`, `trial.py`
  - Experiments / alternative solver setups

---

## Dataset

The solver expects an Excel file named:
- `CollegeDataset.xlsx`

Required sheet names (as used by `DataLoader.py`):
- `Courses`
- `Instructors`
- `Rooms`
- `TimeSlots`
- `Sections`

---

## Requirements

Python packages used in the codebase include:
- `pandas`
- `openpyxl` (for writing `.xlsx` files)
- `python-constraint` (for CSP)
- `pulp` (for ILP)

(Depending on your PuLP solver setup, an included CBC solver is typically used.)

---

## How to Run

### CSP (Backtracking)

```bash
python "CSP_model (Back Tracking).py"
```

If a solution is found, an Excel file named `timetable.xlsx` is written.

### PuLP / ILP

```bash
python timetable_pulp.py
```

Or try the variant:

```bash
python timetable_pulp2.py
```

---

## Notes / Tips

- If you hit “No solution found”, check the dataset constraints and/or reduce the problem size (some scripts filter to a small subset for testing).
- For semester splitting, `DataLoader.load_data(..., half='first'|'second')` is supported.
- Exported timetable output will be saved as `timetable.xlsx` in the project directory.

---

## Author

Project repository: **Automatic-timeTable-generator-with-CSP-**

