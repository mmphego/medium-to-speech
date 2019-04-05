#!/usr/bin/env python3

import subprocess
from io import StringIO
from pathlib import Path

import docker
from gtts import gTTS
from markdown import Markdown


def which(program):
    """Takes a program name or full path,
    and returns the full path of the requested executable.
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


def md_to_text(text=None, filename=None, tab_length=4):
    Markdown.output_formats["plain"] = unmark_element
    md = Markdown(output_format="plain")
    md.stripTopLevelTags = False
    md.tab_length = tab_length
    return md.convert(text)


def read_from_medium(docker_container, medium_url, runonce=True, filename="medium.md"):
    client = docker.from_env()
    with open(filename, "wb") as _f:
        data = client.containers.run(docker_container, medium_url, remove=runonce)
        _f.write(data)
    return data


def read_from_file(filename):
    with open(filename) as _f:
        lines = [x for x in [x.rstrip() for x in _f.readlines()] if x]
    return lines


def get_markdown_titles(lines):
    return {i: '' for i in lines if "# " in i}


def text_to_speech(words, tmp_dir="/tmp", file_format="mp3"):
    for count, line in enumerate(words, 1):
        tts = gTTS(text=line, lang='en-us')
        tts.save(f'{tmp_dir}/{count}.{file_format}')


def play_it(play_with="mpg123", tmp_dir="/tmp", file_format="mp3"):
    FNULL = open(subprocess.os.devnull, 'wb')
    play_with = which(play_with)
    tmp_dir = Path(tmp_dir)
    mp3_files = tmp_dir.glob(f"*{file_format}")
    for mp3_file in sorted(mp3_files):
        subprocess.call(f"{play_with} {mp3_file}", shell=True,
                        stdout=FNULL, stderr=subprocess.STDOUT)
        subprocess.call(f"rm -rf {mp3_file}")
