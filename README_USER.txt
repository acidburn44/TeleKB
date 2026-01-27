# TeleKB 사용 가이드

## 1. 초기 설정

TeleKB를 실행하기 전에 API 키 설정이 필요합니다.

1.  이 폴더에 있는 `.env.template` 파일의 이름을 `.env`로 변경합니다.
2.  `.env` 파일을 메모장 등으로 열어 아래 정보를 입력합니다.

    *   **API_ID, API_HASH**: [https://my.telegram.org/apps](https://my.telegram.org/apps) 에서 발급받을 수 있습니다.
    *   **GEMINI_API_KEY**: [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey) 에서 발급받을 수 있습니다.

    작성 예시:
    ```
    API_ID=12345678
    API_HASH=abcdef1234567890abcdef1234567890
    GEMINI_API_KEY=AIzaSy...
    ```

## 2. 실행 방법

1.  `TeleKB.exe`를 더블 클릭하여 실행합니다.
2.  프로그램이 실행되면 텔레그램 로그인을 진행합니다. (최초 1회)
    *   전화번호 입력 (예: +821012345678)
    *   인증 코드 입력

## 3. 사용 방법

1.  **Output Directory**: 결과 파일이 저장될 폴더를 선택합니다.
2.  **Channel Management**: 수집할 채널을 관리합니다.
    *   [채널 추가] 버튼을 눌러 채널을 추가합니다.
3.  **Run Collection**: 수집을 시작합니다.

## 주의사항

*   `.env` 파일에는 개인 키 정보가 들어있으므로 타인에게 공유하지 마세요.
*   `telekb_session.session` 파일은 텔레그램 로그인 정보를 담고 있습니다. 절대 삭제하거나 공유하지 마세요.
