import pandas as pd
import genanki
import os
import logging
import re
import requests
import urllib.parse

# Paths and configuration
csv_path = './Hakka Vocabulary.csv'
output_deck_path = './hakka_language_deck_with_diacritics_and_sound.apkg'
log_file = './hakka_with_diacritics_and_sound_anki.log'
audio_folder = './audio'

# Hakka TTS API
TTS_API_URL = "https://Chaak2.pythonanywhere.com/TTS/hakka"

# Tone mapping (Diacritics) Ref： http://www.hkilang.org/v2/%e7%99%bc%e9%9f%b3%e5%ad%97%e5%85%b8/
# Ref： p433 香港客家话研究
# Hong Kong Hakka is part of the Huiyang dialect.

TONE_DIACRITICS = {
    '1': '\u0301',  # acute (́ ) 陰平聲
    '2': '\u0304',  # macron (ˉ) 陽平聲
    '3': '\u030c',  # caron (̌ ) 上聲
    '4': '\u0300',  # grave (̀ ) 去聲
    '5': '\u030c',  # caron (̌ ) (short tone) 陰入聲
    '6': '\u0300'   # grave (̀ ) (short tone) 陽入聲
}

# Tone color mapping for Anki
TONE_COLORS = {
    '1': 'red',
    '2': 'blue',
    '3': 'green',
    '4': 'purple',
    '5': 'orange',
    '6': 'yellow'
}

# Set up logging
logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(message)s')
verbose = True  # Default verbose mode

def log_message(message, is_error=False):
    if verbose:
        print(message)
    if is_error:
        logging.error(message)
    else:
        logging.info(message)

def apply_tone_color(text, tone_number):
    """ Wraps the text in a span with the appropriate tone color for Anki. """
    if tone_number in TONE_COLORS:
        return f'<span style="color: {TONE_COLORS[tone_number]};">{text}</span>'
    return text

def strip_html(text):
    """ Removes HTML tags from the text. """
    return re.sub(r'<.*?>', '', text)

def colorize_character(character, pronunciation):
    """ Matches each Chinese character with the corresponding tone color from pronunciation. """
    tone_numbers = re.findall(r'[1-6]', pronunciation)  # Extract all tone numbers
    colored_chars = []
    for i, char in enumerate(character):
        if i < len(tone_numbers):
            colored_chars.append(apply_tone_color(char, tone_numbers[i]))
        else:
            colored_chars.append(char)  # No tone number available, keep default color
    return ''.join(colored_chars)

def convert_tone_numbers_to_diacritics(pronunciation):
    """ Converts tone numbers (e.g., ngai2) to diacritics (e.g., ngái) with color-coding for Anki. """
    def replace_tone(match):
        syllable, tone_number = match.group(1), match.group(2)
        if tone_number in TONE_DIACRITICS:
            vowels = [i for i, c in enumerate(syllable) if c in "aeiouAEIOU"]
            if len(vowels) >= 2:
                target_index = vowels[-2]
                modified_syllable = (
                    syllable[:target_index + 1]
                    + TONE_DIACRITICS[tone_number]
                    + syllable[target_index + 1:]
                )
            elif vowels:
                target_index = vowels[0]
                modified_syllable = (
                    syllable[:target_index + 1]
                    + TONE_DIACRITICS[tone_number]
                    + syllable[target_index + 1:]
                )
            else:
                modified_syllable = syllable
            return apply_tone_color(modified_syllable, tone_number)
        return syllable
    return re.sub(r"([a-zA-Z]+)([1-6])", replace_tone, pronunciation)

def fetch_tts_audio(pronunciation_api, filename, voice="male", speed="1"):  
    """ 
    Calls the Hakka TTS API to generate an audio file while handling various HTTP errors. 
    
    For Hong Kong Hakka TTS - https://hkilang.github.io/TTS/
    For the source, please see here - https://github.com/hkilang/TTS/tree/main
    For the API, please see here - https://github.com/hkilang/TTS-API/tree/main
    
    """
    
    filepath = os.path.join(audio_folder, filename)
    # Check if file exists before downloading
    if os.path.exists(filepath):
        log_message(f"Audio file already exists: {filename}. Skipping download.")
        return filename
    
    log_message(f"Encoded TTS Text: {pronunciation_api}")  # Debugging output
    url = f"{TTS_API_URL}/{pronunciation_api}?voice={voice}&speed={speed}"
    log_message(f"Fetching TTS from URL: {url}")

    try:
        response = requests.get(url, stream=True, timeout=10)
        response.raise_for_status()  # Ensure we catch HTTP errors like 404, 500, etc.

        filepath = os.path.join(audio_folder, filename)
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        log_message(f"Audio saved: {filepath}")
        return filename

    except requests.exceptions.HTTPError as http_err:
        log_message(f"HTTP error occurred: {http_err} - Status Code: {response.status_code}", is_error=True)
    except requests.exceptions.ConnectionError as conn_err:
        log_message(f"Connection error occurred: {conn_err}", is_error=True)
    except requests.exceptions.Timeout as timeout_err:
        log_message(f"Timeout error occurred: {timeout_err}", is_error=True)
    except requests.exceptions.RequestException as req_err:
        log_message(f"An error occurred: {req_err}", is_error=True)

    return None

