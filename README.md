## Api Guide

### Class schedule
#### End point
 1. ```/clsSchedule/clsCode/``` for default term (currently summer 2020) 
 2. ```/clsSchedule/clsCode/termName``` for specific term
#### Methods&Response
1. ```GET``` retrieve all sections of a course
    ```javascript
    {
        "status": "failed" or "success",
        "description": "Some description",
        "data": [{
            "crn":12345,
            "clsCode":"cs666",
            "clsType":"Online",
            "startTime":"08:30:00", //Note this is a string
            "endTime":"23:30:00", //nullable
            "meetday":"MTW", //nullable
            "building":"Siebel", //nullable
            "room":"1111", //nullable
        }]
    }
    ```
#### Example 
Request:
``` Bash
curl localhost:5000/clsSchedule/cs411/Summer%202020
``` 
Response:
``` javascript
{
    "status": "success",
    "description": "Sections for 'cs411' in 'Summer 2020'",
    "data": [
        {
            "crn": 40317,
            "clsCode": "CS411",
            "clsType": "Online Lecture",
            "startTime": "11:00:00",
            "endTime": "12:15:00",
            "meetDay": "MTWR",
            "building": null,
            "room": null
        },
        {
            "crn": 40318,
            "clsCode": "CS411",
            "clsType": "Online Lecture",
            "startTime": "11:00:00",
            "endTime": "12:15:00",
            "meetDay": "MTWR",
            "building": null,
            "room": null
        }
    ]
}
```
### User Schedule
#### End point
 1. ```/usrSchedule/email/``` for default term (currently summer 2020) 
 2. ```/usrSchedule/emailCode/termName``` for specific term
#### Methods&Response
**Note that ignoring term is not recordmended when delete/add user schedule** 
1. ```GET``` retrieve all schedule of a user in a specific term, sample response:
    ```javascript
    {
        "status": "failed" or "success",
        "description": "Some description",
        "data": [{
            "crn":12345,
            "clsCode":"cs666",
            "clsType":"Online",
            "startTime":"08:30:00", //Note this is a string
            "endTime":"23:30:00", //nullable
            "meetday":"MTW", //nullable
            "building":"Siebel", //nullable
            "room":"1111", //nullable
        }]
    }
    ```
2. ```DELETE``` delete enrollment of a section of a user, argument: ```crn=12345```, sample response:
    ```javascript
    {
        "status": "failed" or "success",
        "description": "Some description",
        "data": null
    }
    ```
3. ```PUT``` add enrollment of a section of a user, argument: ```crn=12345```, sample response: 
    ```javascript
    {
        "status": "failed" or "success",
        "description": "Some description",
        "data": null
    }
    ```

#### Example
Request:
``` Bash
curl localhost:5000/usrSchedule/jyh@test.com/Summer%202020 -d "crn=36797" -X PUT
``` 
Response:
``` Json
{
    "status": "success",
    "description": "Deleted '36796' for 'jyh@test.com' in 'Summer 2020'",
    "data": null
}
```

### Fuzzy Search

#### Endpoint
``/search`` to filter courses based on given query parameters.

#### Query Parameters
+ `crn` The CRN of a certain section. Could be `null`. For example, `10374`.
+ `name` The course name of the course where the selected sections belong. Fuzzy search is supported. For example, `data` will filter the courses whose name have "data."
+ `subject` The corresponding subject of selected sections. For example, `CS`.
+ `id` The course ID of the courses to be filtered. For example, `411`.
+ `isCurrentTerm` The flag to determine whether to filter past courses. If not specified, the default value of this field is `true`.
+ `limit` The number of results. If not specified, the default value of this field is `50`.

#### Notes
+ All fields can be `null`. However, `crn`, `name`, `subject`, and `id` can't be `null` at the same time.
+ If a field is not specified, then it is not a part of the searching condition.

#### Sample Response
``/search?subject=CS&name=data&isCurrentTerm=false``
Search for all the CS courses that have "data" in course name and the related sections in all semesters.
Limit the number of results to 50 (default).
Some results are omitted here.
```json
{
    "status": "success",
    "description": "Sections matched by fuzzy search",
    "response": [
        {
            "term_id": 120201,
            "term_name": "Spring 2020",
            "crn": 31208,
            "subject": "CS",
            "course_id": 225,
            "course_name": "Data Structures",
            "type_name": "Lecture",
            "full_name": "Evans, G",
            "days_of_week": "MWF",
            "start": "11:00:00",
            "end": "11:50:00"
        },
        {
            "term_id": 120201,
            "term_name": "Spring 2020",
            "crn": 31208,
            "subject": "CS",
            "course_id": 225,
            "course_name": "Data Structures",
            "type_name": "Lecture",
            "full_name": "Jiang, J",
            "days_of_week": "MWF",
            "start": "11:00:00",
            "end": "11:50:00"
        },
        {
            "term_id": 120201,
            "term_name": "Spring 2020",
            "crn": 31213,
            "subject": "CS",
            "course_id": 225,
            "course_name": "Data Structures",
            "type_name": "Lecture",
            "full_name": "Evans, G",
            "days_of_week": "MWF",
            "start": "14:00:00",
            "end": "14:50:00"
        },
        {
            "term_id": 120201,
            "term_name": "Spring 2020",
            "crn": 47139,
            "subject": "CS",
            "course_id": 512,
            "course_name": "Data Mining Principles",
            "type_name": "Online",
            "full_name": "Han, J",
            "days_of_week": null,
            "start": null,
            "end": null
        }
    ]
}
```
