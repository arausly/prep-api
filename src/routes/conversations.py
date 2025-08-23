"""Routes for conversations"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from src.libs.supabase_client import supabase

from src.constants.tables import Table

router = APIRouter()


@router.get("/{session_id}")
def get_conversations(session_id: str):
    """Get all conversations for session id provided"""
    try:
        response = (
            supabase.table(Table.interview_conversations)
            .select()
            .eq("session", session_id)
            .execute()
        )
        return JSONResponse(
            status_code=200,
            content={
                "conversations": list() if response.data is None else response.data
            },
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error fetching items: {str(e)}"
        ) from e
