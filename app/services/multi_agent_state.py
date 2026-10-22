from typing import TypedDict


class MultiAgentState(TypedDict):
    """
    Shared state for the RecruitOS Multi-Agent workflow.

    The Supervisor and specialist agents use this state
    to communicate with each other.
    """

    # -----------------------------------------------------
    # RECRUITER REQUEST
    # -----------------------------------------------------

    user_request: str

    # -----------------------------------------------------
    # JOB DESCRIPTION
    # -----------------------------------------------------

    jd_text: str

    # -----------------------------------------------------
    # RECRUITMENT TARGET
    # -----------------------------------------------------

    target_count: int

    # -----------------------------------------------------
    # CURRENT WORKFLOW TASK
    # -----------------------------------------------------

    current_task: str

    # -----------------------------------------------------
    # LAST AGENT THAT EXECUTED
    # -----------------------------------------------------

    last_agent: str

    # -----------------------------------------------------
    # CANDIDATE DATA
    # -----------------------------------------------------

    candidates: list
    screened_candidates: list
    matched_candidates: list
    shortlisted_candidates: list

    # -----------------------------------------------------
    # WORKFLOW CONTROL
    # -----------------------------------------------------

    next_agent: str
    workflow_complete: bool
    stop_reason: str
    search_attempts: int
    max_search_attempts: int
    last_search_error: str
    screening_completed: bool
    matching_completed: bool
    last_screening_error: str
    last_matching_error: str