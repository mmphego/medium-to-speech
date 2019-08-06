
# medium-to-speech

[![Build Status](https://travis-ci.com/mmphego/medium-to-speech.svg?branch=master)](https://travis-ci.com/mmphego/medium-to-speech)
[![Python](https://img.shields.io/badge/Python-3.6%2B-red.svg)](https://www.python.org/downloads/)
![GitHub](https://img.shields.io/github/license/mmphego/medium-to-speech.svg) [
![PyPI](https://img.shields.io/pypi/v/medium-speech.svg?color=green&label=pypi%20release)
![PyPI - Downloads](https://img.shields.io/pypi/dm/medium-speech.svg?label=PyPi%20Downloads)
[![saythanks](https://img.shields.io/badge/say-thanks-ff69b4.svg)](https://saythanks.io/to/mmphego)
[![Donate](https://img.shields.io/badge/Donate-%24-green.svg)](https://paypal.me/mmphego)

## Medium posts to Speech.

A Python library for lazy people (like myself), who never finds time to read daily [Medium](http://medium.com/) posts and prefer to listen to them instead. It convert [medium](http://medium.com/) post to markdown using a [Docker container/image](https://hub.docker.com/r/mmphego/mediumexporter) then uses [gTTs](https://github.com/pndurette/gTTS)  to interface with Google Translate's text-to-speech API which converts text to spoken `MP3` files, thereafter plays the generated `mp3` files with [`cvlc`](https://www.videolan.org/vlc/) assuming it is installed.

## Apt Requirements

You will need to install a few dependencies before you continue:

```shell
sudo apt install -y docker-ce mpg123 python3.6 python3.6-dev vlc
```

## Installation

To install run:
```shell
python3 -m pip install -U medium-speech
```

## Usage

Available arguments:
```shell
play_medium_post.py -h

usage: play_medium_post.py [-h] [--play] [--cleanup] [--speed N_SPEED]
                           [--loglevel LOG_LEVEL] [--url-post MEDIUM_URL]
                           [--file MARKDOWN_FILE]

optional arguments:
  -h, --help            show this help message and exit
  --play, -p            Play generated MP3 files.
  --cleanup, -c         Cleanup generated MP3 files.
  --speed N_SPEED, -s N_SPEED
                        Play every n'th frame only ie Play speed.
  --loglevel LOG_LEVEL  log level to use, default [INFO], options [INFO,
                        DEBUG, ERROR]
  --url-post MEDIUM_URL, -u MEDIUM_URL
                        Medium post URL.
  --file MARKDOWN_FILE  Specify a Markdown file.

```

Listen to a [Medium](http://medium.com/) post:
```shell
play_medium_post.py -ps 1 -u https://medium.com/@mmphego/how-i-managed-to-harness-imposter-syndrome-391fdb754820
```

Listen to Markdown file:
```shell
play_medium_post.py -ps 1 --file README.md
```

## Oh, Thanks!

By the way... thank you! And if you'd like to [say thanks](https://saythanks.io/to/mmphego)... :)

✨🍰✨

## Feedback

Feel free to fork it or send me PR to improve it.
