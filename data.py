# Time structure: Sunday-Thursday, 8 periods/day (matches the source sheets)
# ---------------------------------------------------------------------------
DAYS = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday"]

PERIODS = [
    "09:00-09:50",
    "09:50-10:40",
    "10:45-11:35",
    "11:35-12:25",
    "12:30-13:20",
    "13:20-14:10",
    "14:15-15:05",
    "15:05-15:55",
]

# ---------------------------------------------------------------------------
# Rooms, pooled by type from the many hall/room codes seen across the sheets
# ---------------------------------------------------------------------------
ROOMS = []

def _add_rooms(prefix, names, rtype, capacity):
    for n in names:
        ROOMS.append({"id": f"{prefix}{n}", "type": rtype, "capacity": capacity})

# Theaters / big lecture halls (LEC sessions)
_add_rooms("", ["B7 Theater", "B8 Theater", "B9 Theater", "B10 Theater", "Blue Hall",
                "B25 F1.19 Theater"], "theater", 150)

# Medium lecture/seminar halls (also used for some LEC sessions, e.g. B18-Gxx)
_add_rooms("B18-G", ["01", "05", "08", "09", "11", "13", "14", "16", "17", "19", "21"],
            "hall", 45)
_add_rooms("B7-G", ["01", "09"], "hall", 45)

# Tutorial rooms (TUT sessions). Capacity 35 (assumption, not printed in the
# source) so the largest single section (Y3-AID, 34 students) always fits.
_add_rooms("B7-F1-", [str(i) for i in range(1, 25)], "tutorial", 35)
_add_rooms("B10-F1-", ["6", "7", "8", "10", "11", "18"], "tutorial", 35)
_add_rooms("B18-F1-", [str(i) for i in range(1, 21)], "tutorial", 35)

# Labs (LAB sessions). Same capacity assumption as tutorial rooms above.
_add_rooms("B17-G", ["01", "05", "14", "16", "17", "22"], "lab", 35)
_add_rooms("B18-G", ["01L", "05L", "14L", "17L"], "lab", 35)  # some LAB sessions also ran in B18-Gxx rooms
ROOMS += [
    {"id": "LABnet", "type": "lab", "capacity": 35},
    {"id": "LABsec", "type": "lab", "capacity": 35},
    {"id": "Net Lab", "type": "lab", "capacity": 35},
    {"id": "COE PHY LAB", "type": "lab", "capacity": 35},
    {"id": "COE F1.13", "type": "lab", "capacity": 35},
    {"id": "B7 F1.04", "type": "lab", "capacity": 35},
]

ROOM_TYPE_FOR_SESSION = {"LEC": ("theater", "hall"), "TUT": ("tutorial",), "LAB": ("lab",)}

SECTIONS = {
    1: ["Y1-G1", "Y1-G2", "Y1-G3", "Y1-G4"],
    2: ["Y2-G1", "Y2-G2", "Y2-G3", "Y2-G4"],
    3: ["Y3-CNC", "Y3-AID", "Y3-CSC", "Y3-BIF"],
    4: ["Y4-CNC", "Y4-AID", "Y4-CSC", "Y4-BIF"],
}

def all_sections_for_year(year):
    return SECTIONS[year]

SECTION_SIZE = {
    "Y1-G1": 30, "Y1-G2": 30, "Y1-G3": 30, "Y1-G4": 30,
    "Y2-G1": 30, "Y2-G2": 30, "Y2-G3": 30, "Y2-G4": 30,
    "Y3-CNC": 32, "Y3-AID": 34, "Y3-CSC": 28, "Y3-BIF": 18,
    "Y4-CNC": 30, "Y4-AID": 33, "Y4-CSC": 26, "Y4-BIF": 16,
}


def required_capacity(sections):
    """Total attendees for a session covering the given section id(s)."""
    return sum(SECTION_SIZE.get(s, 30) for s in sections)


BAS_TAS = ["Eng. Yasmine Adel", "Eng. Karim Refaat", "Eng. Nourhan Sabry", "Eng. Ziad Mahfouz"]
ECE_TAS = ["Eng. Tarek Fahmy", "Eng. Mona Kamel", "Eng. Youssef Adly", "Eng. Nesma Wagdy"]
LANG_TAS = ["Instr. Hanan Zaki", "Instr. Rasha Adel", "Instr. Sherine Kamal", "Instr. Yasmin Farouk"]

