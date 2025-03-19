# Hong Kong Hakka AnkiDeck Generator

This repository contains a Python script that generates an Anki deck for learning **fui4 yong2 (惠陽) Hakka**. It not only converts tone numbers to diacritics with colour-coding based on the "香港客家话研究" textbook by **劉鎮發 (liu2 zin3 fat5)** but also integrates audio by utilising the new **Fui Yong Hakka TTS model**. The script calls the **Hakka TTS API** to generate audio files while handling various HTTP errors and packages them into the final Anki deck.

![image](https://github.com/user-attachments/assets/72308faf-d61e-4701-9041-6bcc7a1afa10)

## What is Fui Yong Hakka 惠陽客家?

Fui Yong Hakka (惠陽客家) refers to the distinct group of Hakka people originating from Huiyang (惠陽) originally, a region in Guangdong Province, Southern China. Today, the Fui Yong dialect is spoken in Hong Kong, Malaysia, Singapore, Indonesia, Vietnam, Thailand, (mostly South East Asia) as well as within diaspora communities in the United Kingdom, Australia, Canada, and the United States.

While Fui Yong Hakka shares similarities with other Hakka dialects, it differs notably from those spoken in Taiwan, such as Sixian (四縣) and Hailu (海陸). These differences arose from distinct historical migration periods, isolation, and interactions with neighbouring languages. Taiwan Hakka dialects were influenced by prolonged contact with Minnan (Hokkien), Indigenous Formosan languages, and Japanese colonisation, resulting in noticeable divergence in pronunciation, vocabulary, and grammar. In contrast, Fui Yong Hakka has maintained closer ties to Cantonese and regional languages in Southern China, reflecting the geographic and cultural influences specific to Guangdong and other South East Asian countries.

## Features

- **Tone Diacritic Conversion**:  
  Converts tone numbers (e.g., `ngai2`) into diacritic forms (e.g., `ngái`) using mappings inspired by the "香港客家话研究" textbook.

- **Colour Coding**:  
  Applies specific colours to Chinese characters based on their tones to enhance visual learning.

- **Audio Integration**:  
  Downloads audio files via the **Hakka TTS API** (only if the file doesn't already exist) and embeds them in the Anki deck using `[sound:...]` markup.

- **Error Handling**:  
  Handles various HTTP errors (404, 500, connection issues, timeouts) when fetching audio.

- **Anki Deck Packaging**:  
  Uses `genanki` to compile vocabulary, diacritics, colour coding, and audio into a self-contained `.apkg` file ready for import into Anki.

## Prerequisites

- **Python 3.x**

- **Required Python Libraries**:
  - `pandas`
  - `genanki`
  - `requests`

You can install the necessary libraries using pip:

```bash
pip install pandas genanki requests
```

## Setup and Usage

- **Prepare Your CSV File**  
  Create or update the `Hakka Vocabulary.csv` file with the following columns:

  * **客家汉字**: Hakka characters.
  * **Hakka Pronunciation**: Pronunciation with tone numbers.
  * **普通中文**: Standard Chinese translation.
  * **English Definition**: English explanation/definition.

- **Run the Script**  
  Execute the script with the desired command-line options:

  ```bash
  python create_anki_deck_with_diacritics_and_sound.py [--test] [--verbose] [--no-audio]
  ```

  * `--test`: Processes only the first 5 rows (for testing purposes).
  * `--verbose`: Enables detailed logging.
  * `--no-audio`: Skips audio generation if you want to generate a deck without audio files. (with sound, the anki deck becomes around 200MB!)
  
- **Output**  
  The script will generate an Anki deck file named `hakka_language_deck_with_diacritics_and_sound.apkg` and store audio files in the `audio` directory. The audio files are also merged into the deck file so that the deck is self-contained.

## How It Works

- **Tone Conversion & Colour Coding**  
  The script reads vocabulary data from the CSV file, converts tone numbers into diacritics, and applies colour coding based on tone. This conversion is based on tone mappings provided in the "香港客家话研究" textbook by **劉鎮發**.

- **Audio File Generation**  
  For each vocabulary entry, the script checks if an audio file already exists in the `audio` folder. If not, it calls the **Hakka TTS API** to generate the audio file. This API call is robust, handling HTTP errors and timeouts gracefully.

- **Deck Creation**  
  The script uses `genanki` to create flashcards with the following fields:

  * **Character**: The Hakka character with colour coding.
  * **Pronunciation**: The tone-converted and colour-coded pronunciation.
  * **StandardChinese**: The standard Chinese translation.
  * **English**: The English definition.
  * **Audio**: Embedded audio using the `[sound:...]` markup.

  Audio files are included in the final `.apkg` file by specifying them in the `media_files` parameter of `genanki.Package`.

## Future areas to improve

* Provide option to keep numbered tones for those who prefer.
* Add more vocabulary and phrases
* Also open to any feedback or requests so feel free to submit issues.

## References

**Source Material**:  
"香港客家话研究" by **劉鎮發 (liu2 zin3 fat5)** – provides the tone and language basis for the diacritic conversion.

**Fui Yong Hakka TTS Model & API**:

- **Hong Kong Hakka TTS**: [https://hkilang.github.io/TTS/](https://hkilang.github.io/TTS/)
- **Source Code**: [https://github.com/hkilang/TTS/tree/main](https://github.com/hkilang/TTS/tree/main)
- **TTS API**: [https://github.com/hkilang/TTS-API/tree/main](https://github.com/hkilang/TTS-API/tree/main)
- Special thanks to https://github.com/graphemecluster for his assistance, for pointing me in the right direction, and for creating the TTS application.

## License

This project is licensed under the Apache 2.0 License. See the `LICENSE` file for details.
