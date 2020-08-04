from src.api.query import get_cls_gpa, get_usr_sections, find_hour, get_instructor, get_instructor_cls_gpa, \
    get_default_term
from os import environ

environ.setdefault("DEFAULT_TERM", str(get_default_term()[0]))
environ.setdefault("DEFAULT_TERM_NAME", str(get_default_term()[1]))

# purposed algo sum((1 + int(cls_num/100)*weight)*(4 - avg_gpa)*(1 - sentiment)*hrs) * (total_hrs/semester hr cap)

# pre-defined
weight = 0.15
# need data to do sentiment analysis
sentiment = 0.7
# cap is 9 for summer
cap = 9


# wrapper
def calculate_difficulty(email, term=environ.get("DEFAULT_TERM")):
    status, response = fetch_grades(email, term)
    if status == 1:
        return status, response
    class_id, subject_id, credit, crn, gpa = response
    return 0, sum([(1 + int(cls_num / 100) * weight) * (4 - grade) * (1 - sentiment) * c for cls_num, grade, c in zip(class_id, gpa, credit)]) * (sum(credit) / cap)


# this output should reflect difficulty in some degree
# but probably need some normalization using data
# also weight and sentiment need to be implemented&&refined
def fetch_grades(email, term=environ["DEFAULT_TERM"]):
    status, sections = sections_parser(email, term)
    if status == 1:
        return 1, sections
    gpa = []
    class_id, subject_id, credit, crn = sections
    
    # Updated GPA calculation logic. Use specific instructor gpa if available, if not, use course gpa, finally use 3.0
    for cid, sid, crn in zip(class_id, subject_id, crn):
        status, instructor = get_instructor(crn, term)
        if status == 0:
            s, grade = get_instructor_cls_gpa(sid, cid, instructor)
            if s == 0:
                gpa.append(grade)
            else:
                s, response = get_cls_gpa(sid, cid)
                # if failed to get gpa append 3.0 as an median estimate
                gpa.append(response if s == 0 else 3.0)
        else:
            s, response = get_cls_gpa(sid, cid)
            gpa.append(response if s == 0 else 3.0)

    for i in range(0, len(credit)):
        if credit[i] is None:
            # Some data has credit entry as None, need to find it manually
            # When CreditHours attribute contains multiple hours, the max one is used
            credit[i] = find_hour(subject_id[i], class_id[i], term)
    
    print("Parsed credit info: {}".format(credit))
    print("Course IDs: {}".format(class_id))
    
    # Numpy is not used for deployment size issues, sry if you can't understand manual broadcast
    return 0, (class_id, subject_id, credit, crn, gpa)


def sections_parser(email, term):
    status, response = get_usr_sections(email, term)
    if status == 1:
        return 1, response
    if len(response) == 0:
        return 1, "No Schedule found"
    #print("User Section Raw: {}".format(response))
    class_id = [s[0] for s in response]
    subject_id = [s[1] for s in response]
    credit = [s[2] for s in response]
    crn = [s[3] for s in response]
    return 0, (class_id, subject_id, credit, crn)


def diff_breakdown(email, term=environ.get("DEFAULT_TERM")):
    status, response = fetch_grades(email, term)
    if status == 1:
        return status, response
    class_id, subject_id, credit, crn, gpa = response
    weighted_gpa = [(1 + int(cls_num / 100) * weight) * (4 - grade) * (1 - sentiment) * c for cls_num, grade, c in zip(class_id, gpa, credit)]
    factors = [w / sum(weighted_gpa) for w in weighted_gpa]
    return (
        0,
        [(cid, sid, factor) for cid, sid, factor in zip(class_id, subject_id, factors)]
    )