# ---------------------------------------------------------------------------

COURSES = []


def add_course(code, name, year, semester, sessions, sections, instructors):
    COURSES.append({
        "code": code, "name": name, "year": year, "semester": semester,
        "sessions": sessions, "sections": sections, "instructors": instructors,
    })


# ===================== YEAR 1 - FALL =====================
Y1 = SECTIONS[1]
add_course("CSC 111", "Fundamentals of Programming", 1, "Fall", ["LEC", "LAB"], Y1,
           {"LEC": "Dr. Reda Elbasiony",
            "LAB": ["Eng. Nada Essam", "Eng. Mariam Ismael", "Eng. Nada Hamdy", "Eng. Nour Akram"]})
add_course("MTH 111", "Mathematics (1)", 1, "Fall", ["LEC", "TUT"], Y1,
           {"LEC": "Dr. Ayman Arafa", "TUT": BAS_TAS})
add_course("PHY 113", "Physics (1)", 1, "Fall", ["LEC", "TUT", "LAB"], Y1,
           {"LEC": "Dr. Adel Fathy", "TUT": BAS_TAS, "LAB": BAS_TAS})
add_course("ECE 111", "Digital Logic Design", 1, "Fall", ["LEC", "TUT", "LAB"], Y1,
           {"LEC": "Prof. Ahmed Allam / Dr. Sameh Sherif", "TUT": ECE_TAS, "LAB": ECE_TAS})
add_course("LRA 101", "Japanese Culture", 1, "Fall", ["LEC"], Y1,
           {"LEC": "Dr. Sherine Elmotasem"})
add_course("LRA 401", "Japanese Language (1)", 1, "Fall", ["TUT"], Y1,
           {"TUT": LANG_TAS})
add_course("LRA 104/105", "Music & Technology / Theater & Drama (Elective)", 1, "Fall", ["LEC"], Y1,
           {"LEC": "Dr. Heba Sultan"})

# ===================== YEAR 1 - SPRING =====================
add_course("CSC 121", "Data Structures and Algorithms", 1, "Spring", ["LEC", "LAB"], Y1,
           {"LEC": "Dr. Reda", "LAB": ["Eng. Nour Akram", "Eng. Sama Alqasaby", "Eng. Fatma Elsayed", "Eng. Heba Abdelkader"]})
add_course("CSC 122", "Advanced Programming", 1, "Spring", ["LEC", "LAB"], Y1,
           {"LEC": "Dr. Ahmed Anter / Dr. Mostafa Elsayed",
            "LAB": ["Eng. Nouran", "Eng. Nada Hamdy", "Eng. Menna Magdy", "Eng. Nada Ahmed"]})
add_course("MTH 121", "Mathematics (2)", 1, "Spring", ["LEC", "TUT"], Y1,
           {"LEC": "Prof. Yasser Kamal", "TUT": BAS_TAS})
add_course("PHY 123", "Physics (2)", 1, "Spring", ["LEC", "TUT", "LAB"], Y1,
           {"LEC": "Dr. Adel Fathy", "TUT": BAS_TAS, "LAB": BAS_TAS})
add_course("LRA 402", "Japanese Language (2)", 1, "Spring", ["TUT"], Y1, {"TUT": LANG_TAS})
add_course("LRA 405", "Key Skills 1", 1, "Spring", ["LEC"], Y1, {"LEC": "Dr. Maali Fouad"})
add_course("LRA 208", "Safety and Risk Management", 1, "Spring", ["LEC"], Y1, {"LEC": "Dr. Mona Reda"})
add_course("UR Elective 2", "Sociology of Work / Intro Economics / Entrepreneurship / Peace Studies",
           1, "Spring", ["LEC"], Y1, {"LEC": "Prof. Said Sadik / Dr. Hanan Amin / Dr. Mohamed El-khateeb / Dr. Mamdouh Mansour"})

