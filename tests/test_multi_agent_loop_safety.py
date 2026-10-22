from app.services.multi_agent_graph import search_agent_node
from app.services.supervisor_agent import choose_next_agent


def empty_search_state():
    return {
        "user_request": "Python FastAPI RAG developer",
        "jd_text": "Python FastAPI RAG",
        "target_count": 2,
        "current_task": "",
        "last_agent": "",
        "candidates": [],
        "screened_candidates": [],
        "matched_candidates": [],
        "shortlisted_candidates": [],
        "next_agent": "",
        "workflow_complete": False,
        "stop_reason": "",
        "search_attempts": 0,
        "max_search_attempts": 3,
        "last_search_error": "",
    }


def test_empty_search_retries_until_limit():
    state = empty_search_state()

    assert choose_next_agent(state) == "SEARCH"

    state["search_attempts"] = 2
    assert choose_next_agent(state) == "SEARCH"

    state["search_attempts"] = 3
    assert choose_next_agent(state) == "END"


def test_search_exception_is_recorded_and_bounded(monkeypatch):
    import app.services.multi_agent_graph as graph_module

    def fail_search(**kwargs):
        raise RuntimeError("simulated search outage")

    monkeypatch.setattr(
        graph_module,
        "search_recruitos",
        fail_search,
    )
    monkeypatch.setattr(
        graph_module,
        "get_required_skill_experience",
        lambda jd: {},
    )

    state = empty_search_state()
    result = search_agent_node(state)

    assert result["candidates"] == []
    assert result["search_attempts"] == 1
    assert "simulated search outage" in result["last_search_error"]
    assert choose_next_agent(result) == "SEARCH"

    result["search_attempts"] = 3
    assert choose_next_agent(result) == "END"


def test_successful_search_clears_previous_error(monkeypatch):
    import app.services.multi_agent_graph as graph_module

    monkeypatch.setattr(
        graph_module,
        "get_required_skill_experience",
        lambda jd: {},
    )
    monkeypatch.setattr(
        graph_module,
        "search_recruitos",
        lambda **kwargs: [{"candidate_id": "candidate_001"}],
    )

    state = empty_search_state()
    state["last_search_error"] = "previous failure"

    result = search_agent_node(state)

    assert len(result["candidates"]) == 1
    assert result["last_search_error"] == ""
    assert result["search_attempts"] == 1


def test_compiled_graph_stops_after_repeated_skill_extraction_failures(
    monkeypatch,
):
    import app.services.multi_agent_graph as graph_module

    def fail_skill_extraction(jd):
        raise RuntimeError("simulated skill extraction failure")

    monkeypatch.setattr(
        graph_module,
        "get_required_skill_experience",
        fail_skill_extraction,
    )

    state = empty_search_state()
    state["max_search_attempts"] = 2

    result = graph_module.build_multi_agent_graph().invoke(state)

    assert result["search_attempts"] == 2
    assert result["candidates"] == []
    assert "simulated skill extraction failure" in (
        result["last_search_error"]
    )
    assert result["workflow_complete"] is True
    assert result["stop_reason"] == "SEARCH_ATTEMPTS_EXHAUSTED"

def test_screening_continues_after_one_candidate_fails(monkeypatch):
    import app.services.multi_agent_graph as graph_module

    def screen(candidate, jd_text, resume_text=None):
        if candidate["candidate_id"] == "bad":
            raise RuntimeError("simulated screening failure")
        return {
            "qualified": True,
            "final_score": 90,
            "candidate_id": candidate["candidate_id"],
        }

    monkeypatch.setattr(graph_module, "check_candidate", screen)

    state = empty_search_state()
    state["candidates"] = [
        {"candidate_id": "bad", "resume_text": "bad resume"},
        {"candidate_id": "good", "resume_text": "good resume"},
    ]

    result = graph_module.screening_agent_node(state)

    assert result["screening_completed"] is True
    assert [c["candidate_id"] for c in result["screened_candidates"]] == ["good"]
    assert "simulated screening failure" in result["last_screening_error"]
    assert result["stop_reason"] == "SCREENING_PARTIAL_FAILURE"
    assert choose_next_agent(result) == "MATCHING"


def test_all_screening_failures_stop_compiled_graph(monkeypatch):
    import app.services.multi_agent_graph as graph_module

    monkeypatch.setattr(
        graph_module, "get_required_skill_experience", lambda jd: {}
    )
    monkeypatch.setattr(
        graph_module,
        "search_recruitos",
        lambda **kwargs: [
            {"candidate_id": "bad1", "resume_text": "resume 1"},
            {"candidate_id": "bad2", "resume_text": "resume 2"},
        ],
    )

    def fail_screening(*args, **kwargs):
        raise RuntimeError("screening service unavailable")

    monkeypatch.setattr(graph_module, "check_candidate", fail_screening)

    result = graph_module.build_multi_agent_graph().invoke(empty_search_state())

    assert result["screening_completed"] is True
    assert result["screened_candidates"] == []
    assert result["workflow_complete"] is True
    assert result["stop_reason"] == "SCREENING_FAILED"
    assert "screening service unavailable" in result["last_screening_error"]


def test_ranking_exception_terminates_workflow(monkeypatch):
    import app.services.multi_agent_graph as graph_module

    monkeypatch.setattr(
        graph_module,
        "rank_candidates",
        lambda results: (_ for _ in ()).throw(
            RuntimeError("simulated ranking failure")
        ),
    )

    state = empty_search_state()
    state["candidates"] = [{"candidate_id": "candidate_001"}]
    state["screened_candidates"] = [
        {"candidate_id": "candidate_001", "qualified": True, "final_score": 80}
    ]
    state["screening_completed"] = True

    result = graph_module.matching_agent_node(state)

    assert result["workflow_complete"] is True
    assert result["matching_completed"] is False
    assert result["matched_candidates"] == []
    assert result["shortlisted_candidates"] == []
    assert result["stop_reason"] == "MATCHING_FAILED"
    assert "simulated ranking failure" in result["last_matching_error"]
    assert choose_next_agent(result) == "END"


def test_empty_screening_result_routes_to_matching_when_completed():
    state = empty_search_state()
    state["candidates"] = [{"candidate_id": "candidate_001"}]
    state["screening_completed"] = True
    state["screened_candidates"] = []

    assert choose_next_agent(state) == "MATCHING"
