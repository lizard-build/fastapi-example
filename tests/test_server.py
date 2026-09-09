"""Check the production Uvicorn entry point through real HTTP requests."""

import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import time
import unittest
import urllib.error
import urllib.request


class ServerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with socket.socket() as sock:
            sock.bind(("127.0.0.1", 0))
            port = sock.getsockname()[1]
        cls.origin = f"http://127.0.0.1:{port}"
        cls.server = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", str(port)],
            cwd=Path(__file__).resolve().parents[1],
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        cls.addClassCleanup(cls.stop_server)
        for _ in range(100):
            if cls.server.poll() is not None:
                raise RuntimeError("Uvicorn exited before opening its port")
            try:
                with urllib.request.urlopen(cls.origin + "/health", timeout=1):
                    return
            except (urllib.error.URLError, TimeoutError):
                time.sleep(0.1)
        raise RuntimeError("Uvicorn did not become ready")

    @classmethod
    def stop_server(cls):
        cls.server.terminate()
        try:
            cls.server.wait(timeout=5)
        except subprocess.TimeoutExpired:
            cls.server.kill()
            cls.server.wait()

    def get(self, path):
        with urllib.request.urlopen(self.origin + path, timeout=5) as response:
            return response.status, response.read()

    def test_health(self):
        status, body = self.get("/health")
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(body), {"status": "ok"})

    def test_openapi(self):
        _, body = self.get("/openapi.json")
        paths = json.loads(body)["paths"]
        self.assertIn("get", paths["/health"])
        self.assertIn("post", paths["/echo"])

    def test_interactive_docs(self):
        status, body = self.get("/docs")
        self.assertEqual(status, 200)
        self.assertIn(b"/openapi.json", body)

    def test_echo(self):
        payload = {"message": "hello", "nested": {"number": 42}}
        request = urllib.request.Request(
            self.origin + "/echo", data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(request, timeout=5) as response:
            self.assertEqual(json.load(response), {"echo": payload})

    def test_invalid_body(self):
        request = urllib.request.Request(
            self.origin + "/echo", data=b"[]",
            headers={"Content-Type": "application/json"},
        )
        with self.assertRaises(urllib.error.HTTPError) as caught:
            urllib.request.urlopen(request, timeout=5)
        self.assertEqual(caught.exception.code, 422)

    def test_missing_route(self):
        with self.assertRaises(urllib.error.HTTPError) as caught:
            self.get("/missing-route")
        self.assertEqual(caught.exception.code, 404)


if __name__ == "__main__":
    unittest.main()