# ===================== YEAR 2 - FALL =====================
Y2 = SECTIONS[2]
add_course("CSC 211", "Software Engineering", 2, "Fall", ["LEC", "LAB"], Y2,
           {"LEC": "Dr. Ahmed Arafa", "LAB": ["Eng. Nada Ahmed", "Eng. Menna Magdy"]})
add_course("MTH 212", "Probability and Statistics", 2, "Fall", ["LEC", "TUT"], Y2,
           {"LEC": "Prof. Ahmed Zakaria", "TUT": BAS_TAS})
add_course("ACM 215", "Ordinary Differential Equations", 2, "Fall", ["LEC", "TUT"], Y2,
           {"LEC": "Dr. Ayman Arafa", "TUT": BAS_TAS})
add_course("CSE 214", "Computer Organization", 2, "Fall", ["LEC", "TUT", "LAB"], Y2,
           {"LEC": "Prof. Mostafa Soliman", "TUT": ["Eng. Omnya Ramadan", "Eng. Heba Abdelkader"],
            "LAB": ["Eng. Omnya Ramadan", "Eng. Heba Abdelkader"]})
add_course("CNC 111", "Networks and Web Programming", 2, "Fall", ["LEC", "LAB"], Y2,
           {"LEC": "Dr. Ahmed Anter", "LAB": ["Eng. Heba", "Eng. Menna Hamdy", "Eng. Omnia Shehata"]})
add_course("LRA 403", "Japanese Language (3)", 2, "Fall", ["TUT"], Y2, {"TUT": LANG_TAS})
add_course("LRA 306", "Natural Resources and Sustainability", 2, "Fall", ["LEC"], Y2,
           {"LEC": "Prof. Laila Badr Amin"})

# ===================== YEAR 2 - SPRING =====================
add_course("CSC 221", "Operating Systems", 2, "Spring", ["LEC", "LAB"], Y2,
           {"LEC": "Dr. Arafa", "LAB": ["Eng. Nourhan Waleed", "Eng. Salma Alashry", "Eng. Mariem Nagy"]})
add_course("CSC 114 / CNC 223", "Algorithms Analysis & Design / Computer Architecture (Elective)",
           2, "Spring", ["LEC", "LAB"], Y2,
           {"LEC": "Dr. Ahmed Bayumi / Prof. Mostafa Soliman", "LAB": "Eng. Sama Alqasaby"})
add_course("CNC 222", "Introduction to Embedded Systems", 2, "Spring", ["LEC", "LAB"], Y2,
           {"LEC": "Prof. Mostafa Soliman", "LAB": "Eng. Omnya Ramadan"})
add_course("ACM 323", "Applied Numerical Methods", 2, "Spring", ["LEC", "TUT"], Y2,
           {"LEC": "Dr. Ehab Soliman", "TUT": BAS_TAS})
add_course("ACM 422", "Operations Research", 2, "Spring", ["LEC", "TUT"], Y2,
           {"LEC": "Dr. Issa", "TUT": "Eng. Nada Essam"})
add_course("CSE 312", "Discrete Mathematics", 2, "Spring", ["LEC", "TUT"], Y2,
           {"LEC": "Prof. Marghany Hassan", "TUT": ["Eng. Omnia Shehata", "Eng. Zeina Ahmed"]})
add_course("LRA 404", "Japanese Language (4)", 2, "Spring", ["TUT"], Y2, {"TUT": LANG_TAS})
add_course("UR Elective 4", "English Language / Fundamentals of Communication", 2, "Spring", ["LEC"], Y2,
           {"LEC": "Dr. Amal Gomaa"})

# ===================== YEAR 3 - FALL (tracks) =====================
add_course("CNC 311", "Computer Networks", 3, "Fall", ["LEC", "LAB"], ["Y3-CNC"],
           {"LEC": "Prof. Samir Ahmed", "LAB": ["Eng. Nada Hamdy", "Eng. Fatma Elsayed"]})
add_course("CNC 312", "Foundations of Information Systems", 3, "Fall", ["LEC", "TUT", "LAB"], ["Y3-CNC"],
           {"LEC": "Dr. Reda", "TUT": "Eng. Menna Hamdi", "LAB": "Eng. Menna Hamdi"})
