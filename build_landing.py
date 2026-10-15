# -*- coding: utf-8 -*-
"""쏙이의 꿀템굴 — 링크 랜딩페이지 빌더.
사용법: python build_landing.py <작업폴더> [출력경로]
  기본 출력: <작업폴더>/docs/index.html  (GitHub Pages: Settings > Pages > /docs)

설계 의도
  · 인스타 bio 링크는 한 번만 등록하고 영구 고정한다. 상품 교체는 이 파일만 갱신.
  · 유입원 분리는 쿼리스트링으로 처리한다.
      ?from=ig → instagramreels subId 링크
      ?from=yt → youtubeshorts subId 링크
      없으면   → deepLink(기본)
    따라서 subId 리포트가 채널별로 계속 분리된다.
  · 대가성 고지문을 상단 고정 + 각 카드 + 푸터 3곳에 노출한다(파트너스 반려 사유 차단).
"""
import json, os, sys, html, datetime

MAX_CARDS = 9              # 최신 게시물 우선 노출 수
BRAND = "쏙이의 꿀템굴"
YOUTUBE = "https://www.youtube.com/@hotaeshin502"
INSTAGRAM = "https://www.instagram.com/shin.hotae/"
DISCLOSURE = ("이 포스팅은 쿠팡 파트너스 활동의 일환으로, "
              "이에 따른 일정액의 수수료를 제공받습니다.")

CSS = """
*{box-sizing:border-box;margin:0;padding:0}
:root{
  --ink:#462814; --sub:#8e7a68; --cream:#fbe4c4; --teal:#2e8b7e;
  --orange:#c76822; --bg1:#fff7ec; --bg2:#e0f3f0; --card:#fff; --line:#f0e2cd;
}
html{-webkit-text-size-adjust:100%}
body{
  font-family:'Pretendard','Apple SD Gothic Neo','Noto Sans KR',system-ui,sans-serif;
  color:var(--ink); background:linear-gradient(170deg,var(--bg1),var(--bg2));
  min-height:100vh; line-height:1.6; padding:0 16px 56px;
}
.wrap{max-width:520px;margin:0 auto}
header{text-align:center;padding:36px 0 16px}
h1{font-size:26px;font-weight:800;letter-spacing:-.02em}
.tag{color:var(--teal);font-size:14px;font-weight:700;margin-top:6px}
.notice{
  background:#fff;border:2px solid var(--cream);border-radius:14px;
  padding:12px 14px;font-size:12.5px;color:var(--sub);margin:16px 0 22px;text-align:center
}
.asof{text-align:center;font-size:12px;color:var(--sub);margin-bottom:18px}
.card{
  background:var(--card);border:1px solid var(--line);border-radius:18px;
  padding:18px 18px 16px;margin-bottom:14px;box-shadow:0 2px 10px rgba(120,80,40,.05)
}
.badge{
  display:inline-block;background:var(--ink);color:#fff;font-size:11px;font-weight:700;
  border-radius:6px;padding:3px 8px;margin-bottom:10px;letter-spacing:.02em
}
.name{font-size:17px;font-weight:700;line-height:1.4}
.price{font-size:24px;font-weight:800;margin:8px 0 4px}
.meta{font-size:12.5px;color:var(--sub)}
.check{
  background:#fffaf2;border-radius:10px;padding:10px 12px;margin:12px 0 14px;
  font-size:12.5px;color:var(--ink)
}
.check b{display:block;color:var(--orange);font-size:11.5px;margin-bottom:4px;font-weight:700}
.check span{display:block}
.btn{
  display:block;text-align:center;background:var(--teal);color:#fff;text-decoration:none;
  font-weight:700;font-size:15px;border-radius:12px;padding:13px;letter-spacing:-.01em
}
.btn:active{opacity:.82}
.fine{font-size:11px;color:var(--sub);margin-top:9px;text-align:center}
.links{margin-top:26px;display:grid;gap:10px}
.links a{
  display:block;text-align:center;background:#fff;border:1px solid var(--line);
  border-radius:12px;padding:12px;text-decoration:none;color:var(--ink);
  font-weight:700;font-size:14px
}
footer{margin-top:28px;text-align:center;font-size:11.5px;color:var(--sub);line-height:1.7}
@media (prefers-color-scheme:dark){
  :root{--ink:#f3e7d8;--sub:#b9a690;--card:#2a2320;--line:#473a30;--bg1:#241d19;--bg2:#1b2524}
  .check{background:#342b25}
  .links a{background:#2a2320}
  .notice{background:#2a2320;border-color:#473a30}
}
"""

