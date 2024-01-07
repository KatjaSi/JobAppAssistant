import datetime
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv, find_dotenv
from langchain.llms import OpenAI
from langchain.chains import LLMChain
from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage
)
from langchain.chat_models import ChatOpenAI
from time import sleep
from datetime import datetime

load_dotenv(find_dotenv(), override=True)

LANGUAGE_VALUES = {
    "no": "Norwegian",
    "en": "English",
    "norsk": "Norwegian",
    "english": "English"
}

def generate_application(job_info, candidate_info, language):
    language = LANGUAGE_VALUES[language]
    eng_template = f" Write a cover letter in norwegian language\
          to apply for a postion {job_info['position']} with a following requirements: {job_info['key_qualifications']} in company with describtion: {job_info['company_info']}\
              for a candidate with the folowing qualifications: {candidate_info['qualifications']}.\
                Take into consideration this information about candidate experience: {candidate_info['years of experience']}. Candidate name is {candidate_info['name']}.\
                    Answer the question: 'Why should you hire me?'"
    no_template = f"Generer et søknadsbrev på norsk språk for å søke på stillingen {job_info['position']} med følgende krav: {job_info['key_qualifications']} \
        i selskapet med beskrivelse: {job_info['company_info']} for en kandidat med følgende kvalifikasjoner: {candidate_info['qualifications']}. \
            Ta hensyn til denne informasjonen om kandidatens erfaring: \
        {candidate_info['years of experience']}. Kandidatens navn er {candidate_info['name']}. Besvar spørsmålet: 'Hvorfor bør du ansette meg?'"
    prompt = PromptTemplate(
        input_variables=['position', 'requirements', 'company', 'candidate_description', 'experience','name'],
        template=eng_template if language=="English" else no_template
    )

    llm = OpenAI(model_name="text-davinci-003", temperature=0.6, max_tokens=1024)
    output = llm(prompt.format( job_info=job_info, candidate_info=candidate_info))
    
    return output


def get_key_info(job_info, language):
    language = LANGUAGE_VALUES[language]
    key_info = dict(())
    key_info.update(job_info)

    human_message_en = f"Provide main key qualifications required for the job from the following job advertisement: {job_info['ad_text']}. \
                     Provide the answer as a list with each qualification in one line."
    human_message_no = f"Gi de viktigste nøkkelkvalifikasjonene som kreves for jobben fra følgende stillingsannonse: {job_info['ad_text']}. \
        Gi svaret som en liste med hver kvalifikasjon på en linje."

    messages_1 = [
        SystemMessage(content="You are expert in summirizing the key points of job advertisements."),
        SystemMessage(content = f"Provide text in {language} language."),
        HumanMessage(content=human_message_en if language=="English" else human_message_no )
    ]

    llm = ChatOpenAI(temperature=0, model_name='gpt-3.5-turbo')
    key_qualifications = llm(messages_1).content
    key_info['key_qualifications']=key_qualifications

    human_message_en= f"Provide the most relevant information about the hiring company from the folowing job advertisement: {job_info['extended_ad_text']}. \
                     The answer should be in 5-6 sentences and only contain the information about the company itself."
    human_message_no = f"Gi den mest relevante informasjonen om selskapet som rekrutterer fra følgende stillingsannonse: {job_info['extended_ad_text']}. \
        Svaret bør være på 5-6 setninger og kun inneholde informasjon om selve selskapet."

    messages_2 = [
        SystemMessage(content="You are expert in summirizing the key points of job advertisements."),
        SystemMessage(content = f"Provide text in {language} language."),
        HumanMessage(content=human_message_en if language=="English" else human_message_no )
    ]

    company_info = llm(messages_2).content
    key_info['company_info'] = company_info
    

    return key_info

