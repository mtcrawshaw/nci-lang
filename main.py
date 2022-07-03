""" Main function for nci-lang. """

import re

from googletrans import Translator
from gtts import gTTS


SRC_LANG = 'es'
DEST_LANG = 'en'


def main():
    """ Main function for nci-lang. """

    # Read text to translate.
    src_text = "Me llamo Miguel, y me gusta leer. Pero no me gusta libros sobre gatos."

    # Translate text one line at a time.
    translator = Translator()
    i = 0
    for src_line in re.split("\.|!|\?", src_text):

        # Skip empty lines.
        src_line = src_line.strip()
        if len(src_line) == 0:
            continue

        # Translate line to target language.
        dest_line = translator.translate(src_line, src=SRC_LANG, dest=DEST_LANG).text

        # Convert line (in both languages) to speech.
        src_speech = gTTS(src_line, lang=SRC_LANG)
        dest_speech = gTTS(dest_line, lang=DEST_LANG)

        # Display text and play audio for source and target lines.
        # TEMP: Saving audio to file individually.
        print(f"{SRC_LANG}: {src_line}")
        src_speech.save(f"src_{i}.mp3")
        print(f"{DEST_LANG}: {dest_line}")
        dest_speech.save(f"dest_{i}.mp3")
        print("")
        i += 1


if __name__ == "__main__":
    main()
