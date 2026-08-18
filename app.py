import streamlit as st
from PIL import Image
import requests

st.set_page_config(
    page_title="Agri-Vision Agent",
    page_icon="🌾",
    layout="centered"
)

st.title("🌾 Agri-Vision Agent")
st.caption("Observe → Investigate → Verify → Decide")

st.write(
    "AI-powered farming decision-support system"
)

uploaded_file = st.file_uploader(
    "📷 Upload a crop photo",
    type=["jpg", "jpeg", "png"]
)

city = st.text_input(
    "📍 Farm location",
    "Guntur"
)
st.subheader("🌐 Farmer Language")

language = st.selectbox(
    "Choose response language",
    ["English", "తెలుగు"]
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

        st.subheader(
            "🤖 Agent Activity"
        )

        activity = st.empty()

        activity.markdown(
            "🟢 **Photo received**"
        )

        activity.markdown(
            "🟢 **Photo received**\n\n"
            "🌦️ **Weather Agent gathering data...**"
        )

        try:

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
                    "Location not found."
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

            activity.markdown(
                "🟢 **Photo received**\n\n"
                "✅ **Weather data gathered**\n\n"
                "📊 **Preparing farm investigation...**"
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
                precipitation,
                "mm"
            )

            st.divider()

            st.subheader(
                "🤖 AI Agent"
            )

            st.warning(
                "🟡 AI analysis is temporarily "
                "paused because the AI provider "
                "quota is unavailable."
            )

            st.info(
                "The farming investigation "
                "framework is working correctly. "
                "AI analysis will be connected "
                "when the provider is available."
            )

            st.subheader(
                "🔎 Verification Stage"
            )

            st.write(
                "Waiting for AI analysis..."
            )

            st.subheader(
                "🧠 Decision Stage"
            )

            st.write(
                "Waiting for verified AI evidence..."
            )

            st.divider()

            st.subheader(
                "📊 FARM MONITOR"
            )

            st.info(
                f"🌱 Farm location: {location['name']}"
            )

            st.info(
                f"🌡️ Current temperature: "
                f"{temperature} °C"
            )

            st.info(
                f"💧 Current humidity: "
                f"{humidity}%"
            )

            st.info(
                f"🌧️ Rain probability: "
                f"{rain_probability}%"
            )

            activity.markdown(
                "🟢 **Photo received**\n\n"
                "✅ **Weather data gathered**\n\n"
                "⏸️ **AI analysis waiting for provider**\n\n"
                "🔎 **Verification waiting**\n\n"
                "🧠 **Decision waiting**"
            )

            st.success(
                "🌾 Farm investigation framework "
                "is ready."
            )

        except Exception as e:

            st.error(
                "The farm investigation "
                "encountered an error."
            )

            st.code(
                str(e)
            )