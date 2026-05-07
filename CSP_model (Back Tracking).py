from DataLoader import load_data
import constraint
import time
import pandas as pd

df_path = r"D:\My projects\Intelligent Systems\Auto timeTable generator with CSP\Automatic-timeTable-generator-with-CSP-\CollegeDataset.xlsx"

def get_room_types(session_type): #mapping variables for ensuring types!
    
    if session_type in ['Lecture', 'Tutorial', 'Project']:
        return ['Hall', 'Classroom', 'Theater']
    elif session_type == 'Lab':
        return ['Computer Lab', 'FoE Drawing Lab', 'Drawing Studio']
    return ['Classroom']  # as default


def get_domain(session, data): #generate the domains for the variables
    
    domain = []
    allowed_room_types = get_room_types(session['type'])
    for ts in data['timeslots']:
        for room in data['rooms']:
            if room['Type'] in allowed_room_types and room['Capacity'] >= session['student_count']:
                for instr in data['instructors']:
                    if session['course_id'] in [qc.strip() for qc in instr['qualified_courses']]:
                        domain.append((ts['Day_id'], room['RoomID'], instr['instructor_id']))
    return domain

                         ########################### Hard constraint functions ###########################
def no_prof_overlap(*assignments):
    
    instr_times = {}
    for value in assignments:
        time, room, instr = value
        if instr not in instr_times:
            instr_times[instr] = set()
        if time in instr_times[instr]:
            return False
        instr_times[instr].add(time)
    return True

def no_room_overlap(*assignments):
    
    room_times = {}
    for value in assignments:
        time, room, instr = value
        if room not in room_times:
            room_times[room] = set()
        if time in room_times[room]:
            return False
        room_times[room].add(time)
    return True

#-----------------------------------------------------------------------------------------------------------------
data = load_data(df_path)
if not data:
    print("Data loading failed. Check file path and sheets.")
else:
    sessions = data['sessions']

    # testing
    sessions = [s for s in sessions if s['required_year'] == 1 and s['section_id'] in ['1_1', '1_2']]
    print(f"Using {len(sessions)} sessions for testing")

    problem = constraint.Problem()

    # Define variables and domains
    domain_dict = {}  #to store domains
    for session in sessions:
        domain = get_domain(session, data)
        if not domain:
            print(f"Warning: Empty domain for {session['session_id']} - no valid assignments!")
        domain_dict[session['session_id']] = domain
        problem.addVariable(session['session_id'], domain)

    # Adding hard constraints
    variables = [s['session_id'] for s in sessions]
    problem.addConstraint(no_prof_overlap, variables)
    problem.addConstraint(no_room_overlap, variables)

    print("CSP model set up complete!")
    print(f"Variables: {len(variables)}")
    if variables:
        print(f"Example domain size: {len(domain_dict[variables[0]])}")


# using backtracking
start_time = time.time()
solution = problem.getSolution()  # Get first solution (or None if none)
solve_time = time.time() - start_time
print(f"Solved in {solve_time:.2f} seconds")

if solution:
    
    def calculate_score(solution, data): #scoring for penalization
        score = 0
        
        for sess_id, (time_id, room, instr) in solution.items():
            time = next(ts for ts in data['timeslots'] if ts['Day_id'] == time_id)
            day_slots = [ts['Day_id'] for ts in data['timeslots'] if ts['Day'] == time['Day']]
            if time_id == min(day_slots) or time_id == max(day_slots):
                score += 1
        # Even distribution
        day_counts = {day: 0 for day in set(ts['Day'] for ts in data['timeslots'])}
        for (time_id, _, _) in solution.values():
            day = next(ts['Day'] for ts in data['timeslots'] if ts['Day_id'] == time_id)
            day_counts[day] += 1
        variance = sum((count - len(solution)/len(day_counts))**2 for count in day_counts.values())
        score += variance
        #here for  more soft constraints
        return score

    score = calculate_score(solution, data)
    print(f"Solution found with score: {score}")

    # Output the grid
    timetable_data = []
    for sess_id, (time_id, room_id, instr_id) in solution.items():
        sess = next(s for s in sessions if s['session_id'] == sess_id)
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
    
    df_pivot = df_timetable.pivot_table(index='Room', columns=['Day', 'Start'], values='Details', aggfunc='first')
    print("Timetable Grid:")
    print(df_pivot.fillna(''))

    df_pivot.to_excel('timetable.xlsx') # Export to Excel
else:
    print("No solution found. Relax constraints or check data.")

