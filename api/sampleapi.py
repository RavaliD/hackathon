from flask import Flask
from flask import jsonify
from flask import request
from flask_cors import CORS
from cloudant.client import Cloudant
from cloudant.error import CloudantException
from cloudant.result import Result, ResultByKey
import os
import atexit, json

app = Flask(__name__)


# Values to be updated during deployment
serviceUsername = ""
servicePassword = ""
serviceURL = ""

client = Cloudant(serviceUsername, servicePassword, url=serviceURL)
client.connect()

# These are the name of the database we are working with
volunteerDb = "volunteer"
seniorDb = "senior"
requestDb = "request"

# Open an existing database
_volunteerData = client[volunteerDb]
_seniorData = client[seniorDb]
_requestData = client[requestDb]

def fetchVolunteers():
    result_collection = Result(_volunteerData.all_docs, include_docs=True)
    print("Retrieved full document:\n{0}\n".format(result_collection[0]))

    # Space out the results.
    print("----\n")

    # Define the end point and parameters
    end_point = '{0}/{1}'.format(serviceURL, volunteerDb + "/_all_docs")
    params = {'include_docs': 'true'}

    # Issue the request
    response = client.r_session.get(end_point, params=params)

    # Display the response content
    print("{0}\n".format(response.json()))

    return format(response.json())

def fetchSeniors():
    result_collection = Result(_seniorData.all_docs, include_docs=True)
    print("Retrieved full document:\n{0}\n".format(result_collection[0]))

    # Space out the results.
    print("----\n")

    # Define the end point and parameters
    end_point = '{0}/{1}'.format(serviceURL, seniorDb + "/_all_docs")
    params = {'include_docs': 'true'}

    # Issue the request
    response = client.r_session.get(end_point, params=params)

    # Display the response content
    print("{0}\n".format(response.json()))

    return format(response.json())

def fetchRequests():
    result_collection = Result(_requestData.all_docs, include_docs=True)
    print("Retrieved full document:\n{0}\n".format(result_collection[0]))

    # Space out the results.
    print("----\n")

    # Define the end point and parameters
    end_point = '{0}/{1}'.format(serviceURL, requestDb + "/_all_docs")
    params = {'include_docs': 'true'}

    # Issue the request
    response = client.r_session.get(end_point, params=params)

    # Display the response content
    print("{0}\n".format(response.json()))

    return format(response.json())


@app.route('/voloservices/volunteers',methods=['GET'])
def getAllVolunteers():        
    return jsonify({'Volunteers':fetchVolunteers()})

@app.route('/voloservices/seniors',methods=['GET'])
def getAllSeniors():        
    return jsonify({'Seniors':fetchSeniors()})

@app.route('/voloservices/requests',methods=['GET'])
def getAllRequests():        
    return jsonify({'RequestForms':fetchRequests()})    


@app.route('/voloservices/volunteers/<volunteerId>',methods=['GET'])
def getVolunteer(volunteerId):
    partition_key = 'volunteer'
    document_key = volunteerId
    doc = _volunteerData[':'.join((partition_key, document_key))]
    return doc

@app.route('/voloservices/seniors/<seniorId>',methods=['GET'])
def getSenior(seniorId):
    partition_key = 'senior'
    document_key = seniorId
    doc = _seniorData[':'.join((partition_key, document_key))]
    return doc

@app.route('/voloservices/requests/<requestId>',methods=['GET'])
def getRequest(requestId):
    partition_key = 'request'
    document_key = requestId
    doc = _requestData[':'.join((partition_key, document_key))]
    return doc

@app.route('/voloservices/volunteers',methods=['POST'])
def createVolunteer():
    volunteerData = request.get_json("force = True")
    partition_key = 'volunteer'
    document_key = volunteerData['volunteerId']
    document_id = ':'.join((partition_key, document_key))
    doc_exists = document_id in _volunteerData

    if doc_exists:
        rtnString = jsonify("Message", "Volunteer " + volunteerData['volunteerId'] + " already exists!")
    else:
        my_document = _volunteerData.create_document({
            '_id': document_id,
            'volunteerId':volunteerData['volunteerId'],
            'firstName':volunteerData['firstName'],
            'lastName':volunteerData['lastName'],
            'mobileNo':volunteerData['mobileNo'],
            'address':volunteerData['address'],
            'pincode':volunteerData['pincode'],
            'location':volunteerData['location'],
            'serviceopted':volunteerData['serviceopted'],
            'serving':volunteerData['serving'],
            'comments':volunteerData['comments'],
            'emailid':volunteerData['emailid']
        })
        if my_document.exists():
           rtnString = jsonify("Message", "Volunteer " + volunteerData['volunteerId'] + " Added!")
    
    return rtnString

