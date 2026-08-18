import streamlit as st
from google import genai
from PIL import Image

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

if uploaded_file:
    image = Image.open(uploaded_file)

    st.image(image, caption="Uploaded Crop", use_container_width=True)

    if st.button("🔍 Analyze Crop", use_container_width=True):

        client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

        prompt = """
You are the Vision Agent of an agricultural AI system.

Analyze the uploaded crop image.

Give the answer in this format:

Crop:
Visible symptoms:
Possible problem:
Confidence:
Why:
What should be checked next:

Important:
Do not claim that an image alone proves a disease.
If the image is unclear, say that the diagnosis is uncertain.
Do not recommend a specific pesticide or chemical from the image alone.
"""

        with st.spinner("🤖 Vision Agent is analyzing..."):
            response = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=[prompt, image]
            )

        st.subheader("🤖 Vision Agent Result")
        st.write(response.text)