add_course("CNC 314", "Database Systems", 3, "Fall", ["LEC", "LAB"], ["Y3-CNC"],
           {"LEC": "Dr. Mohamed Issa", "LAB": ["Eng. Salma Alashry", "Eng. Nourhan Waleed"]})
add_course("AID 311", "Mathematics of Data Science", 3, "Fall", ["LEC", "TUT", "LAB"], ["Y3-AID"],
           {"LEC": "Dr. Ahmed Anter", "TUT": "Eng. Salma Waleed", "LAB": "Eng. Salma Waleed"})
add_course("AID 312", "Intelligent Systems", 3, "Fall", ["LEC", "LAB"], ["Y3-AID"],
           {"LEC": "Dr. Ahmed Bayumi", "LAB": ["Eng. Salma Waleed", "Eng. Nourhan Waleed"]})
add_course("CSC 317", "Computer Graphics and Visualization", 3, "Fall", ["LEC", "LAB"], ["Y3-CSC"],
           {"LEC": "Dr. Hataba", "LAB": ["Eng. Nada Ahmed", "Eng. Menna Magdy"]})
add_course("BIF 311", "Human Biology", 3, "Fall", ["LEC", "TUT", "LAB"], ["Y3-BIF"],
           {"LEC": "Prof. Eman Allam", "TUT": "Eng. Rania Hossam", "LAB": "Eng. Rania Hossam"})

# ===================== YEAR 3 - SPRING (tracks) =====================
add_course("CNC 321", "Cryptography and Cryptanalysis", 3, "Spring", ["LEC", "TUT", "LAB"], ["Y3-CNC"],
           {"LEC": "Dr. Hataba", "TUT": "Eng. Fatma Elsayed", "LAB": "Eng. Fatma Elsayed"})
add_course("CNC 323", "Computer and Network Security", 3, "Spring", ["LEC", "TUT", "LAB"], ["Y3-CNC"],
           {"LEC": "Dr. Hataba", "TUT": "Eng. Samaa", "LAB": ["Eng. Aya Tarek", "Eng. Samaa"]})
add_course("CNC 325", "Wireless and Mobile Networks", 3, "Spring", ["LEC", "TUT", "LAB"], ["Y3-CNC"],
           {"LEC": "Dr. Ahmed Abdelmalek", "TUT": "Eng. Ola Refaat", "LAB": "Eng. Ola Refaat"})
add_course("CNC 327", "Internet of Things", 3, "Spring", ["LEC", "TUT", "LAB"], ["Y3-CNC"],
           {"LEC": "Prof. Samir Elsagheer", "TUT": "Eng. Aya Tarek", "LAB": "Eng. Aya Tarek"})
add_course("CNC 320", "IS Project Management (Elective 1)", 3, "Spring", ["LEC", "TUT", "LAB"], ["Y3-CNC"],
           {"LEC": "Adjunct Prof. Mahmoud Zaher", "TUT": "Eng. Nada Hamdy", "LAB": "Eng. Nada Hamdy"})
add_course("AID 322", "Data Mining", 3, "Spring", ["LEC", "TUT", "LAB"], ["Y3-AID"],
           {"LEC": "Adjunct Prof. Salma Youssef", "TUT": "Eng. Salma Alashry", "LAB": "Eng. Salma Alashry"})
add_course("AID 323", "Parallel & Distributed Computing", 3, "Spring", ["LEC", "TUT", "LAB"], ["Y3-AID"],
           {"LEC": "Dr. Mostafa Elsayed", "TUT": "Eng. Peter Adel", "LAB": "Eng. Peter Adel"})
add_course("AID 324", "Image Processing", 3, "Spring", ["LEC", "TUT", "LAB"], ["Y3-AID"],
           {"LEC": "Dr. Ahmed Anter", "TUT": "Eng. Menna Magdy", "LAB": "Eng. Menna Magdy"})
add_course("CSC 321", "Software Design", 3, "Spring", ["LEC", "TUT", "LAB"], ["Y3-CSC"],
           {"LEC": "Dr. Arafa", "TUT": "Eng. Omnia Shehata", "LAB": "Eng. Salma Alashry"})
