
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime, timezone


# =========================================================
# 1. FASTAPI CONFIGURATION
# =========================================================

app = FastAPI(title="ATS Testing Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# 2. RECRUITMENT POSTS DATA
# Matches recruitment_posts:
# post_id, job_title, job_description
# =========================================================

jobs = [
    {
        "post_id": "JOB001",
        "job_title": "Python Developer",
        "job_description": (
            "Python developer with experience in FastAPI, SQL and REST APIs."
        )
    },
    {
        "post_id": "JOB002",
        "job_title": "AI/ML Engineer",
        "job_description": (
            "AI/ML engineer with Python, NLP and machine learning experience."
        )
    },
    {
        "post_id": "JOB003",
        "job_title": "Data Analyst",
        "job_description": (
            "Data analyst with SQL, Excel and Power BI experience."
        )
    }
]


# =========================================================
# 3. RECRUITMENT METADATA DATA
# Matches recruitment_metadata
# =========================================================

metadata = {
    "JOB001": {
        "metadata_id": 1,
        "post_id": "JOB001",
        "form_id": "FORM001",
        "form_url": "https://forms.google.com/python-developer",
        "image_urls": [],
        "created_at": "2026-11-10T10:00:00+00:00",
        "updated_at": "2026-11-10T10:00:00+00:00"
    },

    "JOB002": {
        "metadata_id": 2,
        "post_id": "JOB002",
        "form_id": "FORM002",
        "form_url": "https://forms.google.com/ai-ml-engineer",
        "image_urls": [],
        "created_at": "2026-11-11T10:00:00+00:00",
        "updated_at": "2026-11-11T10:00:00+00:00"
    },

    "JOB003": {
        "metadata_id": 3,
        "post_id": "JOB003",
        "form_id": "FORM003",
        "form_url": "https://forms.google.com/data-analyst",
        "image_urls": [],
        "created_at": "2026-11-12T10:00:00+00:00",
        "updated_at": "2026-11-12T10:00:00+00:00"
    }
}


# =========================================================
# 4. RECRUITMENT APPLICATION DATA
# Matches recruitment_data, including candidate_score
# =========================================================

applications = {
    "JOB001": [
        {
            "application_id": 101,
            "post_id": "JOB001",
            "full_name": "Aarav Sharma",
            "email": "aarav@example.com",
            "phone": "9876543210",
            "resume_file": None,
            "resume_filename": "aarav_resume.pdf",
            "resume_content_type": "application/pdf",
            "additional_data": {},
            "submitted_at": "2026-11-10T11:00:00+00:00",
            "candidate_score": 92.00
        },
        {
            "application_id": 102,
            "post_id": "JOB001",
            "full_name": "Riya Verma",
            "email": "riya@example.com",
            "phone": "9876543211",
            "resume_file": None,
            "resume_filename": "riya_resume.pdf",
            "resume_content_type": "application/pdf",
            "additional_data": {},
            "submitted_at": "2026-11-10T12:00:00+00:00",
            "candidate_score": 85.00
        },
        {
            "application_id": 103,
            "post_id": "JOB001",
            "full_name": "Kabir Singh",
            "email": "kabir@example.com",
            "phone": "9876543212",
            "resume_file": None,
            "resume_filename": "kabir_resume.pdf",
            "resume_content_type": "application/pdf",
            "additional_data": {},
            "submitted_at": "2026-11-10T13:00:00+00:00",
            "candidate_score": 76.00
        }
    ],

    "JOB002": [
        {
            "application_id": 201,
            "post_id": "JOB002",
            "full_name": "Ananya Gupta",
            "email": "ananya@example.com",
            "phone": "9876543213",
            "resume_file": None,
            "resume_filename": "ananya_resume.pdf",
            "resume_content_type": "application/pdf",
            "additional_data": {},
            "submitted_at": "2026-11-11T11:00:00+00:00",
            "candidate_score": 96.00
        },
        {
            "application_id": 202,
            "post_id": "JOB002",
            "full_name": "Dev Patel",
            "email": "dev@example.com",
            "phone": "9876543214",
            "resume_file": None,
            "resume_filename": "dev_resume.pdf",
            "resume_content_type": "application/pdf",
            "additional_data": {},
            "submitted_at": "2026-11-11T12:00:00+00:00",
            "candidate_score": 88.00
        }
    ],

    "JOB003": [
        {
            "application_id": 301,
            "post_id": "JOB003",
            "full_name": "Ishita Rao",
            "email": "ishita@example.com",
            "phone": "9876543215",
            "resume_file": None,
            "resume_filename": "ishita_resume.pdf",
            "resume_content_type": "application/pdf",
            "additional_data": {},
            "submitted_at": "2026-11-12T11:00:00+00:00",
            "candidate_score": 91.00
        }
    ]
}


# =========================================================
# 5. APPLICATION REQUEST MODEL
# =========================================================

class ApplicationRequest(BaseModel):

    full_name: str
    email: str
    phone: Optional[str] = None

    resume_file: Optional[bytes] = None
    resume_filename: Optional[str] = None
    resume_content_type: Optional[str] = None

    resume_text: Optional[str] = None

    additional_data: Dict[str, Any] = Field(default_factory=dict)


# =========================================================
# 6. CANDIDATE EVALUATION
# =========================================================

def evaluate_candidate(
    resume_text: Optional[str],
    job_description: str
):
    """
    Temporary testing evaluation.

    This is not an actual AI evaluation.
    A real AI model must be connected before generating
    genuine candidate match scores.
    """

    return {
        "candidate_score": None
    }


# =========================================================
# 7. HOME ENDPOINT
# =========================================================

@app.get("/")
def home():

    return {
        "message": "ATS testing backend is running"
    }


# =========================================================
# 8. DASHBOARD ENDPOINT
# =========================================================

@app.get("/api/ats/dashboard")
def get_dashboard():

    combined_jobs = []

    for job in jobs:

        post_id = job["post_id"]

        job_metadata = metadata.get(post_id, {})

        combined_job = {
            **job,
            **job_metadata
        }

        combined_jobs.append(combined_job)

    total_applicants = sum(
        len(job_applications)
        for job_applications in applications.values()
    )

    return {
        "jobs": combined_jobs,
        "total_jobs": len(jobs),
        "total_applicants": total_applicants
    }


# =========================================================
# 9. GET CANDIDATE APPLICATIONS
# =========================================================

@app.get("/api/ats/jobs/{post_id}/applications")
def get_applications(post_id: str):

    selected_job = next(
        (
            job for job in jobs
            if job["post_id"] == post_id
        ),
        None
    )

    if selected_job is None:

        raise HTTPException(
            status_code=404,
            detail="Job posting not found"
        )

    return {
        "post_id": post_id,
        "applications": applications.get(post_id, [])
    }


# =========================================================
# 10. SUBMIT NEW CANDIDATE APPLICATION
# =========================================================

@app.post("/api/ats/jobs/{post_id}/applications")
def submit_application(
    post_id: str,
    request: ApplicationRequest
):

    selected_job = next(
        (
            job for job in jobs
            if job["post_id"] == post_id
        ),
        None
    )

    if selected_job is None:

        raise HTTPException(
            status_code=404,
            detail="Job posting not found"
        )

    evaluation = evaluate_candidate(
        request.resume_text,
        selected_job["job_description"]
    )

    next_application_id = max(
        (
            application["application_id"]
            for job_applications in applications.values()
            for application in job_applications
        ),
        default=0
    ) + 1

    submitted_at = datetime.now(timezone.utc).isoformat()

    new_application = {
        "application_id": next_application_id,
        "post_id": post_id,
        "full_name": request.full_name,
        "email": request.email,
        "phone": request.phone,
        "resume_file": request.resume_file,
        "resume_filename": request.resume_filename,
        "resume_content_type": request.resume_content_type,
        "additional_data": request.additional_data,
        "submitted_at": submitted_at,
        "candidate_score": evaluation["candidate_score"]
    }

    applications.setdefault(post_id, []).append(new_application)

    # Do not return raw binary resume_file in the JSON response.
    response_application = {
        key: value
        for key, value in new_application.items()
        if key != "resume_file"
    }

    return {
        "message": "Application submitted successfully",
        "application": response_application
    }
