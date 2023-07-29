#!/usr/bin/env python3
import os
import argparse
import tkinter as tk
from tkinter import scrolledtext, END
from dotenv import load_dotenv
from langchain.chains import RetrievalQA
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.vectorstores import Chroma
from langchain.llms import GPT4All, LlamaCpp
import threading
import time

load_dotenv()

embeddings_model_name = os.environ.get("EMBEDDINGS_MODEL_NAME")
persist_directory = os.environ.get('PERSIST_DIRECTORY')

model_type = os.environ.get('MODEL_TYPE')
model_path = os.environ.get('MODEL_PATH')
model_n_ctx = os.environ.get('MODEL_N_CTX')
model_n_threads = os.environ.get('MODEL_N_THREADS')
target_source_chunks = int(os.environ.get('TARGET_SOURCE_CHUNKS', 4))
n_gpu_layers = os.environ.get('N_GPU_LAYERS')
use_mlock = os.environ.get('USE_MLOCK')
n_batch = os.environ.get('N_BATCH') if os.environ.get('N_BATCH') else 512

from constants import CHROMA_SETTINGS

class GPTThread(threading.Thread):
    def __init__(self, query, qa):
        threading.Thread.__init__(self)
        self.query = query
        self.qa = qa
        self.result = None
        self.running = True

    def run(self):
        self.result = self.qa(self.query)
        self.running = False

def main():
    # Parse the command line arguments
    args = parse_arguments()
    embeddings = HuggingFaceEmbeddings(model_name=embeddings_model_name)
    db = Chroma(persist_directory=persist_directory, embedding_function=embeddings, client_settings=CHROMA_SETTINGS)
    retriever = db.as_retriever(search_kwargs={"k": target_source_chunks})
    # activate/deactivate the streaming StdOut callback for LLMs
    callbacks = [] if args.mute_stream else [StreamingStdOutCallbackHandler()]
    # Prepare the LLM
    match model_type:
        case "LlamaCpp":
            llm = LlamaCpp(model_path=model_path, n_batch=n_batch, n_ctx=model_n_ctx, use_mlock=use_mlock,
                           n_gpu_layers=n_gpu_layers, n_threads=model_n_threads, callbacks=callbacks, verbose=False)
        case "GPT4All":
            llm = GPT4All(model=model_path, n_ctx=model_n_ctx, backend='gptj', callbacks=callbacks, verbose=False)
        case _default:
            print(f"Model {model_type} not supported!")
            exit;

    qa = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=retriever, return_source_documents=not args.hide_source)

    def update_answer():
        if gpt_thread.running and gpt_thread.result is None:
            answer_text.delete(1.0, END)
            answer_text.insert(tk.END, "Generating answer. Please wait...")
            root.update()
            root.after(200, update_answer)  # Schedule the function to run again after 200 milliseconds (0.2 seconds)
        elif not gpt_thread.running and gpt_thread.result is not None:
            answer_text.delete(1.0, END)
            answer_text.insert(tk.END, f"Question:\n{query_entry.get()}\n\nAnswer:\n{gpt_thread.result['result']}")
        else:
            root.after(200, update_answer)  # Schedule the function to run again after 200 milliseconds (0.2 seconds)



    def submit_query():
        global gpt_thread
        query = query_entry.get()
        if query:
            # Start the GPT thread for answer generation
            gpt_thread = GPTThread(query, qa)
            gpt_thread.start()
            # Start the thread to update the answer during generation
            update_thread = threading.Thread(target=update_answer)
            update_thread.start()

    def submit_query_on_enter(event):
        submit_query()

    # Create the GUI
    root = tk.Tk()
    root.title("PrivateGPT GUI")
    root.geometry("800x600")
    root.configure(background='white')

    # Text entry box for query
    query_label = tk.Label(root, text="Enter your query:", font=("Arial", 14), bg='white')
    query_label.pack(pady=10)
    query_entry = tk.Entry(root, font=("Arial", 14), width=50)
    query_entry.pack(pady=10)

    # Text area to display the answer
    answer_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, font=("Arial", 11), height=10)
    answer_text.pack(pady=10)

    # Display chunk size, MODEL_N_THREADS, and MODEL_PATH in the top right corner
    info_label = tk.Label(root, text=f"Chunk Size: {target_source_chunks}\nThreads: {model_n_threads}\nModel: {model_path}",
                          font=("Arial", 10), bg='white', fg='gray', anchor='se')
    info_label.pack(side='bottom', anchor='se', padx=10, pady=10)

    # Bind the 'Return' key to the submit_query_on_enter function
    query_entry.bind("<Return>", submit_query_on_enter)

    # Submit button
    submit_button = tk.Button(root, text="Submit", font=("Arial", 14), command=submit_query, bg='blue', fg='white')
    submit_button.pack(pady=10)

    root.mainloop()

def parse_arguments():
    parser = argparse.ArgumentParser(description='privateGPT: Ask questions to your documents without an internet connection, '
                                                 'using the power of LLMs.')
    parser.add_argument("--hide-source", "-S", action='store_true',
                        help='Use this flag to disable printing of source documents used for answers.')

    parser.add_argument("--mute-stream", "-M",
                        action='store_true',
                        help='Use this flag to disable the streaming StdOut callback for LLMs.')

    return parser.parse_args()


if __name__ == "__main__":
    main()
