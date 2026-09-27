from unittest.mock import MagicMock, patch

from django.contrib.auth.models import User
from django.test import TestCase, override_settings

from reports.models import Department, Issue, IssueAIAnalysis
from reports.services.ai_service import analyze_issue


class AIServiceTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="test_citizen",
            password="testpassword123",
        )

        self.road_dept = Department.objects.create(
            name="Roads Department",
            description="Road repair, asphalt, potholes, and flyovers.",
        )

        self.water_dept = Department.objects.create(
            name="Water Department",
            description="Water supply pipelines, leakage, and public taps.",
        )

        self.issue = Issue.objects.create(
            user=self.user,
            title="Large pothole",
            description="A large pothole is damaging vehicles.",
            location="Main Street",
            status="REPORTED",
        )

    @override_settings(AI_ENABLED=False)
    def test_ai_disabled(self):
        result = analyze_issue(self.issue)

        self.assertIsNone(result)

        self.assertFalse(
            IssueAIAnalysis.objects.filter(issue=self.issue).exists()
        )

    @override_settings(
        AI_ENABLED=True,
        GEMINI_API_KEY="",
    )
    def test_missing_api_key(self):
        result = analyze_issue(self.issue)

        self.assertIsNotNone(result)
        self.assertFalse(result.is_successful)

        self.assertIn(
            "not configured",
            result.error_message.lower(),
        )

    @override_settings(
        AI_ENABLED=True,
        GEMINI_API_KEY="fake-key",
        AI_MODEL="gemini-3.6-flash",
    )
    @patch("reports.services.ai_service.get_gemini_client")
    def test_successful_ai_analysis(self, mock_get_client):

        mock_client = MagicMock()

        mock_response = MagicMock()

        mock_response.text = """
        {
            "department_id": %d,
            "department_confidence": 0.92,
            "department_reasoning": "The complaint describes a pothole.",
            "is_image_relevant": false,
            "image_confidence": 0.95,
            "image_explanation": "No image was provided.",
            "detected_problem": "road pothole"
        }
        """ % self.road_dept.id

        mock_client.models.generate_content.return_value = mock_response

        mock_get_client.return_value = mock_client

        result = analyze_issue(self.issue)

        self.assertIsNotNone(result)
        self.assertTrue(result.is_successful)

        self.assertEqual(
            result.suggested_department,
            self.road_dept,
        )

        self.assertAlmostEqual(
            result.department_confidence,
            0.92,
        )

        self.assertFalse(
            result.is_image_relevant
        )

        self.assertEqual(
            result.detected_problem,
            "road pothole",
        )

        self.assertEqual(
            result.model_name,
            "gemini-3.6-flash",
        )

    @override_settings(
        AI_ENABLED=True,
        GEMINI_API_KEY="fake-key",
    )
    @patch("reports.services.ai_service.get_gemini_client")
    def test_invalid_department_is_rejected(self, mock_get_client):

        mock_client = MagicMock()

        mock_response = MagicMock()

        mock_response.text = """
        {
            "department_id": 99999,
            "department_confidence": 0.90,
            "department_reasoning": "Invalid department.",
            "is_image_relevant": false,
            "image_confidence": 0.50,
            "image_explanation": "Unknown.",
            "detected_problem": "unknown"
        }
        """

        mock_client.models.generate_content.return_value = mock_response

        mock_get_client.return_value = mock_client

        result = analyze_issue(self.issue)

        self.assertFalse(result.is_successful)

        self.assertIsNone(
            result.suggested_department
        )

        self.assertIn(
            "invalid department",
            result.error_message.lower(),
        )

    @override_settings(
        AI_ENABLED=True,
        GEMINI_API_KEY="fake-key",
    )
    @patch("reports.services.ai_service.get_gemini_client")
    def test_gemini_exception_is_handled(self, mock_get_client):

        mock_client = MagicMock()

        mock_client.models.generate_content.side_effect = RuntimeError(
            "API rate limit exceeded"
        )

        mock_get_client.return_value = mock_client

        result = analyze_issue(self.issue)

        self.assertFalse(result.is_successful)

        self.assertIn(
            "API rate limit exceeded",
            result.error_message,
        )


class IssueAIAnalysisModelTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="citizen1",
            password="password123",
        )

        self.dept = Department.objects.create(
            name="Electricity Department",
            description="Power lines and street lamps",
        )

        self.issue = Issue.objects.create(
            user=self.user,
            title="Broken street lamp",
            description="Dark street at night",
            location="Market Street",
            status="REPORTED",
        )

    def test_create_issue_ai_analysis_record(self):

        analysis = IssueAIAnalysis.objects.create(
            issue=self.issue,
            suggested_department=self.dept,
            department_confidence=0.88,
            department_reasoning=(
                "Electricity department handles broken street lights."
            ),
            is_image_relevant=True,
            image_confidence=0.91,
            image_explanation=(
                "Photo shows an unlit lamp post."
            ),
            detected_problem="broken lamp post",
            model_name="gemini-3.6-flash",
            is_successful=True,
        )

        self.assertEqual(
            analysis.issue,
            self.issue,
        )

        self.assertEqual(
            self.issue.ai_analysis,
            analysis,
        )

        self.assertEqual(
            analysis.suggested_department,
            self.dept,
        )

        self.assertIn(
            "Electricity Department",
            str(analysis),
        )

        self.assertIn(
            "88%",
            str(analysis),
        )