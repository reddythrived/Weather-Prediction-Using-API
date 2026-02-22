from flask import Flask, render_template, request
import requests
from datetime import datetime
from pytz import timezone

app = Flask(__name__)

API_KEY = "Your api key"

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        city = request.form.get("city")
        if not city:
            return render_template("index.html", error="Please enter a city name!")

        # Fetch current weather
        current_weather_url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
        response = requests.get(current_weather_url)
        if response.status_code != 200:
            return render_template("index.html", error="Error fetching current weather!")

        current_data = response.json()

        forecast_weather_url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric"
        response_forecast = requests.get(forecast_weather_url)
        if response_forecast.status_code != 200:
            return render_template("index.html", error="Error fetching forecast data!")

        forecast_data = response_forecast.json()

        # Process forecast data
        ist = timezone('Asia/Kolkata')  
        now = datetime.now(ist) 
        unique_dates = set() 
        forecast_list = []  

        for day in forecast_data['list']:
            # Parse the forecast timestamp (UTC)
            dt_obj_utc = datetime.strptime(day['dt_txt'], "%Y-%m-%d %H:%M:%S")
            # Convert UTC to IST
            dt_obj_ist = dt_obj_utc.replace(tzinfo=timezone('UTC')).astimezone(ist)

            # Only display forecasts for the next 3 days
            if dt_obj_ist > now and len(unique_dates) < 3:
                date_str = dt_obj_ist.strftime("%Y-%m-%d")
                if date_str not in unique_dates:
                    unique_dates.add(date_str)
                    forecast_list.append({
                        "date": date_str,
                        "time": dt_obj_ist.strftime("%Y-%m-%d %I:%M %p"),
                        "temp": day['main']['temp'],
                        "description": day['weather'][0]['description']
                    })

        return render_template("index.html", city=city, current_data=current_data, forecast_data=forecast_list)

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
