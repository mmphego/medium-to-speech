#!/usr/bin/env python3
"""# -*- coding: utf-8 -*-"""
import argparse

import argcomplete

from medium_speech import MarkdownToSpeech


def main():
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("--url-post", "-u", dest="medium_url", help="Medium Post URL")
    parser.add_argument("--file", dest="markdown_file", help="Specify a Markdown file.")
    parser.add_argument("--loglevel", dest="log_level", default="INFO",
        help="log level to use, default [INFO], options [INFO, DEBUG, ERROR]")
    argcomplete.autocomplete(parser)
    args = vars(parser.parse_args())

    medium_to_speech = MarkdownToSpeech(
        medium_url=args.get("medium_url"),
        filename=args.get("markdown_file"),
        log_level=args.get("log_level", "INFO"),
    )
    medium_to_speech.text_to_speech()
    medium_to_speech.play_it()


if __name__ == "__main__":
    main()
