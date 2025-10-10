from app.setup_db import setup_database

if __name__ == '__main__':
    if setup_database():
        print("[DB] Initialization SUCCESS")
    else:
        print("[DB] Initialization FAILED")