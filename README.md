# 쏙이의 꿀템굴 — 링크 랜딩

인스타그램 bio / 유튜브 설명란에 거는 **영구 고정 링크**. 상품이 바뀌어도 이 페이지만 갱신하면 됨.

## 유입원 분기

| 링크 | 붙는 위치 | 적용 subId |
|---|---|---|
| `/?from=ig` | 인스타 bio | instagramreels |
| `/?from=yt` | 유튜브 설명란 | youtubeshorts |
| `/` | 기타 | 기본 deepLink |

쿼리로 subId를 갈라 쿠팡 파트너스 리포트에서 채널별 수익이 분리 집계됨.

## 갱신

```
python build_landing.py . docs/index.html
git commit -am "landing update" && git push
```

`products.json` 중 `videoStatus == "게시"` 인 상품을 최신순 9개까지 노출.
구매 전 확인 문구는 `checks.json` (productId → 2줄).

## 고지

대가성 문구를 상단 고정 / 각 카드 하단 / 푸터 3곳에 노출함. 쿠팡 파트너스 최종승인 반려 사유(경제적 이해관계 미표시) 차단 목적이므로 임의 제거 금지.
`noindex` 설정 — 검색 노출 차단.
