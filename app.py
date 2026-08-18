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

Important rules:
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

            weather_url = "https://api.openweathermap.org/data/2.5/weather"

            params = {
                "q": city,
                "appid": st.secrets["WEATHER_API_KEY"],
                "units": "metric"
            }

            with st.spinner("🌦️ Checking weather..."):

                weather_response = requests.get(
                    weather_url,
                    params=params,
                    timeout=15
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
                st.error(
                    "Weather service could not find this location."
                )

        except Exception as e:

            st.error(
                "The AI service temporarily failed. Please try again."
            )

            st.info(
                "If the problem continues, check the Gemini API key "
                "and API usage limits."
            )