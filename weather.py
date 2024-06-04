#weather.py
from flask import Flask, render_template, request
import requests
from datetime import datetime

app = Flask(__name__)
api_key = '0dbafd19fb31e198e2ed51d414bde931'

def get_weather_data(city_name, api_key):
    url = f'http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={api_key}&units=metric&lang=kr'
    response = requests.get(url)
    return response.json()

@app.route('/', methods=['GET', 'POST'])
def index():
    error_message = None  # 오류 메시지 변수 초기화
    weather_data = None  # 날씨 데이터 변수 초기화

    if request.method == 'POST':
        city = request.form['city']
        weather_data = get_weather_data(city, api_key)
        if weather_data['cod'] == 200:
            city_name = weather_data['name']
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            weather = weather_data['weather'][0]['description']
            feels_like = weather_data['main']['feels_like']
            temp_min = weather_data['main']['temp_min']
            temp_max = weather_data['main']['temp_max']
            icon = weather_data['weather'][0]['icon']
            return render_template('index.html', city_name=city_name, current_time=current_time,
                                   weather=weather, feels_like=feels_like, temp_min=temp_min,
                                   temp_max=temp_max, icon=icon)
        else:
            error_message = "도시를 찾을 수 없습니다."

    return render_template('index.html', error_message=error_message, weather_data=weather_data)

if __name__ == '__main__':
    app.run(debug=True)
