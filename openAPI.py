import os
open_api_key=""
os.environ["OPENAI_API_KEY"]=open_api_key

from langchain.chat_models import ChatOpenAI

from langchain import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.chains.summarize import load_summarize_chain
from langchain.text_splitter import RecursiveCharacterTextSplitter

from PyPDF2 import PdfReader

pdfreader = PdfReader('hess401.pdf')
from typing_extensions import Concatenate
# read text from pdf
text = ''
for i, page in enumerate(pdfreader.pages):
    content = page.extract_text()
    if content:
        text += content

llm = ChatOpenAI(temperature=0, model_name='gpt-3.5-turbo')


## Splittting the text
text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=20)
chunks = text_splitter.create_documents([text])

chain = load_summarize_chain(
    llm,
    chain_type='map_reduce',
    verbose=False
)
summary = chain.run(chunks)