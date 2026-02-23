from dotenv import load_dotenv

load_dotenv()
import base64
import streamlit as st
import os
import io
from PIL import Image 
import pdf2image
import google.generativeai as genai
from PyPDF2 import PdfReader  # For text extraction
from docx import Document

def get_google_api_key():
    # Local dev uses .env; Streamlit Cloud uses st.secrets.
    env_key = os.getenv("GOOGLE_API_KEY")
    if env_key:
        return env_key
    try:
        return st.secrets["GOOGLE_API_KEY"]
    except Exception:
        return None

api_key = get_google_api_key()
if api_key:
    # Configure Gemini only when a valid API key is present.
    genai.configure(api_key=api_key)

def get_gemini_response(instruction, resume_data, job_description):
    """
    Send resume and job description to Gemini for analysis.
    resume_data can be text (string) or a list of image parts.
    """
    model = genai.GenerativeModel("gemini-2.5-flash-lite")
    
    # Build content list: instruction, resume_data, job_description
    if isinstance(resume_data, str):
        # Text mode: send as plain text
        content = [instruction, resume_data, job_description]
    else:
        # Image mode: send as image parts
        content = [instruction] + resume_data + [job_description]
    
    response = model.generate_content(content)
    return response.text

def input_resume_setup(uploaded_file):
    """
    Extract resume content from uploaded file.
    Returns:
      - str: Full text for text-based resumes (PDF/DOCX)
      - list: List of image parts if PDF is scanned or has no text
    """
    if uploaded_file is not None:
        file_name = uploaded_file.name.lower()

        # For PDFs: prefer direct text extraction, fallback to image mode for scanned files.
        if file_name.endswith(".pdf"):
            pdf_bytes = uploaded_file.read()

            # Try to extract text from all pages
            try:
                reader = PdfReader(io.BytesIO(pdf_bytes))
                text_content = ""

                for page_num, page in enumerate(reader.pages):
                    text = page.extract_text()
                    text_content += f"\n--- Page {page_num + 1} ---\n{text}"

                # If we extracted meaningful text, return it
                if text_content.strip():
                    return text_content
            except Exception as e:
                st.warning(f"Text extraction failed: {e}. Falling back to image mode.")

            # Fallback: Convert PDF to images
            try:
                images = pdf2image.convert_from_bytes(pdf_bytes)
                pdf_parts = []

                for img in images:
                    # Convert to bytes
                    img_byte_arr = io.BytesIO()
                    img.save(img_byte_arr, format='JPEG')
                    img_byte_arr = img_byte_arr.getvalue()

                    pdf_parts.append({
                        "mime_type": "image/jpeg",
                        "data": base64.b64encode(img_byte_arr).decode()
                    })

                return pdf_parts
            except Exception as e:
                raise FileNotFoundError(f"Failed to process PDF: {e}")

        # DOCX resumes are usually text-first, so we extract paragraph text directly.
        if file_name.endswith(".docx"):
            try:
                docx_file = io.BytesIO(uploaded_file.read())
                document = Document(docx_file)
                paragraphs = [p.text.strip() for p in document.paragraphs if p.text.strip()]
                text_content = "\n".join(paragraphs)

                if text_content.strip():
                    return text_content

                raise ValueError("The DOCX file appears empty or has no readable text.")
            except Exception as e:
                raise FileNotFoundError(f"Failed to process DOCX: {e}")

        raise ValueError("Unsupported file type. Please upload a PDF or DOCX file.")
    else:
        raise FileNotFoundError("No file uploaded")

## Streamlit App

# Main UI section.
st.set_page_config(page_title="ATS Resume Expert")
st.header("ATS Tracking System")
input_text=st.text_area("Job Description: ",key="input")
uploaded_file=st.file_uploader("Upload your resume (PDF or DOCX)...",type=["pdf", "docx"])


if uploaded_file is not None:
    st.write("Resume uploaded successfully")


submit1 = st.button("Tell Me About the Resume")

#submit2 = st.button("How Can I Improvise my Skills")

submit3 = st.button("Percentage match")

# Two prompts for two analysis modes using the same resume + job description.

input_prompt1 = """
 You are an experienced Technical Human Resource Manager,your task is to review the provided resume against the job description. 
  Please share your professional evaluation on whether the candidate's profile aligns with the role. 
 Highlight the strengths and weaknesses of the applicant in relation to the specified job requirements.
"""

input_prompt3 = """
You are an skilled ATS (Applicant Tracking System) scanner with a deep understanding of data science and ATS functionality, 
your task is to evaluate the resume against the provided job description. give me the percentage of match if the resume matches
the job description. First the output should come as percentage and then keywords missing and last final thoughts.
"""

if submit1:
    # Shared validations: key must exist and a resume must be uploaded.
    if not api_key:
        st.error("GOOGLE_API_KEY not found. Set it in .env (local) or Streamlit Cloud Secrets.")
    elif uploaded_file is not None:
        resume_data = input_resume_setup(uploaded_file)
        response = get_gemini_response(input_prompt1, resume_data, input_text)
        st.subheader("Resume Analysis:")
        st.write(response)
    else:
        st.write("Please upload the resume")

elif submit3:
    if not api_key:
        st.error("GOOGLE_API_KEY not found. Set it in .env (local) or Streamlit Cloud Secrets.")
    elif uploaded_file is not None:
        resume_data = input_resume_setup(uploaded_file)
        response = get_gemini_response(input_prompt3, resume_data, input_text)
        st.subheader("Percentage Match Analysis:")
        st.write(response)
    else:
        st.write("Please upload the resume")



   