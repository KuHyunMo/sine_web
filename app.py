import os
import filetype
import io
from PIL import Image 
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import pymysql
import pymysql.cursors
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from typing import Any, Optional

# 1. 환경 변수 로드
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')
if not app.secret_key:
    raise RuntimeError("SECRET_KEY 환경변수가 설정되지 않았습니다.")

# 업로드 폴더 설정
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'webp'}
MAX_FILE_SIZE = 5 * 1024 * 1024 
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 파일 검수 --------------
# 확장자 화이트리스트 검사
def is_allowed_extension(filename: str) -> bool:
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#매직 바이트로 실제 이미지 여부 검사 -> 확장자만 바꾼 웹셀 차단
def is_real_image(file_stream) -> bool:
    header = file_stream.read(512)
    file_stream.seek(0)
    kind = filetype.guess(header)
    if kind is None:
        return False
    return kind.mime in {'image/jpeg', 'image/png', 'image/gif', 'image/webp'}

    

#확장자 → 크기 → 매직바이트 → Pillow 순으로 검증 후 저장
def validate_and_save_image(profile_image, user_id: int) -> tuple[bool, str]:
    filename = secure_filename(str(profile_image.filename))

    # 1단계: 확장자 검사
    if not is_allowed_extension(filename):
        return False, "허용되지 않는 파일 형식입니다. (jpg, png, gif, webp만 가능)"

    # 2단계: 파일 크기 검사
    profile_image.stream.seek(0, 2)
    file_size = profile_image.stream.tell()
    profile_image.stream.seek(0)
    if file_size > MAX_FILE_SIZE:
        return False, "파일 크기는 5MB를 초과할 수 없습니다."

    # 3단계: 매직 바이트 검사
    if not is_real_image(profile_image.stream):
        return False, "실제 이미지 파일이 아닙니다."

    # 4단계: Pillow로 재인코딩 (EXIF 악성 메타데이터 제거)
    try:
        image_data = profile_image.stream.read()
        Image.open(io.BytesIO(image_data)).verify()

        clean_img = Image.open(io.BytesIO(image_data))
        img_format = clean_img.format
        output = io.BytesIO()
        clean_img.save(output, format=img_format)

        save_filename = f"user_{user_id}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], save_filename)
        with open(filepath, 'wb') as f:
            f.write(output.getvalue())

        return True, f"/static/uploads/{save_filename}"
    except Exception:
        return False, "이미지 처리 중 오류가 발생했습니다."

#

# 2. 데이터베이스 연결 함수 (반환 타입을 Optional로 명시)
def get_db_connection() -> Any: 
    try:
        conn = pymysql.connect(
            host=os.getenv("DB_HOST", "127.0.0.1"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", ""),
            database=os.getenv("DB_NAME", "web_hacking_study"),
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        return conn
    except Exception as e:
        print(f"❌ DB 연결 실패: {e}")
        return None

@app.route('/')
def login_page():
    return render_template('login.html')

@app.route('/joinmember')
def join_page():
    return render_template('joinmember.html')

# --- [API: 회원가입] ---
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    hashed_pw = generate_password_hash(password)
    conn = get_db_connection()
    
    #  여기서 확실하게 체크해주면 Pylance가 아래 코드에서 에러가 안남
    if conn is None:
        return jsonify({"status": "error", "message": "DB 연결 실패"}), 500
    
    try:
        with conn.cursor() as cursor: 
            cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_pw))
            user_id = cursor.lastrowid
            cursor.execute("INSERT INTO user_profiles (user_id) VALUES (%s)", (user_id,))
        conn.commit()
        return jsonify({"status": "success"})
    except Exception as e:
        conn.rollback()
        return jsonify({"status": "error", "message": str(e)})
    finally:
        conn.close()

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    conn = get_db_connection()
    if conn is None:
        return jsonify({"status": "error", "message": "DB 연결 실패"}), 500
    
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            user = cursor.fetchone()
            
            if user and check_password_hash(user['password'], password):
                session['user_id'] = user['id']
                session['username'] = user['username']
                return jsonify({"status": "success"})
            return jsonify({"status": "error", "message": "아이디나 비밀번호가 틀렸습니다."})
    finally:
        conn.close()

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login_page'))

# --- [프로필 조회 및 탈퇴] ---
@app.route('/profile')
def profile_page():
    if 'user_id' not in session: return redirect(url_for('login_page'))
    
    conn = get_db_connection()
    if conn is None: return "DB 연결 실패", 500
    
    try:
        with conn.cursor() as cursor:
            sql_user = "SELECT u.username, p.* FROM users u LEFT JOIN user_profiles p ON u.id = p.user_id WHERE u.id = %s"
            cursor.execute(sql_user, (session['user_id'],))
            user_info = cursor.fetchone()
            
            sql_sections = "SELECT * FROM profile_sections WHERE user_id = %s"
            cursor.execute(sql_sections, (session['user_id'],))
            sections_info = cursor.fetchall()
            
            return render_template('profile.html', user=user_info, sections=sections_info)
    finally:
        conn.close()

