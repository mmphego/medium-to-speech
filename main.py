#!/usr/bin/env python3

import subprocess
import time
import docker

from gtts import gTTS

from markdown import Markdown
from io import StringIO


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
    with open(filename,"wb") as _f:
        data = client.containers.run(docker_container, medium_url, remove=runonce)
        _f.write(data)
    return data

def read_from_file(filename):
    with open(filename) as _f:
        lines = [x for x in [x.rstrip() for x in _f.readlines()] if x]
    return lines

def get_markdown_titles(lines):
    return {i:'' for i in lines if "# " in i}

