from DataLoader import load_data
import pulp
import pandas as pd
import time

df_path = r"D:\My projects\Intelligent Systems\Auto timeTable generator with CSP\Automatic-timeTable-generator-with-CSP-\CollegeDataset.xlsx"
data = load_data(df_path)
sessions = [s for s in data['sessions'] if s['required_year'] == 1 and s['section_id'] in ['1_1', '1_2']]

# Precompute domains
domains = {}
for session in sessions:
    allowed_room_types = ['Hall', 'Classroom', 'Theater'] if session['type'] in ['Lecture', 'Tutorial', 'Project'] else ['Computer Lab', 'FoE Drawing Lab', 'Drawing Studio']
    domain = []
    for ts in data['timeslots']:
        for room in data['rooms']:
            if room['Type'] in allowed_room_types and room['Capacity'] >= session['student_count']:
                for instr in data['instructors']:
                    if session['course_id'] in [qc.strip() for qc in instr['qualified_courses']]:
                        domain.append((ts['Day_id'], room['RoomID'], instr['instructor_id']))
    domains[session['session_id']] = domain

# PuLP model
prob = pulp.LpProblem("Timetable", pulp.LpMinimize)  # Using PuLP

# Binary variables: x[session_id, time_id, room_id, instr_id] = 1 if assigned
# Sanitize sess_id for var names (replace spaces)
sess_map = {sess['session_id'].replace(' ', '_'): sess['session_id'] for sess in sessions}
x = {}
for sess in sessions:
    sess_sanit = sess['session_id'].replace(' ', '_')
    for time_id, room_id, instr_id in domains[sess['session_id']]:
        var_name = f"x__{sess_sanit}__{time_id}__{room_id}__{instr_id}"
        x[(sess['session_id'], time_id, room_id, instr_id)] = pulp.LpVariable(var_name, cat='Binary')

# Constraint: Each session assigned exactly once
for sess in sessions:
    prob += pulp.lpSum(x[(sess['session_id'], t, r, i)] for t, r, i in domains[sess['session_id']]) == 1

# No instructor overlap (only used instructors)
used_instr = set(i for dom in domains.values() for _, _, i in dom)
for instr in used_instr:
    for time_id in [ts['Day_id'] for ts in data['timeslots']]:
        prob += pulp.lpSum(x[(sess['session_id'], t, r, instr)] for sess in sessions for t, r, i in domains[sess['session_id']] if t == time_id and i == instr) <= 1

# No room overlap (only used rooms)
used_rooms = set(r for dom in domains.values() for _, r, _ in dom)
for room in used_rooms:
    for time_id in [ts['Day_id'] for ts in data['timeslots']]:
        prob += pulp.lpSum(x[(sess['session_id'], t, room, i)] for sess in sessions for t, r, i in domains[sess['session_id']] if t == time_id and r == room) <= 1

# Soft constraints as objective (minimize penalties)
# Penalty for early/late slots (last char of Day_id is '1' or '4')
penalty_early_late = pulp.lpSum(10 * x[(sess['session_id'], t, r, i)] for sess in sessions for t, r, i in domains[sess['session_id']]
                                if t[-1] in ['1', '4'])
prob += penalty_early_late

# Solve with time measurement
start_time = time.time()
prob.solve()
solve_time = time.time() - start_time
print(f"Solved in {solve_time:.2f} seconds")
print("Status:", pulp.LpStatus[prob.status])

if pulp.LpStatus[prob.status] == 'Optimal':
    # Extract solution
    solution = {}
    for var in prob.variables():
        if var.value() == 1:
            parts = var.name.split('__')[1:]  # Split by '__' to get components
            sess_sanit = parts[0]  # First part is sanitized session ID
            time_id = parts[1]
            room_id = parts[2]
            instr_id = parts[3]
            sess_id = sess_map.get(sess_sanit, sess_sanit)  # Map back, fallback to sanitized if not found
            if sess_id not in [s['session_id'] for s in sessions]:
                print(f"Warning: Session ID {sess_id} not found in sessions, using {sess_sanit}")
                sess_id = sess_sanit.replace('_', ' ')  # Revert to original if mapping fails
            solution[sess_id] = (time_id, room_id, instr_id)

    # Output grid
    timetable_data = []
    for sess_id, (time_id, room_id, instr_id) in solution.items():
        sess = next((s for s in sessions if s['session_id'] == sess_id), None)
        if not sess:
            print(f"Warning: No session data for {sess_id}, skipping")
            continue
        time = next(ts for ts in data['timeslots'] if ts['Day_id'] == time_id)
        room = next(r for r in data['rooms'] if r['RoomID'] == room_id)
        instr = next(i for i in data['instructors'] if i['instructor_id'] == instr_id)
        details = f"{sess['course_id']} ({sess['type']}) - Sec {sess['section_id']} by {instr['name']}"
        timetable_data.append({
            'Day': time['Day'],
            'Time_ID': time_id,
            'Start': time['StartTime'],
            'Room': room_id,
            'Details': details
        })

    df_timetable = pd.DataFrame(timetable_data)
    # Pivot to grid: rooms as rows, time slots (grouped by day) as columns
    df_pivot = df_timetable.pivot_table(index='Room', columns=['Day', 'Start'], values='Details', aggfunc='first')
    print("Timetable Grid:")
    print(df_pivot.fillna(''))
    # Export to Excel
    df_pivot.to_excel('timetable.xlsx')
else:
    print("No solution. Relax soft penalties or check hard constraints.")