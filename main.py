""" Main function for nci-lang. """

import os
import re
import argparse

from googletrans import Translator
from gtts import gTTS


PAUSE_MULT = 1.1
PAUSE_LOG_PATH = "pause.log"
TEMP_MP3_PATH = "src.mp3"
TEMP_MERGE_PATH = "merged.mp3"
MERGE_LOG_PATH = "merge.log"
DURATION_LOG_PATH = "duration.log"
PADDING_LEN = 2


def write_silence(seconds: int, path: str) -> None:
    """
    Generate silent audio encoded in mp3 format. Note that we have to match the sampling
    frequency (24 kHz) of the audio returned by gTTS.
    """
    silence_cmd = f"ffmpeg -f lavfi -i anullsrc=r=24000:cl=mono -t {seconds} "
    silence_cmd += f"-b:a 32k -acodec libmp3lame -y {path}"
    silence_cmd += f" > {PAUSE_LOG_PATH} 2>&1"
    exit_code = os.system(silence_cmd)
    if exit_code != 0:
        raise RuntimeError(
            "Generatation of silent MP3 with ffmpeg failed."
            f" Check output in {PAUSE_LOG_PATH}."
        )


def merge_mp3(path1: str, path2: str) -> None:
    """ Merge two mp3 files and store the result into `path1`. """
    merge_cmd = f"ffmpeg -i \"concat:{path1}|{path2}\" -acodec copy {TEMP_MERGE_PATH} "
    merge_cmd += f" -y > {MERGE_LOG_PATH} 2>&1"
    exit_code = os.system(merge_cmd)
    if exit_code != 0:
        raise RuntimeError(
            f"Failed to merge mp3 files. Check output in {MERGE_LOG_PATH}."
        )
    os.rename(TEMP_MERGE_PATH, path1)


def main(
    input_path: str,
    output_path: str,
    src_lang: str,
    dest_lang: str,
    src_first: bool = False,
    slow: bool = False,
) -> None:
    """ Main function for nci-lang. """

    # Read text to translate.
    with open(input_path, "r") as input_file:
        src_text = input_file.read()

    # Initialize audio file with padding.
    write_silence(PADDING_LEN, output_path)

    # Generate translated audio and write to file.
    translator = Translator()
    for src_line in re.split("\.|!|\?", src_text):

        # Skip empty lines.
        src_line = src_line.strip()
        if len(src_line) == 0:
            continue

        # Translate line to target language.
        dest_line = translator.translate(src_line, src=src_lang, dest=dest_lang).text

        # Convert line (in both languages) to speech.
        src_speech = gTTS(src_line, lang=src_lang, slow=slow)
        dest_speech = gTTS(dest_line, lang=dest_lang, slow=slow)

        # Get length of source sentence.
        src_speech.save(TEMP_MP3_PATH)
        duration_cmd = f"mp3info -p \"%S\" {TEMP_MP3_PATH} > {DURATION_LOG_PATH} 2>&1"
        exit_code = os.system(duration_cmd)
        if exit_code != 0:
            raise RuntimeError(
                "Checking length of mp3 with mp3info failed."
                f" Check output in {DURATION_LOG_PATH}."
            )
        with open(DURATION_LOG_PATH) as duration_file:
            src_duration = int(duration_file.read())

        # Append first sentence, pause, second sentence, pause to audio stream.
        if src_first:
            ordered_speeches = [src_speech, dest_speech]
        else:
            ordered_speeches = [dest_speech, src_speech]
        for speech in ordered_speeches:
            speech.save(TEMP_MP3_PATH)
            merge_mp3(output_path, TEMP_MP3_PATH)
            write_silence(round(src_duration * PAUSE_MULT), TEMP_MP3_PATH)
            merge_mp3(output_path, TEMP_MP3_PATH)

    # Cleanup files for pause generation.
    cleanup_paths = [PAUSE_LOG_PATH, TEMP_MP3_PATH, TEMP_MERGE_PATH, MERGE_LOG_PATH, DURATION_LOG_PATH]
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
    parser.add_argument(
        "--src_lang",
        type=str,
        default="en",
        help="Language of source text."
    )
    parser.add_argument(
        "--dest_lang",
        type=str,
        default="es",
        help="Language into which to translate source text."
    )
    parser.add_argument(
        "--src_first",
        default=False,
        action="store_true",
        help=(
            "If true, audio lesson includes the source sentence before the "
            "destination sentence."
        )
    )
    parser.add_argument(
        "--slow",
        default=False,
        action="store_true",
        help="Slow speech."
    )
    args = parser.parse_args()

    main(**vars(args))