JS = """
(function(){
  var p = new URLSearchParams(location.search).get('from');
  var key = p === 'ig' ? 'ig' : (p === 'yt' ? 'yt' : 'base');
  document.querySelectorAll('a[data-base]').forEach(function(a){
    a.href = a.dataset[key] || a.dataset.base;
  });
})();
"""


def card(p, checks):
    h = p["history"][-1]
    links = {
        "base": p.get("deepLink") or "",
        "ig": p.get("deepLinkInstagram") or p.get("deepLink") or "",
        "yt": p.get("deepLinkYoutube") or p.get("deepLink") or "",
    }
    c = checks.get(p["id"], [])
    chk = ""
    if c:
        chk = ('<div class="check"><b>구매 전 확인</b>'
               + "".join(f"<span>{html.escape(x)}</span>" for x in c) + "</div>")
    return f"""      <div class="card">
        <span class="badge">광고</span>
        <div class="name">{html.escape(p['name'])}</div>
        <div class="price">{h['price']:,}원</div>
        <div class="meta">쿠팡 {html.escape(p['keyword'])} 판매량순 {h['rank']}위 ·
          후기 {h['review']:,}개 · 평점 {h['rating']}</div>
{chk}
        <a class="btn" data-base="{links['base']}" data-ig="{links['ig']}"
           data-yt="{links['yt']}" href="{links['base']}"
           target="_blank" rel="nofollow noopener">쿠팡에서 보기</a>
        <div class="fine">{DISCLOSURE}</div>
      </div>"""


def main():
    root = sys.argv[1] if len(sys.argv) > 1 else "."
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(root, "docs", "index.html")
    prods = json.load(open(os.path.join(root, "products.json"), encoding="utf-8"))["products"]

    chk_path = os.path.join(root, "checks.json")
    checks = json.load(open(chk_path, encoding="utf-8")) if os.path.exists(chk_path) else {}

    live = [p for p in prods.values() if p.get("videoStatus") == "게시"]
    live.sort(key=lambda p: (p.get("postedAt") or "", p.get("usedAt") or ""), reverse=True)
    live = live[:MAX_CARDS]
    if not live:
        raise SystemExit("게시 상태 상품 없음 — 랜딩 생성 중단")

    asof = max((p["history"][-1]["date"] for p in live), default="")
    cards = "\n".join(card(p, checks) for p in live)
    today = datetime.date.today().isoformat()

    doc = f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{BRAND}</title>
<meta name="description" content="반려동물 꿀템 큐레이션 · 쿠팡 파트너스">
<meta name="robots" content="noindex">
<style>{CSS}</style>
</head>
<body>
  <div class="wrap">
    <header>
      <h1>{BRAND}</h1>
      <div class="tag">반려동물 꿀템 큐레이션</div>
    </header>

    <div class="notice">{DISCLOSURE}</div>
    <div class="asof">순위·후기 수·가격은 {asof} 쿠팡 검색 판매량순 화면 기준이며 변동될 수 있습니다.</div>

{cards}

    <div class="links">
      <a href="{YOUTUBE}" target="_blank" rel="noopener">유튜브 채널</a>
      <a href="{INSTAGRAM}" target="_blank" rel="noopener">인스타그램</a>
    </div>

    <footer>
      {DISCLOSURE}<br>
      제품 사양·가격은 판매 페이지에서 직접 확인하시기 바랍니다.<br>
      최종 갱신 {today}
    </footer>
  </div>
<script>{JS}</script>
</body>
</html>
"""
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, "w", encoding="utf-8").write(doc)
    print(f"OK {out} cards={len(live)} asof={asof}")


if __name__ == "__main__":
    main()
