import nltk
from nltk.tokenize import sent_tokenize
from transformers import BertTokenizer, BertModel
from sklearn.metrics.pairwise import cosine_similarity
import torch 

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