@app.route('/voloservices/seniors',methods=['POST'])
def createSenior():
    seniorData = request.get_json("force = True")
    partition_key = 'senior'
    document_key = seniorData['seniorprofileId']
    document_id = ':'.join((partition_key, document_key))
    doc_exists = document_id in _seniorData

    if doc_exists:
        rtnString = jsonify("Message", "Senior " + seniorData['seniorprofileId'] + " already exists!")
    else:
        my_document = _seniorData.create_document({
            '_id': document_id,
            'seniorprofileId':seniorData['seniorprofileId'],
            'firstName':seniorData['firstName'],
            'lastname':seniorData['lastname'],
            'mobileno':seniorData['mobileno'],
            'address':seniorData['address'],
            'pincode':seniorData['pincode'],
            'location':seniorData['location'],
            'emailid':seniorData['emailid']
        })
        if my_document.exists():
           rtnString = jsonify("Message", "Senior " + seniorData['seniorprofileId'] + " Added!")
    
    return rtnString

@app.route('/voloservices/requests',methods=['POST'])
def createRequest():
    requestData = request.get_json("force = True")
    partition_key = 'request'
    document_key = requestData['requestid']
    document_id = ':'.join((partition_key, document_key))
    doc_exists = document_id in _requestData

    if doc_exists:
        rtnString = jsonify("Message", "RequestForm " + requestData['requestid'] + " already exists!")
    else:
        my_document = _requestData.create_document({
            '_id': document_id,
            'requestid':requestData['requestid'],
            'seniorid':requestData['seniorid'],
            'status':requestData['status'],
            'mobileNo':requestData['mobileNo'],
            'serviceopted':requestData['serviceopted'],
            'timings':requestData['timings'],
            'comments':requestData['comments'],
            'emailid':requestData['emailid'],
            'filepath':requestData['filepath'],
            'commentshistory':requestData['commentshistory']
            
        })
        if my_document.exists():
           rtnString = jsonify("Message", "RequestForm " + requestData['requestid'] + " Added!")
    
    return rtnString

@app.route('/voloservices/volunteers',methods=['PUT'])
def updateVolunteer():
    volunteerData = request.get_json("force = True")
    partition_key = 'volunteer'
    document_key = volunteerData['volunteerId']
    document_id = ':'.join((partition_key, document_key))
    doc_exists = document_id in _volunteerData

    if doc_exists:
        # First retrieve the document
        volunteerDocument = _volunteerData[document_id]

        # Update the document content
        # This can be done as you would any other dictionary
        if volunteerData['firstName'] != "" :
            volunteerDocument['firstName'] = volunteerData['firstName']
        if volunteerData['lastName'] != "" :
            volunteerDocument['lastName'] = volunteerData['lastName']
        if volunteerData['mobileNo'] != "" :
            volunteerDocument['mobileNo'] = volunteerData['mobileNo']
        if volunteerData['address'] != "" :
            volunteerDocument['address'] = volunteerData['address']
        if volunteerData['pincode'] != "" :
            volunteerDocument['pincode'] = volunteerData['pincode']
        if volunteerData['location'] != "" :
            volunteerDocument['location'] = volunteerData['location']
        if volunteerData['serviceopted'] != "" :
            volunteerDocument['serviceopted'] = volunteerData['serviceopted']
        if volunteerData['serving'] != "" :
            volunteerDocument['serving'] = volunteerData['serving']
        if volunteerData['comments'] != "" :
            volunteerDocument['comments'] = volunteerData['comments']
        if volunteerData['emailid'] != "" :
            volunteerDocument['emailid'] = volunteerData['emailid']

        # You must save the document in order to update it on the database
        volunteerDocument.save()
        rtnString = "Volunteer " + volunteerData['volunteerId'] + " updated!"
    else:
        my_document = _volunteerData.create_document({
            '_id': document_id,
            'volunteerId':volunteerData['volunteerId'],
            'firstName':volunteerData['firstName'],
            'lastName':volunteerData['lastName'],
            'mobileNo':volunteerData['mobileNo'],
            'address':volunteerData['address'],
            'pincode':volunteerData['pincode'],
            'location':volunteerData['location'],
            'serviceopted':volunteerData['serviceopted'],
            'serving':volunteerData['serving'],
            'comments':volunteerData['comments'],
            'emailid':volunteerData['emailid']
        })
        if my_document.exists():
           rtnString = "Volunteer " + volunteerData['volunteerId'] + " Added!"
    
    return rtnString

@app.route('/voloservices/volunteers/<volunteerId>',methods=['DELETE'])
def deleteEmp(volunteerId):
    partition_key = 'volunteer'
    document_key = volunteerId
    my_document = _volunteerData[':'.join((partition_key, document_key))]
    my_document.delete()
    return "Volunteer " + volunteerId + " Deleted!"    

@app.route('/voloservices/seniors/<seniorid>',methods=['DELETE'])
def deleteSenior(seniorid):
    partition_key = 'senior'
    document_key = seniorid
    my_document = _seniorData[':'.join((partition_key, document_key))]
    my_document.delete()
    return "Senior " + seniorid + " Deleted!"

@app.route('/voloservices/requestform/<requestid>',methods=['DELETE'])
def deleteRequest(requestid):
    partition_key = 'request'
    document_key = requestid
    my_document = _requestData[':'.join((partition_key, document_key))]
    my_document.delete()
    return "RequestForm " + requestid + " Deleted!"

port = int(os.getenv('PORT', 8080))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port, debug=False)


# When shutting down the app server, use ``client.disconnect()`` to properly
# logout and end the ``client`` session
@atexit.register
def shutdown():
   client.disconnect()
