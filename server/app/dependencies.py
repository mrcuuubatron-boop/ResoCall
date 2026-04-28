from app.config import Settings, get_settings
from app.services.database import Database
from app.services.storage import Storage
from app.services.task_manager import TaskManager


class AppContext:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.storage = Storage(settings)
        self.db = Database(postgres_dsn=settings.postgres_dsn)
        self.tasks = TaskManager(max_workers=settings.max_workers)
        self._pipeline = None

    def get_pipeline(self):
        if self._pipeline is None:
            from app.services.audio_pipeline import PipelineConfig, ProcessingPipeline

            self._pipeline = ProcessingPipeline(
                PipelineConfig(
                    sample_rate=16000,
                    asr_model=self.settings.asr_model,
                    denoise=self.settings.denoise,
                    use_external_asr_module=self.settings.external_asr_module,
                    external_asr_module_path=str(self.settings.external_asr_module_path),
                )
            )
        return self._pipeline


def build_context() -> AppContext:
    settings = get_settings()
    return AppContext(settings)
