from os import environ
import pymysql


def connect_to_db():
    db = pymysql.connect(
        host=environ.get("MYSQL_WRITER_HOST"),
        user=environ.get("MYSQL_USER"),
        password=environ.get("MYSQL_PASSWD"),
        database=environ.get("MYSQL_DEFAULT_DB")
    )
    cursor = db.cursor()
    return db, cursor


def get_default_term():
    db, cursor = connect_to_db()
    query = "CALL GetDefaultTerm()"
    cursor.execute(query)
    [[default_term]] = cursor.fetchall()
    db.close()
    return default_term


def uuid_finder(cursor, email):
    query = "SELECT UUID FROM Users WHERE Email = '%s'" % email
    cursor.execute(query)
    return cursor.fetchall()


# Term in format "name year", e.g. "Spring 2020"
def get_term_id(term):
    db, cursor = connect_to_db()
    query = "SELECT TermID FROM Terms WHERE TermName = '%s'" % term
    cursor.execute(query)
    id = cursor.fetchall()
    return id[0][0]


# Start of INSERT queries
def register(email, name, salted_password):
    if email == '' or name == '' or salted_password == '':
        return 1, "Empty field"
    db, cursor = connect_to_db()
    try:
        query = "INSERT INTO Users VALUES (UUID(),%s,%s,%s)"
        val = (email, name, salted_password)
        cursor.execute(query, val)
        db.commit()
        db.close()
    except pymysql.Error as err:
        return 1, str(err)
    return 0, "Success"


def add_schedule(email, crn, term=environ.get("DEFAULT_TERM")):
    if email == '' or crn == '':
        return 1, "Empty field"
    db, cursor = connect_to_db()
    try:
        uuid = uuid_finder(cursor, email)
        try:
            uuid = uuid[0][0]
        except:
            return 1, "User doesn't exist"
        query = "INSERT INTO Enrollments VALUES(%s, %s, %s)"
        val = (uuid, term, crn)
        cursor.execute(query, val)
        db.commit()
        db.close()
    except pymysql.Error as err:
        return 1, str(err)
    return 0, "success"


# End of INSERT queries, start of UPDATE queries
def update_name(email, name):
    if email == '' or name == '':
        return 1, "Empty field"
    db, cursor = connect_to_db()
    try:
        query = "UPDATE Users SET Name = %s WHERE email = %s"
        val = (name, email)
        cursor.execute(query, val)
        db.commit()
        db.close()
    except pymysql.Error as err:
        return 1, str(err)
    return 0, "Success"


# End of UPDATE queries, begin of DELETE queries
def delete_account(email):
    if email == '':
        return 1, "Empty field"
    db, cursor = connect_to_db()
    try:
        query = "DELETE FROM Users WHERE email = '%s'" % email
        cursor.execute(query)
        db.commit()
        db.close()
    except pymysql.Error as err:
        return 1, str(err)
    return 0, "Success"


def delete_schedule(email, crn, term=environ.get("DEFAULT_TERM")):
    if email == '' or crn == '':
        return 1, "Empty field"
    db, cursor = connect_to_db()
    try:
        uuid = uuid_finder(cursor, email)
        try:
            uuid = uuid[0][0]
        except:
            return 1, "User doesn't exist"
        query = "DELETE FROM Enrollments WHERE UUID = %s AND crn = %s AND TermID = %s"
        print(uuid)
        print(crn)
        print(term)
        val = (uuid, crn, term)
        cursor.execute(query, val)
        db.commit()
        db.close()
    except pymysql.Error as err:
        return 1, str(err)
    return 0, "Success"


# End of DELETE query, start SELECT query/advanced query
def get_schedule(email, term=environ.get("DEFAULT_TERM")):
    db, cursor = connect_to_db()
    try:
        uuid = uuid_finder(cursor, email)
        try:
            uuid = uuid[0][0]
        except:
            return 1, "User doesn't exist"
        query = "SELECT CRN, CourseID, SubjectID, TypeName, StartTime, EndTime, DaysOfWeek, BuildingName, RoomNumber\
                FROM Enrollments NATURAL JOIN Sections NATURAL JOIN Meetings\
                WHERE UUID = %s AND TermID = %s"
        value = (uuid, term)
        print(term)
        cursor.execute(query, value)
        res = cursor.fetchall()
        db.commit()
        db.close()
        return 0, res
    except pymysql.Error as err:
        return 1, str(err)


def get_class_section(subject, code, term=environ.get("DEFAULT_TERM")):
    db, cursor = connect_to_db()
    try:
        query = "SELECT CRN, CourseID, SubjectID, TypeName, StartTime, EndTime, DaysOfWeek, BuildingName, RoomNumber\
                FROM Sections NATURAL JOIN Meetings\
                WHERE CourseID = %s AND SubjectID = %s AND TermID = %s"
        value = (code, subject, term)
        cursor.execute(query, value)
        res = cursor.fetchall()
        db.commit()
        db.close()
        return 0, res
    except pymysql.Error as err:
        return 1, str(err)


# Waiting for Chatbot
def get_class_mate(email):
    pass


# Waiting for crawl data
def get_difficulty(subject, code):
    pass


if __name__ == '__main__':
    print(get_default_term())
