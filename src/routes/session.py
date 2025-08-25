"""Routes for interview sessions"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from pydantic import BaseModel
from src.libs.supabase_client import supabase
from src.constants.tables import Table

router = APIRouter()


class Session(BaseModel):
    """Interview session model"""

    job_position: str
    company: str
    job_description: str


@router.post("")
def create_session(interview_session: Session):
    """Create new session"""
    try:
        response = (
            supabase.table(Table.interview_session)
            .insert(interview_session.model_dump())
            .execute()
        )
        if response.data is None or not bool(len(response.data)):
            raise HTTPException(status_code=500, detail="Failed to create session")
        # create default interviewer message
        interviewer_response = (
            supabase.table(Table.interview_conversations)
            .insert(
                {
                    "session_id": response.data[0]["id"],
                    "type": "interviewer",
                    "content": (
                        "Hello! I'm your interviewer and I'll be conducting your interview"
                        f"for the {interview_session.job_position}"
                        f"position at {interview_session.company}.",
                        "Let's start with a simple question: Can you tell me a"
                        "bit about yourself and why you're interested in this role?",
                    ),
                }
            )
            .execute()
        )
        if interviewer_response.data is None or not bool(
            len(interviewer_response.data)
        ):
            raise HTTPException(
                status_code=500, detail="Failed to create default interviewer message"
            )
        return JSONResponse(
            status_code=201,
            content={"message": "session created", "session": response.data[0]},
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error creating session: {str(e)}"
        ) from e


@router.get("/{session_id}")
def get_session(session_id: str):
    """Get session by ID"""
    try:
        response = (
            supabase.table(Table.interview_session)
            .select("*")
            .eq("id", session_id)
            .execute()
        )
        if response.data is None or not bool(len(response.data)):
            raise HTTPException(status_code=404, detail="Session not found")
        return JSONResponse(
            status_code=200,
            content={"message": "session fetched", "session": response.data[0]},
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error fetching session: {str(e)}"
        ) from e
