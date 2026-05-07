import pandas as pd
import os

df_path = r"D:\My projects\Intelligent Systems\Auto timeTable generator with CSP\Automatic-timeTable-generator-with-CSP-\CollegeDataset.xlsx"

def load_data(file_path, half='first'): #gets the data from the excel, cleans  it and process it as dictionaries.
    
    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        return None
    
    if not file_path.endswith('.xlsx'):
        print("Error: Invalid file type - must be .xlsx")
        return None
    
    if half not in ['first', 'second']:
        print("Error: Invalid half - must be 'first' or 'second'")
        return None

    data = {}
    try:
        data['courses'] = pd.read_excel(file_path, sheet_name='Courses').to_dict('records')
        data['instructors'] = pd.read_excel(file_path, sheet_name='Instructors').to_dict('records')
        data['rooms'] = pd.read_excel(file_path, sheet_name='Rooms').to_dict('records')
        data['timeslots'] = pd.read_excel(file_path, sheet_name='TimeSlots').to_dict('records')
        data['sections'] = pd.read_excel(file_path, sheet_name='Sections').to_dict('records')
        
        # Check for empty data
        for key in data:
            if not data[key]:
                print(f"Warning: Empty data in {key}")
        
        # Clean and process data
        for course in data['courses']:
            course['type'] = course.get('type', '')  # Ensure string
            try:
                course['RequiredSemester'] = int(course.get('RequiredSemester', 0))
                course['RequiredYearLevel'] = int(course.get('RequiredYearLevel', 0))
            except ValueError:
                print(f"Warning: Invalid RequiredSemester/RequiredYearLevel in course {course.get('course_id', 'Unknown')} - defaulting to 0")
                course['RequiredSemester'] = 0
                course['RequiredYearLevel'] = 0

        for instr in data['instructors']:
            quals = instr.get('qualifications', '')
            instr['qualified_courses'] = [q.strip() for q in quals.split(',')] if quals else []

        for room in data['rooms']:
            try:
                room['Capacity'] = int(room.get('Capacity', 0))
            except ValueError:
                print(f"Warning: Invalid Capacity in room {room.get('RoomID', 'Unknown')} - defaulting to 0")
                room['Capacity'] = 0

        for ts in data['timeslots']:
            ts['StartTime'] = ts.get('StartTime', 0)
            ts['EndTime'] = ts.get('EndTime', 0)

        for section in data['sections']:
            try:
                section['group_number'] = int(section.get('group_number', 0))
                section['year'] = int(section.get('year', 0))
                section['student_count'] = int(section.get('student_count', 0))
            except ValueError:
                print(f"Warning: Invalid data in section {section.get('section_id', 'Unknown')} - defaulting to 0")
                section['group_number'] = 0
                section['year'] = 0
                section['student_count'] = 0

        # Pre-group courses by year for performance
        courses_by_year = {}
        for course in data['courses']:
            year = course['RequiredYearLevel']
            if year not in courses_by_year:
                courses_by_year[year] = []
            courses_by_year[year].append(course)

        # Generate variables
        sessions = []
        session_ids = set()  # For duplicate check
        for section in data['sections']:
            year = section['year']
            if year in courses_by_year:
                for course in courses_by_year[year]:
                    if (half == 'first' and course['RequiredSemester'] % 2 == 1) or (half == 'second' and course['RequiredSemester'] % 2 == 0):
                        types = [t.strip() for t in course['type'].split(',') if t.strip()]
                        if not types:
                            print(f"Warning: No types for course {course['course_id']}")
                        for session_type in types:
                            session_id = f"{course['course_id']}_{section['section_id']}_{session_type.lower()}"
                            if session_id in session_ids:
                                print(f"Warning: Duplicate session_id {session_id}")
                            session_ids.add(session_id)
                            sessions.append({
                                'session_id': session_id,
                                'course_id': course['course_id'],
                                'section_id': section['section_id'],
                                'type': session_type,
                                'student_count': section['student_count'],
                                'required_semester': course.get('RequiredSemester'),
                                'required_year': year
                            })

        data['sessions'] = sessions
        return data
    except ValueError as e:
        print(f"Error loading sheet: {e}")
        return None
    except Exception as e:
        print(f"Error loading data: {e}")
        return None

if __name__ == "__main__":
    data = load_data(df_path)
    if data:
        print(f"Loaded {len(data['sessions'])} sessions")
        print("Example session:", data['sessions'][0] if data['sessions'] else "None")