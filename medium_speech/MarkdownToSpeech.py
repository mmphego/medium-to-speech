#!/usr/bin/env python3
"""# -*- coding: utf-8 -*-"""

import logging
import os
import re
import subprocess
import sys
from contextlib import suppress
from io import StringIO
from pathlib import Path

import coloredlogs
import docker
from gtts import gTTS
from markdown import Markdown


class LoggingClass:
    @property
    def logger(self):
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(pathname)s : %(lineno)d - %(message)s"
        name = ".".join([os.path.basename(sys.argv[0]), self.__class__.__name__])
        logging.basicConfig(format=log_format)
        return logging.getLogger(name)


class MarkdownToSpeech(LoggingClass):
    def __init__(
        self,
        medium_url=None,
        filename=None,
        docker_container="mmphego/mediumexporter",
        tmp_dir="/tmp",
        log_level="INFO",
    ):

        self.medium_url = medium_url
        self.filename = filename
        self.docker_container = docker_container
        self.tmp_dir = tmp_dir
        self.logger.setLevel(log_level.upper())
        coloredlogs.install(level=log_level.upper())

    def read_from_medium(self, runonce=True, save_to_file=False):
        """

        Args:
            runonce (bool, optional): Description
            save_to_file (bool, optional): Description
        """
        if not self.which("docker"):
            msg = (
                "Ensure that Docker is installed in your system\n"
                "Run 'sudo apt install docker-ce'"
            )
            raise RuntimeError(msg)

        if self.medium_url:
            try:
                self.logger.debug(
                    "Running docker container '%s'", self.docker_container
                )
                client = docker.from_env()
                data = client.containers.run(
                    self.docker_container, self.medium_url, remove=runonce
                )
            except Exception as _err:
                raise RuntimeError(f"{_err}: Failed to retrieve Medium post.")
            if save_to_file:
                with open("medium.md", "wb") as _f:
                    _f.write(data)
            return data

    def read_from_file(self):
        """Read Markdown file

        Returns:
            bytes: Contents of file
        """
        with open(self.filename, "rb") as _f:
            return _f.read()

    def remove_tags(self, text):
        """Remove HTML tags from string

        Args:
            text (String):

        Returns:
            String:
        """
        TAG_RE = re.compile(r"<[^>]+>")
        return TAG_RE.sub("", text)

    def which(self, program):
        """Takes a program name or full path,
        and returns the full path of the requested executable.

        Args:
            program (str): Unix program

        Returns:
            String: path to program
        """
        with suppress(Exception):
            return subprocess.check_output(["which", program]).strip().decode()

    def unmark_element(self, element, stream=None):
        """patching Markdown"""
        if stream is None:
            stream = StringIO()
        if element.text:
            stream.write(element.text)
        for sub in element:
            self.unmark_element(sub, stream)
        if element.tail:
            stream.write(element.tail)
        return stream.getvalue()

    def bytes_to_str(self, text=None):
        """Decode bytes to string

        Args:
            text (None, optional): bytes

        Returns:
            text: str

        Example:
            >>> text = b"Hello World"
            >>> print(bytes_to_str(text))
                "Hello World"
        """
        if isinstance(text, bytes):
            text = text.decode("UTF-8").strip()
            return text

    def splits_words(self, words=None, char_length=99):
        """Split list of words to n-characters

        Args:
            words (List, optional): list of words
            char_length (int, optional): character length to split to!

        Returns:
            TYPE: Description

        Example:
            >>> text = ["<a>", "hello", "World", "!", "</a>"]
            >>> splits_words(text)
                [['', 'hello', 'World', '!', '']]
    I    """
        if isinstance(words, list):
            words = [self.remove_tags(i) for i in words]
            return [
                words[n : n + char_length] for n in range(0, len(words), char_length)
            ]

    def markdown_to_text(self, tab_length=4):
        """

        Args:
            tab_length (int, optional): Description

        Returns:

        """
        if self.medium_url:
            md_text = self.read_from_medium()
        elif self.filename:
            md_text = self.read_from_file()
        else:
            raise RuntimeError("URL or Filename cannot be None")
        text = self.bytes_to_str(md_text)
        Markdown.output_formats["plain"] = self.unmark_element
        md = Markdown(output_format="plain")
        md.stripTopLevelTags = False
        md.tab_length = tab_length
        plain_text = md.convert(text)
        return [x for x in plain_text.split("\n") if x]

    def clean_up_files(self, file_format="mp3"):
        """Delete old mp3 files"""
        tmp_dir = Path(self.tmp_dir)
        mp3_files = tmp_dir.glob(f"*{file_format}")
        self.logger.debug("Cleaning up old mp3 files from %s", str(tmp_dir))
        for mp3_file in sorted(mp3_files):
            with suppress(FileNotFoundError):
                mp3_file.unlink()

    def text_to_speech(self):
        """Generate speech from text using Google TTS API"""
        text_from_markdown = self.markdown_to_text()
        splitted_words = self.splits_words(text_from_markdown)
        self.logger.info("Generate speech from text using Google TTS API")
        self.clean_up_files()
        for words in splitted_words:
            for count, line in enumerate(words, 1):
                if line:
                    self.logger.debug(line)
                    tts = gTTS(text=line, lang="en-us")
                    tts.save(f"{self.tmp_dir}/{count}.mp3")
        self.logger.info("Done: Generating speech from text using Google TTS API")

    def play_it(self, play_with="mpg123"):
        """Play generated TTS as mp3 files

        Args:
            play_with (str, "mph123"): Unix/Linux program to play mp3 with!
        """
        FNULL = open(subprocess.os.devnull, "wb")
        play_with = self.which(play_with)
        if not play_with:
            msg = (
                "Ensure that mpg123 is installed in your system\n"
                "Run 'sudo apt install mpg123'"
            )
            raise RuntimeError(msg)
        tmp_dir = Path(self.tmp_dir)
        mp3_files = tmp_dir.glob(f"*.mp3")
        self.logger.info("Playing generated TTS data with %s", play_with)
        for mp3_file in sorted(mp3_files):
            if mp3_file.is_file():
                self.logger.debug("Playing %s", mp3_file)
                subprocess.call(
                    f"{play_with} {mp3_file}",
                    shell=True,
                    stdout=FNULL,
                    stderr=subprocess.STDOUT,
                )
        self.clean_up_files()
