# 캔버스 → 사이트 동기화

캔버스(Claude Design 아티팩트 https://claude.ai/artifact/GnQangvfSwyDqs7UxXw5ZX)에서 고친 내용을 `docs/` 사이트에 반영하는 순서예요.

1. 아티팩트의 `project/*.dc.html`, `project/canvas.json`을 한 폴더로 받아요(아티팩트 read, path별로).
2. `python3 tools/sync/prepare.py <받은 폴더>` → `project/`, `docs/app/screens/` 갱신. `CHANGED`와 `MISSING_BLOBS`를 출력해요.
3. `MISSING_BLOBS`가 있으면 아티팩트 에셋을 id별로 받아 `docs/blobs/<id>.svg`로 넣어요.
4. 장표 이미지를 다시 찍으려면: 렌더러 `artifact-type/dc-runtime.js`를 아티팩트에서 받아 `tools/sync/.render/support.js`로 둬요(로컬 테스트용 · 커밋 금지, .gitignore 처리됨). 그다음
   `python3 tools/sync/serve.py tools/sync/.render docs/blobs 8765 &` → `node tools/sync/render.js`
5. 장표 순서/개수가 바뀌면 `slides.txt`와 `docs/deck.html`(N, names)도 같이 고쳐요.
6. `BrandSymbols.dc.html`이 바뀌었으면 `python3 tools/sync/symbols_section.py`로 랜딩의 심볼 섹션을 다시 만들어요.
7. `BrandSite.dc.html`(랜딩)이 바뀌었으면 `docs/index.html`에 같은 내용을 옮겨요(정적 버전이라 자동으로는 안 바뀌어요).

## 패키지 v8 (사용설명서 섹션)

패키지 3D 모형은 `RUMO 올인원 패키지 v8` 아티팩트(https://claude.ai/artifact/VYuXUBv8A7ntd73bgiQDoH)만 따라가요.
1. v8을 Artifact read(path "index.html")로 받아요.
2. `python3 tools/sync/package.py <받은 index.html>` → `docs/package/index.html` 갱신(전체 화면 3D + `?embed` 모드).
3. 랜딩의 사용설명서 섹션은 단계 문구·구성품 표를 이 페이지에서 바로 읽어서 따로 손볼 필요 없어요. 섹션 모양을 바꿀 때만 `python3 tools/sync/package_section.py`.
