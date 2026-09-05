import json

from scripts import validate_repo as validate


def _write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_low_level_contract_helpers_report_type_missing_and_duplicates(tmp_path):
    errors = []
    assert validate.require_mapping([], tmp_path / "x.yml", errors) == {}
    assert validate.require_list({}, "items", errors) == []
    assert validate.missing_fields({"id": "", "name": None}, {"id", "name", "url"}) == [
        "id",
        "name",
        "url",
    ]
    validate.check_unique([{"id": "a"}, {"id": "a"}], "id", "items", errors)
    assert any("top-level YAML must be a mapping" in error for error in errors)
    assert "items: must be a list" in errors
    assert "items: duplicate id='a'" in errors
    assert validate.CheckResult("ok", []).ok
    assert not validate.CheckResult("bad", ["error"]).ok


def test_source_brand_people_and_taxonomy_checks_validate_semantics(tmp_path, monkeypatch):
    monkeypatch.setattr(validate, "DATA_DIR", tmp_path)
    _write(
        tmp_path / "sources.yml",
        "sources:\n"
        "  - {id: duplicate, name: A, region: jp, type: media, tier: A, url: https://a}\n"
        "  - {id: duplicate, name: B, region: jp, type: media, tier: A, url: https://b, "
        "body_fetchable: false}\n"
        "  - invalid\n",
    )
    _write(
        tmp_path / "brands.yml",
        "brands:\n  - {id: b, name: B, region: jp, segment: designer, tier: A, watch: wrong}\n",
    )
    _write(
        tmp_path / "people.yml",
        "people:\n  - {id: p, name: P, role: designer, region: jp, influence: high, watch: wrong}\n",
    )
    _write(
        tmp_path / "trend_taxonomy.yml",
        "categories:\n  - {id: c, name: C, desc: D}\ntag_groups: []\n",
    )

    source_errors = validate.check_sources().errors
    assert any("body_fetch_note" in error for error in source_errors)
    assert any("duplicate id" in error for error in source_errors)
    assert any("sources[3] must be a mapping" in error for error in source_errors)
    assert any("watch must be a list" in error for error in validate.check_brands().errors)
    assert any("watch must be a list" in error for error in validate.check_people().errors)
    taxonomy_errors = validate.check_taxonomy().errors
    assert any("tag_groups must be a mapping" in error for error in taxonomy_errors)
    assert any("missing examples" in error for error in taxonomy_errors)


def test_rank_checks_reject_bool_duplicate_and_missing_display_keys(tmp_path, monkeypatch):
    errors = []
    validate.check_rank_values(
        [{"rank": True}, {"rank": 1, "name": "A"}, {"rank": 1, "name": "B"}],
        tmp_path / "rank.yml",
        "brands",
        errors,
        ("name",),
    )
    assert any("rank must be an integer" in error for error in errors)
    assert any("missing name" in error for error in errors)
    assert any("duplicate ranks" in error for error in errors)

    monkeypatch.setattr(validate, "ROOT", tmp_path)
    lyst = tmp_path / "lyst.yml"
    _write(
        lyst,
        "source: lyst-index\nsnapshots:\n  - period: 2026-Q2\n"
        "    brands: [{rank: 1}]\n    products: [{rank: 1, brand: B}]\n",
    )
    assert len(validate.check_ranking_file(lyst).errors) == 2

    stockx = tmp_path / "stockx.yml"
    _write(stockx, "source: stockx\nsnapshots:\n  - period: annual\n    ranking: []\n")
    assert "must not collapse" in validate.check_ranking_file(stockx).errors[0]

    kream = tmp_path / "kream.yml"
    _write(kream, "source: kream\nsnapshots:\n  - period: now\n")
    assert len(validate.check_ranking_file(kream).errors) == 2


def test_generic_yaml_check_catches_parse_and_top_level_errors(tmp_path, monkeypatch):
    monkeypatch.setattr(validate, "ROOT", tmp_path)
    malformed = tmp_path / "malformed.yml"
    _write(malformed, "key: [\n")
    assert "YAML 無法解析" in validate.check_yaml_parseable(malformed).errors[0]

    sequence = tmp_path / "sequence.yml"
    _write(sequence, "- one\n")
    assert "top-level YAML must be a mapping" in validate.check_yaml_parseable(sequence).errors[0]


def test_reader_schema_node_reports_required_unknown_type_and_enum():
    schema = {
        "type": "object",
        "required": ["items"],
        "properties": {
            "items": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["evidence"],
                    "properties": {"evidence": {"enum": ["親測"]}},
                },
            }
        },
    }
    errors = []
    validate._check_reader_example_node({"items": [{"evidence": "聽說", "extra": 1}]}, schema, "root", errors)
    assert any("不在 enum" in error for error in errors)
    assert any("schema 未定義欄位" in error for error in errors)

    errors = []
    validate._check_reader_example_node({}, schema, "root", errors)
    assert any("缺少必填欄位" in error for error in errors)

    errors = []
    validate._check_reader_example_node({"items": {}}, schema, "root", errors)
    assert any("必須是 array" in error for error in errors)


