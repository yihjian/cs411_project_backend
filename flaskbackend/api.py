from flask import Flask, request, jsonify
from flask_restful import Resource, Api, abort, reqparse
from query import *
from globalVar import *
import re
import json

app = Flask(__name__)
api = Api(app)

parser = reqparse.RequestParser()
parser.add_argument('crn')

def abortInvalidRequest(description):
    abort(400, status = "failed", description = description, data = None)

def scheduleParser(schedule):
    return {
        'crn':schedule[0],
        'clsCode':schedule[2]+str(schedule[1]),
        'clsType':schedule[3],
        'startTime':str(schedule[4]),
        'endTime':str(schedule[5]),
        'meetDay':schedule[6],
        'building':schedule[7],
        'room':schedule[8]
    }

def termIdGetter(term):
    try:
        return getTermID(term)
    except:
        abortInvalidRequest("Term '{}' is invalid".format(term))

class classSchedule(Resource):
    def get(self, clsCode, term = "Summer 2020"):
        termId = termIdGetter(term)
        parsedClsCode = re.findall('(\d+|\D+)',clsCode)
        subject = None
        courseId = None
        try:
            subject = parsedClsCode[0].upper()
            courseId = int(parsedClsCode[1])
        except:
            abortInvalidRequest("Class '{}' is invalid".format(clsCode))
        queryResult = getClassSection(subject, courseId, termId)
        if queryResult[0] == 1:
            abortInvalidRequest(queryResult[1])
        if len(queryResult[1]) == 0:
            abortInvalidRequest("Class '{}' not found".format(clsCode))
        return {
            'status':'success',
            'description':"Sections for '{}' in '{}'".format(clsCode, term),
            'data':[scheduleParser(s) for s in queryResult[1]]
        }

class userSchedule(Resource):
    
    def get(self, email, term = "Summer 2020"):
        termId = termIdGetter(term)
        queryResult = getSchedule(email, termId)
        if queryResult[0] == 1:
            abortInvalidRequest(queryResult[1])
        if len(queryResult[1]) == 0:
            abortInvalidRequest("Schedule for user '{}' in term '{}' not found"
                .format(email, term))
        return {
            'status':'success',
            'description':"Schedule for '{}' in '{}'".format(email, term),
            'data':[scheduleParser(s) for s in queryResult[1]]
        }
    
    def delete(self, email, term = "Summer 2020"):
        termId = termIdGetter(term)
        crn = parser.parse_args()['crn']
        queryResult = deleteSchedule(email, crn, termId)
        if queryResult[0] == 1:
            abortInvalidRequest(queryResult[1])
        return {
            'status':'success',
            'description':"Deleted '{}' for '{}' in '{}'".format(crn, email, term),
            'data':None
        }
    
    def put(self, email, term = "Summer 2020"):
        termId = termIdGetter(term)
        crn = parser.parse_args()['crn']
        queryResult = addSchedule(email, crn, termId)
        if queryResult[0] == 1:
            abortInvalidRequest(queryResult[1])
        return {
            'status':'success',
            'description':"Deleted '{}' for '{}' in '{}'".format(crn, email, term),
            'data':None
        }

api.add_resource(classSchedule, 
    '/clsSchedule/<string:clsCode>',
    '/clsSchedule/<string:clsCode>/<string:term>')

api.add_resource(userSchedule,
    '/usrSchedule/<string:email>',
    '/usrSchedule/<string:email>/<string:term>')

if __name__ == '__main__':
    app.run(debug=True)