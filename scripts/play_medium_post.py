#!/usr/bin/env python3
"""# -*- coding: utf-8 -*-"""
import argparse
import argcomplete
from medium_speech import MediumToSpeech


def main():
    parser = argparse.ArgumentParser(description="")
    parser.add_argument(
        "--play",
        "-p",
        dest="play_it",
        action="store_true",
        help="Play generated MP3 files.",
    )
    parser.add_argument(
        "--cleanup",
        "-c",
        dest="cleanup",
        action="store_true",
        help="Cleanup generated MP3 files.",
    )
    parser.add_argument(
        "--speed",
        "-s",
        dest="n_speed",
        default=0,
        help="Play every n'th frame only ie Play speed.",
    )
    parser.add_argument(
        "--loglevel",
        dest="log_level",
        default="INFO",
        help="log level to use, default [INFO], options [INFO, DEBUG, ERROR]",
    )
    parser.add_argument("--url-post", "-u", dest="medium_url", help="Medium post URL.")
    parser.add_argument("--file", dest="markdown_file", help="Specify a Markdown file.")
    argcomplete.autocomplete(parser)
    args = vars(parser.parse_args())
    medium_to_speech = MediumToSpeech(
        medium_url=args.get("medium_url"),
        filename=args.get("markdown_file"),
        log_level=args.get("log_level", "INFO"),
    )
    medium_to_speech.text_to_speech(cleanup=args.get("cleanup"))
    if args.get("play_it"):
        medium_to_speech.play_it(speed=args.get("n_speed"), cleanup=args.get("cleanup"))


if __name__ == "__main__":
    main()
