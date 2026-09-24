from unittest.mock import MagicMock, patch
from django.test import TestCase, override_settings
from django.contrib.auth.models import User
from reports.models import Department, Issue, IssueAIAnalysis
from reports.services.ai_service import CivicAIService, AIStructuredResponse, AIAnalysisResult


class AIServiceUnitTests(TestCase):
    """
    Unit tests for CivicAIService and Gemini integration (using mocks).
    """

    def setUp(self):
        self.road_dept = Department.objects.create(
            name="Roads Department",
            description="Road repair, asphalt, potholes, and flyovers."
        )
        self.water_dept = Department.objects.create(
            name="Water Department",
            description="Water supply pipelines, leakage, and public taps."
        )
        self.cleaning_dept = Department.objects.create(
            name="Cleaning Department",
            description="Sanitation, waste management, and garbage collection."
        )

        self.departments_list = [
            {"id": self.road_dept.id, "name": self.road_dept.name, "description": self.road_dept.description},
            {"id": self.water_dept.id, "name": self.water_dept.name, "description": self.water_dept.description},
            {"id": self.cleaning_dept.id, "name": self.cleaning_dept.name, "description": self.cleaning_dept.description},
        ]

    def test_disabled_ai_service(self):
        """When AI_ENABLED is False, service returns clean fallback."""
        with override_settings(AI_ENABLED=False):
            service = CivicAIService(api_key="fake-key")
            result = service.analyze_issue(
                title="Pothole on Main St",
                description="Deep hole damaging vehicles",
                departments=self.departments_list,
            )
            self.assertFalse(result.is_successful)
            self.assertIn("disabled", result.error_message.lower())

    def test_missing_api_key(self):
        """When GEMINI_API_KEY is empty, service returns clean fallback."""
        with override_settings(GEMINI_API_KEY="", AI_ENABLED=True):
            service = CivicAIService(api_key="")
            result = service.analyze_issue(
                title="Pothole on Main St",
                description="Deep hole damaging vehicles",
                departments=self.departments_list,
            )
            self.assertFalse(result.is_successful)
            self.assertIn("not configured", result.error_message.lower())

    def test_successful_classification_and_image_validation(self):
        """When Gemini returns structured JSON, service parses it accurately."""
        service = CivicAIService(api_key="fake-key", model_name="gemini-3.8-flash")

        mock_parsed = AIStructuredResponse(
            department_id=self.road_dept.id,
            department_name=self.road_dept.name,
            department_confidence=0.92,
            department_reasoning="Report mentions deep pothole on road which falls under Roads Department.",
            is_image_relevant=True,
            image_confidence=0.95,
            image_explanation="Photo clearly shows cracked asphalt and road crater.",
            detected_problem="road pothole",
        )

        mock_response = MagicMock()
        mock_response.parsed = mock_parsed

        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = mock_response

        with patch.object(service, "get_client", return_value=mock_client):
            result = service.analyze_issue(
                title="Pothole on 5th Ave",
                description="Large dangerous pothole",
                departments=self.departments_list,
            )

            self.assertTrue(result.is_successful)
            self.assertEqual(result.department_id, self.road_dept.id)
            self.assertEqual(result.department_name, "Roads Department")
            self.assertAlmostEqual(result.department_confidence, 0.92)
            self.assertTrue(result.is_image_relevant)
            self.assertAlmostEqual(result.image_confidence, 0.95)
            self.assertEqual(result.detected_problem, "road pothole")
            self.assertEqual(result.model_name, "gemini-3.8-flash")

    def test_hallucinated_department_id_rejected(self):
        """If AI returns an ID not present in provided departments, it is rejected safely."""
        service = CivicAIService(api_key="fake-key")

        mock_parsed = AIStructuredResponse(
            department_id=99999,  # Non-existent ID
            department_name="Space Exploration Department",
            department_confidence=0.85,
            department_reasoning="Fell from the sky.",
            is_image_relevant=True,
            image_confidence=0.80,
            image_explanation="Looks strange.",
            detected_problem="meteorite",
        )

        mock_response = MagicMock()
        mock_response.parsed = mock_parsed

        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = mock_response

        with patch.object(service, "get_client", return_value=mock_client):
            result = service.analyze_issue(
                title="Unknown object in park",
                description="Strange object",
                departments=self.departments_list,
            )

            self.assertTrue(result.is_successful)
            # Must reject hallucinated department ID
            self.assertIsNone(result.department_id)
            self.assertIsNone(result.department_name)

    def test_gemini_api_exception_handling(self):
        """When Gemini API throws an exception (e.g. timeout, quota, auth), service does not crash."""
        service = CivicAIService(api_key="fake-key")

        mock_client = MagicMock()
        mock_client.models.generate_content.side_effect = RuntimeError("API rate limit exceeded (429)")

        with patch.object(service, "get_client", return_value=mock_client):
            result = service.analyze_issue(
                title="Garbage pile",
                description="Overflowing bins",
                departments=self.departments_list,
            )

            self.assertFalse(result.is_successful)
            self.assertIn("API rate limit exceeded", result.error_message)


class IssueAIAnalysisModelTests(TestCase):
    """
    Tests for the IssueAIAnalysis model.
    """

    def setUp(self):
        self.user = User.objects.create_user(username="citizen1", password="password123")
        self.dept = Department.objects.create(name="Electricity Department", description="Power lines & lamps")
        self.issue = Issue.objects.create(
            user=self.user,
            title="Broken street lamp",
            description="Dark street at night",
            location="Market Street",
            status="REPORTED"
        )

    def test_create_issue_ai_analysis_record(self):
        analysis = IssueAIAnalysis.objects.create(
            issue=self.issue,
            suggested_department=self.dept,
            department_confidence=0.88,
            department_reasoning="Electricity department handles broken street lights.",
            is_image_relevant=True,
            image_confidence=0.91,
            image_explanation="Photo shows an unlit lamp post.",
            detected_problem="broken lamp post",
            model_name="gemini-3.8-flash",
            is_successful=True,
        )

        self.assertEqual(analysis.issue, self.issue)
        self.assertEqual(self.issue.ai_analysis, analysis)
        self.assertEqual(analysis.suggested_department, self.dept)
        self.assertIn("Electricity Department", str(analysis))
        self.assertIn("88%", str(analysis))

