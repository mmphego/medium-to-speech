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
import requests
from docker.errors import ImageNotFound
from gtts import gTTS
from markdown import Markdown


class LoggingClass:
    @property
    def logger(self):
        log_format = (
            "%(asctime)s - %(name)s - %(levelname)s - %(module)s - "
            "%(pathname)s : %(lineno)d - %(message)s"
        )
        name = ".".join([os.path.basename(sys.argv[0]), self.__class__.__name__])
        logging.basicConfig(format=log_format)
        return logging.getLogger(name)


class MediumToSpeech(LoggingClass):
    def __init__(
        self,
        medium_url=None,
        filename=None,
        docker_image="mmphego/mediumexporter",
        tmp_dir="/tmp",
        log_level="INFO",
    ):

        self.medium_url = medium_url
        self.filename = filename
        self.docker_image = docker_image
        self.tmp_dir = tmp_dir
        self.logger.setLevel(log_level.upper())
        coloredlogs.install(level=log_level.upper())
        self.pull_images()

    @staticmethod
    def check_url_exist(url):
        _request = requests.get(url)
        return bool(_request.status_code == 200)

    def pull_images(self, force_pull=False):
        if force_pull:
            self._client.images.pull(self.docker_image)

        try:
            self._client = docker.from_env()
            self._client.images.get(self.docker_image)
        except ImageNotFound:
            self.logger.debug(
                "Pulling Docker image (%s) from Docker Hub.", repr(self.docker_image)
            )
            try:
                self._client.images.pull(self.docker_image)
                self.logger.debug(
                    "Successfully downloaded/pulled %s image.", repr(self.docker_image)
                )
            except ImageNotFound:
                raise SystemExit(
                    "Failed to pull the Docker image %s from hub.docker.com"
                    % repr(self.docker_image)
                )

        finally:
            self.logger.debug(
                "Successfully found %s Docker image",
                self._client.images.get(self.docker_image).__repr__(),
            )

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

        if self.medium_url and self.check_url_exist:
            restart_policy = {"Name": "on-failure", "MaximumRetryCount": 5}
            try:
                self.logger.debug("Running docker container '%s'", self.docker_image)
                data = self._client.containers.run(
                    image=self.docker_image,
                    command=self.medium_url,
                    # auto_remove=runonce,
                    remove=runonce,
                    restart_policy=restart_policy,
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
        """Split list of words to n-characters/chunks

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
            return [words[n : n + char_length] for n in range(0, len(words), char_length)]

    def read_markdown(self):
        """
        Read Markdown from Medium URL or File

        Returns: md_text (str): Markdown text in the form of bytes
        """
        if self.medium_url:
            md_text = self.read_from_medium()
        elif self.filename:
            md_text = self.read_from_file()
        else:
            raise RuntimeError("URL or Filename cannot be None")
        return md_text

    def markdown_to_text(self, md_text="", tab_length=4):
        """

        Args:
            md_text (bytes, str): Markdown text in the form of bytes
            tab_length (int, optional): Description

        Returns:
            plain_text (list): Converted Markdown into plain text
        """
        if not md_text:
            md_text = self.read_markdown()

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

    def text_to_speech(self, cleanup=False):
        """Generate speech from text using Google TTS API

        Args:
            cleanup (bool, False): Delete MP3 files after playing.

        """
        text_from_markdown = self.markdown_to_text()
        splitted_words = self.splits_words(text_from_markdown)
        self.logger.info("Generate speech from text using Google TTS API")
        if cleanup:
            self.clean_up_files()
        for words in splitted_words:
            for count, line in enumerate(words, 1):
                if line:
                    self.logger.debug(line)
                    with suppress(Exception):
                        tts = gTTS(text=line, lang="en-us")
                        tts.save(f"{self.tmp_dir}/file_{str(count).zfill(2)}.mp3")
        self.logger.info("Done: Generating speech from text using Google TTS API")

    def play_it(self, play_with="cvlc", speed=0, cleanup=False):
        """Play generated TTS as mp3 files

        Args:
            play_with (str, "cvlc"): Unix/Linux program to play mp3 with!
            speed (int, 0): Play every n'th frame only ie Player speed.
            cleanup (bool, False): Delete MP3 files after playing.

        """
        if not play_with:
            msg = (
                "Ensure that mpg123/vlc is installed in your system\n"
                "Run 'sudo apt install --install-recommends mpg123' or\n"
                "Run 'sudo apt install --install-recommends vlc' "
            )
            raise RuntimeError(msg)

        FNULL = open(subprocess.os.devnull, "wb")
        tmp_dir = Path(self.tmp_dir)
        mp3_files = tmp_dir.glob(f"*.mp3")
        play_with = self.which(play_with)
        if "cvlc":
            play_cmd = f"{play_with} --play-and-exit --no-loop --rate {speed}"
        elif "mpg123":
            play_cmd = f"{play_with} -d {speed}"
        else:
            play_cmd = play_with

        self.logger.info("Playing generated TTS data with %s", play_with)
        for mp3_file in sorted(mp3_files):
            if mp3_file.is_file():
                self.logger.info("Playing %s", mp3_file)
                subprocess.call(
                    f"{play_cmd} {mp3_file}",
                    shell=True,
                    stdout=FNULL,
                    stderr=subprocess.STDOUT,
                )
        if cleanup:
            self.clean_up_files()
