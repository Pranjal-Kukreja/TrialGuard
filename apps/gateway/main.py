import os
import sys
from pathlib import Path

# Add gateway directory and repo root to sys.path
GATEWAY_DIR = Path(__file__).resolve().parent
REPO_ROOT = GATEWAY_DIR.parent.parent
for p in [str(GATEWAY_DIR), str(REPO_ROOT)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from fastapi.middleware.cors import CORSMiddleware
from routers import extraction, orchestrator
from a2a_server import router as a2a_router
from fastapi import FastAPI
from dotenv import load_dotenv

load_dotenv()
app = FastAPI(title="TechQuest Gateway")
app.include_router(extraction.router)
app.include_router(orchestrator.router)
app.include_router(a2a_router)



app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://techquest-roan.vercel.app",
        "https://techquest-roan.vercel.app:3000",
        "https://techquest-roan.vercel.app:8000",
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
    ],
    allow_origin_regex=r"https://.*\.vercel\.app|http://localhost:\d+|http://127\.0\.0\.1:\d+",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def load_env_file(path: Path) -> None:
    if not path.is_file():
        return

    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
            value = value[1:-1]
        os.environ.setdefault(key.strip(), value)


load_env_file(Path(__file__).parents[2] / ".env")
load_env_file(Path(__file__).with_name(".env"))


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("GATEWAY_PORT", 8000))
    print(f"--> TechQuest Gateway starting on http://0.0.0.0:{port}")
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)