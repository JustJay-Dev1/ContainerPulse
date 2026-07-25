# 🐳 ContainerPulse

> A real-time Docker container monitoring dashboard built using Flask, PostgreSQL and Docker.

ContainerPulse is a lightweight monitoring system that tracks Docker containers running on a host machine. It collects container metrics such as CPU usage, memory usage, network activity and disk I/O, stores them in PostgreSQL, and visualizes the data through a real-time web dashboard.

---

## 📸 Dashboard Preview

![Dashboard](static/screenshots/full_page.png)

---

# ✨ Features

- 🚀 Deploy Docker containers
- 📊 Real-time container monitoring
- 💾 Persistent PostgreSQL storage
- 📈 Historical CPU and Memory metrics
- 🌐 Network usage monitoring
- 💿 Disk I/O monitoring
- 📜 Deployment history
- 🔄 Automatic metric collection every 5 seconds
- 🐳 Docker Engine connectivity check
- REST APIs for monitoring data

---

# 🛠 Tech Stack

| Category | Technology |
|-----------|------------|
| Backend | Flask |
| Database | PostgreSQL |
| ORM | SQLAlchemy |
| Container Runtime | Docker |
| Monitoring | Docker CLI |
| Frontend | HTML, CSS, JavaScript |
| Charts | Chart.js |
| Operating System | Linux (WSL) |

---
# 🗼Architecture Diagram
```text
                                    +----------------------+
                                    |        User          |
                                    | (Browser / Postman)  |
                                    +----------+-----------+
                                               |
                                               | HTTP Requests
                                               |
                                               v
                               +-------------------------------+
                               |         Flask API             |
                               |            app.py             |
                               +---------------+---------------+
                                               |
                     +-------------------------+-------------------------+
                     |                                                   |
                     |                                                   |
                     v                                                   v
        +---------------------------+                     +----------------------------+
        |      Docker Service       |                     |    Dashboard Service       |
        |   deploy / stop / stats   |                     | Queries & Aggregations     |
        +-------------+-------------+                     +-------------+--------------+
                      |                                                   |
                      |                                                   |
                      v                                                   |
             +--------------------+                                      |
             |   Docker Engine    |                                      |
             |  (Containers)      |                                      |
             +----------+---------+                                      |
                        |                                                |
                        | docker stats                                   |
                        |                                                |
                        v                                                |
             +-----------------------------+                             |
             |    Metrics Collector        |<----------------------------+
             | Background Thread (5 sec)   |
             +--------------+--------------+
                            |
                            | Stores Metrics
                            |
                            v
                 +------------------------------+
                 |      PostgreSQL Database     |
                 |------------------------------|
                 | container_logs               |
                 | container_metrics            |
                 +--------------+---------------+
                                ^
                                |
                                | Reads Dashboard Data
                                |
                    +-----------+------------+
                    |      dashboard.js      |
                    | Charts & Live Tables   |
                    +-----------+------------+
                                |
                                |
                                v
                     +------------------------+
                     |   HTML + CSS + Charts  |
                     |   ContainerPulse UI    |
                     +------------------------+
```
---

# 📁 Project Structure

![FolderStructure](static/screenshots/folder_structure.png)

# ⚙️ How It Works

1. Flask exposes REST APIs for the dashboard.
2. Docker commands are executed using Python's `subprocess` module.
3. Every 5 seconds, a background metrics collector fetches live statistics from Docker.
4. Metrics are stored in PostgreSQL.
5. The frontend polls the APIs and updates the dashboard in real time.

---
# 📊 Dashboard

## Overview

Shows

- Running Containers
- Stopped Containers
- Total Deployments
- Docker Connection Status

![Dashboard](static/screenshots/full_page.png)

---

## Live Container Monitoring

Displays live resource utilization of all running containers.

Metrics include

- CPU Usage
- Memory Usage
- Network Usage
- Disk I/O
- Container Status

![Live_Containers](static/screenshots/full_page.png)

---
## CPU Usage

Real-time CPU utilization collected every 5 seconds.

![CPU_Chart](static/screenshots/cpu_usage.png)

---
## Memory Usage

Real-time Memory utilization.

![Memory_Chart](static/screenshots/memoryusage.png)

---
## Deployment History

