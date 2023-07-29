from llama_cpp import Llama
from dotenv import load_dotenv
import os
import glob

load_dotenv()

model_path_env = os.environ.get('MODEL_PATH_SUMMARY_LMM')
n_batch_env = int(os.environ.get('N_BATCH')) #integer
model_n_ctx = int(os.environ.get('MODEL_N_CTX_SUMMARY_LMM')) #integer
model_n_threads = int(os.environ.get('MODEL_N_THREADS')) #integer
use_mlock = bool(int(os.environ.get('USE_MLOCK')))  #Boolean
n_gpu_layers = int(os.environ.get('N_GPU_LAYERS'))  #integer
input_folder_env = os.environ.get('INPUT_folder_SUMMARY_LLM')
output_dir_env = os.environ.get('OUTPUT_DIR_SUMMARY_LLM')
summary_token = int(os.environ.get('SUMMARY_MAXTOKEN_SIZE_SUMMARY_LMM')) #integer

# Load the llama model
print("Loading Llama model...")
try:
    llm = Llama(model_path="./models/llama-2-7b-chat.ggmlv3.q5_K_M.bin", n_ctx=model_n_ctx, n_threads=model_n_threads)
    print("Llama model loaded successfully.")
except Exception as e:
    print("Error loading the Llama model:", str(e))
    exit(1)

def generate_text(
    prompt="You are a helpful assistant. Be Honest.",
    max_tokens=summary_token,
    temperature=0.1,
    top_p=0.5,
    echo=False,
    stop=["#"],  # Fix the stop parameter to be a string
):
    print("Generating text...")
    try:
        output = llm(
            prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            echo=echo,
            stop=stop,
        )
        output_text = output["choices"][0]["text"].strip()
        print("Text generated successfully.")
        return output_text
    except Exception as e:
        print("Error generating text:", str(e))
        return None

def summarize_text_from_file(input_file_path, output_file_path, callback=None):
    # Read the prompt text from the input file using utf-8 encoding
    with open(input_file_path, "r", encoding="utf-8") as file:
        prompt_text = file.read()

    # Generate the summary using the prompt text - increase the token for longer summaries
    summary_text = generate_text(prompt=prompt_text, max_tokens=summary_token)

    if summary_text:
        # Save the summary to the output file
        with open(output_file_path, "w", encoding="utf-8") as file:
            file.write(summary_text)
        print(f"Summary saved to '{output_file_path}'.")
    else:
        print("Error generating summary. Summary not saved.")

# List all the TXT files in the input folder
txt_files = glob.glob(os.path.join(input_folder_env, "*.txt"))

# Process each TXT file and generate summaries
total_files = len(txt_files)
for i, txt_file in enumerate(txt_files, 1):
    # Extract the title of the TXT file
    title = os.path.splitext(os.path.basename(txt_file))[0]

    # Define the output file path for the summary
    output_file_path = os.path.join(output_dir_env, f"{title}_summaries.txt")

    print(f"\nProcessing file {i}/{total_files} - '{txt_file}'")
    # Call the function to summarize the text from the input file and save it to the output file
    summarize_text_from_file(txt_file, output_file_path)
