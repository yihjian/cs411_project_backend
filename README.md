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
    ```Json
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