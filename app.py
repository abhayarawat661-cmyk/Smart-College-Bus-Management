from flask import Flask, render_template, request
import sqlite3
import math

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
            # Prevent invalid capacity
            # -------------------------------------------------

            if capacity <= 0:
                capacity = 50

            # -------------------------------------------------
            # Calculate required buses
            # -------------------------------------------------

            required_buses = math.ceil(
                students / capacity
            )

            # -------------------------------------------------
            # Save data into SQLite
            # -------------------------------------------------

            conn = sqlite3.connect(DATABASE)

            cursor = conn.cursor()

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

            conn.commit()

            conn.close()

            # -------------------------------------------------
            # Result shown on dashboard
            # -------------------------------------------------

            result = {

                "route": route,

                "time": departure_time,

                "students": students,

                "capacity": capacity,

                "buses": required_buses
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

    conn.close()


    # =====================================================
    # DASHBOARD STATISTICS
    # =====================================================

    conn = sqlite3.connect(DATABASE)

    cursor = conn.cursor()


    # -----------------------------------------------------
    # Total students
    # -----------------------------------------------------

    cursor.execute("""
        SELECT COALESCE(SUM(students), 0)
        FROM bus_demand
    """)

    total_students = cursor.fetchone()[0]


    # -----------------------------------------------------
    # Total trips
    # -----------------------------------------------------

    cursor.execute("""
        SELECT COUNT(*)
        FROM bus_demand
    """)

    total_trips = cursor.fetchone()[0]


    # -----------------------------------------------------
    # Total buses required
    # -----------------------------------------------------

    cursor.execute("""
        SELECT COALESCE(SUM(required_buses), 0)
        FROM bus_demand
    """)

    total_buses_required = cursor.fetchone()[0]


    # -----------------------------------------------------
    # Total routes
    # -----------------------------------------------------

    cursor.execute("""
        SELECT COUNT(DISTINCT route)
        FROM bus_demand
    """)

    total_routes = cursor.fetchone()[0]


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

        route_summary=route_summary,

        route_labels=route_labels,

        route_students=route_students,

        route_buses=route_buses

    )


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":

    create_database()

    app.run(
        debug=True
    )