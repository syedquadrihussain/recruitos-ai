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

    # Find skills
    for skill in skills_to_find:
        if skill.lower() in text_lower:
            candidate["skills"].append(skill)

    # Find overall experience
    overall_patterns = [
        r"(\d+)\+?\s*years?\s+of\s+experience",
        r"(\d+)\+?\s*years?\s+of\s+.*?experience"
    ]

    for pattern in overall_patterns:
        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:
            candidate["overall_experience"] = int(
                match.group(1)
            )
            break

    # Find roles
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

    # Find companies
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

    # Find individual skill experience
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

        patterns = [

            # Example: Python: 6 years
            rf"{re.escape(skill)}\s*[:\-]\s*(\d+)\+?\s*years?",

            # Example: 6 years of Python experience
            rf"(\d+)\+?\s*years?\s+of\s+{re.escape(skill)}\s+experience",

            # Example: Python Developer with 6 years of Python experience
            rf"{re.escape(skill)}\s+\w+\s+with\s+(\d+)\+?\s*years?\s+of\s+{re.escape(skill)}\s+experience",

            # Example: FastAPI 2 years
            rf"{re.escape(skill)}\s+(\d+)\+?\s*years?"
        ]

        for pattern in patterns:

            match = re.search(
                pattern,
                text,
                re.IGNORECASE
            )

            if match:
                candidate["experience"][skill] = int(
                    match.group(1)
                )
                break

    return candidate