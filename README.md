# sine web

### 구현 기능

회원 가입, 로그인, 프로필

url : https://implementmo.world

### 기술 스택

| **분류** | **기술 스택** | **선택 이유** |
| --- | --- | --- |
| **Frontend** | HTML5, CSS, JS | 웹 표준 기술<br>활용한 UI 구성 및 서버 API와의 비동기 통신 |
| **Backend** | **Python (Flask)** | 가벼우면서도 확장이 용이함 |
| **Database** | **MySQL** | 관계형 데이터베이스(RDBMS)의 표준<br>데이터 정규화 및 무결성 보장 |
| **Server** | **AWS EC2 (Ubuntu)** | 클라우드 인프라 경험<br>리눅스 환경에서의 서버 제어 경험 |
| **Proxy** | **Nginx** | 보안을 위한 리버스 프록시 구성 및 정적 파일 처리 최적화<br>AWS(Flask)를 외부망에 노출하지 않아 직접적인 공격 방지 |
| **Security** | **Certbot (SSL)** | 비용 없이 HTTPS를 구축<br>만료 전 자동 갱신으로 유지보수 최소화 |

### 전체 구조

**3-Tier Architecture**를 따르며 Nginx가 앞단에서 요청을 관리함

• **Proxy**

 80(HTTP) 요청을 443(HTTPS)으로 강제 전환하고, 복호화된 요청을 내부 Flask 서버(5000번 포트)로 전달

• Frontend

HTML5, CSS3, JavaScript를 활용하여 사용자 UI 제공 및 서버 API 통신

• **Backend**

 비즈니스 로직 처리 및 MySQL 데이터베이스와의 트랜잭션 수행

• **Database**: 1:1 및 1:N 관계의 3개 테이블로 구성.<br>
 ◦ `users`: 계정 정보 (ID, PW 해시)<br>
 ◦ `user_profiles`: 상세 정보 (이메일, 사진 URL, 자기소개)<br>
 ◦ `profile_sections`: 유저별 동적 추가 섹션 (추가 소개글)<br>
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
