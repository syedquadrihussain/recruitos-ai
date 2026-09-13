def get_recruiter_approval(candidate_result):

    print("\n" + "=" * 60)
    print("RECRUITER APPROVAL REQUIRED")
    print("=" * 60)

    print(f"Candidate: {candidate_result['name']}")
    print(f"Final Score: {candidate_result['final_score']}")
    print(f"Qualified: {candidate_result['qualified']}")
    print(f"Recommendation: {candidate_result['recommendation']}")

    print("\nChoose an action:")
    print("1. Approve")
    print("2. Reject")
    print("3. Review")

    choice = input("\nEnter your choice: ").strip()

    if choice == "1":
        decision = "APPROVED"

    elif choice == "2":
        decision = "REJECTED"

    elif choice == "3":
        decision = "REVIEW"

    else:
        decision = "INVALID"

    return {
        "candidate": candidate_result["name"],
        "ai_recommendation": candidate_result["recommendation"],
        "final_score": candidate_result["final_score"],
        "qualified": candidate_result["qualified"],
        "recruiter_decision": decision
    }