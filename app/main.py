"""Local UNSTUCK application; only the static directory is public."""
from pathlib import Path
from typing import Annotated, Literal
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator
from .ai import GenerationError, PriorityContext, Step, generate_step

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env", override=False)
app = FastAPI(title="UNSTUCK", docs_url=None, redoc_url=None, openapi_url=None)
app.mount("/static", StaticFiles(directory=ROOT / "static"), name="static")


class StepRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    thoughts: str = Field(min_length=1, max_length=2000)
    previous_action: str | None = Field(default=None, min_length=1, max_length=500)
    completed_actions: list[Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=500)]] = Field(default_factory=list, max_length=100)
    mode: Literal["suggest", "retry", "continue"] = "suggest"
    priority_context: PriorityContext | None = None

    @model_validator(mode="after")
    def validate_continuation(self):
        if self.mode == "continue" and (not self.completed_actions or self.previous_action != self.completed_actions[-1]):
            raise ValueError("Continue requires the latest completed action as context.")
        if self.priority_context:
            source = " ".join(self.thoughts.casefold().split())
            if " ".join(self.priority_context.task.casefold().split()) not in source or (
                self.priority_context.evidence and " ".join(self.priority_context.evidence.casefold().split()) not in source
            ):
                raise ValueError("Priority context must be grounded in the original thoughts.")
        return self


@app.get("/", include_in_schema=False)
async def index():
    return FileResponse(ROOT / "static" / "index.html")


@app.post("/api/step", response_model=Step)
async def step(payload: StepRequest):
    try:
        return await generate_step(payload.thoughts, payload.previous_action, payload.completed_actions, payload.mode, payload.priority_context)
    except GenerationError as exc:
        raise HTTPException(status_code=exc.status, detail=exc.message) from None
