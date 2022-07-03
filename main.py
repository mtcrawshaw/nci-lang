""" Main function for nci-lang. """

import re

from googletrans import Translator


SRC_LANG = 'es'
DEST_LANG = 'en'


def main():
    """ Main function for nci-lang. """

    # Read text to translate.
    src_text = "Me llamo Miguel, y me gusta leer. Pero no me gusta libros sobre gatos."

    # Translate test text.
    translator = Translator()
    for src_line in re.split("\.|!|\?", src_text):

        # Skip empty lines.
        src_line = src_line.strip()
        if len(src_line) == 0:
            continue

        print(f"{SRC_LANG}: {src_line}")
        dest_line = translator.translate(src_line, src=SRC_LANG, dest=DEST_LANG).text
        print(f"{DEST_LANG}: {dest_line}")
        print("")


if __name__ == "__main__":
    main()
