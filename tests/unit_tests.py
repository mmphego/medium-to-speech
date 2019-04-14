# -*- coding: utf-8 -*-
import random
import unittest
import warnings

from gtts.tts import gTTS, gTTSError

from medium_speech import MediumToSpeech

from . import utils


class test_gTTS(unittest.TestCase):

    tmp_path = utils.create_tmp_dir("/tmp/gtts_tests")

    def setUp(self):
        warnings.simplefilter("ignore", category=DeprecationWarning)
        langs = utils.get_languages()
        self.lang = random.choice(list(langs.keys()))

    def cleanUp(self):
        utils.delete_folder(self.tmp_path)
        self.assertFalse(self.tmp_path.exists())

    def test_TTS(self):
        """Test a random language and save file"""
        text = "This is a test"
        """Create output .mp3 file successfully"""
        for slow in (False, True):
            filename = self.tmp_path / "test_{}_.mp3".format(self.lang)
            # Create gTTS and save
            tts = gTTS(text, self.lang, slow=slow)
            tts.save(filename)
            # Check if files created is > 2k
            self.assertGreater(
                filename.stat().st_size, 2000, "Check if files created is > 2k"
            )

    def test_unsupported_language_check(self):
        """Raise ValueError on unsupported language (with language check)"""
        lang = "xx"
        text = "Lorem ipsum"
        check = True
        with self.assertRaises(ValueError):
            gTTS(text=text, lang=lang, lang_check=check)

    def test_empty_string(self):
        """Raise AssertionError on empty string"""
        text = ""
        with self.assertRaises(AssertionError):
            gTTS(text=text)

    def test_no_text_parts(self):
        """Raises AssertionError on, no content to send to API (no text_parts)"""
        text = "..,\n"
        with self.assertRaises(AssertionError):
            filename = self.tmp_path / "no_content.txt"
            tts = gTTS(text=text)
            tts.save(filename)


class test_MediumtoSpeech(unittest.TestCase):
    def setUp(self):
        warnings.simplefilter("ignore", category=ResourceWarning)
        self.medium_speech = MediumToSpeech()
        self.medium_speech.medium_url = (
            "https://medium.com/@mmphego/"
            + "how-i-managed-to-harness-imposter-syndrome-391fdb754820"
        )
        self.medium_speech.docker_image = "mmphego/mediumexporter"

    def test_remove_HTML_tags(self):
        """Raise AssertionError when fails to remove HTML code from string"""
        html_code = "Hello, <b>world</b>"
        expected_str = "Hello, world"
        format_str = self.medium_speech.remove_tags(html_code)
        self.assertEqual(format_str, expected_str)

    def test_docker_pull_images(self):
        """ Raises AssertionError if it Docker image doesn't exists. """
        self.medium_speech.pull_images(force_pull=True)
        get_available_images = self.medium_speech._client.images.list()
        _available_images = []
        for image in get_available_images:
            image_tag = image.attrs.get("RepoTags")
            if image_tag:
                _available_images.append("".join(image_tag).split(":")[0])
        self.assertIn(self.medium_speech.docker_image, _available_images)

    def test_docker_pull_wrong_image(self):
        """ Raises AssertionError if it pulls a fake image """
        from docker.errors import ImageNotFound

        self.medium_speech.docker_image = "fake/image:latest"
        with self.assertRaises(ImageNotFound):
            with self.assertWarns(ResourceWarning):
                self.medium_speech.pull_images(force_pull=True)

    def test_read_from_medium(self):
        """ Raises AssertionError if fails to read Medium post from specified URL. """
        medium_data = self.medium_speech.read_from_medium()
        self.assertIsInstance(medium_data, bytes)
        self.assertEqual(len(medium_data), 7265)

    def test_which(self):
        """ Raise AssertionError if Docker is not installed."""
        _path = self.medium_speech.which("docker")
        self.assertEqual(_path, "/usr/bin/docker")

    def test_bytes_to_str(self):
        """ Raises AssertionError if cannot convert bytes to string. """
        _bytes_text = b"Hello World"
        _str_text = self.medium_speech.bytes_to_str(_bytes_text)
        self.assertIsInstance(_str_text, str)

    def test_check_url_exists(self):
        """ Raise AssertionError if link doesn't exist. """
        self.assertTrue(self.medium_speech.check_url_exist(self.medium_speech.medium_url))

    def test_markdown_to_text(self):
        """ Raise AssertionError if it cannot convert Markdown to plain txt. """
        md_text = b"# Markdown Test\n" b"**Hello world!**\n"
        plain_text = ", ".join(self.medium_speech.markdown_to_text(md_text=md_text))
        expected_plain_text = "Markdown Test, Hello world!"
        self.assertEqual(plain_text, expected_plain_text)
