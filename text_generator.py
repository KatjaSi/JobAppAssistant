import datetime
from langchain import PromptTemplate
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

#def generate_application(company, position, candidate_description):
def generate_application(job_info, candidate_info):
    print(job_info['position'])
    template = f" Write a cover letter in norwegian language\
          to apply for a postion {job_info['position']} with a following requirements: {job_info['key_qualifications']} in company with describtion: {job_info['company_info']}\
              for a candidate with the folowing qualifications: {candidate_info['qualifications']}.\
                Take into consideration this information about candidate experience: {candidate_info['years of experience']}. Candidate name is {candidate_info['name']}."

    prompt = PromptTemplate(
        input_variables=['position', 'requirements', 'company', 'candidate_description', 'experience','name'],
        template=template
    )

    llm = OpenAI(model_name="text-davinci-003", temperature=0.7, max_tokens=1400)
    output = llm(prompt.format( job_info=job_info, candidate_info=candidate_info))
    
    return output


def get_key_info(job_info):
    # qualifications && about company
    key_info = dict(())
    key_info.update(job_info)
    messages_1 = [
        SystemMessage(content="You are expert in summirizing the key points of job advertisements."),
        HumanMessage(content=f"Provide main key qualifications required for the job from the following job advertisement: {job_info['ad_text']}. \
                     Provide the answer as a list with each qualification in one line.")
    ]

    llm = ChatOpenAI(temperature=0, model_name='gpt-3.5-turbo')
    key_qualifications = llm(messages_1).content
    key_info['key_qualifications']=key_qualifications

    messages_2 = [
        SystemMessage(content="You are expert in summirizing the key points of job advertisements."),
        HumanMessage(content=f"Provide the most relevant information about the hiring company from the folowing job advertisement: {job_info['extended_ad_text']}. \
                     The answer should be in 5-6 sentences and only contain the information about the company itself.")
    ]

    company_info = llm(messages_2).content
    key_info['company_info'] = company_info
    

    return key_info

def extract_candidate_info(candidate_info_text, job_info):
    info = dict(())
    messages = [
        SystemMessage(content="You are expert in summirizing the key points of CV. "),
        HumanMessage(content=f"Extract the candidate's name from the provided CV snippet : {candidate_info_text[:200]}. \
                    Respond with the candidate's name only (e.g., 'Maria Knudsen').")
    ]

    llm = ChatOpenAI(temperature=0, model_name='gpt-3.5-turbo')
    name = llm(messages).content
    info["name"] = name

    human_message = f"Extract the candidate's main qualifications from the provided CV snippet (not more than six) : {candidate_info_text}. \
                   Provide the answer as a list with each qualification in one line in english language."

    messages_2 = [
        SystemMessage(content="You are expert in summirizing the key points of CV. "),
        HumanMessage(content=human_message)
    ]

    qualifications = llm(messages_2).content
    info["qualifications"] = qualifications

    messages_3 = [
        SystemMessage(content="You are expert in summirizing the key points of CV. "),
        HumanMessage(content=f"Extract the information about the candidate's current position (job) from the provided CV : {candidate_info_text}.\
                     The response should consist of two to five sentences focusing solely on the candidate's present job role.\
                      If using pronouns use he or she basen on the name: {name}. \
                        Do not use 'they'.")
    ]

    cur_position = llm(messages_3).content
    info["current position"] = cur_position

    sleep(60)
    messages_4 = [
        SystemMessage(content="You are expert in summirizing the key points of CV. "),
        HumanMessage(content=f"Extract the information about how many years of experience the candidate has from the provided CV : {candidate_info_text}.\
                     The response should be in the format 'interpreter - 1 month, software developer - 2 years 3 months, data scientist - 1 year.'\
                     Present time is {__current_time__()}")
    ]

    years = llm(messages_4).content
    relevant_experience = llm(
        messages=[
            SystemMessage(content="You are a HR that can accurately identify which working experience is relevant for a particular position."),
            HumanMessage(content=f"Identify which working experience from {years} is relevant for the position with {job_info['position']} with requirements: {job_info['key_qualifications']}.\
                     Summarize the total time of relevant and somehow relevant experience."),
            SystemMessage(content="Prioritize depth and breadth of skills and experiences rather than a strict match of job titles. \
                          Summarize the range of experiences, emphasizing transferable skills and relevant project work.")
        ]
    )
    info["years of experience"] = relevant_experience.content
    return info

def __current_time__():
    now = datetime.now()
    formatted_time = now.strftime("%B %Y")
    print(formatted_time)
    return formatted_time
