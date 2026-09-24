import json
import logging
from pathlib import Path

from django.conf import settings

from google import genai
from google.genai import types

from reports.models import Department, Issue, IssueAIAnalysis

logger = logging.getLogger(__name__)


def get_gemini_client():
    api_key = getattr(settings, "GEMINI_API_KEY", "")

    if not api_key:
        raise ValueError("GEMINI_API_KEY is not configured.")

    return genai.Client(api_key=api_key)


def analyze_issue(issue: Issue):
    """
    Analyze a civic issue using Gemini.

    AI provides:
    1. Department recommendation
    2. Image relevance check

    AI NEVER automatically assigns the department.
    """

    if not getattr(settings, "AI_ENABLED", True):
        return None

    departments = list(
        Department.objects.all().values("id", "name")
    )

    if not departments:
        logger.warning("No departments available for AI classification.")
        return None

    department_text = "\n".join(
        f"- ID {department['id']}: {department['name']}"
        for department in departments
    )

    prompt = f"""
You are an AI assistant for a civic complaint management system.

Analyze the citizen's complaint and uploaded photograph.

Your tasks:

1. Recommend the most appropriate department.
2. Determine whether the uploaded photograph appears relevant
   to the reported civic problem.
3. Identify what problem appears to be shown in the photograph.

IMPORTANT RULES:

- You MUST select a department only from the provided list.
- NEVER invent a department.
- NEVER assign or modify the issue's department.
- The department recommendation is only a suggestion for a corporation employee.
- Give department confidence between 0 and 1.
- Give image relevance confidence between 0 and 1.
- If the image does not clearly show the reported problem,
  mark image relevance as false.
- Do not claim certainty when the photograph is unclear.
- Return ONLY valid JSON.

AVAILABLE DEPARTMENTS:

{department_text}

CITIZEN REPORT

Title:
{issue.title}

Description:
{issue.description}

Return exactly this JSON structure:

{{
    "department_id": 1,
    "department_confidence": 0.90,
    "department_reasoning": "Brief explanation",
    "is_image_relevant": true,
    "image_confidence": 0.90,
    "image_explanation": "Brief explanation of whether the image matches the report",
    "detected_problem": "Problem visible in the image"
}}
"""

    try:
        client = get_gemini_client()

        contents = [prompt]

        # ---------------------------------------------------------
        # ADD IMAGE IF ONE WAS UPLOADED
        # ---------------------------------------------------------
        if issue.image_before:
            try:
                image_path = Path(issue.image_before.path)

                if image_path.exists():
                    image_bytes = image_path.read_bytes()

                    image_part = types.Part.from_bytes(
                        data=image_bytes,
                        mime_type=issue.image_before.file.content_type
                        if hasattr(issue.image_before.file, "content_type")
                        else "image/jpeg",
                    )

                    contents.append(image_part)

            except Exception as image_error:
                logger.warning(
                    "Could not load image for issue %s: %s",
                    issue.id,
                    image_error,
                )

        response = client.models.generate_content(
            model=getattr(
                settings,
                "AI_MODEL",
                "gemini-3.6-flash",
            ),
            contents=contents,
            config=types.GenerateContentConfig(
                temperature=0.1,
                response_mime_type="application/json",
            ),
        )

        raw_text = response.text or ""

        data = json.loads(raw_text)

        # ---------------------------------------------------------
        # VALIDATE DEPARTMENT
        # ---------------------------------------------------------

        department_id = data.get("department_id")

        valid_department_ids = {
            department["id"]
            for department in departments
        }

        if department_id not in valid_department_ids:
            raise ValueError(
                f"AI returned invalid department ID: {department_id}"
            )

        department = Department.objects.get(id=department_id)

        # ---------------------------------------------------------
        # NORMALIZE VALUES
        # ---------------------------------------------------------

        department_confidence = float(
            data.get("department_confidence", 0)
        )

        image_confidence = float(
            data.get("image_confidence", 0)
        )

        department_confidence = max(
            0.0,
            min(1.0, department_confidence)
        )

        image_confidence = max(
            0.0,
            min(1.0, image_confidence)
        )

        # ---------------------------------------------------------
        # SAVE AI ANALYSIS
        # ---------------------------------------------------------

        analysis, _ = IssueAIAnalysis.objects.update_or_create(
            issue=issue,
            defaults={
                "suggested_department": department,

                "department_confidence": department_confidence,

                "department_reasoning": str(
                    data.get("department_reasoning", "")
                ),

                "is_image_relevant": data.get(
                    "is_image_relevant"
                ),

                "image_confidence": image_confidence,

                "image_explanation": str(
                    data.get("image_explanation", "")
                ),

                "detected_problem": str(
                    data.get("detected_problem", "")
                ),

                "model_name": getattr(
                    settings,
                    "AI_MODEL",
                    "gemini-3.6-flash",
                ),

                "raw_response": data,

                "is_successful": True,

                "error_message": "",
            },
        )

        return analysis

    except Exception as exc:

        logger.exception(
            "AI analysis failed for issue %s",
            issue.id,
        )

        analysis, _ = IssueAIAnalysis.objects.update_or_create(
            issue=issue,

            defaults={
                "suggested_department": None,

                "department_confidence": None,

                "department_reasoning": "",

                "is_image_relevant": None,

                "image_confidence": None,

                "image_explanation": "",

                "detected_problem": "",

                "model_name": getattr(
                    settings,
                    "AI_MODEL",
                    "gemini-3.6-flash",
                ),

                "raw_response": None,

                "is_successful": False,

                "error_message": str(exc),
            },
        )

        return analysis