@app.route('/api/delete_account', methods=['POST'])
def api_delete_account():
    if 'user_id' not in session: return jsonify({"status": "error", "message": "로그인 필요"})
    
    user_id = session['user_id']
    conn = get_db_connection()
    if conn is None: return jsonify({"status": "error", "message": "DB 연결 실패"}), 500
    
    try:
        with conn.cursor() as cursor:
            # 1. 사진 파일 먼저 삭제
            cursor.execute("SELECT profile_image_url FROM user_profiles WHERE user_id = %s", (user_id,))
            profile = cursor.fetchone()
            if profile and profile['profile_image_url']:
                file_path = profile['profile_image_url'].lstrip('/')
                if os.path.exists(file_path):
                    os.remove(file_path)
            
            # 2. 유저 삭제
            cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        conn.commit()
        session.clear()
        return jsonify({"status": "success", "message": "회원 탈퇴 완료"})
    except Exception as e:
        conn.rollback()
        return jsonify({"status": "error", "message": str(e)})
    finally:
        conn.close()

# --- [프로필 수정] ---
@app.route('/edit_profile')
def edit_profile_page():
    if 'user_id' not in session: return redirect(url_for('login_page'))
    
    conn = get_db_connection()
    if conn is None: return "DB 연결 실패", 500
    
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM user_profiles WHERE user_id = %s", (session['user_id'],))
            return render_template('edit_profile.html', user=cursor.fetchone())
    finally:
        conn.close()

@app.route('/api/edit_profile', methods=['POST'])
def api_edit_profile():
    if 'user_id' not in session: return jsonify({"status": "error", "message": "로그인 필요"})
    
    user_id = session['user_id']
    email = request.form.get('email')
    phone_number = request.form.get('phone_number')
    bio = request.form.get('bio')
    profile_image = request.files.get('profile_image')
    image_url = None
    
    if profile_image and profile_image.filename:
        success, result = validate_and_save_image(profile_image, user_id)
        if not success:
            return jsonify({"status": "error", "message": result})
        image_url = result
        
    conn = get_db_connection()
    if conn is None: return jsonify({"status": "error", "message": "DB 연결 실패"}), 500
    
    try:
        old_file_path = None
        with conn.cursor() as cursor:
            if image_url:
                cursor.execute("SELECT profile_image_url FROM user_profiles WHERE user_id = %s", (user_id,))
                row = cursor.fetchone()
                if row and row['profile_image_url']:
                    old_file_path = row['profile_image_url'].lstrip('/')

                sql = "UPDATE user_profiles SET email=%s, phone_number=%s, bio=%s, profile_image_url=%s WHERE user_id=%s"
                cursor.execute(sql, (email, phone_number, bio, image_url, user_id))
            else:
                sql = "UPDATE user_profiles SET email=%s, phone_number=%s, bio=%s WHERE user_id=%s"
                cursor.execute(sql, (email, phone_number, bio, user_id))
        conn.commit()

        if old_file_path and os.path.exists(old_file_path):
            try:
                os.remove(old_file_path)
            except Exception as e:
                print(f"파일 삭제 실패: {e}")

        return jsonify({"status": "success"})
    
    except Exception as e:
        conn.rollback()
        return jsonify({"status": "error", "message": str(e)})
    finally:
        conn.close()


# --- [소개창 관리] ---
@app.route('/edit_sections')
def edit_sections_page():
    if 'user_id' not in session: return redirect(url_for('login_page'))
    conn = get_db_connection()
    if conn is None: return "DB 연결 실패", 500
    
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM profile_sections WHERE user_id = %s", (session['user_id'],))
            return render_template('edit_sections.html', sections=cursor.fetchall())
    finally:
        conn.close()

@app.route('/api/add_section', methods=['POST'])
def api_add_section():
    if 'user_id' not in session: return jsonify({"status": "error", "message": "로그인 필요"})
    data = request.get_json()
    conn = get_db_connection()
    if conn is None: return jsonify({"status": "error", "message": "DB 연결 실패"}), 500
    
    try:
        with conn.cursor() as cursor:
            sql = "INSERT INTO profile_sections (user_id, content) VALUES (%s, %s)"
            cursor.execute(sql, (session['user_id'], data['content']))
        conn.commit()
        return jsonify({"status": "success"})
    except Exception as e:
        conn.rollback()
        return jsonify({"status": "error", "message": str(e)})
    finally:
        conn.close()

@app.route('/api/delete_section/<int:section_id>', methods=['DELETE'])
def api_delete_section(section_id):
    if 'user_id' not in session: return jsonify({"status": "error", "message": "로그인 필요"})
    conn = get_db_connection()
    if conn is None: return jsonify({"status": "error", "message": "DB 연결 실패"}), 500
    
    try:
        with conn.cursor() as cursor:
            sql = "DELETE FROM profile_sections WHERE id = %s AND user_id = %s"
            cursor.execute(sql, (section_id, session['user_id']))
        conn.commit()
        return jsonify({"status": "success"})
    except Exception as e:
        conn.rollback()
        return jsonify({"status": "error", "message": str(e)})
    finally:
        conn.close()

if __name__ == '__main__':
    """ 디버깅 모드
    app.run(host='0.0.0.0', port=5000, debug=True)
    """
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=os.getenv('FLASK_DEBUG', 'False') == 'True'
    )