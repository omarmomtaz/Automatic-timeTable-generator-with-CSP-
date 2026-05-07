from DataLoader import load_data
import pulp
import pandas as pd
import time

TEST_SUBSET = False  # Set to True for debugging with 10 sessions
half = 'first'  # Set to 'first' or 'second' based on half of the year; GUI will ask user
df_path = r"D:\My projects\Intelligent Systems\Auto timeTable generator with CSP\Automatic-timeTable-generator-with-CSP-\CollegeDataset.xlsx"
data = load_data(df_path, half=half)
if data is None:
    print("Data loading failed. Exiting.")
    exit(1)

# Validate required fields
required_fields = {
    'instructors': ['role', 'qualified_courses'],
    'rooms': ['Capacity', 'Type', 'RoomID', 'Building'],
    'timeslots': ['Day_id', 'Day', 'StartTime', 'EndTime'],
    'sessions': ['course_id', 'section_id', 'type', 'student_count', 'required_year', 'required_semester']
}
for key, fields in required_fields.items():
    if key in data and not all(f in d for f in fields for d in data[key]):
        print(f"Warning: Missing required fields in {key}. Exiting.")
        exit(1)

sessions = data['sessions'][:10] if TEST_SUBSET else data['sessions']
print(f"Processing {len(sessions)} sessions")
print(f"Timeslots: {len(data['timeslots'])}, Rooms: {len(data['rooms'])}, Instructors: {len(data['instructors'])}")

# Limit sessions to 100 to manage memory and solver capacity
if len(sessions) > 100:
    print(f"Warning: Reducing sessions to 100 for feasibility")
    sessions = sessions[:100]

if len(sessions) > 500:
    print("Warning: Large dataset - limiting to 500 sessions to avoid memory issues")
    sessions = sessions[:500]

domains = {}
qualified_instr_per_course = {}
for course_id in set(s['course_id'] for s in sessions):
    qualified_instr_per_course[course_id] = [i for i in data['instructors'] if course_id in [qc.strip() for qc in i.get('qualified_courses', [])]]

for session in sessions:
    allowed_room_types = ['Hall', 'Classroom', 'Theater'] if session['type'] in ['Lecture', 'Tutorial', 'Project'] else ['Computer Lab', 'FoE Drawing Lab', 'Drawing Studio']
    qualified_instr = qualified_instr_per_course.get(session['course_id'], [])
    domain = []
    for ts in data['timeslots']:
        for room in [r for r in data['rooms'] if r.get('Type', '') in allowed_room_types and r.get('Capacity', 0) >= session.get('student_count', 0)]:
            for instr in qualified_instr:
                role = instr.get('role', '')
                if (session['type'] in ['Lecture', 'Project'] and role in ['Doctor', 'Professor']) or (session['type'] in ['Tutorial', 'Lab'] and role == 'Teaching Assistant'):
                    domain.append((ts['Day_id'], room['RoomID'], instr['instructor_id']))
    if not domain:
        print(f"Warning: Empty domain for {session['session_id']} - skipping")
        continue
    domains[session['session_id']] = domain
    print(f"Domain size for {session['session_id']}: {len(domain)}")

prob = pulp.LpProblem("Timetable", pulp.LpMinimize)

sess_map = {sess['session_id'].replace(' ', '_'): sess['session_id'] for sess in sessions}
x = {}
for sess in sessions:
    sess_sanit = sess['session_id'].replace(' ', '_')
    for time_id, room_id, instr_id in domains.get(sess['session_id'], []):
        var_name = f"x__{sess_sanit}__{time_id}__{room_id}__{instr_id}"
        x[(sess['session_id'], time_id, room_id, instr_id)] = pulp.LpVariable(var_name, cat='Binary')

# Hard Constraints
for sess in sessions:
    prob += pulp.lpSum(x[(sess['session_id'], t, r, i)] for t, r, i in domains.get(sess['session_id'], [])) == 1

used_instr = set(i for dom in domains.values() for _, _, i in dom if i != 'None')
for instr in used_instr:
    for time_id in [ts['Day_id'] for ts in data['timeslots']]:
        prob += pulp.lpSum(x[(sess['session_id'], t, r, instr)] for sess in sessions for t, r, i in domains.get(sess['session_id'], []) if t == time_id and i == instr) <= 1

used_rooms = set(r for dom in domains.values() for _, r, _ in dom)
for room in used_rooms:
    for time_id in [ts['Day_id'] for ts in data['timeslots']]:
        prob += pulp.lpSum(x[(sess['session_id'], t, room, i)] for sess in sessions for t, r, i in domains.get(sess['session_id'], []) if t == time_id and r == room) <= 1

