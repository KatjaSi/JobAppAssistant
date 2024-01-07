import streamlit as st  
import json
from langchain.vectorstores import chroma

from data_utils import scrap_from_job_ad, read_pdf
from PIL import Image
from time import sleep

from text_generator import generate_application, get_key_info, extract_candidate_info

st.session_state['app_lan_key'] = 0

def load_texts():
    with open("texts.json", "r", encoding="utf-8") as file:
        all_texts = json.load(file)
        st.session_state.all_texts = all_texts

def get_language():
    lang = st.session_state.language if "language" in st.session_state else "no"
    return lang

selected_language = get_language()


def language_callback(language):
    st.session_state.language = language
    st.session_state.app_lan_key = 1


def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

local_css("main.css")

all_texts = load_texts()

with st.sidebar:
    button_container = st.container()
    button_container.subheader(st.session_state.all_texts["choose_lan_msg"][selected_language])
    col1, col2, _ = button_container.columns([1,1,2])
    en_button = col1.button(label="no", type="secondary", use_container_width=True, on_click=language_callback, args=("no",))
    no_button = col2.button(label="en",type="secondary", use_container_width=True,  on_click=language_callback, args=("en",))

def main():
    st.title(st.session_state.all_texts['welcome_message'][selected_language])
    st.divider()


    st.subheader(st.session_state.all_texts['need_help_message'][selected_language])
    left_col, right_col = st.columns([3,4])

    with st.container():
        with left_col:
            image_orginal = Image.open("img/woman_assistant.png")
            st.image(image=image_orginal, use_column_width=True)

        with right_col:
            http_job = st.text_input(st.session_state.all_texts['job_http'][selected_language])
            cv_file = st.file_uploader(st.session_state.all_texts['upload_cv_message'][selected_language], type="pdf")
            app_language = st.selectbox(st.session_state.all_texts['choose_app_lan_msg'][selected_language],("norsk", "english")) 
              
        #extra_text = st.text_area(placeholder="Skriv mer om deg selv hvis du har lyst ..", label="Skriv mer:", max_chars=512)   
        clicked = st.button(st.session_state.all_texts['generate_app_message'][selected_language], use_container_width=True, type="primary")

        if clicked:
            if cv_file is None:
                st.write(st.session_state.all_texts["did_not_get_cv_msg"][selected_language])
                return
            st.divider()
            with st.spinner(st.session_state.all_texts["extract_from_job_app_msg"][selected_language]):
                # TODO: add error handling here
                job_info = scrap_from_job_ad(path=http_job)
                key_info = get_key_info(job_info, language=app_language)
            
            with st.expander(st.session_state.all_texts['hiring_company_expander_heading'][selected_language]):
                st.write(key_info['company_info'])
                
            with st.expander(st.session_state.all_texts['qualifications_required_expander_heading'][selected_language]):
                st.write(key_info['key_qualifications'])

            st.divider()
            with st.spinner(st.session_state.all_texts['fit_for_position_spinner_msg'][selected_language]):
                sleep(60) # wait one minute to not exceed api limit
            
                text = read_pdf(cv_file)
                info = extract_candidate_info(candidate_info_text=text, job_info=key_info, language=app_language)
            with st.expander(st.session_state.all_texts['your_qualifications_expander_msg'][selected_language]):
                st.write(info["qualifications"])
                #st.write(info["current position"])
            with st.expander(st.session_state.all_texts['your_working_experience_expander_msg'][selected_language]):
                st.write(info["years of experience"])
            with st.spinner(st.session_state.all_texts['generating_app_soinner_msg'][selected_language]):
                sleep(60)   
                text = generate_application(job_info=key_info, candidate_info=info, language=app_language)
                st.divider()
                st.subheader(st.session_state.all_texts['cover_letter_heading'][selected_language])
                st.text_area("", text, height=700)
            


if __name__ == "__main__":
    main()
