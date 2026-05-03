import logging
import time
from dataclasses import dataclass, field
from abc import ABC, abstractmethod

log = logging.getLogger(__name__)

@dataclass
class PipelineContext:
    manuscript_path: str
    config: dict = field(default_factory=dict)
    data: dict = field(default_factory=dict)
    errors: list = field(default_factory=list)
    recommendation: str = ""

class PipelineStep(ABC):
    name: str = "unnamed_step"

    @abstractmethod
    def run(self, ctx: PipelineContext) -> PipelineContext: ...

    def should_run(self, ctx: PipelineContext) -> bool:
        return True

class PipelineRunner:
    def __init__(self, steps: list[PipelineStep]):
        self.steps = steps

    def run(self, manuscript_path: str, config: dict = None) -> PipelineContext:
        ctx = PipelineContext(manuscript_path=manuscript_path, config=config or {})
        log.info(f"Pipeline start: {manuscript_path}")

        for step in self.steps:
            if not step.should_run(ctx):
                log.info(f"[SKIP] {step.name}")
                continue
            log.info(f"[RUN]  {step.name}")
            t0 = time.time()
            try:
                ctx = step.run(ctx)
            except Exception as e:
                log.error(f"[FAIL] {step.name}: {e}")
                ctx.errors.append({"step": step.name, "error": str(e)})
                break
            finally:
                log.info(f"[DONE] {step.name} ({time.time()-t0:.2f}s)")

        return ctx
