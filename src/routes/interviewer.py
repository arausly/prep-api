"""Routes for interview questions"""

import asyncio
from crewai import Agent, Task, Crew
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from src.libs.supabase_client import supabase
from src.constants.tables import Table
from src.libs.load_yaml import load_yaml_with_vars
from src.configs.typing import InterviewerType
from src.libs.helper import get_formatted_messages


router = APIRouter()


@router.post("")
async def get_interview_question(session_id: str):
    """Generates interview questions with or without context"""
    try:
        interview_session_response, conversations_response = await asyncio.gather(
            asyncio.to_thread(
                lambda: supabase.table(Table.interview_session)
                .select()
                .eq("id", session_id)
                .execute()
            ),
            asyncio.to_thread(
                lambda: supabase.table(Table.interview_conversations)
                .select()
                .eq("session", session_id)
                .execute()
            ),
        )
        if interview_session_response.data is None:
            raise HTTPException(status_code=404, detail="Invalid session")
        interview_session = interview_session_response.data[0]
        conversations = conversations_response.data

        first_question = (
            "Hello! I'm your interviewer and I'll be conducting your interview for"
            f"the {interview_session.get("job_position")} position."
            "Let's start with a simple question:"
            "Can you tell me a bit about yourself and why you're interested in this role?"
        )

        question = first_question

        if len(conversations):
            # load yaml
            agents = load_yaml_with_vars(
                "src/configs/agents.yaml",
                company=interview_session.get("company"),
                job_position=interview_session.get("job_position"),
                job_description=interview_session.get("job_description"),
            )

            tasks = load_yaml_with_vars(
                "src/configs/tasks.yaml",
                context=get_formatted_messages(
                    conversations
                ),  # remove extra information to reduce tokens
                job_position=interview_session.get("job_position"),
                job_description=interview_session.get("job_description"),
                question="",
                answer="",
            )

            agent_dict = {k: v for k, v in agents["agents"][0].items() if k != "name"}
            interviewer_agent = Agent(**agent_dict)
            task_dict = {
                **{k: v for k, v in tasks["tasks"][0].items() if k != "name"},
                "agent": interviewer_agent,
            }
            interviewer_task = Task(**task_dict)
            crew = Crew(agents=[interviewer_agent], tasks=[interviewer_task])
            question = crew.kickoff()

        # save question to session
        response = (
            supabase.table(Table.interview_conversations)
            .insert(
                {
                    "session": session_id,
                    "content": str(question),
                    "type": InterviewerType.INTERVIEWER,
                }
            )
            .execute()
        )

        if response.data is None or not bool(len(response.data)):
            raise HTTPException(status_code=500, detail="Could not save conversations")

        return JSONResponse(
            status_code=200, content={"messages": [*conversations, *response.data]}
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Something unexpected happened: {str(e)}"
        ) from e
