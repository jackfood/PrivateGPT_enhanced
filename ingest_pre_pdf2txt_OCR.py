import os
import nltk
import PyPDF2
from nltk.tokenize import sent_tokenize
from dotenv import load_dotenv

nltk.download('punkt')
load_dotenv()

# Get the path to 'source_documents' within the current directory
pdf_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'source_documents')

# Function to process a single PDF file
def process_pdf(pdf_path):
    # Open PDF file
    with open(pdf_path, 'rb') as pdf_file:
        # Create PDF reader object
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        
        # Extract text from PDF
        text = ""
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            page_text = page.extract_text()
            text += page_text

        # Tokenize text into sentences
        sentences = sent_tokenize(text)

        # Group sentences into paragraphs
        paragraphs = []
        current_para = []
        for sentence in sentences:
            if sentence.strip() == "":
                paragraphs.append(" ".join(current_para))
                current_para = []
            else:
                current_para.append(sentence)

        if current_para:
            paragraphs.append(" ".join(current_para))

        # Write paragraphs to output file
        output_file_name = os.path.basename(pdf_path).replace(".pdf", "_Source.txt")
        output_file_path = os.path.join(pdf_dir, output_file_name)
        with open(output_file_path, 'w', encoding='utf-8') as output_file:
            for para in paragraphs:
                output_file.write(para + "\n")

        # Process output file to join sentences with spaces instead of newlines
        with open(output_file_path, 'r', encoding='utf-8') as original_file:
            original_text = original_file.read()

        # Join sentences with spaces instead of newlines
        processed_text = original_text.replace("\n", " ")

        # Write processed text to a new output file
        output_combined_file_path = os.path.join(pdf_dir, output_file_name.replace("_Source.txt", "_Combined.txt"))
        with open(output_combined_file_path, 'w', encoding='utf-8') as output_combined_file:
            output_combined_file.write(processed_text)

# Process all PDF files in the 'source_documents' directory
for filename in os.listdir(pdf_dir):
    if filename.endswith(".pdf"):
        pdf_path = os.path.join(pdf_dir, filename)
        process_pdf(pdf_path)
