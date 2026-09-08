import re


def extract_candidate(text):

    candidate = {
        "name": "Unknown",
        "overall_experience": 0,
        "skills": [],
        "roles": [],
        "companies": [],
        "experience": {}
    }

    text_lower = text.lower()

    # --------------------------------
    # 1. Extract skills
    # --------------------------------

    skills_to_find = [
        "Python",
        "FastAPI",
        "RAG",
        "Docker",
        "Java",
        ".NET",
        "SAP",
        "IT Recruitment",
        "Talent Acquisition",
        "Business Development",
        "Client Relationship Management",
        "Lead Generation",
        "Contract Negotiation",
        "Team Leadership",
        "ATS",
        "VMS",
        "MSP",
        "Ceipal",
        "SAP Fieldglass",
        "Beeline"
    ]

    for skill in skills_to_find:

        if skill.lower() in text_lower:

            candidate["skills"].append(skill)

    # --------------------------------
    # 2. Extract overall experience
    # --------------------------------

    overall_experience_match = re.search(
        r"(\d+)\+?\s*years?\s+of\s+experience",
        text,
        re.IGNORECASE
    )

    if overall_experience_match:

        candidate["overall_experience"] = int(
            overall_experience_match.group(1)
        )

    # --------------------------------
    # 3. Extract roles
    # --------------------------------

    roles_to_find = [
        "Business Development Manager",
        "Lead Recruiter",
        "Accounts Manager",
        "Recruitment Account Manager",
        "Account Manager",
        "Technical Recruiter"
    ]

    for role in roles_to_find:

        if role.lower() in text_lower:

            candidate["roles"].append(role)

    # --------------------------------
    # 4. Extract companies
    # --------------------------------

    companies_to_find = [
        "Tek Wissen Software LLC",
        "Tachyon Technologies",
        "IPIVOT LLC",
        "Cloudgen",
        "IBASE IT",
        "MUTEX Systems"
    ]

    for company in companies_to_find:

        if company.lower() in text_lower:

            candidate["companies"].append(company)

    # --------------------------------
    # 5. Extract skill experience
    # --------------------------------

    skills_for_experience = [
        "Python",
        "FastAPI",
        "RAG",
        "Docker",
        "Java",
        ".NET",
        "SAP"
    ]

    for skill in skills_for_experience:

        pattern = rf"{re.escape(skill)}\s*[:\-]?\s*(\d+)\+?\s*years?"

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:

            candidate["experience"][skill] = int(
                match.group(1)
            )

    return candidate