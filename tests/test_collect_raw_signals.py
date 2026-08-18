import io
import urllib.error

from scripts import collect_raw_signals as signals

FIXTURES = signals.ROOT / "tests" / "fixtures"


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


def test_spam_clean_and_date_helpers_encode_fact_layer_rules():
    assert signals.is_spam("Watch the match live free online")
    assert signals.is_spam("Normal title", "Join Telegram t.me/channel")
    assert not signals.is_spam("How to style a technical jacket")
    assert signals._clean("<p>A&nbsp; &amp; <b>B</b></p>") == "A & B"
    assert signals._clean("abcdef", limit=3) == "abc"
    assert signals._norm_date("Wed, 04 Jun 2026 10:00:00 +0000") == "2026-06-04"
    assert signals._norm_date("2026-06-05T10:00:00Z") == "2026-06-05"
    assert signals._norm_date("unknown") == "待查"


def test_parse_rss_fixture_preserves_source_metadata_and_unknown_judgments():
    xml = (FIXTURES / "sample_feed.xml").read_text(encoding="utf-8")
    source = {"id": "fixture", "tier": "A", "region": "jp"}

    rows = signals.parse_feed(xml, source, limit=1)

    assert rows == [
        {
            "source_id": "fixture",
            "source_tier": "A",
            "region": "jp",
            "url": "https://example.com/a",
            "title": "Test Brand A 發表 2099 春夏系列",
            "published": "2026-06-04",
            "summary": "合成測試摘要：Test Brand A 的 新系列 與聯名。",
            "signal_type": "待查",
            "credibility": "待查",
        }
    ]


def test_parse_atom_and_repairs_unbound_namespace():
    atom = """<feed xmlns="http://www.w3.org/2005/Atom">
    <entry><title>A &amp; B</title><link href="https://example.com/a"/>
    <updated>2026-08-18T00:00:00Z</updated><summary>&lt;b&gt;News&lt;/b&gt;</summary></entry>
    </feed>"""
    rows = signals.parse_feed(atom, {"id": "atom", "tier": "B", "region": "global"})
    assert rows[0]["title"] == "A & B"
    assert rows[0]["summary"] == "News"
    assert rows[0]["published"] == "2026-08-18"

    broken = """<rss><channel><item><title>Repair</title><link>https://example.com</link>
    <media:content url="x"/></item></channel></rss>"""
    assert signals.parse_feed(broken, {"id": "repair"})[0]["title"] == "Repair"
    assert signals.parse_feed("<not xml", {"id": "bad"}) == []


def test_fetch_feed_uses_reader_agent_and_decodes_replacement(monkeypatch):
    captured = {}

    def fake_urlopen(request, timeout):
        captured["agent"] = request.headers["User-agent"]
        captured["timeout"] = timeout
        return FakeResponse(b"hello\xff")

    monkeypatch.setattr(signals.urllib.request, "urlopen", fake_urlopen)

    assert signals.fetch_feed("https://example.com/feed", timeout=7) == "hello�"
    assert captured == {"agent": signals.UA, "timeout": 7}


def test_fetch_feed_retries_429_once_without_real_sleep(monkeypatch):
    calls = []

    def fake_urlopen(request, timeout):
        calls.append(request.full_url)
        if len(calls) == 1:
            raise urllib.error.HTTPError(request.full_url, 429, "limited", {}, io.BytesIO())
        return FakeResponse(b"ok")

    sleeps = []
    monkeypatch.setattr(signals.urllib.request, "urlopen", fake_urlopen)

    assert signals.fetch_feed("https://example.com/feed", sleep=sleeps.append) == "ok"
    assert len(calls) == 2
    assert sleeps == [3]


def test_fetch_feed_returns_none_for_http_and_transport_errors(monkeypatch):
    def forbidden(request, timeout):
        raise urllib.error.HTTPError(request.full_url, 403, "forbidden", {}, io.BytesIO())

    monkeypatch.setattr(signals.urllib.request, "urlopen", forbidden)
    assert signals.fetch_feed("https://example.com") is None

    monkeypatch.setattr(signals.urllib.request, "urlopen", lambda request, timeout: 1 / 0)
    assert signals.fetch_feed("https://example.com") is None


def test_collect_is_ordered_and_reports_fetch_parse_and_spam_failures():
    valid = (FIXTURES / "sample_feed.xml").read_text(encoding="utf-8")
    spam = """<rss><channel><item><title>Watch game live free online</title>
    <link>https://example.com/spam</link></item></channel></rss>"""
    sources = [
        {"id": "first", "rss": "first", "tier": "A", "region": "jp", "type": "media"},
        {"id": "missing", "rss": "missing", "type": "media"},
        {"id": "broken", "rss": "broken", "type": "media"},
        {"id": "community", "rss": "spam", "type": "community"},
    ]
    payloads = {"first": valid, "missing": None, "broken": "<bad", "spam": spam}

    rows, warnings = signals.collect(sources, limit=1, fetcher=payloads.get, max_workers=50)

    assert [row["source_id"] for row in rows] == ["first"]
    assert warnings == [
        "missing: 抓取失敗（跳過）",
        "broken: 解析不到項目（跳過）",
        "community: 標題層濾掉 1 則疑似 spam（盜播/導流）",
    ]
    assert signals.collect([], fetcher=lambda url: 1 / 0) == ([], [])


def test_rss_sources_and_yaml_output_use_local_files(tmp_path, monkeypatch):
    source_file = tmp_path / "sources.yml"
    source_file.write_text(
        "sources:\n  - {id: has, rss: https://example.com/feed}\n  - {id: none}\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(signals, "SOURCES", source_file)
    assert [source["id"] for source in signals.rss_sources()] == ["has"]

    text = signals.to_yaml([{"title": "中文"}])
    assert "事實層" in text
    assert "title: 中文" in text
