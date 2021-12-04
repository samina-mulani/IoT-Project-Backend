# Required imports
import os
import random
from flask import Flask, request, jsonify, render_template
from sqlalchemy.sql.functions import user
from models import RegistrationInfo, setup_db, LocationUpdates, db_drop_and_create_all
import json
from sqlalchemy import desc

from datetime import datetime

# import urllib

# Initialize Flask app
app = Flask(__name__)
if app.config["ENV"] == "production":
    app.config.from_object("config.ProductionConfig")
else:
    app.config.from_object("config.DevelopmentConfig")

setup_db(app)
# db_drop_and_create_all()

@app.route('/',methods=['GET'])
def mainPage():
    devices = RegistrationInfo.query.all()
    devicelist = []
    lcnlist = []
    for idx,device in enumerate(devices):
        devicelist.append(RegistrationInfo.columns_to_dict(device))
        recentLocationUpdate = LocationUpdates.query.filter_by(deviceAddress=device.deviceAddress).order_by(desc(LocationUpdates.timestamp)).first()
        lcnlist.append(LocationUpdates.columns_to_dict(recentLocationUpdate))
    info = zip(devicelist,lcnlist)
    return render_template('index.html', devices = info)

@app.template_filter()
def format_timestamp(timestamp):
    date_time = datetime.fromtimestamp(timestamp)
    return date_time.strftime("%d/%m/%Y, %H:%M:%S")   

@app.route('/viewRegisteredDevices', methods=['GET'])
def getRegisteredDevices():
    devices = RegistrationInfo.query.all()
    devicedict = {}
    for idx,device in enumerate(devices):
        devicedict[idx] = RegistrationInfo.columns_to_dict(device)
    return jsonify(devicedict), 200   

@app.route('/viewLocationUpdates', methods=['GET'])
def getLocationUpdates():
    lcns = LocationUpdates.query.all()
    lcndict = {}
    for idx,lcn in enumerate(lcns):
        lcndict[idx] = LocationUpdates.columns_to_dict(lcn)
    return jsonify(lcndict), 200

# Sample object
# {
#   "deviceAddress": "C:54:91:88:C9:E3",
#   "deviceName": "Sample device",
#   "ownerName": "Samina",
#   "ownerNumber": "8792852130",
#   "ownerEmail": "samina00@gmail.com",
#   "timestamp": "1638453",
#   "latitude": "28.3802",
#   "longitude": "75.6092"
# }
@app.route('/registerDevice', methods=['POST'])
def registerDevice():
    jsonData = request.json
    deviceAddress = request.json['deviceAddress']
    deviceName = request.json['deviceName']
    ownerName = request.json['ownerName']
    ownerNumber = request.json['ownerNumber']
    ownerEmail = request.json['ownerEmail']
    timestamp = request.json['timestamp']
    timestamp = int(timestamp)
    latitude = request.json['latitude']
    longitude = request.json['longitude']
    if deviceName is None or not deviceName:
        deviceName = 'N/A'
    if deviceAddress is None or ownerName is None or ownerNumber is None or ownerEmail is None or timestamp is None or latitude is None or longitude is None:
        return json.dumps({"msg": "All required info not present"}), 400
    newRegisteredDevice = RegistrationInfo(deviceAddress, deviceName, ownerName, ownerNumber, ownerEmail, timestamp)
    newLocationUpdate = LocationUpdates(deviceAddress, deviceName, ownerName, ownerNumber, ownerEmail, timestamp, latitude, longitude)
    RegistrationInfo.insert(newRegisteredDevice)
    LocationUpdates.insert(newLocationUpdate)
    return json.dumps({"msg": "Success"}), 200

@app.route('/sendLocationUpdate', methods=['POST'])
def sendLocationUpdate():
    deviceAddress = request.json['deviceAddress']
    deviceName = request.json['deviceName']
    updaterName = request.json['updaterName']
    updaterNumber = request.json['updaterNumber']
    updaterEmail = request.json['updaterEmail']
    timestamp = request.json['timestamp']
    timestamp = int(timestamp)
    latitude = request.json['latitude']
    longitude = request.json['longitude']
    if deviceName is None or not deviceName:
        deviceName = 'N/A'
    if deviceAddress is None or updaterName is None or updaterNumber is None or updaterEmail is None or timestamp is None or latitude is None or longitude is None:
        return json.dumps({"msg": "All required info not present"}), 400
    newLocationUpdate = LocationUpdates(deviceAddress, deviceName, updaterName, updaterNumber, updaterEmail, timestamp, latitude, longitude)
    LocationUpdates.insert(newLocationUpdate)
    return json.dumps({"msg": "Success"}), 200

@app.route('/getLocation',methods=['GET'])
def getLocation():
    deviceAddress = request.args.get('deviceAddress')
    
    if deviceAddress is None:
        return json.dumps({"msg":"All required info not present"}), 400
    deviceInfo = RegistrationInfo.query.filter_by(deviceAddress=deviceAddress).first()

    recentLocationUpdate = LocationUpdates.query.filter_by(deviceAddress=deviceAddress).order_by(desc(LocationUpdates.timestamp)).first()
    
    if deviceInfo is None or recentLocationUpdate is None:
        return json.dumps({"msg": "No device or location present in database"}), 500
    
    response = {
    "deviceAddress": recentLocationUpdate.deviceAddress,
    "latitude": recentLocationUpdate.latitude,
    "longitude": recentLocationUpdate.longitude,
    "updaterName": recentLocationUpdate.updaterName,
    "updaterEmail": recentLocationUpdate.updaterEmail,
    "updaterNumber": recentLocationUpdate.updaterNumber,
    "timestamp": str(recentLocationUpdate.timestamp)
    }
    return json.dumps(response), 200

@app.route('/getListRegistered', methods=['GET'])
def getList():
    devices = RegistrationInfo.query.all()
    myList = []
    for device in devices:
        myList.append(device.deviceAddress)
    return json.dumps({"list": myList}), 200

@app.route('/delete', methods=['GET'])
def deleteAll():
    deviceAddress = request.args.get('deviceAddress')
    device = RegistrationInfo.query.filter_by(deviceAddress=deviceAddress).first();
    if device is not None:
        RegistrationInfo.delete(device)
    lcnUpdates = LocationUpdates.query.filter_by(deviceAddress=deviceAddress)
    for idx,update in enumerate(lcnUpdates):
        LocationUpdates.delete(update)
    return "Success", 200