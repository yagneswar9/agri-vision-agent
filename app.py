import streamlit as st
from PIL import Image
import requests

st.set_page_config(
    page_title="Agri-Vision Agent",
    page_icon="🌾",
    layout="centered"
)

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
    st.success("🎤 Voice message recorded successfully.")

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

    image = Image.open(uploaded_file).convert("RGB")

    if max(image.size) > 1600:
        image.thumbnail((1600, 1600))

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

            st.subheader("🤖 Agent Activity")

            if ai_mode == "AI ON":
                ai_status = "🤖 AI analysis enabled"
            else:
                ai_status = "⏸️ AI analysis disabled"

            st.markdown(
                "🟢 **Photo received**\n\n"
                "🎤 **Farmer input received**\n\n"
                f"{ai_status}\n\n"
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

            temperature = current["temperature_2m"]

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
                "✅ **Weather data gathered**\n\n"
                "🧠 **Smart Decision Engine analyzing...**"
            )

            st.subheader("🌦️ Weather Agent")

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

            st.subheader("🧠 Smart Decision Engine")

            if temperature >= 35 and humidity < 50:

                risk_level = "🟡 Moderate"

                farm_condition = (
                    "Hot and relatively dry"
                )

                action = (
                    "Monitor the crop closely "
                    "and check soil moisture."
                )

                weather_advice = (
                    "High temperature and low "
                    "humidity may increase "
                    "plant water stress."
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
                    "and monitor for rapid "
                    "spread of visible symptoms."
                )

                weather_advice = (
                    "Wet conditions may increase "
                    "the risk of moisture-related "
                    "crop problems."
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

                weather_advice = (
                    "Rain is likely during "
                    "the next several hours."
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

                weather_advice = (
                    "Higher humidity can "
                    "increase moisture-related "
                    "crop risk."
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

                weather_advice = (
                    "Current weather does not "
                    "show a major environmental "
                    "warning."
                )

            st.success(
                f"🎯 Environmental Risk: {risk_level}"
            )

            st.write(
                "🌱 Environmental condition:",
                farm_condition
            )

            st.write(
                "📋 Recommended next step:",
                action
            )

            st.write(
                "🌦️ Weather advice:",
                weather_advice
            )

            st.caption(
                "This is a preliminary environmental "
                "assessment. It is not a disease diagnosis."
            )

            st.divider()

            st.subheader("🔎 Verification Stage")

            if ai_mode == "AI ON":

                st.info(
                    "🤖 AI verification is selected. "
                    "Gemini connection will be added "
                    "in the next stage."
                )

            else:

                st.info(
                    "⏸️ AI verification is currently "
                    "disabled. No Gemini API request "
                    "is being made."
                )

            st.subheader("🧠 Decision Stage")

            if language == "తెలుగు":

                st.write("🇮🇳 భాష: తెలుగు")

                st.write(
                    "ప్రస్తుత వాతావరణ పరిస్థితులను "
                    "బట్టి పంటను గమనించండి."
                )

                st.write(
                    "📋 తదుపరి చర్య:",
                    action
                )

            else:

                st.write("🇬🇧 Language: English")

                st.write(
                    "Monitor the crop using "
                    "the current environmental "
                    "conditions."
                )

                st.write(
                    "📋 Next action:",
                    action
                )

            st.divider()

            st.subheader("📊 Farm Health Report")

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
                    "🎯 Risk",
                    risk_level
                )

            st.info(
                f"📍 Farm: {location['name']}"
            )

            st.info(
                f"🌱 Condition: {farm_condition}"
            )

            st.subheader("🤖 Agent Activity")

            st.markdown(
                "🟢 **Photo received**\n\n"
                "🟢 **Farmer input received**\n\n"
                "🟢 **Location identified**\n\n"
                "🟢 **Weather data retrieved**\n\n"
                "🟢 **Environmental conditions analyzed**\n\n"
                "🟢 **Farm action framework created**"
            )

            if ai_mode == "AI ON":

                st.warning(
                    "⚠️ AI provider connection is "
                    "not active yet. No Gemini request "
                    "was made."
                )

            else:

                st.success(
                    "⏸️ AI is OFF. "
                    "No Gemini quota was used."
                )

            st.success(
                "🌾 Farm investigation framework completed."
            )

            st.caption(
                "⚠️ This system provides preliminary "
                "decision support and does not replace "
                "professional agricultural diagnosis."
            )

        except requests.exceptions.RequestException:

            st.error(
                "🌐 Network error. "
                "Please check your internet connection "
                "and try again."
            )

        except Exception as e:

            st.error(
                "The farm investigation encountered an error."
            )

            st.code(str(e))