Displays every deployment stored in PostgreSQL.

- Container Name
- Image
- Creation Time
- Stop Time
- Status

![History](static/screenshots/history.png)

---
# 🗄 Data Model 

The application uses two tables.

## container_logs

Stores deployment information.

| Column |
|---------|
| container_id |
| container_name |
| image |
| status |
| created_at |
| stopped_at |

![Container_Logs](static/screenshots/container_logs.png)

---

## container_metrics

Stores historical metrics.

| Column |
|---------|
| container_log_id |
| cpu_usage |
| memory_usage |
| network_rx |
| network_tx |
| disk_read |
| disk_write |
| recorded_at |

![Container_Metrics](static/screenshots/container_metrics.png)

---
# 🌐 REST API

| Method | Endpoint | Description |
|----------|-----------|-------------|
| GET | `/dashboard` | Dashboard summary |
| GET | `/containers/live` | Running containers |
| GET | `/history` | Deployment history |
| GET | `/metrics/<container_id>` | Historical metrics |
| POST | `/deploy` | Deploy new container |
| POST | `/stop` | Stop all monitored containers |

---
# 🚀 Installation

Clone the repository

```bash
git clone https://github.com/JustJay-Dev1/ContainerPulse.git

cd ContainerPulse
```

Create virtual environment

```bash
python -m venv venv
```

Activate

Linux

```bash
source venv/bin/activate
```

Windows

```bash
venv\Scripts\activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

Start PostgreSQL

```bash
docker compose up -d
```

Run the application

```bash
python app.py
```

Open

```
http://localhost:5000
```

---
## ⚙️ Configuration

Create a `.env` file in the project root.

```env
# PostgreSQL Database URL
DATABASE_URL=postgresql://admin:password@localhost:5432/monitoring

# Metrics collection interval (seconds)
METRICS_INTERVAL=5
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string used by SQLAlchemy | `postgresql://admin:password@localhost:5432/monitoring` |
| `METRICS_INTERVAL` | Time interval (in seconds) for collecting container metrics | `5` |

> **Note:** The background metrics collector polls Docker every `METRICS_INTERVAL` seconds and stores CPU, memory, network, and disk usage in PostgreSQL.

---

> Copy `.env.example` to `.env` and update the values according to your local PostgreSQL configuration.
---
# 📚 What I Learned

During this project I gained practical experience with

- Flask REST APIs
- Docker CLI integration
- PostgreSQL
- SQLAlchemy ORM
- Background Threads
- System Monitoring
- Chart.js
- Linux Development
- Project Structuring
- Git & GitHub

---
# ❗Limitation
ContainerPulse tracks containers deployed through its REST API. Containers started or stopped directly using Docker CLI are not synchronized with the database in the current version.
---

# ☸️ Kubernetes Deployment

ContainerPulse can also be deployed on Kubernetes.

### Kubernetes Components

| Resource | Purpose |
|----------|----------|
| Namespace | Isolates ContainerPulse resources |
| ConfigMap | Stores application configuration |
| Secret | Stores database credentials |
| StatefulSet | Deploys PostgreSQL with persistent identity |
| PersistentVolumeClaim | Persists PostgreSQL data |
| Deployment | Runs the ContainerPulse application |
| Service | Exposes the application inside/outside the cluster |

### Deploy

```bash
kubectl apply -f k8s/
```

Verify deployment

```bash
kubectl get all -n containerpulse
```

Access the application

```bash
minikube service containerpulse -n containerpulse --url
```
---
# 🗼Architecture Diagram kubernetes

                    Browser
                        │
                        ▼
              NodePort Service
                        │
                        ▼
              ContainerPulse Deployment
                        │
                        ▼
             ContainerPulse Pod
               │              │
               │              ▼
               │       Docker Socket
               │
               ▼
          PostgreSQL Service
               │
               ▼
        PostgreSQL StatefulSet
               │
               ▼
      Persistent Volume Claim
               │
               ▼
         Persistent Volume

---
# 🚧 Future Improvements

- GitHub Actions CI/CD
- Helm Charts
- Prometheus Monitoring
- Grafana Dashboards
- Horizontal Pod Autoscaler
- Ingress Controller
- Kubernetes-native deployment engine

---
# 📄 License

MIT License