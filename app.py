
import streamlit as st

from agent import create_application


# =========================================================
# Page configuration
# =========================================================

st.set_page_config(
    page_title="Job Application Agent",
    page_icon="💼",
    layout="wide",
)


# =========================================================
# Header
# =========================================================

st.title("💼 Job Application Agent")

st.caption(
    "Tailor your job application using CrewAI + Ollama"
)


# =========================================================
# Sidebar
# =========================================================

with st.sidebar:

    st.header("⚙️ Settings")

    st.success("🟢 Local AI")

    st.markdown(
        """
        **LLM:** Ollama  
        **Agent framework:** CrewAI  
        **Model:** Qwen 3  
        **Server:** localhost:11434
        """
    )

    st.divider()

    st.markdown(
        """
        ### How it works

        1. Enter your candidate profile
        2. Paste a job description
        3. Click Generate
        4. Review your tailored application
        """
    )


# =========================================================
# Input section
# =========================================================

left, right = st.columns(2)


with left:

    st.subheader("👤 Candidate Profile")

    candidate_profile = st.text_area(
        "Your experience",
        height=400,

        placeholder="""Example:

Jane Doe
Senior Software Engineer

7 years Python experience.

Skills:
- Python
- FastAPI
- Django
- PostgreSQL
- Redis
- Docker
- Kubernetes
- AWS

Achievements:
- Built API platform handling 5M requests/day
- Led team of 4 engineers
- Reduced API latency by 40%
- Mentored 3 junior engineers

Education:
BS Computer Science
""",
    )


with right:

    st.subheader("💼 Job Description")

    job_description = st.text_area(
        "Paste the job description",
        height=400,

        placeholder="""Paste the complete job description here.

Example:

Senior Python Engineer

We're looking for a Senior Python Engineer
to join our API Platform team.

Requirements:
- 5+ years Python
- Distributed systems
- REST APIs
- PostgreSQL
- Redis
- Kubernetes

Responsibilities:
- Build high-performance APIs
- Lead technical design reviews
- Mentor engineers
""",
    )


# =========================================================
# Generate
# =========================================================

st.divider()

generate = st.button(
    "🚀 Generate Application",
    type="primary",
    use_container_width=True,
)


if generate:

    if not candidate_profile.strip():

        st.error("Please enter your candidate profile.")

        st.stop()

    if not job_description.strip():

        st.error("Please enter a job description.")

        st.stop()

    # -----------------------------------------------------
    # Generate
    # -----------------------------------------------------

    with st.spinner(
        "🤖 Analyzing job and generating your application..."
    ):

        try:

            application = create_application(
                job_description=job_description,
                candidate_profile=candidate_profile,
            )

            st.session_state["application"] = application

        except Exception as e:

            st.error(
                "Unable to generate the application."
            )

            st.exception(e)


# =========================================================
# Results
# =========================================================

if "application" in st.session_state:

    application = st.session_state["application"]

    st.divider()

    st.header("📋 Your Application Package")

    # -----------------------------------------------------
    # Tabs
    # -----------------------------------------------------

    (
        cover_tab,
        resume_tab,
        interview_tab,
        salary_tab,
        strategy_tab,
    ) = st.tabs(
        [
            "📄 Cover Letter",
            "📋 Resume",
            "🎤 Interview",
            "💰 Negotiation",
            "🎯 Strategy",
        ]
    )

    # =====================================================
    # Cover Letter
    # =====================================================

    with cover_tab:

        st.subheader("Cover Letter")

        st.text_area(
            "Generated cover letter",
            value=application.cover_letter,
            height=500,
            label_visibility="collapsed",
        )

        st.download_button(
            "⬇️ Download Cover Letter",
            data=application.cover_letter,
            file_name="cover_letter.txt",
            mime="text/plain",
        )

    # =====================================================
    # Resume
    # =====================================================

    with resume_tab:

        st.subheader("Resume Bullets")

        st.caption(
            "These are the five experiences the AI recommends "
            "highlighting for this particular job."
        )

        resume_text = ""

        for i, bullet in enumerate(
            application.resume_bullets,
            start=1,
        ):

            st.markdown(
                f"**{i}.** {bullet}"
            )

            resume_text += f"• {bullet}\n"

        st.download_button(
            "⬇️ Download Resume Bullets",
            data=resume_text,
            file_name="resume_bullets.txt",
            mime="text/plain",
        )

    # =====================================================
    # Interview
    # =====================================================

    with interview_tab:

        st.subheader("Behavioral Questions")

        for i, item in enumerate(
            application.behavioral_questions,
            start=1,
        ):

            with st.expander(
                f"{i}. {item.question}"
            ):

                st.markdown(
                    "**Why they may ask:**"
                )

                st.write(
                    item.why_they_ask
                )

                st.markdown(
                    "**Suggested answer framework:**"
                )

                st.write(
                    item.answer_framework
                )

        st.divider()

        st.subheader("Technical Questions")

        for i, item in enumerate(
            application.technical_questions,
            start=1,
        ):

            with st.expander(
                f"{i}. {item.question}"
            ):

                st.markdown(
                    "**Why they may ask:**"
                )

                st.write(
                    item.why_they_ask
                )

                st.markdown(
                    "**Suggested answer framework:**"
                )

                st.write(
                    item.answer_framework
                )

    # =====================================================
    # Negotiation
    # =====================================================

    with salary_tab:

        st.subheader(
            "💰 Estimated Compensation"
        )

        st.info(
            application.negotiation_range
        )

        st.subheader(
            "Negotiation Notes"
        )

        for note in application.negotiation_notes:

            st.markdown(
                f"• {note}"
            )

        st.warning(
            "Compensation is an AI-generated estimate, not "
            "verified salary-market data."
        )

    # =====================================================
    # Strategy
    # =====================================================

    with strategy_tab:

        st.subheader(
            "🎯 Application Strategy"
        )

        for i, recommendation in enumerate(
            application.application_strategy,
            start=1,
        ):

            st.markdown(
                f"**{i}.** {recommendation}"
            )

    # =====================================================
    # Download complete package
    # =====================================================

    st.divider()

    complete_package = f"""
JOB APPLICATION PACKAGE
=======================

COVER LETTER
------------

{application.cover_letter}


RESUME BULLETS
--------------

""" + "\n".join(
        f"• {bullet}"
        for bullet in application.resume_bullets
    ) + """


BEHAVIORAL INTERVIEW QUESTIONS
------------------------------

""" + "\n\n".join(
        f"""
{i}. {item.question}

Why they may ask:
{item.why_they_ask}

Answer framework:
{item.answer_framework}
"""
        for i, item in enumerate(
            application.behavioral_questions,
            start=1,
        )
    ) + """


TECHNICAL INTERVIEW QUESTIONS
-----------------------------

""" + "\n\n".join(
        f"""
{i}. {item.question}

Why they may ask:
{item.why_they_ask}

Answer framework:
{item.answer_framework}
"""
        for i, item in enumerate(
            application.technical_questions,
            start=1,
        )
    ) + f"""


NEGOTIATION
-----------

Estimated range:
{application.negotiation_range}


Negotiation notes:

""" + "\n".join(
        f"• {note}"
        for note in application.negotiation_notes
    ) + """


APPLICATION STRATEGY
--------------------

""" + "\n".join(
        f"{i}. {strategy}"
        for i, strategy in enumerate(
            application.application_strategy,
            start=1,
        )
    )

    st.download_button(
        "📦 Download Complete Application Package",
        data=complete_package,
        file_name="application_package.txt",
        mime="text/plain",
        type="primary",
        use_container_width=True,
    )
