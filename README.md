# PrivateGPT_enhanced

This is to be used with PrivateGPT by imartinez.

https://github.com/imartinez/privateGPT

ingest_pre_pdf2txt_OCR.py
- Convert PDF to Text file using OCR before ingestion.
- Ensure you have pip install nltk PyPDF2
- NLTK to download as full package.
- Be sure to put your pdf in 'source_documents' folder within PrivateGPT.

Outlook_Extract.py
- Grab your inbox from Outlook and convert to Text File for ingestion.
- summarize your emails.
- Be sure to change 'save_dir' and 'model_path'.
- Current model used for summarization is 'bart-large-cnn' from hugging face.

PrivateGPT.py
- added simple GUI for query.

Summaries txt using LLM v2 and .env
- Download Env.env
- Rename as .env
- edit the .env file according to the directory where you store .txt that you want to summarize, as well location to save summarized txt
- ensure Llama model (GGLM) is downloaded and store in the 'Model' folder privateGPT.
