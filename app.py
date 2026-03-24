from dotenv import load_dotenv
import os
from flask import Flask, render_template, request
import requests
load_dotenv() # Load environment variables from .env file
API_KEY = os.getenv("API_KEY") # Get API key from environment variable

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    cafes =[]
    location = None
    error = None

    if request.method == 'POST':
        location = request.form.get('location')
        if not location:
            error = "Please enter a location."
        elif not API_KEY:
            error = "API key is not configured. Please set API_KEY in your .env file."
        else:
            geo_url = "https://maps.googleapis.com/maps/api/geocode/json"
            geo_params = {
                "address": location,
                "key": API_KEY
            }
            try:
                geo_response = requests.get(geo_url, params=geo_params).json()
            except requests.exceptions.RequestException:
                error = "Failed to connect to the geocoding service."
                return render_template('index.html', location=location, cafes=cafes, error=error)
            if geo_response.get("results"):
                lat = geo_response["results"][0]["geometry"]["location"]["lat"]
                lng = geo_response["results"][0]["geometry"]["location"]["lng"]

                places_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
                places_params = {
                    "location" : f"{lat},{lng}",
                    "radius" : 6000,
                    "type" : "cafe",
                    "key": API_KEY,
                }
                try:
                    places_response = requests.get(places_url, params=places_params).json()
                except requests.exceptions.RequestException:
                    error = "Failed to connect to the places service."
                    return render_template('index.html', location=location, cafes=cafes, error=error)

                if places_response.get("results"):
                    for place in places_response["results"]:
                        photo_url = None

                        if place.get("photos"):
                            photo_reference = place["photos"][0]["photo_reference"]
                            photo_url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference={photo_reference}&key={API_KEY}"

                        cafes.append({
                            "name": place["name"],
                            "address": place.get("vicinity", "N/A"),
                            "rating": place.get("rating", "N/A"),
                            "photo" : photo_url
                        })
            else:
                error = "Could not find that location. Please try a different search."

    return render_template('index.html', location=location, cafes=cafes, error=error)
if __name__ == '__main__':
    app.run(debug=True)
    app.run(host='0.0.0.0', port=10000)

