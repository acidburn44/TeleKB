# TeleKB (Telegram Knowledge Base)

TeleKB is a local GUI application that collects messages from your subscribed Telegram channels and groups. It intelligently detects non-Korean messages, translates them using Google's Gemini API, and saves them as Markdown files for your personal knowledge base.

## Features

*   **Channel Management**: Easily add or remove (hard delete) channels and groups via a GUI.
*   **Smart Collection**: Collects only new messages since the last run.
*   **Auto Translation**: Automatically detects non-Korean messages and translates them to Korean using **Google Gemini**.
*   **Markdown Export**: Saves messages as `.md` files, preserving original formatting, hyperlinks, and URLs. Messages are consolidated into a single file per channel per day (`channel_YYYYMMDD.md`).
*   **Duplicate Prevention**: Uses a local SQLite database to prevent saving duplicate messages.
*   **GUI-based Login**: Convenient Telegram login with a popup dialog for phone number and code entry.

## Prerequisites

1.  **Python 3.8** or higher.
2.  **Telegram API Credentials**:
    *   Go to [my.telegram.org](https://my.telegram.org) and log in.
    *   Select **API development tools**.
    *   Create a new application to get your `API_ID` and `API_HASH`.
3.  **Google Gemini API Key**:
    *   Get an API key from [Google AI Studio](https://aistudio.google.com/).

## Installation

1.  Clone or download this repository.
2.  Install the required dependencies:
    ```bash
    pip install -r TeleKB/requirements.txt
    ```

## Configuration

1.  Create a `.env` file in the project root (copy from `.env.example`).
2.  Fill in your credentials:
    ```ini
    API_ID=12345678
    API_HASH=your_telegram_api_hash
    GEMINI_API_KEY=your_gemini_api_key
    ```

## Usage

### 1. Running the Application
Run the `main.py` script:
```bash
python main.py
```

### 2. First-Time Login
*   When you try to add a channel for the first time, a **Login Dialog** will appear.
*   Enter your phone number (including country code, e.g., `+821012345678`).
*   Enter the verification code sent to your Telegram app.
*   (If enabled) Enter your Two-Step Verification password.
*   Once logged in, a `telekb_session.session` file will be created locally.

### 3. Managing Channels
*   Click **Channel Management**.
*   **Add Channel**: Click "Add Channel", select the channels/groups you want to archive, and click "Add Selected".
*   **Delete Channel**: Select a channel and click "Delete Channel" to remove it from the database permanently.

### 4. Collecting Messages
*   In the main window, choose an **Output Directory**.
*   Click **Run Collection**.
*   The application will fetch new messages, translate them if necessary, and save them as Markdown files in the selected folder using a `YYYY-MM` directory structure.

## Troubleshooting

*   **Login Issues**: If you face persistent login errors, try deleting the `telekb_session.session` file and logging in again.
*   **Database Locked**: If you see "database is locked" errors, ensure only one instance of the app is running. (The app is designed to handle concurrency internally).
*   **Translation Errors**: Verify your Gemini API Key is valid and has quota remaining.
*   **Channels Not Loading**: Use the "Refresh" button in Channel Management or check your internet connection.

## License
MIT License

---

# TeleKB (Telegram Knowledge Base)

TeleKB는 구독 중인 텔레그램 채널과 그룹의 메시지를 수집하는 로컬 GUI 애플리케이션입니다. 한국어가 아닌 메시지를 자동으로 감지하여 구글 Gemini API로 번역하고, 나만의 지식 베이스를 위해 Markdown 파일로 저장합니다.

## 주요 기능

*   **채널 관리**: GUI를 통해 채널 통계를 확인하고 추가하거나 완전히 삭제(Hard Delete)할 수 있습니다.
*   **스마트 수집**: 마지막 실행 이후의 새로운 메시지만 수집합니다.
*   **자동 번역**: 비한국어 메시지를 감지하여 **Google Gemini**로 자동 번역합니다.
*   **Markdown 내보내기**: 원본 서식, 하이퍼링크, URL을 유지한 채 `.md` 파일로 저장합니다. 메시지는 채널별/일자별로 하나의 파일(`channel_YYYYMMDD.md`)에 통합되어 저장됩니다.
*   **중복 방지**: 로컬 SQLite 데이터베이스를 사용하여 중복 메시지 저장을 방지합니다.
*   **GUI 기반 로그인**: 전화번호 및 인증 코드 입력을 위한 팝업 대화상자를 통해 편리하게 로그인할 수 있습니다.

## 사전 요구 사항

1.  **Python 3.8** 이상.
2.  **Telegram API 자격 증명**:
    *   [my.telegram.org](https://my.telegram.org)에 로그인합니다.
    *   **API development tools**를 선택합니다.
    *   새 애플리케이션을 생성하여 `API_ID`와 `API_HASH`를 발급받습니다.
3.  **Google Gemini API 키**:
    *   [Google AI Studio](https://aistudio.google.com/)에서 API 키를 발급받습니다.

## 설치 방법

1.  이 저장소를 클론하거나 다운로드합니다.
2.  필요한 의존성 패키지를 설치합니다:
    ```bash
    pip install -r TeleKB/requirements.txt
    ```

## 설정

1.  프로젝트 루트에 `.env` 파일을 생성합니다 (`.env.example` 복사).
2.  발급받은 키를 입력합니다:
    ```ini
    API_ID=12345678
    API_HASH=your_telegram_api_hash
    GEMINI_API_KEY=your_gemini_api_key
    ```

## 사용 방법

### 1. 애플리케이션 실행
`main.py` 스크립트를 실행합니다:
```bash
python main.py
```

### 2. 최초 로그인
*   채널을 추가하려고 할 때 **로그인 대화상자**가 나타납니다.
*   전화번호(국가 코드 포함, 예: `+821012345678`)를 입력합니다.
*   텔레그램 앱으로 전송된 인증 코드를 입력합니다.
*   (설정된 경우) 2단계 인증 비밀번호를 입력합니다.
*   로그인이 완료되면 로컬에 `telekb_session.session` 파일이 생성됩니다.

### 3. 채널 관리
*   **Channel Management** 버튼을 클릭합니다.
*   **Add Channel**: "Add Channel"을 클릭하고 수집할 채널/그룹을 선택한 뒤 "Add Selected"를 누릅니다.
*   **Delete Channel**: 채널을 선택하고 "Delete Channel"을 누르면 데이터베이스에서 영구적으로 삭제됩니다.

### 4. 메시지 수집
*   메인 창에서 **Output Directory**를 선택합니다.
*   **Run Collection**을 클릭합니다.
*   앱이 새로운 메시지를 가져와 번역(필요 시)하고, 선택한 폴더 내 `YYYY-MM` 디렉토리에 Markdown 파일로 저장합니다.

## 문제 해결

*   **로그인 문제**: 지속적인 로그인 오류 발생 시 `telekb_session.session` 파일을 삭제하고 다시 시도하세요.
*   **데이터베이스 잠금(Locked)**: "database is locked" 오류가 발생하면 앱이 중복 실행되고 있지 않은지 확인하세요. (앱은 내부적으로 동시성을 처리하도록 설계되었습니다.)
*   **번역 오류**: Gemini API 키가 유효한지, 할당량이 남아있는지 확인하세요.
*   **채널 로딩 불가**: 채널 관리 창에서 "Refresh" 버튼을 누르거나 인터넷 연결을 확인하세요.

## 라이선스
MIT License
