# runtime/i18n.py

from __future__ import annotations

from typing import Any


DEFAULT_LANGUAGE = "es"


I18N = {
    "es": {
        "ui": {
            "select": "Selecciona {type_label}:",
            "enter_number": "Ingresa número:",
            "go_back": "Regresar",
            "invalid_option": "❌ Opción inválida. Intenta de nuevo.",
        },
        "runtime": {
            "csv_generated": "✅ CSV generado: {path}",
            "zip_generated": "✅ ZIP generado: {path}",
            "process_done": "✅ Proceso terminado.",
        },
        "feedback": {
            "no_submission": "Sin entrega enviada. Calificacion automatica en 0.",
            "manual_review": "Requiere revision manual por tipo de evidencia.",
            "readable_content": "Contenido legible detectado con {word_count} palabras aprox.",
            "not_readable": "No se detecto contenido legible automaticamente.",
        },
        "fallbacks": {
            "file": "archivo",
            "course": "curso",
            "activity": "actividad",
        },
        "labels": {
            "submission_status": {
                "TURNED_IN": "turned_in",
                "CREATED": "assigned_not_submitted",
                "RETURNED": "returned",
                "RECLAIMED_BY_STUDENT": "reclaimed_by_student",
                "UNKNOWN": "unknown",
            },
            "submission_type": {
                "none": "none",
                "text_only": "text_only",
                "image_only": "image_only",
                "file_only": "file_only",
                "mixed": "mixed",
                "link_only": "link_only",
            },
            "bool": {
                True: "true",
                False: "false",
            },
        },
    },
    "en": {
        "ui": {
            "select": "Select {type_label}:",
            "enter_number": "Enter number:",
            "go_back": "Go back",
            "invalid_option": "❌ Invalid option. Try again.",
        },
        "runtime": {
            "csv_generated": "✅ CSV generated: {path}",
            "zip_generated": "✅ ZIP generated: {path}",
            "process_done": "✅ Process finished.",
        },
        "feedback": {
            "no_submission": "No submission sent. Automatic grade set to 0.",
            "manual_review": "Requires manual review due to evidence type.",
            "readable_content": "Readable content detected with about {word_count} words.",
            "not_readable": "No readable content was detected automatically.",
        },
        "fallbacks": {
            "file": "file",
            "course": "course",
            "activity": "activity",
        },
        "labels": {
            "submission_status": {
                "TURNED_IN": "turned_in",
                "CREATED": "assigned_not_submitted",
                "RETURNED": "returned",
                "RECLAIMED_BY_STUDENT": "reclaimed_by_student",
                "UNKNOWN": "unknown",
            },
            "submission_type": {
                "none": "none",
                "text_only": "text_only",
                "image_only": "image_only",
                "file_only": "file_only",
                "mixed": "mixed",
                "link_only": "link_only",
            },
            "bool": {
                True: "true",
                False: "false",
            },
        },
    },
}


class _SafeFormatDict(dict):
    def __missing__(self, key: str) -> str:
        return "{" + key + "}"


def get_runtime_language() -> str:
    """
    Futuro punto central para cargar idioma desde config/runtime.
    """
    return DEFAULT_LANGUAGE


LANG = get_runtime_language()


def t(
    key: str,
    lang: str | None = None,
    **kwargs: Any,
) -> str:

    active_lang = lang or LANG
    fallback_lang = "es"

    def resolve_translation(
        language: str,
        translation_key: str,
    ) -> Any:

        value: Any = I18N.get(language, {})

        for part in translation_key.split("."):

            if not isinstance(value, dict):
                raise KeyError(part)

            if part not in value:
                raise KeyError(part)

            value = value[part]

        return value

    try:
        value = resolve_translation(
            active_lang,
            key,
        )

    except Exception:

        try:
            value = resolve_translation(
                fallback_lang,
                key,
            )

        except Exception:
            return f"[missing_translation:{key}]"

    if not isinstance(value, str):
        return str(value)

    format_kwargs = dict(kwargs)

    if (
        "type_label" in format_kwargs
        and "tipo" not in format_kwargs
    ):
        format_kwargs["tipo"] = format_kwargs["type_label"]

    if (
        "name" in format_kwargs
        and "nombre" not in format_kwargs
    ):
        format_kwargs["nombre"] = format_kwargs["name"]

    return (
        value.format_map(_SafeFormatDict(format_kwargs))
        if format_kwargs
        else value
    )


def labels() -> dict[str, Any]:
    return I18N.get(
        LANG,
        I18N["es"],
    )["labels"]