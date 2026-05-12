# ==========================================================
# publish_precheck.py
# GradeOps-AI
# ==========================================================

from __future__ import annotations

import os
import sys
import unicodedata
from typing import Any

import pandas as pd

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


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

ENCODINGS = [
    "utf-8",
    "utf-8-sig",
    "cp1252",
    "latin1",
    "macroman",
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
# Encoding Repair Layer
# ==========================================================

def repair_mojibake(text: str) -> str:

    if not isinstance(text, str):
        return text

    try:
        return text.encode("latin1").decode("utf-8")
    except Exception:
        return text


# ==========================================================
# Unicode Normalization Layer
# ==========================================================

def normalize_unicode(text: str) -> str:

    if pd.isna(text):
        return ""

    text = str(text).strip()

    text = unicodedata.normalize(
        "NFKD",
        text
    )

    text = (
        text
        .encode("ascii", "ignore")
        .decode("ascii")
    )

    return text


# ==========================================================
# Semantic Normalization Layer
# ==========================================================

def normalize_text(text: str) -> str:

    if pd.isna(text):
        return ""

    text = str(text)

    text = repair_mojibake(text)

    text = normalize_unicode(text)

    return text.lower().strip()


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
            "CSV schema invalido. "
            f"Faltan columnas requeridas: {missing}"
        )

        sys.exit(1)

    log_info("CSV schema validado correctamente.")


# ==========================================================
# CSV Loader
# ==========================================================

def load_csv_safe(csv_path):

    last_error = None

    for enc in ENCODINGS:

        try:

            print(f"Trying encoding: {enc}")

            return pd.read_csv(
                csv_path,
                encoding=enc,
            )

        except UnicodeDecodeError as e:

            last_error = e

    raise last_error


# ==========================================================
# Precheck Layer
# ==========================================================

def show_publish_summary(df: pd.DataFrame):

    total_rows = len(df)

    valid_grades = df["final_grade"].notna().sum()

    manual_review = total_rows - valid_grades

    course_name = "N/A"

    if total_rows > 0:
        course_name = str(
            df.iloc[0]["course_name"]
        )

    print("")
    print("==================================================")
    print("RESUMEN DE PUBLICACION")
    print("==================================================")
    print(f"Curso             : {course_name}")
    print(f"Evaluaciones      : {valid_grades}")
    print(f"Manual review     : {manual_review}")
    print("==================================================")

    user_input = input(
        "¿Continuar? [ ENTER=continuar / c=cancelar] : "
    ).strip().lower()

    if user_input == "c":

        log_warning(
            "Proceso cancelado por usuario."
        )

        sys.exit(0)


# ==========================================================
# Google Auth
# ==========================================================

def build_classroom_service():

    token_path = "token.json"

    if not os.path.exists(token_path):

        log_error("No se encontro token.json")

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

    normalized_course_name = normalize_text(course_name)

    for course in courses:

        name = str(course.get("name", ""))

        if normalize_text(name) == normalized_course_name:
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

    normalized_activity_name = normalize_text(
        activity_name
    )

    for coursework in courseworks:

        title = str(coursework.get("title", ""))

        if normalize_text(title) == normalized_activity_name:
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
# Publish Layer
# ==========================================================

def publish_grade(
    service,
    course_id: str,
    coursework_id: str,
    submission_id: str,
    final_grade: float,
) -> None:

    patch_body = {
        "draftGrade": final_grade,
        "assignedGrade": final_grade,
    }

    (
        service.courses()
        .courseWork()
        .studentSubmissions()
        .patch(
            courseId=course_id,
            courseWorkId=coursework_id,
            id=submission_id,
            updateMask="draftGrade,assignedGrade",
            body=patch_body,
        )
        .execute()
    )

    log_info(
        f"Calificacion publicada "
        f"(submission={submission_id})"
    )


# ==========================================================
# CSV Processing
# ==========================================================

def process_csv(
    service,
    csv_path: str,
) -> None:

    if not os.path.exists(csv_path):

        log_error(f"No existe CSV: {csv_path}")

        sys.exit(1)

    df = load_csv_safe(csv_path)

    validate_csv_schema(df)

    show_publish_summary(df)

    total_rows = len(df)

    log_info(f"Filas detectadas: {total_rows}")

    auto_publish_all = False

    for _, row in df.iterrows():

        try:

            course_name = str(
                row["course_name"]
            ).strip()

            activity_name = str(
                row["activity_name"]
            ).strip()

            student_name = str(
                row["student_name"]
            ).strip()

            student_mail = str(
                row["student_mail"]
            ).strip()

            if pd.isna(row["final_grade"]):

                log_warning(
                    f"final_grade vacio para "
                    f"{student_name}"
                )

                continue

            final_grade = float(
                row["final_grade"]
            )

            final_feedback = ""

            if not pd.isna(
                row["final_feedback"]
            ):

                final_feedback = str(
                    row["final_feedback"]
                ).strip()

            print("\n--------------------------------------------------")
            print(f"Alumno: {student_name}")
            print(f"Correo: {student_mail}")
            print(f"Curso: {course_name}")
            print(f"Actividad: {activity_name}")

            print("")
            print("==================================================")
            print("PREVIEW DE EVALUACION")
            print("==================================================")
            print(f"final_grade    : {final_grade}")
            print(f"final_feedback : {final_feedback}")
            print("==================================================")

            if not auto_publish_all:

                preview_input = input(
                    "[ENTER]=continuar | "
                    "c=corregir y cancelar | "
                    "a=automatico : "
                ).strip().lower()

                if preview_input == "c":

                    log_warning(
                        "Proceso detenido para correccion manual."
                    )
                    #con continue podria solo marcarse y pasar a la siguiente evaluacion
                    #salimos
                    return

                if preview_input == "a":

                    auto_publish_all = True

                    log_info(
                        "Modo automatico habilitado."
                    )

            course = find_course(
                service,
                course_name,
            )

            if not course:

                log_warning(
                    f"Curso no encontrado: "
                    f"{course_name}"
                )

                continue

            course_id = course["id"]

            coursework = find_coursework(
                service,
                course_id,
                activity_name,
            )

            if not coursework:

                log_warning(
                    f"Actividad no encontrada: "
                    f"{activity_name}"
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
                    f"No se encontro submission "
                    f"para: {student_mail}"
                )

                continue

            submission_id = submission["id"]

            publish_grade(
                service=service,
                course_id=course_id,
                coursework_id=coursework_id,
                submission_id=submission_id,
                final_grade=final_grade,
            )

            log_info(
                f"Publicado correctamente "
                f"para {student_name}"
            )

        except HttpError as err:

            log_error(
                f"Google API error: {err}"
            )

        except Exception as err:

            log_error(
                f"Error inesperado: {err}"
            )


# ==========================================================
# Entry Point
# ==========================================================

def main():

    print("")
    print("==================================================")
    print("GradeOps-AI Publisher")
    print("==================================================")
    print("")

    service = build_classroom_service()

    process_csv(
        service=service,
        csv_path=CSV_FILENAME,
    )

    log_info("Proceso terminado.")


if __name__ == "__main__":
    main()
