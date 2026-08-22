import streamlit as st
from google import genai
from PIL import Image
import requests
import tempfile
import os

st.set_page_config(
    page_title="Agri-Vision Agent",
    page_icon="🌾",
    layout="centered"
)
st.markdown("""
<style>
.block-container {
    max-width: 900px;
    padding-top: 1rem;
    padding-left: 1rem;
    padding-right: 1rem;
}
.stButton > button {
    width: 100%;
    min-height: 55px;
    border-radius: 12px;
    font-size: 18px;
    font-weight: 600;
}
h1 {
    text-align: center;
}
@media (max-width: 600px) {
    .block-container {
        padding: 0.8rem;
    }
    h1 {
        font-size: 30px;
    }
    h2 {
        font-size: 24px;
    }
    h3 {
        font-size: 20px;
    }
}
</style>
""", unsafe_allow_html=True)

st.title("🌾 Agri-Vision Agent")
st.caption("Observe • Investigate • Verify • Decide")

st.write(
    "AI-powered farming decision-support system"
)

st.subheader("📷 Crop Photo")

uploaded_file = st.file_uploader(
    "Upload a crop photo",
    type=["jpg", "jpeg", "png"]
)

st.subheader("📍 Farm Location")

city = st.text_input(
    "Enter your farm location",
    "Guntur"
)

st.subheader("🎤 Farmer Voice")

audio_value = st.audio_input(
    "Speak your farming problem"
)

if audio_value:
    st.audio(audio_value)
    st.success(
        "🎤 Voice message recorded successfully."
    )

st.subheader("🌐 Farmer Language")

language = st.selectbox(
    "Choose response language",
    ["English", "తెలుగు"]
)

st.subheader("🤖 AI Analysis")

ai_mode = st.radio(
    "Choose AI mode",
    ["AI OFF", "AI ON"],
    horizontal=True
)

