import streamlit as st
from google import genai
from PIL import Image
import requests
import json

st.set_page_config(
    page_title="Agri-Vision Agent",
    page_icon="🌾",
    layout="centered"
)

st.title("🌾 Agri-Vision Agent")
st.caption("Observe → Investigate → Verify → Decide")

st.write("AI-powered self-verifying farming assistant")

uploaded_file = st.file_uploader(
    "📷 Upload a crop photo",
    type=["jpg", "jpeg", "png"]
)

city = st.text_input(
    "📍 Farm location",
    "Guntur"
)

if uploaded_file:

    image = Image.open(uploaded_file).convert("RGB")

    if max(image.size) > 1600:
        image.thumbnail((1600, 1600))

    st.image(
        image,
        caption="Uploaded Crop",
        use_container_width=True
    )

    if st.button(
        "🔍 Analyze Crop",
        use_container_width=True
    ):

        try:

            st.subheader("🤖 Agent Activity")

            activity = st.empty()

            activity.markdown(
                "🟢 **Photo received**"
            )

            activity.markdown(
                "🟢 **Photo received**\n\n"
                "🌦️ **Weather Agent gathering live weather...**"
            )

            geo_url = (
                "https://geocoding-api.open-meteo.com/v1/search"
            )

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
                st.error(
                    "Location not found. Try another city."
                )
                st.stop()

            location = geo_data["results"][0]

            latitude = location["latitude"]
            longitude = location["longitude"]

            weather_url = (
                "https://api.open-meteo.com/v1/forecast"
            )

            weather_params = {
                "latitude": latitude,
                "longitude": longitude,
                "current": (
                    "temperature_2m,"
                    "relative_humidity_2m,"
                    "precipitation"
                ),
                "hourly": (
                    "precipitation_probability,"
                    "precipitation"
                ),
                "forecast_days": 2,
                "timezone": "auto"
            }

            weather_response = requests.get(
                weather_url,
                params=weather_params,
                timeout=15
            )

            if weather_response.status_code != 200:
                st.error("Weather service failed.")
                st.stop()

            weather = weather_response.json()

            current = weather["current"]

            temperature = current[
                "temperature_2m"
            ]

            humidity = current[
                "relative_humidity_2m"
            ]

            precipitation = current[
                "precipitation"
            ]

            rain_probability = max(
                weather["hourly"][
                    "precipitation_probability"
                ][:12]
            )

            activity.markdown(
                "🟢 **Photo received**\n\n"
                "✅ **Weather data gathered**\n\n"
                "👁️ **Vision Agent analyzing crop...**"
            )

            if "GEMINI_API_KEY" not in st.secrets:
                st.error(
                    "GEMINI_API_KEY is missing."
                )
                st.stop()

            client = genai.Client(
                api_key=st.secrets["GEMINI_API_KEY"]
            )

            prompt = f"""
You are Agri-Vision Agent, an agricultural
decision-support AI.

You are performing ONE coordinated investigation.

You have:

1. A crop photograph.
2. Real-time weather information.

Your internal workflow must be:

STEP 1 — VISION ANALYSIS

Analyze visible symptoms in the photograph.

STEP 2 — VERIFICATION

Compare the visual evidence with the weather
conditions.

Do NOT blindly trust the image diagnosis.

STEP 3 — DECISION

Create a safe, practical farmer action plan.

REAL-TIME WEATHER:

Location: {location["name"]}

Temperature:
{temperature} °C

Humidity:
{humidity} %

Current precipitation:
{precipitation} mm

Rain probability during next 12 hours:
{rain_probability} %

Return the result in exactly this structure:

VISION ANALYSIS

Crop:
Visible symptoms:
Possible problem:
Visual confidence:
Evidence:

VERIFICATION

Verification status:
Environmental support:
Conflicting evidence:
What needs to be checked:

FINAL FARM DECISION

Farm status:
Risk level:
What is most likely happening:
What to do now:
What to check next:
Weather advice:
When to recheck:
Overall confidence:

AGENT SUMMARY

Explain in 2 or 3 simple sentences how the
agent connected the photo and weather information
before reaching its decision.

IMPORTANT SAFETY RULES:

An image alone cannot prove a plant disease.

Do not claim laboratory confirmation.

Do not recommend a specific pesticide,
chemical, or dosage.

If evidence is insufficient, clearly say:
"Further verification needed."

Do not invent weather information.

Keep the final advice simple enough
for a farmer to understand.
"""

            response = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=[
                    prompt,
                    image
                ]
            )

            if not response.text:
                st.error(
                    "The AI returned an empty response."
                )
                st.stop()

            result = response.text

            activity.markdown(
                "🟢 **Photo received**\n\n"
                "✅ **Weather data gathered**\n\n"
                "✅ **Vision analysis completed**\n\n"
                "🔎 **Verification completed**\n\n"
                "🧠 **Decision generated**\n\n"
                "🎯 **Investigation complete**"
            )

            st.divider()

            st.subheader(
                "📊 FARM HEALTH REPORT"
            )

            col1, col2 = st.columns(2)

            with col1:
                st.metric(
                    "🌡️ Temperature",
                    f"{temperature} °C"
                )

            with col2:
                st.metric(
                    "💧 Humidity",
                    f"{humidity}%"
                )

            col3, col4 = st.columns(2)

            with col3:
                st.metric(
                    "🌧️ Rain Chance",
                    f"{rain_probability}%"
                )

            with col4:
                st.metric(
                    "📍 Location",
                    location["name"]
                )

            st.divider()

            st.subheader(
                "🤖 AI INVESTIGATION RESULT"
            )

            st.write(result)

            st.divider()

            st.caption(
                "⚠️ AI decision support only. "
                "This is not laboratory diagnosis "
                "or professional agricultural advice."
            )

            st.success(
                "🌾 Agri-Vision Agent completed the investigation."
            )

        except Exception as e:

            st.error(
                "The investigation could not be completed."
            )

            if "429" in str(e):

                st.warning(
                    "Gemini API quota is currently exhausted. "
                    "Please wait for the quota to reset."
                )

            st.write("Technical error:")

            st.code(str(e))