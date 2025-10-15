import pandas as pd


Instructors = pd.read_excel('D:\My projects\Intelligent Systems\Auto timeTable generator with CSP\Automatic-timeTable-generator-with-CSP-\CollegeDataset.xlsx', sheet_name='Instructors')

Courses = pd.read_excel('D:\My projects\Intelligent Systems\Auto timeTable generator with CSP\Automatic-timeTable-generator-with-CSP-\CollegeDataset.xlsx'
, sheet_name='Courses')

print(Instructors.head())
print(Courses.head())