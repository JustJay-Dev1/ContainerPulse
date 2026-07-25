"""  <!-- ===================== -->
    <!-- this is a metric collector thread which executes every METRICS_INTERVAL to get all the data from every running container and store it in container_metric table  -->
    <!-- ===================== -->"""
import os
import json
import re
import threading
import time

from datetime import datetime

from database import db
from models import ContainerLog, ContainerMetric
from services.docker_service import docker
from dotenv import load_dotenv
load_dotenv()

METRICS_INTERVAL = int(os.getenv("METRICS_INTERVAL", 5))                # use the METRICS_INTERVAL variable created in .env file, has default value 5

def parse_cpu(cpu):                                                     # used to process the cpu output by removing % from the output 
    return float(cpu.replace("%", ""))

def convert_to_mb(value):                                               # converts all the value to megabytes

    value = value.strip()

    if value.startswith("0B"):
        return 0.0

    number = float(re.findall(r"[\d.]+", value)[0])

    if "GiB" in value or "GB" in value:
        return number * 1024

    elif "MiB" in value or "MB" in value:
        return number

    elif "KiB" in value or "kB" in value:
        return number / 1024

    elif value.endswith("B"):
        return number / (1024 * 1024)

    return number

def parse_memory(memory):                                               # get memory used in GBs and convert it into MBs

    used = memory.split("/")[0].strip()

    return convert_to_mb(used)

def parse_network(network):                                             # split network into received and transmitted

    rx, tx = network.split("/")

    return (
        convert_to_mb(rx.strip()),
        convert_to_mb(tx.strip())
    )

def parse_disk(disk):                                                   # split disk into read and write

    read, write = disk.split("/")

    return (
        convert_to_mb(read.strip()),
        convert_to_mb(write.strip())
    )

def collect_metrics():                                                  # collect all the data required to store intpo container_metrics table

    running = ContainerLog.query.filter_by(                             # runs "SELECT * FROM container_log WHERE status = 'running';" on container_logs to get all the running containers
        status="running"
    ).all()

    if not running:
        return

    running_map = {
        c.container_id: c
        for c in running
    }

    result = docker([                                                   # runs "docker stats container_id --no-stream --format "{{json .}}"", get json output of docker stats 
        "stats",
        "--no-stream",
        "--format",
        "{{json .}}"
    ])

    if result.returncode != 0:
        return

    metrics = []

    for line in result.stdout.splitlines():

        stats = json.loads(line)

        container = None

        for cid, log in running_map.items():

            if cid.startswith(stats["Container"]):

                container = log

                break

        if container is None:
            continue

        cpu = parse_cpu(stats["CPUPerc"])

        memory = parse_memory(stats["MemUsage"])

        network_rx, network_tx = parse_network(
            stats["NetIO"]
        )

        disk_read, disk_write = parse_disk(
            stats["BlockIO"]
        )

        metric = ContainerMetric(

            container_log_id=container.id,

            cpu_usage=cpu,

            memory_usage=memory,

            network_rx=network_rx,

            network_tx=network_tx,

            disk_read=disk_read,

            disk_write=disk_write,

            recorded_at=datetime.now()

        )

        metrics.append(metric)

    if metrics:

        db.session.add_all(metrics)

        db.session.commit()

def collector_loop():                                                   # run collecter_metrics function every METRICS_INTERVAL

    while True:

        try:

            collect_metrics()

        except Exception as e:

            print(f"[Collector Error] {e}")

        time.sleep(METRICS_INTERVAL)

def start_metrics_collector(app):                                       # starts a background thread that runs a infinite metric-collection loop

    def collector():

        with app.app_context():

            collector_loop()

    thread = threading.Thread(
        target=collector,
        daemon=True
    )

    thread.start()