def extract_candidate_info(candidate_info_text, job_info, language):
    language = LANGUAGE_VALUES[language]
    info = dict(())
    messages = [
        SystemMessage(content="You are expert in summirizing the key points of CV. "),
        HumanMessage(content=f"Extract the candidate's name from the provided CV snippet : {candidate_info_text[:200]}. \
                    Respond with the candidate's name only (e.g., 'Maria Knudsen').")
    ]

    llm = ChatOpenAI(temperature=0, model_name='gpt-3.5-turbo')
    name = llm(messages).content
    info["name"] = name

    human_message_en = f"Extract the candidate's main qualifications from the provided CV snippet (not more than six) : {candidate_info_text}. \
                   Provide the answer as a list with each qualification in one line."
    human_message_no = f"Finn kandidatens viktigste kvalifikasjoner fra den gitte CV-utdragsbiten (ikke mer enn seks): {candidate_info_text}.\
          Gi svaret som en liste med hver kvalifikasjon på en linje."

    messages_2 = [
        SystemMessage(content="You are expert in summirizing the key points of CV. "),
        SystemMessage(content = f"Provide text in {language} language."),
        HumanMessage(content=human_message_en if language=="English" else human_message_no)
    ]

    qualifications = llm(messages_2).content
    info["qualifications"] = qualifications

    human_message_en = f"Extract the information about the candidate's current position (job) from the provided CV : {candidate_info_text}.\
                     The response should consist of two to five sentences focusing solely on the candidate's present job role."
    human_message_no = f"Finn informasjonen om kandidatens nåværende stilling (jobb) fra den gitte CV-en: {candidate_info_text}. \
        Svaret bør bestå av to til fem setninger som fokuserer utelukkende på kandidatens nåværende jobbrolle."

    messages_3 = [
        SystemMessage(content="You are expert in summirizing the key points of CV. "),
        SystemMessage(content = f"Provide text in {language} language."),
        HumanMessage(content=human_message_en if language=="English" else human_message_no)
    ]

    cur_position = llm(messages_3).content
    info["current position"] = cur_position

    sleep(60)
    human_message_en = f"Extract the information about how many years of experience the candidate has from the provided CV : {candidate_info_text}.\
                     The response should be in the format 'interpreter - 1 month, software developer - 2 years 3 months, data scientist - 1 year.'\
                     Present time is {__current_time__()}"
    human_message_no = f"Finn informasjonen om hvor mange års erfaring kandidaten har fra den gitte CV-en: {candidate_info_text}.\
          Svaret bør være i formatet 'tolk - 1 måned, programvareutvikler - 2 år 3 måneder, data scientist - 1 år.' \
            Nåværende tidspunkt er {__current_time__()}."
    messages_4 = [
        SystemMessage(content="You are expert in summirizing the key points of CV. "),
        SystemMessage(content = f"Provide text in {language} language."),
        HumanMessage(content=human_message_en if language=="English" else human_message_no)
    ]

    years = llm(messages_4).content
    human_message_en = f"Identify which working experience from {years} is relevant for the position with {job_info['position']} with requirements: \
                         {job_info['key_qualifications']}.\
                     Summarize the total time of relevant and somehow relevant experience."
    human_message_no = f"Identifiser hvilken arbeidserfaring fra {years} som er relevant for stillingen med {job_info['position']} \
        med kravene: {job_info['key_qualifications']}. \
        Oppsummer den totale tiden med relevant og noenlunde relevant erfaring."
    system_message_en = "Prioritize depth and breadth of skills and experiences rather than a strict match of job titles. \
                          Summarize the range of experiences, emphasizing transferable skills and relevant project work."
    system_message_no = "Prioriter dybden og bredden av ferdigheter og erfaringer heller enn en streng match av stillingstitler. \
        Oppsummer rekkevidden av erfaringer og legg vekt på overførbare ferdigheter og relevant prosjektarbeid."
    relevant_experience = llm(
        messages=[
            SystemMessage(content="You are a HR that can accurately identify which working experience is relevant for a particular position."),
            HumanMessage(content=human_message_en if language=="English" else human_message_no),
            SystemMessage(content=system_message_en if language=="English" else system_message_no)
        ]
    )
    info["years of experience"] = relevant_experience.content
    return info

def __current_time__():
    now = datetime.now()
    formatted_time = now.strftime("%B %Y")
    print(formatted_time)
    return formatted_time
