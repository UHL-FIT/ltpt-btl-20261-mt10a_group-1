"""
MODEL - Lớp dữ liệu
Chỉ biết về database. Không biết gì về giao diện (tkinter).
Nhiệm vụ: CRUD bệnh nhân + truy vấn thống kê.
"""
import sqlite3
import os
from datetime import datetime, date
from contextlib import contextmanager
from utils.helpers import remove_accents


class PatientModel:
    @contextmanager
    def _db_conn(self):
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
        finally:
            conn.close()
    def __init__(self):
        import sys
        # Nếu chạy dạng file đóng gói (executable), lưu DB cùng thư mục với file .exe
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
            self.db_path = os.path.join(base_dir, "patients_data.db")
        else:
            # Nếu chạy dạng script python, lưu DB ở thư mục gốc của project
            base_dir = os.path.dirname(os.path.abspath(__file__))
            self.db_path = os.path.join(base_dir, "..", "patients_data.db")
        self.db_name = self.db_path            
        self._init_database()

    # ------------------------------------------------------------------
    # Khởi tạo
    # ------------------------------------------------------------------
    def _init_database(self):
        with self._db_conn() as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS patients (
                    id               INTEGER PRIMARY KEY AUTOINCREMENT,
                    name             TEXT NOT NULL,
                    age              INTEGER,
                    gender           TEXT,
                    phone            TEXT,
                    receive_time     TEXT,
                    primary_disease  TEXT,
                    history          TEXT,
                    height           REAL,
                    weight           REAL
                )
            ''')
            # Migration an toàn cho DB cũ
            for col, col_type in [("height", "REAL"), ("weight", "REAL")]:
                try:
                    conn.execute(f"ALTER TABLE patients ADD COLUMN {col} {col_type}")
                except Exception:
                    pass
            conn.execute('''
                CREATE TABLE IF NOT EXISTS follow_up_appointments (
                    id               INTEGER PRIMARY KEY AUTOINCREMENT,
                    patient_id       INTEGER NOT NULL,
                    appointment_date TEXT NOT NULL,
                    reason           TEXT,
                    frequency        TEXT,
                    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE
                )
            ''')
            # Indexes để tăng tốc truy vấn
            conn.execute('CREATE INDEX IF NOT EXISTS idx_patients_name ON patients(name)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_patients_phone ON patients(phone)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_patients_receive_time ON patients(receive_time)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_patients_primary_disease ON patients(primary_disease)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_followup_patient_id ON follow_up_appointments(patient_id)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_followup_appt_date ON follow_up_appointments(appointment_date)')
            conn.commit()

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------
    def add_patient(self, data: tuple) -> None:
        """Thêm một bệnh nhân mới. data là tuple chứa các trường."""
        with self._db_conn() as conn:
            conn.execute('''
                INSERT INTO patients
                    (name, age, gender, phone, receive_time,
                     primary_disease, history, height, weight)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', data)
    def add_patients_batch(self, batch: list[tuple]) -> None:
        """Thêm nhiều bệnh nhân cùng lúc kèm theo lịch tái khám. batch = [(patient_data, fu_str), ...]"""
        with self._db_conn() as conn:
            for patient_data, fu_str in batch:
                cursor = conn.execute('''
                    INSERT INTO patients
                        (name, age, gender, phone, receive_time,
                         primary_disease, history, height, weight)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', patient_data)
                
                if fu_str:
                    patient_id = cursor.lastrowid
                    fu_items = fu_str.split(";")
                    fu_batch = []
                    for item in fu_items:
                        parts = item.split("|")
                        if len(parts) >= 3:
                            fu_batch.append((patient_id, parts[0], parts[1], parts[2]))
                    if fu_batch:
                        conn.executemany('''
                            INSERT INTO follow_up_appointments
                                (patient_id, appointment_date, reason, frequency)
                            VALUES (?, ?, ?, ?)
                        ''', fu_batch)
            conn.commit()

    def delete_patient(self, patient_id: int) -> None:
        with self._db_conn() as conn:
            conn.execute("PRAGMA foreign_keys = ON")            
            conn.execute("DELETE FROM patients WHERE id = ?", (patient_id,))
            conn.commit()

    def update_patient(self, patient_id: int, data: tuple) -> None:
        """Hàm dùng để cập nhật thông tin bệnh nhân (Tính năng Sửa)"""
        with self._db_conn() as conn:
            # data là tuple: (name, age, gender, phone, receive_time, primary_disease, history, height, weight, patient_id)
            conn.execute('''
                UPDATE patients 
                SET name=?, age=?, gender=?, phone=?, receive_time=?, 
                    primary_disease=?, history=?, height=?, weight=?
                WHERE id=?
            ''', data)
            conn.commit()

    def get_patient_by_id(self, patient_id: int) -> tuple | None:
        with self._db_conn() as conn:
            cursor = conn.execute("SELECT * FROM patients WHERE id = ?", (patient_id,))
            return cursor.fetchone()

    def search_patients(self, query: str = "") -> list[tuple]:
        """Trả về danh sách bệnh nhân, lọc theo tên/SĐT nếu có query."""
        with self._db_conn() as conn:
            conn.create_function("REMOVE_ACCENTS", 1, remove_accents)
            if query.strip():
                clean = remove_accents(query.strip())
                rows = conn.execute('''
                    SELECT id, name, age, gender, receive_time, primary_disease, height, weight
                    FROM patients
                    WHERE REMOVE_ACCENTS(name) LIKE ? OR phone LIKE ?
                    ORDER BY id DESC LIMIT 1000
                ''', (f"%{clean}%", f"%{query.strip()}%")).fetchall()
            else:
                rows = conn.execute('''
                    SELECT id, name, age, gender, receive_time, primary_disease, height, weight
                    FROM patients ORDER BY id DESC LIMIT 1000
                ''').fetchall()
        return rows

    def export_all(self) -> list[tuple]:
        """Trả về toàn bộ dữ liệu (bỏ id) kèm theo lịch tái khám để xuất CSV."""
        with self._db_conn() as conn:
            patients = conn.execute('''
                SELECT id, name, age, gender, phone, receive_time,
                       primary_disease, history, height, weight
                FROM patients ORDER BY id DESC
            ''').fetchall()

            followups = conn.execute('''
                SELECT patient_id, appointment_date, reason, frequency
                FROM follow_up_appointments
            ''').fetchall()

            from collections import defaultdict
            fu_dict = defaultdict(list)
            for fu in followups:
                pid, date, reason, freq = fu
                safe_reason = str(reason).replace("|", ",").replace(";", ",") if reason else ""
                safe_freq = str(freq).replace("|", ",").replace(";", ",") if freq else ""
                fu_dict[pid].append(f"{date}|{safe_reason}|{safe_freq}")

            result = []
            for p in patients:
                pid = p[0]
                fu_str = ";".join(fu_dict[pid]) if pid in fu_dict else ""
                result.append(p[1:] + (fu_str,))
            return result

    # ------------------------------------------------------------------
    # Thống kê
    # ------------------------------------------------------------------
    def get_statistics(self, today_str: str) -> dict:
        """
        Trả về dict chứa toàn bộ số liệu thống kê.
        today_str: chuỗi ngày dạng 'YYYY-MM-DD'
        """
        with self._db_conn() as conn:
            total = conn.execute("SELECT COUNT(*) FROM patients").fetchone()[0]

            today = conn.execute(
                "SELECT COUNT(*) FROM patients WHERE receive_time LIKE ?",
                (f"{today_str}%",)
            ).fetchone()[0]

            gender_data = conn.execute(
                "SELECT gender, COUNT(*) FROM patients GROUP BY gender"
            ).fetchall()

            disease_data = conn.execute('''
                SELECT primary_disease, COUNT(*) FROM patients
                WHERE primary_disease != ''
                GROUP BY primary_disease
                ORDER BY COUNT(*) DESC LIMIT 5
            ''').fetchall()

            # Dữ liệu BMI – chỉ lấy những bệnh nhân có đủ chiều cao & cân nặng
            bmi_rows = conn.execute('''
                SELECT name, height, weight
                FROM patients
                WHERE height IS NOT NULL AND weight IS NOT NULL
                  AND height > 0 AND weight > 0
            ''').fetchall()

        # Phân loại BMI
        bmi_categories = {"Thiếu cân": 0, "Bình thường": 0,
                          "Thừa cân": 0, "Béo phì": 0}
        bmi_list = []
        for name, h, w in bmi_rows:
            bmi = w / ((h / 100) ** 2)
            bmi_list.append((name, round(bmi, 1)))
            if bmi < 18.5:
                bmi_categories["Thiếu cân"] += 1
            elif bmi < 25:
                bmi_categories["Bình thường"] += 1
            elif bmi < 30:
                bmi_categories["Thừa cân"] += 1
            else:
                bmi_categories["Béo phì"] += 1

        with self._db_conn() as conn2:
            monthly_patients = conn2.execute('''
                SELECT strftime('%Y-%m', receive_time) AS month, COUNT(*) AS cnt
                FROM patients
                WHERE receive_time IS NOT NULL AND receive_time != ''
                GROUP BY month
                ORDER BY month ASC
            ''').fetchall()

            monthly_followups = conn2.execute('''
                SELECT strftime('%Y-%m', appointment_date) AS month, COUNT(*) AS cnt
                FROM follow_up_appointments
                WHERE appointment_date IS NOT NULL AND appointment_date != ''
                GROUP BY month
                ORDER BY month ASC
            ''').fetchall()

            # Top 10 bệnh chính kèm số Nam / Nữ
            disease_gender_raw = conn2.execute('''
                SELECT primary_disease, gender, COUNT(*) AS cnt
                FROM patients
                WHERE primary_disease IS NOT NULL AND primary_disease != ''
                GROUP BY primary_disease, gender
            ''').fetchall()

        # Tổng hợp top 10 bệnh kèm giới tính
        from collections import defaultdict
        disease_agg: dict = defaultdict(lambda: {"Nam": 0, "Nữ": 0, "Khác": 0, "total": 0})
        for disease, gender, cnt in disease_gender_raw:
            g = gender if gender in ("Nam", "Nữ") else "Khác"
            disease_agg[disease][g] += cnt
            disease_agg[disease]["total"] += cnt
        disease_gender_data = sorted(
            [(d, v["total"], v["Nam"], v["Nữ"], v["Khác"])
             for d, v in disease_agg.items()],
            key=lambda x: x[1], reverse=True
        )[:10]

        return {
            "total": total,
            "today": today,
            "gender_data": gender_data,
            "disease_data": disease_data,
            "bmi_list": bmi_list,
            "bmi_categories": bmi_categories,
            "monthly_patients": monthly_patients,
            "monthly_followups": monthly_followups,
            "disease_gender_data": disease_gender_data,
        }

    # ------------------------------------------------------------------
    # CRUD – Lịch Tái Khám
    # ------------------------------------------------------------------
    def add_follow_up(self, patient_id: int, appointment_date: str,
                      reason: str, frequency: str) -> None:
        """Thêm lịch tái khám mới."""
        with self._db_conn() as conn:
            conn.execute('''
                INSERT INTO follow_up_appointments
                    (patient_id, appointment_date, reason, frequency)
                VALUES (?, ?, ?, ?)
            ''', (patient_id, appointment_date, reason, frequency))
            conn.commit()
 
    def delete_follow_up(self, follow_up_id: int) -> None:
        with self._db_conn() as conn:
            conn.execute("DELETE FROM follow_up_appointments WHERE id = ?", (follow_up_id,))
            conn.commit()
 
    def get_follow_ups(self, search: str = "") -> list[tuple]:
        """
        Trả về danh sách lịch tái khám, join với bảng patients.
        Mỗi row: (fu_id, patient_id, name, phone, appointment_date,
                  reason, frequency, days_remaining)
        """
        with self._db_conn() as conn:
            conn.create_function("REMOVE_ACCENTS", 1, remove_accents)
            if search.strip():
                clean = remove_accents(search.strip())
                rows = conn.execute('''
                    SELECT f.id, f.patient_id, p.name, p.phone,
                           f.appointment_date, f.reason, f.frequency
                    FROM follow_up_appointments f
                    JOIN patients p ON p.id = f.patient_id
                    WHERE REMOVE_ACCENTS(p.name) LIKE ?
                       OR p.phone LIKE ?
                       OR CAST(f.patient_id AS TEXT) LIKE ?
                    ORDER BY f.appointment_date ASC LIMIT 1000
                ''', (f"%{clean}%", f"%{search.strip()}%",
                      f"%{search.strip()}%")).fetchall()
            else:
                rows = conn.execute('''
                    SELECT f.id, f.patient_id, p.name, p.phone,
                           f.appointment_date, f.reason, f.frequency
                    FROM follow_up_appointments f
                    JOIN patients p ON p.id = f.patient_id
                    ORDER BY f.appointment_date ASC LIMIT 1000
                ''').fetchall()
 
        today = date.today()
        result = []
        for row in rows:
            try:
                appt_date = datetime.strptime(row[4], "%Y-%m-%d").date()
                days_remaining = (appt_date - today).days
            except (ValueError, TypeError):
                days_remaining = 0
            result.append(row + (days_remaining,))
        return result
 
    def get_patient_name_by_id(self, patient_id: int) -> str | None:
        """Tra cứu nhanh tên bệnh nhân theo ID."""
        with self._db_conn() as conn:
            row = conn.execute(
                "SELECT name FROM patients WHERE id = ?", (patient_id,)
            ).fetchone()
        return row[0] if row else None

    def get_follow_up_by_id(self, follow_up_id: int) -> tuple | None:
        """Lấy chi tiết một lịch tái khám theo ID (join với patients)."""
        with self._db_conn() as conn:
            row = conn.execute('''
                SELECT f.id, f.patient_id, p.name, p.phone,
                       f.appointment_date, f.reason, f.frequency
                FROM follow_up_appointments f
                JOIN patients p ON p.id = f.patient_id
                WHERE f.id = ?
            ''', (follow_up_id,)).fetchone()
        return row
 
    def get_follow_up_stats(self) -> dict:
        """Thống kê tóm tắt cho dashboard lịch tái khám."""
        today_str = date.today().isoformat()
        with self._db_conn() as conn:
            total = conn.execute(
                "SELECT COUNT(*) FROM follow_up_appointments"
            ).fetchone()[0]
            today_count = conn.execute(
                "SELECT COUNT(*) FROM follow_up_appointments WHERE appointment_date = ?",
                (today_str,)
            ).fetchone()[0]
            overdue = conn.execute(
                "SELECT COUNT(*) FROM follow_up_appointments WHERE appointment_date < ?",
                (today_str,)
            ).fetchone()[0]
            upcoming = conn.execute(
                "SELECT COUNT(*) FROM follow_up_appointments WHERE appointment_date > ?",
                (today_str,)
            ).fetchone()[0]
        return {
            "total": total,
            "today": today_count,
            "overdue": overdue,
            "upcoming": upcoming,
        }

    def get_patient_summary_stats(self) -> dict:
        """
        Thống kê tổng hợp bệnh nhân: Tổng số bệnh nhân (nam/nữ), trung bình tuổi, tỉ lệ tái khám.
        """
        with self._db_conn() as conn:
            total = conn.execute("SELECT COUNT(*) FROM patients").fetchone()[0]
            male = conn.execute(
                "SELECT COUNT(*) FROM patients WHERE gender = 'Nam'"
            ).fetchone()[0]
            female = conn.execute(
                "SELECT COUNT(*) FROM patients WHERE gender = 'Nữ'"
            ).fetchone()[0]
            avg_age_row = conn.execute(
                "SELECT AVG(CAST(age AS REAL)) FROM patients WHERE age IS NOT NULL AND age != ''"
            ).fetchone()
            avg_age = round(avg_age_row[0], 1) if avg_age_row[0] is not None else 0

            # Số bệnh nhân có ít nhất 1 lịch tái khám
            patients_with_followup = conn.execute('''
                SELECT COUNT(DISTINCT patient_id) FROM follow_up_appointments
            ''').fetchone()[0]

        followup_rate = round(patients_with_followup / total * 100, 1) if total > 0 else 0

        return {
            "total": total,
            "male": male,
            "female": female,
            "avg_age": avg_age,
            "followup_rate": followup_rate,
            "patients_with_followup": patients_with_followup,
        }