import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os
from dotenv import load_dotenv
import sys

# Load current .env
load_dotenv()

def setup():
    print("--- CẤU HÌNH TỰ ĐỘNG DATABASE ---")
    
    # 1. Get credentials
    print(f"Đang đọc cấu hình từ .env:")
    user = os.getenv("POSTGRES_USER", "postgres")
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    dbname = os.getenv("POSTGRES_DB", "crypto_bot")
    password = os.getenv("POSTGRES_PASSWORD")

    print(f" - User: {user}")
    print(f" - Host: {host}")
    print(f" - Port: {port}")
    print(f" - Database cần tạo: {dbname}")
    
    if not password or password == "password":
        print("\n[!] CẢNH BÁO: Mật khẩu hiện tại là mặc định hoặc chưa điền.")
        new_pass = input("Nhập mật khẩu PostgreSQL của bạn (để trống nếu muốn giữ nguyên): ").strip()
        if new_pass:
            password = new_pass
            # Update .env file logic could go here, but for now let's just use it
    
    # 2. Connect to default 'postgres' database to create the new db
    print(f"\nĐang kết nối tới Postgres để kiểm tra...")
    try:
        conn = psycopg2.connect(
            user=user,
            password=password,
            host=host,
            port=port,
            dbname="postgres"
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
        
        # Check if db exists
        cur.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{dbname}'")
        exists = cur.fetchone()
        
        if not exists:
            print(f"Database '{dbname}' chưa tồn tại. Đang tạo...")
            cur.execute(f"CREATE DATABASE {dbname}")
            print(f"[OK] Đã tạo database '{dbname}' thành công!")
        else:
            print(f"[OK] Database '{dbname}' đã tồn tại.")
            
        cur.close()
        conn.close()
        
        # 3. Update .env file if password changed
        if password != os.getenv("POSTGRES_PASSWORD"):
            update_env_file("POSTGRES_PASSWORD", password)
            print("[OK] Đã cập nhật mật khẩu mới vào file .env")

        print("\n--- CÀI ĐẶT HOÀN TẤT ---")
        print("Bạn có thể chạy 'python main.py' ngay bây giờ.")
        
    except psycopg2.OperationalError as e:
        print("\n[LỖI KẾT NỐI] Không thể kết nối tới PostgreSQL.")
        print("Nguyên nhân có thể:")
        print("1. PostgreSQL chưa được cài đặt hoặc chưa chạy.")
        print("2. Sai mật khẩu (password).")
        print("3. Sai port (mặc định là 5432).")
        print(f"\nChi tiết lỗi: {e}")
        print("\nHƯỚNG DẪN KHẮC PHỤC:")
        print("1. Tải và cài đặt PostgreSQL tại: https://www.enterprisedb.com/downloads/postgres-postgresql-downloads")
        print("2. Khi cài đặt, hãy GHI NHỚ mật khẩu bạn đặt cho tài khoản 'postgres'.")
        print("3. Chạy lại script này và nhập đúng mật khẩu đó.")

def update_env_file(key, value):
    env_path = ".env"
    with open(env_path, "r") as f:
        lines = f.readlines()
    
    new_lines = []
    found = False
    for line in lines:
        if line.startswith(f"{key}="):
            new_lines.append(f"{key}={value}\n")
            found = True
        else:
            new_lines.append(line)
    
    if not found:
        new_lines.append(f"{key}={value}\n")
        
    with open(env_path, "w") as f:
        f.writelines(new_lines)

if __name__ == "__main__":
    setup()
