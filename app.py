import os
import json
import logging
import numpy as np
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from sklearn.linear_model import LinearRegression
from werkzeug.middleware.proxy_fix import ProxyFix

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Create the Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Load hostel data from JSON
def load_hostel_data():
    try:
        with open('static/data/hostels.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        # If file doesn't exist, create it with sample data
        hostels = generate_hostel_data()
        with open('static/data/hostels.json', 'w') as f:
            json.dump(hostels, f, indent=4)
        return hostels

def generate_hostel_data():
    """Generate initial hostel data for the application"""
    return {
        "hostels": [
            {
                "id": 1,
                "name": "Sunshine Girls Hostel",
                "type": "hostel",
                "rent": 8000,
                "room_type": ["single", "double"],
                "amenities": ["food", "wifi", "laundry", "AC", "gym"],
                "distance_from_college": 1.5,
                "safety_rating": 4.5,
                "cleanliness": 4.2,
                "reviews_count": 120,
                "avg_rating": 4.3,
                "address": "123 College Road",
                "contact": "9876543210",
                "image_url": "https://images.unsplash.com/photo-1555854877-bab0e564b8d5?ixlib=rb-4.0.3",
                "colleges_nearby": ["Delhi University", "IP University"]
            },
            {
                "id": 2,
                "name": "Comfort PG for Ladies",
                "type": "PG",
                "rent": 7000,
                "room_type": ["double", "shared"],
                "amenities": ["food", "wifi", "laundry"],
                "distance_from_college": 0.8,
                "safety_rating": 4.0,
                "cleanliness": 3.8,
                "reviews_count": 85,
                "avg_rating": 3.9,
                "address": "45 Park Street",
                "contact": "9876543211",
                "image_url": "https://images.unsplash.com/photo-1522771739844-6a9f6d5f14af?ixlib=rb-4.0.3",
                "colleges_nearby": ["Delhi University", "JNU"]
            },
            {
                "id": 3,
                "name": "Elite Women's Residence",
                "type": "hostel",
                "rent": 12000,
                "room_type": ["single"],
                "amenities": ["food", "wifi", "laundry", "AC", "gym", "swimming pool"],
                "distance_from_college": 2.5,
                "safety_rating": 4.8,
                "cleanliness": 4.7,
                "reviews_count": 200,
                "avg_rating": 4.6,
                "address": "78 Luxury Avenue",
                "contact": "9876543212",
                "image_url": "https://images.unsplash.com/photo-1611892440504-42a792e24d32?ixlib=rb-4.0.3",
                "colleges_nearby": ["Delhi University", "IIT Delhi"]
            },
            {
                "id": 4,
                "name": "Budget Girls PG",
                "type": "PG",
                "rent": 5000,
                "room_type": ["shared"],
                "amenities": ["wifi", "laundry"],
                "distance_from_college": 3.0,
                "safety_rating": 3.5,
                "cleanliness": 3.2,
                "reviews_count": 60,
                "avg_rating": 3.4,
                "address": "120 Economy Lane",
                "contact": "9876543213",
                "image_url": "https://images.unsplash.com/photo-1595526114035-0d45ed16cfbf?ixlib=rb-4.0.3",
                "colleges_nearby": ["IP University", "Jamia Millia Islamia"]
            },
            {
                "id": 5,
                "name": "Serene Sisters Hostel",
                "type": "hostel",
                "rent": 9000,
                "room_type": ["single", "double"],
                "amenities": ["food", "wifi", "laundry", "AC"],
                "distance_from_college": 1.2,
                "safety_rating": 4.3,
                "cleanliness": 4.0,
                "reviews_count": 150,
                "avg_rating": 4.2,
                "address": "56 Serenity Road",
                "contact": "9876543214",
                "image_url": "https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?ixlib=rb-4.0.3",
                "colleges_nearby": ["JNU", "IP University"]
            },
            {
                "id": 6,
                "name": "Campus Corner PG",
                "type": "PG",
                "rent": 6500,
                "room_type": ["double", "shared"],
                "amenities": ["food", "wifi"],
                "distance_from_college": 0.5,
                "safety_rating": 3.8,
                "cleanliness": 3.6,
                "reviews_count": 90,
                "avg_rating": 3.7,
                "address": "10 Campus Road",
                "contact": "9876543215",
                "image_url": "https://images.unsplash.com/photo-1533090161767-e6ffed986c88?ixlib=rb-4.0.3",
                "colleges_nearby": ["Delhi University", "IP University"]
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
    all_amenities = ["food", "wifi", "laundry", "AC", "gym", "swimming pool"]
    
    # Extract features from hostels
    X = []
    for hostel in hostels:
        # Basic features
        rent_match = 1 if hostel["rent"] <= preferences["budget"] else 0
        room_match = map_room_type(hostel["room_type"], preferences["room_type"])
        type_match = 1 if hostel["type"] == preferences["hostel_type"] else 0
        
        # College match (weight: how close the hostel is to preferred college)
        college_match = 1 if preferences["college"] in hostel["colleges_nearby"] else 0
        
        # Amenities
        amenities_features = map_amenities(hostel["amenities"], all_amenities)
        
        # Safety and cleanliness are important factors
        safety = hostel["safety_rating"] / 5.0  # Normalize to 0-1
        cleanliness = hostel["cleanliness"] / 5.0  # Normalize to 0-1
        
        # Combine all features
        features = [rent_match, room_match, type_match, college_match, 
                    safety, cleanliness]
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
        "safety": 0.15,
        "cleanliness": 0.1,
        "amenities": 0.15  # Split among all amenities
    }
    
    all_amenities = ["food", "wifi", "laundry", "AC", "gym", "swimming pool"]
    amenity_weight = weights["amenities"] / len(all_amenities)
    
    preferred_amenities = preferences.get("amenities", [])
    
    scores = []
    for hostel in hostels:
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
        
        # College match
        if preferences["college"] in hostel["colleges_nearby"]:
            score += weights["college_match"]
        
        # Safety and cleanliness
        score += weights["safety"] * (hostel["safety_rating"] / 5.0)
        score += weights["cleanliness"] * (hostel["cleanliness"] / 5.0)
        
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

@app.route('/')
def index():
    return render_template('index.html')

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
