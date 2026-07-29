import os
from data import courses_for
from csp_solver import Solver
from verify import verify
from export import export_semester

OUT_DIR = os.path.join(os.path.dirname(__file__), "output")
os.makedirs(OUT_DIR, exist_ok=True)

for semester in ("Fall", "Spring"):
    courses = courses_for(semester)
    solver = Solver(courses)
    assignment, by_id = solver.solve()

    violations = verify(assignment, by_id, total_variables=len(solver.variables))
    status = "VALID - zero constraint violations" if not violations else f"{len(violations)} VIOLATIONS FOUND"
    print(f"[{semester}] variables={len(solver.variables)} assigned={len(assignment)} -> {status}")
    print(f"[{semester}] complete solutions explored={solver.solutions_found}, "
          f"best schedule-gap cost={solver.best_cost}")
    for v in violations[:10]:
        print("   ", v)

    out_path = os.path.join(OUT_DIR, f"CSIT_Timetable_{semester}.xlsx")
    export_semester(semester, assignment, by_id, out_path)
    print(f"[{semester}] written -> {out_path}")
