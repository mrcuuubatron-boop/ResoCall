from app.config import Settings, get_settings
from app.services.audio_pipeline import PipelineConfig, ProcessingPipeline
from app.services.database import Database
from app.services.storage import Storage
from app.services.task_manager import TaskManager


class AppContext:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.storage = Storage(settings)
        self.db = Database(postgres_dsn=settings.postgres_dsn)
        self.tasks = TaskManager(max_workers=settings.max_workers)
        self.pipeline = ProcessingPipeline(
            PipelineConfig(
                sample_rate=16000,
                asr_model=settings.asr_model,
                denoise=settings.denoise,
                use_external_asr_module=settings.external_asr_module,
                external_asr_module_path=str(settings.external_asr_module_path),
            )
        )


def build_context() -> AppContext:
    settings = get_settings()
    return AppContext(settings)
