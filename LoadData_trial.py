import pandas as pd


Instructors = pd.read_excel('D:\My projects\Intelligent Systems\Auto timeTable generator with CSP\Automatic-timeTable-generator-with-CSP-\CollegeDataset.xlsx', sheet_name='Instructors')

Courses = pd.read_excel('D:\My projects\Intelligent Systems\Auto timeTable generator with CSP\Automatic-timeTable-generator-with-CSP-\CollegeDataset.xlsx'
, sheet_name='Courses')


import constraint as ct

problem = ct.Problem()

times = ['Mon 9-10', 'Mon 10-11', 'Tue 9-10']

problem.addVariables(['class1', 'class2'], times)

problem.addConstraint(ct.AllDifferentConstraint()) #it returns true if satisfied

solutions = problem.getSolutions()  #returns a list of dictionaries

print("Solutions: ")

for s in solutions:
    print(s)
