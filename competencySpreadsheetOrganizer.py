# Before running this code:
# Move csv file into file path containing this python file
# Using a spreadsheet application (i.e. excel):
# REMOVE ALL LINE BREAKS IN EXCEL FILE (CTRL + F and replace character ALT + 0010)
# REMOVE ALL QUOTATION MARKS IN CSV FILE
# REPLACE ALL CHARACTERS '.0.' with '.00'

# ---------------------------------------------------------------------------------------------------------------------
# This python file takes in messy competency data and produces a cleaner spreadsheet table.
# Each row of the new spreadsheet corresponds to a list of competency scores for a given employee. Each column
# Corresponds to employee scores in a given competency category. For categories that do not apply to a certain employee,
# their score is listed as 'n/a'. Note, the scores are from the manager reviews and NOT the self evaluations
# ---------------------------------------------------------------------------------------------------------------------

import csv

# define column labels
employeeColumn = 0
reviewerColumn = 9

with open('Example5.csv', encoding="utf8") as csvfile:

    # parse the csv file into rawData
    rawData = csv.reader(csvfile, delimiter=',', quotechar='|')

    # filter raw data to include only manager reviews
    managerReviews = []
    # iterate through each row
    for row in rawData:
        # do not include reviews in which the reviewer is the employee themselves
        if not (row[employeeColumn] == row[reviewerColumn]):
            managerReviews.append(row)

# Initialize a dataset to contain the unique competency categories
competencies = set()

# Initialize list that will contain sublists of format [employee, competency n, score n, competency n+1, score n+1, ...
# competency n+2, score n+2, etc...]
employeeScores = []

# Initialize a dictionary of employee names to reference their manager, SST Site, site, reviewer summary score, and
# performance rating
additionalFields = {}

# Will become true once the machine detects a cell containing a competency category
lookingForScore = False

# Iterate over each employee's review
for n in range(len(managerReviews)):

    # append sublist and dictionary with employee name
    employeeScores.append([managerReviews[n][0]])
    additionalFields[managerReviews[n][0]] = {'Manager Name': managerReviews[n][1], 'SST Team Site':
            managerReviews[n][2], 'Site': managerReviews[n][3], 'Performance Rating': managerReviews[n][6],
                'Reviewer Summary Score': managerReviews[n][11]}

    # Iterate across the cells for a given review, left to right
    for m in range(len(managerReviews[n])):

        # If the cell contains the word 'competency' followed by a number, get the number
        if ('Competency ' in managerReviews[n][m]) and (managerReviews[n][m][len('Competency ')] in '1234567890'):

            # Store competency number in the competencies dataset
            competencies.add(float(managerReviews[n][m][len('Competency '):len('Competency ')+4]))

            # Store competency number in the employee score sublist
            employeeScores[n].append(float(managerReviews[n][m][len('Competency '):len('Competency ')+4]))

            # Ready the machine to look for a competency score
            lookingForScore = True

        # If the machine is ready to look for a competency score and the current cell contains a number, append the
        # employee score sublist with the score adjacent to its corresponding competency number
        if lookingForScore and managerReviews[n][m] in '1234567890':
            employeeScores[n].append(float(managerReviews[n][m]))
            lookingForScore = False

# Convert the competencies dataset into a list and sort them in ascending order
competencies = list(competencies)
competencies.sort()

# Initialize a dictionary to contain employee names as keys and competency scores as values.
outDictionary = {}

# loop through each employee
for n in range(len(managerReviews)):

    # Competency scores are stored in a sub dictionary as values corresponding to their respective competency numbers
    outDictionary[managerReviews[n][0]] = {}
    competenciesForNthEmployee = employeeScores[n][1:-1:2]

    # loop through all possible m competencies
    for m in range(len(competencies)):

        # if an employee has a competency score in the mth competency, then map the employee's score (value) to the
        # competency number (key). Otherwise, map 'n/a' (value) to the competency number (key)
        if competencies[m] in competenciesForNthEmployee:
            # the index of matching Nth employee competencies and the test competencies maps to the index of the
            # employee's competency score index through: score = matching index * 2 + 1
            outDictionary[managerReviews[n][0]][competencies[m]] = \
                employeeScores[n][competenciesForNthEmployee.index(competencies[m])*2 + 2]
        else:
            outDictionary[managerReviews[n][0]][competencies[m]] = 'n/a'

# For convenience of outputting the data to a csv file, initialize a list that will contain the information of the
# dictionary
outputList = []

# loop through outDictionary and additionalFields and the dictionaries within
for name in outDictionary.keys():

    # Concatenate the employee name with the additional fields and competency scores
    outputList.append([name] + list(additionalFields[name].values()) + list(outDictionary[name].values()))

# export outputList as a csv file, fix formatting of the first row to include competency scores
outputList[0][0] = 'Employee/Competency'
outputList[0][5:] = competencies[:]

with open('Competency_Scores_Good.csv', 'w',newline='\n',encoding="utf8") as csvfile:
    filewriter = csv.writer(csvfile, delimiter=',',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
    for row in range(len(outputList)):
        filewriter.writerow(outputList[row])