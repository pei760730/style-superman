import io
import json
import urllib.error

from scripts import fetch_article

FIXTURES = fetch_article.ROOT / "tests" / "fixtures"


class FakeResponse:
    def __init__(self, body, status=200):
        self.body = body
        self.status = status

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False

    def read(self):
        return self.body


def test_fetch_returns_status_and_handles_http_and_transport_errors(monkeypatch):
    monkeypatch.setattr(
        fetch_article.urllib.request,
        "urlopen",
        lambda request, timeout: FakeResponse(b"<html>ok</html>", 201),
    )
    assert fetch_article.fetch("https://example.com", 2) == (201, "<html>ok</html>")

    def forbidden(request, timeout):
        raise urllib.error.HTTPError(request.full_url, 403, "forbidden", {}, io.BytesIO())

    monkeypatch.setattr(fetch_article.urllib.request, "urlopen", forbidden)
    assert fetch_article.fetch("https://example.com") == (403, "")

    monkeypatch.setattr(fetch_article.urllib.request, "urlopen", lambda request, timeout: 1 / 0)
    assert fetch_article.fetch("https://example.com") == (0, "")


def test_html_extractors_choose_article_and_remove_non_content_blocks():
    raw = (FIXTURES / "sample_article.html").read_text(encoding="utf-8")

    region = fetch_article.main_region(raw)
    text = fetch_article.to_text(region)

    assert "Six Linen Shirts Worth Knowing" in text
    assert "$118" in text
    assert "SCRIPTNOISE" not in text
    assert "STYLENOISE" not in text
    assert "SIDEBARNOISE" not in text
    assert fetch_article.title_of(raw) == "Six Linen Shirts Worth Knowing – Fixture Times"
    assert fetch_article.published_of(raw) == "2026-07-28"


def test_main_region_falls_back_from_short_article_to_main_then_page():
    main = "M" * 501
    raw = "<article>short</article><main>" + main + "</main>"
    assert fetch_article.main_region(raw) == main
    assert fetch_article.main_region("<article>short</article><p>page</p>") == (
        "<article>short</article><p>page</p>"
    )


def test_title_and_published_fallbacks_are_honest():
    assert fetch_article.title_of("<h1>Hello <em>World</em></h1>") == "Hello World"
    assert fetch_article.title_of("<p>none</p>") == ""
    assert fetch_article.published_of('<meta name="date" content="2026-08-01">') == "2026-08-01"
    assert fetch_article.published_of('<time datetime="2026-08-02T12:00:00">') == "2026-08-02"
    assert fetch_article.published_of('{"datePublished":"2026-08-03"}') == "2026-08-03"
    assert fetch_article.published_of("<p>none</p>") == "待查"


def test_known_domains_normalizes_www_without_corrupting_wwd(tmp_path, monkeypatch):
    path = tmp_path / "sources.yml"
    path.write_text(
        "sources:\n"
        "  - url: https://www.example.com/articles\n"
        "    rss: https://wwd.com/feed\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(fetch_article, "SOURCES", path)

    assert fetch_article.known_domains() == {"example.com", "wwd.com"}
    monkeypatch.setattr(fetch_article, "yaml", None)
    assert fetch_article.known_domains() == set()


def test_article_returns_structured_success_and_failure():
    raw = (FIXTURES / "sample_article.html").read_text(encoding="utf-8")

    result = fetch_article.article(
        "https://example.com/story", max_chars=220, fetcher=lambda url, timeout: (200, raw)
    )
    assert result["status"] == 200
    assert result["published"] == "2026-07-28"
    assert result["chars"] == 220
    assert result["ok"] is True
    assert len(result["text"]) == 220

    failure = fetch_article.article(
        "https://example.com/story", fetcher=lambda url, timeout: (503, "")
    )
    assert failure["status"] == 503
    assert failure["ok"] is False
    assert failure["published"] == "待查"


def test_main_json_output_is_offline_and_machine_readable(monkeypatch, capsys):
    result = {
        "url": "https://example.com/story",
        "status": 200,
        "title": "Title",
        "published": "2026-08-18",
        "chars": 250,
        "words": 40,
        "text": "x" * 250,
        "ok": True,
    }
    monkeypatch.setattr(fetch_article, "known_domains", lambda: {"example.com"})
    monkeypatch.setattr(fetch_article, "article", lambda url, timeout, max_chars: result)

    assert fetch_article.main(["https://example.com/story", "--json"]) == 0
    assert json.loads(capsys.readouterr().out)["title"] == "Title"


def test_main_maps_failures_to_stable_exit_codes(monkeypatch, capsys):
    monkeypatch.setattr(fetch_article, "known_domains", set)

    for status, expected in ((0, 4), (403, 3), (404, 3)):
        monkeypatch.setattr(
            fetch_article,
            "article",
            lambda url, timeout, max_chars, status=status: {
                "status": status,
                "ok": False,
                "chars": 0,
                "title": "",
                "published": "待查",
                "words": 0,
                "text": "",
                "url": url,
            },
        )
        assert fetch_article.main(["https://unknown.example/story"]) == expected

    output = capsys.readouterr().err
    assert "不在 data/sources.yml" in output
    assert "本視角被拒" in output


def test_main_marks_short_body_as_insufficient_evidence(monkeypatch, capsys):
    monkeypatch.setattr(fetch_article, "known_domains", lambda: {"example.com"})
    monkeypatch.setattr(
        fetch_article,
        "article",
        lambda url, timeout, max_chars: {
            "status": 200,
            "ok": False,
            "chars": 5,
            "title": "Short",
            "published": "待查",
            "words": 1,
            "text": "short",
            "url": url,
        },
    )

    assert fetch_article.main(["https://example.com/story"]) == 5
    assert "不足以當「讀過原文」" in capsys.readouterr().err


def test_body_exactly_at_minimum_counts_as_evidence():
    """`ok` 的門檻是 `>=`：長度剛好等於 `MIN_BODY_CHARS` 的正文算數。

    改成 `>` 只差一個字元，卻會讓「剛好及格」的文章被降級成 `待查` 而整條不列（D36 的
    取內文順序會誤判成本機也讀不到）。既有測試把 `article` 整個 mock 掉，這個邊界從沒跑過。
    """
    exact = "字" * fetch_article.MIN_BODY_CHARS
    html = f"<html><body><article><p>{exact}</p></article></body></html>"
    result = fetch_article.article(
        "https://example.com/a", fetcher=lambda url, timeout: (200, html)
    )
    assert result["chars"] == fetch_article.MIN_BODY_CHARS
    assert result["ok"] is True
