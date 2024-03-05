from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import firebase_admin
from firebase_admin import db, credentials
from flask import Flask, render_template
import folium
import firebase_admin
from firebase_admin import db, credentials

cred = credentials.Certificate("firebase_cred.json")
firebase_admin.initialize_app(
    cred, {"databaseURL": "https://h4h2024-300a6-default-rtdb.firebaseio.com/"})
app = Flask(__name__, template_folder='template')

location_cordinates = {}
CORS(app)

activities = []

# @app.route('/', methods=['POST'])


@app.route('/login', methods=['POST'])
def login():
    # In a real application, you would validate the username and password
    # against a database or some other form of authentication.
    data = request.json
    print(data)
    if data['username'] == 'admin' and data['password'] == 'password':
        return jsonify({'message': 'Login successful'})
    else:
        return jsonify({'message': 'Invalid username or password'}), 401


@app.route('/new-activity', methods=['POST'])
def create_activity():
    data = request.json
    print(data)
    # Extract individual fields from the activity data
    event_name = data['newActivity'].get('eventName')
    event_description = data['newActivity'].get('eventDescription')
    event_date = data['newActivity'].get('eventDate')
    event_time = data['newActivity'].get('eventTime')
    location = data['newActivity'].get('location')
    audience = data['newActivity'].get('audience')

    # Create a new activity dictionary
    activity = {
        'eventName': event_name,
        'eventDescription': event_description,
        'eventDate': event_date,
        'eventTime': event_time,
        'location': location,
        'audience': audience
    }
    activities.append(activity)
    if event_name != None:
        print(event_description)
        print("if")
        db.reference("/"+event_name).update({"event_desc": event_description, "event_date": event_date,
                                             "event_time": event_time, "event_loc": location, "event_aud": audience})
        return jsonify({'message': event_name + ' Activity created successfully'})
    else:
        print("else")
        return jsonify({'error': 'Invalid activity name'}), 400

    # return jsonify({'message': 'Activity created successfully'})
    # activity_name = data['newActivity']


@app.route('/eventlist')
def index():
    # Latitude and longitude values for the locations
    ref = db.reference("/")
    event_deets = ref.get()
    print(type(event_deets))

    location_cordinates = {
        "The Forge Garden": {"latitude": 37.352484, "longitude": -121.939357, "img": "template/forgegarden.jpg"},
        "City Plaza Park": {"latitude": 37.347664, "longitude": -121.945053, "img": "template/fremontpark.jpg"},
        "Mission Garden": {"latitude": 37.348883, "longitude": -121.941514, "img": "template/missiongarden.jpg"},
        "Santa Clara Farmers Market": {"latitude": 37.349678, "longitude": -121.947366, "img": "template/missionlibrary.jpg"},
        "Larry J. Marsalli Park": {"latitude": 37.35507, "longitude": -121.944549, "img": "template/missionlibrary.jpg"}
    }
    events = []
    i = 0
    for event in event_deets:
        print(event_deets)
        print(event, type(event))
        print(event_deets[event]['event_loc'])
        name = event.upper()
        event_details = f"<b>{name}</b><br>Venue: {event_deets[event]['event_loc']}<br>Date and Time: {event_deets[event]['event_date']} {event_deets[event]['event_time']}<br>What is it about?: {event_deets[event]['event_desc']}"
        d = {'event_details': event_details, 'latitude': location_cordinates[event_deets[event]['event_loc']]['latitude'], 'longitude': location_cordinates[
            event_deets[event]['event_loc']]['longitude'], 'img': location_cordinates[event_deets[event]['event_loc']]['img']}
        print(event_details)
        events.append(d)
        i += 1

    print(events)

    # Create a folium map centered around the mean of the given latitude and longitude
    map = folium.Map(location=[sum(loc['latitude'] for loc in events) / i,
                               sum(loc['longitude'] for loc in events) / i],
                     zoom_start=16)

    # Add markers for each location to the map
    for loc in events:
        folium.Marker(location=[loc['latitude'], loc['longitude']],
                      popup=folium.Popup(loc['event_details'], max_width=200),
                      icon=folium.CustomIcon(loc['img'], icon_size=(90, 90))).add_to(map)

    # Save the map to a HTML file
    map.save('template/example.html')

    # Render the HTML template containing the map
    return render_template('example.html')


if __name__ == '__main__':
    app.run(debug=True)
