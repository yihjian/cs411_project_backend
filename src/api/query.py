from os import environ
import pymysql
import re

def connect_to_db():
    db = pymysql.connect(
        host=environ["MYSQL_WRITER_HOST"],
        user=environ["MYSQL_USER"],
        password=environ["MYSQL_PASSWD"],
        database=environ["MYSQL_DEFAULT_DB"]
    )
    cursor = db.cursor()
    return db, cursor


def get_default_term():
    db, cursor = connect_to_db()
    query = "CALL GetDefaultTerm()"
    cursor.execute(query)
    [(default_term_id, default_term_name)] = cursor.fetchall()
    db.close()
    return default_term_id, default_term_name


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
    db.close()
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
        val = (uuid, crn, term)
        cursor.execute(query, val)
        db.commit()
        db.close()
    except pymysql.Error as err:
        return 1, str(err)
    return 0, "Success"


# End of DELETE query, start SELECT query/advanced query
def get_schedule(email, term=environ.get("DEFAULT_TERM")):
    if email == '':
        return 1, "Empty field"
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


def search_courses(crn, course_name, subject, course_id, is_current_term, num_records):
    db, cursor = connect_to_db()
    try:
        query = "CALL SearchCourse(%s, %s, %s, %s, %s, %s)"
        param = (crn, course_name, subject, course_id, is_current_term, num_records)
        cursor.execute(query, param)
        response = cursor.fetchall()
        print(response)
        db.close()
        return parse_search_result((0, response))
    except pymysql.Error as err:
        print(err)
        return 1, str(err)


def parse_search_result(search_response):
    (status, result) = search_response
    return (
        status,
        list(map(lambda section: {
            "term_id": section[0],
            "term_name": section[1],
            "crn": section[2],
            "subject": section[3],
            "course_id": section[4],
            "course_name": section[5],
            "type_name": section[6],
            "full_name": section[7],
            "days_of_week": section[8],
            "start": str(section[9]) if section[9] is not None else section[9],
            "end": str(section[10]) if section[9] is not None else section[10]
        }, result)) if status == 0 else result
    )

def add_remark(email, crn, term_id, remark):
    try:
        db, cursor = connect_to_db()
        query = "CALL AddRemark(%s, %s, %s, %s)"
        param = (email, crn, term_id, remark)
        cursor.execute(query, param)
        [response] = cursor.fetchall()
        db.commit()
        db.close()
        return 0, {
            "rid": response[0],
            'uuid': response[1],
            'crn': response[2],
            'term_id': response[3]
        }
    except pymysql.MySQLError as err:
        print(err)
        return 1, str(err)


def modify_remark(rid, email, crn, term_id, remark):
    try:
        db, cursor = connect_to_db()
        query = "CALL ModifyRemark(%s, %s, %s, %s, %s)"
        param = (rid, email, crn, term_id, remark)
        cursor.execute(query, param)
        [response] = cursor.fetchall()
        db.commit()
        db.close()
        return 0, {
            "rid": response[0],
            "uid": response[1],
            "crn": response[2],
            "term_id": response[3],
            "remark": response[4]
        }
    except pymysql.MySQLError as err:
        print(err)
        return 1, str(err)

#########################################################
##      helper queries for our advanced functions      ##
#########################################################

# No error should occur here considering all the foreign keys
# So I'm not checking
def find_hour(subject, course, term=environ.get("DEFAULT TERM")):
    db, cursor = connect_to_db()
    query = "SELECT CreditHours FROM Courses WHERE SubjectID = %s AND TermID = %s AND CourseID = %s"
    val = (subject, term, course)
    cursor.execute(query, val)
    response = cursor.fetchall() #Should be length 1
    print(response)
    hours = re.findall(r'\d+', response[0][0])
    return max(hours)
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            

def get_usr_sections(email, term=environ.get("DEFAULT_TERM")):
    if email == '':
        return 1, "Empty field"
    db, cursor = connect_to_db()
    try:
        uuid = uuid_finder(cursor, email)
        try:
            uuid = uuid[0][0]
        except:
            return 1, "User doesn't exist"
        query = "SELECT DISTINCT CourseID, SubjectID, Credits\
            FROM Enrollments NATURAL JOIN Sections\
            WHERE uuid = %s AND TermID = %s"
        val = (uuid, term)
        cursor.execute(query, val)
        res = cursor.fetchall()
        db.close()
        return 0, res
    except pymysql.Error as err:
        return 1, str(err)

weight = [4.0, 4.0, 3.67, 3.33, 3, 2.67, 2.33, 2, 1.67, 1.33, 1, 0.67, 0, 0]

def get_cls_gpa(subject, code):
    if (subject == ''):
        return 1, "Empty subject"
    db, cursor = connect_to_db()
    query = "SELECT SubjectID, CourseID, \
            SUM(Ap), SUM(A), SUM(Am), \
            SUM(Bp), SUM(B), SUM(Bm), \
            SUM(Cp), SUM(C), SUM(Cm), \
            SUM(Dp), SUM(D), SUM(Dm), \
            SUM(F), SUM(W)\
            FROM GPA \
            WHERE SubjectID = %s AND CourseID = %s"
    value = (subject, code)
    try:
        cursor.execute(query, value)
        res = cursor.fetchall()
        db.commit()
        db.close()
        if res[0][0] == None: return (1, "class not found")
        return(0, sum(int(x)*y for x, y in zip(res[0][2:], weight))/sum(int(x) for x in res[0][2:]))
    except pymysql.MySQLError as err:
        return(1, str(err))
    except:
        return(1, "Something wrong")

def get_instructor_cls_gpa(subject, code, instructor):
    if (subject == '' or instructor == ''):
        return 1, "Empty field"
    db, cursor = connect_to_db()
    query = "SELECT SubjectID, CourseID, \
            SUM(Ap), SUM(A), SUM(Am), \
            SUM(Bp), SUM(B), SUM(Bm), \
            SUM(Cp), SUM(C), SUM(Cm), \
            SUM(Dp), SUM(D), SUM(Dm), \
            SUM(F), SUM(W)\
            FROM GPA \
            WHERE SubjectID = %s AND CourseID = %s AND PrimaryInstructor LIKE %s"
    value = (subject, code, instructor+"%")
    try:
        cursor.execute(query, value)
        res = cursor.fetchall()
        db.commit()
        db.close()
        if res[0][0] == None: return (1, "class not found")
        return(0, sum(int(x)*y for x, y in zip(res[0][2:], weight))/sum(int(x) for x in res[0][2:]))
    except pymysql.MySQLError as err:
        return(1, str(err))
    except:
        return(1, "Something wrong")