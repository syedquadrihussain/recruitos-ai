import re


def parse_jd(jd_text):
    """
    Parse a job description into:

    - must_have: mandatory skills and required experience
    - nice_to_have: preferred skills
    - skill_weights: scoring weights

    Supports:

    1. Structured JDs

       Must Have:
       Python - 5 years
       FastAPI 3 years
       RAG: 2 years

       Required Skills:
       Python - 5 years
       FastAPI - 2 years
       RAG - 2 years

       Nice to Have:
       Docker

    2. Normal recruiter-style JDs

       We are looking for a Python Developer
       with experience in Python, RAG and FastAPI.

       The candidate should have strong experience
       working with GenAI technologies.
    """

    jd = {
        "must_have": {},
        "nice_to_have": {},
        "skill_weights": {}
    }

    # --------------------------------
    # 1. Split JD into sections
    # --------------------------------

    must_have_section = ""
    nice_to_have_section = ""

    # --------------------------------
    # 1A. Detect Must Have section
    # --------------------------------

    must_have_match = re.search(
        r"(?:Must\s*Have|Required\s*Skills?|"
        r"Mandatory\s*Skills?)"
        r"\s*:?(.*?)(?="
        r"Nice\s*to\s*Have\s*:|"
        r"Nice\s*to\s*Have|"
        r"Preferred\s*Skills?\s*:|"
        r"Preferred\s*Skills?|"
        r"$)",
        jd_text,
        re.IGNORECASE | re.DOTALL
    )

    # --------------------------------
    # 1B. Detect Nice to Have section
    # --------------------------------

    nice_to_have_match = re.search(
        r"(?:Nice\s*to\s*Have|"
        r"Preferred\s*Skills?)"
        r"\s*:?(.*)$",
        jd_text,
        re.IGNORECASE | re.DOTALL
    )

    if must_have_match:

        must_have_section = (
            must_have_match
            .group(1)
            .strip()
        )

    if nice_to_have_match:

        nice_to_have_section = (
            nice_to_have_match
            .group(1)
            .strip()
        )

    # --------------------------------
    # 2. Known skills
    # --------------------------------
    #
    # Longer skill names are intentionally
    # checked before shorter names.
    #
    # Example:
    #
    # Business Development Manager
    #
    # should be detected before:
    #
    # Business Development

    known_skills = [
        "Business Development Manager",
        "Client Relationship Management",
        "Contract Negotiation",
        "Machine Learning",
        "Deep Learning",
        "Spring Boot",
        "IT Recruitment",
        "Talent Acquisition",
        "Lead Generation",
        "Team Leadership",
        "SAP Fieldglass",
        "Generative AI",
        "FastAPI",
        "LangChain",
        "LangGraph",
        "Kubernetes",
        "Python",
        "RAG",
        "Docker",
        "MCP",
        "GenAI",
        "SQL",
        "Java",
        "AWS",
        "Azure",
        "GCP",
        "Django",
        ".NET",
        "SAP",
        "Business Development",
        "ATS",
        "VMS",
        "MSP",
        "Ceipal",
        "Beeline"
    ]

    # Remove duplicates while preserving order.
    known_skills = list(
        dict.fromkeys(known_skills)
    )

    # --------------------------------
    # 3. Helper function
    # --------------------------------

    def skill_present(text, skill):

        return re.search(
            rf"\b{re.escape(skill)}\b",
            text,
            re.IGNORECASE
        ) is not None

    # --------------------------------
    # 4. Parse explicit Must Have section
    # --------------------------------

    if must_have_section:

        for skill in known_skills:

            if skill_present(
                must_have_section,
                skill
            ):

                jd["must_have"][skill] = 0

    # --------------------------------
    # 5. Parse explicit Nice to Have section
    # --------------------------------

    if nice_to_have_section:

        for skill in known_skills:

            if skill_present(
                nice_to_have_section,
                skill
            ):

                jd["nice_to_have"][skill] = 0

    # --------------------------------
    # 6. Remove overlapping shorter skills
    # --------------------------------
    #
    # Example:
    #
    # Business Development Manager
    # Business Development
    #
    # If the JD contains the longer skill,
    # we should not separately treat the
    # shorter phrase as another requirement.

    must_have_skills = list(
        jd["must_have"].keys()
    )

    for short_skill in list(
        jd["must_have"].keys()
    ):

        for long_skill in must_have_skills:

            if (
                short_skill != long_skill
                and len(long_skill) > len(short_skill)
                and short_skill.lower()
                in long_skill.lower()
            ):

                jd["must_have"].pop(
                    short_skill,
                    None
                )

                break

    # --------------------------------
    # 7. Parse normal recruiter-style
    #    requirement sentences
    # --------------------------------

    requirement_patterns = [
        r"experience[ \t]+(?:in|with)[ \t]+([^.!?\n]+)",
        r"experienced[ \t]+(?:in|with)[ \t]+([^.!?\n]+)",
        r"proficient[ \t]+(?:in|with)[ \t]+([^.!?\n]+)",
        r"expertise[ \t]+(?:in|with)[ \t]+([^.!?\n]+)",
        r"strong[ \t]+experience[ \t]+(?:in|with)[ \t]+([^.!?\n]+)",
        r"knowledge[ \t]+(?:of|in)[ \t]+([^.!?\n]+)",
        r"skills?[ \t]+(?:in|with)[ \t]+([^.!?\n]+)"
    ]

    requirement_texts = []

    for pattern in requirement_patterns:

        matches = re.findall(
            pattern,
            jd_text,
            re.IGNORECASE
        )

        requirement_texts.extend(
            matches
        )

    for requirement_text in requirement_texts:

        for skill in known_skills:

            if skill_present(
                requirement_text,
                skill
            ):

                if skill not in jd["nice_to_have"]:

                    jd["must_have"][skill] = (
                        jd["must_have"].get(
                            skill,
                            0
                        )
                    )

    # --------------------------------
    # 8. Detect skills in mandatory
    #    requirement lines
    # --------------------------------

    mandatory_keywords = [
        "required",
        "must have",
        "must-have",
        "should have",
        "need",
        "needs",
        "strong experience",
        "experience with",
        "experience in",
        "proficient",
        "expertise"
    ]

    for line in jd_text.splitlines():

        line_clean = line.strip()

        if not line_clean:
            continue

        line_lower = line_clean.lower()

        if any(
            keyword in line_lower
            for keyword in mandatory_keywords
        ):

            for skill in known_skills:

                if skill_present(
                    line_clean,
                    skill
                ):

                    if skill not in jd["nice_to_have"]:

                        jd["must_have"][skill] = (
                            jd["must_have"].get(
                                skill,
                                0
                            )
                        )

    # --------------------------------
    # 9. Extract experience requirements
    # --------------------------------
    #
    # Supported formats:
    #
    # Python - 5 years
    # Python: 5 years
    # Python 5 years
    # 5 years of Python experience
    # 5 years Python experience
    #
    # IMPORTANT:
    #
    # [ \t] is used instead of \s so
    # matching cannot cross newlines.

    for skill in list(
        jd["must_have"].keys()
    ):

        patterns = [

            # --------------------------------
            # Python - 5 years
            # Python: 5 years
            # --------------------------------

            rf"{re.escape(skill)}"
            rf"[ \t]*(?:-|:)[ \t]*"
            rf"(\d+)\+?[ \t]*years?",

            # --------------------------------
            # Python 5 years
            # --------------------------------

            rf"{re.escape(skill)}"
            rf"[ \t]+"
            rf"(\d+)\+?[ \t]*years?",

            # --------------------------------
            # 5 years of Python experience
            # --------------------------------

            rf"(\d+)\+?[ \t]*years?"
            rf"[ \t]+of[ \t]+"
            rf"{re.escape(skill)}"
            rf"(?:[ \t]+experience)?",

            # --------------------------------
            # 5 years Python experience
            # --------------------------------

            rf"(\d+)\+?[ \t]+"
            rf"{re.escape(skill)}"
            rf"(?:[ \t]+experience)?"
        ]

        for pattern in patterns:

            match = re.search(
                pattern,
                jd_text,
                re.IGNORECASE
            )

            if match:

                jd["must_have"][skill] = int(
                    match.group(1)
                )

                break

    # --------------------------------
    # 10. Line-level experience parsing
    # --------------------------------
    #
    # This gives structured JD lines
    # the highest confidence.
    #
    # Example:
    #
    # Python 5 years
    # FastAPI 3 years
    # RAG 2 years

    for line in jd_text.splitlines():

        line = line.strip()

        if not line:
            continue

        for skill in list(
            jd["must_have"].keys()
        ):

            patterns = [

                # Python - 5 years
                rf"\b{re.escape(skill)}\b"
                rf"[ \t]*(?:-|:)[ \t]*"
                rf"(\d+)\+?[ \t]*years?",

                # Python 5 years
                rf"\b{re.escape(skill)}\b"
                rf"[ \t]+"
                rf"(\d+)\+?[ \t]*years?"
            ]

            for pattern in patterns:

                match = re.search(
                    pattern,
                    line,
                    re.IGNORECASE
                )

                if match:

                    jd["must_have"][skill] = int(
                        match.group(1)
                    )

                    break

    # --------------------------------
    # 11. Create skill weights
    # --------------------------------

    for skill in jd["must_have"]:

        jd["skill_weights"][skill] = 3

    for skill in jd["nice_to_have"]:

        if skill not in jd["skill_weights"]:

            jd["skill_weights"][skill] = 1

    # --------------------------------
    # 12. Return parsed JD
    # --------------------------------

    return jd
def get_required_skill_experience(jd_text):
    """
    Return required skills and their minimum experience
    from the parsed job description.

    Example:
    {
        "Python": 5,
        "FastAPI": 2,
        "RAG": 2
    }
    """

    parsed_jd = parse_jd(jd_text)

    return {
        skill: experience
        for skill, experience
        in parsed_jd["must_have"].items()
    }