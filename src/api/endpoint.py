from flask_restful import Resource, Api, abort, reqparse
from flask_restful.inputs import boolean
from flask import Flask, redirect
from src.api.query import *
from src.api.difficulty import calculate_difficulty, diff_breakdown
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


def difficulty_parser(data):
    return {
        "clsCode": data[1] + str(data[0]),
        "contribution": data[2]
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

    def get(self, cls_code, term=environ["DEFAULT_TERM_NAME"]):
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
                "status": "success" if status == 0 else "failed",
                "description": "Update user name",
                "data": result
            }
        except Exception as err:
            traceback.print_exception(type(err), err, err.__traceback__)
            abort_invalid_request(str(err))


class GetRemark(Resource):

    def post(self, email):
        try:
            parser = reqparse.RequestParser()
            parser.add_argument("crn")
            parser.add_argument("term")
            parser.add_argument("content")
            args = parser.parse_args()
            (status, result) = get_remark(email, args["crn"], args["content"], args["term"])
            return {
                "status": "success" if status == 0 else "failed",
                "data": result
            }
        except Exception as err:
            traceback.print_exception(type(err), err, err.__traceback__)
            abort_invalid_request(str(err))


class AddRemark(Resource):

    def post(self, email):
        try:
            parser = reqparse.RequestParser()
            parser.add_argument("crn")
            parser.add_argument("term")
            parser.add_argument("remark")
            args = parser.parse_args()
            (status, result) = add_remark(email, args["crn"], args["term"], args["remark"])
            return {
                "status": "success" if status == 0 else "failed",
                "data": result
            }
        except Exception as err:
            print(err)
            abort(str(err))


class ModifyRemark(Resource):

    def post(self, email):
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
                "description": "Modified remark for %s " % email,
                "data": result
            }
        except Exception as err:
            abort_invalid_request(str(err))
            traceback.print_exception(type(err), err, err.__traceback__)


class GetDifficulty(Resource):
    def post(self, email):
        try:
            parser = reqparse.RequestParser()
            parser.add_argument("term")
            args = parser.parse_args()
            status, result = calculate_difficulty(email,
                                                  environ["DEFAULT_TERM"] if args["term"] is None else args["term"])
            return {
                "status": "success" if status == 0 else "failed",
                "description": "Estimated work load for %s " % email,
                "data": result
            }
        except Exception as err:
            traceback.print_exception(type(err), err, err.__traceback__)
            abort_invalid_request(str(err))


class GetDifficultyBreakdown(Resource):
    def post(self, email):
        try:
            parser = reqparse.RequestParser()
            parser.add_argument("term", type=int)
            args = parser.parse_args()
            status, result = diff_breakdown(email,
                                            environ["DEFAULT_TERM"] if args.get("term") is None else args.get("term"))
            return {
                "status": "success" if status == 0 else "failed",
                "description": "Difficulty breakdown %s " % email,
                "data": [difficulty_parser(r) for r in result]
            }
        except Exception as err:
            traceback.print_exception(type(err), err, err.__traceback__)
            abort_invalid_request(str(err))


class GetRawGPA(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("term", type=int)
        parser.add_argument("subject", type=str)
        parser.add_argument("course_id", type=int)
        parser.add_argument("course_name", type=str)
        parser.add_argument("crn", type=int)
        parser.add_argument("instructor", type=str)
        parser.add_argument("limit", type=int)
        try:
            args = parser.parse_args()

            (status, response) = get_raw_gpa(args.get("term"), args.get("subject"), args.get("course_id"),
                                             args.get("course_name"), args.get("crn"), args.get("instructor"),
                                             args.get("limit"))
            return {
                "status": "success" if status == 0 else "failed",
                "description": "fetch all the GPA raw data of the records that meet search condition",
                "data": response
            }
        except Exception as err:
            traceback.print_exception(type(err), err, err.__traceback__)
            abort_invalid_request(str(err))


class GetRating(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument("name", type=str)
        args = parser.parse_args()
        (status, response) = get_rating(args["name"])
        return {
            "status": "success" if status == 0 else "failed",
            "description": "A fuzzy match of instructor name to ratings",
            "data": response
        }


class GetCommentsByName(Resource):
    def get(self, name):
        parser = reqparse.RequestParser()
        parser.add_argument("limit", type=int)
        args = parser.parse_args()
        result_limit = args.get("limit") if args.get("limit") is not None else 50
        (status, response) = get_comments_by_name(name, limit=result_limit)
        return {
            "status": "success" if status == 0 else "failed",
            "description": "A fuzzy match of instructor name to comments",
            "data": response
        }


class GetCommentsByClass(Resource):
    def get(self, class_name):
        parser = reqparse.RequestParser()
        parser.add_argument("limit", type=int)
        args = parser.parse_args()
        result_limit = args.get("limit") if args.get("limit") is not None else 50
        (status, response) = get_comments_by_class(class_name, limit=result_limit)
        return {
            "status": "success" if status == 0 else "failed",
            "description": "A fuzzy match of instructor name to comments",
            "data": response
        }


class WeChat(Resource):
    def put(self, email):
        parser = reqparse.RequestParser()
        parser.add_argument("wxid", type=str)
        args = parser.parse_args()
        (status, response) = add_wechat_account(args["wxid"], email)
        return {
            "status": "success" if status == 0 else "failed",
            "description": "Link Ultimate-MyIllini account to WeChat account",
            "data": response
        }

    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument("term", type=str)
        parser.add_argument("subject", type=str)
        parser.add_argument("course", type=int)
        args = parser.parse_args()
        term_id = termid_getter(args["term"])
        (status, response) = find_wechat_room(args["subject"], args["course"], term_id)
        return {
            "status": "success" if status == 0 else "failed",
            "description": "Wechat room ID for the searched course",
            "data": response
        }

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("room_id", type=str)
        parser.add_argument("room_topic", type=str)
        parser.add_argument("subject", type=str)
        parser.add_argument("course", type=int)
        parser.add_argument("term", type=int)
        args = parser.parse_args()
        (status, response) = create_room(args["room_id"], args["room_topic"], args["subject"],
                                         args["course"], args["term"])
        return {
            "status": "success" if status == 0 else "failed",
            "description": "Room Creation",
            "data": response
        }


class GetEmailByWxid(Resource):
    def get(self, wxid):
        (status, response) = get_email_by_wx(wxid)
        return {
            "status": "success" if status == 0 else "failed",
            "description": "Registered email by wxid",
            "data": response
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

api.add_resource(GetRemark, '/remark/<string:email>')

api.add_resource(AddRemark, '/remark/<string:email>/add')

api.add_resource(ModifyRemark, '/remark/<string:email>/modify')

api.add_resource(GetDifficulty, '/difficulty/<string:email>')

api.add_resource(GetDifficultyBreakdown, '/difficulty/<string:email>/breakdown')

api.add_resource(GetRawGPA, '/gpa/raw')

api.add_resource(GetRating, '/rating')

api.add_resource(GetCommentsByName, '/comment/name/<string:name>')

api.add_resource(GetCommentsByClass, '/comment/class/<string:class_name>')

api.add_resource(WeChat,
                 '/wechat/link/<string:email>',
                 '/wechat/room/create',
                 '/wechat/room/find')

api.add_resource(GetEmailByWxid, '/wechat/email/<string:wxid>')


if __name__ == '__main__':
    app.run(debug=True)
