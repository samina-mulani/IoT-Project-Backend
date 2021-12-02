import os
from sqlalchemy import Column, String, Integer, create_engine
from sqlalchemy.sql.expression import null
from sqlalchemy.sql.sqltypes import Boolean
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import ARRAY

db = SQLAlchemy()
'''
setup_db(app):
    binds a flask application and a SQLAlchemy service
'''
def setup_db(app):
    database_name ='iotProject'
    default_database_path= "postgresql://{}:{}@{}/{}".format('postgres', 'blackCatsRule374', 'localhost:5432', database_name)
    database_path = os.getenv('DATABASE_URL', default_database_path)
    if database_path.startswith("postgres://"):
        database_path = database_path.replace("postgres://", "postgresql://", 1)
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
'''
    drops the database tables and starts fresh
    can be used to initialize a clean database
'''
def db_drop_and_create_all():
    db.drop_all()
    db.create_all()

class RegistrationInfo(db.Model):
    __tablename__ = 'registration_info'
    deviceAddress = Column(String, primary_key=True)
    deviceName = Column(String, nullable=True)
    ownerName = Column(String, nullable=False)
    ownerNumber = Column(String, nullable=False)
    ownerEmail = Column(String, nullable=False)
    timestamp = Column(Integer, nullable=False)

    def __init__(self, deviceAddres, deviceName, ownerName, ownerNumber, ownerEmail, timestamp):
        self.deviceAddres = deviceAddres
        self.deviceName = deviceName
        self.ownerName = ownerName
        self.ownerNumber = ownerNumber
        self.ownerEmail = ownerEmail
        self.timestamp = timestamp

    def columns_to_dict(self):
        dict_ = {}
        for key in self.__mapper__.c.keys():
            dict_[key] = getattr(self, key)
        return dict_

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def update(self):
        db.session.commit()

class LocationUpdates(db.Model):
    __tablename__ = 'location_updates'
    pk = Column(Integer, primary_key=True)
    deviceAddres = Column(String)
    deviceName = Column(String, nullable=True)
    updaterName = Column(String, nullable=False)
    updaterNumber = Column(String, nullable=False)
    updaterEmail = Column(String, nullable=False)
    timestamp = Column(Integer, nullable=False)
    latitude = Column(String, nullable=False)
    longitude = Column(String, nullable=False)

    def __init__(self, deviceAddres, deviceName, updaterName, updaterNumber, updaterEmail, timestamp, latitude, longitude):
        self.deviceAddres = deviceAddres
        self.deviceName = deviceName
        self.updaterName = updaterName
        self.updaterNumber = updaterNumber
        self.updaterEmail = updaterEmail
        self.timestamp = timestamp
        self.latitude = latitude
        self.longitude = longitude

    def columns_to_dict(self):
        dict_ = {}
        for key in self.__mapper__.c.keys():
            dict_[key] = getattr(self, key)
        return dict_

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def update(self):
        db.session.commit()
