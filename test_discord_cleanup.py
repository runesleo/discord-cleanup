import os
import tempfile
import unittest
from io import BytesIO
from unittest import mock
from urllib.error import HTTPError, URLError

import discord_cleanup


class FakeResponse:
    def __init__(self, status, payload=b"{}"):
        self.status = status
        self._payload = payload

    def read(self):
        return self._payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


class FakeOpener:
    def __init__(self, side_effect):
        self.side_effect = side_effect

    def open(self, request):
        if isinstance(self.side_effect, Exception):
            raise self.side_effect
        return self.side_effect(request)


class LoadEnvFileTests(unittest.TestCase):
    def test_load_env_file_sets_missing_values(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            env_path = os.path.join(temp_dir, ".env")
            with open(env_path, "w", encoding="utf-8") as env_file:
                env_file.write("# comment\n")
                env_file.write("DISCORD_TOKEN=test-token\n")

            with mock.patch.dict(os.environ, {}, clear=True):
                discord_cleanup.load_env_file(env_path)
                self.assertEqual(os.environ["DISCORD_TOKEN"], "test-token")

    def test_load_env_file_does_not_override_existing_environment(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            env_path = os.path.join(temp_dir, ".env")
            with open(env_path, "w", encoding="utf-8") as env_file:
                env_file.write("DISCORD_TOKEN=file-token\n")

            with mock.patch.dict(os.environ, {"DISCORD_TOKEN": "shell-token"}, clear=True):
                discord_cleanup.load_env_file(env_path)
                self.assertEqual(os.environ["DISCORD_TOKEN"], "shell-token")


class ApiRequestTests(unittest.TestCase):
    def test_api_request_sends_json_body_for_delete(self):
        captured = {}

        def fake_urlopen(request):
            captured["data"] = request.data
            captured["headers"] = dict(request.header_items())
            return FakeResponse(204, b"")

        opener = FakeOpener(fake_urlopen)
        result = discord_cleanup.api_request(
            "DELETE",
            "/users/@me/guilds/123",
            "token",
            data=discord_cleanup.LEAVE_GUILD_DATA,
            opener=opener,
        )

        self.assertIsNone(result)
        self.assertEqual(captured["data"], b'{"lurking": false}')
        self.assertEqual(captured["headers"]["Content-type"], "application/json")

    def test_api_request_returns_failed_sentinel_on_http_error(self):
        error = HTTPError(
            url="https://discord.com/api/v10/users/@me/guilds/123",
            code=400,
            msg="Bad Request",
            hdrs=None,
            fp=BytesIO(b'{"message": "The request body contains invalid JSON.", "code": 50109}'),
        )

        with mock.patch("builtins.print"):
            result = discord_cleanup.api_request(
                "DELETE",
                "/users/@me/guilds/123",
                "token",
                data=discord_cleanup.LEAVE_GUILD_DATA,
                opener=FakeOpener(error),
            )

        self.assertIs(result, discord_cleanup.REQUEST_FAILED)

    def test_api_request_returns_failed_sentinel_on_url_error(self):
        with mock.patch("builtins.print"):
            with mock.patch("time.sleep"):
                result = discord_cleanup.api_request(
                    "DELETE",
                    "/users/@me/guilds/123",
                    "token",
                    data=discord_cleanup.LEAVE_GUILD_DATA,
                    attempt=discord_cleanup.NETWORK_RETRY_ATTEMPTS,
                    opener=FakeOpener(URLError(FileNotFoundError(2, "No such file or directory"))),
                )

        self.assertIs(result, discord_cleanup.REQUEST_FAILED)


if __name__ == "__main__":
    unittest.main()
