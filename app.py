# app.py

# Required imports
import os
import random
from flask import Flask, request, jsonify
from sqlalchemy.sql.functions import user
from models import RegistrationInfo, setup_db, LocationUpdates, db_drop_and_create_all

# import urllib

# Initialize Flask app
app = Flask(__name__)
if app.config["ENV"] == "production":
    app.config.from_object("config.ProductionConfig")
else:
    app.config.from_object("config.DevelopmentConfig")

setup_db(app)
db_drop_and_create_all()

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

@app.route('/registerDevice', methods=['POST'])
def registerDevice():
    jsonData = request.json
    deviceAddress = request.args.get('deviceAddress')
    deviceName = request.args.get('deviceName')
    ownerName = request.args.get('ownerName')
    ownerNumber = request.args.get('ownerNumber')
    ownerEmail = request.args.get('ownerEmail')
    timestamp = request.args.get('timestamp')
    latitude = request.args.get('latitude')
    longitude = request.args.get('longitude')
    if deviceName is None or not deviceName:
        deviceName = 'N/A'
    if deviceAddress is None or ownerName is None or ownerNumber is None or ownerEmail is None or timestamp is None or latitude is None or longitude is None:
        return json.dumps({"msg": "All required info not present"}), 400
    newRegisteredDevice = RegistrationInfo(deviceAddres, deviceName, ownerName, ownerNumber, ownerEmail, timestamp)
    newLocationUpdate = LocationUpdates(deviceAddres, deviceName, ownerName, ownerNumber, ownerEmail, timestamp, latitude, longitude)
    RegistrationInfo.insert(newRegisteredDevice)
    LocationUpdates.insert(newLocationUpdate)
    return json.dumps({"msg": "Success"}), 200

@app.route('/sendLocationUpdate', methods=['POST'])
def sendLocationUpdate():
    deviceAddress = request.args.get('deviceAddress')
    deviceName = request.args.get('deviceName')
    updaterName = request.args.get('updaterName')
    updaterNumber = request.args.get('updaterNumber')
    updaterEmail = request.args.get('updaterEmail')
    timestamp = request.args.get('timestamp')
    latitude = request.args.get('latitude')
    longitude = request.args.get('longitude')
    if deviceName is None or not deviceName:
        deviceName = 'N/A'
    if deviceAddress is None or updaterName is None or updaterNumber is None or updaterEmail is None or timestamp is None or latitude is None or longitude is None:
        return json.dumps({"msg": "All required info not present"}), 400
    newLocationUpdate = LocationUpdates(deviceAddres, deviceName, updaterName, updaterNumber, updaterEmail, timestamp, latitude, longitude)
    LocationUpdates.insert(newLocationUpdate)
    return json.dumps({"msg": "Success"}), 200

@app.route('/getLocation',methods=['GET'])
def getLocation():
    deviceAddress = request.args.get('deviceAddress')
    deviceInfo = RegistrationInfo.query.filter_by(deviceAddress=deviceAddress).first()
    recentLocationUpdate = LocationUpdates.query.filter_by(deviceAddress=deviceAddress).order_by(desc(LocationUpdates.timestamp))
    
    if deviceInfo is None or recentLocationUpdate is None:
        return json.dumps({"msg": "No device or location present in database"}), 500
    
    response = {
    "deviceAddress": recentLocationUpdate.deviceAddress,
    "latitude": recentLocationUpdate.latitude,
    "longitude": recentLocationUpdate.longitude,
    "updaterName": recentLocationUpdate.updaterName,
    "updaterEmail": recentLocationUpdate.updaterEmail,
    "updaterNumber": recentLocationUpdate.updaterNumber,
    "timestamp": recentLocationUpdate.timestamp
    }
    return json.dumps(response), 200

    #get global list of devices