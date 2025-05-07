# This file is currently not used as we're using JSON for data storage
# In a production environment, we would use a database with proper models

from app import db
from sqlalchemy.dialects.postgresql import ARRAY

# Association table for many-to-many relationship between hostels and colleges
hostel_college = db.Table('hostel_college',
    db.Column('hostel_id', db.Integer, db.ForeignKey('hostel.id'), primary_key=True),
    db.Column('college_id', db.Integer, db.ForeignKey('college.id'), primary_key=True)
)

# Association table for many-to-many relationship between hostels and room types
hostel_room_type = db.Table('hostel_room_type',
    db.Column('hostel_id', db.Integer, db.ForeignKey('hostel.id'), primary_key=True),
    db.Column('room_type_id', db.Integer, db.ForeignKey('room_type.id'), primary_key=True)
)

# Association table for many-to-many relationship between hostels and amenities
hostel_amenity = db.Table('hostel_amenity',
    db.Column('hostel_id', db.Integer, db.ForeignKey('hostel.id'), primary_key=True),
    db.Column('amenity_id', db.Integer, db.ForeignKey('amenity.id'), primary_key=True)
)

class College(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, unique=True)

class RoomType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50), nullable=False, unique=True)  # single, double, shared

class Amenity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)  # food, wifi, laundry, etc.

class Hostel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # PG or hostel
    rent = db.Column(db.Integer, nullable=False)
    address = db.Column(db.String(500), nullable=False)
    contact = db.Column(db.String(20), nullable=False)
    safety_priority = db.Column(db.Float, nullable=False)
    rating = db.Column(db.Float, nullable=False, default=0)
    reviews_count = db.Column(db.Integer, nullable=False, default=0)
    distance_to_college = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(500), nullable=True)
    
    # Relationships
    room_types = db.relationship('RoomType', secondary=hostel_room_type, backref=db.backref('hostels', lazy='dynamic'))
    amenities = db.relationship('Amenity', secondary=hostel_amenity, backref=db.backref('hostels', lazy='dynamic'))
    colleges_nearby = db.relationship('College', secondary=hostel_college, backref=db.backref('hostels', lazy='dynamic'))
    
    def to_dict(self):
        """Convert hostel object to dictionary for API responses"""
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "rent": self.rent,
            "room_type": [rt.type for rt in self.room_types],
            "amenities": [a.name for a in self.amenities],
            "safety_priority": self.safety_priority,
            "rating": self.rating,
            "reviews_count": self.reviews_count,
            "distance_to_college": self.distance_to_college,
            "address": self.address,
            "contact": self.contact,
            "image_url": self.image_url,
            "colleges_nearby": [c.name for c in self.colleges_nearby]
        }
