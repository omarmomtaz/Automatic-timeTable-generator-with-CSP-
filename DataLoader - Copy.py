import pandas as pd

df_path = r"D:\My projects\Intelligent Systems\Auto timeTable generator with CSP\Automatic-timeTable-generator-with-CSP-\CollegeDataset.xlsx"

def load_data(file_path): #gets the data from the excel, cleans  it and process it as dictionaries.

    data = {}
    try:
        data['courses'] = pd.read_excel(file_path, sheet_name='Courses').to_dict('records')
        data['instructors'] = pd.read_excel(file_path, sheet_name='Instructors').to_dict('records')
        data['rooms'] = pd.read_excel(file_path, sheet_name='Rooms').to_dict('records')
        data['timeslots'] = pd.read_excel(file_path, sheet_name='TimeSlots').to_dict('records')
        data['sections'] = pd.read_excel(file_path, sheet_name='Sections').to_dict('records')

        # Clean and process data
        for course in data['courses']:
            course['type'] = course.get('type', '')  # Ensure string
            course['RequiredSemester'] = int(course.get('RequiredSemester', 0))
            course['RequiredYearLevel'] = int(course.get('RequiredYearLevel', 0))

        for instr in data['instructors']:
            quals = instr.get('qualifications', '')
            instr['qualified_courses'] = [q.strip() for q in quals.split(',')] if quals else []

        for room in data['rooms']:
            room['Capacity'] = int(room.get('Capacity', 0))

        for ts in data['timeslots']:
            ts['StartTime'] = ts.get('StartTime', 0)
            ts['EndTime'] = ts.get('EndTime', 0)

        for section in data['sections']:
            section['group_number'] = int(section.get('group_number', 0))
            section['year'] = int(section.get('year', 0))
            section['student_count'] = int(section.get('student_count', 0))

        # Generate variables
        sessions = []
        for section in data['sections']:
            year = section['year']
            expected_semester = 2 * year - 1 
            for course in data['courses']:
                if course['RequiredYearLevel'] == year and course['RequiredSemester'] == expected_semester:
                    types = [t.strip() for t in course['type'].split(',') if t.strip()]
                    for session_type in types:
                        session_id = f"{course['course_id']}_{section['section_id']}_{session_type.lower()}"
                        sessions.append({
                            'session_id': session_id,
                            'course_id': course['course_id'],
                            'section_id': section['section_id'],
                            'type': session_type,
                            'student_count': section['student_count'],
                            'required_semester': expected_semester,
                            'required_year': year
                        })

        data['sessions'] = sessions
        return data
    except Exception as e:
        print(f"Error loading data: {e}")
        return None

if __name__ == "__main__":
    data = load_data(df_path)
    if data:
        print(f"Loaded {len(data['sessions'])} sessions")
        print("Example session:", data['sessions'][0] if data['sessions'] else "None")