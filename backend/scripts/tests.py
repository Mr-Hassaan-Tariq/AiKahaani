from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from unittest.mock import patch, MagicMock
from io import BytesIO
from PIL import Image

from .models import Tone, TemplateStyle
from .serializers import GenerateOutlineRequestSerializer

User = get_user_model()


class GenerateOutlineRequestSerializerTest(TestCase):
    """Test the GenerateOutlineRequestSerializer with file uploads"""

    def setUp(self):
        self.tone = Tone.objects.create(name="Test Tone")
        self.template_style = TemplateStyle.objects.create(
            name="Test Style",
            min_length=100,
            max_length=1000,
            duration=60,
            description="Test description"
        )

    def create_test_image(self):
        """Create a test image file"""
        # Create a simple test image
        image = Image.new('RGB', (100, 100), color='red')
        image_io = BytesIO()
        image.save(image_io, format='JPEG')
        image_io.seek(0)
        
        return SimpleUploadedFile(
            name='test_image.jpg',
            content=image_io.getvalue(),
            content_type='image/jpeg'
        )

    def test_serializer_with_text_description(self):
        """Test serializer with text description"""
        data = {
            'description': 'Test description',
            'tones': [self.tone.id],
            'template_style': self.template_style.id,
            'min_length': 100,
            'max_length': 1000,
            'title': 'Test Title'
        }
        
        serializer = GenerateOutlineRequestSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['description'], 'Test description')

    def test_serializer_with_image_upload(self):
        """Test serializer with image upload"""
        test_image = self.create_test_image()
        
        data = {
            'tones': [self.tone.id],
            'template_style': self.template_style.id,
            'min_length': 100,
            'max_length': 1000,
            'image': test_image
        }
        
        serializer = GenerateOutlineRequestSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
        # Check that description and title are cleared when image is provided
        validated_data = serializer.validated_data
        self.assertEqual(validated_data['description'], '')
        self.assertEqual(validated_data['title'], '')
        self.assertIsNotNone(validated_data['image'])

    def test_serializer_validation_requires_description_or_image(self):
        """Test that serializer requires either description or image"""
        data = {
            'tones': [self.tone.id],
            'template_style': self.template_style.id,
            'min_length': 100,
            'max_length': 1000,
        }
        
        serializer = GenerateOutlineRequestSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)

    def test_serializer_image_overrides_text(self):
        """Test that image upload overrides text description and title"""
        test_image = self.create_test_image()
        
        data = {
            'description': 'This should be cleared',
            'title': 'This should also be cleared',
            'tones': [self.tone.id],
            'template_style': self.template_style.id,
            'min_length': 100,
            'max_length': 1000,
            'image': test_image
        }
        
        serializer = GenerateOutlineRequestSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
        # Check that description and title are cleared when image is provided
        validated_data = serializer.validated_data
        self.assertEqual(validated_data['description'], '')
        self.assertEqual(validated_data['title'], '')


class OutlineGenerationAPITest(APITestCase):
    """Test the outline generation API endpoint"""

    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            is_active=True
        )
        self.tone = Tone.objects.create(name="Test Tone")
        self.template_style = TemplateStyle.objects.create(
            name="Test Style",
            min_length=100,
            max_length=1000,
            duration=60,
            description="Test description"
        )
        
        # Mock authentication and subscription
        self.client.force_authenticate(user=self.user)

    def create_test_image(self):
        """Create a test image file"""
        image = Image.new('RGB', (100, 100), color='blue')
        image_io = BytesIO()
        image.save(image_io, format='JPEG')
        image_io.seek(0)
        
        return SimpleUploadedFile(
            name='test_image.jpg',
            content=image_io.getvalue(),
            content_type='image/jpeg'
        )

    @patch('scripts.services.open_ai.OpenAIScriptService.generate_outline')
    @patch('payments.permissions.HasActiveSubscriptionPermission.has_permission')
    def test_text_description_endpoint(self, mock_permission, mock_generate_outline):
        """Test the endpoint with text description"""
        mock_permission.return_value = True
        mock_generate_outline.return_value = (
            "Test outline text",
            {"sections": []},
            {"model": "gpt-4", "tokens_used": 100, "generation_time": 1.5}
        )
        
        data = {
            'description': 'Test description',
            'tones': [self.tone.id],
            'template_style': self.template_style.id,
            'min_length': 100,
            'max_length': 1000,
            'title': 'Test Title'
        }
        
        response = self.client.post('/api/v1/scripts/outline/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('outline', response.data)

    @patch('scripts.services.open_ai.OpenAIScriptService.analyze_image')
    @patch('scripts.services.open_ai.OpenAIScriptService.generate_outline')
    @patch('payments.permissions.HasActiveSubscriptionPermission.has_permission')
    def test_image_upload_endpoint(self, mock_permission, mock_generate_outline, mock_analyze_image):
        """Test the endpoint with image upload"""
        mock_permission.return_value = True
        mock_analyze_image.return_value = ("Generated Title", "Generated Description")
        mock_generate_outline.return_value = (
            "Test outline text",
            {"sections": []},
            {"model": "gpt-4", "tokens_used": 100, "generation_time": 1.5}
        )
        
        test_image = self.create_test_image()
        
        data = {
            'tones': [self.tone.id],
            'template_style': self.template_style.id,
            'min_length': 100,
            'max_length': 1000,
            'image': test_image
        }
        
        response = self.client.post('/api/v1/scripts/outline/', data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('outline', response.data)
        
        # Verify that analyze_image was called
        mock_analyze_image.assert_called_once()
        
        # Verify that the image file object was passed correctly
        call_args = mock_analyze_image.call_args[0][0]
        self.assertTrue(hasattr(call_args, 'read'))
        self.assertTrue(hasattr(call_args, 'seek'))
