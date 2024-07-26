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