add_course("CSC 322", "Requirements Analysis and Specification", 3, "Spring", ["LEC", "TUT", "LAB"], ["Y3-CSC"],
           {"LEC": "Prof. Marghany", "TUT": "Eng. Sama Alqasaby", "LAB": "Eng. Sama Alqasaby"})
add_course("CSC 323", "Software Process", 3, "Spring", ["LEC", "TUT", "LAB"], ["Y3-CSC"],
           {"LEC": "Prof. Mohamed Akhames", "TUT": "Eng. Farida Hossam", "LAB": "Eng. Farida Hossam"})
add_course("CSC 324", "Human Computer Interaction", 3, "Spring", ["LEC", "TUT", "LAB"], ["Y3-CSC"],
           {"LEC": "Prof. Mohamed Akhames", "TUT": "Eng. Omnia Shehata", "LAB": "Eng. Omnia Shehata"})
add_course("BIF 321", "Bioinformatics", 3, "Spring", ["LEC", "TUT", "LAB"], ["Y3-BIF"],
           {"LEC": "Dr. Mohamed Issa", "TUT": "Eng. Nouran Moussa", "LAB": "Eng. Nouran Moussa"})
add_course("BIF 322", "Computational Biology", 3, "Spring", ["LEC", "TUT", "LAB"], ["Y3-BIF"],
           {"LEC": "Dr. Sameh Sherif", "TUT": "Eng. Ramy Fouad", "LAB": "Eng. Ramy Fouad"})
add_course("BIF 323", "Biocomputing", 3, "Spring", ["LEC", "TUT", "LAB"], ["Y3-BIF"],
           {"LEC": "Dr. Mohamed Issa", "TUT": "Eng. Nour Akram", "LAB": "Eng. Nour Akram"})
add_course("BIF 325", "Molecular & Cell Biology (Elective 1)", 3, "Spring", ["LEC", "TUT", "LAB"], ["Y3-BIF"],
           {"LEC": "Prof. M. Ghazy", "TUT": "Eng. Dina Elshamy", "LAB": "Eng. Dina Elshamy"})

# ===================== YEAR 4 - FALL (tracks) =====================
add_course("CNC 411", "Fundamentals of Cybersecurity", 4, "Fall", ["LEC", "TUT", "LAB"], ["Y4-CNC"],
           {"LEC": "Dr. Ahmed Arafa", "TUT": "Eng. Sama Osama", "LAB": "Eng. Mariam Ismael"})
add_course("CNC 413", "Digital Forensics", 4, "Fall", ["LEC", "TUT", "LAB"], ["Y4-CNC"],
           {"LEC": "Prof. Samir Ahmed", "TUT": "Eng. Aya Tarek", "LAB": "Eng. Aya Tarek"})
add_course("CNC 415", "Network Design and Management", 4, "Fall", ["LEC", "LAB"], ["Y4-CNC"],
           {"LEC": "Dr. Mustafa AlSayed", "LAB": "Eng. Ibrahim Sameh"})
add_course("CNC 418", "Software Security", 4, "Fall", ["LEC", "TUT", "LAB"], ["Y4-CNC"],
           {"LEC": "Dr. Hataba", "TUT": "Eng. Aya Tarek", "LAB": "Eng. Aya Tarek"})
add_course("CNC 419", "IT Security and Risk Management", 4, "Fall", ["LEC", "TUT", "LAB"], ["Y4-CNC"],
           {"LEC": "Dr. Hataba", "TUT": "Eng. Sama Osama", "LAB": "Eng. Sama Osama"})
add_course("CNC 324", "IT Infrastructure", 4, "Fall", ["LEC", "TUT", "LAB"], ["Y4-CNC"],
           {"LEC": "Dr. Mohamed Akhames", "TUT": "Eng. Sama Osama", "LAB": "Eng. Sama Osama"})
add_course("AID 413", "Data Security", 4, "Fall", ["LEC", "TUT", "LAB"], ["Y4-AID"],
           {"LEC": "Dr. Ahmed Arafa", "TUT": "Eng. Mariem Nagy", "LAB": "Eng. Mariem Nagy"})