if uploaded_file:

    image = Image.open(
        uploaded_file
    ).convert("RGB")

    if max(image.size) > 1600:
        image.thumbnail(
            (1600, 1600)
        )

    st.image(
        image,
        caption="Uploaded Crop",
        use_container_width=True
    )

    if st.button(
        "🔍 Start Farm Investigation",
        use_container_width=True
    ):

        try:

            st.subheader(
                "🤖 Agent Activity"
            )

            st.markdown(
                "🟢 **Photo received**\n\n"
                "🎤 **Farmer input received**\n\n"
                "📍 **Farm location identified**\n\n"
                "🌦️ **Weather Agent gathering data...**"
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
                st.error(
                    "Unable to connect to location service."
                )
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
                st.error(
                    "Unable to retrieve weather."
                )
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

            st.markdown(
                "🟢 **Photo received**\n\n"
                "🎤 **Farmer input received**\n\n"
                "📍 **Location identified**\n\n"
                "✅ **Weather data gathered**"
            )

            st.subheader(
                "🌦️ Weather Agent"
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

            st.write(
                "Current precipitation:",
                f"{precipitation} mm"
            )

            st.divider()

            if ai_mode == "AI ON":

                st.subheader(
                    "🤖 Agri-Vision AI Agent"
                )

                if "GEMINI_API_KEY" not in st.secrets:

                    st.error(
                        "GEMINI_API_KEY is missing "
                        "from Streamlit Secrets."
                    )

                    st.stop()

                st.info(
                    "One Gemini AI request will "
                    "analyze the crop, farmer input "
                    "and weather together."
                )

                client = genai.Client(
                    api_key=st.secrets[
                        "GEMINI_API_KEY"
                    ]
                )

                prompt = f"""
You are Agri-Vision Agent, an agricultural
decision-support AI.

Perform ONE coordinated investigation.

INPUTS:

1. Crop photograph.
2. Farmer voice message, if provided.
3. Farm location.
4. Real-time weather.

LOCATION:

{location["name"]}

TEMPERATURE:

{temperature} °C

HUMIDITY:

{humidity} %

CURRENT PRECIPITATION:

{precipitation} mm

RAIN PROBABILITY NEXT 12 HOURS:

{rain_probability} %

RESPONSE LANGUAGE:

{language}

Your workflow:

STEP 1 — OBSERVE

Analyze visible symptoms in the crop image.

STEP 2 — UNDERSTAND

Use the farmer's spoken problem if audio is
provided.

STEP 3 — VERIFY

Compare the visual evidence and farmer's
description with the real-time weather.

Do not blindly trust the initial visual
assessment.

STEP 4 — DECIDE

Create a practical and safe farm action plan.

Return:

🌱 CROP:
Visible symptoms:

🔎 POSSIBLE PROBLEM:
Visual confidence:

🔬 VERIFICATION:
Does the environmental evidence support
the suspicion?

Supporting evidence:

Conflicting evidence:

🟡 RISK LEVEL:

📋 WHAT TO DO NOW:

🔍 WHAT TO CHECK NEXT:

🌦️ WEATHER ADVICE:

⏰ WHEN TO RECHECK:

🎯 OVERALL CONFIDENCE:

🤖 AGENT SUMMARY:

Explain briefly how the agent connected
the photo, farmer input and weather before
reaching the decision.

SAFETY:

An image alone cannot prove a disease.

Do not claim laboratory confirmation.

Do not recommend a specific pesticide,
chemical or dosage.

If evidence is insufficient, say:
"Further verification needed."

Do not invent weather information.

Keep the answer simple enough for a farmer.
"""

                try:

                    if audio_value:

                        audio_suffix = ".wav"

                        if audio_value.type:
                            if "mpeg" in audio_value.type:
                                audio_suffix = ".mp3"
                            elif "mp4" in audio_value.type:
                                audio_suffix = ".mp4"

                        with tempfile.NamedTemporaryFile(
                            delete=False,
                            suffix=audio_suffix
                        ) as temp_audio:

                            temp_audio.write(
                                audio_value.getvalue()
                            )

                            audio_path = (
                                temp_audio.name
                            )

                        try:

                            audio_file = client.files.upload(
                                file=audio_path
                            )

                            response = (
                                client.models.generate_content(
                                    model="gemini-3.6-flash",
                                    contents=[
                                        prompt,
                                        image,
                                        audio_file
                                    ]
                                )
                            )

                        finally:

                            if os.path.exists(
                                audio_path
                            ):
                                os.remove(
                                    audio_path
                                )

                    else:

                        response = (
                            client.models.generate_content(
                                model="gemini-3.6-flash",
                                contents=[
                                    prompt,
                                    image
                                ]
                            )
                        )

                    if not response.text:

                        st.error(
                            "Gemini returned an empty response."
                        )

                        st.stop()

                    st.markdown(
                        "🟢 **Photo received**\n\n"
                        "🎤 **Farmer input processed**\n\n"
                        "🌦️ **Weather gathered**\n\n"
                        "👁️ **Crop observed**\n\n"
                        "🔎 **Evidence verified**\n\n"
                        "🧠 **Farm decision generated**\n\n"
                        "🎯 **Investigation complete**"
                    )

                    st.divider()

                    st.subheader(
                        "📋 AI FARM REPORT"
                    )

                    st.write(
                        response.text
                    )

                except Exception as e:

                    error_text = str(e)

                    if "429" in error_text:

                        st.warning(
                            "⚠️ Gemini quota is currently "
                            "exhausted. AI is temporarily "
                            "unavailable."
                        )

                        st.info(
                            "The Weather Agent and "
                            "Smart Decision Engine can "
                            "still operate without Gemini."
                        )

                    else:

                        st.error(
                            "The AI Agent encountered "
                            "an error."
                        )

                        st.code(
                            error_text
                        )

            else:

                st.subheader(
                    "⏸️ AI Agent"
                )

                st.info(
                    "AI is currently OFF. "
                    "No Gemini request will be made."
                )

            st.divider()

            st.subheader(
                "🧠 Smart Environmental Decision"
            )

            if (
                temperature >= 35
                and humidity < 50
            ):

                risk_level = "🟡 Moderate"

                farm_condition = (
                    "Hot and relatively dry"
                )

                action = (
                    "Monitor the crop closely "
                    "and check soil moisture."
                )

            elif (
                humidity >= 80
                and rain_probability >= 60
            ):

                risk_level = "🟠 Elevated"

                farm_condition = (
                    "High humidity and high "
                    "rain probability"
                )

                action = (
                    "Inspect leaves carefully "
                    "and monitor for visible "
                    "symptom changes."
                )

            elif rain_probability >= 70:

                risk_level = "🟡 Moderate"

                farm_condition = (
                    "High probability of rain"
                )

                action = (
                    "Monitor the crop and "
                    "recheck conditions "
                    "after rainfall."
                )

            elif humidity >= 75:

                risk_level = "🟡 Moderate"

                farm_condition = (
                    "Relatively humid conditions"
                )

                action = (
                    "Inspect affected leaves "
                    "and monitor for changes."
                )

            else:

                risk_level = "🟢 Low environmental alert"

                farm_condition = (
                    "No major environmental "
                    "warning detected"
                )

                action = (
                    "Continue normal crop "
                    "monitoring."
                )

            st.success(
                f"🎯 Environmental Risk: "
                f"{risk_level}"
            )

            st.write(
                "🌱 Environmental condition:",
                farm_condition
            )

            st.write(
                "📋 Recommended next step:",
                action
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
                    "🎯 Environmental Risk",
                    risk_level
                )

            st.info(
                f"📍 Farm: {location['name']}"
            )

            st.info(
                f"🌱 Condition: {farm_condition}"
            )

            if language == "తెలుగు":

                st.subheader(
                    "🇮🇳 రైతు కోసం సూచన"
                )

                st.write(
                    "ప్రస్తుత వాతావరణ పరిస్థితులను "
                    "బట్టి పంటను గమనించండి."
                )

                st.write(
                    "తదుపరి చర్య:",
                    action
                )

            else:

                st.subheader(
                    "🇬🇧 Farmer Guidance"
                )

                st.write(
                    "Monitor the crop using "
                    "the current environmental "
                    "conditions."
                )

                st.write(
                    "Next action:",
                    action
                )

            st.divider()

            st.subheader(
                "🤖 COMPLETE AGENT WORKFLOW"
            )

            st.markdown(
                "🟢 **1. Photo received**\n\n"
                "🟢 **2. Farmer input received**\n\n"
                "🟢 **3. Location identified**\n\n"
                "🟢 **4. Weather gathered**\n\n"
                "🟢 **5. Environmental conditions analyzed**\n\n"
                "🟢 **6. Farm decision prepared**"
            )

            if ai_mode == "AI ON":

                st.success(
                    "🎯 AI Agent completed its "
                    "investigation."
                )

            else:

                st.info(
                    "⏸️ AI is OFF. "
                    "The application is running "
                    "in safe development mode."
                )

            st.caption(
                "⚠️ AI decision support only. "
                "Image analysis is not laboratory "
                "confirmation."
            )

        except requests.exceptions.RequestException:

            st.error(
                "🌐 Network error. "
                "Check your internet connection "
                "and try again."
            )

        except Exception as e:

            st.error(
                "The farm investigation "
                "encountered an error."
            )

            st.code(
                str(e)
            )