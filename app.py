import streamlit as st
import easyocr
import numpy as np
from PIL import Image
import google.generativeai as genai
from gtts import gTTS

import os

#====1.page config====
st.set_page_config(
    page_title="Tamil Health Buddy",
    page_icon="🩺",
    layout="centered"
)

#====GEMINI API KEY-SAFE CONFIG====
try:
    api_key=st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except KeyError:
    st.error("GEMINI_API_KEY not found. please add it in streamlit cloud secrets.")
    st.stop()
except Exception as e:
    st.error(f"API Key error:{e}")
    st.stop()

#ocr
@st.cache_resource
def load_ocr():
    return easyocr.Reader(['en'],gpu=False,quantize=False,model_storage_directory='./models')

reader=load_ocr()


#====2.BIG BUTTON CSS- MELA POTTALEY POTHUM====
st.markdown("""
<style>
.stButton>button{
  width:100%;
  height:60px;
  font-size:20px;
  border-radius:15px;
  background-color:#FF4B4B;
  color:white;
}
</style>
""",unsafe_allow_html=True)

#===3.title===
st.title("Tamil Health Buddy")
st.caption("Upload your blood report and listen to the explanation in tamil")

#1.Gemini API Key setup-https://aistudio.google.com/app/apikey la vaangunathu
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

#safety settings
safety_settings=[
    {"category":"HARM_CATEGORY_HARASSMENT","threshold":"BLOCK_NONE"},
    {"category":"HARM_CATEGORY_HATE SPEECH","threshold":"BLOCK_NONE"},
    {"category":"HARM_CATEGORY_SEXUALLY_EXPLICIT","threshold":"BLOCK_NONE"},
    {"category":"HARM_CATEGORY_DANGEROUS_CONTENT","threshold":"BLOCK_NONE"},
]
model=genai.GenerativeModel('gemini-2.5-flash')

st.title("Tamil Medical Report Explainer")
st.write("please upload your blood report. I will explain it in simple tamil.")

uploaded_file=st.file_uploader("Upload Report",type=["png","jpg","jpeg","pdf"])

if uploaded_file:
    img=Image.open(uploaded_file)
    st.image(img,caption="your uploaded report",width=300)

    #2.OCR-Extracting text your images
    with st.spinner('Reading report...'):
        result=reader.readtext(np.array(img))
        extracted_text=" ".join([res[1] for res in result])

    if extracted_text.strip():
        st.subheader("Extracted text from report:")
        st.text(extracted_text[:500]+"...")

        #3.sending to AI to explain in tamil
        prompt=f"""
you are a helpful medical assistant.Read this blood report text and explain it in simple tamil that normal people can understand.
Rules:
1.Translate medical terms to tamil.example:hemoglobin=Ratha sogai.
2.Tell what is normal range,what is low/high.
3.Tell if it is concerning,but also tell what to do for better health.
4.Finally must add:"This is not a doctor's advice, please consult a doctor for actual advice".

Report Text:
{extracted_text}
"""
        with st.spinner('AI Doctor is Explaining in Tamil...'):
            response=model.generate_content(prompt)
            report_text=response.text
            st.markdown(report_text)
            
        
            st.markdown("### Listen to Audio")
            if st.button("Generate Audio Report"):
                with st.spinner("Generating Google Tamil Voice....Please wait 15 sec"):

                    try:
                         from gtts import gTTS

                         clean_text=report_text.replace('*','').replace('#','').replace('**','')

                         tts=gTTS(text=clean_text,lang='ta',slow=False)
                         audio_file='report_audio.mp3'
                         tts.save(audio_file)

                         st.audio(audio_file,format='audio/mp3')
                         st.success("Ready! Click the play Button to listen in tamil.")

                        
                    except Exception as e:
                         st.error(f"audio Error:{e}")
                         st.info("Please check your internet connection.gTTS requires internet.")
    else:
        st.error("Could not read text from the image.please upload a clear photo.")

          
