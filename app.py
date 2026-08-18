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

city = st.text_input("📍 Enter your farm location", "Guntur")

if uploaded_file:
    image = Image.open(uploaded_file)

    st.image(image, caption="Uploaded Crop", use_container_width=True)

    if st.button("🔍 Analyze Crop", use_container_width=True):

        client = genai.Client(
            api_key=st.secrets["GEMINI_API_KEY"]
        )

        prompt = """
You are the Vision Agent of an agricultural AI system.

Analyze this crop image.

Return:

Crop:
Visible symptoms:
Possible problem:
Confidence:
Why:
What should be checked next:

Do not claim that an image alone proves a disease.
If the image is unclear, say the diagnosis is uncertain.
Do not recommend a specific pesticide or chemical from the image alone.
"""

        with st.spinner("👁️ Vision Agent analyzing..."):
            response = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=[prompt, image]
            )

        st.subheader("👁️ Vision Agent")
        st.write(response.text)

        st.subheader("🌦️ Weather Agent")

        weather_url = "https://api.openweathermap.org/data/2.5/weather"

        params = {
            "q": city,
            "appid": st.secrets["WEATHER_API_KEY"],
            "units": "metric"
        }

        with st.spinner("🌦️ Checking local weather..."):
            weather_response = requests.get(
                weather_url,
                params=params
            )

        if weather_response.status_code == 200:

            weather = weather_response.json()

            temperature = weather["main"]["temp"]
            humidity = weather["main"]["humidity"]
            description = weather["weather"][0]["description"]

            st.write("📍 Location:", city)
            st.write("🌡️ Temperature:", temperature, "°C")
            st.write("💧 Humidity:", humidity, "%")
            st.write("☁️ Conditions:", description)

        else:
            st.error("Unable to get weather information.")