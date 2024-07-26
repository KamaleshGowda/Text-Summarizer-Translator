import os
import fitz  # PyMuPDF
import requests
from bs4 import BeautifulSoup
from summarize import summarize_text_bert
from translate import TranslatorHelper

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
        text = ''
        with fitz.open(file_path) as pdf_file:
            num_pages = len(pdf_file)
            for page_num in range(num_pages):
                page = pdf_file.load_page(page_num)
                text += page.get_text()
        return text
    except FileNotFoundError:
        raise FileNotFoundError(f"PDF file '{file_path}' not found.")
    except Exception as e:
        raise Exception(f"Error extracting text from PDF '{file_path}': {e}")

def fetch_text_from_url(url):
    """
    Fetches text content from a given URL using web scraping.
    
    Parameters:
    - url (str): The URL of the web page.
    
    Returns:
    - text (str): The text content extracted from the web page.
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

def main():
    """
    Main function to run the summarizer and translator. Provides an interactive command-line interface.
    """
    while True:
        print("Enter '1' to summarize text, '2' to translate text (or 'q' to quit):")
        choice = input().strip()

        if choice == 'q':
            print("Exiting program.")
            break
        
        text = ""  # Initialize text variable
        
        if choice in ['1', '2']:
            print("Enter '1' to enter text from terminal, '2' to read from a text file, '3' to read from a PDF file, '4' to read from a URL (or 'q' to quit):")
            input_choice = input().strip()
            
            if input_choice == 'q':
                break
            
            if input_choice == '1':
                print("Please enter the text (end with an empty line):")
                input_text = []
                while True:
                    line = input()
                    if line:
                        input_text.append(line)
                    else:
                        break
                text = ' '.join(input_text)
            
            elif input_choice in ['2', '3']:
                file_type = "text" if input_choice == '2' else "PDF"
                file_path = input(f"Please enter the path to the {file_type} file (or 'q' to quit): ").strip()
                if file_path.lower() == 'q':
                    break
                
                try:
                    if choice == '1':
                        text = read_text_from_file(file_path)
                    else:
                        text = read_text_from_file(file_path)
                    print(f"{file_type.capitalize()} read from file '{file_path}':")
                    print(text[:500] + '...')  # Debug print to verify text content
                except FileNotFoundError:
                    print(f"File '{file_path}' not found. Please enter a valid file path.")
                    continue
                except ValueError as ve:
                    print(ve)
                    continue
                except Exception as e:
                    print(f"Error reading {file_type} file '{file_path}': {e}")
                    continue
            
            elif input_choice == '4':
                url = input("Please enter the URL (or 'q' to quit): ").strip()
                if url.lower() == 'q':
                    break
                
                try:
                    if choice == '1':
                        text = fetch_text_from_url(url)
                    else:
                        text = fetch_text_from_url(url)
                    print(f"Text fetched from URL '{url}':")
                    print(text[:500] + '...')  # Debug print to display part of the fetched text
                except Exception as e:
                    print(f"Error fetching content from URL '{url}': {e}")
                    continue
            
            else:
                print("Invalid choice. Please enter '1', '2', '3', '4', or 'q'.")
                continue
        
            if text.strip():  # Check if text is not empty
                if choice == '1':
                    while True:
                        try:
                            num_lines = int(input("Enter the number of lines for the summary: "))
                            break
                        except ValueError:
                            print("Please enter a valid number.")
                    
                    summary = summarize_text_bert(text, num_sentences=num_lines)
                    print("\nSummary:")
                    print(summary)
                    
                    # Save summary to a file
                    save_path = input("Enter the path to save the summary (or 'n' to skip saving): ").strip()
                    if save_path.lower() != 'n':
                        try:
                            with open(save_path, 'w', encoding='utf-8') as file:
                                file.write(summary)
                            print(f"Summary saved to '{save_path}' successfully.")
                        except Exception as e:
                            print(f"Error saving summary to '{save_path}': {e}")
                
                elif choice == '2':
                    while True:
                        try:
                            # Language Codes
                            print("\nLanguage Codes:")
                            print("Indian Languages: Hindi (hi), Bengali (bn), Tamil (ta), Telugu (te), Marathi (mr), Gujarati (gu), Kannada (kn)")
                            print("International Languages: Spanish (es), French (fr), German (de), Japanese (ja), Arabic (ar), Russian (ru)\n")

                            src_lang = input("Enter the source language code (e.g., 'en' for English): ").strip()
                            tgt_lang = input("Enter the target language code (e.g., 'hi' for Hindi): ").strip()
                            
                            if len(src_lang) != 2 or len(tgt_lang) != 2:
                                raise ValueError("Language codes should be exactly two characters.")
                            
                            translator = TranslatorHelper(source_language=src_lang)
                            translated_text = translator.translate_text(text, dest_language_code=tgt_lang)
                            print("\nTranslated Text:")
                            print(translated_text)
                            
                            # Save translated text to a file
                            save_path = input("Enter the path to save the translated text (or 'n' to skip saving): ").strip()
                            if save_path.lower() != 'n':
                                try:
                                    with open(save_path, 'w', encoding='utf-8') as file:
                                        file.write(translated_text)
                                    print(f"Translated text saved to '{save_path}' successfully.")
                                except Exception as e:
                                    print(f"Error saving translated text to '{save_path}': {e}")
                            
                            break  # Exit language input loop
                        
                        except ValueError as ve:
                            print(f"Invalid input: {ve}")
                            continue
                        except Exception as e:
                            print(f"Translation error: {e}")
                            continue
            else:
                print("Input text is empty. Cannot summarize or translate.")
        
        else:
            print("Invalid choice. Please enter '1', '2', or 'q'.")
    
    print("Exiting program.")

if __name__ == "__main__":
    main()
