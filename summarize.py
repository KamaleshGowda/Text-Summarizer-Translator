import nltk
from nltk.tokenize import sent_tokenize
from transformers import BertTokenizer, BertModel
from sklearn.metrics.pairwise import cosine_similarity
import torch 
import requests
from bs4 import BeautifulSoup

# Ensure necessary NLTK data is downloaded
nltk.download('punkt')

def summarize_text_bert(text, num_sentences=5):
    """
    Summarizes the given text using BERT embeddings.
    
    Parameters:
    - text (str): The input text to be summarized.
    - num_sentences (int): The number of sentences for the summary.
    
    Returns:
    - summary (str): The generated summary.
    """
    # Step 1: Split the text into sentences
    sentences = sent_tokenize(text)
    
    # Step 2: Initialize BERT tokenizer and model
    tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
    model = BertModel.from_pretrained('bert-base-uncased')
    
    # Step 3: Encode sentences using BERT
    encoded_sentences = [tokenizer.encode_plus(sent, add_special_tokens=True, max_length=512, truncation=True, padding='max_length', return_tensors='pt') for sent in sentences]
    
    # Combine the encoded sentences into a single tensor
    input_ids = torch.cat([item['input_ids'] for item in encoded_sentences])
    attention_mask = torch.cat([item['attention_mask'] for item in encoded_sentences])
    
    with torch.no_grad():
        outputs = model(input_ids, attention_mask=attention_mask)
        embeddings = outputs.last_hidden_state.mean(dim=1)
    
    # Step 4: Calculate sentence scores based on cosine similarity with the document embedding
    document_embedding = embeddings.mean(dim=0, keepdim=True)
    cosine_scores = cosine_similarity(embeddings.numpy(), document_embedding.numpy())
    sentence_scores = cosine_scores.flatten()
    
    # Step 5: Get the indices of the top sentences
    top_sentence_indices = sentence_scores.argsort()[-num_sentences:][::-1]
    
    # Step 6: Select the top sentences
    summary_sentences = [sentences[i] for i in sorted(top_sentence_indices)]
    
    # Step 7: Combine the top sentences into a summary
    summary = ' '.join(summary_sentences)
    
    return summary

def read_text_from_file(file_path):
    """
    Reads text from a given file path. Supports .txt and .pdf files.
    
    Parameters:
    - file_path (str): The path to the input file.
    
    Returns:
    - text (str): The text extracted from the file.
    """
    file_extension = file_path.split('.')[-1].lower()
    try:
        if file_extension == 'pdf':
            return read_pdf_text(file_path)
        elif file_extension in ['txt', 'text']:
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()
            return text
        else:
            raise ValueError(f"Unsupported file format: '{file_extension}'. Only .txt and .pdf files are supported.")
    except FileNotFoundError:
        raise FileNotFoundError(f"File '{file_path}' not found.")
    except Exception as e:
        raise Exception(f"Error reading file '{file_path}': {e}")

def read_pdf_text(file_path):
    """
    Reads text from a PDF file.
    
    Parameters:
    - file_path (str): The path to the PDF file.
    
    Returns:
    - text (str): The text extracted from the PDF.
    """
    try:
        import fitz  # PyMuPDF is imported as fitz
        text = ''
        pdf_file = fitz.open(file_path)
        num_pages = len(pdf_file)
        
        for page_num in range(num_pages):
            page = pdf_file.load_page(page_num)
            text += page.get_text()
        
        pdf_file.close()
        return text
    except Exception as e:
        raise Exception(f"Error extracting text from PDF '{file_path}': {e}")

def fetch_text_from_url(url):
    """
    Fetches text content from a given URL using web scraping.
    
    Parameters:
    - url (str): The URL of the web page.
    
    Returns:
    - text (str): The extracted text content from the web page.
    """
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        paragraphs = soup.find_all('p')
        text = ' '.join([para.get_text() for para in paragraphs])
        return text
    except Exception as e:
        raise Exception(f"Error fetching content from URL '{url}': {e}")