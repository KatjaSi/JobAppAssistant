import streamlit as st  
from langchain.vectorstores import chroma

from doc_utils import load_pdf
from data_utils import chunk_data, create_embeddings, scrap_from_job_ad
from PIL import Image

from text_generator import generate_application

st.markdown("""
<style>
div.stButton > button:first-child {
    background-color:#e9753c;
}
</style>
""", unsafe_allow_html=True)

def main():

    st.subheader("Trenger du hjelp til å skrive en jobbsøknad?")

    left_col, right_col = st.columns(2, gap="small")

    with st.container():
        with left_col:
            image_orginal = Image.open("img/woman_assistant.png")
            st.image(image=image_orginal, use_column_width=True)

        with right_col:
            http_job = st.text_input("Limm inn http av jobbannonsen her:")
            cv_file = st.file_uploader("Upload din CV her:", type="pdf")
        
            extra_text = st.text_area(placeholder="Skriv mer om deg selv hvis du har lyst ..", label="Skriv mer:", max_chars=512)
        
        clicked = st.button("Generer Søknad!", use_container_width=True, type="primary")

        if clicked:
            st.divider()
            job_info = scrap_from_job_ad(path=http_job)
            text = generate_application(company=job_info['employer'], position=job_info['position'], candidate_description=extra_text)
            st.text_area("Jobbsøknad:", text, height=800)

if __name__ == "__main__":
    main()
