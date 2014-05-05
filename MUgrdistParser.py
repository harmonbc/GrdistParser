import csv, sys, re, sys
from os import listdir
from os.path import isfile, join
from SQLManager import SQLManager
import time

sql = SQLManager()
isdept = re.compile('^[A-Z]{3}\s[A-Z]')
isclass = re.compile('^[A-Z]{3}\s[0-9]')

class Responses:
	Ignore, Class, Department = range(3)
	
def handleDepartment(row):
	global sql
	sql.adddept(row[0:3],row[3:].strip())

def determineCampus(section):
	if len(section) == 1: return 'O'
	if section[0] == 'M': return 'M'
	if section[0] == 'H': return 'H'
	if section[0] == 'L': return 'L'
	if section[0] == 'V': return 'V'
	return 'O'

def handleclass(row,year,semester):
	global sql
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

def handlegrades(row, cid):
	global sql
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

	sql.addgrades(cid,ap,a,am,bp,b,bm,cp,c,cm,dp,d,dm,f,w,wp,wf,i,x,y,p,s,finished,withdrawl,other,total,gpa)

def analyze(row):
	if isdept.match(row) != None: return Responses.Department
	if isclass.match(row) != None: return Responses.Class
	return Responses.Ignore

def processfile(filename, year, semester):
	with open(filename, 'rb') as csvfile:
		infile = csv.reader(csvfile,delimiter=',',quotechar='"')
		lastcid = -1
		skipnext = False
		for row in infile:
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

			elif t is Responses.Class:
				skipnext = True
				lastcid = handleclass(row,year,semester)
				if lastcid%1000 == 0: print lastcid

def __main__(argv):
	directory = sys.argv[1]
	files = [f for f in listdir(directory) if isfile(join(directory,f))]
	for f in files:
		print f
		name = f[:f.index(' ')]
		year = name[0:4]
		semester = name[-2:]
		processfile(directory+'/'+f,year,semester)
		sql.commit()

if __name__ == '__main__':
	__main__(sys.argv)
