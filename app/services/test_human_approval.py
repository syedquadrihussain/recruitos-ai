from app.services.human_approval import get_recruiter_approval


def test_recruiter_approval(monkeypatch):

    candidate_result = {
        "name": "Syed Hussain BDM",
        "final_score": 95.4,
        "qualified": True,
        "recommendation": "Strong Match"
    }

    # Simulate recruiter selecting "1 - Approve"
    monkeypatch.setattr(
        "builtins.input",
        lambda _: "1"
    )

    result = get_recruiter_approval(
        candidate_result
    )

    # Verify candidate information
    assert result["candidate"] == "Syed Hussain BDM"

    # Verify AI recommendation
    assert result["ai_recommendation"] == "Strong Match"

    # Verify score
    assert result["final_score"] == 95.4

    # Verify qualification
    assert result["qualified"] is True

    # Verify recruiter decision
    assert result["recruiter_decision"] == "APPROVED"