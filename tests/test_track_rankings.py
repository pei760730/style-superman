from scripts import track_rankings as rankings


def test_snapshots_defaults_to_empty_list():
    assert rankings.snapshots({}) == []
    assert rankings.snapshots({"snapshots": [{"period": "2026-Q1"}]}) == [
        {"period": "2026-Q1"}
    ]


def test_comparison_requires_two_snapshots():
    assert rankings.lyst_comparison_text({"snapshots": []}) is None
    assert rankings.lyst_comparison_text({"snapshots": [{"period": "2026-Q1"}]}) is None


def test_comparison_reports_moves_new_entries_and_drops():
    data = {
        "snapshots": [
            {
                "period": "2026-Q2",
                "brands": [
                    {"rank": 1, "name": "Up"},
                    {"rank": 2, "name": "Same"},
                    {"rank": 3, "name": "Down"},
                    {"rank": 4, "name": "New", "move": "new"},
                    {"rank": 5, "name": "Returning", "move": "re-entry"},
                    {"rank": 6, "name": "Unlabeled"},
                ],
            },
            {
                "period": "2026-Q1",
                "brands": [
                    {"rank": 3, "name": "Up"},
                    {"rank": 2, "name": "Same"},
                    {"rank": 1, "name": "Down"},
                    {"rank": 4, "name": "Dropped"},
                ],
            },
        ]
    }

    text = rankings.lyst_comparison_text(data)

    assert "2026-Q1 → 2026-Q2" in text
    assert "Up                 ↑ 2" in text
    assert "Same               — 持平" in text
    assert "Down               ↓ 2" in text
    assert "New                🆕 新進榜" in text
    assert "Returning          重返榜" in text
    assert "Unlabeled          本季入榜（上季未列榜）" in text
    assert "掉出榜外：Dropped" in text


def test_partial_previous_snapshot_avoids_false_new_and_dropped_claims():
    data = {
        "snapshots": [
            {
                "period": "new",
                "brands": [{"rank": 1, "name": "Unknown", "move": "re-entry"}],
            },
            {
                "period": "old",
                "coverage": "partial Top 10",
                "brands": [{"rank": 1, "name": "Known"}],
            },
        ]
    }

    text = rankings.lyst_comparison_text(data, top=1)

    assert "殘缺快照" in text
    assert "前季殘缺，無法判定" in text
    assert "🆕" not in text
    assert "重返榜" not in text
    assert "掉出榜外" not in text


def test_partial_current_snapshot_keeps_known_changes_but_does_not_infer_drops():
    data = {
        "snapshots": [
            {
                "period": "2026-Q2",
                "coverage": "partial Top 10",
                "brands": [
                    {"rank": 1, "name": "Up"},
                    {"rank": 5, "name": "New", "move": "new"},
                    {"rank": 7, "name": "Returning", "move": "re-entry"},
                ],
            },
            {
                "period": "2026-Q1",
                "coverage": "full",
                "brands": [{"rank": 2, "name": "Up"}, {"rank": 17, "name": "Not in excerpt"}],
            },
        ]
    }

    text = rankings.lyst_comparison_text(data)

    assert "掉出榜外：" not in text
    assert "本季（2026-Q2）為殘缺快照" in text
    assert "Up                 ↑ 1" in text
    assert "New                🆕 新進榜" in text
    assert "Returning          重返榜" in text
