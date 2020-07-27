from flask_restful import Resource, Api, abort, reqparse
from flask_restful.inputs import boolean
from flask import Flask, redirect
from src.api.query import *
from os import environ
import re

app = Flask(__name__)
api = Api(app)

environ.setdefault("DEFAULT_TERM", str(get_default_term()[0]))
environ.setdefault("DEFAULT_TERM_NAME", str(get_default_term()[1]))

enrollment_parser = reqparse.RequestParser()
enrollment_parser.add_argument('crn')
enrollment_parser.add_argument('key')


def abort_invalid_request(description):
    abort(400, status="failed", description=description, data=None)


def schedule_parser(schedule):
    return {
        'crn': schedule[0],
        'clsCode': schedule[2] + str(schedule[1]),
        'clsType': schedule[3],
        'startTime': str(schedule[4]),
        'endTime': str(schedule[5]),
        'meetDay': schedule[6],
        'building': schedule[7],
        'room': schedule[8]
    }


def termid_getter(term):
    try:
        return get_term_id(term)
    except Exception as e:
        print(e)
        abort_invalid_request("Term '{}' is invalid".format(term))


class SectionSearch(Resource):

    def get(self):
        query_string_parser = reqparse.RequestParser()
        query_string_parser.add_argument("crn", type=int, location="args")
        query_string_parser.add_argument("name", type=str, location="args")
        query_string_parser.add_argument("subject", type=str, location="args")
        query_string_parser.add_argument("id", type=int, location="args")
        query_string_parser.add_argument("isCurrentTerm", type=boolean, location="args")
        query_string_parser.add_argument("limit", type=int, location="args")
        args = query_string_parser.parse_args()
        print("Fuzzy search query {}".format(args))
        try:
            search_result = search_courses(
                args.get("crn"),
                args.get("name"),
                args.get("subject"),
                args.get("id"),
                boolean(args.get("isCurrentTerm")) if args.get("isCurrentTerm") is not None else True,
                args.get("limit")
            )
            print("Query result {}".format(search_result))
            (status, result) = search_result
            return {
                "status": "success" if status == 0 else "failed",
                "description": "Sections matched by fuzzy search",
                "response": result
            }
        except Exception as e:
            print(e)
            abort_invalid_request("Invalid request: {}".format(args))


class Docs(Resource):

    def get(self):
        return redirect("https://github.com/yihjian/cs411_project_backend/blob/production/README.md", 302)


class ClassSchedule(Resource):

    def get(self, cls_code, term="Summer 2020"):
        term_id = termid_getter(term)
        parsed_cls_code = re.findall('(\d+|\D+)', cls_code)
        subject = None
        course_id = None
        try:
            subject = parsed_cls_code[0].upper()
            course_id = int(parsed_cls_code[1])
        except Exception as e:
            print(e)
            abort_invalid_request("Class '{}' is invalid".format(cls_code))
        query_result = get_class_section(subject, course_id, term_id)
        if query_result[0] == 1:
            abort_invalid_request(query_result[1])
        if len(query_result[1]) == 0:
            abort_invalid_request("Class '{}' not found".format(cls_code))
        return {
            'status': 'success',
            'description': "Sections for '{}' in '{}'".format(cls_code, term),
            'data': [schedule_parser(s) for s in query_result[1]]
        }


class UserSchedule(Resource):

    def get(self, email, term=environ["DEFAULT_TERM_NAME"]):
        term_id = termid_getter(term)
        query_result = get_schedule(email, term_id)
        if query_result[0] == 1:
            abort_invalid_request(query_result[1])
        if len(query_result[1]) == 0:
            abort_invalid_request("Schedule for user '{}' in term '{}' not found"
                                  .format(email, term))
        return {
            'status': 'success',
            'description': "Schedule for '{}' in '{}'".format(email, term),
            'data': [schedule_parser(s) for s in query_result[1]]
        }

    def delete(self, email, term=environ["DEFAULT_TERM_NAME"]):
        term_id = termid_getter(term)
        crn = enrollment_parser.parse_args().get('crn')
        # key = enrollment_parser.parse_args().get('key')
        # if key != environ["API_KEY"]:
        # abort_invalid_request("Authentication failed")
        query_result = delete_schedule(email, crn, term_id)
        if query_result[0] == 1:
            abort_invalid_request(query_result[1])
        return {
            'status': 'success',
            'description': "Deleted '{}' for '{}' in '{}'".format(crn, email, term),
            'data': None
        }

    def put(self, email, term=environ["DEFAULT_TERM_NAME"]):
        term_id = termid_getter(term)
        crn = enrollment_parser.parse_args().get('crn')
        # key = enrollment_parser.parse_args().get('key')
        # if key != environ["API_KEY"]:
        #    abort_invalid_request("Authentication failed")
        query_result = add_schedule(email, crn, term_id)
        if query_result[0] == 1:
            abort_invalid_request(query_result[1])
        return {
            'status': 'success',
            'description': "Added '{}' for '{}' in '{}'".format(crn, email, term),
            'data': None
        }


class Test(Resource):

    def put(self):
        return {
            'status': 'success'
        }


class UpdateName(Resource):

    def put(self, email):
        parser = reqparse.RequestParser()
        parser.add_argument("name")
        try:
            args = parser.parse_args()
            new_name = args["name"]

            (status, result) = update_name(email, new_name)
            return {
                "status": "failed" if status == 0 else "success",
                "description": "Update user name",
                "response": result
            }
        except Exception as e:
            print(e)
            return {
                "status": "failed",
                "description": "Update user name",
                "response": str(e)
            }


class AddRemark(Resource):

    def put(self, email):
        try:
            parser = reqparse.RequestParser()
            parser.add_argument("crn")
            parser.add_argument("term")
            parser.add_argument("remark")
            args = parser.parse_args()
            (status, result) = add_remark(email, args["crn"], args["term"], args["remark"])
            return {
                "status": "success" if status == 0 else "failed",
                "response": result
            }
        except Exception as err:
            print(err)
            return {
                "status": "failed",
                "response": str(err)
            }


class ModifyRemark(Resource):

    def put(self, email):
        try:
            parser = reqparse.RequestParser()
            parser.add_argument("rid")
            parser.add_argument("crn")
            parser.add_argument("term")
            parser.add_argument("remark")
            args = parser.parse_args()
            (status, result) = modify_remark(args["rid"], email, args["crn"], args["term"], args["remark"])
            return {
                "status": "success" if status == 0 else "failed",
                "response": result
            }
        except Exception as err:
            print(err)
            return {
                "status": "failed",
                "response": str(err)
            }


api.add_resource(ClassSchedule,
                 '/clsSchedule/<string:cls_code>',
                 '/clsSchedule/<string:cls_code>/<string:term>')

api.add_resource(UserSchedule,
                 '/usrSchedule/<string:email>',
                 '/usrSchedule/<string:email>/<string:term>')

api.add_resource(SectionSearch, '/search')

api.add_resource(Docs, '/doc')

api.add_resource(Test, '/test')

api.add_resource(UpdateName, '/user/<string:email>')

api.add_resource(AddRemark, '/remark/<string:email>')

api.add_resource(ModifyRemark, '/remark/modify/<string:email>')


if __name__ == '__main__':
    app.run(debug=True)
