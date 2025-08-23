"""Typings shared for agents and tasks"""

from enum import Enum


class InterviewerType(str, Enum):
    """interviewer types"""

    CANDIDATE = "candidate"
    COACH = "coach"
    INTERVIEWER = "interviewer"
