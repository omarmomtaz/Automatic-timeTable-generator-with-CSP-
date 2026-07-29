from collections import defaultdict


def verify(assignment, by_id, total_variables=None):
    """Return list of violation strings (empty = fully valid, COMPLETE schedule).

    total_variables: if given, an assignment covering fewer than this many
    sessions is reported as an INCOMPLETE SCHEDULE violation -- otherwise a
    partial (fallback) assignment could silently read as "zero violations".
    """
    room_slot = defaultdict(list)
    section_slot = defaultdict(list)
    instr_slot = defaultdict(list)
    violations = []

    if total_variables is not None and len(assignment) < total_variables:
        violations.append(
            f"INCOMPLETE SCHEDULE: only {len(assignment)}/{total_variables} sessions were placed"
        )

    for vid, (day, period, room) in assignment.items():
        v = by_id[vid]
        room_slot[(day, period, room)].append(vid)
        for sec in v.sections:
            section_slot[(day, period, sec)].append(vid)
        if v.instructor != "TBA":
            instr_slot[(day, period, v.instructor)].append(vid)

    for key, vids in room_slot.items():
        if len(vids) > 1:
            violations.append(f"ROOM CLASH at day{key[0]} period{key[1]} room{key[2]}: {vids}")
    for key, vids in section_slot.items():
        if len(vids) > 1:
            violations.append(f"SECTION CLASH {key[2]} at day{key[0]} period{key[1]}: {vids}")
    for key, vids in instr_slot.items():
        if len(vids) > 1:
            violations.append(f"INSTRUCTOR CLASH {key[2]} at day{key[0]} period{key[1]}: {vids}")

    return violations