def create_deck(df, output_path, is_test=False, no_audio=False):
    log_message("Creating Anki deck...")

    if is_test:
        df = df.head(5)
        log_message("Test mode enabled: Only processing the first 5 rows.")

    if not os.path.exists(audio_folder):
        os.makedirs(audio_folder)

    model = genanki.Model(
        1607392319,
        'Hakka Flashcard Model with Diacritics & Audio',
        fields=[
            {'name': 'Character'},
            {'name': 'Pronunciation'},
            {'name': 'StandardChinese'},
            {'name': 'English'},
            {'name': 'Audio'}
        ],
        templates=[
            {
                'name': 'Card 1',
                'qfmt': '''
                    <div style="font-size: 50px; text-align: center;">{{Character}}</div>
                ''',
                'afmt': '''
                    <div style="font-size: 50px; text-align: center;">{{Character}}</div>
                    <div style="font-size: 40px; text-align: center; margin-top: 20px;">
                        <strong>Hakka Pronunciation:</strong> {{Pronunciation}}
                    </div>
                    <div style="font-size: 30px; text-align: center; margin-top: 15px;">
                        <strong>普通中文:</strong> {{StandardChinese}}
                    </div>
                    <div style="font-size: 30px; text-align: center; margin-top: 15px;">
                        <strong>Eng:</strong> {{English}}
                    </div>
                    <div style="text-align: center;">
                        {{Audio}}
                    </div>
                ''',
            },
        ])

    deck = genanki.Deck(2059400110, 'Fui Yong Hakka Language Deck with Diacritics & Audio')

    media_files = []  # List to collect audio file paths

    for _, row in df.iterrows():
        try:
            character = str(row['客家汉字'])
            pronunciation = str(row['Hakka Pronunciation'])
            colored_character = colorize_character(character, pronunciation)
            pronunciation = convert_tone_numbers_to_diacritics(pronunciation)
            standard_chinese = str(row['普通中文'])
            english = str(row['English Definition'])
            pronunciation_api = str(row['Hakka Pronunciation'])

            if no_audio:
                audio_field = ""
            else:
                audio_filename = f"{character}.mp3"
                audio_path = fetch_tts_audio(pronunciation_api, audio_filename)
                if audio_path:
                    # Using standard [sound:...] markup so Anki knows to play it
                    audio_field = f"[sound:{audio_filename}]"
                    # Append the full path to the audio file for packaging
                    media_files.append(os.path.join(audio_folder, audio_filename))
                else:
                    audio_field = ""

            note = genanki.Note(model=model, fields=[colored_character, pronunciation, standard_chinese, english, audio_field])
            deck.add_note(note)

        except Exception as e:
            log_message(f"Error processing row: {row}. Error: {e}", is_error=True)

    log_message("Saving Anki deck...")
    genanki.Package(deck, media_files=media_files).write_to_file(output_path)
    log_message(f"Anki deck created successfully: {output_path}")

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="Generate an Anki deck with diacritic conversion.")
    parser.add_argument('--test', action='store_true', help="Test mode: Generate only 5 cards.")
    parser.add_argument('--verbose', action='store_true', help="Verbose mode for detailed logging.")
    parser.add_argument('--no-audio', action='store_true', help="Skip audio generation.")
    args = parser.parse_args()
    verbose = args.verbose
    no_audio = args.no_audio
    log_message("Loading CSV file...")
    try:
        df = pd.read_csv(csv_path, encoding='utf-8')
        create_deck(df, output_deck_path, is_test=args.test, no_audio=no_audio)
    except Exception as e:
        log_message(f"Script failed: {e}", is_error=True)