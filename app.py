import os
import json
import logging
import random
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

# MongoDB connection to your existing Atlas database
def get_db_connection():
    try:
        mongodb_uri = os.environ.get("MONGODB_URI", "mongodb+srv://sakshi:gaurinde@cluster0.vpbqv.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
        if mongodb_uri:
            client = MongoClient(mongodb_uri, tlsCAFile=certifi.where())
            return client.lrm  # Use the 'lrm' database you've created
        else:
            logging.warning("MongoDB URI not found. Using JSON data instead.")
            return None
    except Exception as e:
        logging.error(f"MongoDB connection error: {e}")
        return None

# Load hostel data from MongoDB or JSON as fallback
def load_hostel_data():
    db = get_db_connection()
    if db is not None:
        try:
            hostels_list = list(db.hinfo.find({}, {'_id': 0}))
            if hostels_list:
                transformed_hostels = []
                for hostel in hostels_list:
                    transformed_hostel = {
                        "id": hostel.get("hostel_id", hash(hostel["hostel_name"]) % 10000),
                        "name": hostel["hostel_name"],
                        "type": hostel["hostel_type"],
                        "rent": hostel["rent"],
                        "room_type": [hostel["room_type"].lower()],
                        "amenities": [a.lower().replace(" ", "_") for a in hostel["amenities"]],
                        "safety_priority": 5 if hostel["safety_priority"] == "High" else (3.5 if hostel["safety_priority"] == "Medium" else 2),
                        "rating": hostel["rating"],
                        "reviews_count": random.randint(50, 200),
                        "distance_to_college": float(hostel["distance_to_college"].split()[0]),
                        "address": hostel["address"],
                        "contact": hostel["contact_number"],
                        "image_url": f"https://images.unsplash.com/photo-{random.randint(1500000000, 1600000000)}-{random.randint(10000000, 99999999)}?ixlib=rb-4.0.3",
                        "colleges_nearby": [hostel["college"]]
                    }
                    transformed_hostels.append(transformed_hostel)

                logging.info(f"Loaded {len(transformed_hostels)} hostels from MongoDB")
                return {"hostels": transformed_hostels}
            else:
                logging.warning("No data found in MongoDB. Using JSON fallback.")
        except Exception as e:
            logging.error(f"Error retrieving data from MongoDB: {e}")

    try:
        with open('static/data/hostels.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        hostels = generate_hostel_data()
        with open('static/data/hostels.json', 'w') as f:
            json.dump(hostels, f, indent=4)
        return hostels

def load_data_to_mongodb():
    db = get_db_connection()
    if db is None:
        return False

    try:
        count = db.hinfo.count_documents({})
        logging.info(f"MongoDB contains {count} hostel records")
        return True
    except Exception as e:
        logging.error(f"Error checking MongoDB data: {e}")
        return False

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

def calculate_suitability_scores(hostels, preferences):
    """Calculate suitability scores for all relevant hostels, flagging exact matches."""
    perfect_matches = []
    other_hostels = []

    for hostel in hostels:
        if preferences["college"] not in hostel["colleges_nearby"]:
            continue
        if hostel["rent"] > preferences["budget"]:
            continue

        is_perfect_match = (
            preferences["room_type"].lower() in [rt.lower() for rt in hostel["room_type"]] and
            preferences["hostel_type"].lower() == hostel["type"].lower()
        )

        score = 0
        if is_perfect_match:
            score = 100.0
            perfect_matches.append({"hostel": hostel, "score": score})
        else:
            # Calculate a suitability score for other hostels based on other factors
            # (You can reuse your original scoring logic here or a simplified version)
            if hostel["rent"] <= preferences["budget"]:
                score += 20
            if preferences["room_type"].lower() in [rt.lower() for rt in hostel["room_type"]]:
                score += 15
            if preferences["hostel_type"].lower() == hostel["type"].lower():
                score += 10
            # Add weights for other factors like distance, safety, rating, amenities
            distance_factor = 1 / (1 + hostel["distance_to_college"])
            score += distance_factor * 10
            score += hostel["safety_priority"] * 5
            score += hostel["rating"] * 5
            # ... add more scoring for amenities if needed ...
            normalized_score = min(100, max(0, score))
            other_hostels.append({"hostel": hostel, "score": round(normalized_score, 1)})

    # Sort other hostels by score
    other_hostels.sort(key=lambda x: x["score"], reverse=True)

    return perfect_matches, other_hostels

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

    perfect_matches, other_hostels = calculate_suitability_scores(hostels, preferences)

    return render_template('recommendations_new.html',
                           perfect_matches=perfect_matches,
                           other_hostels=other_hostels,
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

        # Calculate suitability scores with strict filtering
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