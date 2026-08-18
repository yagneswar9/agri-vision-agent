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
st.write("Self-verifying AI farming assistant")

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

            st.subheader("👁️ Vision Agent")

            vision_prompt = """
You are the Vision Agent in an agricultural AI system.

Analyze this crop image.

Return:

Crop:
Visible symptoms:
Possible problem:
Confidence:
Evidence:
What should be checked next:

Rules:
An image alone cannot prove a disease.
If the image is unclear, say the diagnosis is uncertain.
Do not recommend a specific pesticide or chemical from the image alone.
"""

            with st.spinner("👁️ Analyzing crop..."):

                vision_response = client.models.generate_content(
                    model="gemini-3.6-flash",
                    contents=[
                        vision_prompt,
                        image
                    ]
                )

            vision_result = vision_response.text

            st.write(vision_result)

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

                geo_data = geo_response.json()

                if "results" not in geo_data:
                    st.error("Location not found.")
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

                weather = weather_response.json()

            current = weather["current"]

            temperature = current["temperature_2m"]
            humidity = current["relative_humidity_2m"]
            precipitation = current["precipitation"]

            hourly = weather["hourly"]

            rain_probability = max(
                hourly["precipitation_probability"][:12]
            )

            st.write("📍 Location:", location["name"])
            st.write("🌡️ Temperature:", temperature, "°C")
            st.write("💧 Humidity:", humidity, "%")
            st.write("🌧️ Current precipitation:", precipitation, "mm")
            st.write(
                "🌧️ Rain probability next 12 hours:",
                rain_probability,
                "%"
            )

            st.success("🌦️ Weather data retrieved.")

            st.subheader("🔎 Verification Agent")

            verification_prompt = f"""
You are the Verification Agent in a farming AI system.

You received two sources of evidence.

SOURCE 1 — VISION AGENT:

{vision_result}

SOURCE 2 — REAL-TIME WEATHER:

Location: {location["name"]}
Temperature: {temperature} °C
Humidity: {humidity} %
Current precipitation: {precipitation} mm
Maximum rain probability next 12 hours: {rain_probability} %

Your job is NOT to blindly accept the Vision Agent.

Compare the image diagnosis with the environmental evidence.

Determine:

1. Does the weather/environment support the suspected problem?
2. Is the diagnosis strongly supported, partially supported, or uncertain?
3. What evidence supports your conclusion?
4. What evidence conflicts with it?
5. What should the farmer check next?

Return exactly:

VERIFICATION STATUS:
SUPPORT LEVEL:
REASON:
CONFLICTING EVIDENCE:
NEXT STEP:

Important:
Do not claim that weather alone proves or disproves a plant disease.
Do not recommend a specific pesticide or chemical.
If evidence is insufficient, clearly say that the diagnosis needs further verification.
"""

            with st.spinner("🔎 Verification Agent checking evidence..."):

                verification_response = client.models.generate_content(
                    model="gemini-3.6-flash",
                    contents=verification_prompt
                )

            verification_result = verification_response.text

            st.write(verification_result)

            st.success(
                "✅ Vision → Weather → Verification completed"
            )

        except Exception as e:

            st.error(
                "Something went wrong. Please try again."
           )