add_course("AID 417", "Advanced Data Mining", 4, "Fall", ["LEC", "TUT"], ["Y4-AID"],
           {"LEC": "Dr. Mohamed Issa", "TUT": "Eng. Fatma Elsayed"})
add_course("AID 411", "BIG Data Analytics & Visualization", 4, "Fall", ["LEC", "TUT", "LAB"], ["Y4-AID"],
           {"LEC": "Prof. Marghany Hassan", "TUT": "Eng. Nada Essam", "LAB": "Eng. Nada Essam"})
add_course("AID 427", "New Trends in Data Science", 4, "Fall", ["LEC", "TUT", "LAB"], ["Y4-AID"],
           {"LEC": "Dr. Ahmed Arafa", "TUT": "Eng. Zeina Ahmed", "LAB": "Eng. Zeina Shreif"})
add_course("AID 428", "New Trends in AI", 4, "Fall", ["LEC", "LAB"], ["Y4-AID"],
           {"LEC": "Dr. Ahmed Bayumi", "LAB": ["Eng. Zeina Ahmed", "Eng. Omnia Shehata"]})
add_course("AID 321", "Machine Learning", 4, "Fall", ["LEC", "LAB"], ["Y4-AID"],
           {"LEC": "Prof. Marghany Hassan", "LAB": "Eng. Salma Alashry"})
add_course("CSC 410", "Software Quality", 4, "Fall", ["LEC", "TUT", "LAB"], ["Y4-CSC"],
           {"LEC": "Dr. Mohamed Khames", "TUT": "Eng. Zeina Shreif", "LAB": "Eng. Zeina Shreif"})
add_course("CSC 411", "Software Verification and Validation (V&V)", 4, "Fall", ["LEC", "TUT", "LAB"], ["Y4-CSC"],
           {"LEC": "Dr. Mohamed Akhames", "TUT": "Eng. Marwa Adel", "LAB": "Eng. Marwa Adel"})
add_course("CSC 412", "Software Security", 4, "Fall", ["LEC", "TUT"], ["Y4-CSC"],
           {"LEC": "Dr. Mustafa AlSayed", "TUT": "Eng. Aya Tarek"})
add_course("CSC 414", "Game Design & Development", 4, "Fall", ["LEC", "TUT", "LAB"], ["Y4-CSC"],
           {"LEC": "Dr. Mustafa AlSayed", "TUT": "Eng. Nouran Moussa", "LAB": "Eng. Nouran Moussa"})
add_course("CSC 415", "New Trends in Computer Science", 4, "Fall", ["LEC", "TUT", "LAB"], ["Y4-CSC"],
           {"LEC": "Dr. Ahmed Bayumi", "TUT": "Eng. Nouran Moussa", "LAB": "Eng. Nouran Moussa"})
add_course("CSC 426", "Distributed Systems", 4, "Fall", ["LEC", "TUT", "LAB"], ["Y4-CSC"],
           {"LEC": "Dr. Mustafa AlSayed", "TUT": "Eng. Zeina Shreif", "LAB": "Eng. Zeina Shreif"})
add_course("BIF 411", "Structural Bioinformatics", 4, "Fall", ["LEC", "TUT", "LAB"], ["Y4-BIF"],
           {"LEC": "Dr. Sameh Sherif", "TUT": "Eng. Yara Naguib", "LAB": "Eng. Yara Naguib"})
add_course("BIF 412", "Management and Design of Health Care Systems", 4, "Fall", ["LEC", "TUT", "LAB"], ["Y4-BIF"],
           {"LEC": "Dr. Sameh Sherif", "TUT": "Eng. Nour Akram", "LAB": "Eng. Nour Akram"})
add_course("BIF 413", "Algorithms in Bioinformatics", 4, "Fall", ["LEC", "TUT", "LAB"], ["Y4-BIF"],
           {"LEC": "Prof. Marghany", "TUT": "Eng. Nouran Moussa", "LAB": "Eng. Nouran Moussa"})
add_course("BIF 424", "IT Infrastructure", 4, "Fall", ["LEC", "TUT", "LAB"], ["Y4-BIF"],
           {"LEC": "Dr. Mohamed Akhames", "TUT": "Eng. Nouran Moussa", "LAB": "Eng. Mina Fahim"})
