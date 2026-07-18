
#  1. 

A secure, tested, containerized backend service built with FastAPI, SQLAlchemy, JWT authentication, and PostgreSQL, featuring full CI/CD deployment to Docker Hub.

Features:
   User registration & login (JWT authentication)

   Polymorphic calculation system (addition, subtraction, multiplication, division)

   CRUD operations for user‑owned calculations

   Secure password hashing

   Token expiration & refresh logic

   Integration tests using PostgreSQL

   Unit tests for authentication & JWT

   GitHub Actions CI/CD pipeline

   Dockerized deployment

   Automatic vulnerability scanning (Trivy)

   Auto‑generated API documentation (Swagger + ReDoc)

Tech Stack
   FastAPI

   SQLAlchemy ORM

   PostgreSQL

   Pytest

   Docker

   GitHub Actions

   JWT (python‑jose)

   Pydantic v2

   Uvicorn
---

# 🧩 2. Configuration

## Clone

   git clone https://github.com/davidb9790/module12_is601_v2.git
   cd module12_is601_v2

---

## Create Virtual Environment
   python -m venv venv
   source venv/bin/activate


---

## Install Dependencies
   pip install -r requirements.txt


---

# Running the Application

   python3 main.py

   API will be available at:
   http://localhost:8000

---

# 🐳 5. (Optional) Docker Setup

> Skip if Docker isn't used in this module.

## Install Docker

- [Install Docker Desktop for Mac](https://www.docker.com/products/docker-desktop/)
- [Install Docker Desktop for Windows](https://www.docker.com/products/docker-desktop/)

## Build Docker Image

```bash
docker build -t <image-name> .
```

## Run Docker Container

```bash
docker run -it --rm <image-name>
```

---

# 🔥 Useful Commands Cheat Sheet

| Action                         | Command                                          |
| ------------------------------- | ------------------------------------------------ |
| Install Homebrew (Mac)          | `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"` |
| Install Git                     | `brew install git` or Git for Windows installer |
| Configure Git Global Username  | `git config --global user.name "Your Name"`      |
| Configure Git Global Email     | `git config --global user.email "you@example.com"` |
| Clone Repository                | `git clone <repo-url>`                          |
| Create Virtual Environment     | `python3 -m venv venv`                           |
| Activate Virtual Environment   | `source venv/bin/activate` / `venv\Scripts\activate.bat` |
| Install Python Packages        | `pip install -r requirements.txt`               |
| Build Docker Image              | `docker build -t <image-name> .`                |
| Run Docker Container            | `docker run -it --rm <image-name>`               |
| Push Code to GitHub             | `git add . && git commit -m "message" && git push` |

---

# 📋 Notes

http://localhost:8000/docs API Test GUI
http://localhost:5050      pgAdmin

---
# Authentication Endpoints
   Register
      POST /auth/register

   Login (JSON)
      POST /auth/login

   Login (Form – Swagger)
      POST /auth/token

---
# Calculation Endpoints
   Create Calculation
      POST /calculations

   List Calculations
      GET /calculations

   Get Calculation
      GET /calculations/{id}

   Update Calculation
      PUT /calculations/{id}

   Delete Calculation
      DELETE /calculations/{id}
---

# Testing
   pytest