import argparse
from contextlib import closing
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import re
import sqlite3
import sys
from urllib.parse import urlsplit

BASE = Path(__file__).resolve().parent
DATABASE = Path(os.environ.get("COMMUNITY_DB", BASE / "community.sqlite3"))
ORIGIN = os.environ.get("COMMUNITY_ORIGIN", "").rstrip("/")
CATEGORIES = ("먹어봤어요", "궁금해요", "이런 빵 어때요?")
NOTICE = "매장 공지"


def connect():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize():
    with closing(connect()) as db:
        db.executescript("""
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY, category TEXT NOT NULL, author TEXT NOT NULL,
                title TEXT NOT NULL, body TEXT NOT NULL, created TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS comments (
                id INTEGER PRIMARY KEY, post_id INTEGER NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
                author TEXT NOT NULL, body TEXT NOT NULL, created TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE INDEX IF NOT EXISTS comments_post ON comments(post_id);
        """)


def fields(data, limits):
    if not isinstance(data, dict):
        raise ValueError("입력 항목을 확인해 주세요.")
    values = []
    for key, maximum in limits.items():
        value = data.get(key)
        if not isinstance(value, str) or not 0 < len(value.strip()) <= maximum:
            raise ValueError("입력 항목과 글자 수를 확인해 주세요.")
        values.append(value.strip())
    return values


class Handler(SimpleHTTPRequestHandler):
    def list_directory(self, path):
        self.send_error(404)
        return None

    def reply(self, status, data=None):
        payload = json.dumps(data, ensure_ascii=False).encode("utf-8") if data is not None else b""
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Vary", "Origin")
        if ORIGIN and self.headers.get("Origin") == ORIGIN:
            self.send_header("Access-Control-Allow-Origin", ORIGIN)
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        if payload:
            self.wfile.write(payload)

    def do_OPTIONS(self):
        if not urlsplit(self.path).path.startswith("/api/"):
            self.send_error(404)
            return
        self.reply(204)

    def do_GET(self):
        path = urlsplit(self.path).path
        if path == "/api/posts":
            with closing(connect()) as db:
                posts = [dict(row) for row in db.execute("""
                    SELECT *, (SELECT COUNT(*) FROM comments WHERE post_id = posts.id) AS comment_count
                    FROM posts ORDER BY (category = ?) DESC, id DESC LIMIT 100
                """, (NOTICE,))]
            self.reply(200, posts)
            return
        match = re.fullmatch(r"/api/posts/([0-9]{1,18})/comments", path)
        if match:
            with closing(connect()) as db:
                comments = [dict(row) for row in db.execute(
                    "SELECT * FROM comments WHERE post_id = ? ORDER BY id", (int(match[1]),)
                )]
            self.reply(200, comments)
            return
        super().do_GET()

    def do_POST(self):
        path = urlsplit(self.path).path
        match = re.fullmatch(r"/api/posts/([0-9]{1,18})/comments", path)
        if path != "/api/posts" and not match:
            self.reply(404, {"error": "요청한 페이지가 없습니다."})
            return
        if self.headers.get_content_type() != "application/json":
            self.reply(415, {"error": "지원하지 않는 요청 형식입니다."})
            return
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if not 0 < size <= 16384:
                raise ValueError("요청 크기를 확인해 주세요.")
            data = json.loads(self.rfile.read(size))
            with closing(connect()) as db, db:
                if match:
                    author, body = fields(data, {"author": 24, "body": 400})
                    post_id = int(match[1])
                    if not db.execute("SELECT id FROM posts WHERE id = ?", (post_id,)).fetchone():
                        self.reply(404, {"error": "게시글을 찾을 수 없습니다."})
                        return
                    item = db.execute(
                        "INSERT INTO comments (post_id, author, body) VALUES (?, ?, ?)",
                        (post_id, author, body),
                    )
                else:
                    category, author, title, body = fields(
                        data, {"category": 20, "author": 24, "title": 80, "body": 1500}
                    )
                    if category not in CATEGORIES:
                        raise ValueError("고객용 게시판을 선택해 주세요.")
                    item = db.execute(
                        "INSERT INTO posts (category, author, title, body) VALUES (?, ?, ?, ?)",
                        (category, author, title, body),
                    )
                item_id = item.lastrowid
        except (json.JSONDecodeError, UnicodeDecodeError):
            self.reply(400, {"error": "요청 형식을 확인해 주세요."})
            return
        except ValueError as error:
            self.reply(400, {"error": str(error)})
            return
        except sqlite3.IntegrityError:
            self.reply(409, {"error": "게시글 상태가 변경되었습니다. 새로고침해 주세요."})
            return
        self.reply(201, {"id": item_id})


def main():
    parser = argparse.ArgumentParser(description="Bread Compass website and community")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=int(os.environ.get("PORT", 8000)))
    parser.add_argument("--notice", nargs=2, metavar=("TITLE", "BODY"))
    parser.add_argument("--delete-post", type=int)
    parser.add_argument("--delete-comment", type=int)
    args = parser.parse_args()
    initialize()

    with closing(connect()) as db, db:
        if args.notice:
            title, body = fields(dict(zip(("title", "body"), args.notice)), {"title": 80, "body": 1500})
            db.execute(
                "INSERT INTO posts (category, author, title, body) VALUES (?, ?, ?, ?)",
                (NOTICE, "브레드 컴퍼스", title, body),
            )
            return
        if args.delete_post is not None:
            db.execute("DELETE FROM posts WHERE id = ?", (args.delete_post,))
            return
        if args.delete_comment is not None:
            db.execute("DELETE FROM comments WHERE id = ?", (args.delete_comment,))
            return

    handler = partial(Handler, directory=str(BASE / "docs"))
    with ThreadingHTTPServer((args.host, args.port), handler) as server:
        print(f"http://{args.host}:{server.server_port}/", flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    sys.exit(main())
