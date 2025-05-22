import reflex as rx
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import io
import json

try:
    from xgboost import XGBRegressor

    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False

    class XGBRegressor:

        def __init__(self, *args, **kwargs):
            print(
                "Warning: XGBoost not found. Using dummy regressor."
            )

        def fit(self, X, y):
            print("Dummy XGBRegressor: Fit called.")

        def predict(self, X):
            print("Dummy XGBRegressor: Predict called.")
            return np.full(
                X.shape[0],
                25.0 + np.random.rand(X.shape[0]) * 5,
            )


class ForecastState(rx.State):
    uploaded_file_name: str = ""
    is_processing: bool = False
    forecast_chart_data: list[dict[str, str | float]] = []
    raw_forecast_df_json: str = ""
    show_chart: bool = False
    error_message: str | None = None
    status_message: str = (
        "Veuillez télécharger un fichier Excel."
    )
    LAG_FEATURES: int = 30
    FORECAST_CYCLES: int = 200

    @rx.event
    async def handle_upload(
        self, files: list[rx.UploadFile]
    ):
        if not files:
            self.error_message = (
                "Aucun fichier sélectionné."
            )
            self.status_message = "Échec du téléchargement."
            return
        file = files[0]
        if not file.name.endswith((".xlsx", ".xls")):
            self.error_message = "Format de fichier invalide. Veuillez télécharger un fichier Excel (.xlsx ou .xls)."
            self.status_message = "Échec du téléchargement."
            return
        try:
            upload_data = await file.read()
            self.uploaded_file_name = file.name
            self.status_message = f"Fichier '{file.name}' téléchargé. Prêt pour la prévision."
            self.error_message = None
            self.show_chart = False
            self.forecast_chart_data = []
            self.raw_forecast_df_json = ""
            outfile_path = rx.get_upload_dir() / file.name
            with open(outfile_path, "wb") as outfile:
                outfile.write(upload_data)
            self.uploaded_file_name = file.name
        except Exception as e:
            self.error_message = (
                f"Erreur lors du téléchargement: {str(e)}"
            )
            self.status_message = "Échec du téléchargement."

    @rx.event(background=True)
    async def run_forecast(self):
        async with self:
            if not self.uploaded_file_name:
                self.error_message = "Aucun fichier n'a été téléchargé pour la prévision."
                self.status_message = "Veuillez d'abord télécharger un fichier."
                self.is_processing = False
                return
            self.is_processing = True
            self.show_chart = False
            self.error_message = None
            self.status_message = "Traitement des données et entraînement du modèle..."
            self.forecast_chart_data = []
            self.raw_forecast_df_json = ""
        try:
            file_path = (
                rx.get_upload_dir()
                / self.uploaded_file_name
            )
            df = pd.read_excel(file_path, header=7)
            df.dropna(how="all", inplace=True)
            df["Flight DateTime"] = pd.to_datetime(
                df["Flight DateTime"]
            )
            df.set_index("Flight DateTime", inplace=True)
            df.sort_index(inplace=True)
            async with self:
                self.status_message = (
                    "Création des caractéristiques lag..."
                )
            for i in range(1, self.LAG_FEATURES + 1):
                df[f"lag_{i}"] = df["EGT Margin"].shift(i)
            feature_cols = [
                f"lag_{i}"
                for i in range(1, self.LAG_FEATURES + 1)
            ] + ["Vibration of the core", "CSN"]
            target_col = "EGT Margin"
            df_model = df[
                feature_cols + [target_col]
            ].copy()
            df_model.dropna(inplace=True)
            if df_model.empty:
                async with self:
                    self.error_message = "Pas assez de données après la préparation pour entraîner le modèle."
                    self.status_message = (
                        "Échec de la prévision."
                    )
                    self.is_processing = False
                return
            X = df_model[feature_cols]
            y = df_model[target_col]
            async with self:
                self.status_message = (
                    "Entraînement du modèle XGBoost..."
                )
            model = XGBRegressor(
                objective="reg:squarederror",
                n_estimators=100,
                random_state=42,
            )
            if not XGBOOST_AVAILABLE:
                await asyncio.sleep(2)
            model.fit(X, y)
            if not XGBOOST_AVAILABLE:
                await asyncio.sleep(1)
            async with self:
                self.status_message = (
                    "Génération des prévisions..."
                )
            last_known_data = df_model.iloc[-1]
            last_date = df_model.index[-1]
            current_lags = last_known_data[
                feature_cols[: self.LAG_FEATURES]
            ].values.tolist()
            current_vibration = last_known_data[
                "Vibration of the core"
            ]
            current_csn = last_known_data["CSN"]
            predictions = []
            future_dates = []
            for i in range(self.FORECAST_CYCLES):
                input_features = np.array(
                    current_lags
                    + [current_vibration, current_csn]
                ).reshape(1, -1)
                forecast_value = model.predict(
                    input_features
                )[0]
                predictions.append(forecast_value)
                future_date = last_date + timedelta(
                    days=i + 1
                )
                future_dates.append(future_date)
                current_lags.pop(0)
                current_lags.append(forecast_value)
                current_csn += 1
            forecast_df = pd.DataFrame(
                {
                    "Date": future_dates,
                    "EGT Margin Forecast (XGBoost)": predictions,
                }
            )
            chart_data_list = []
            for _, row in forecast_df.iterrows():
                chart_data_list.append(
                    {
                        "date": row["Date"].strftime(
                            "%Y-%m-%d"
                        ),
                        "EGT Margin Forecast (XGBoost)": round(
                            row[
                                "EGT Margin Forecast (XGBoost)"
                            ],
                            2,
                        ),
                    }
                )
            async with self:
                self.forecast_chart_data = chart_data_list
                self.raw_forecast_df_json = (
                    forecast_df.to_json(
                        orient="records", date_format="iso"
                    )
                )
                self.show_chart = True
                self.status_message = (
                    "Prévision terminée avec succès."
                )
                self.error_message = None
                if not XGBOOST_AVAILABLE:
                    self.status_message += " (Utilisation d'un modèle factice car XGBoost n'est pas installé)."
        except FileNotFoundError:
            async with self:
                self.error_message = f"Fichier '{self.uploaded_file_name}' non trouvé. Veuillez le télécharger à nouveau."
                self.status_message = (
                    "Échec de la prévision."
                )
        except KeyError as e:
            async with self:
                self.error_message = f"Colonne manquante dans le fichier Excel: {str(e)}. Vérifiez les en-têtes à la ligne 8."
                self.status_message = (
                    "Échec de la prévision."
                )
        except Exception as e:
            import traceback

            tb_str = traceback.format_exc()
            async with self:
                self.error_message = f"Une erreur est survenue: {str(e)}\n{tb_str}"
                self.status_message = (
                    "Échec de la prévision."
                )
        finally:
            async with self:
                self.is_processing = False

    @rx.var
    def can_download(self) -> bool:
        return bool(self.raw_forecast_df_json) and (
            not self.is_processing
        )

    def download_excel(self):
        if not self.raw_forecast_df_json:
            return rx.toast(
                "Aucune donnée de prévision à télécharger.",
                duration=3000,
            )
        try:
            forecast_df = pd.read_json(
                self.raw_forecast_df_json, orient="records"
            )
            if "Date" in forecast_df.columns and (
                not pd.api.types.is_datetime64_any_dtype(
                    forecast_df["Date"]
                )
            ):
                forecast_df["Date"] = pd.to_datetime(
                    forecast_df["Date"]
                )
            if "Date" in forecast_df.columns:
                forecast_df["Date"] = forecast_df[
                    "Date"
                ].dt.strftime("%Y-%m-%d")
            output = io.BytesIO()
            with pd.ExcelWriter(
                output, engine="openpyxl"
            ) as writer:
                forecast_df.to_excel(
                    writer,
                    index=False,
                    sheet_name="Forecast",
                )
            file_name = f"EGT_Margin_Forecast_{self.uploaded_file_name.split('.')[0]}_{self.FORECAST_CYCLES}_Cycles.xlsx"
            return rx.download(
                data=output.getvalue(), filename=file_name
            )
        except Exception as e:
            self.error_message = f"Erreur lors de la création du fichier Excel: {str(e)}"
            return rx.toast(
                f"Erreur Excel: {str(e)}", duration=5000
            )