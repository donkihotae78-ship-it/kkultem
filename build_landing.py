# -*- coding: utf-8 -*-
"""꿀템 상점 — 검색 콘텐츠 사이트 빌더 (v2.1, 2026-10-21)
브랜드명을 네이버 블로그와 통일했다(쏙이의 꿀템굴 → 꿀템 상점, 2026-10-21).
쏙이는 영상 캐릭터명으로만 쓰고, 사이트·블로그 브랜드는 꿀템 상점으로 맞춘다.
사용법: python build_landing.py <작업폴더> [출력폴더]
  기본 출력: <작업폴더>/docs/   (GitHub Pages: Settings > Pages > /docs)

v1 → v2 변경 (수익 구조 전환)
  · v1 은 noindex 였다. 검색 엔진이 수집하지 않아 검색 유입이 구조적으로 0이었다 → 제거
  · 상품별 개별 페이지(p/<productId>.html) 신설. 긴꼬리 검색어를 받는 단위가 된다
  · 시계열(순위·후기·가격 변동) 표를 넣는다. 외부에 없는 고유 정보이고,
    운영정책의 "광고성 비중 과다" 제한에 대한 방어가 된다
  · title / description / canonical / OG / JSON-LD(Article) / sitemap.xml / robots.txt 추가
  · 쿠팡 링크는 페이지에서 직접 나간다(1홉). 유입원 분리는 v1 과 동일하게 ?from= 로 처리

금지 (파트너스 약관 제8조 · 공정위)
  · 효능·기호성·최상급 표현, 체험담형 서술, 클릭 유도 문구를 쓰지 않는다
  · 수치는 수집일 기준임을 병기한다
"""
import json, os, sys, html, datetime

BASE = "https://donkihotae78-ship-it.github.io/kkultem"
BRAND = "꿀템 상점"
YOUTUBE = "https://www.youtube.com/@hotaeshin502"
INSTAGRAM = "https://www.instagram.com/shin.hotae/"
# 네이버 블로그 「꿀템 상점」 (2026-10-22 연결). 올리브영은 자체 웹사이트를 허용
# 채널로 인정하지 않으므로(AUTORUN 27.1) 블로그가 몰 확장의 본진이다.
BLOG = "https://blog.naver.com/kkultemshop"
DISCLOSURE = ("이 포스팅은 쿠팡 파트너스 활동의 일환으로, "
              "이에 따른 일정액의 수수료를 제공받습니다.")
MAX_CARDS = 12

CSS = """
*{box-sizing:border-box;margin:0;padding:0}
:root{--ink:#462814;--sub:#8e7a68;--cream:#fbe4c4;--teal:#2e8b7e;--orange:#c76822;
 --bg1:#fff7ec;--bg2:#e0f3f0;--card:#fff;--line:#f0e2cd}
html{-webkit-text-size-adjust:100%}
body{font-family:'Pretendard','Apple SD Gothic Neo','Noto Sans KR',system-ui,sans-serif;
 color:var(--ink);background:linear-gradient(170deg,var(--bg1),var(--bg2));
 min-height:100vh;line-height:1.65;padding:0 16px 56px}
.wrap{max-width:640px;margin:0 auto}
header{padding:32px 0 12px}
h1{font-size:25px;font-weight:800;letter-spacing:-.02em;line-height:1.35}
h2{font-size:18px;font-weight:800;margin:26px 0 10px;letter-spacing:-.01em}
h3{font-size:15px;font-weight:700;margin:18px 0 6px}
.tag{color:var(--teal);font-size:14px;font-weight:700;margin-top:6px}
p{margin:8px 0;font-size:14.5px}
.lead{font-size:15px;color:var(--ink)}
.notice{background:#fff;border:2px solid var(--cream);border-radius:14px;padding:12px 14px;
 font-size:12.5px;color:var(--sub);margin:16px 0 20px}
.asof{font-size:12px;color:var(--sub);margin-bottom:16px}
.card{background:var(--card);border:1px solid var(--line);border-radius:18px;
 padding:18px;margin-bottom:14px;box-shadow:0 2px 10px rgba(120,80,40,.05)}
.badge{display:inline-block;background:var(--ink);color:#fff;font-size:11px;font-weight:700;
 border-radius:6px;padding:3px 8px;margin-bottom:10px}
.name{font-size:17px;font-weight:700;line-height:1.4}
.name a{color:inherit;text-decoration:none}
.price{font-size:24px;font-weight:800;margin:8px 0 4px}
.meta{font-size:12.5px;color:var(--sub)}
table{width:100%;border-collapse:collapse;margin:10px 0 4px;font-size:13px}
th,td{border:1px solid var(--line);padding:7px 8px;text-align:right}
th{background:#fffaf2;font-weight:700;text-align:center}
td:first-child,th:first-child{text-align:left}
.check{background:#fffaf2;border-radius:10px;padding:11px 13px;margin:12px 0 14px;font-size:13px}
.check b{display:block;color:var(--orange);font-size:11.5px;margin-bottom:5px}
.check span{display:block}
.btn{display:block;text-align:center;background:var(--teal);color:#fff;text-decoration:none;
 font-weight:700;font-size:15px;border-radius:12px;padding:13px}
.btn:active{opacity:.82}
.fine{font-size:11px;color:var(--sub);margin-top:9px;text-align:center}
ul{margin:8px 0 8px 18px;font-size:14.5px}
li{margin:4px 0}
.links{margin-top:26px;display:grid;gap:10px}
.links a{display:block;text-align:center;background:#fff;border:1px solid var(--line);
 border-radius:12px;padding:12px;text-decoration:none;color:var(--ink);font-weight:700;font-size:14px}
.crumb{font-size:12.5px;color:var(--sub);padding-top:20px}
.crumb a{color:var(--teal);text-decoration:none}
footer{margin-top:28px;text-align:center;font-size:11.5px;color:var(--sub);line-height:1.7}
@media (prefers-color-scheme:dark){
 :root{--ink:#f3e7d8;--sub:#b9a690;--card:#2a2320;--line:#473a30;--bg1:#241d19;--bg2:#1b2524}
 .check,th{background:#342b25}.links a,.notice{background:#2a2320}.notice{border-color:#473a30}}
"""

