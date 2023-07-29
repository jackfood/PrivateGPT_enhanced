import win32com.client
import os
import re
from tqdm import tqdm
from transformers import BartTokenizer, BartForConditionalGeneration  
import time
print("Script started")
# Set up Outlook application
try:
    outlook = win32com.client.Dispatch("Outlook.Application") 
except Exception as e:
    print("Error creating Outlook application:", e)
    outlook = None
if outlook:
    print("Outlook application created")
    # Get the namespace
    try:
        namespace = outlook.GetNamespace("MAPI")
        print("Got namespace")
    except Exception as e:
        print("Error getting namespace:", e)
        namespace = None
        
if namespace:
    print("Got namespace")
    # Get the inbox folder
    try:
        inbox = namespace.GetDefaultFolder(6)
        print("Got inbox")
    except Exception as e:
        print("Error getting Inbox folder:", e)
        inbox = None
        
if inbox:
    print("Got inbox")
    # Get emails and sort by received time
    try:
        emails = inbox.Items
        emails.Sort("[ReceivedTime]", True)
        print("Got emails")
    except Exception as e:
        print("Error getting emails:", e)
        emails = []
        
# Check if emails found        
if len(emails) == 0:
    print("No emails found in Inbox")
else:
    print(f"Found {len(emails)} emails")
    
    # Create output directory
    save_dir = r'D:\Users\gnulch2\Desktop' 
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
        print("Created output directory")
    
    # Load model
    try:
        model_path = r'D:\PrivateGPT\.cache\huggingface\hub\models--facebook--bart-large-cnn\snapshots\3d224934c6541b2b9147e023c2f6f6fe49bd27e1'
        tokenizer = BartTokenizer.from_pretrained(model_path)
        model = BartForConditionalGeneration.from_pretrained(model_path)
        print("Loaded model")
    except Exception as e: 
        print("Error loading model:", e)
        model, tokenizer = None, None
    
    if model and tokenizer:
        # Track time
        start_time = time.time()
        
        # Summarize emails
        summary_length = 1024
        for i in range(min(100000, len(emails))):
            print(f"Processing email {i+1}/{len(emails)}")
            email = emails[i]
            
            # Check if summary already exists
            try:
                subject = email.Subject 
                save_path = os.path.join(save_dir, f"{subject}.txt")
                if os.path.exists(save_path):
                    print(f"Summary for {subject} already exists, skipping")
                    continue
            except Exception as e:
                print(f"Error checking for existing summary:", e)
            
            try:
                subject = email.Subject
                body = email.Body
                print(f"Got content for email {i+1}")
            except Exception as e:
                print(f"Error getting email {i+1} content:", e)
                continue
            
            # Extract text
            try:
                text_content = re.sub('<[^<>]*>', '', body)
                text_content = text_content.replace('\n', '') 
                print(f"Preprocessed email {i+1}")
            except Exception as e:
                print(f"Error preprocessing email {i+1}:", e)
                continue
            
            # Summarize
         
            try:
                chunks = [text_content[i:i+summary_length] for i in range(0, len(text_content), summary_length)]
                summarized_text = ""
                for chunk in tqdm(chunks, desc=f"Summarizing email {i+1}", unit="chunk"):
                    inputs = tokenizer.batch_encode_plus([chunk], return_tensors='pt', max_length=summary_length, truncation=True)
                    summary_ids = model.generate(inputs['input_ids'], num_beams=4, max_length=summary_length, early_stopping=True)
                    summary = tokenizer.decode(summary_ids.squeeze(), skip_special_tokens=True)
                    summarized_text += summary + " "
                print(f"Summarized email {i+1}")
            except Exception as e:
                print(f"Error summarizing email {i+1}:", e)
                continue
            
            # Save summary
            try:
                date_str = time.strftime("%Y-%m-%d %H:%M:%S") 
            except:
                date_str = ""
            
            try:
                save_path = os.path.join(save_dir, re.sub(r'[^\w\s-]', '', subject) + ".txt")
                with open(save_path, 'w', encoding='utf-8') as f:
                    f.write(f"Subject: {subject}\n")
                    if date_str: 
                        f.write(f"Date: {date_str}\n\n")
                    f.write(f"Summary:\n{summarized_text}\n")
                print(f"Saved summary for email {i+1}")
            except Exception as e:
                print(f"Error saving summary for email {i+1}:", e)
            
        print(f"Processed {i+1} emails in {time.time() - start_time} seconds")
        
print("Script finished")