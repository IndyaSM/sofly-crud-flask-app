from flask import Flask, request, redirect, url_for
import sqlite3

app = Flask(__name__)


def get_db_connection():
    conn = sqlite3.connect("sofly.db")
    conn.row_factory = sqlite3.Row
    return conn

def create_table():
        conn = get_db_connection()
        conn.execute("""
            CREATE TABLE IF NOT EXISTS flight_requests (
                     id INTEGER PRIMARY KEY AUTOINCREMENT,
                     passenger_name TEXT NOT NULL,
                     departure_city TEXT NOT NULL,
                     destination_city TEXT NOT NULL
            )
        """)
        conn.commit()
        conn.close()


        @app.route("/")
        def home():
            return """
            <h1>SoFly Flight Request System</h1>
            <p>This app demonstrates Create, Read, Update, and Delete using Flask and SQLite.</p>

            <h3>Submit Flight Request</h3>
            <form action="/submit" method="POST">
            Passenger Name:<br>
            <input type="text" name="passenger" required><br><br>

            Departure City:<br>
            <input type="text" name="departure" required><br><br>

            Destination City:<br>
            <input type="text" name="destination" required><br><br>

            <button type="submit">Submit Request</button>
            </form>

            <br>
            <a href="/requests">View Requests</a>
            """
        

        @app.route("/submit", methods=["POST"])
        def submit():
            passenger = request.form["passenger"]
            departure = request.form["departure"]
            destination = request.form["destination"]

            conn = get_db_connection()
            conn.execute(
                "INSERT INTO flight_requests (passenger_name, departure_city, destination_city) VALUES (?, ?, ?)",
                (passenger, departure, destination)
            )
            conn.commit()
            conn.close()

            return redirect(url_for("requests_page"))
        

        @app.route("/requests")
        def requests_page():
            conn = get_db_connection()
            rows = conn.execute("SELECT * FROM flight_requests").fetchall()
            conn.close()

            html = "<h1>Submitted Flight Requests</h1>"
            html += "<a href='/'>Back to Home</a><br><br>"

            if not rows:
                html += "No requests submitted yet.<br><br>"

            for r in rows:
                html += f"""
                {r['id']} - {r['passenger_name']} | {r['departure_city']}  {r['destination_city']}
                <a href='/edit/{r['id']}'>Edit</a>
                <a href='/delete/{r['id']}'>Delete</a>
                <br><br>
                """

            return html


@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    conn = get_db_connection()

    if request.method == "POST":
        passenger = request.form["passenger"]
        departure = request.form["departure"]
        destination = request.form["destination"]

        conn.execute(
            "UPDATE flight_requests SET passenger_name=?, departure_city=?, destination_city=? WHERE id=?",
            (passenger, departure, destination, id)
            )
        conn.commit()
        conn.close()
        return redirect(url_for("requests_page"))
    
    row = conn.execute(
        "SELECT * FROM flight_requests WHERE id=?",
        (id,)
    ).fetchone()
    conn.close()

    if row is None:
        return "<h1>Request not found</h1><a href='/requests'>Back to Requests</a>"

    return f"""
    <h1>Edit Flight Request</h1>

    <form method="POST">
        Passenger Name:<br>
        <input type="text" name="passenger" value="{row['passenger_name']}" required><br><br>

        Departure City:<br>
        <input type="text" name="departure" value="{row['departure_city']}" required><br><br>

        Destination City:<br>
        <input type="text" name="destination" value="{row['destination_city']}" required><br><br>

        <button type="submit">Update Request</button>
    </form>

    <br>
    <a href="/requests">Back to Requests</a>
    """
    
@app.route("/delete/<int:id>")
def delete(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM flight_requests WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect(url_for("requests_page"))
    
if __name__ == "__main__":
    create_table()
    app.run(debug=True)