import re


def parse_jd(jd_text):

    jd = {
        "must_have": {},
        "nice_to_have": set(),
        "skill_weights": {}
    }

    skills = [
        "Python",
        "FastAPI",
        "RAG",
        "Docker",
        "Java",
        ".NET",
        "SAP",
        "AWS",
        "React",
        "SQL"
    ]

    # --------------------------------
    # 1. Find Must-Have section
    # --------------------------------

    must_have_match = re.search(
        r"Must\s*Have\s*:(.*?)(?=Nice\s*to\s*Have\s*:|$)",
        jd_text,
        re.IGNORECASE | re.DOTALL
    )

    must_have_text = ""

    if must_have_match:
        must_have_text = must_have_match.group(1)

    # --------------------------------
    # 2. Find Nice-to-Have section
    # --------------------------------

    nice_to_have_match = re.search(
        r"Nice\s*to\s*Have\s*:(.*?)(?=$)",
        jd_text,
        re.IGNORECASE | re.DOTALL
    )

    nice_to_have_text = ""

    if nice_to_have_match:
        nice_to_have_text = nice_to_have_match.group(1)

    # --------------------------------
    # 3. Process Must-Have skills
    # --------------------------------

    for skill in skills:

        if skill.lower() in must_have_text.lower():

            pattern = rf"{re.escape(skill)}\s*(?:-|:)?\s*(\d+)\+?\s*years?"

            match = re.search(
                pattern,
                must_have_text,
                re.IGNORECASE
            )

            if match:

                required_years = int(match.group(1))

                jd["must_have"][skill] = required_years

            else:

                jd["must_have"][skill] = 0

            jd["skill_weights"][skill] = 3

    # --------------------------------
    # 4. Process Nice-to-Have skills
    # --------------------------------

    for skill in skills:

        if skill.lower() in nice_to_have_text.lower():

            jd["nice_to_have"].add(skill)

            jd["skill_weights"][skill] = 1

    return jd