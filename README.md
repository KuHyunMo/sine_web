# sine web

### 구현 기능

회원 가입, 로그인, 프로필

url : https://implementmo.world

### 기술 스택

| **분류** | **기술 스택** | **선택 이유** |
| --- | --- | --- |
| **Frontend** | HTML5, CSS, JS | 웹 표준 기술
활용한 UI 구성 및 서버 API와의 비동기 통신 |
| **Backend** | **Python (Flask)** | 가벼우면서도 확장이 용이함 |
| **Database** | **MySQL** | 관계형 데이터베이스(RDBMS)의 표준
데이터 정규화 및 무결성 보장 |
| **Server** | **AWS EC2 (Ubuntu)** | 클라우드 인프라 경험
리눅스 환경에서의 서버 제어 경험 |
| **Proxy** | **Nginx** | 보안을 위한 리버스 프록시 구성 및 정적 파일 처리 최적화
WAS(Flask)를 외부망에 노출하지 않아 직접적인 공격 방지 |
| **Security** | **Certbot (SSL)** | 비용 없이 HTTPS를 구축
만료 전 자동 갱신으로 유지보수 최소화 |

### 전체 구조

**3-Tier Architecture**를 따르며 Nginx가 앞단에서 요청을 관리함

• **Proxy**

 80(HTTP) 요청을 443(HTTPS)으로 강제 전환하고, 복호화된 요청을 내부 Flask 서버(5000번 포트)로 전달

• Frontend

HTML5, CSS3, JavaScript를 활용하여 사용자 UI 제공 및 서버 API 통신

• **Backend**

 비즈니스 로직 처리 및 MySQL 데이터베이스와의 트랜잭션 수행

• **Database**: 1:1 및 1:N 관계의 3개 테이블로 구성.
    ◦ `users`: 계정 정보 (ID, PW 해시)
    ◦ `user_profiles`: 상세 정보 (이메일, 사진 URL, 자기소개)
    ◦ `profile_sections`: 유저별 동적 추가 섹션 (추가 소개글)

사용자 정보 및 서비스 데이터를 관계형 구조로 안전하게 저장 및 관리

### 배포 과정

- **인프라 세팅**: AWS EC2 인스턴스 생성
- **환경 구축**: Python 가상환경(`venv`)을 통한 라이브러리 의존성 격리 및 설치
- **데이터베이스 구성**: MySQL 설치 및 Flask 애플리케이션과의 연동 설정
- **리버스 프록시 설정**: Nginx의 `proxy_pass` 기능을 이용해 Flask 애플리케이션 연결
- **도메인**: 도메인 구매 후 DNS A 레코드 설정하고 퍼블릭 IPv4 주소와 연결
- **서비스 영속성 확보**: `nohup` 명령어를 사용하여 SSH 세션 종료 후에도 서버가 24시간 상주하도록 설정
- **SSL 적용:** Certbot을 활용한 Let's Encrypt HTTPS 인증서 발급
 ****

### **막혔던 부분과 해결 방법**

Issue 1: AttributeError: 'NoneType' object has no attribute 'cursor'
• 현상: DB 연결 실패 시 conn이 None이 되어 이후 코드에서 에러 발생.
• 원인: DB 정보가 틀려 get_db_connection()이 실패함.
• 해결: DB 정보를 갱신함

Issue 2: 회원 탈퇴 시 사진 파일 잔류
• 현상: DB에서 유저를 삭제(CASCADE)해도 서버 하드디스크의 이미지 파일은 삭제되지 않음
• 원인: DB 데이터와 서버의 물리 파일 시스템은 별개로 동작함.
• 해결: os.remove()를 사용하여 DB 삭제 전 실제 파일 경로를 조회해 먼저 삭제하는 로직 구현

Issue 3: 로그인 실패 시 알림창(Toggle/Alert) 중복 발생
• 현상: 아이디/비번이 틀렸을 때 알림창이 두 번 뜸.
• 원인: JS 코드 내 log(result.message)라는 오타로 인해 ReferenceError가 발생, try 문이 중단되고 catch 블록의 알림이 추가로 실행됨
• 해결: 오타 수정

Issue 4: 502 bad Gateway 에러
• 현상: 메인 접속 시 Nginx에서 502 에러 발생
• 원인: JNginx(프록시)는 살아있으나 flask 서버(python)이 꺼져있었음
• 해결: `python3 app.py`로 에러 로그 확인 후, 가상환경(`source venv/bin/activate`)을 활성화하고 `nohup`을 이용해 백그라운드에서 재실행하여 해결

Issue 5: Certbot 인증 실패 (NXDOMAIN)
• 현상: HTTPS 인증서 발급 중 `NXDOMAIN` 에러 발생
• 원인: 설정 파일(`server_name`)에 도메인 오타가 있었음
• 해결: 오타 수정 후 재시도