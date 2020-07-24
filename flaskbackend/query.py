from globalVar import *
import MySQLdb

# Connects to db
def connectToDb():
    db = MySQLdb.connect(
        host=host,
        user=user,
        password=password,
        database=database
    )
    cursor = db.cursor()
    return db, cursor

def uuidFinder(cursor, email):
    query = "SELECT UUID FROM Users WHERE Email = '%s'"%email
    cursor.execute(query)
    return cursor.fetchall()

# Term in format "name year", e.g. "Spring 2020"
def getTermID(term):
    db, cursor = connectToDb()
    query = "SELECT TermID FROM Terms WHERE TermName = '%s'"%term
    cursor.execute(query)
    id = cursor.fetchall()
    return id[0][0]

## Start of INSERT queries

def register(email, name, saltedpassword):
    if (email == '' or name == '' or saltedpassword == ''):
        return (1, "Empty field")
    db, cursor = connectToDb()
    try:
        query = "INSERT INTO Users VALUES (UUID(),%s,%s,%s)"
        val = (email, name, saltedpassword)
        cursor.execute(query, val)
        db.commit()
        db.close()
    except MySQLdb.Error as err:
        return (1, str(err))
    return (0, "Sucess")

def addSchedule(email, crn, term = defaultTerm):
    if (email == '' or crn == ''):
        return (1, "Empty field")
    db, cursor = connectToDb()
    try:
        uuid = uuidFinder(cursor, email)
        try:
            uuid = uuid[0][0]
        except:
            return (1, "User doesn't exist")
        query = "INSERT INTO Enrollments VALUES(%s, %s, %s)"
        val = (uuid, term, crn)
        cursor.execute(query, val)
        db.commit()
        db.close()
    except MySQLdb.Error as err:     
        return (1, str(err))
    return (0, "sucess")

## End of INSERT queries, start of UPDATE queries

def updateName(email, name):
    if (email == '' or name == ''):
        return (1, "Empty field")
    db, cursor = connectToDb()
    try:
        query = "UPDATE Users SET Name = %s WHERE email = %s"
        val = (name, email)
        cursor.execute(query, val)
        db.commit()
        db.close()
    except MySQLdb.Error as err:     
        return (1, str(err))
    return (0, "Sucess")

## End of UPDATE queries, begin of DELETE queries

def deleteAccount(email):
    if (email == ''):
        return (1, "Empty field")
    db, cursor = connectToDb()
    try:
        query = "DELETE FROM Users WHERE email = '%s'"%email
        cursor.execute(query)
        db.commit()
        db.close()
    except MySQLdb.Error as err:     
        return (1, str(err))
    return (0, "Sucess")

def deleteSchedule(email, crn, term = defaultTerm):
    if (email == '' or crn == ''):
        return (1, "Empty field")
    db, cursor = connectToDb()
    try:
        uuid = uuidFinder(cursor, email)
        try:
            uuid = uuid[0][0]
        except:
            return (1, "User doesn't exist")
        query = "DELETE FROM Enrollments WHERE UUID = %s AND crn = %s AND TermID = %s"
        print(uuid)
        print(crn)
        print(term)
        val = (uuid, crn, term)
        cursor.execute(query, val)
        db.commit()
        db.close()
    except MySQLdb.Error as err:     
        return (1, str(err))
    return (0, "Sucess")

## End of DELETE query, start SELECT query/advanced query

def getSchedule(email, term = defaultTerm):
    db, cursor = connectToDb()
    try:
        uuid = uuidFinder(cursor, email)
        try:
            uuid = uuid[0][0]
        except:
            return (1, "User doesn't exist")
        query = "SELECT CRN, CourseID, SubjectID, TypeName, StartTime, EndTime, DaysOfWeek, BuildingName, RoomNumber\
                FROM Enrollments NATURAL JOIN Sections NATURAL JOIN Meetings\
                WHERE UUID = %s AND TermID = %s"
        value = (uuid, term)
        cursor.execute(query, value)
        res = cursor.fetchall()
        db.commit()
        db.close()
        return(0, res)
    except MySQLdb.Error as err:     
        return (1, str(err))

def getClassSection(subject, code, term = defaultTerm):
    db, cursor = connectToDb()
    try:
        query = "SELECT CRN, CourseID, SubjectID, TypeName, StartTime, EndTime, DaysOfWeek, BuildingName, RoomNumber\
                FROM Sections NATURAL JOIN Meetings\
                WHERE CourseID = %s AND SubjectID = %s AND TermID = %s"
        value = (code, subject, term)
        cursor.execute(query, value)
        res = cursor.fetchall()
        db.commit()
        db.close()
        return(0, res)
    except MySQLdb.Error as err:     
        return (1, str(err))

# Waiting for chatbot
def getClassMate(email):
    pass

# Waiting for crawl data
def getDifficulty(subject, code):
    pass