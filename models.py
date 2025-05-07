# This file is currently not used as we're using JSON for data storage
# In a production environment, we would use a database with proper models

"""
Example models that could be used if we switched to a database:

from app import db
from flask_login import UserMixin

class Hostel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # PG or hostel
    rent = db.Column(db.Integer, nullable=False)
    address = db.Column(db.String(500), nullable=False)
    contact = db.Column(db.String(20), nullable=False)
    safety_rating = db.Column(db.Float, nullable=False)
    cleanliness = db.Column(db.Float, nullable=False)
    reviews_count = db.Column(db.Integer, nullable=False, default=0)
    avg_rating = db.Column(db.Float, nullable=False, default=0)
    distance_from_college = db.Column(db.Float, nullable=True)
    
    # Relationships
    room_types = db.relationship('RoomType', backref='hostel', lazy=True)
    amenities = db.relationship('Amenity', backref='hostel', lazy=True)
    colleges_nearby = db.relationship('College', secondary='hostel_college', backref='hostels', lazy=True)

class RoomType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hostel_id = db.Column(db.Integer, db.ForeignKey('hostel.id'), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # single, double, shared

class Amenity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hostel_id = db.Column(db.Integer, db.ForeignKey('hostel.id'), nullable=False)
    name = db.Column(db.String(50), nullable=False)  # food, wifi, laundry, etc.

class College(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    
# Association table for many-to-many relationship between hostels and colleges
hostel_college = db.Table('hostel_college',
    db.Column('hostel_id', db.Integer, db.ForeignKey('hostel.id'), primary_key=True),
    db.Column('college_id', db.Integer, db.ForeignKey('college.id'), primary_key=True)
)
"""
