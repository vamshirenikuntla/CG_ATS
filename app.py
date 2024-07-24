from dotenv import load_dotenv

load_dotenv()
import base64
import streamlit as st
import os
import io
from PIL import Image
import fitz  # PyMuPDF
import google.generativeai as genai
import re

# Configure the generative AI with the provided API key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def get_gemini_response(input_text, pdf_content, prompt):
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content([input_text, pdf_content, prompt])
    return response.text

def input_pdf_setup(uploaded_file):
    if uploaded_file is not None:
        try:
            pdf_document = fitz.open(stream=uploaded_file.read(), filetype="pdf")
            pdf_text = ""
            for page_num in range(len(pdf_document)):
                page = pdf_document.load_page(page_num)
                pdf_text += page.get_text()
            
            return pdf_text
        except Exception as e:
            st.error("An error occurred while processing the PDF.")
            raise e
    else:
        raise FileNotFoundError("No file uploaded")

def extract_percentage(response_text):
    match = re.search(r"(\d+)%", response_text)
    if match:
        return float(match.group(1))
    return 0.0

def process_all_resumes(resumes, job_description):
    results = {}
    for resume_name, resume_text in resumes.items():
        response = get_gemini_response(job_description, resume_text, input_prompt3)
        results[resume_name] = response
    return results

def pick_best_candidate(results):
    best_candidate = None
    best_score = 0
    for candidate, result in results.items():
        percentage_match = extract_percentage(result)
        if percentage_match > best_score:
            best_score = percentage_match
            best_candidate = candidate
    return best_candidate, best_score

## Streamlit App

st.set_page_config(page_title="ATS Resume Expert")
st.header("CG ATS System")

input_text = st.text_area("Job Description: ", key="input")

uploaded_files = st.file_uploader("Upload your resumes (PDFs)...", type=["pdf"], accept_multiple_files=True)

if uploaded_files:
    st.write(f"{len(uploaded_files)} PDF(s) Uploaded Successfully")
    resumes = {file.name: input_pdf_setup(file) for file in uploaded_files}

submit1 = st.button("Analyze Resumes")
submit2 = st.button("Match Percentages for All Resumes")
submit3 = st.button("Pick Best Candidate")
submit4 = st.button("Statistics")

input_prompt1 = """
You are an experienced Technical Human Resource Manager. Your task is to review the provided resume against the job description. 
Please share your professional evaluation on whether the candidate's profile aligns with the role. 
Highlight the strengths and weaknesses of the applicant in relation to the specified job requirements.
"""

input_prompt3 = """
You are a skilled ATS (Applicant Tracking System) scanner with a deep understanding of data science and ATS functionality. 
Your task is to evaluate the resume against the provided job description. Give me the percentage match if the resume matches
the job description. First, the output should come as a percentage, then keywords missing, and lastly, final thoughts.
"""

if submit1:
    if uploaded_files:
        st.subheader("Analysis of Resumes")
        for resume_name, resume_text in resumes.items():
            response = get_gemini_response(input_text, resume_text, input_prompt1)
            st.write(f"Resume: {resume_name}")
            st.write(response)

if submit2:
    if uploaded_files:
        results = process_all_resumes(resumes, input_text)
        st.subheader("Match Percentages for All Resumes")
        for candidate, result in results.items():
            percentage = extract_percentage(result)
            st.write(f"{candidate}: {percentage}%")

if submit3:
    if uploaded_files:
        results = process_all_resumes(resumes, input_text)
        best_candidate, best_score = pick_best_candidate(results)
        if best_candidate:
            st.subheader("Best Candidate")
            st.write(f"Best Candidate: {best_candidate}")
            st.write(f"Match Percentage: {best_score}%")
        else:
            st.write("No candidate found with a match percentage.")

if submit4:
    if uploaded_files:
        results = process_all_resumes(resumes, input_text)
        total_resumes = len(results)
        scores = [extract_percentage(result) for result in results.values()]
        highest_score = max(scores, default=0)
        average_score = sum(scores) / total_resumes if total_resumes > 0 else 0
        st.subheader("Statistics")
        st.write(f"Total Resumes Analyzed: {total_resumes}")
        st.write(f"Highest Match Percentage: {highest_score}%")
        st.write(f"Average Match Percentage: {average_score}%")
