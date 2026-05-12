# ==========================================================
# publish.py
# Standalone Google Classroom publisher
# ==========================================================

from __future__ import annotations

import os
import sys
import pandas as pd
from typing import Any

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


# ==========================================================
# Config
# ==========================================================

CSV_FILENAME = "src/evaluation_results_ag.csv"

REQUIRED_COLUMNS = [
    "course_name",
    "activity_name",
    "student_name",
    "student_mail",
    "final_grade",
    "final_feedback",
]

SCOPES = [
    "https://www.googleapis.com/auth/classroom.coursework.students",
    "https://www.googleapis.com/auth/classroom.rosters.readonly",
]


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
# CSV Validation
# ==========================================================

def validate_csv_schema(df: pd.DataFrame) -> None:

    missing = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing:
        log_error(
            "CSV schema inválido. "
            f"Faltan columnas requeridas: {missing}"
        )
        sys.exit(1)

    log_info("CSV schema validado correctamente.")


# ==========================================================
# Google Auth
# ==========================================================

def build_classroom_service():

    token_path = "token.json"

    if not os.path.exists(token_path):
        log_error("No se encontró token.json")
        sys.exit(1)

    credentials = Credentials.from_authorized_user_file(
        token_path,
        SCOPES,
    )

    service = build(
        "classroom",
        "v1",
        credentials=credentials,
    )

    log_info("Google Classroom API conectada.")

    return service


# ==========================================================
# Classroom Search Helpers
# ==========================================================

def find_course(
    service,
    course_name: str,
) -> dict[str, Any] | None:

    results = (
        service.courses()
        .list(pageSize=200)
        .execute()
    )

    courses = results.get("courses", [])

    for course in courses:

        name = str(course.get("name", "")).strip()

        if name.lower() == course_name.strip().lower():
            return course

    return None


def find_coursework(
    service,
    course_id: str,
    activity_name: str,
) -> dict[str, Any] | None:

    results = (
        service.courses()
        .courseWork()
        .list(courseId=course_id)
        .execute()
    )

    courseworks = results.get("courseWork", [])

    for coursework in courseworks:

        title = str(coursework.get("title", "")).strip()

        if title.lower() == activity_name.strip().lower():
            return coursework

    return None


def find_student_submission(
    service,
    course_id: str,
    coursework_id: str,
    student_email: str,
) -> dict[str, Any] | None:

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

    items = submissions.get("studentSubmissions", [])

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

            if email == student_email.strip().lower():
                return submission

        except Exception:
            continue

    return None


# ==========================================================
# Publish Grade + Feedback
# ==========================================================

def publish_grade_and_feedback(
    service,
    course_id: str,
    coursework_id: str,
    submission_id: str,
    final_grade: float,
    final_feedback: str,
) -> None:

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

    if final_feedback.strip():

        comment_body = {
            "text": final_feedback
        }

        (
            service.courses()
            .courseWork()
            .studentSubmissions()
            .modifyAttachments(
                courseId=course_id,
                courseWorkId=coursework_id,
                id=submission_id,
                body={}
            )
            .execute()
        )

        (
            service.courses()
            .announcements()
        )

    (
        service.courses()
        .courseWork()
        .studentSubmissions()
        .return_(
            courseId=course_id,
            courseWorkId=coursework_id,
            id=submission_id,
            body={}
        )
        .execute()
    )

    log_info(
        f"Actividad retornada correctamente "
        f"(submission={submission_id})"
    )


# ==========================================================
# Main CSV Processor
# ==========================================================

def process_csv(
    service,
    csv_path: str,
) -> None:

    if not os.path.exists(csv_path):
        log_error(f"No existe CSV: {csv_path}")
        sys.exit(1)

    df = pd.read_csv(csv_path)

    validate_csv_schema(df)

    total_rows = len(df)

    log_info(f"Filas detectadas: {total_rows}")

    for index, row in df.iterrows():

        try:

            course_name = str(row["course_name"]).strip()
            activity_name = str(row["activity_name"]).strip()
            student_name = str(row["student_name"]).strip()
            student_mail = str(row["student_mail"]).strip()

            final_grade = float(row["final_grade"])
            final_feedback = str(row["final_feedback"]).strip()

            print("\n--------------------------------------------------")
            print(f"Alumno: {student_name}")
            print(f"Correo: {student_mail}")
            print(f"Curso: {course_name}")
            print(f"Actividad: {activity_name}")

            course = find_course(
                service,
                course_name,
            )

            if not course:
                log_warning(f"Curso no encontrado: {course_name}")
                continue

            course_id = course["id"]

            coursework = find_coursework(
                service,
                course_id,
                activity_name,
            )

            if not coursework:
                log_warning(
                    f"Actividad no encontrada: {activity_name}"
                )
                continue

            coursework_id = coursework["id"]

            submission = find_student_submission(
                service,
                course_id,
                coursework_id,
                student_mail,
            )

            if not submission:
                log_warning(
                    f"No se encontró submission para: {student_mail}"
                )
                continue

            submission_id = submission["id"]

            publish_grade_and_feedback(
                service=service,
                course_id=course_id,
                coursework_id=coursework_id,
                submission_id=submission_id,
                final_grade=final_grade,
                final_feedback=final_feedback,
            )

            log_info(
                f"Publicado correctamente para "
                f"{student_name}"
            )

        except HttpError as err:
            log_error(f"Google API error: {err}")

        except Exception as err:
            log_error(f"Error inesperado: {err}")


# ==========================================================
# Entry Point
# ==========================================================

def main():

    service = build_classroom_service()

    process_csv(
        service=service,
        csv_path=CSV_FILENAME,
    )

    log_info("Proceso terminado.")


if __name__ == "__main__":
    main()