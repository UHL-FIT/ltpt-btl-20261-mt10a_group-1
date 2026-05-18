"""
MODEL - Lớp dữ liệu
Chỉ biết về database. Không biết gì về giao diện (tkinter).
Nhiệm vụ: CRUD bệnh nhân + truy vấn thống kê.
"""
import sqlite3
import os
from datetime import datetime, date
from utils.helpers import remove_accents


class PatientModel:
    def __init__(self):
        # Luôn lưu DB cùng thư mục với file model này
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.db_path = os.path.join(base_dir, "..", "patients_data.db")
        self.db_name = self.db_path            
        self._init_database()

    # ------------------------------------------------------------------
    # Khởi tạo
    # ------------------------------------------------------------------
    def _init_database(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS patients (
                    id               INTEGER PRIMARY KEY AUTOINCREMENT,
                    name             TEXT NOT NULL,
                    age              INTEGER,
                    gender           TEXT,
                    phone            TEXT,
                    receive_time     TEXT,
                    primary_disease  TEXT,
                    secondary_disease TEXT,
                    history          TEXT
                )
            ''')
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
            conn.commit()

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------
    def add_patient(self, data: tuple) -> None:
        """Thêm một bệnh nhân mới. data là dict chứa các trường."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO patients
                    (name, age, gender, phone, receive_time,
                     primary_disease, secondary_disease, history)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', data)
            conn.commit()

    def delete_patient(self, patient_id: int) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("PRAGMA foreign_keys = ON")            
            conn.execute("DELETE FROM patients WHERE id = ?", (patient_id,))
            conn.commit()

    def update_patient(self, patient_id: int, data: tuple) -> None:
        """Hàm dùng để cập nhật thông tin bệnh nhân (Tính năng Sửa)"""
        with sqlite3.connect(self.db_path) as conn:
            # data là tuple: (name, age, gender, phone, receive_time, primary_disease, secondary_disease, history, patient_id)
            conn.execute('''
                UPDATE patients 
                SET name=?, age=?, gender=?, phone=?, receive_time=?, 
                    primary_disease=?, secondary_disease=?, history=?
                WHERE id=?
            ''', data)
            conn.commit()

    def get_patient_by_id(self, patient_id: int) -> tuple | None:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT * FROM patients WHERE id = ?", (patient_id,))
            return cursor.fetchone()

    def search_patients(self, query: str = "") -> list[tuple]:
        """Trả về danh sách bệnh nhân, lọc theo tên/SĐT nếu có query."""
        with sqlite3.connect(self.db_path) as conn:
            conn.create_function("REMOVE_ACCENTS", 1, remove_accents)
            if query.strip():
                clean = remove_accents(query.strip())
                rows = conn.execute('''
                    SELECT id, name, age, gender, receive_time, primary_disease, secondary_disease
                    FROM patients
                    WHERE REMOVE_ACCENTS(name) LIKE ? OR phone LIKE ?
                    ORDER BY id DESC
                ''', (f"%{clean}%", f"%{query.strip()}%")).fetchall()
            else:
                rows = conn.execute('''
                    SELECT id, name, age, gender, receive_time, primary_disease, secondary_disease
                    FROM patients ORDER BY id DESC
                ''').fetchall()
        return rows

    def export_all(self) -> list[tuple]:
        """Trả về toàn bộ dữ liệu (bỏ id) để xuất CSV."""
        with sqlite3.connect(self.db_path) as conn:
            return conn.execute('''
                SELECT name, age, gender, phone, receive_time,
                       primary_disease, secondary_disease, history
                FROM patients ORDER BY id DESC
            ''').fetchall()

    # ------------------------------------------------------------------
    # Thống kê
    # ------------------------------------------------------------------
    def get_statistics(self, today_str: str) -> dict:
        """
        Trả về dict chứa toàn bộ số liệu thống kê.
        today_str: chuỗi ngày dạng 'YYYY-MM-DD'
        """
        with sqlite3.connect(self.db_path) as conn:
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

        return {
            "total": total,
            "today": today,
            "gender_data": gender_data,
            "disease_data": disease_data,
        }

    # ------------------------------------------------------------------
    # CRUD – Lịch Tái Khám
    # ------------------------------------------------------------------
    def add_follow_up(self, patient_id: int, appointment_date: str,
                      reason: str, frequency: str) -> None:
        """Thêm lịch tái khám mới."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO follow_up_appointments
                    (patient_id, appointment_date, reason, frequency)
                VALUES (?, ?, ?, ?)
            ''', (patient_id, appointment_date, reason, frequency))
            conn.commit()
 
    def delete_follow_up(self, follow_up_id: int) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM follow_up_appointments WHERE id = ?", (follow_up_id,))
            conn.commit()
 
    def get_follow_ups(self, search: str = "") -> list[tuple]:
        """
        Trả về danh sách lịch tái khám, join với bảng patients.
        Mỗi row: (fu_id, patient_id, name, phone, appointment_date,
                  reason, frequency, days_remaining)
        """
        with sqlite3.connect(self.db_path) as conn:
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
                    ORDER BY f.appointment_date ASC
                ''', (f"%{clean}%", f"%{search.strip()}%",
                      f"%{search.strip()}%")).fetchall()
            else:
                rows = conn.execute('''
                    SELECT f.id, f.patient_id, p.name, p.phone,
                           f.appointment_date, f.reason, f.frequency
                    FROM follow_up_appointments f
                    JOIN patients p ON p.id = f.patient_id
                    ORDER BY f.appointment_date ASC
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
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT name FROM patients WHERE id = ?", (patient_id,)
            ).fetchone()
        return row[0] if row else None
 
    def get_follow_up_stats(self) -> dict:
        """Thống kê tóm tắt cho dashboard lịch tái khám."""
        today_str = date.today().isoformat()
        with sqlite3.connect(self.db_path) as conn:
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