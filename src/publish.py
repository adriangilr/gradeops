# ==========================================================
# pub_api_coursework_test.py
# GradeOps-AI
# ==========================================================

from __future__ import annotations

import os
import sys
from pathlib import Path

import pandas as pd

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


CSV_FILENAME = "src/evaluation_results_ag.csv"

SCOPES = [
    "https://www.googleapis.com/auth/classroom.coursework.students",
    "https://www.googleapis.com/auth/classroom.rosters.readonly",
    "https://www.googleapis.com/auth/classroom.profile.emails",
    "https://www.googleapis.com/auth/classroom.courses.readonly",
]

DRY_RUN = False


# ==========================================================
# Logging
# ==========================================================

def log_info(message: str) -> None:
    print(f"✅ {message}")


def log_warning(message: str) -> None:
    print(f"⚠️ {message}")


def log_error(message: str) -> None:
    print(f"❌ {message}")


# ==========================================================
# OAuth
# ==========================================================

def get_credentials():

    credentials_path = Path(
        "credentials/client_secret.json"
    )

    token_path = Path("token.json")

    creds = None

    if token_path.exists():

        creds = Credentials.from_authorized_user_file(
            str(token_path),
            SCOPES,
        )

    if creds and creds.expired and creds.refresh_token:

        creds.refresh(Request())

        token_path.write_text(
            creds.to_json(),
            encoding="utf-8",
        )

    elif not creds or not creds.valid:

        flow = InstalledAppFlow.from_client_secrets_file(
            str(credentials_path),
            SCOPES,
        )

        creds = flow.run_local_server(port=0)

        token_path.write_text(
            creds.to_json(),
            encoding="utf-8",
        )

    return creds


def build_classroom_service():

    creds = get_credentials()

    service = build(
        "classroom",
        "v1",
        credentials=creds,
    )

    log_info("Google Classroom API conectada.")

    return service


# ==========================================================
# Course selection
# ==========================================================

def select_course(service):

    results = (
        service.courses()
        .list(pageSize=100)
        .execute()
    )

    courses = results.get("courses", [])

    print("")
    print("==================================================")
    print("MATERIAS DISPONIBLES")
    print("==================================================")

    for idx, course in enumerate(courses, start=1):

        print(
            f"{idx}. "
            f"{course.get('name')} "
            f"({course.get('id')})"
        )

    print("==================================================")

    selected = int(
        input("Selecciona materia: ")
    ) - 1

    return courses[selected]


# ==========================================================
# Create coursework from API
# ==========================================================

def create_api_coursework(
    service,
    course_id,
):

    title = input(
        "Titulo nueva actividad API: "
    ).strip()

    coursework = {
        "title": title,
        "description": (
            "Actividad creada desde "
            "GradeOps-AI API"
        ),
        "workType": "ASSIGNMENT",
        "state": "PUBLISHED",
        "maxPoints": 100,
    }

    created = (
        service.courses()
        .courseWork()
        .create(
            courseId=course_id,
            body=coursework,
        )
        .execute()
    )

    print("")
    print("==================================================")
    print("API COURSEWORK CREATED")
    print("==================================================")
    print(created)
    print("==================================================")

    return created


# ==========================================================
# Submission lookup
# ==========================================================

def find_student_submission(
    service,
    course_id,
    coursework_id,
    student_email,
):

    submissions = (
        service.courses()
        .courseWork()
        .studentSubmissions()
        .list(
            courseId=course_id,
            courseWorkId=coursework_id,
        )
        .execute()
    )

    items = submissions.get(
        "studentSubmissions",
        [],
    )

    normalized_email = (
        student_email
        .strip()
        .lower()
    )

    for submission in items:

        user_id = submission.get("userId")

        try:

            profile = (
                service.userProfiles()
                .get(userId=user_id)
                .execute()
            )

            email = (
                profile.get("emailAddress", "")
                .strip()
                .lower()
            )

            if email == normalized_email:
                return submission

        except Exception:
            continue

    return None


# ==========================================================
# Publish grade
# ==========================================================

def publish_grade(
    service,
    course_id,
    coursework_id,
    submission,
    final_grade,
):

    submission_id = submission["id"]

    print("")
    print("==================================================")
    print("DEBUG SUBMISSION")
    print("==================================================")
    print(submission)
    print("==================================================")

    if DRY_RUN:

        log_warning(
            f"[DRY_RUN] "
            f"{submission_id} "
            f"{final_grade}"
        )

        return

    patch_body = {
        "draftGrade": final_grade,
    }

    (
        service.courses()
        .courseWork()
        .studentSubmissions()
        .patch(
            courseId=course_id,
            courseWorkId=coursework_id,
            id=submission_id,
            updateMask="draftGrade",
            body=patch_body,
        )
        .execute()
    )

    log_info(
        f"Publicado: {submission_id}"
    )


# ==========================================================
# Main
# ==========================================================

def main():

    print("")
    print("==================================================")
    print("GradeOps-AI API Coursework Test")
    print("==================================================")

    service = build_classroom_service()

    selected_course = select_course(service)

    course_id = selected_course["id"]

    created_coursework = create_api_coursework(
        service,
        course_id,
    )

    coursework_id = created_coursework["id"]

    print("")
    print("==================================================")
    print("NEXT STEP")
    print("==================================================")
    print("1. Abre Classroom")
    print("2. Entrega una tarea con una cuenta alumno")
    print("3. Ejecuta nuevamente el publisher")
    print("==================================================")

    print("")
    print(f"coursework_id : {coursework_id}")


if __name__ == "__main__":
    main()
