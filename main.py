import os
from summarize import summarize_text_bert, read_text_from_file as read_text_for_summarization, fetch_text_from_url as fetch_text_for_summarization
from translate import TranslatorHelper, read_text_from_file as read_text_for_translation, fetch_text_from_url as fetch_text_for_translation

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
                        text = read_text_for_summarization(file_path)
                    else:
                        text = read_text_for_translation(file_path)
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
                        text = fetch_text_for_summarization(url)
                    else:
                        text = fetch_text_for_translation(url)
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
                    summary = summarize_text_bert(text)
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