add_course("BIF 425", "New Trends in Bioinformatics", 4, "Fall", ["LEC", "TUT", "LAB"], ["Y4-BIF"],
           {"LEC": "Dr. Mohamed Issa", "TUT": "Eng. Nouran Moussa", "LAB": "Eng. Nouran Moussa"})

# ===================== YEAR 4 - SPRING (tracks) =====================
add_course("CNC 421", "Ethical Hacking and Penetration Testing", 4, "Spring", ["LEC", "TUT", "LAB"], ["Y4-CNC"],
           {"LEC": "Dr. Arafa", "TUT": "Eng. Rana Adly", "LAB": "Eng. Aya Tarek"})
add_course("CNC 422", "Cloud Computing and Virtualization", 4, "Spring", ["LEC", "TUT", "LAB"], ["Y4-CNC"],
           {"LEC": "Dr. Mostafa Elsayed", "TUT": "Eng. Samaa", "LAB": "Eng. Samaa"})
add_course("AID 421", "Computer Vision", 4, "Spring", ["LEC", "TUT", "LAB"], ["Y4-AID"],
           {"LEC": "Adjunct Prof. Khaled Nasr", "TUT": "Eng. Mariem Nagy", "LAB": "Eng. Mariem Nagy"})
add_course("AID 422", "Natural Language Processing", 4, "Spring", ["LEC", "TUT", "LAB"], ["Y4-AID"],
           {"LEC": "Dr. Ahmed Bayumi", "TUT": "Eng. Zeina Ahmed", "LAB": "Eng. Zeina Ahmed"})
add_course("AID 412", "Neural Networks", 4, "Spring", ["LEC", "TUT", "LAB"], ["Y4-AID"],
           {"LEC": "Dr. Ahmed Bayumi", "TUT": "Eng. Heba Abdelkader", "LAB": "Eng. Heba Abdelkader"})
add_course("CSC 422", "Fundamentals of Cloud Computing", 4, "Spring", ["LEC", "TUT", "LAB"], ["Y4-CSC"],
           {"LEC": "Dr. Mostafa Elsayed", "TUT": "Eng. Nada Ahmed", "LAB": "Eng. Nada Ahmed"})
add_course("CSC 425", "Soft Computing (Elective 1)", 4, "Spring", ["LEC", "TUT", "LAB"], ["Y4-CSC"],
           {"LEC": "Dr. Ahmed Anter", "TUT": "Eng. Omnya Ramadan", "LAB": "Eng. Omnya Ramadan"})
add_course("CSC 427", "Design Patterns (Elective 4)", 4, "Spring", ["TUT", "LAB"], ["Y4-CSC"],
           {"TUT": "Eng. Sama Alqasaby", "LAB": "Eng. Sama Alqasaby"})
add_course("AID 426", "Robotics (Elective 2)", 4, "Spring", ["LEC", "TUT", "LAB"], ["Y4-CSC", "Y4-AID"],
           {"LEC": "Dr. Reda", "TUT": "Eng. Menna Hamdi", "LAB": "Eng. Menna Hamdi"})
add_course("AID 325", "BlockChain & Distributed Ledgers (Elective 2)", 4, "Spring", ["LEC", "TUT", "LAB"],
           ["Y4-CNC"], {"LEC": "Dr. Hataba", "TUT": "Eng. Salma Waleed", "LAB": "Eng. Salma Waleed"})
add_course("BIF 421", "Telemedicine", 4, "Spring", ["LEC", "TUT", "LAB"], ["Y4-BIF"],
           {"LEC": "Dr. Sameh Sherif", "TUT": "Eng. Nouran Moussa", "LAB": "Eng. Nouran Moussa"})
add_course("BIF 328", "Genetic Algorithms (Elective 2)", 4, "Spring", ["LEC", "TUT"], ["Y4-BIF"],
           {"LEC": "Dr. Mohamed Issa", "TUT": "Eng. Fatma Elsayed"})


def courses_for(semester):
    return [c for c in COURSES if c["semester"] == semester]