JS = """
(function(){var p=new URLSearchParams(location.search).get('from');
var k=p==='ig'?'ig':(p==='yt'?'yt':'base');
document.querySelectorAll('a[data-base]').forEach(function(a){a.href=a.dataset[k]||a.dataset.base;});})();
"""

E = html.escape


def head(title, desc, canonical, ld=None):
    j = f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>' if ld else ""
    return f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(title)}</title>
<meta name="description" content="{E(desc)}">
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="article">
<meta property="og:title" content="{E(title)}">
<meta property="og:description" content="{E(desc)}">
<meta property="og:url" content="{canonical}">
<meta property="og:site_name" content="{BRAND}">
<meta name="twitter:card" content="summary">
<style>{CSS}</style>
{j}
</head>
<body><div class="wrap">"""


def foot():
    return f"""
    <footer>{DISCLOSURE}<br>
      제품 사양·가격은 판매 페이지에서 직접 확인하시기 바랍니다.<br>
      최종 갱신 {datetime.date.today().isoformat()}</footer>
  </div><script>{JS}</script></body></html>
"""


def links_of(p):
    return {"base": p.get("deepLink") or "",
            "ig": p.get("deepLinkInstagram") or p.get("deepLink") or "",
            "yt": p.get("deepLinkYoutube") or p.get("deepLink") or ""}


def buy_btn(p, label="쿠팡 상품 페이지"):
    L = links_of(p)
    return (f'<a class="btn" data-base="{L["base"]}" data-ig="{L["ig"]}" data-yt="{L["yt"]}" '
            f'href="{L["base"]}" target="_blank" rel="nofollow noopener sponsored">{label}</a>'
            f'<div class="fine">{DISCLOSURE}</div>')


def history_table(p):
    h = p["history"]
    rows = []
    for i, x in enumerate(h):
        d = ""
        if i:
            dr = h[i - 1]["rank"] - x["rank"]
            dv = x["review"] - h[i - 1]["review"]
            d = f"{'+' if dr > 0 else ''}{dr} / {'+' if dv > 0 else ''}{dv:,}"
        rows.append(f"<tr><td>{x['date']}</td><td>{x['rank']}위</td><td>{x['review']:,}개</td>"
                    f"<td>{x['price']:,}원</td><td>{d or '-'}</td></tr>")
    return ("<table><tr><th>수집일</th><th>판매량순</th><th>후기</th><th>가격</th>"
            "<th>순위·후기 변동</th></tr>" + "".join(rows) + "</table>")


def product_page(p, checks, siblings):
    h = p["history"][-1]
    kw, nm = p["keyword"], p["name"]
    short = nm.split(",")[0].strip()
    title = f"{kw} {short} — 순위·후기 변동 기록 | {BRAND}"
    desc = (f"{kw} 쿠팡 판매량순 {h['rank']}위 {short}. {h['date']} 기준 "
            f"가격 {h['price']:,}원, 후기 {h['review']:,}개. 구매 전 확인할 항목과 수집일별 변동 기록.")
    url = f"{BASE}/p/{p['id']}.html"
    ld = {"@context": "https://schema.org", "@type": "Article", "headline": title[:110],
          "description": desc, "datePublished": p.get("firstSeen"), "dateModified": h["date"],
          "author": {"@type": "Organization", "name": BRAND},
          "publisher": {"@type": "Organization", "name": BRAND},
          "mainEntityOfPage": url, "inLanguage": "ko"}

    c = checks.get(p["id"], [])
    chk = ""
    if c:
        chk = ('<div class="check"><b>구매 전 확인</b>'
               + "".join(f"<span>{E(x)}</span>" for x in c) + "</div>")

    first, last = p["history"][0], h
    span = ""
    if len(p["history"]) > 1:
        dv = last["review"] - first["review"]
        dp = last["price"] - first["price"]
        span = (f"<p>{first['date']}부터 {last['date']}까지 후기 수는 {first['review']:,}개에서 "
                f"{last['review']:,}개로 {'+' if dv >= 0 else ''}{dv:,}개 변했고, "
                f"가격은 {first['price']:,}원에서 {last['price']:,}원으로 "
                f"{'변동이 없었습니다' if dp == 0 else ('+' if dp > 0 else '') + format(dp, ',') + '원 변했습니다'}.</p>")

    sib = ""
    if siblings:
        sib = ("<h2>같은 키워드의 다른 기록</h2><ul>" + "".join(
            f'<li><a href="{BASE}/p/{s["id"]}.html">{E(s["name"].split(",")[0].strip())}</a> — '
            f'{s["history"][-1]["price"]:,}원 · 판매량순 {s["history"][-1]["rank"]}위</li>'
            for s in siblings) + "</ul>")

    vid = ""
    if p.get("postUrl"):
        vid = f'<p>영상으로 보기 · <a href="{p["postUrl"]}" target="_blank" rel="noopener">유튜브 쇼츠</a></p>'

    return head(title, desc, url, ld) + f"""
    <div class="crumb"><a href="{BASE}/">{BRAND}</a> › {E(kw)}</div>
    <header><h1>{E(kw)} — {E(short)} 순위·후기 변동 기록</h1>
      <div class="tag">수집일 {h['date']} 기준</div></header>
    <div class="notice">{DISCLOSURE}</div>

    <p class="lead">쿠팡 <b>{E(kw)}</b> 검색의 판매량순 화면을 주기적으로 수집해, 이 상품의 순위와
      후기 수가 어떻게 변했는지 날짜별로 기록한 페이지입니다. 사용 후기가 아니라 공개 수치의 변동 기록입니다.</p>

    <h2>현재 수치</h2>
    <div class="card">
      <span class="badge">광고</span>
      <div class="name">{E(nm)}</div>
      <div class="price">{h['price']:,}원</div>
      <div class="meta">쿠팡 {E(kw)} 판매량순 {h['rank']}위 · 후기 {h['review']:,}개 · 평점 {h['rating']}</div>
      {chk}
      {buy_btn(p)}
    </div>

    <h2>수집일별 변동</h2>
    {history_table(p)}
    <p class="asof">순위·후기 수·가격은 각 수집일의 쿠팡 검색 판매량순 화면 기준이며 변동될 수 있습니다.</p>
    {span}
    {vid}
    {sib}

    <h2>고지</h2>
    <p class="meta">{DISCLOSURE} 본 페이지는 제품을 직접 사용해 본 후기가 아니며, 효능·품질을 보증하지 않습니다.
      구매 전 판매 페이지에서 사양과 가격을 직접 확인하시기 바랍니다.</p>

    <div class="links">
      <a href="{BASE}/">전체 기록 목록</a>
      <a href="{BLOG}" target="_blank" rel="noopener">네이버 블로그 꿀템 상점</a>
      <a href="{YOUTUBE}" target="_blank" rel="noopener">유튜브 채널</a>
    </div>""" + foot()


def index_page(live, checks):
    asof = max(p["history"][-1]["date"] for p in live)
    kws = sorted({p["keyword"] for p in live})
    # 2026-10-24: 카테고리 고정 문구 제거(AUTORUN 34.2 — 카테고리 무관, 전환 우선).
    #   수집 키워드가 홈·리빙·시즌으로 넓어지면 '반려동물 용품'이 내용과 어긋난다.
    title = f"{BRAND} — 쿠팡 판매량순 순위·후기 변동 기록"
    desc = ("쿠팡 판매량순 상위 상품의 순위·후기 수·가격 변동을 주기적으로 기록합니다. "
            + " · ".join(kws[:6]) + f" 등 {len(live)}개 상품, {asof} 기준.")
    ld = {"@context": "https://schema.org", "@type": "CollectionPage", "name": title,
          "description": desc, "url": BASE + "/", "dateModified": asof, "inLanguage": "ko"}

    cards = []
    for p in live:
        h = p["history"][-1]
        short = p["name"].split(",")[0].strip()
        cards.append(f"""      <div class="card">
        <span class="badge">광고</span>
        <div class="name"><a href="{BASE}/p/{p['id']}.html">{E(p['name'])}</a></div>
        <div class="price">{h['price']:,}원</div>
        <div class="meta">쿠팡 {E(p['keyword'])} 판매량순 {h['rank']}위 · 후기 {h['review']:,}개 · 평점 {h['rating']}</div>
        <p class="meta"><a href="{BASE}/p/{p['id']}.html">{E(short)} 순위·후기 변동 기록 보기</a></p>
        {buy_btn(p)}
      </div>""")

    return head(title, desc, BASE + "/", ld) + f"""
    <header><h1>{BRAND}</h1><div class="tag">쿠팡 판매량순 순위·후기 변동 기록</div></header>
    <div class="notice">{DISCLOSURE}</div>

    <p class="lead">쿠팡에서 <b>{E(' · '.join(kws))}</b> 키워드를 주기적으로 검색해,
      판매량순 상위 상품의 순위·후기 수·가격이 어떻게 변하는지 날짜별로 기록합니다.
      카테고리를 가리지 않고, 수집 중인 키워드는 위에 그대로 적습니다.
      사용 후기가 아니라 공개 수치의 변동 기록입니다.</p>

    <h2>기록 중인 상품</h2>
    <div class="asof">{asof} 수집 기준</div>
{chr(10).join(cards)}

    <h2>이 기록을 보는 법</h2>
    <ul>
      <li>판매량순 순위는 검색 시점의 화면 기준이며 수시로 바뀝니다.</li>
      <li>후기 증가량은 최근 수요를 보는 보조 지표로만 씁니다.</li>
      <li>가격은 수집 시점 기준이므로 구매 전 판매 페이지에서 반드시 확인해야 합니다.</li>
      <li>효능·품질에 대한 판단은 담지 않습니다. 공개 수치만 기록합니다.</li>
    </ul>

    <div class="links">
      <a href="{BLOG}" target="_blank" rel="noopener">네이버 블로그 꿀템 상점</a>
      <a href="{YOUTUBE}" target="_blank" rel="noopener">유튜브 채널</a>
      <a href="{INSTAGRAM}" target="_blank" rel="noopener">인스타그램</a>
    </div>""" + foot()


def main():
    root = sys.argv[1] if len(sys.argv) > 1 else "."
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(root, "docs")
    if out.endswith(".html"):                      # v1 호환: 파일 경로가 오면 상위 폴더를 쓴다
        out = os.path.dirname(out)
    prods = json.load(open(os.path.join(root, "products.json"), encoding="utf-8"))["products"]
    cp = os.path.join(root, "checks.json")
    checks = json.load(open(cp, encoding="utf-8")) if os.path.exists(cp) else {}

    live = [p for p in prods.values() if p.get("videoStatus") == "게시" and p.get("deepLink")]
    live.sort(key=lambda p: (p.get("postedAt") or "", p.get("usedAt") or ""), reverse=True)
    live = live[:MAX_CARDS]
    if not live:
        raise SystemExit("게시 상태 상품 없음 — 랜딩 생성 중단")

    os.makedirs(os.path.join(out, "p"), exist_ok=True)
    open(os.path.join(out, "index.html"), "w", encoding="utf-8").write(index_page(live, checks))

    for p in live:
        sib = [s for s in live if s["keyword"] == p["keyword"] and s["id"] != p["id"]]
        open(os.path.join(out, "p", f"{p['id']}.html"), "w", encoding="utf-8").write(
            product_page(p, checks, sib))

    today = datetime.date.today().isoformat()
    urls = [(BASE + "/", today, "0.9")] + [
        (f"{BASE}/p/{p['id']}.html", p["history"][-1]["date"], "0.8") for p in live]
    open(os.path.join(out, "sitemap.xml"), "w", encoding="utf-8").write(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join(f"  <url><loc>{u}</loc><lastmod>{m}</lastmod><priority>{pr}</priority></url>\n"
                  for u, m, pr in urls) + "</urlset>\n")
    open(os.path.join(out, "robots.txt"), "w", encoding="utf-8").write(
        f"User-agent: *\nAllow: /\nSitemap: {BASE}/sitemap.xml\n")

    print(f"OK {out} index=1 pages={len(live)} sitemap={len(urls)} asof={live[0]['history'][-1]['date']}")


if __name__ == "__main__":
    main()
