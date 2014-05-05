import sqlite3 as lite
import re
global con;

instructors = """CREATE TABLE if not exists INSTRUCTORS( 
     iid INTEGER PRIMARY KEY AUTOINCREMENT, 
     name VARCHAR)"""
department = """CREATE TABLE if not exists DEPARTMENTS(
     did INTEGER PRIMARY KEY AUTOINCREMENT,
     name VARCHAR,
     NameShort VARCHAR)"""
worksin = """CREATE TABLE if not exists WORKS_IN(
     iid INTEGER,  
     did INTEGER,
     FOREIGN KEY(iid)
          REFERENCES INSTRUCTORS(iid)
     FOREIGN KEY(did)
          REFERENCES DEPARTMENTS(did)
     PRIMARY KEY(iid,did))"""
classes = """CREATE TABLE if not exists CLASS(
     cid INTEGER PRIMARY KEY AUTOINCREMENT,
     did INTEGER,
     iid INTEGER,
     Honors VARCHAR,
     number INTEGER,
     Semester VARCHAR,
     Section VARCHAR,
     Year INTEGER,
     Title VARCHAR,
     FOREIGN KEY(iid)
          REFERENCES INSTRUCTORS(iid)
     FOREIGN KEY(did)
          REFERENCES DEPARTMENTS(did))"""
grades = """CREATE TABLE if not exists GRADES(
     gid INTEGER PRIMARY KEY AUTOINCREMENT,
     cid INTEGER,
     ap INTEGER, a INTEGER, am INTEGER, 
     bp INTEGER, b INTEGER, bm INTEGER,
     cp INTEGER, c INTEGER, cm INTEGER,
     dp INTEGER, d INTEGER, dm INTEGER,
     f INTEGER, 
     wp INTEGER, w INTEGER, wf INTEGER,
     i INTEGER, x INTEGER, y INTEGER,
     p INTEGER, s INTEGER, 
     finished INTEGER, withdrawl INTEGER, other INTEGER,
     total INTEGER, avggpa DOUBLE,
     FOREIGN KEY(cid)
          REFERENCES CLASS(cid))"""
addclass = """ INSERT INTO CLASS(did,honors, iid, number, semester, section, year, title) VALUES (?,?,?,?,?,?,?,?) """
addinstructor = """ INSERT INTO INSTRUCTORS(name) VALUES (?) """
adddepartment = """ INSERT INTO DEPARTMENTS(name, nameshort) VALUES (?,?) """
addgrades = """ INSERT INTO GRADES(cid,ap,a,am,bp,b,bm,cp,c,cm,dp,d,dm,f,w,wp,wf,i,x,y,p,s,finished,withdrawl,other,total,avggpa) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"""
addworksin = """INSERT INTO WORKS_IN(iid,did) VALUES (?,?) """
checkinst = """ SELECT iid FROM INSTRUCTORS  WHERE Name LIKE ? """
checkdept = """ SELECT did FROM DEPARTMENTS where nameshort LIKE ? """
checkclass = """SELECT cid FROM CLASS WHERE did = ? AND iid = ? AND number = ? AND semester = ? and section LIKE ? and year = ? and title like ? """
checkworksin = """SELECT iid,did FROM WORKS_IN WHERE iid=? AND did=? """
enableregex = ".load /usr/lib/sqlite3/pcre.so"
findbroken = "SELECT * FROM instructors WHERE name REGEXP '^[a-z]'"
checkinstructor = "SELECT * FROM instructors WHERE name LIKE ?"
updateinstructors = "UPDATE class SET iid=? WHERE iid=?"
updateworksin = "UPDATE worksin SET iid=? WHERE iid=?"

def re_fn(expr, item):
	reg=re.compile(expr,re.I)
	return reg.search(item) is not None

class SQLManager:
	con = None
	deptref = {}
	instref = {}

	def __init__(self):
        	self.con = lite.connect("grades2.db")
	        self.con.create_function("REGEXP",2,re_fn)
	        self.con.execute(instructors)
	        self.con.execute(department)
	        self.con.execute(worksin)
	        self.con.execute(classes)
	        self.con.execute(grades)
	        self.con.commit()

	def adddept(self, nameshort, name):
		global deptref
		if nameshort in self.deptref: return
		cur = self.con.cursor()
		data = [name, nameshort]
		cur.execute(adddepartment, data)
		result = cur.lastrowid
		self.deptref[nameshort] = result

    	def addgrades(self,cid,ap,a,am,bp,b,bm,cp,c,cm,dp,d,dm,f,w,wp,wf,i,x,y,p,s,finished,withdrawl,other,total,avggpa):
        	data = [cid,ap,a,am,bp,b,bm,cp,c,cm,dp,d,dm,f,w,wp,wf,i,x,y,p,s,finished,withdrawl,other,total,avggpa]
        	self.con.execute(addgrades, data)

	def addworksin(self,did,iid):
		self.con.execute(addworksin,[iid,did])

	def addinstructor(self, inst):
		if inst in self.instref: return
		cur = self.con.cursor()
		self.con.execute(addinstructor,[inst])
		result = cur.lastrowid
		self.instref[inst] = result

	def commit(self):
		self.con.commit()

	def addclass(self,dept,honors,number,section,year,semester,instructor,title):
		cur = self.con.cursor()
		iid = self.instref[instructor]
		did = self.deptref[dept]

		args = [did,honors,iid,number,semester,section,year,title]
		cur.execute(addclass, args)	
		cid = cur.lastrowid

		reg = cur.execute(checkworksin,[iid,did]).fetchone()
		if reg is None:
			self.addworksin(did,iid)

		return cid
