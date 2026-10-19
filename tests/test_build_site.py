import pytest

from build_site import load_scores, main, render_html


def test_load_scores(tmp_path):
    csv_file = tmp_path / "scores.csv"
    csv_file.write_text("name,score\nเอ,90\nบี,40\n", encoding="utf-8")
    assert load_scores(csv_file) == [("เอ", 90), ("บี", 40)]


@pytest.mark.parametrize(
    ("csv_content", "error_message"),
    [
        ("name,score\n,90\n", "ชื่อห้ามว่าง"),
        ("name,score\nเอ,90\nเอ,80\n", "ชื่อซ้ำ"),
    ],
)
def test_load_scores_rejects_empty_or_duplicate_names(
    tmp_path, csv_content, error_message
):
    csv_file = tmp_path / "scores.csv"
    csv_file.write_text(csv_content, encoding="utf-8")

    with pytest.raises(ValueError, match=error_message):
        load_scores(csv_file)


def test_render_html_has_title_and_rows():
    page = render_html([("สมชาย", 85), ("ปิติ", 48)], "ทดสอบ")
    assert "<title>ทดสอบ</title>" in page
    assert "<td>สมชาย</td><td>85</td><td>A</td>" in page
    assert "<td>ปิติ</td><td>48</td><td>F</td>" in page
    assert "ค่าเฉลี่ย: 66.5" in page
    assert "คะแนนสูงสุด: 85" in page
    assert "คะแนนต่ำสุด: 48" in page
    assert "อัตราผ่าน: 50.00%" in page


def test_render_html_escapes_names():
    page = render_html([("<script>", 50)], "ทดสอบ")
    assert "<script>" not in page
    assert "&lt;script&gt;" in page


def test_real_data_file_is_valid():
    rows = load_scores("data/scores.csv")
    assert len(rows) > 0
    assert all(0 <= score <= 100 for _, score in rows)


def test_main_builds_site(tmp_path, monkeypatch):
    (tmp_path / "data").mkdir()
    (tmp_path / "data" / "scores.csv").write_text(
        "name,score\nเอ,90\n", encoding="utf-8"
    )
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("SITE_TITLE", "หัวข้อ จาก Variable")
    main()
    page = (tmp_path / "_site" / "index.html").read_text(encoding="utf-8")
    assert "<h1>หัวข้อ จาก Variable</h1>" in page
