import os
import pathlib
from contextlib import suppress

from gtts.lang import _extra_langs, _fetch_langs


def get_languages():
    env = os.environ.get("TEST_LANGS")
    if not env or env == "all":
        langs = _fetch_langs()
        langs.update(_extra_langs())
    elif env == "fetch":
        langs = _fetch_langs()
    elif env == "extra":
        langs = _extra_langs()
    else:
        env_langs = env.split(",")
        env_langs = [l for l in env_langs if l]
        langs = env_langs
    return langs


def delete_folder(pth):
    for sub in pth.iterdir():
        if sub.is_dir():
            delete_folder(sub)
        else:
            sub.unlink()
    # if you just want to delete dir content, remove this line
    pth.rmdir()


def create_tmp_dir(path):
    tmp_path = None
    with suppress(FileExistsError):
        tmp_path = pathlib.Path(path).mkdir()
    return tmp_path if tmp_path else pathlib.Path(path)
