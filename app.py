import streamlit as st
import easyocr
from PIL import Image
import google.generativeai as genai
from gtts import gTTS

import os

#ocr
@st.cache_resource
def load_ocr():
    return easyocr.Reader(['en','ta'],gpu=False,verbose=False,download_enabled=True,model_storage_directory='./')

reader=load_ocr()

#====1.page config====
st.set_page_config(
    page_title="Tamil Health Buddy",
    page_icon="🩺",
    layout="centered"
)
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
st.caption("Blood report ah upload pannu,Tamil la kekalam")

#1.Gemini API Key setup-https://aistudio.google.com/app/apikey la vaangunathu
genai.configure(api_key="AIzaSyAQU6VkXYuwdkff8L4buS27o7F2c5QTLGc")

#safety settings
safety_settings=[
    {"category":"HARM_CATEGORY_HARASSMENT","threshold":"BLOCK_NONE"},
    {"category":"HARM_CATEGORY_HATE SPEECH","threshold":"BLOCK_NONE"},
    {"category":"HARM_CATEGORY_SEXUALLY_EXPLICIT","threshold":"BLOCK_NONE"},
    {"category":"HARM_CATEGORY_DANGEROUS_CONTENT","threshold":"BLOCK_NONE"},
]
model=genai.GenerativeModel('gemini-2.5-flash')

st.title("Tamil Medical Report Explainer")
st.write("ungaloda blood report ah upload pannunga.simple tamil la puriya vachudalam.")

uploaded_file=st.file_uploader("Report Upload Pannunga",type=["png","jpg","jpeg","pdf"])

if uploaded_file:
    img=Image.open(uploaded_file)
    st.image(img,caption="neenga upload panna report",width=300)

    #2.OCR-Image la irunthu text edukurathu
    with st.spinner('Report ah padikuren...'):
        extracted_text=" ".join(result)

    if extracted_text.strip():
        st.subheader("report la irunthu edutha text:")
        st.text(extracted_text[:500]+"...")

        #3.AI ku anuppi tamil la explain kekurathu
        prompt=f"""
nee oru udhaviyana medical assistant.intha blood report text ah paathu,normal manushangaluku puriyura maari simple tamil la explain pannu.
Rules:
1.medical terms ah tamil paduthu.hemoglobin=Ratha sogai
2.edhu normal range,edhu kammi/jaasthi nu sollu
3.bayamuruthaatha,aanal nallathuku sonna kelunga nu sollu
4.kadasiya:"idhu doctor advice illa,unmaiyana advice ku doctor ah parunga"nu kandippa podu

Report Text:
{extracted_text}
"""
        with st.spinner('AI Doctor Tamil la explain pandran...'):
            response=model.generate_content(prompt)
            report_text=response.text
            st.markdown(report_text)
            
        
            st.markdown("### audio va kekalam")
            if st.button("Generate Audio Report"):
                with st.spinner("Google Tamil Voice generate aagudhu...15 sec wait pannu"):

                    try:
                         from gtts import gTTS

                         clean_text=report_text.replace('*','').replace('#','').replace('**','')

                         tts=gTTS(text=clean_text,lang='ta',slow=False)
                         audio_file='report_audio.mp3'
                         tts.save(audio_file)

                         st.audio(audio_file,format='audio/mp3')
                         st.success("vanthuruchi!! play button ah thattu,tamil la pesum")

                        
                    except Exception as e:
                         st.error(f"audio Error:{e}")
                         st.info("Net connection iruka nu check pannu.gTTS ku net venum.")
    else:
        st.error("Image la text ah read panna mudiyala.thelivana photo upload pannu.")

          
