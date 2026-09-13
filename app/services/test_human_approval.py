from app.services.human_approval import get_recruiter_approval


candidate_result = {
    "name": "Syed Hussain BDM",
    "final_score": 95.4,
    "qualified": True,
    "recommendation": "Strong Match"
}


result = get_recruiter_approval(candidate_result)


print("\nRecruiter Decision:")
print(result)