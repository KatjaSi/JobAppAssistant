import PyPDF2
from  urllib import request
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores.chroma import Chroma
from bs4 import BeautifulSoup

def chunk_data(data, chunk_size=256, chunk_overlap=20):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunks = text_splitter.split_documents(data)
    return chunks

def create_embeddings(chunks):
    embeddings = OpenAIEmbeddings()
    vector_store = Chroma.from_documents(chunks, embeddings)
    return vector_store


def scrap_from_job_ad(path):
    contents = request.urlopen(path).read().decode("utf-8") 
    soup = BeautifulSoup(contents, 'html.parser')
    def_table = soup.find("dl", class_="definition-list")  
    all_lines = def_table.find_all('dd')
    job_info = dict()
    job_info['position'] = all_lines[1].get_text()
    job_info['employer'] = all_lines[0].get_text()
    job_info['ad_text'] = soup.find("div", class_="import-decoration").get_text()
    job_info['extended_ad_text'] = soup.find("div", class_="u-word-break").get_text()
    return job_info

def read_pdf(file):
    pdf_reader = PyPDF2.PdfReader(file)
    num_pages = len(pdf_reader.pages)
    text = ""
    for page_num in range(num_pages):
        page = pdf_reader.pages[page_num]
        text += page.extract_text()
    return text

if __name__ == "__main__":
    #scrap_from_job_ad("https://www.finn.no/job/fulltime/ad.html?finnkode=330475481")
    pass