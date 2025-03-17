import streamlit as st
import pandas as pd
import numpy as np
import requests
import datetime

#Сразу отвечая на вопрос, так как запросы к API небольшие, то как будто лучше использовать синхронные методы
#но из-за этого, как понимаю, прежде, чем вбить api код и получить мониторинг текущей температуры, 
#мы сначала ждем выполнения анализа временных рядов

seasonal_temperatures = {
    "New York": {"winter": 0, "spring": 10, "summer": 25, "autumn": 15},
    "London": {"winter": 5, "spring": 11, "summer": 18, "autumn": 12},
    "Paris": {"winter": 4, "spring": 12, "summer": 20, "autumn": 13},
    "Tokyo": {"winter": 6, "spring": 15, "summer": 27, "autumn": 18},
    "Moscow": {"winter": -10, "spring": 5, "summer": 18, "autumn": 8},
    "Sydney": {"winter": 12, "spring": 18, "summer": 25, "autumn": 20},
    "Berlin": {"winter": 0, "spring": 10, "summer": 20, "autumn": 11},
    "Beijing": {"winter": -2, "spring": 13, "summer": 27, "autumn": 16},
    "Rio de Janeiro": {"winter": 20, "spring": 25, "summer": 30, "autumn": 25},
    "Dubai": {"winter": 20, "spring": 30, "summer": 40, "autumn": 30},
    "Los Angeles": {"winter": 15, "spring": 18, "summer": 25, "autumn": 20},
    "Singapore": {"winter": 27, "spring": 28, "summer": 28, "autumn": 27},
    "Mumbai": {"winter": 25, "spring": 30, "summer": 35, "autumn": 30},
    "Cairo": {"winter": 15, "spring": 25, "summer": 35, "autumn": 25},
    "Mexico City": {"winter": 12, "spring": 18, "summer": 20, "autumn": 15},
}

month_to_season = {12: "winter", 1: "winter", 2: "winter",
                   3: "spring", 4: "spring", 5: "spring",
                   6: "summer", 7: "summer", 8: "summer",
                   9: "autumn", 10: "autumn", 11: "autumn"}

def generate_realistic_temperature_data(cities, num_years=10):
    dates = pd.date_range(start="2010-01-01", periods=365 * num_years, freq="D")
    data = []

    for city in cities:
        for date in dates:
            season = month_to_season[date.month]
            mean_temp = seasonal_temperatures[city][season]
            temperature = np.random.normal(loc=mean_temp, scale=5)
            data.append({"Город": city, "Временная шкала": date, "Температура": temperature})

    df = pd.DataFrame(data)
    df['season'] = df['timestamp'].dt.month.map(lambda x: month_to_season[x])
    return df

#для получения текущей температуры
def get_temperature(api_key, city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data['main']['temp']
    elif response.status_code == 401:
        return {" error": "Invalid API key. Please see https://openweathermap.org/faq#error401 for more info."}
    else:
        return None

def analyze_temp_data(df):
    seasonal_stats = df.groupby('season')['temperature'].agg(['mean', 'std']).reset_index()

    df['rolling_mean'] = df['temperature'].rolling(window=30).mean()
    df['rolling_std'] = df['temperature'].rolling(window=30).std()
    
    df['anomaly'] = ((df['temperature'] > df['rolling_mean'] + 2 * df['rolling_std']) |
                     (df['temperature'] < df['rolling_mean'] - 2 * df['rolling_std']))

    return seasonal_stats, df

def main():
    st.title("Анализ температурных данных")
    
    cities = list(seasonal_temperatures.keys())
    df = generate_realistic_temperature_data(cities)

    seasonal_stats, analyzed_data = analyze_temp_data(df)
    
    st.subheader("Статистика по сезонам")
    st.write(seasonal_stats)

    st.subheader("Анализ временных рядов")
    st.line_chart(analyzed_data[['timestamp', 'temperature', 'rolling_mean']].set_index('timestamp'))

    st.subheader("Мониторинг текущей температуры")
    api_key = st.text_input("Введите API ключ (c41bdb2001ec4723b2530c7d788d2e64)", "")
    city = st.selectbox("Выберите город", cities)

    if st.button("Получить текущую температуру"):
        current_temp = get_temperature(api_key, city)
        if current_temp is not None:
            season = month_to_season[datetime.datetime.now().month]
            normal_mean = seasonal_temperatures[city][season]
            normal_std = 5
            normal_range = (normal_mean - 2 * normal_std, normal_mean + 2 * normal_std)

            if response.status_code != 401:
                st.write(f"Текущая температура в {city}: {current_temp}°C")
                if normal_range[0] <= current_temp <= normal_range[1]:
                    st.write("Температура в пределах нормы")
                else:
                    st.write("Температура аномальная")

if __name__ == "__main__":
    main()