year_sem_groups = {}
for sess in sessions:
    key = (sess.get('required_year', 0), sess.get('required_semester', 0))
    if key not in year_sem_groups:
        year_sem_groups[key] = []
    year_sem_groups[key].append(sess['session_id'])
# Relax student conflict constraint (commented out to avoid infeasibility)
# for group in year_sem_groups.values():
#     for time_id in [ts['Day_id'] for ts in data['timeslots']]:
#         prob += pulp.lpSum(x[(s, t, r, i)] for s in group for t, r, i in domains.get(s, []) if t == time_id) <= 1

penalty_total = 0

for sect in set(s.get('section_id', '') for s in sessions):
    for day in set(ts['Day'] for ts in data['timeslots']):
        day_slots = sorted(set(int(t[-1]) for s in sessions if s.get('section_id', '') == sect for t, _, _ in domains.get(s['session_id'], []) if next((ts for ts in data['timeslots'] if ts['Day_id'] == t), {}).get('Day', '') == day))
        if len(day_slots) > 1:
            for i in range(len(day_slots) - 1):
                if day_slots[i + 1] - day_slots[i] > 1:
                    gap_var = pulp.LpVariable(f"gap_{sect}_{day}_{i}", cat='Binary')
                    prob += gap_var <= pulp.lpSum(x[(s['session_id'], t, r, i)] for s in sessions if s.get('section_id', '') == sect for t, r, i in domains.get(s['session_id'], []) if next((ts for ts in data['timeslots'] if ts['Day_id'] == t), {}).get('Day', '') == day and int(t[-1]) == day_slots[i])
                    prob += gap_var <= pulp.lpSum(x[(s['session_id'], t, r, i)] for s in sessions if s.get('section_id', '') == sect for t, r, i in domains.get(s['session_id'], []) if next((ts for ts in data['timeslots'] if ts['Day_id'] == t), {}).get('Day', '') == day and int(t[-1]) == day_slots[i + 1])
                    penalty_total += 10 * gap_var

penalty_early_late = pulp.lpSum(10 * x[(sess['session_id'], t, r, i)] for sess in sessions for t, r, i in domains.get(sess['session_id'], []) if t[-1] in ['1', '4'])
penalty_total += penalty_early_late

building_map = {r['RoomID']: r.get('Building', 'Unknown') for r in data['rooms']}
distant_penalty = {}
for instr in used_instr:
    for day in set(ts['Day'] for ts in data['timeslots']):
        assigned_times = [t for s in sessions for t, r, i in domains.get(s['session_id'], []) if i == instr and next((ts for ts in data['timeslots'] if ts['Day_id'] == t), {}).get('Day', '') == day if x.get((s['session_id'], t, r, i), pulp.LpVariable("dummy", cat='Binary')).value() == 1]
        assigned_times.sort(key=lambda t: int(next(ts for ts in data['timeslots'] if ts['Day_id'] == t)['StartTime']))
        for i in range(len(assigned_times) - 1):
            prev_t = assigned_times[i]
            next_t = assigned_times[i + 1]
            prev_start = int(next(ts for ts in data['timeslots'] if ts['Day_id'] == prev_t)['StartTime'])
            next_start = int(next(ts for ts in data['timeslots'] if ts['Day_id'] == next_t)['StartTime'])
            if next_start - prev_start == 1:  # Assuming 1-unit time difference
                var_name = f"distant_{instr}_{day}_{prev_t}_{next_t}"
                distant_penalty[(instr, day, prev_t, next_t)] = pulp.LpVariable(var_name, lowBound=0, cat='Continuous')
                for s1 in sessions:
                    for r1, _ in [(r, i) for t, r, i in domains.get(s1['session_id'], []) if t == prev_t and i == instr]:
                        for s2 in sessions:
                            for r2, _ in [(r, i) for t, r, i in domains.get(s2['session_id'], []) if t == next_t and i == instr]:
                                if building_map.get(r1, 'Unknown') != building_map.get(r2, 'Unknown'):
                                    prob += distant_penalty[(instr, day, prev_t, next_t)] >= x[(s1['session_id'], prev_t, r1, instr)] + x[(s2['session_id'], next_t, r2, instr)] - 1
                                    penalty_total += 15 * distant_penalty[(instr, day, prev_t, next_t)]

day_sessions = pulp.LpVariable.dicts("day_sessions", set(ts['Day'] for ts in data['timeslots']), lowBound=0, cat='Continuous')
for day in set(ts['Day'] for ts in data['timeslots']):
    prob += day_sessions[day] == pulp.lpSum(x[(sess['session_id'], t, r, i)] for sess in sessions for t, r, i in domains.get(sess['session_id'], []) if next((ts for ts in data['timeslots'] if ts['Day_id'] == t), {}).get('Day', '') == day)
