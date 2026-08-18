import streamlit as st
from google import genai
from PIL import Image
import requests

st.set_page_config(
    page_title="Agri-Vision Agent",
    page_icon="🌾",
    layout="centered"
)

st.title("🌾 Agri-Vision Agent")
st.write("AI-powered farming assistant")

uploaded_file = st.file_uploader(
    "📷 Upload a crop photo",
    type=["jpg", "jpeg", "png"]
)

city = st.text_input("📍 Farm location", "Guntur")

if uploaded_file:
    image = Image.open(uploaded_file).convert("RGB")

    max_size = 1600

    if max(image.size) > max_size:
        image.thumbnail((max_size, max_size))

    st.image(
        image,
        caption="Uploaded Crop",
        use_container_width=True
    )

    if st.button("🔍 Analyze Crop", use_container_width=True):

        try:
            client = genai.Client(
                api_key=st.secrets["GEMINI_API_KEY"]
            )

            prompt = """
You are the Vision Agent of an agricultural AI system.

Analyze the uploaded crop image.

Return:

Crop:
Visible symptoms:
Possible problem:
Confidence:
Evidence:
What should be checked next:

Important:
An image alone cannot prove a disease.
If the image is unclear, say the diagnosis is uncertain.
Do not recommend a specific pesticide or chemical from the image alone.
"""

            with st.spinner("👁️ Vision Agent analyzing..."):

                response = client.models.generate_content(
                    model="gemini-3.6-flash",
                    contents=[
                        prompt,
                        image
                    ]
                )

            st.subheader("👁️ Vision Agent")

            if response.text:
                st.write(response.text)
            else:
                st.warning("The AI did not return a text response.")

            st.subheader("🌦️ Weather Agent")

            with st.spinner("🌦️ Checking local weather..."):

                geo_url = "https://geocoding-api.open-meteo.com/v1/search"

                geo_params = {
                    "name": city,
                    "count": 1,
                    "language": "en",
                    "format": "json"
                }

                geo_response = requests.get(
                    geo_url,
                    params=geo_params,
                    timeout=15
                )

                if geo_response.status_code != 200:
                    st.error("Unable to find the location.")
                    st.stop()

                geo_data = geo_response.json()

                if "results" not in geo_data:
                    st.error("Location not found. Try another city.")
                    st.stop()

                location = geo_data["results"][0]

                latitude = location["latitude"]
                longitude = location["longitude"]

                weather_url = "https://api.open-meteo.com/v1/forecast"

                weather_params = {
                    "latitude": latitude,
                    "longitude": longitude,
                    "current": "temperature_2m,relative_humidity_2m,precipitation,weather_code",
                    "hourly": "temperature_2m,relative_humidity_2m,precipitation_probability,precipitation",
                    "forecast_days": 2,
                    "timezone": "auto"
                }

                weather_response = requests.get(
                    weather_url,
                    params=weather_params,
                    timeout=15
                )

                if weather_response.status_code != 200:
                    st.error("Unable to get weather information.")
                    st.stop()

                weather = weather_response.json()

            current = weather["current"]

            temperature = current["temperature_2m"]
            humidity = current["relative_humidity_2m"]
            precipitation = current["precipitation"]

            st.write("📍 Location:", location["name"])
            st.write("🌡️ Temperature:", temperature, "°C")
            st.write("💧 Humidity:", humidity, "%")
            st.write("🌧️ Current precipitation:", precipitation, "mm")

            hourly = weather["hourly"]

            rain_probability = max(
                hourly["precipitation_probability"][:12]
            )

            st.write(
                "🌧️ Maximum rain probability in next 12 hours:",
                rain_probability,
                "%"
            )

            st.success("🌦️ Weather data successfully retrieved.")

        except Exception:
            st.error(
                "Something went wrong while connecting to the AI or weather service."
            )