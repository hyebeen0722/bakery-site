# 브레드 컴퍼스

가상의 동네 베이커리 홍보 사이트입니다. 홈에는 대표 메뉴와 매장 안내가 있고, 고객 커뮤니티에서는 주제별 글과 댓글을 공유할 수 있습니다. 실제 매장명, 메뉴 가격, 주소와 운영시간은 공개 전에 `docs/index.html`에서 반영하세요.

## 서버 없이 열기

`docs` 폴더 전체를 같은 위치에 보관한 뒤 `index.html`을 브라우저에서 엽니다. 스마트폰에서도 파일 미리보기 대신 HTML과 JavaScript를 실행하는 브라우저로 엽니다. 파일 모드에서는 글과 댓글이 해당 기기와 브라우저의 로컬 저장 공간에 보관됩니다. 같은 파일 경로에서 다시 열어 확인할 수 있으며 브라우저의 파일 저장 정책에 따라 이용 가능 여부가 달라집니다.

## 여러 방문자가 게시판을 공유하도록 Windows에서 실행

프로젝트 폴더의 PowerShell에서 다음 명령을 실행합니다. Python 3.11 기준이며 별도 패키지 설치가 필요 없습니다.

```powershell
python server.py
```

- 홈 · [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- 고객 커뮤니티 · [http://127.0.0.1:8000/community.html](http://127.0.0.1:8000/community.html)

게시글과 댓글은 서버의 `community.sqlite3`에 저장됩니다. 같은 서버에 접속하는 방문자는 동일한 게시판을 봅니다.

## 매장 공지와 게시물 관리

서버와 같은 폴더에서 실행하며, 운영 서버에서 데이터베이스 경로를 설정했다면 관리 명령에도 동일한 `COMMUNITY_DB` 값을 사용합니다.

```powershell
python server.py --notice "시즌 메뉴 안내" "이번 주부터 계절 잼 데니시를 소개합니다."
```

공지 작성은 서버 운영 명령으로 제공됩니다. 게시글이나 댓글을 내릴 때는 각 API 응답의 ID를 확인한 뒤 `python server.py --delete-post 123` 또는 `python server.py --delete-comment 123`을 사용합니다. 게시글을 삭제하면 연결된 댓글도 삭제됩니다.

## GitHub Pages에 배포할 때

1. [GitHub 연결 가이드](GITHUB-DEPLOYMENT.md)에 따라 소스를 저장소에 올립니다. `docs/`, `server.py`, `.gitignore`를 포함하고 로컬 데이터베이스와 비밀 값은 Git에 올리지 않습니다.
2. GitHub Pages의 배포 소스로 `main`의 `/docs`를 선택합니다.
3. 커뮤니티에는 별도 Python 서버가 필요합니다. 같은 서버에서 웹사이트와 API를 함께 제공하는 구성도 가능합니다. 제공된 서버는 로컬 실행용입니다. 인터넷 공개 운영 시에는 HTTPS, 요청 제한과 접근 로그를 처리하는 운영 환경을 갖추고 영구 저장소에 `COMMUNITY_DB`를 지정하세요. 운영 환경에서 `python server.py --host 0.0.0.0`으로 실행하면 `PORT` 환경 변수에 지정된 포트를 사용합니다.
4. Pages와 API를 분리할 때는 `docs/community-config.js`의 `window.COMMUNITY_API`에 서버 HTTPS 주소를 설정합니다. 서버의 `COMMUNITY_ORIGIN`에는 Pages의 출처를 설정합니다. 예를 들어 사이트 주소가 `https://OWNER.github.io/REPOSITORY/`라면 출처는 `https://OWNER.github.io`입니다.
5. 공개 주소에서 글과 댓글을 작성하고, 다른 브라우저에서도 내용이 보이는지 확인합니다.
