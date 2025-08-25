"""Coach routes to hep=lp improve users responses per interview questions"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from crewai import Agent, Task, Crew

from src.libs.supabase_client import supabase
from src.constants.tables import Table
from src.libs.load_yaml import load_yaml_with_vars
from src.configs.typing import InterviewerType
from src.libs.helper import get_formatted_messages


router = APIRouter()


class CoachFeedbackRequest(BaseModel):
    """Request model for coach feedback"""

    session_id: str
    candidate_answer: str
    interview_question: str


@router.post("")
async def get_coach_feedback(payload: CoachFeedbackRequest):
    """Generates coaching feedback based on the last interview question and answer"""
    if not payload.session_id or not payload.candidate_answer:
        raise HTTPException(status_code=400, detail="Missing required parameters")
    try:
        session_response = (
            supabase.table(Table.interview_session)
            .select()
            .eq("id", payload.session_id)
            .execute()
        )
        if session_response.data is None:
            raise HTTPException(status_code=404, detail="Invalid session")
        session = session_response.data[0]
        conversations_response = (
            supabase.table(Table.interview_conversations)
            .select()
            .eq("session", session.get("id"))
            .execute()
        )
        conversations = (
            conversations_response.data
            if conversations_response.data is not None
            else []
        )
        # load yaml
        agents = load_yaml_with_vars(
            "src/configs/agents.yaml",
            company=session.get("company"),
            job_position=session.get("job_position"),
            job_description=session.get("job_description"),
        )

        tasks = load_yaml_with_vars(
            "src/configs/tasks.yaml",
            context=get_formatted_messages(
                conversations
            ),  # remove extra information to reduce tokens
            job_position=session.get("job_position"),
            job_description="",  # not needed here but keeping for consistency
            question=payload.interview_question,
            answer=payload.candidate_answer,
        )

        agent_dict = {k: v for k, v in agents["agents"][1].items() if k != "name"}
        coach_agent = Agent(**agent_dict)
        task_dict = {
            **{k: v for k, v in tasks["tasks"][1].items() if k != "name"},
            "agent": coach_agent,
        }
        interviewer_task = Task(**task_dict)
        crew = Crew(agents=[coach_agent], tasks=[interviewer_task])
        suggestion = crew.kickoff()

        # save suggestion to session
        suggestion_save_response = (
            supabase.table(Table.interview_conversations)
            .insert(
                [
                    {
                        "session": payload.session_id,
                        "content": payload.candidate_answer,
                        "type": InterviewerType.CANDIDATE,
                    },
                    {
                        "session": payload.session_id,
                        "content": str(suggestion),
                        "type": InterviewerType.COACH,
                    },
                ]
            )
            .execute()
        )

        if suggestion_save_response.data is None:
            raise HTTPException(status_code=500, detail="Could not save conversation")

        return JSONResponse(
            status_code=200,
            content={"messages": [*conversations, *suggestion_save_response.data]},
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error generating feedback: {str(e)}"
        ) from e
