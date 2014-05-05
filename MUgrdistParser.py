import csv, sys, re, sys
from os import listdir
from os.path import isfile, join
from SQLManager import SQLManager
import time

'''
@Author: Brandon Harmon (bharm86@gmail.com)
@Sponsor: T.M. Rajkumar (rajkumtm@miamioh.edu)

Parser for Miami University's grade distribution CSV file format
into a SQLite database. Intended for use in conjuntion with the
grade distribution web application
'''

sql = SQLManager()
isdept = re.compile('^[A-Z]{3}\s[A-Z]')
isclass = re.compile('^[A-Z]{3}\s[0-9]')

#Class used as enum for what actions to take at each line
class Responses:
	Ignore, Class, Department = range(3)

#Attempts to add department to the database, if department
#already exists sql will disregard the request
def handleDepartment(row):
	sql.adddept(row[0:3],row[3:].strip())

#Uses the section name in conjunction with Miami's naming
#conventions to determine the location of the class
#M = Middletown
#O = Oxford
#H = Hamilton
#V = Voice of America
#L = Luxemburg
#Defaults to Oxford if no matching pattern found.
def determineCampus(section):
	if len(section) == 1: return 'O'
	if section[0] == 'M': return 'M'
	if section[0] == 'H': return 'H'
	if section[0] == 'L': return 'L'
	if section[0] == 'V': return 'V'
	return 'O'

#Parses the information out of the string, and adds
#class information to the database.
#
#Returns the id of the class in the database
def handleclass(row,year,semester):
	s = row[0].strip()
	dept = s[0:s.find(' ')].strip()
	s  = s[s.find(' '):].strip()
	num = s[0:s.find(' ')].strip()
	s = s[s.find(' '):].strip()
	sec = s[0:s.find('  ')].strip()
	s = s[s.find('  '):].strip()
	inst = s[0:s.find('  ')].strip()
	title = s[s.find('  '):].strip()
	sql.addinstructor(inst)
	return sql.addclass(dept,s[1],num,sec,year,semester,inst,title,determineCampus(sec))

#Given a row and a class ID it will parse out the grade
#information and push that information into the database
def handlegrades(row, cid):
	ap = int(row[1])
	a  = int(row[2])
	am = int(row[3])
	bp = int(row[4])
	b  = int(row[5])
	bm = int(row[6])
	cp = int(row[7])
	c  = int(row[8])
	cm = int(row[9])
	dp = int(row[10])
	d  = int(row[11])
	dm = int(row[12])
	f  = int(row[13])
	w  = int(row[14])
	wp = int(row[15])
	wf = int(row[16])
	i  = int(row[17])
	x  = int(row[18])
	y  = int(row[19])
	p  = int(row[20])
	s  = int(row[21])

	finished = ap+a+am+bp+b+bm+cp+c+cm+dp+d+dm+f
	withdrawl = w+wp+wf
	other = i+x+y+p+s
	total = finished+withdrawl+other

	gpa = row[22]

	sql.addgrades(cid,ap,a,am,bp,b,bm,cp,c,cm,dp,d,
		dm,f,w,wp,wf,i,x,y,p,s,finished,withdrawl,other,total,gpa)

#Checks if line is a department or a class line, if not ignore that line
def analyze(row):
	if isdept.match(row) != None: 
		return Responses.Department
	if isclass.match(row) != None: 
		return Responses.Class
	return Responses.Ignore

#Main loop that iterates through the rows and calls the appropreate methods
def processfile(filename, year, semester):
	count = 0;
	with open(filename, 'rb') as csvfile:
		infile = csv.reader(csvfile,delimiter=',',quotechar='"')
		lastcid = -1
		skipnext = False
		#Control flow that iterates through each line of the csv.
		for row in infile:
			count+=1
			if skipnext:
				skipnext = False
				continue

			if lastcid != -1:
				handlegrades(row, lastcid)
				lastcid = -1
				continue

			t = analyze(row[0])
			if t is Responses.Department:
				handleDepartment(row[0])
				continue

			if t is Responses.Class:
				skipnext = True
				lastcid = handleclass(row,year,semester)
				continue
	return count

def __main__(argv):
	directory = sys.argv[1]
	files = [f for f in listdir(directory) if isfile(join(directory,f))]
	count = 0
	for f in files:
		print f
		name = f[:f.index(' ')]
		year = name[0:4]
		semester = name[-2:]
		count += processfile(directory+'/'+f,year,semester)
		sql.commit()

	print "Lines Processed: " + count

if __name__ == '__main__':
	__main__(sys.argv)
