"""main routes"""

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

# routers
from src.routes.conversations import router as conversations_router
from src.routes.session import router as session_router
from src.routes.interviewer import router as interviewer_router
from src.routes.coach import router as coach_router


app = FastAPI()

origins = [
    "http://localhost:3000",
    "https://discnet.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    conversations_router,
    prefix="/conversations",
    tags=["Interview Conversations"],
)
app.include_router(session_router, prefix="/sessions", tags=["Sessions"])
app.include_router(interviewer_router, prefix="/interviewer", tags=["Interviewer"])
app.include_router(coach_router, prefix="/coach", tags=["Coach"])
