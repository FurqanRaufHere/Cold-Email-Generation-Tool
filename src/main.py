import streamlit as st
from langchain_community.document_loaders import WebBaseLoader
import requests
from langchain_core.documents import Document
import os
from dotenv import load_dotenv

from chains import Chain
from portfolio import Portfolio
from utils import clean_text

load_dotenv()

def create_streamlit_app(llm, portfolio, clean_text):
    st.title("📧 Cold Mail Generator")
    url_input = st.text_input("Enter a URL:", value="")
    # https://careers.nike.com/administrative-assistant-itc/job/R-66395
    submit_button = st.button("Submit")

    if submit_button:
        try:
            # loader = WebBaseLoader([url_input])
            # data = clean_text(loader.load().pop().page_content)
            headers = {
                "User-Agent": "Mozilla/5.0 (compatible; ColdMailBot/1.0)"
                }
            response = requests.get(url_input, headers=headers)
            response.raise_for_status()  # will raise an HTTPError if request fails
            text = response.text
            document = Document(page_content=text)
            data = clean_text(document.page_content)
            
            portfolio.load_portfolio()
            jobs = llm.extract_jobs(data)
            for job in jobs:
                skills = job.get('skills', [])
                links = portfolio.query_links(skills)
                email = llm.write_mail(job, links)
                st.code(email, language='markdown')
        except Exception as e:
            st.error(f"An Error Occurred: {e}")


if __name__ == "__main__":
    chain = Chain()
    portfolio = Portfolio()
    st.set_page_config(layout="wide", page_title="Cold Email Generator", page_icon="📧")
    create_streamlit_app(chain, portfolio, clean_text)