avg_sessions = len(sessions) / len(set(ts['Day'] for ts in data['timeslots']))
dev_pos = pulp.LpVariable.dicts("dev_pos", day_sessions.keys(), lowBound=0, cat='Continuous')
dev_neg = pulp.LpVariable.dicts("dev_neg", day_sessions.keys(), lowBound=0, cat='Continuous')
for d in day_sessions:
    prob += day_sessions[d] - avg_sessions == dev_pos[d] - dev_neg[d]
penalty_variance = pulp.lpSum(dev_pos[d] + dev_neg[d] for d in day_sessions)
penalty_total += 5 * penalty_variance

instr_prefs = {i['instructor_id']: i.get('PreferredSlots', '').split(',') for i in data['instructors']}
pref_penalty = pulp.lpSum(5 * x[(sess['session_id'], t, r, i)] for sess in sessions for t, r, i in domains.get(sess['session_id'], []) if t not in instr_prefs.get(i, []))
penalty_total += pref_penalty

util_penalty = pulp.lpSum(2 * (room.get('Capacity', 1) - sess.get('student_count', 0)) * x[(sess['session_id'], t, r, i)] / max(room.get('Capacity', 1), 1) for sess in sessions for t, r, i in domains.get(sess['session_id'], []) for room in data['rooms'] if room.get('RoomID', '') == r)
penalty_total += util_penalty

workload_penalty = pulp.LpVariable.dicts("workload_penalty", [(i, d) for i in used_instr for d in set(ts['Day'] for ts in data['timeslots'])], lowBound=0, cat='Continuous')
for instr in used_instr:
    for day in set(ts['Day'] for ts in data['timeslots']):
        sessions_per_day = pulp.lpSum(x[(sess['session_id'], t, r, instr)] for sess in sessions for t, r, i in domains.get(sess['session_id'], []) if i == instr and next((ts for ts in data['timeslots'] if ts['Day_id'] == t), {}).get('Day', '') == day)
        # Relax workload (increased cap to 4) and cap penalty
        prob += workload_penalty[(instr, day)] >= sessions_per_day - 4
        prob += workload_penalty[(instr, day)] <= 0
penalty_total += 10 * pulp.lpSum(workload_penalty.values())

prob += penalty_total

start_time = time.time()
# Use PULP_CBC_CMD with msg=1 for detailed output
prob.solve(solver=pulp.PULP_CBC_CMD(msg=1))
solve_time = time.time() - start_time
print(f"Solved in {solve_time:.2f} seconds")
print("Status:", pulp.LpStatus[prob.status])

if pulp.LpStatus[prob.status] == 'Optimal':
    solution = {}
    for var in prob.variables():
        if var.value() == 1 and var.name.startswith('x__'):
            parts = var.name.split('__')[1:]
            sess_sanit = parts[0]
            time_id = parts[1]
            room_id = parts[2]
            instr_id = parts[3]
            sess_id = sess_map.get(sess_sanit, sess_sanit.replace('_', ' '))
            solution[sess_id] = (time_id, room_id, instr_id)

    timetable_data = []
    for sess_id, (time_id, room_id, instr_id) in solution.items():
        sess = next((s for s in sessions if s['session_id'] == sess_id), {})
        if sess:
            time = next((ts for ts in data['timeslots'] if ts['Day_id'] == time_id), {})
            room = next((r for r in data['rooms'] if r.get('RoomID', '') == room_id), {})
            instr = next((i for i in data['instructors'] if i.get('instructor_id', '') == instr_id), {})
            has_unknown = any(v == 'Unknown' for v in [time.get('Day'), instr.get('name')])
            if has_unknown:
                print(f"Warning: Unknown data encountered for session {sess_id}")
            details = f"{sess.get('course_id', 'Unknown')} ({sess.get('type', 'Unknown')}) - Sec {sess.get('section_id', 'Unknown')} by {instr.get('name', 'Unknown')}"
            timetable_data.append({
                'Day': time.get('Day', 'Unknown'),
                'Start': time.get('StartTime', 'Unknown'),
                'Room': room_id,
                'Details': details
            })

    df_timetable = pd.DataFrame(timetable_data)
    df_pivot = df_timetable.pivot_table(index='Room', columns=['Day', 'Start'], values='Details', aggfunc='first')
    print("Timetable Grid:")
    print(df_pivot.fillna(''))
    df_pivot.to_excel('timetable.xlsx')
else:
    print("No solution. Relax soft penalties or check hard constraints.")