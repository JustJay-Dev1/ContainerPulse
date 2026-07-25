import os
from dotenv import load_dotenv
from services.docker_service import (
    deploy_container,
    list_containers,
    stop_all_containers,
    docker_status,
    container_stats,
    docker_health
)
import time
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from services.metrics_collector import start_metrics_collector
from database import db
from flask import Flask, jsonify, request, render_template
from services.dashboard_service import (
    dashboard_summary,
    live_containers,
    deployment_history,
    container_metrics,
    latest_metrics
)

load_dotenv()

app = Flask(__name__)

def get_database_url():
    database_url = os.getenv("DATABASE_URL")

    if database_url:
        return database_url

    return (
        f"postgresql://{os.getenv('DATABASE_USER')}:"
        f"{os.getenv('DATABASE_PASSWORD')}@"
        f"{os.getenv('DATABASE_HOST')}:"
        f"{os.getenv('DATABASE_PORT', '5432')}/"
        f"{os.getenv('DATABASE_NAME')}"
    )

app.config["SQLALCHEMY_DATABASE_URI"] = get_database_url()
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
def wait_for_database(max_retries=30):

    database_url = app.config["SQLALCHEMY_DATABASE_URI"]

    print("Waiting for PostgreSQL...")

    for attempt in range(max_retries):

        try:
            engine = create_engine(database_url)
            connection = engine.connect()
            connection.close()

            print("PostgreSQL is ready!")
            return

        except OperationalError:
            print(f"Database not ready (attempt {attempt + 1}/{max_retries})")
            time.sleep(2)

    raise RuntimeError("Could not connect to PostgreSQL.")

"""  <!-- ===================== -->
    <!-- FRONTEND API'S -->
    <!-- ===================== -->"""
@app.route("/")                                                     # home page route
def home():
    return render_template("index.html")

@app.route("/dashboard")                                            # dashboard route ---> shows summary counts
def dashboard():

    return jsonify(
        dashboard_summary()
    )

@app.route("/metrics/<int:container_id>")                           # shows the history of container from container_metrics table using container_id
def metrics(container_id):

    return jsonify(
        container_metrics(container_id)
    )

@app.route("/metrics/latest")                                       # shows data of latest running container stored in container_metric table
def latest_metrics_api():

    return jsonify(
        latest_metrics()
    )

@app.route("/history")                                              # shows deployment history stored in container_logs table
def history():

    return jsonify(
        deployment_history()
    )

@app.route("/containers/live")                                      # shows all the running containers 
def live_container_api():

    return jsonify(
        live_containers()
    )

"""BACKEND API'S"""

@app.route("/health")                                               # shows docker health using "docker info" command
def health():

    docker_ok = docker_health()

    try:
        db.session.execute(db.text("SELECT 1"))
        database_ok = True
    except Exception:
        database_ok = False

    overall = docker_ok and database_ok

    return jsonify({
        "status": "healthy" if overall else "unhealthy",
        "docker": "connected" if docker_ok else "disconnected",
        "database": "connected" if database_ok else "disconnected"
    }), 200 if overall else 503

@app.route("/status")                                               # shows the number of containers running
def status():

    count = docker_status()

    return jsonify({
        "docker": "connected",
        "containers": count
    })

@app.route("/deploy", methods=["POST"])                             # POST route used to deploy docker image
def deploy():

    data = request.get_json()

    if not data or "image" not in data:
        return jsonify({
            "error": "image is required"
        }), 400

    result = deploy_container(data["image"])

    if not result["success"]:
        return jsonify({
            "error": result["error"]
        }), 500

    return jsonify({
        "message": "Container deployed",
        "container_id": result["container_id"]
    })

@app.route("/containers")                                           # gives the names of all the running containers
def containers():

    return jsonify({
        "containers": list_containers()
    })

@app.route("/stop", methods=["POST"])                               # POST request which stops all the running containers
def stop():

    ids = stop_all_containers()

    if not ids:
        return jsonify({
            "message": "No containers running"
        }), 200

    return jsonify({
        "message": "Containers stopped",
        "stopped_containers": ids
    }), 200

if __name__ == "__main__":

    wait_for_database()

    with app.app_context():

        db.create_all()

        print("Database tables created.")

    start_metrics_collector(app)

    app.run(host="0.0.0.0", port=5000)