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

## Start of insert queries

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
        query = "SELECT UUID FROM Users WHERE Email = '%s'"%email
        cursor.execute(query)
        uuid = cursor.fetchall()
        query = "INSERT INTO Enrollments VALUES(%s, %s, %s)"
        try:
            uuid = uuid[0][0]
        except:
            return (1, "User doesn't exist")
        val = (uuid, term, crn)
        cursor.execute(query, val)
        db.commit()
        db.close()
    except MySQLdb.Error as err:     
        return (1, str(err))
    return (0, "sucess")

## End of insert queries, start of update queries

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

## End of update queries, begin of delete queries

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
        query = "SELECT UUID FROM Users WHERE Email = '%s'"%email
        cursor.execute(query)
        uuid = cursor.fetchall()
        query = "DELETE FROM Enrollments WHERE UUID = %s AND crn = %s AND TermID = %s"
        val = (email, crn, term)
        cursor.execute(query, val)
        db.commit()
        db.close()
    except MySQLdb.Error as err:     
        return (1, str(err))
    return (0, "Sucess")

##