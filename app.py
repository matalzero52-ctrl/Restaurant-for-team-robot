import os
import psycopg2
import psycopg2.extras
from flask import Flask, render_template, request, redirect
from datetime import datetime
from dotenv import load_dotenv

app = Flask(__name__)
load_dotenv()

# ตำแหน่งฐานข้อมูล
DATABASE_URL = os.getenv("DATABASE_URL")

# ฟังก์ชันเชื่อมฐานข้อมูล
def get_db_connection():
    return psycopg2.connect(
        DATABASE_URL,
        cursor_factory=psycopg2.extras.RealDictCursor
    )

# สร้างฐานข้อมูล
def init_db():
    
    print("===== init_db START =====")

    conn = get_db_connection()
    cursor = conn.cursor()

    print("Connected to PostgreSQL")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS restaurants (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            province TEXT NOT NULL,
            industrial_estate TEXT NOT NULL,
            google_map TEXT,
            created_by TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    print("restaurants OK")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS provinces (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL UNIQUE
        )
    """)
    print("provinces OK")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS industrial_estates (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            province_id INTEGER,
            UNIQUE(name, province_id),
            FOREIGN KEY(province_id)
            REFERENCES provinces(id)
        )
    """)
    print("industrial_estates OK")


    # ตารางร้านอาหาร
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS restaurants (
        id SERIAL PRIMARY KEY,
        name TEXT NOT NULL,
        province TEXT NOT NULL,
        industrial_estate TEXT NOT NULL,
        google_map TEXT,
        created_by TEXT NOT NULL,
        created_at TEXT NOT NULL
    )
    """)


    # ตารางจังหวัด
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS provinces (
        id SERIAL PRIMARY KEY,
        name TEXT NOT NULL UNIQUE
    )
    """)

    # ตารางนิคม
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS industrial_estates (
        id SERIAL PRIMARY KEY,
        name TEXT NOT NULL,
        province_id INTEGER,
        UNIQUE(name, province_id),
        FOREIGN KEY(province_id)
        REFERENCES provinces(id)
    )
    """)

    # เพิ่มข้อมูลจังหวัดเริ่มต้น
    provinces = [
        "กรุงเทพมหานคร",
        "ชลบุรี",
        "ระยอง",
        "อยุธยา",
        "ฉะเชิงเทรา",
        "นครราชสีมา",
        "สมุทรปราการ",
        "สมุทรสาคร",
        "นครปฐม",
        "ราชบุรี",
        "ปทุมธานี",
        "ลพบุรี",
        "ปราจีนบุรี",
        "สระบุรี"
    ]


    for province in provinces:

        cursor.execute(
            """
            INSERT INTO provinces(name)
            VALUES (%s)
            ON CONFLICT(name) DO NOTHING
            """,
            (province,)
            )


    # เพิ่มข้อมูลนิคมเริ่มต้น
    industrial_estates = [
        ("Hi-tech" ,"ปราจีนบุรี"),
        ("บ่อทอง" ,"ปราจีนบุรี"),
        ("304" ,"ปราจีนบุรี"),
        ("Well grow" ,"ฉะเชิงเทรา"),
        ("Gateway" ,"ฉะเชิงเทรา"),
        ("มาบตาพุด" ,"ระยอง"),
        ("Eastern seaboard" ,"ระยอง"),
        ("Amata City#2" ,"ระยอง"),
        ("Asia" ,"ระยอง"),
        ("ปิ่นทอง" ,"ระยอง"),
        ("แหลมฉบัง" ,"ชลบุรี"),
        ("Amata City#1" ,"ชลบุรี"),
        ("ปิ่นทอง" ,"ชลบุรี"),
        ("บ้านบึง" ,"ชลบุรี"),
        ("โรจนะ" ,"ชลบุรี"),
        ("บางปู" ,"สมุทรปราการ"),
        ("บางพลี" ,"สมุทรปราการ"),
        ("เอเชีย" ,"สมุทรปราการ"),
        ("บางชัน" ,"กรุงเทพมหานคร"),
        ("ลาดกระบัง" ,"กรุงเทพมหานคร"),
        ("สมุทรสาคร" ,"สมุทรสาคร"),
        ("สินสาคร" ,"สมุทรสาคร"),
        ("มหาราชนคร" ,"สมุทรสาคร"),
        ("บ้านหว้า" ,"อยุธยา"),
        ("บางปะอิน" ,"อยุธยา"),
        ("นครหลวง" ,"อยุธยา"),
        ("Hi-tech" ,"อยุธยา"),
        ("แก่งคอย" ,"สระบุรี"),
        ("หนองแค" ,"สระบุรี"),
        ("ปทุมธานี" ,"ปทุมธานี"),
        ("ลพบุรี" ,"ลพบุรี"),
        ("นครปฐม" ,"นครปฐม"),
        ("ราชบุรี" ,"ราชบุรี"),
        ("นวนคร" ,"นครราชสีมา"),
        ("Suranaree" ,"นครราชสีมา")
    ]


    for estate, province in industrial_estates:

        cursor.execute(
        """
        SELECT id
        FROM provinces
        WHERE name = %s
        """,
        (province,)
        )
        province_data = cursor.fetchone()


        cursor.execute(
            """
            INSERT INTO industrial_estates
            (
                name,
                province_id
            )
            VALUES (%s,%s)
            ON CONFLICT(name, province_id) DO NOTHING
            """,
            (
                estate,
                province_data["id"] if province_data else None
            )
            )
    conn.commit()
    print("===== init_db FINISH =====")
    conn.close()


@app.route("/")
def home():
    conn = get_db_connection()

    # รับค่าจากช่องค้นหา
    name = request.args.get("name", "")
    province = request.args.get("province", "")
    industrial_estate = request.args.get("industrial_estate", "")

    sql = "SELECT * FROM restaurants WHERE 1=1"
    params = []

    # ค้นหาชื่อร้าน
    if name:
        sql += " AND name ILIKE %s"
        params.append(f"%{name}%")

    # ค้นหาจังหวัด
    if province:
        sql += " AND province ILIKE %s"
        params.append(f"%{province}%")

    # ค้นหานิคม
    if industrial_estate:
        sql += " AND industrial_estate ILIKE %s"
        params.append(f"%{industrial_estate}%")

    sql += " ORDER BY id DESC"

    cursor = conn.cursor()
    cursor.execute(sql, params)
    restaurants = cursor.fetchall()


    # ดึงข้อมูลสำหรับ dropdown จังหวัด
    cursor.execute(
        """
        SELECT name
        FROM provinces
        ORDER BY name
        """
        )
    provinces = cursor.fetchall()

    # ดึงข้อมูลสำหรับ dropdown นิคม
    cursor.execute("""
        SELECT
        industrial_estates.name,
        provinces.name AS province
    FROM industrial_estates
    LEFT JOIN provinces
    ON industrial_estates.province_id = provinces.id
    ORDER BY provinces.name, industrial_estates.name
    """)

    industrial_estates = cursor.fetchall()

    conn.close()
    return render_template(
        "index.html",
        restaurants=restaurants,
        name=name,
        province=province,
        industrial_estate=industrial_estate,
        provinces=provinces,
        industrial_estates=industrial_estates
    )

@app.route("/add", methods=["GET", "POST"])
def add_restaurant():

    conn = get_db_connection()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT name
        FROM provinces
        ORDER BY name
    """)
    provinces = cursor.fetchall()

    cursor.execute("""
        SELECT
            industrial_estates.name,
            provinces.name AS province
            FROM industrial_estates
            LEFT JOIN provinces
            ON industrial_estates.province_id = provinces.id
            ORDER BY provinces.name, industrial_estates.name
            """)
        
    industrial_estates = cursor.fetchall()

    if request.method == "POST":

        name = request.form["name"]
        province = request.form["province"]
        industrial_estate = request.form["industrial_estate"]
        if not province or not industrial_estate:
            conn.close()
            return "กรุณาเลือกจังหวัดและนิคม"
        google_map = request.form["google_map"]
        created_by = request.form["created_by"]

        created_at = datetime.now().strftime("%d/%m/%Y %H:%M")

        cursor = conn.cursor()

        try:

            cursor.execute("""
                INSERT INTO restaurants
                (
                    name,
                    province,
                    industrial_estate,
                    google_map,
                    created_by,
                    created_at
                )
                VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
            name,
            province,
            industrial_estate,
            google_map,
            created_by,
            created_at
            ))

            conn.commit()
        except Exception as e:
            conn.rollback()
            conn.close()
            return f"Error: {e}"

        finally:
            if conn:
                conn.close()

        return redirect("/")

    return render_template(
    "add.html",
    provinces=provinces,
    industrial_estates=industrial_estates
)
@app.route("/delete/<int:id>")
def delete_restaurant(id):

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM restaurants WHERE id = %s",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect("/")

@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_restaurant(id):

    conn = get_db_connection()


    # ดึงข้อมูลร้านเดิม
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM restaurants WHERE id = %s",
        (id,)
        )
    restaurant = cursor.fetchone()

    if restaurant is None:
            conn.close()
            return "ไม่พบร้านอาหาร"
    cursor.execute("""
    SELECT name
    FROM provinces
    ORDER BY name
    """)
    provinces = cursor.fetchall()

    cursor.execute("""
        SELECT
            industrial_estates.name,
            provinces.name AS province
        FROM industrial_estates
        LEFT JOIN provinces
        ON industrial_estates.province_id = provinces.id
        ORDER BY provinces.name, industrial_estates.name
        """)
    industrial_estates = cursor.fetchall()

    if request.method == "POST":

        name = request.form["name"]
        province = request.form["province"]
        industrial_estate = request.form["industrial_estate"]
        google_map = request.form["google_map"]
        created_by = request.form["created_by"]


        cursor.execute("""
            UPDATE restaurants SET
            name = %s,
            province = %s,
            industrial_estate = %s,
            google_map = %s,
            created_by = %s

        WHERE id = %s

        """,
        (
            name,
            province,
            industrial_estate,
            google_map,
            created_by,
            id
        ))
        conn.commit()
        conn.close()
        return redirect("/")
    conn.close()

    return render_template(
        "edit.html",
        restaurant=restaurant,
        provinces=provinces,
        industrial_estates=industrial_estates
    )

init_db()

if __name__ == "__main__":



    app.run(
        host="0.0.0.0",
        port=5000
        )