import streamlit as st  
from langchain.vectorstores import chroma

from data_utils import scrap_from_job_ad, read_pdf
from PIL import Image
from time import sleep

from text_generator import generate_application, get_key_info, extract_candidate_info


def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

local_css("main.css")

def main():

    st.subheader("Trenger du hjelp til å skrive en jobbsøknad?")

    left_col, right_col = st.columns(2, gap="small")

    with st.container():
        with left_col:
            image_orginal = Image.open("img/woman_assistant.png")
            st.image(image=image_orginal, width=280)

        with right_col:
            http_job = st.text_input("Limm inn http av jobbannonsen her:")
            cv_file = st.file_uploader("Last opp din CV her:", type="pdf")
              
        #extra_text = st.text_area(placeholder="Skriv mer om deg selv hvis du har lyst ..", label="Skriv mer:", max_chars=512)
        clicked = st.button("Generer Søknad!", use_container_width=True, type="primary")

        if clicked:
            st.divider()
            job_info = scrap_from_job_ad(path=http_job)
    
            key_info = get_key_info(job_info)
            #st.subheader("Hiring company:")
            with st.expander("Hiring Company:"):
                st.write(key_info['company_info'])
            #st.subheader("Key Qualifications Required:")
            with st.expander("Key Qualifications Required:"):
                st.write(key_info['key_qualifications'])

            st.divider()
            

            sleep(60) # wait one minute to not exceed api limit
            if cv_file is not None:
                text = read_pdf(cv_file)
                info = extract_candidate_info(candidate_info_text=text, job_info=key_info)
                # st.write(info["name"])
                with st.expander("Your Qualifications:"):
                    st.write(info["qualifications"])
                #st.write(info["current position"])
                with st.expander("Your Working Experience:"):
                    st.write(info["years of experience"])
            sleep(60)   
            text = generate_application(job_info=key_info, candidate_info=info)
            st.divider()
            st.subheader("Cover Letter:")
            st.text_area("", text, height=800)


if __name__ == "__main__":
    main()
