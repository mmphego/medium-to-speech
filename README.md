
# medium-to-speech

[![Build Status](https://travis-ci.com/mmphego/medium-to-speech.svg?branch=master)](https://travis-ci.com/mmphego/medium-to-speech)
![GitHub](https://img.shields.io/github/license/mmphego/medium-to-speech.svg) [
![saythanks](https://img.shields.io/badge/say-thanks-ff69b4.svg)](https://saythanks.io/to/mmphego)

## Medium posts to Speech.

A Python library for lazy people (like myself), who never finds time to read daily [Medium](http://medium.com/) posts and prefer to listen to them instead. It convert [medium](http://medium.com/) post to markdown using a [Docker container/image](https://hub.docker.com/r/mmphego/mediumexporter) then uses [gTTs](https://github.com/pndurette/gTTS)  to interface with Google Translate's text-to-speech API which converts text to spoken `MP3` data, thereafter plays the generated `mp3` files with [`cvlc`](https://www.videolan.org/vlc/) assuming it is installed.

## Apt Requirements

You will need to install a few dependencies before you continue:

```shell
sudo apt install -y docker-ce mpg123 python3.6 python3.6-dev vlc
```

## Installation

To install run:
```shell
pip3 install -U --pre .
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
