import csv
import html
import os
from pathlib import Path

from grades import grade, pass_rate

OUTPUT_DIR = Path("_site")

def load_scores(csv_path):
    """อ่านไฟล์ CSV คืนค่าเป็น list ของ (ชื่อ, คะแนน)"""
    with open(csv_path, encoding="utf-8") as f:
        rows = [(row["name"], int(row["score"])) for row in csv.DictReader(f)]

    names = [name.strip() for name, _ in rows]
    if any(not name for name in names):
        raise ValueError("ชื่อห้ามว่าง")
    if len(names) != len(set(names)):
        raise ValueError("ชื่อซ้ำในไฟล์คะแนน")
    return rows

def render_html(rows, title):
    """สร้างหน้าเว็บ HTML จากข้อมูลคะแนน"""
    table_rows = "\n".join(
        f"<tr><td>{html.escape(name)}</td><td>{score}</td><td>{grade(score)}</td></tr>"
        for name, score in rows
    )
    scores = [score for _, score in rows]
    avg = sum(scores) / len(scores) if scores else 0
    highest_score = max(scores) if scores else 0
    lowest_score = min(scores) if scores else 0
    passing_rate = pass_rate(scores)

    return f"""<!DOCTYPE html>
<html lang="th">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light">
<title>{html.escape(title)}</title>
<style>
* {{ box-sizing: border-box; }}
body {{ margin: 0; background: #f3f5f8; color: #24334b; font-family: "Leelawadee UI", "Noto Sans Thai", Tahoma, sans-serif; line-height: 1.65; }}
.masthead {{ background: #142b49; color: white; border-top: 4px solid #b99a5b; }}
.brand {{ max-width: 1120px; margin: auto; padding: 22px 32px; display: flex; gap: 14px; align-items: center; }}
.mark {{ width: 44px; height: 44px; display: grid; place-items: center; border: 1px solid #71819a; border-radius: 10px; font-weight: 700; letter-spacing: .04em; }}
.brand strong {{ display: block; font-size: 17px; }}
.brand small {{ color: #c2cddd; font-size: 12px; letter-spacing: .1em; }}
main {{ max-width: 1120px; margin: auto; padding: 40px 32px 48px; }}
.eyebrow {{ color: #63738a; font-size: 12px; font-weight: 700; letter-spacing: .12em; margin: 0 0 10px; }}
h1 {{ color: #142b49; font-size: clamp(25px, 4vw, 36px); line-height: 1.4; margin: 0 0 10px; }}
.intro {{ margin: 0; color: #63738a; }}
.summary {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin: 28px 0; }}
.summary p {{ margin: 0; background: white; border: 1px solid #dce3ec; border-top: 3px solid #b99a5b; border-radius: 8px; padding: 23px 18px; font-size: 17px; font-weight: 600; color: #142b49; }}
.panel {{ border: 1px solid #dce3ec; border-radius: 12px; overflow: hidden; background: white; box-shadow: 0 4px 20px #142b4905; }}
.panel-heading {{ display: flex; justify-content: space-between; align-items: center; gap: 16px; padding: 22px 26px; border-bottom: 1px solid #e3e8ef; }}
h2 {{ font-size: 19px; margin: 0; color: #142b49; }}
.count {{ padding: 5px 12px; background: #edf2f7; border-radius: 20px; font-size: 13px; white-space: nowrap; }}
.table-wrap {{ overflow-x: auto; }}
table {{ width: 100%; border-collapse: collapse; text-align: left; }}
caption {{ text-align: left; padding: 14px 26px; color: #63738a; font-size: 13px; }}
th {{ background: #f7f9fc; padding: 14px 26px; color: #63738a; font-size: 13px; font-weight: 600; border-bottom: 1px solid #dce3ec; }}
td {{ padding: 18px 26px; border-bottom: 1px solid #edf0f5; font-size: 16px; }}
tr:last-child td {{ border-bottom: 0; }}
tbody tr:hover {{ background: #f7f9fc; }}
td:nth-child(2), th:nth-child(2) {{ text-align: right; font-variant-numeric: tabular-nums; }}
td:nth-child(3), th:nth-child(3) {{ text-align: center; width: 150px; }}
td:nth-child(3) {{ font-weight: 700; color: #274c74; }}
.criteria {{ display: flex; flex-wrap: wrap; gap: 8px 22px; padding: 18px 26px; border-top: 1px solid #e3e8ef; color: #63738a; background: #fafbfd; font-size: 12px; }}
.criteria strong {{ color: #24334b; }}
footer {{ display: flex; justify-content: space-between; gap: 14px; flex-wrap: wrap; margin-top: 24px; font-size: 12px; color: #63738a; }}
@media (max-width: 700px) {{ main {{ padding: 28px 18px; }} .brand {{ padding: 18px; }} .summary {{ grid-template-columns: repeat(2, 1fr); gap: 10px; }} .summary p {{ font-size: 15px; padding: 18px 12px; }} .panel-heading, td, th, caption {{ padding-left: 16px; padding-right: 16px; }} .criteria {{ padding: 16px; }} }}
@media print {{ body {{ background: white; }} main {{ padding: 20px 0; }} .masthead {{ background: white; color: #142b49; }} .brand small {{ color: #63738a; }} .panel {{ box-shadow: none; }} tr {{ break-inside: avoid; }} }}
</style>
</head>
<body>
<header class="masthead"><div class="brand">
<span class="mark" aria-hidden="true">CI</span>
<div><strong>ระบบประกาศผลการเรียน</strong><small>ACADEMIC RESULTS PORTAL</small></div>
</div></header>
<main>
<p class="eyebrow">ผลการประเมิน · CI/CD</p>
<h1>{html.escape(title)}</h1>
<p class="intro">รายงานคะแนนและผลการประเมิน พร้อมสรุปภาพรวมของผู้เรียน</p>
<section class="summary" aria-label="สรุปผลคะแนน">
<p>ค่าเฉลี่ย: {avg:.2f}</p>
<p>คะแนนสูงสุด: {highest_score}</p>
<p>คะแนนต่ำสุด: {lowest_score}</p>
<p>อัตราผ่าน: {passing_rate:.2f}%</p>
</section>
<section class="panel" aria-labelledby="results-heading">
<div class="panel-heading"><h2 id="results-heading">รายละเอียดผลคะแนน</h2><span class="count">ผู้เรียนทั้งหมด {len(rows)} คน</span></div>
<div class="table-wrap"><table>
<caption>คะแนนเต็ม 100 คะแนน · เกณฑ์ผ่านตั้งแต่ 50 คะแนนขึ้นไป</caption>
<thead><tr><th scope="col">ชื่อผู้เรียน</th><th scope="col">คะแนน</th><th scope="col">เกรด</th></tr></thead>
<tbody>
{table_rows}
</tbody>
</table></div>
<div class="criteria"><strong>เกณฑ์การประเมิน</strong><span>A 80–100</span><span>B+ 75–79</span><span>B 70–74</span><span>C+ 65–69</span><span>C 60–64</span><span>D 50–59</span><span>F ต่ำกว่า 50</span></div>
</section>
<footer><span>รายงานผลคะแนนรายวิชา CI/CD</span><span>หากพบข้อมูลคลาดเคลื่อน กรุณาติดต่อผู้สอน</span></footer>
</main>
</body>
</html>
"""


def main():
    title = os.environ.get("SITE_TITLE") or "ผลคะแนนวิชา CI/CD"
    rows = load_scores("data/scores.csv")
    OUTPUT_DIR.mkdir(exist_ok=True)
    (OUTPUT_DIR / "index.html").write_text(
        render_html(rows, title), encoding="utf-8"
    )
    print(f"Built {OUTPUT_DIR / 'index.html'} ({len(rows)} students)")


if __name__ == "__main__":
    main()
