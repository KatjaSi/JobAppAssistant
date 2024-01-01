import os
from langchain.document_loaders import PyPDFLoader

def load_pdf(file):
    name, extention = os.path.splitext(file)
    assert extention==".pdf"
    loader = PyPDFLoader(file)
    data = loader.load()
    return data