import reflex as rx
from app.states.forecast_state import ForecastState


def file_uploader_component() -> rx.Component:
    return rx.el.div(
        rx.upload.root(
            rx.el.div(
                rx.icon(
                    tag="cloud_upload",
                    class_name="w-12 h-12 text-gray-400 mb-3",
                ),
                rx.el.p(
                    rx.el.span(
                        "Cliquez pour télécharger",
                        class_name="font-semibold text-indigo-600",
                    ),
                    " ou glissez-déposez",
                    class_name="text-sm text-gray-600",
                ),
                rx.el.p(
                    "Fichier Excel (.xlsx, .xls)",
                    class_name="text-xs text-gray-500",
                ),
                class_name="flex flex-col items-center justify-center py-6",
            ),
            rx.el.p(
                rx.cond(
                    ForecastState.uploaded_file_name,
                    ForecastState.uploaded_file_name,
                    "",
                ),
                class_name="text-sm text-gray-500 mt-2 text-center",
            ),
            id="excel_uploader",
            accept={
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": [
                    ".xlsx"
                ],
                "application/vnd.ms-excel": [".xls"],
            },
            multiple=False,
            on_drop=ForecastState.handle_upload(
                rx.upload_files(upload_id="excel_uploader")
            ),
            class_name="w-full max-w-lg border-2 border-dashed border-gray-300 rounded-lg cursor-pointer bg-gray-50 hover:bg-gray-100 transition-colors duration-200 p-4",
        ),
        class_name="flex flex-col items-center w-full",
    )