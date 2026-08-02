import random
from data import DAYS, PERIODS, ROOMS, ROOM_TYPE_FOR_SESSION, required_capacity


class Variable:
    __slots__ = ("vid", "code", "name", "session", "sections", "instructor",
                 "room_types", "capacity_needed")

    def __init__(self, vid, code, name, session, sections, instructor, room_types):
        self.vid = vid
        self.code = code
        self.name = name
        self.session = session          # "LEC" / "TUT" / "LAB"
        self.sections = sections        # list[str]
        self.instructor = instructor    # str
        self.room_types = room_types    # tuple[str]
        self.capacity_needed = required_capacity(sections)

    def __repr__(self):
        return f"<{self.vid} {self.code} {self.session} {self.sections} {self.instructor}>"


def build_variables(courses):
    variables = []
    for c in courses:
        instr_map = c["instructors"]
        for session in c["sessions"]:
            room_types = ROOM_TYPE_FOR_SESSION[session]
            instr = instr_map.get(session, "TBA")
            if session == "LEC":
                # one shared session for every section taking the course
                iname = instr if isinstance(instr, str) else instr[0]
                vid = f"{c['code']}-LEC"
                variables.append(Variable(vid, c["code"], c["name"], "LEC",
                                           list(c["sections"]), iname, room_types))
            else:
                # one variable per section (parallel groups)
                for i, sec in enumerate(c["sections"]):
                    if isinstance(instr, list):
                        iname = instr[i % len(instr)]
                    else:
                        iname = instr
                    vid = f"{c['code']}-{session}-{sec}"
                    variables.append(Variable(vid, c["code"], c["name"], session,
                                               [sec], iname, room_types))
    return variables


def build_domain(var):
    rooms = [r["id"] for r in ROOMS if r["type"] in var.room_types and r["capacity"] >= var.capacity_needed]
    domain = [(d, p, r) for d in range(len(DAYS)) for p in range(len(PERIODS)) for r in rooms]
    return domain


def schedule_cost(assignment, by_id):
    from collections import defaultdict
    per_section_day = defaultdict(list)
    for vid, (day, period, _room) in assignment.items():
        v = by_id[vid]
        for sec in v.sections:
            per_section_day[(sec, day)].append(period)

    cost = 0
    for periods in per_section_day.values():
        periods.sort()
        for a, b in zip(periods, periods[1:]):
            gap = (b - a - 1)
            if gap > 0:
                cost += gap
    return cost


class Solver:
    def __init__(self, courses, seed=42, max_restarts=20):
        self.variables = build_variables(courses)
        self.domains = {v.vid: build_domain(v) for v in self.variables}
        self.rng = random.Random(seed)
        self.max_restarts = max_restarts

    def _conflicts(self, var, value, assignment):
        day, period, room = value
        for other_vid, other_val in assignment.items():
            o_day, o_period, o_room = other_val
            if o_day != day or o_period != period:
                continue
            other_var = self.by_id[other_vid]
            if o_room == room:
                return True
            if set(other_var.sections) & set(var.sections):
                return True
            if other_var.instructor == var.instructor and var.instructor != "TBA":
                return True
        return False

    def solve(self):
        self.by_id = {v.vid: v for v in self.variables}
        complete_solutions = []
        best_partial = {}

        for attempt in range(self.max_restarts):
            order = sorted(self.variables, key=lambda v: -len(v.sections))
            self.rng.shuffle(order)
            order.sort(key=lambda v: -len(v.sections))
            assignment = {}
            ok = self._backtrack(order, 0, assignment, limit=[60000])
            if ok:
                complete_solutions.append(dict(assignment))
            elif len(assignment) > len(best_partial):
                best_partial = dict(assignment)

        if complete_solutions:
            best = min(complete_solutions, key=lambda a: schedule_cost(a, self.by_id))
            self.best_cost = schedule_cost(best, self.by_id)
            self.solutions_found = len(complete_solutions)
            return best, self.by_id

        self.best_cost = None
        self.solutions_found = 0
        return best_partial, self.by_id

    def _backtrack(self, order, idx, assignment, limit):
        if idx == len(order):
            return True
        limit[0] -= 1
        if limit[0] <= 0:
            return False
        var = order[idx]
        domain = list(self.domains[var.vid])
        self.rng.shuffle(domain)
        for value in domain:
            if not self._conflicts(var, value, assignment):
                assignment[var.vid] = value
                if self._backtrack(order, idx + 1, assignment, limit):
                    return True
                del assignment[var.vid]
        return False
