# ==========================================================
# pub-men.py
# GradeOps-AI
# ==========================================================

from __future__ import annotations

import os
import sys
import unicodedata
from pathlib import Path
from typing import Any

import pandas as pd

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

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
    "https://www.googleapis.com/auth/classroom.profile.emails",
    "https://www.googleapis.com/auth/classroom.courses.readonly",
]

ENCODINGS = [
    "utf-8",
    "utf-8-sig",
    "cp1252",
    "latin1",
    "macroman",
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

def get_credentials(
    credentials_path: Path,
    token_path: Path,
) -> Credentials:

    creds = None

    if token_path.exists():

        creds = Credentials.from_authorized_user_file(
            str(token_path),
            SCOPES,
        )

    if creds and creds.expired and creds.refresh_token:

        log_warning(
            "Token expirado. Renovando..."
        )

        creds.refresh(Request())

        token_path.write_text(
            creds.to_json(),
            encoding="utf-8",
        )

    elif not creds or not creds.valid:

        if not credentials_path.exists():

            log_error(
                f"No existe: {credentials_path}"
            )

            sys.exit(1)

        log_info(
            "Abriendo navegador OAuth..."
        )

        flow = InstalledAppFlow.from_client_secrets_file(
            str(credentials_path),
            SCOPES,
        )

        creds = flow.run_local_server(port=0)

        token_path.write_text(
            creds.to_json(),
            encoding="utf-8",
        )

        log_info(
            "Nuevo token.json generado."
        )

    return creds


# ==========================================================
# Encoding
# ==========================================================

def repair_mojibake(text: str) -> str:

    if not isinstance(text, str):
        return text

    try:
        return text.encode("latin1").decode("utf-8")
    except Exception:
        return text


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


def normalize_text(text: str) -> str:

    if pd.isna(text):
        return ""

    text = str(text)

    text = repair_mojibake(text)

    text = normalize_unicode(text)

    return text.lower().strip()


# ==========================================================
# CSV
# ==========================================================

def validate_csv_schema(df: pd.DataFrame) -> None:

    missing = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing:

        log_error(
            f"Faltan columnas: {missing}"
        )

        sys.exit(1)

    log_info("CSV schema validado correctamente.")


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
# Classroom
# ==========================================================

def build_classroom_service():

    credentials_path = Path("credentials/client_secret.json")
    token_path = Path("token.json")

    credentials = get_credentials(
        credentials_path=credentials_path,
        token_path=token_path,
    )

    service = build(
        "classroom",
        "v1",
        credentials=credentials,
    )

    log_info("Google Classroom API conectada.")

    return service


def select_course(service):

    results = (
        service.courses()
        .list(pageSize=200)
        .execute()
    )

    courses = results.get("courses", [])

    if not courses:

        log_error("No se encontraron cursos.")

        sys.exit(1)

    print("")
    print("==================================================")
    print("MATERIAS DISPONIBLES")
    print("==================================================")

    for idx, course in enumerate(courses, start=1):

        print(
            f"{idx}. {course.get('name')} "
            f"({course.get('id')})"
        )

    print("==================================================")

    selected = int(
        input("Selecciona materia: ")
    ) - 1

    return courses[selected]


def select_coursework(
    service,
    course_id,
):

    results = (
        service.courses()
        .courseWork()
        .list(courseId=course_id)
        .execute()
    )

    courseworks = results.get(
        "courseWork",
        [],
    )

    if not courseworks:

        log_error(
            "No se encontraron actividades."
        )

        sys.exit(1)

    print("")
    print("==================================================")
    print("ACTIVIDADES DISPONIBLES")
    print("==================================================")

    for idx, coursework in enumerate(
        courseworks,
        start=1,
    ):

        print(
            f"{idx}. {coursework.get('title')}"
        )

    print("==================================================")

    selected = int(
        input("Selecciona actividad: ")
    ) - 1

    return courseworks[selected]


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
# Summary
# ==========================================================

def show_publish_summary(
    df,
    course_name,
    activity_name,
):

    total_rows = len(df)

    valid_grades = df[
        "final_grade"
    ].notna().sum()

    manual_review = 0

    if "requires_manual_review" in df.columns:

        manual_review = (
            df["requires_manual_review"]
            .astype(str)
            .str.upper()
            .eq("TRUE")
            .sum()
        )

    print("")
    print("==================================================")
    print("RESUMEN DE PUBLICACION")
    print("==================================================")
    print(f"Curso Clsr                     : {course_name}")
    print(f"Actividad Clsr                 : {activity_name}")
    print(f"Evaluaciones detectadas en")
    print(f" src/evaluation_results_ag.csv : {valid_grades}")
    print(f"Manual review                  : {manual_review}")
    print(f"DRY_RUN                        : {DRY_RUN}")
    print("==================================================")

    user_input = input(
        "¿Continuar? [ENTER/c] : "
    ).strip().lower()

    if user_input == "c":

        log_warning(
            "Proceso cancelado."
        )

        sys.exit(0)


# ==========================================================
# Publish
# ==========================================================

def publish_grade(
    service,
    course_id,
    coursework_id,
    submission_id,
    final_grade,
):

    if DRY_RUN:

        log_warning(
            f"[DRY_RUN] "
            f"submission={submission_id} "
            f"grade={final_grade}"
        )

        return

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
        f"Publicado submission={submission_id}"
    )


