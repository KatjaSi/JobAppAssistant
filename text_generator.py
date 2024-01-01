from langchain import PromptTemplate
from dotenv import load_dotenv, find_dotenv
from langchain.llms import OpenAI

def generate_application(company, position, candidate_description):
    load_dotenv(find_dotenv(), override=True)
    template = f"You are an experience HR assitant, helping to create cover letters for job application. Write a cover letter\
          to apply for a postion: {position} in company {company} for a candidate with the folowing description: {candidate_description}."

    prompt = PromptTemplate(
        input_variables=['company', 'position', 'candidate_description'],
        template=template
    )

    llm = OpenAI(model_name="text-davinci-003", temperature=0.7, max_tokens=512)
    output = llm(prompt.format( company=company, position=position, 
                               candidate_description = candidate_description))
    
    return output