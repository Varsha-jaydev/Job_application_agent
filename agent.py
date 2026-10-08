
from crewai import Agent, Crew, Process, Task, LLM
from pydantic import BaseModel, Field
from typing import List


# =========================================================
# Structured output models
# =========================================================

class InterviewQuestion(BaseModel):
    question: str
    why_they_ask: str
    answer_framework: str


class ApplicationPackage(BaseModel):
    cover_letter: str

    resume_bullets: List[str] = Field(
        description="Five tailored resume bullet points"
    )

    behavioral_questions: List[InterviewQuestion] = Field(
        description="Five behavioral interview questions"
    )

    technical_questions: List[InterviewQuestion] = Field(
        description="Five technical interview questions"
    )

    negotiation_range: str

    negotiation_notes: List[str]

    application_strategy: List[str]


# =========================================================
# Main CrewAI function
# =========================================================

def create_application(
    job_description: str,
    candidate_profile: str,
) -> ApplicationPackage:

    # -----------------------------------------------------
    # Ollama configuration
    # -----------------------------------------------------

    # Check available models with:
    #
    #     ollama list
    #
    # Change this if you use another model.

    llm = LLM(
        model="ollama/qwen3:8b",
        base_url="http://localhost:11434",
        temperature=0.4,
    )

    # -----------------------------------------------------
    # Agent 1: Job Analyst
    # -----------------------------------------------------

    analyst = Agent(
        role="Job Requirements Analyst",

        goal=(
            "Analyze the job description and identify the most "
            "important requirements, keywords, technical skills, "
            "soft skills, and hiring priorities."
        ),

        backstory=(
            "You are an experienced technical recruiter and hiring "
            "manager. You understand how to read job descriptions "
            "and identify what employers actually care about."
        ),

        llm=llm,
        verbose=False,
    )

    # -----------------------------------------------------
    # Agent 2: Career Coach
    # -----------------------------------------------------

    writer = Agent(
        role="Career Coach and Application Writer",

        goal=(
            "Create highly targeted, professional and truthful "
            "job application materials based on the candidate's "
            "actual experience."
        ),

        backstory=(
            "You are an experienced technology career coach who "
            "specializes in resumes, cover letters and technical "
            "interview preparation."
        ),

        llm=llm,
        verbose=False,
    )

    # -----------------------------------------------------
    # Task 1: Analyze job
    # -----------------------------------------------------

    analysis_task = Task(
        description=f"""
Analyze the following job description.

================ JOB DESCRIPTION ================

{job_description}

===================================================

Identify:

1. The five most important requirements
2. Technical skills required
3. Soft skills required
4. Important responsibilities
5. Company/culture signals
6. Important keywords
7. Likely interview focus areas
8. Which candidate experiences should be emphasized
""",

        agent=analyst,

        expected_output=(
            "A structured analysis of the job requirements, "
            "keywords, responsibilities and hiring priorities."
        ),
    )

    # -----------------------------------------------------
    # Task 2: Generate application
    # -----------------------------------------------------

    application_task = Task(
        description=f"""
Create a complete tailored job application package.

================ CANDIDATE =======================

{candidate_profile}

===================================================

IMPORTANT RULES:

- Only use information actually provided about the candidate.
- Never invent experience.
- Never invent employers.
- Never invent skills.
- Never invent achievements.
- Never invent metrics.
- Never claim the candidate has used a technology unless it
  appears in the candidate profile.
- Tailor everything to the specific job.

Create:

---------------------------------------------------
COVER LETTER
---------------------------------------------------

Write a professional 250-300 word cover letter.

Use:
1. Strong opening
2. Relevant candidate evidence
3. Specific connection to the role
4. Professional closing


---------------------------------------------------
RESUME BULLETS
---------------------------------------------------

Create exactly 5 tailored resume bullets.

Prioritize measurable achievements where available.


---------------------------------------------------
BEHAVIORAL INTERVIEW
---------------------------------------------------

Create exactly 5 behavioral interview questions.

For each provide:

- question
- why_they_ask
- answer_framework


---------------------------------------------------
TECHNICAL INTERVIEW
---------------------------------------------------

Create exactly 5 technical/job-specific interview questions.

For each provide:

- question
- why_they_ask
- answer_framework


---------------------------------------------------
NEGOTIATION
---------------------------------------------------

Provide:

- estimated compensation range
- several negotiation notes

This is an estimate only.


---------------------------------------------------
APPLICATION STRATEGY
---------------------------------------------------

Provide 3-5 specific recommendations for how the
candidate should position themselves for this job.

The final answer MUST conform to the requested structured
output format.
""",

        agent=writer,

        expected_output=(
            "A structured application package containing "
            "cover letter, five resume bullets, five behavioral "
            "questions, five technical questions, negotiation "
            "information and application strategy."
        ),

        context=[analysis_task],

        output_pydantic=ApplicationPackage,
    )

    # -----------------------------------------------------
    # Run Crew
    # -----------------------------------------------------

    crew = Crew(
        agents=[
            analyst,
            writer,
        ],

        tasks=[
            analysis_task,
            application_task,
        ],

        process=Process.sequential,

        verbose=False,
    )

    result = crew.kickoff()

    # CrewAI returns the Pydantic object through pydantic
    if result.pydantic:
        return result.pydantic

    raise RuntimeError(
        "CrewAI did not return structured application data."
    )