# ==========================================================
# Main Processing
# ==========================================================

def process_csv(
    service,
    csv_path,
):

    if not os.path.exists(csv_path):

        log_error(
            f"No existe CSV: {csv_path}"
        )

        sys.exit(1)

    df = load_csv_safe(csv_path)

    validate_csv_schema(df)

    selected_course = select_course(service)

    course_id = selected_course["id"]

    selected_coursework = select_coursework(
        service,
        course_id,
    )

    coursework_id = selected_coursework["id"]

    selected_course_name = normalize_text(
        selected_course["name"]
    )

    selected_activity_name = normalize_text(
        selected_coursework["title"]
    )

    df["course_name_normalized"] = (
        df["course_name"]
        .astype(str)
        .apply(normalize_text)
    )

    df["activity_name_normalized"] = (
        df["activity_name"]
        .astype(str)
        .apply(normalize_text)
    )

    # ------------------------------------------------------
    # v1 publishing strategy
    # ------------------------------------------------------
    # The selected Google Classroom activity is the publish target.
    # CSV activity_name is not used for matching yet because current
    # courses and activities are not fully standardized.
    #
    # For now, the CSV only provides:
    # - student_name
    # - student_mail
    # - final_grade
    # - final_feedback
    #
    # Future evolution:
    # Replace this with coursework_id or exact activity matching.
    # ------------------------------------------------------

    log_warning(
        "Activity matching deshabilitado. "
        "Usando todas las filas del CSV para la actividad seleccionada."
    )

    filtered_df = df.copy()

    print("")
    print("==================================================")
    print("DEBUG PUBLISH TARGET")
    print("==================================================")
    print(f"selected_course_name   : {selected_course_name}")
    print(f"selected_activity_name : {selected_activity_name}")

    print("")
    print("CSV activities detectadas:")

    for activity in (
        df["activity_name_normalized"]
        .dropna()
        .unique()
    ):
        print(f" - {activity}")


    if filtered_df.empty:

        log_error(
            "El CSV no contiene filas para publicar."
        )

        sys.exit(1)

    show_publish_summary(
        filtered_df,
        selected_course["name"],
        selected_coursework["title"],
    )

    auto_publish_all = False

    for _, row in filtered_df.iterrows():

        try:

            student_name = str(
                row["student_name"]
            ).strip()

            student_mail = str(
                row["student_mail"]
            ).strip()

            final_grade = float(
                row["final_grade"]
            )

            final_feedback = str(
                row["final_feedback"]
            ).strip()

            print("")
            print("--------------------------------------------------")
            print(f"Alumno    : {student_name}")
            print(f"Correo    : {student_mail}")

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
                    "c=cancelar | "
                    "a=automatico : "
                ).strip().lower()

                if preview_input == "c":

                    log_warning(
                        "Proceso cancelado."
                    )

                    return

                if preview_input == "a":

                    auto_publish_all = True

            submission = find_student_submission(
                service,
                course_id,
                coursework_id,
                student_mail,
            )

            if not submission:

                log_warning(
                    f"No submission: "
                    f"{student_mail}"
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

        except HttpError as err:

            log_error(
                f"Google API error: {err}"
            )

        except Exception as err:

            log_error(
                f"Error inesperado: {err}"
            )


# ==========================================================
# Entry
# ==========================================================

def main():

    print("")
    print("==================================================")
    print("GradeOps-AI Publisher")
    print("==================================================")

    service = build_classroom_service()

    process_csv(
        service=service,
        csv_path=CSV_FILENAME,
    )

    log_info("Proceso terminado.")


if __name__ == "__main__":
    main()
