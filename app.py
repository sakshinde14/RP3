import os
import json
import logging
import numpy as np
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from sklearn.linear_model import LinearRegression
from werkzeug.middleware.proxy_fix import ProxyFix
import pymongo
from pymongo import MongoClient
import certifi

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Create the Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# MongoDB connection (disabled for now, using JSON as fallback)
def get_db_connection():
    try:
        # The MongoDB connection string would typically be stored in an environment variable
        mongodb_uri = os.environ.get("MONGODB_URI")
        if mongodb_uri:
            client = MongoClient(mongodb_uri, tlsCAFile=certifi.where())
            return client.hostel_recommendation_db
        else:
            logging.warning("MongoDB URI not found. Using JSON data instead.")
            return None
    except Exception as e:
        logging.error(f"MongoDB connection error: {e}")
        return None

# Load hostel data from MongoDB or JSON as fallback
def load_hostel_data():
    # Try to load from MongoDB first
    db = get_db_connection()
    if db:
        try:
            # Get all hostels from MongoDB
            hostels_list = list(db.hostels.find({}, {'_id': 0}))
            if hostels_list:
                return {"hostels": hostels_list}
        except Exception as e:
            logging.error(f"Error retrieving data from MongoDB: {e}")
    
    # Fallback to JSON
    try:
        with open('static/data/hostels.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        # If file doesn't exist, create it with sample data
        hostels = generate_hostel_data()
        with open('static/data/hostels.json', 'w') as f:
            json.dump(hostels, f, indent=4)
        return hostels

# Load initial data into MongoDB (would be called once during setup)
def load_data_to_mongodb():
    db = get_db_connection()
    if not db:
        return False
    
    # Check if data already exists
    if db.hostels.count_documents({}) == 0:
        try:
            # Load from JSON
            with open('static/data/hostels.json', 'r') as f:
                hostels_data = json.load(f)
            
            # Insert into MongoDB
            db.hostels.insert_many(hostels_data["hostels"])
            logging.info("Data successfully loaded into MongoDB")
            return True
        except Exception as e:
            logging.error(f"Error loading data into MongoDB: {e}")
            return False
    else:
        logging.info("MongoDB already contains hostel data")
        return True

def generate_hostel_data():
    """Generate initial hostel data for the application"""
    # This function is a fallback and shouldn't be needed if JSON file exists
    return {
        "hostels": [
            {
                "id": 1,
                "name": "Sunshine Girls Hostel",
                "type": "hostel",
                "rent": 8000,
                "room_type": ["single", "double"],
                "amenities": ["food", "wifi", "laundry", "AC", "security", "geyser", "attached_bathroom"],
                "safety_priority": 4.5,
                "rating": 4.3,
                "reviews_count": 120,
                "distance_to_college": 1.5,
                "address": "123 FC Road, Pune",
                "contact": "9876543210",
                "image_url": "https://images.unsplash.com/photo-1555854877-bab0e564b8d5?ixlib=rb-4.0.3",
                "colleges_nearby": ["Fergusson College", "Symbiosis College of Arts and Commerce"]
            }
        ]
    }

# Feature mapping helpers
def map_amenities(amenities_list, all_amenities):
    """Convert amenities list to binary features"""
    return [1 if amenity in amenities_list else 0 for amenity in all_amenities]

def map_room_type(room_types, preferred_type):
    """Check if preferred room type is available"""
    return 1 if preferred_type in room_types else 0

def preprocess_hostel_data(hostels, preferences):
    """Process hostel data to prepare for regression model"""
    all_amenities = ["food", "wifi", "laundry", "AC", "security", "geyser", 
                    "attached_bathroom", "CCTV", "RO_water", "parking", "cleaning", 
                    "fridge", "warden"]
    
    # Extract features from hostels
    X = []
    for hostel in hostels:
        # Basic features
        rent_match = 1 if hostel["rent"] <= preferences["budget"] else 0
        room_match = map_room_type(hostel["room_type"], preferences["room_type"])
        type_match = 1 if hostel["type"] == preferences["hostel_type"] else 0
        
        # College match (weight: how close the hostel is to preferred college)
        college_match = 1 if preferences["college"] in hostel["colleges_nearby"] else 0
        distance_factor = 1 / (1 + hostel["distance_to_college"]) # Normalize distance (closer is better)
        
        # Amenities
        amenities_features = map_amenities(hostel["amenities"], all_amenities)
        
        # Safety is an important factor for female students
        safety = hostel["safety_priority"] / 5.0  # Normalize to 0-1
        rating = hostel["rating"] / 5.0  # Normalize to 0-1
        
        # Combine all features
        features = [rent_match, room_match, type_match, college_match, 
                    distance_factor, safety, rating]
        features.extend(amenities_features)
        
        X.append(features)
    
    return np.array(X)

def calculate_suitability_scores(hostels, preferences):
    """Calculate suitability scores using linear regression"""
    # Simple weights for features (these would ideally be learned from data)
    weights = {
        "rent_match": 0.2,
        "room_match": 0.15,
        "type_match": 0.1,
        "college_match": 0.15,
        "distance_factor": 0.05,
        "safety": 0.15,
        "rating": 0.1,
        "amenities": 0.1  # Split among all amenities
    }
    
    all_amenities = ["food", "wifi", "laundry", "AC", "security", "geyser", 
                    "attached_bathroom", "CCTV", "RO_water", "parking", "cleaning", 
                    "fridge", "warden"]
    amenity_weight = weights["amenities"] / len(all_amenities)
    
    preferred_amenities = preferences.get("amenities", [])
    
    scores = []
    for hostel in hostels:
        # First filter: Only consider hostels near the chosen college
        if preferences["college"] not in hostel["colleges_nearby"]:
            continue
            
        score = 0
        
        # Budget match (penalize if over budget)
        if hostel["rent"] <= preferences["budget"]:
            score += weights["rent_match"]
        else:
            # Apply penalty proportional to how much over budget
            overage_ratio = min(1, (hostel["rent"] - preferences["budget"]) / preferences["budget"])
            score -= weights["rent_match"] * overage_ratio
        
        # Room type match
        if preferences["room_type"] in hostel["room_type"]:
            score += weights["room_match"]
        
        # Hostel type match
        if hostel["type"] == preferences["hostel_type"]:
            score += weights["type_match"]
        
        # College match and distance
        score += weights["college_match"]
        distance_factor = 1 / (1 + hostel["distance_to_college"])
        score += weights["distance_factor"] * distance_factor
        
        # Safety and rating - important for female students
        score += weights["safety"] * (hostel["safety_priority"] / 5.0)
        score += weights["rating"] * (hostel["rating"] / 5.0)
        
        # Amenities match
        for amenity in preferred_amenities:
            if amenity in hostel["amenities"]:
                score += amenity_weight
        
        # Normalize score to 0-100
        normalized_score = min(100, max(0, score * 100))
        
        scores.append({
            "hostel": hostel,
            "score": round(normalized_score, 1)
        })
    
    # Sort by score in descending order
    scores.sort(key=lambda x: x["score"], reverse=True)
    return scores

@app.route('/preference-form')
def preference_form():
    # Get list of unique colleges from hostel data
    hostels = load_hostel_data()["hostels"]
    colleges = set()
    for hostel in hostels:
        colleges.update(hostel["colleges_nearby"])
    
    return render_template('preference_form.html', colleges=sorted(list(colleges)))

@app.route('/submit-preferences', methods=['POST'])
def submit_preferences():
    preferences = {
        "college": request.form.get('college'),
        "budget": int(request.form.get('budget')),
        "room_type": request.form.get('room_type'),
        "hostel_type": request.form.get('hostel_type'),
        "amenities": request.form.getlist('amenities')
    }
    
    # Save preferences in session
    session['preferences'] = preferences
    
    return redirect(url_for('recommendations'))

@app.route('/recommendations')
def recommendations():
    if 'preferences' not in session:
        flash('Please fill out the preference form first')
        return redirect(url_for('preference_form'))
    
    preferences = session['preferences']
    hostels_data = load_hostel_data()
    hostels = hostels_data["hostels"]
    
    # Calculate suitability scores
    scored_hostels = calculate_suitability_scores(hostels, preferences)
    
    return render_template('recommendations.html', 
                           recommendations=scored_hostels,
                           preferences=preferences)

@app.route('/api/get_recommendations', methods=['POST'])
def api_get_recommendations():
    """API endpoint to get recommendations (for potential React frontend)"""
    try:
        data = request.get_json()
        
        preferences = {
            "college": data.get('college'),
            "budget": int(data.get('budget')),
            "room_type": data.get('room_type'),
            "hostel_type": data.get('hostel_type'),
            "amenities": data.get('amenities', [])
        }
        
        hostels_data = load_hostel_data()
        hostels = hostels_data["hostels"]
        
        # Calculate suitability scores
        scored_hostels = calculate_suitability_scores(hostels, preferences)
        
        # Convert to simpler format for API response
        response = []
        for item in scored_hostels:
            hostel = item["hostel"]
            response.append({
                "id": hostel["id"],
                "name": hostel["name"],
                "type": hostel["type"],
                "rent": hostel["rent"],
                "room_type": hostel["room_type"],
                "amenities": hostel["amenities"],
                "safety_priority": hostel["safety_priority"],
                "rating": hostel["rating"],
                "distance_to_college": hostel["distance_to_college"],
                "address": hostel["address"],
                "contact": hostel["contact"],
                "image_url": hostel["image_url"],
                "colleges_nearby": hostel["colleges_nearby"],
                "score": item["score"]
            })
        
        return jsonify({"recommendations": response})
    except Exception as e:
        logging.error(f"API error: {e}")
        return jsonify({"error": str(e)}), 400

# Initialize MongoDB with a function to be called from routes
def initialize_db():
    try:
        load_data_to_mongodb()
    except Exception as e:
        logging.error(f"Error initializing database: {e}")

# Call initialize_db from the index route to ensure it runs
@app.route('/')
def index():
    # Initialize DB on first request
    initialize_db()
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
