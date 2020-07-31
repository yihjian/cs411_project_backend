from sr.api.query import get_cls_gpa, get_usr_sections, find_hour
from os import environ
# purposed algo sum((1 + int(cls_num/100)*weight)*(4 - avg_gpa)*(1 - sentiment)) * (total_hrs/semester hr cap)

# pre-defined
weight = 0.15
# need data to do sentiment analysis
sentiment = 0.7
# cap is 9 for summer
cap = 9

# this output should reflect difficulty in some degree
# but probably need some normalization using data
# also weight and sentiment need to be implemented&&refined
def calculate_difficulty(email, term=environ.get("DEFAULT_TERM")):
    status, sections = sections_parser(email, term)
    if status == 1:
        return 1, sections
    gpa = []
    class_id, subject_id, credit = sections
    for cid, sid in zip(class_id, subject_id):
        status, response = get_cls_gpa(sid, cid)
        gpa.append(response if status == 0 else 3.0)
        # if failed to get gpa append 3.0 as an median estimate
    for i in range(0, len(credit)):
        if credit[i] == None:
            # Some data has credit entry as None, need to find it manually
            # When CreditHours attribute contains multiple hours, the max one is used
            credit[i] = find_hour(subject_id[i], class_id[i]) 
    # Numpy is not used for deployment size issues, sry if you can't understand mannual broadcast
    return sum((1 + int(cls_num/100) * weight) * (4 - grade) * (1 - sentiment) for cls_num, grade in zip(class_id, gpa)) * (sum(credit) / cap)

def sections_parser(email, term=environ.get("DEFAULT_TERM")):
    status, response = get_usr_sections(email, term)
    if status == 1:
        return sections
    if len(response) == 0:
        return 1, "No Schedule found"
    class_id = [s[0] for s in response]
    subject_id = [s[1] for s in response]
    credit = [s[2] for s in response]
    return 0, (class_id, subject_id, credit)
