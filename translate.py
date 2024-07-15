import requests
from bs4 import BeautifulSoup
from time import sleep
from googletrans import Translator
import backoff

class TranslatorHelper:
    def __init__(self, source_language="en"):
        self.client = Translator()
        self.sleep_in_between_translations_seconds = 10
        self.source_language = source_language
        self.max_chunk_size = 4000

    def __create_chunks(self, corpus):
        chunks = [corpus[i:i + self.max_chunk_size] for i in range(0, len(corpus), self.max_chunk_size)]
        return chunks

    def __sleep_between_queries(self):
        print(f'Sleeping for {self.sleep_in_between_translations_seconds}s after translation query..')
        sleep(self.sleep_in_between_translations_seconds)

    @backoff.on_exception(backoff.expo, Exception, max_tries=5)
    def translate_text(self, content, dest_language_code):
        try:
            print(f'Attempting to translate to lang={dest_language_code}')
            if len(content) > self.max_chunk_size:
                print(f'Warning: Content is longer than allowed size of {self.max_chunk_size}, breaking into chunks')
                results_list = []
                concatenated_result = ""
                original_chunks = self.__create_chunks(content)
                for chunk in original_chunks:
                    result = self.client.translate(chunk, dest=dest_language_code, src=self.source_language)
                    self.__sleep_between_queries()
                    results_list.append(result.text)
                concatenated_result = ''.join(results_list)
                return concatenated_result
            else:
                result = self.client.translate(content, dest=dest_language_code, src=self.source_language)
                self.__sleep_between_queries()
                return result.text
        except Exception as e:
            print(e)
            raise e

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
        import fitz  # PyMuPDF
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
