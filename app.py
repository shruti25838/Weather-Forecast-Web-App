from flask import Flask, render_template, request, redirect, url_for, make_response, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
import requests
import datetime
import csv
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from googleapiclient.discovery import build

app = Flask(__name__)
YOUTUBE_API_KEY = "AIzaSyA0X5wLQIDrHZwcKV6BDGaaU-l2rwts6oo"  # Replace with your API
API_KEY = "7df2bc3acc83410185991151250408"  # Replace with your WeatherAPI key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weather.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# === DATABASE MODEL ===
class SavedWeather(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.String(100), nullable=False)
    date = db.Column(db.String(20), nullable=False)
    temperature = db.Column(db.Float, nullable=False)
    condition = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"<SavedWeather {self.location} on {self.date}>"

with app.app_context():
    db.create_all()

def get_weather_videos(query):
    youtube_url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "q": f"weather in {query}",
        "type": "video",
        "maxResults": 5,
        "key": YOUTUBE_API_KEY
    }
    try:
        response = requests.get(youtube_url, params=params)
        if response.status_code == 200:
            videos = response.json().get("items", [])
            parsed_videos = [
                {
                    "title": video["snippet"]["title"],
                    "thumbnail": video["snippet"]["thumbnails"]["medium"]["url"],
                    "video_id": video["id"]["videoId"]
                }
                for video in videos
            ]
            print("Fetched videos:", parsed_videos)  # Debug log
            return parsed_videos
        else:
            print("YouTube API error:", response.status_code)
            return []
    except Exception as e:
        print("YouTube API exception:", e)
        return []

@app.route("/", methods=["GET", "POST"])
def index():
    weather = None
    videos = None

    if request.method == "POST" and "search" in request.form:
        location = request.form.get("location")
        if location:
            url = f"http://api.weatherapi.com/v1/forecast.json?key={API_KEY}&q={location}&days=5&aqi=no&alerts=no"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                weather = {
                    "location": f"{data['location']['name']}, {data['location']['country']}",
                    "temperature": data["current"]["temp_c"],
                    "description": data["current"]["condition"]["text"],
                    "icon": "https:" + data["current"]["condition"]["icon"],
                    "forecast": [
                        {
                            "date": day["date"],
                            "avg_temp": day["day"]["avgtemp_c"],
                            "condition": day["day"]["condition"]["text"],
                            "icon": "https:" + day["day"]["condition"]["icon"]
                        }
                        for day in data["forecast"]["forecastday"]
                    ]
                }
                videos = get_weather_videos(data['location']['name'])

    records = SavedWeather.query.order_by(SavedWeather.date.desc()).all()
    return render_template("index.html", weather=weather, records=records, videos=videos)

@app.route("/delete/<int:id>")
def delete(id):
    record = SavedWeather.query.get_or_404(id)
    db.session.delete(record)
    db.session.commit()
    return redirect(url_for('index'))

@app.route("/update/<int:id>", methods=["GET", "POST"])
def update(id):
    record = SavedWeather.query.get_or_404(id)
    if request.method == "POST":
        record.temperature = request.form.get("temperature")
        record.condition = request.form.get("condition")
        db.session.commit()
        return redirect(url_for("index"))
    return render_template("update.html", record=record)

@app.route("/export/json")
def export_json():
    records = SavedWeather.query.all()
    data = [
        {
            "location": r.location,
            "date": r.date,
            "temperature": r.temperature,
            "condition": r.condition
        }
        for r in records
    ]
    response = make_response(jsonify(data))
    response.headers["Content-Disposition"] = "attachment; filename=saved_weather.json"
    return response

@app.route("/export/csv")
def export_csv():
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Location", "Date", "Temperature (°C)", "Condition"])
    for r in SavedWeather.query.all():
        writer.writerow([r.location, r.date, r.temperature, r.condition])
    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = "attachment; filename=saved_weather.csv"
    response.headers["Content-type"] = "text/csv"
    return response

@app.route("/export/pdf")
def export_pdf():
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    y = 750
    p.setFont("Helvetica-Bold", 12)
    p.drawString(30, y, "Saved Weather Records")
    y -= 30
    p.setFont("Helvetica", 10)

    for r in SavedWeather.query.all():
        line = f"{r.date} - {r.location}: {r.temperature}°C, {r.condition}"
        p.drawString(30, y, line)
        y -= 20
        if y < 50:
            p.showPage()
            y = 750
            p.setFont("Helvetica", 10)

    p.save()
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name="saved_weather.pdf", mimetype='application/pdf')

if __name__ == "__main__":
    app.run(debug=True)