def test_reader_schema_contract_accepts_matching_prompt_and_rejects_bad_json(tmp_path, monkeypatch):
    data_dir = tmp_path / "data"
    monkeypatch.setattr(validate, "ROOT", tmp_path)
    monkeypatch.setattr(validate, "DATA_DIR", data_dir)
    _write(
        data_dir / "scan_units.yml",
        "reader_output_schema:\n  type: object\n  required: [items]\n  properties:\n"
        "    items:\n      type: array\n      items:\n        type: object\n"
        "        required: [evidence]\n        properties:\n"
        "          evidence:\n            enum: [親測]\n",
    )
    prompt = tmp_path / "prompts" / "region_reader.md"
    _write(prompt, "## 輸出範例\n```json\n" + json.dumps({"items": [{"evidence": "親測"}]}, ensure_ascii=False) + "\n```\n")
    assert validate.check_reader_schema_contract().ok

    _write(prompt, "## 輸出範例\n```json\n{bad}\n```\n")
    assert "不是合法 JSON" in validate.check_reader_schema_contract().errors[0]


def test_template_checks_report_missing_file_and_required_text(tmp_path, monkeypatch):
    monkeypatch.setattr(validate, "TEMPLATES_DIR", tmp_path)
    monkeypatch.setattr(
        validate,
        "TEMPLATE_REQUIREMENTS",
        {"missing.md": ["x"], "present.md": ["required", "also"]},
    )
    _write(tmp_path / "present.md", "required only")

    results = validate.check_templates()

    assert "missing template" in results[0].errors[0]
    assert "missing required text 'also'" in results[1].errors[0]


def test_report_checks_skip_drafts_and_enforce_names_freezes_and_h1(tmp_path, monkeypatch):
    monkeypatch.setattr(validate, "REPORTS_DIR", tmp_path)
    for subdir in validate.REPORT_PATTERNS:
        (tmp_path / subdir).mkdir()
    _write(tmp_path / "daily" / "2026-06-17.md", "# archived")
    _write(tmp_path / "daily" / "bad.md", "no heading")
    _write(tmp_path / "daily" / "ignore.draft.md", "no heading")
    _write(tmp_path / "flash" / "2026-07-26.md", "# archived")
    _write(tmp_path / "monthly" / "2026-08-eu.md", "not h1")

    by_name = {result.name: result.errors for result in validate.check_reports()}

    assert any("D16 違規" in error for error in by_name["reports/daily"])
    assert any("filename does not match" in error for error in by_name["reports/daily"])
    assert any("D35 違規" in error for error in by_name["reports/flash"])
    assert any("level-1 heading" in error for error in by_name["reports/monthly"])
    assert not any("ignore.draft.md" in error for error in by_name["reports/daily"])


def test_print_results_returns_failure_only_for_errors(capsys):
    assert validate.print_results([validate.CheckResult("good", [])]) == 0
    assert "✅ good" in capsys.readouterr().out
    assert validate.print_results([validate.CheckResult("bad", ["why"])]) == 1
    output = capsys.readouterr().out
    assert "❌ bad" in output
    assert "why" in output


def test_template_requirements_pin_the_contracts_that_other_layers_depend_on():
    """`TEMPLATE_REQUIREMENTS` 的**內容**要有守衛，不能只驗機制。

    立法理由（2026-09-05 突變稽核）：既有的 template 測試把整個字典 monkeypatch 掉，
    所以 D40 剛加的 `**上週複驗：**` 契約**可以直接刪掉、測試全綠**——而
    `repo_health.check_weekly_review` 正靠那個欄位存在才讀得到數字。

    這裡只釘「有其他層依賴」的欄位，不是把整份模板抄第二遍（那才會漂）。
    """
    weekly = validate.TEMPLATE_REQUIREMENTS["weekly_buy_picks_template.md"]
    assert "**上週複驗：**" in weekly, (
        "weekly 模板契約少了「上週複驗」——D40 的判斷軸靠它，"
        "repo_health.check_weekly_review 會永遠印「未記」"
    )
    assert "{{week}}" in weekly, "少了 {{week}}，generator 的替換就沒有守衛"

    monthly = validate.TEMPLATE_REQUIREMENTS["monthly_heat_report_template.md"]
    assert "{{month}}" in monthly


def test_every_template_file_has_a_contract_entry():
    """`templates/` 裡每一支 `.md` 都要在 `TEMPLATE_REQUIREMENTS` 裡有條目。

    立法理由：`TEMPLATE_REQUIREMENTS` 是手工同步清單（＝靜默漏洞的標準形狀）。
    2026-09-05 稽核實測 `templates/raw_signal_pack_template.md` 根本沒登記，
    新增模板不接契約沒有任何東西會說話。改成從目錄推導。
    """
    on_disk = {p.name for p in (validate.ROOT / "templates").glob("*.md")}
    registered = set(validate.TEMPLATE_REQUIREMENTS)
    missing = sorted(on_disk - registered)
    assert not missing, f"這些模板沒有契約條目（至少填 [] 表示刻意不驗）：{missing}"
    stale = sorted(registered - on_disk)
    assert not stale, f"契約指向不存在的模板：{stale}"
