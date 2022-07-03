""" Main function for nci-lang. """

import os
import re
import argparse

from googletrans import Translator
from gtts import gTTS


SRC_LANG = "es"
DEST_LANG = "en"
PAUSE_MULT = 1
PAUSE_PATH = "silence.mp3"
PAUSE_LOG_PATH = "pause.log"
SRC_TEMP_PATH = "src.mp3"
DURATION_LOG_PATH = "duration.log"


def main(input_path: str, output_path: str):
    """ Main function for nci-lang. """

    # Read text to translate.
    with open(input_path, "r") as input_file:
        src_text = input_file.read()

    # Generate translated audio and write to file.
    translator = Translator()
    audio_stream = open(output_path, "wb")
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

        # Get length of source sentence.
        src_speech.save(SRC_TEMP_PATH)
        duration_cmd = f"mp3info -p \"%S\" {SRC_TEMP_PATH} > {DURATION_LOG_PATH} 2>&1"
        exit_code = os.system(duration_cmd)
        if exit_code != 0:
            raise RuntimeError(
                "Checking length of mp3 with mp3info failed."
                f" Check output in {DURATION_LOG_PATH}."
            )
        with open(DURATION_LOG_PATH) as duration_file:
            src_duration = int(duration_file.read())

        # Generate MP3 encoding of pause. Note that we have to match the sampling
        # frequency (24 kHz) of the audio returned by gTTS.
        pause_seconds = round(src_duration * PAUSE_MULT)
        silence_cmd = f"ffmpeg -f lavfi -i anullsrc=r=24000:cl=mono -t {pause_seconds} "
        silence_cmd += f"-q:a 9 -acodec libmp3lame -y {PAUSE_PATH}"
        silence_cmd += f" > {PAUSE_LOG_PATH} 2>&1"
        exit_code = os.system(silence_cmd)
        if exit_code != 0:
            raise RuntimeError(
                "Generatation of silent MP3 (for pauses) with ffmpeg failed."
                f" Check output in {PAUSE_LOG_PATH}."
            )
        with open(PAUSE_PATH, "rb") as pause_file:
            pause = pause_file.read()

        # Append source speech, pause, dest speech, pause to audio stream.
        src_speech.write_to_fp(audio_stream)
        audio_stream.write(pause)
        dest_speech.write_to_fp(audio_stream)
        audio_stream.write(pause)

    # Close audio stream.
    audio_stream.close()

    # Cleanup files for pause generation.
    cleanup_paths = [PAUSE_PATH, PAUSE_LOG_PATH, SRC_TEMP_PATH, DURATION_LOG_PATH]
    for path in cleanup_paths:
        if os.path.isfile(path):
            os.remove(path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate audio-based language lessons."
    )
    parser.add_argument(
        "--input_path",
        type=str,
        default="input.txt",
        help="Path to read source text from."
    )
    parser.add_argument(
        "--output_path",
        type=str,
        default="lesson.mp3",
        help="Path in which to store generated audio in mp3 format."
    )
    args = parser.parse_args()

    main(**vars(args))
