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
        return JSONResponse(
            status_code=201,
            content={"message": "session created", "session": response.data[0]},
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error creating session: {str(e)}"
        ) from e
