# 웹사이트를 GitHub에 연결하고 배포하기

이 가이드는 Windows PowerShell에서 완성한 웹사이트를 GitHub에 올리고, HTML·CSS·JavaScript로 만든 정적 사이트를 GitHub Pages에 공개하는 예시입니다.

## 1. 첫 업로드 준비

- GitHub에서 새 저장소를 만들고 HTTPS 주소를 복사합니다. 이미 로컬에 사이트 파일이 있다면 GitHub에서 README, 라이선스, `.gitignore`를 추가하지 않고 빈 저장소로 시작합니다.
- PowerShell에서 `index.html`이 있는 프로젝트 폴더를 열고 `git --version`으로 Git 설치를 확인합니다.
- API 키, 비밀번호, `.env` 파일은 커밋에서 제외합니다. 필요한 경우 로컬 `.gitignore`에 `.env`와 `.env.*`를 추가합니다. 브라우저에 제공하는 JavaScript에도 비밀 키를 넣지 않습니다.

[GitHub Docs · 로컬 코드를 GitHub에 추가하기](https://docs.github.com/en/migrations/importing-source-code/using-the-command-line-to-import-source-code/adding-locally-hosted-code-to-github?platform=windows)

## 2. 로컬 프로젝트와 GitHub 저장소 연결

아래는 새 로컬 저장소와 빈 GitHub 저장소를 연결하는 예시입니다. 파일명과 URL을 실제 프로젝트에 맞게 바꿉니다. 이미지 폴더처럼 사이트에 필요한 파일이 더 있으면 함께 추가합니다.

```powershell
git init -b main
git add -- index.html styles.css script.js
git diff --cached --stat
git commit -m "Add website files"
git remote add origin https://github.com/OWNER/REPOSITORY.git
git remote -v
git push -u origin main
```

`script.js` 등 예시 파일이 없다면 해당 이름을 `git add` 명령에서 뺍니다. Git에서 커밋 작성자 정보를 요청하면 `git config user.name`과 `git config user.email`로 이 저장소에 사용할 이름과 이메일을 설정한 뒤 다시 커밋합니다. HTTPS 푸시 중 로그인 창이 뜨면 안내에 따라 GitHub에 로그인합니다.

이미 Git을 사용하는 프로젝트라면 `git init`을 건너뛰고 `git branch --show-current`와 `git remote -v`로 현재 브랜치와 연결 주소를 확인합니다. `origin`이 올바르면 그대로 사용합니다. 다른 주소를 가리키고 의도적으로 연결을 바꿀 때는 `git remote set-url origin 새-HTTPS-주소`를 사용합니다. 원격 저장소에 기존 커밋이 있으면 먼저 그 내용을 확인하고 로컬 변경과 통합합니다.

[GitHub Docs · 원격 저장소 관리](https://docs.github.com/en/get-started/git-basics/managing-remote-repositories)

## 3. GitHub Pages 배포

1. GitHub 저장소에서 **Settings → Pages**를 엽니다.
2. **Build and deployment → Source**에서 **Deploy from a branch**를 선택합니다.
3. **Branch**에서 `main`과 `/(root)`를 고르고 **Save**를 누릅니다. `index.html`이 `docs` 폴더에 있다면 `/docs`를 선택합니다.
4. **Actions**에서 배포가 성공했는지 확인하고, **Settings → Pages**에 표시되는 주소를 엽니다. 프로젝트 사이트 주소는 보통 `https://OWNER.github.io/REPOSITORY/` 형식입니다.
5. 공개 주소에서 메뉴, 이미지, CSS가 실제로 로드되는지 확인합니다. 저장소 이름이 URL에 포함되는 프로젝트 사이트에서는 `/styles.css` 대신 `./styles.css` 같은 상대 경로를 사용하면 경로 오류를 줄일 수 있습니다.

[GitHub Docs · Pages 게시 소스 설정](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site)

## 4. 업데이트 또는 다른 호스팅 연결

- **GitHub Pages 업데이트**는 바뀐 파일을 `git add`로 선택하고 커밋한 뒤 `git push`로 올립니다. Pages에서 선택한 브랜치에 반영되면 새 배포 상태를 **Actions**에서 확인할 수 있습니다.
- **빌드가 필요한 정적 사이트**는 프레임워크가 생성한 결과물을 GitHub Actions로 Pages에 배포할 수 있습니다. **Settings → Pages → Source**에서 **GitHub Actions**를 선택하고 프로젝트에 맞는 빌드 워크플로를 구성합니다.
- **서버 실행이 필요한 사이트**는 해당 런타임을 지원하는 호스팅 서비스에서 GitHub 저장소를 가져옵니다. 배포 브랜치와 서비스에 필요한 빌드·실행 설정을 지정하고, 비밀 값은 호스팅 서비스의 환경 변수에 등록합니다. 자동 배포가 설정되면 해당 브랜치에 푸시한 뒤 서비스의 배포 로그와 공개 주소를 확인합니다.

[GitHub Docs · GitHub Actions로 사이트 자동 배포](https://docs.github.com/en/get-started/start-your-journey/deploying-your-website-automatically)
