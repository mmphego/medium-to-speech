#!/usr/bin/env python3
"""# -*- coding: utf-8 -*-"""

import re
import subprocess
from contextlib import suppress
from io import StringIO
from pathlib import Path

import docker
from gtts import gTTS
from markdown import Markdown


def remove_tags(text):
    """Remove HTML tags from string

    Args:
        text (String):

    Returns:
        String:
    """
    TAG_RE = re.compile(r"<[^>]+>")
    return TAG_RE.sub("", text)


def which(program):
    """Takes a program name or full path,
    and returns the full path of the requested executable.

    Args:
        program (str): Unix program

    Returns:
        String: path to program
    """
    return subprocess.check_output(["which", program]).strip().decode()


def unmark_element(element, stream=None):
    """patching Markdown"""
    if stream is None:
        stream = StringIO()
    if element.text:
        stream.write(element.text)
    for sub in element:
        unmark_element(sub, stream)
    if element.tail:
        stream.write(element.tail)
    return stream.getvalue()


def bytes_to_str(text=None):
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


def splits_words(words=None, char_length=99):
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
        words = [remove_tags(i) for i in words]
        return [words[n : n + char_length] for n in range(0, len(words), char_length)]


def md_to_text(md_text=None, tab_length=4):
    """Summary

    Args:
        md_text (None, optional): Description
        tab_length (int, optional): Description

    Returns:
        TYPE: Description
    """
    text = bytes_to_str(md_text)
    Markdown.output_formats["plain"] = unmark_element
    md = Markdown(output_format="plain")
    md.stripTopLevelTags = False
    md.tab_length = tab_length
    plain_text = md.convert(text)
    return [x for x in plain_text.split("\n") if x]


def read_from_medium(
    medium_url=None,
    docker_container="mmphego/mediumexporter",
    runonce=True,
    save_to_file=False,
):
    """Summary

    Args:
        medium_url (None, optional): Description
        docker_container (str, optional): Description
        runonce (bool, optional): Description
        save_to_file (bool, optional): Description
    """
    if medium_url:
        try:
            client = docker.from_env()
            data = client.containers.run(docker_container, medium_url, remove=runonce)
        except Exception as _err:
            raise RuntimeError(f"{_err}: Failed to retrieve Medium post.")
        if save_to_file:
            with open("medium.md", "wb") as _f:
                _f.write(data)
        return data


def read_from_file(filename):
    """Read Markdown file

    Args:
        filename (str): Markdown file

    Returns:
        bytes: Contents of file
    """
    with open(filename, "rb") as _f:
        return _f.read()


def text_to_speech(text_from_markdown=[], tmp_dir="/tmp"):
    """Generate speech from text using Google TTS API

    Args:
        text_from_markdown (list, optional): Markdown text
        tmp_dir (str, "/tmp"): Directory to save the mp3 files
    """
    if isinstance(text_from_markdown, list):
        splitted_words = splits_words(text_from_markdown)
        for words in splitted_words:
            for count, line in enumerate(words, 1):
                print(len(line), ":", line)
                if line:
                    tts = gTTS(text=line, lang="en-us")
                    tts.save(f"{tmp_dir}/{count}.mp3")


def play_it(play_with="mpg123", tmp_dir="/tmp", file_format="mp3", delete_file=True):
    """Play mp3 files

    Args:
        play_with (str, "mph123"): Unix/Linux program to play mp3 with!
        tmp_dir (str, "/tmp"): Directory where mp3 files are saved!
        file_format (str, "mp3"): file format
        delete_file (bool, True): Delete file when done!
    """
    FNULL = open(subprocess.os.devnull, "wb")
    play_with = which(play_with)
    tmp_dir = Path(tmp_dir)
    mp3_files = tmp_dir.glob(f"*{file_format}")
    for mp3_file in sorted(mp3_files):
        if mp3_file.is_file():
            subprocess.call(
                f"{play_with} {mp3_file}",
                shell=True,
                stdout=FNULL,
                stderr=subprocess.STDOUT,
            )
        if delete_file:
            with suppress(FileNotFoundError):
                mp3_file.unlink()


