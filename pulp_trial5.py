from DataLoader import load_data
import pulp
import pandas as pd
import time
from datetime import datetime, time as dt_time

TEST_SUBSET = False  # Set to True for debugging with 10 sessions
half = 'first'  # Set to 'first' or 'second' based on half of the year; GUI will ask user
df_path = r"D:\My projects\Intelligent Systems\Auto timeTable generator with CSP\Automatic-timeTable-generator-with-CSP-\CollegeDataset.xlsx"
data = load_data(df_path, half=half)
if data is None:
    print("Data loading failed. Exiting. Please check the file path and content.")
    exit(1)

# Validate and inspect data
required_fields = {
    'instructors': ['role', 'qualified_courses'],
    'rooms': ['Capacity', 'Type', 'RoomID', 'Building'],
    'timeslots': ['Day_id', 'Day', 'StartTime', 'EndTime'],
    'sessions': ['course_id', 'section_id', 'type', 'student_count', 'required_year', 'required_semester']
}
for key, fields in required_fields.items():
    if key in data:
        for d in data[key]:
            if not all(f in d for f in fields):
                print(f"Warning: Missing fields in {key}: {d}")
        print(f"Loaded {key}: {len(data[key])} records")
    else:
        print(f"Warning: {key} data not found. Exiting.")
        exit(1)

sessions = data['sessions'][:10] if TEST_SUBSET else data['sessions']
print(f"Processing {len(sessions)} sessions")
print(f"Timeslots: {len(data['timeslots'])}, Rooms: {len(data['rooms'])}, Instructors: {len(data['instructors'])}")

# Limit sessions
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
        print(f"Warning: Empty domain for {session['session_id']} - consider relaxing constraints")
    else:
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
    prob += pulp.lpSum(x[(sess['session_id'], t, r, i)] for t, r, i in domains.get(sess['session_id'], [])) == 1, f"Session {sess['session_id']} assigned"

used_instr = set(i for dom in domains.values() for _, _, i in dom if i != 'None')
for instr in used_instr:
    for time_id in [ts['Day_id'] for ts in data['timeslots']]:
        prob += pulp.lpSum(x[(sess['session_id'], t, r, instr)] for sess in sessions for t, r, i in domains.get(sess['session_id'], []) if t == time_id and i == instr) <= 1, f"Instructor {instr} constraint"

used_rooms = set(r for dom in domains.values() for _, r, _ in dom)
for room in used_rooms:
    for time_id in [ts['Day_id'] for ts in data['timeslots']]:
        prob += pulp.lpSum(x[(sess['session_id'], t, room, i)] for sess in sessions for t, r, i in domains.get(sess['session_id'], []) if t == time_id and r == room) <= 1, f"Room {room} constraint"

# ... (rest of the constraints and penalties remain the same as before)

# Objective function
prob += penalty_total

start_time = time.time()
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

    # Define time slots
    time_slots = [
        ('09:00-09:45', '09:45-10:30', '10:45-11:30', '11:30-12:15'),
        ('12:30-13:15', '13:15-14:00', '14:15-15:00', '15:00-15:45')
    ]
    days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday']

    # Helper function to convert datetime.datetime to minutes
    def time_to_minutes(t):
        if isinstance(t, datetime):
            return t.hour * 60 + t.minute
        elif isinstance(t, str):
            try:
                return datetime.strptime(t, '%H:%M').hour * 60 + datetime.strptime(t, '%H:%M').minute
            except ValueError:
                print(f"Warning: Invalid time string format for value: {t}")
                return None
        print(f"Warning: Unexpected type for time value: {type(t)}, value: {t}")
        return None

    # Populate timetable data
    timetable_data = []
    for sess_id, (time_id, room_id, instr_id) in solution.items():
        sess = next((s for s in sessions if s['session_id'] == sess_id), {})
        if sess:
            time = next((ts for ts in data['timeslots'] if ts['Day_id'] == time_id), {})
            room = next((r for r in data['rooms'] if r.get('RoomID', '') == room_id), {})
            instr = next((i for i in data['instructors'] if i.get('instructor_id', '') == instr_id), {})
            start_time = time.get('StartTime')
            start_minutes = time_to_minutes(start_time)
            if start_minutes is None:
                print(f"Warning: Skipping session {sess_id} due to invalid start time")
                continue
            day = time.get('Day', 'Unknown')
            slot_idx = next((i for i, slots in enumerate(time_slots) if any(start_minutes >= time_to_minutes(datetime.strptime(s.split('-')[0], '%H:%M')) and start_minutes < time_to_minutes(datetime.strptime(s.split('-')[1], '%H:%M')) for s in slots)), 0)
            slot = time_slots[slot_idx].index(next((s for s in time_slots[slot_idx] if start_minutes >= time_to_minutes(datetime.strptime(s.split('-')[0], '%H:%M')) and start_minutes < time_to_minutes(datetime.strptime(s.split('-')[1], '%H:%M'))), time_slots[slot_idx][0]))
            details = f"{sess.get('course_id', 'Unknown')} ({sess.get('type', 'Unknown')}) by {instr.get('name', 'Unknown')} - Room: {room_id}"
            timetable_data.append({
                'Day': day,
                'TimeSlot': time_slots[slot_idx][slot],
                'Course': sess.get('course_id', 'Unknown'),
                'Instructor': instr.get('name', 'Unknown'),
                'Room': room_id
            })

    # Create and populate DataFrame
    df_timetable = pd.DataFrame(timetable_data)
    df_pivot = df_timetable.pivot_table(index=['Day', 'TimeSlot'], columns='Room', values='Course', aggfunc='first').fillna('')
    print("Timetable Grid:")
    print(df_pivot)
    try:
        with pd.ExcelWriter('timetable.xlsx', engine='openpyxl') as writer:
            df_pivot.to_excel(writer, sheet_name='Timetable')
        print("Timetable saved to timetable.xlsx")
    except Exception as e:
        print(f"Warning: Failed to save to Excel: {e}. Please install openpyxl or check permissions.")

else:
    print("No optimal solution found. Consider relaxing constraints or checking data consistency.")