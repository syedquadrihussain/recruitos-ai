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

    # -----------------------------------------------------
    # WORKFLOW CONTROL
    # -----------------------------------------------------

    next_agent: str
    workflow_complete: bool
    stop_reason: str