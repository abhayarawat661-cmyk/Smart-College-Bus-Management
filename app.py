from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import math
from datetime import datetime

app = Flask(__name__)

DATABASE = "bus_data.db"


# =========================================================
# DATABASE CREATE
# =========================================================

def create_database():

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # -----------------------------------------------------
    # Bus demand table
    # -----------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bus_demand (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            route TEXT NOT NULL,
            departure_time TEXT NOT NULL,
            students INTEGER NOT NULL,
            capacity INTEGER NOT NULL,
            required_buses INTEGER NOT NULL
        )
    """)

    # -----------------------------------------------------
    # Bus master table
    # -----------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bus_master (
            bus_id TEXT PRIMARY KEY,
            capacity INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'Available',
            current_route TEXT,
            current_time TEXT,
            current_students INTEGER,
            assigned_at TEXT
        )
    """)

    # -----------------------------------------------------
    # Bus assignment table
    # -----------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bus_assignments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            demand_id INTEGER NOT NULL,
            bus_id TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Running',
            assigned_at TEXT NOT NULL,
            returned_at TEXT
        )
    """)

    # -----------------------------------------------------
    # Add 15 buses if they don't already exist
    # -----------------------------------------------------

    for i in range(1, 16):

        bus_id = f"BUS-{i:02d}"

        cursor.execute("""
            INSERT OR IGNORE INTO bus_master
            (
                bus_id,
                capacity,
                status
            )
            VALUES (?, ?, ?)
        """,
        (
            bus_id,
            50,
            "Available"
        ))

    conn.commit()
    conn.close()


# =========================================================
# DASHBOARD
# =========================================================

@app.route("/", methods=["GET", "POST"])
def dashboard():

    result = None

    # =====================================================
    # FORM SUBMISSION
    # =====================================================

    if request.method == "POST":

        try:

            route = request.form["route"]

            departure_time = request.form["time"]

            students = int(request.form["students"])

            capacity = int(request.form["capacity"])

            # -------------------------------------------------
            # Validation
            # -------------------------------------------------

            if students <= 0:
                raise ValueError("Number of students must be greater than 0.")

            if capacity <= 0:
                capacity = 50

            # -------------------------------------------------
            # Calculate required buses
            # -------------------------------------------------

            required_buses = math.ceil(
                students / capacity
            )

            conn = sqlite3.connect(DATABASE)
            cursor = conn.cursor()

            # -------------------------------------------------
            # Save demand
            # -------------------------------------------------

            cursor.execute("""
                INSERT INTO bus_demand
                (
                    route,
                    departure_time,
                    students,
                    capacity,
                    required_buses
                )
                VALUES (?, ?, ?, ?, ?)
            """,
            (
                route,
                departure_time,
                students,
                capacity,
                required_buses
            ))

            demand_id = cursor.lastrowid

            # -------------------------------------------------
            # Find available buses
            # -------------------------------------------------

            cursor.execute("""
                SELECT bus_id
                FROM bus_master
                WHERE status = 'Available'
                ORDER BY bus_id
                LIMIT ?
            """,
            (required_buses,))

            available_buses = [
                row[0]
                for row in cursor.fetchall()
            ]

            # -------------------------------------------------
            # Assign buses
            # -------------------------------------------------

            assigned_buses = []

            current_time = datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )

            for bus_id in available_buses:

                cursor.execute("""
                    UPDATE bus_master
                    SET
                        status = 'Running',
                        current_route = ?,
                        current_time = ?,
                        current_students = ?,
                        assigned_at = ?
                    WHERE bus_id = ?
                """,
                (
                    route,
                    departure_time,
                    students,
                    current_time,
                    bus_id
                ))

                cursor.execute("""
                    INSERT INTO bus_assignments
                    (
                        demand_id,
                        bus_id,
                        status,
                        assigned_at
                    )
                    VALUES (?, ?, ?, ?)
                """,
                (
                    demand_id,
                    bus_id,
                    "Running",
                    current_time
                ))

                assigned_buses.append(bus_id)

            conn.commit()
            conn.close()

            # -------------------------------------------------
            # Result
            # -------------------------------------------------

            result = {
                "route": route,
                "time": departure_time,
                "students": students,
                "capacity": capacity,
                "buses": required_buses,
                "assigned_buses": assigned_buses,
                "available_count": len(assigned_buses)
            }

        except Exception as e:

            result = {
                "error": str(e)
            }

    # =====================================================
    # RECENT RECORDS
    # =====================================================

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            route,
            departure_time,
            students,
            capacity,
            required_buses
        FROM bus_demand
        ORDER BY id DESC
        LIMIT 10
    """)

    records = cursor.fetchall()

    # =====================================================
    # DASHBOARD STATISTICS
    # =====================================================

    cursor.execute("""
        SELECT COALESCE(SUM(students), 0)
        FROM bus_demand
    """)

    total_students = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM bus_demand
    """)

    total_trips = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COALESCE(SUM(required_buses), 0)
        FROM bus_demand
    """)

    total_buses_required = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(DISTINCT route)
        FROM bus_demand
    """)

    total_routes = cursor.fetchone()[0]

    # =====================================================
    # BUS STATUS
    # =====================================================

    cursor.execute("""
        SELECT COUNT(*)
        FROM bus_master
        WHERE status = 'Available'
    """)

    available_buses = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM bus_master
        WHERE status = 'Running'
    """)

    running_buses = cursor.fetchone()[0]

    # =====================================================
    # ALL BUS STATUS
    # =====================================================

    cursor.execute("""
        SELECT
            bus_id,
            capacity,
            status,
            current_route,
            current_time,
            current_students
        FROM bus_master
        ORDER BY bus_id
    """)

    bus_status = cursor.fetchall()

    conn.close()

    # =====================================================
    # ROUTE-WISE SUMMARY
    # =====================================================

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            route,
            SUM(students) AS total_students,
            SUM(required_buses) AS total_buses,
            COUNT(*) AS total_trips
        FROM bus_demand
        GROUP BY route
        ORDER BY route
    """)

    route_summary = cursor.fetchall()

    conn.close()

    # =====================================================
    # GRAPH DATA
    # =====================================================

    route_labels = []

    route_students = []

    route_buses = []

    for row in route_summary:

        route_labels.append(
            "Route " + str(row[0])
        )

        route_students.append(
            row[1]
        )

        route_buses.append(
            row[2]
        )

    # =====================================================
    # SEND DATA TO dashboard.html
    # =====================================================

    return render_template(

        "dashboard.html",

        result=result,

        records=records,

        total_students=total_students,

        total_trips=total_trips,

        total_buses_required=total_buses_required,

        total_routes=total_routes,

        available_buses=available_buses,

        running_buses=running_buses,

        bus_status=bus_status,

        route_summary=route_summary,

        route_labels=route_labels,

        route_students=route_students,

        route_buses=route_buses
    )


# =========================================================
# RETURN BUS
# =========================================================

@app.route("/return_bus/<bus_id>", methods=["POST"])
def return_bus(bus_id):

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # -----------------------------------------------------
    # Make bus available
    # -----------------------------------------------------

    cursor.execute("""
        UPDATE bus_master
        SET
            status = 'Available',
            current_route = NULL,
            current_time = NULL,
            current_students = NULL,
            assigned_at = NULL
        WHERE bus_id = ?
    """,
    (bus_id,))

    # -----------------------------------------------------
    # Update assignment
    # -----------------------------------------------------

    returned_time = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    cursor.execute("""
        UPDATE bus_assignments
        SET
            status = 'Returned',
            returned_at = ?
        WHERE bus_id = ?
        AND status = 'Running'
    """,
    (
        returned_time,
        bus_id
    ))

    conn.commit()
    conn.close()

    return redirect(url_for("dashboard"))


# =========================================================
# RETURN ALL RUNNING BUSES
# =========================================================

@app.route("/return_all", methods=["POST"])
def return_all():

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    returned_time = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    # -----------------------------------------------------
    # Return all buses
    # -----------------------------------------------------

    cursor.execute("""
        UPDATE bus_master
        SET
            status = 'Available',
            current_route = NULL,
            current_time = NULL,
            current_students = NULL,
            assigned_at = NULL
        WHERE status = 'Running'
    """)

    # -----------------------------------------------------
    # Update assignments
    # -----------------------------------------------------

    cursor.execute("""
        UPDATE bus_assignments
        SET
            status = 'Returned',
            returned_at = ?
        WHERE status = 'Running'
    """,
    (returned_time,))

    conn.commit()
    conn.close()

    return redirect(url_for("dashboard"))


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":

    create_database()

    app.run(
        debug=True
    )