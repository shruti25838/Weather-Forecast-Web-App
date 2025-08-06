# Weather Forecast App

This is a full-featured weather web app built using Flask, HTML/CSS, and SQLite. Users can access the current weather and 5-day forecast for any location, view YouTube videos related to weather in that area, save and edit forecast records, and export the data in JSON, CSV, or PDF format.

---

## Features

- Weather Search: Get current and 5-day forecast using city name or GPS location.
- YouTube Integration: Fetches weather-related videos for the searched location.
- Save Weather Records: Save temperature, date, and condition into a local database.
- View/Edit/Delete Records: Manage saved weather entries.
- Export Options: Export records as:
  - JSON
  - CSV
  - PDF (using ReportLab)
- Use My Location: Automatically fills location using browser GPS.

---

## Tech Stack

- Backend: Flask
- Frontend: HTML, CSS, JavaScript
- Database: SQLite (via SQLAlchemy)
- External APIs:
  - [WeatherAPI](https://www.weatherapi.com/)
  - [YouTube Data API v3](https://console.cloud.google.com/)

---

## Setup Instructions

### 1. Clone the Repository
git clone https://github.com/shruti25838/weather-app.git
cd weather-app

### 2. Install Requirements
pip install -r requirements.txt

### 3. Get Your API Keys
    a. WeatherAPI Key
    b. Go to https://www.weatherapi.com/
    c. Sign up and copy your API key
    d. Replace it in app.py:
    e. API_KEY = "your_weatherapi_key"

### 4.  YouTube Data API Key
    a. Go to https://console.cloud.google.com/
    b. Create a new project
    c. Enable YouTube Data API v3
    d. Go to Credentials → Create API Key
    e. Replace it in app.py:
    f. YOUTUBE_API_KEY = "your_youtube_api_key"

### 4. Run the App
python app.py

Then open your browser and go to:

http://127.0.0.1:5000/
