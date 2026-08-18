import streamlit as st
from google import genai
from PIL import Image
import requests
import re

st.set_page_config(
    page_title="Agri-Vision Agent",
    page_icon="🌾",
    layout="centered"
)

st.title("🌾 Agri-Vision Agent")
st.caption("Observe → Investigate → Verify → Decide")
st.write("Self-verifying AI farming assistant")

uploaded_file = st.file_uploader(
    "📷 Upload a crop photo",
    type=["jpg", "jpeg", "png"]
)

city = st.text_input("📍 Farm location", "Guntur")

if uploaded_file:
    image = Image.open(uploaded_file).convert("RGB")

    if max(image.size) > 1600:
        image.thumbnail((1600, 1600))

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

            st.subheader("🤖 Agent Activity")

            activity_box = st.empty()
            activity_messages = []

            def update_activity(message):
                activity_messages.append(message)
                activity_box.markdown(
                    "\n\n".join(activity_messages)
                )

            update_activity("🟢 Photo received")
            update_activity("👁️ Vision Agent analyzing crop...")

            vision_prompt = """
You are the Vision Agent in an agricultural AI system.

Analyze the crop image.

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
Do not recommend a specific pesticide or chemical.
"""

            vision_response = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=[
                    vision_prompt,
                    image
                ]
            )

            vision_result = vision_response.text

            update_activity("✅ Vision analysis completed")

            st.subheader("👁️ Vision Agent")
            st.write(vision_result)

            update_activity(
                "🌦️ Weather Agent checking local weather..."
            )

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

            update_activity("✅ Weather data retrieved")

            st.subheader("🌦️ Weather Agent")

            st.write("📍 Location:", location["name"])
            st.write("🌡️ Temperature:", temperature, "°C")
            st.write("💧 Humidity:", humidity, "%")
            st.write(
                "🌧️ Current precipitation:",
                precipitation,
                "mm"
            )
            st.write(
                "🌧️ Rain probability next 12 hours:",
                rain_probability,
                "%"
            )

            verification_prompt = f"""
You are the Verification Agent.

VISION RESULT:
{vision_result}

REAL-TIME WEATHER:
Location: {location["name"]}
Temperature: {temperature} °C
Humidity: {humidity} %
Precipitation: {precipitation} mm
Rain probability: {rain_probability} %

Compare the image-based suspicion with the
environmental evidence.

Return:

VERIFICATION STATUS:
SUPPORT LEVEL:
REASON:
CONFLICTING EVIDENCE:
NEXT STEP:

Do not claim weather alone proves or disproves a disease.
Do not recommend a specific pesticide.
If evidence is insufficient, clearly say further verification is needed.
"""

            update_activity(
                "🔎 Verification Agent cross-checking evidence..."
            )

            verification_response = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=verification_prompt
            )

            verification_result = verification_response.text

            update_activity(
                "✅ Evidence verification completed"
            )

            st.subheader("🔎 Verification Agent")
            st.write(verification_result)

            decision_prompt = f"""
You are the Decision Agent of Agri-Vision Agent.

VISION RESULT:
{vision_result}

WEATHER:
Location: {location["name"]}
Temperature: {temperature} °C
Humidity: {humidity} %
Precipitation: {precipitation} mm
Rain probability: {rain_probability} %

VERIFICATION RESULT:
{verification_result}

Create a simple farmer action plan.

Return exactly:

FARM STATUS:
RISK LEVEL:
WHAT IS MOST LIKELY HAPPENING:
WHAT TO DO NOW:
WHAT TO CHECK NEXT:
WEATHER ADVICE:
WHEN TO RECHECK:
CONFIDENCE:

Rules:
Do not claim certainty from an image alone.
Do not prescribe a specific pesticide, chemical or dosage.
If uncertain, clearly say so.
Use only the weather information provided.
"""

            update_activity(
                "🧠 Decision Agent creating farm action plan..."
            )

            decision_response = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=decision_prompt
            )

            decision_result = decision_response.text

            update_activity("✅ Farm action plan created")
            update_activity("🎯 Investigation complete")

            risk_match = re.search(
                r"RISK LEVEL:\s*(.*)",
                decision_result,
                re.IGNORECASE
            )

            status_match = re.search(
                r"FARM STATUS:\s*(.*)",
                decision_result,
                re.IGNORECASE
            )

            confidence_match = re.search(
                r"CONFIDENCE:\s*(.*)",
                decision_result,
                re.IGNORECASE
            )

            problem_match = re.search(
                r"WHAT IS MOST LIKELY HAPPENING:\s*(.*)",
                decision_result,
                re.IGNORECASE
            )

            risk = (
                risk_match.group(1).strip()
                if risk_match
                else "See detailed report"
            )

            farm_status = (
                status_match.group(1).strip()
                if status_match
                else "Assessment completed"
            )

            confidence = (
                confidence_match.group(1).strip()
                if confidence_match
                else "See detailed report"
            )

            problem = (
                problem_match.group(1).strip()
                if problem_match
                else "See detailed report"
            )

            st.divider()

            st.subheader("📊 FARM HEALTH REPORT")

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
                    "🎯 Risk Level",
                    risk
                )

            st.info(
                f"🌱 **Farm Status:** {farm_status}"
            )

            st.warning(
                f"🔎 **Likely Problem:** {problem}"
            )

            st.info(
                f"🎯 **AI Confidence:** {confidence}"
            )

            st.subheader("🧠 FINAL FARM DECISION")
            st.write(decision_result)

            st.caption(
                "⚠️ This is AI-based decision support, "
                "not laboratory diagnosis or professional "
                "agricultural advice."
            )

            st.success(
                "🌾 Agri-Vision Agent completed the investigation."
            )

        except Exception:
            st.error(
                "Something went wrong. Please try again."
            )