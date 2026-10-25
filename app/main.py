"""Local UNSTUCK application; only the static directory is public."""
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, Field
from .ai import GenerationError, Step, generate_step

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env", override=False)
app = FastAPI(title="UNSTUCK", docs_url=None, redoc_url=None, openapi_url=None)
app.mount("/static", StaticFiles(directory=ROOT / "static"), name="static")


class StepRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    thoughts: str = Field(min_length=1, max_length=2000)
    previous_action: str | None = Field(default=None, min_length=1, max_length=500)


@app.get("/", include_in_schema=False)
async def index():
    return FileResponse(ROOT / "static" / "index.html")


@app.post("/api/step", response_model=Step)
async def step(payload: StepRequest):
    try:
        return await generate_step(payload.thoughts, payload.previous_action)
    except GenerationError as exc:
        raise HTTPException(status_code=exc.status, detail=exc.message) from None
