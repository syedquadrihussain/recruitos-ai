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

    # --------------------------------------------------
    # Candidate Name
    # --------------------------------------------------

    name_patterns = [
        r"(?:Name|Candidate Name)\s*[:\-]\s*([A-Za-z]+(?:[ \t]+[A-Za-z]+){0,3})"
    ]

    for pattern in name_patterns:
        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:
            candidate["name"] = match.group(1).strip()
            break

    # --------------------------------------------------
    # Skills
    # --------------------------------------------------

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

    # --------------------------------------------------
    # Overall Experience
    # --------------------------------------------------

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

    # --------------------------------------------------
    # Roles
    # --------------------------------------------------

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

    # --------------------------------------------------
    # Companies
    # --------------------------------------------------

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

    # --------------------------------------------------
    # Skill Experience
    # --------------------------------------------------

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

            rf"{re.escape(skill)}\s*[:\-]\s*(\d+)\+?\s*years?",

            rf"(\d+)\+?\s*years?\s+of\s+{re.escape(skill)}\s+experience",

            rf"{re.escape(skill)}\s+\w+\s+with\s+(\d+)\+?\s*years?\s+of\s+{re.escape(skill)}\s+experience",

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

    # --------------------------------------------------
    # Business Development Manager Experience
    # --------------------------------------------------

    bd_patterns = [

        r"(\d+)\+?\s*years?\s+as\s+a\s+Business Development Manager",

        r"(\d+)\+?\s*years?\s+as\s+a\s+Business Development\s+Manager",

        r"including\s+(\d+)\+?\s*years?\s+as\s+a\s+Business Development Manager"
    ]

    for pattern in bd_patterns:

        bd_match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if bd_match:

            candidate["experience"][
                "Business Development Manager"
            ] = int(
                bd_match.group(1)
            )

            break

    return candidate