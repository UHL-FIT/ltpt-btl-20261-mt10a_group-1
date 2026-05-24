import sqlite3
import random
from datetime import datetime, timedelta
from faker import Faker

# Khởi tạo Faker với ngôn ngữ tiếng Việt
fake = Faker('vi_VN')

# Tên file database đầu ra
DB_FILE = 'patients_data.db'

# Các danh sách dữ liệu mẫu để random
DISEASES = [
    "Viêm họng hạt", "Đau dạ dày", "Cao huyết áp", "Tiểu đường type 2", 
    "Rối loạn tiền đình", "Viêm phổi", "Thoái hóa cột sống", "Sỏi thận", 
    "Viêm xoang", "Sốt xuất huyết", "Thiếu máu", "Đau nửa đầu", "Viêm gan B"
]

FREQUENCIES = ["1 tuần", "2 tuần", "1 tháng", "3 tháng", "6 tháng", "Không"]

def create_tables(cursor):
    """Tạo bảng patients và follow_up_appointments giống với schema gốc"""
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER,
            gender TEXT,
            phone TEXT,
            receive_time TEXT,
            primary_disease TEXT,
            secondary_disease TEXT,
            history TEXT,
            height REAL,
            weight REAL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS follow_up_appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            appointment_date TEXT NOT NULL,
            reason TEXT,
            frequency TEXT,
            FOREIGN KEY(patient_id) REFERENCES patients(id)
        )
    ''')

def generate_fake_data(num_patients=100):
    # Kết nối tới database (nếu chưa có sẽ tự tạo mới)
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Tạo bảng
    create_tables(cursor)

    # Xóa dữ liệu cũ (nếu có) để tránh trùng lặp khi chạy lại
    cursor.execute("DELETE FROM follow_up_appointments")
    cursor.execute("DELETE FROM patients")
    
    patients_data = []
    
    print(f"Đang tạo dữ liệu cho {num_patients} bệnh nhân...")
    
    for _ in range(num_patients):
        gender = random.choice(["Nam", "Nữ"])
        
        # Tạo tên theo giới tính
        if gender == "Nam":
            name = fake.name_male()
        else:
            name = fake.name_female()
            
        age = random.randint(5, 85)
        phone = fake.phone_number()
        
        # Thời gian tiếp nhận: random trong vòng 2 năm qua
        days_ago = random.randint(0, 730)
        receive_time = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d %H:%M:%S')
        
        primary_disease = random.choice(DISEASES)
        secondary_disease = random.choice(DISEASES + ["Không có", "Không có", "Không có"])
        if primary_disease == secondary_disease:
            secondary_disease = "Không có"
            
        history = fake.text(max_nb_chars=100)
        
        # Chiều cao (cm) và Cân nặng (kg) phù hợp với độ tuổi
        if age < 15:
            height = round(random.uniform(100.0, 160.0), 1)
            weight = round(random.uniform(20.0, 50.0), 1)
        else:
            height = round(random.uniform(150.0, 185.0), 1)
            weight = round(random.uniform(45.0, 90.0), 1)

        patients_data.append((
            name, age, gender, phone, receive_time, 
            primary_disease, secondary_disease, history, height, weight
        ))

    # Chèn dữ liệu bệnh nhân
    cursor.executemany('''
        INSERT INTO patients (
            name, age, gender, phone, receive_time, 
            primary_disease, secondary_disease, history, height, weight
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', patients_data)

    # Random tạo lịch tái khám cho khoảng 30% bệnh nhân
    cursor.execute("SELECT id FROM patients")
    patient_ids = [row[0] for row in cursor.fetchall()]
    
    appointments_data = []
    for pid in patient_ids:
        if random.random() < 0.3: # 30% tỷ lệ có lịch tái khám
            days_ahead = random.randint(1, 90)
            appointment_date = (datetime.now() + timedelta(days=days_ahead)).strftime('%Y-%m-%d')
            reason = f"Tái khám {random.choice(DISEASES).lower()}"
            frequency = random.choice(FREQUENCIES)
            appointments_data.append((pid, appointment_date, reason, frequency))
            
    cursor.executemany('''
        INSERT INTO follow_up_appointments (
            patient_id, appointment_date, reason, frequency
        ) VALUES (?, ?, ?, ?)
    ''', appointments_data)

    # Lưu thay đổi và đóng kết nối
    conn.commit()
    conn.close()
    
    print(f"✅ Đã tạo thành công {num_patients} bệnh nhân và {len(appointments_data)} lịch tái khám.")
    print(f"📂 File database được lưu tại: {DB_FILE}")

if __name__ == "__main__":
    generate_fake_data(100)