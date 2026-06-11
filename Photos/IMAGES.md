# 이미지 관리 가이드 (Photos/)

이 사이트는 빌드 과정이 없는 **정적 `index.html`** 입니다. 이미지는 두 곳에서 관리합니다.
- **`Photos/`** — 사이트 고정 이미지(로고·배경·연구·멤버). 아래 폴더 구조를 따릅니다.
- **`News_Blog_JPG/`** — 뉴스/블로그 행사 사진. JSON으로 자동 로딩됩니다(맨 아래 참고).

---

## 핵심 규칙 (꼭 지키기)

1. **파일명은 ASCII 소문자 + 하이픈(kebab-case) + 확장자 필수.**
   한글·공백·특수문자 금지. (한글 파일명은 NFD/NFC 차이로 깃허브·서버에서 조용히 404가 납니다 — 실제로 두 번 겪었습니다.)
2. **교체는 "같은 이름으로 덮어쓰기".** 사진을 바꿀 땐 파일명을 그대로 두고 내용만 교체하세요. → HTML을 건드릴 필요가 없습니다.
3. **멤버 파일명 = 페이지 슬러그.** `members/<slug>.<ext>` 의 `<slug>` 는 `showPage('member-<slug>')` 의 그 슬러그와 같습니다.

---

## 폴더 구조

```
Photos/
  brand/        logo.png                      로고(파비콘·네비·푸터 공용)
  backgrounds/  home-1.png  home-2.png        메인 히어로 슬라이드 (home-1은 Introduce 히어로에도 재사용)
  research/     data.webp     data-wide.png   Data & Analysis      (.webp=카드, -wide.png=상세 배너)
                systems.webp  systems-wide.png Building Systems
                urban.webp    urban-wide.png  Building & Urban Modeling
  projects/     <key>-1.jpg <key>-2.jpg …      프로젝트 상세 갤러리 (연속 번호, 자동 표시)
  members/      professor.png                 교수님
                <slug>.<ext>                  정식 프로필 헤드샷 (멤버 카드·프로필·논문 저자)
                <slug>-sm.png                 작은 썸네일 (프로젝트 팀·people-row용)
  _archive/     (미사용 보관)
```

### 멤버 슬러그 표
| 이름 | slug | 헤드샷 파일 | 썸네일 파일 |
|---|---|---|---|
| 이상민 | sangmin | members/sangmin.jpeg | members/sangmin-sm.png |
| 조정현 | junghyun | members/junghyun.png | members/junghyun-sm.png |
| 백재욱 | jaeuk | members/jaeuk.jpeg | members/jaeuk-sm.png |
| 한지웅 | jiung | members/jiung.png | members/jiung-sm.png |
| 이도연 | doyeon | members/doyeon.png | members/doyeon-sm.png |
| 김인섭 | inseob | members/inseob.jpg | members/inseob-sm.png |
| 김지영 | jiyoung | members/jiyoung.jpg | members/jiyoung-sm.png |
| 황정윤 | jungyun | members/jungyun.jpg | members/jungyun-sm.png |
| 임지수 | jisu | members/jisu.jpg | members/jisu-sm.png |
| 이현수 | hyunsu | members/hyunsu.jpeg | members/hyunsu-sm.png |
| 이경재 (Alumni) | kyungjae | members/kyungjae.png | — |
| 임현우 (교수) | professor | members/professor.png | — |

> 헤드샷과 썸네일 확장자가 섞여 있는 건 원본 포맷을 그대로 유지했기 때문입니다(.jpg/.jpeg/.png). 교체할 때는 **같은 파일명·같은 확장자**로 덮어쓰면 됩니다.

---

## 자주 하는 작업

### 멤버 사진 바꾸기
`Photos/members/<slug>.<ext>` 를 같은 이름으로 덮어쓰기. (썸네일도 바꾸려면 `<slug>-sm.png` 도 교체) → HTML 수정 불필요.

### 새 멤버 추가하기
1. 헤드샷을 `members/<새slug>.png` 로 저장(필요시 썸네일 `members/<새slug>-sm.png`).
2. `index.html` 의 멤버 그리드/프로필 페이지에서 기존 멤버 블록을 복사해 `showPage('member-<새slug>')` 와 `Photos/members/<새slug>.png` 로 수정.

### 연구 대표 이미지 바꾸기
- 카드용: `research/<topic>.webp` (작게 표시, 가벼운 webp 권장)
- 상세 페이지 풀폭 배너: `research/<topic>-wide.png` (가로로 넓은 고해상도) — `topic ∈ data | systems | urban`
- 같은 이름으로 덮어쓰면 끝.

### 배경 슬라이드 바꾸기
`backgrounds/home-1.png`, `home-2.png` 덮어쓰기. (home-1은 Introduce 페이지 히어로에도 쓰임)

### 프로젝트 상세 갤러리에 사진 추가하기
각 프로젝트 상세 페이지 하단에 "프로젝트 갤러리" 공간이 있고, `Photos/projects/`의 사진을 **자동으로** 읽어 표시합니다(클릭 시 라이트박스로 확대).
- 파일명: `projects/<key>-1.jpg`, `<key>-2.jpg`, … 처럼 **1부터 연속 번호**로 저장(중간 번호가 비면 거기서 멈춤). 확장자는 `.jpg/.png/.jpeg/.webp` 자동 인식.
- 프로젝트별 `<key>`:
  - DataNet → `datanet`   (예: `projects/datanet-1.jpg`, `datanet-2.jpg` …)
  - 그린리모델링 → `green`
  - LH 지열 모니터링 → `lh`
  - 탄소중립 도시 시뮬레이션 → `carbon`
- 사진이 하나도 없으면 그 갤러리 영역은 자동으로 숨겨집니다. HTML 수정 불필요.

---

## 뉴스/블로그 행사 사진 추가 (가장 자주 하는 작업)

HTML 수정 없이 JSON으로 반영됩니다.

1. 폴더 생성: `News_Blog_JPG/beelab_images/News/<행사이름>/` (블로그는 `.../Blog/<행사이름>/`).
   - 가능하면 **간단한 ASCII 이름** 권장(아래 주의 참고).
2. 사진을 `001.jpg, 002.jpg, 003.jpg …` 순번으로 저장.
   - 확장자는 `.jpg` 우선, 없으면 `.png → .jpeg → .webp` 순으로 자동 대체됩니다.
3. `News_Blog_JPG/beelab_content/news.json`(또는 `blog.json`)에 항목 추가:
   ```json
   {
     "title": "행사 제목",
     "folder": "<행사이름>",
     "image_count": 3,
     "date": "Nov 28, 2025",
     "body": "내용(선택)"
   }
   ```
   - `image_count` = 실제 사진 장수.

> **주의:** `folder` 값은 디스크의 실제 폴더명과 **글자가 정확히 일치**해야 합니다. 한글 폴더명은 NFD/NFC 차이로 일치하지 않아 사진이 조용히 안 보일 수 있으니, 새 폴더는 ASCII 이름을 쓰는 게 안전합니다. 깃허브 웹에서 편집할 때 앞뒤 공백이 들어가지 않게 주의하세요.
