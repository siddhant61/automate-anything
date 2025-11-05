"""
Tests for course parser service.
"""

import pytest
import tempfile
import json
from pathlib import Path
from src.services.course_parser_service import CourseParserService, course_parser_service


class TestCourseParserService:
    """Test course parser service functionality."""
    
    def test_validate_xml_file_valid(self, tmp_path):
        """Test XML validation with valid XML file."""
        service = CourseParserService()
        
        # Create a valid XML file
        xml_file = tmp_path / "test.xml"
        xml_file.write_text('<?xml version="1.0"?><root><item>test</item></root>')
        
        result = service.validate_xml_file(str(xml_file))
        assert result is True
    
    def test_validate_xml_file_invalid(self, tmp_path):
        """Test XML validation with invalid XML file."""
        service = CourseParserService()
        
        # Create an invalid XML file
        xml_file = tmp_path / "test.xml"
        xml_file.write_text('<root><item>unclosed')
        
        result = service.validate_xml_file(str(xml_file))
        assert result is False
    
    def test_sanitize_for_xml(self):
        """Test XML content sanitization."""
        service = CourseParserService()
        
        input_text = 'Test & "quotes" <tags> \'apostrophes\''
        result = service.sanitize_for_xml(input_text)
        
        assert '&amp;' in result
        assert '&quot;' in result
        assert '&lt;' in result
        assert '&gt;' in result
        assert '&apos;' in result
        assert '&' not in result.replace('&amp;', '').replace('&quot;', '').replace('&lt;', '').replace('&gt;', '').replace('&apos;', '')
    
    def test_extract_video_urls(self):
        """Test video URL extraction."""
        service = CourseParserService()
        
        video_data = "Video 1: https://example.com/video1.mp4, Video 2: https://example.com/video2.m3u8"
        urls = service.extract_video_urls(video_data)
        
        assert len(urls) == 2
        assert 'https://example.com/video1.mp4' in urls
        assert 'https://example.com/video2.m3u8' in urls
    
    def test_extract_video_urls_empty(self):
        """Test video URL extraction with no URLs."""
        service = CourseParserService()
        
        video_data = "No URLs here"
        urls = service.extract_video_urls(video_data)
        
        assert len(urls) == 0
    
    def test_parse_questions_from_data_multiple_choice(self):
        """Test parsing multiple choice questions."""
        service = CourseParserService()
        
        data = """Question 1
2.00 Pts
What is Python?
A programming language
A snake
A software tool"""
        
        questions = service.parse_questions_from_data(data)
        
        assert len(questions) == 1
        assert questions[0]['text'] == 'What is Python?'
        assert len(questions[0]['options']) == 3
        assert 'A programming language' in questions[0]['options']
    
    def test_parse_questions_from_data_open_ended(self):
        """Test parsing open-ended questions."""
        service = CourseParserService()
        
        data = """Question 1
Describe your experience with the course."""
        
        questions = service.parse_questions_from_data(data)
        
        assert len(questions) == 1
        assert 'Describe your experience' in questions[0]['text']
        assert len(questions[0]['options']) == 0
    
    def test_create_problem_xml_multiple_choice(self):
        """Test problem XML generation for multiple choice."""
        service = CourseParserService()
        
        questions = [{
            'text': 'What is 2+2?',
            'options': ['3', '4', '5']
        }]
        
        xml = service.create_problem_xml('test_vertical', questions)
        
        assert '<vertical url_name="test_vertical">' in xml
        assert '<problem url_name="problem_' in xml
        assert '<label>What is 2+2?</label>' in xml
        assert '<multiplechoiceresponse>' in xml
        assert '<choice correct="false">4</choice>' in xml
        assert '</vertical>' in xml
    
    def test_create_problem_xml_open_ended(self):
        """Test problem XML generation for open-ended questions."""
        service = CourseParserService()
        
        questions = [{
            'text': 'Explain your answer',
            'options': []
        }]
        
        xml = service.create_problem_xml('test_vertical', questions)
        
        assert '<vertical url_name="test_vertical">' in xml
        assert '<problem url_name="problem_' in xml
        assert '<label>Explain your answer</label>' in xml
        assert '<stringresponse' in xml
        assert '<textline' in xml
    
    def test_parse_course_structure_basic(self, tmp_path):
        """Test basic course structure parsing."""
        service = CourseParserService()
        
        course_data = {
            'section1': {
                'type': 'text',
                'data': 'This is lesson content'
            },
            'section2': {
                'type': 'self-test',
                'data': 'Question 1\n2.00 Pts\nTest question?\nAnswer A\nAnswer B'
            }
        }
        
        result = service.parse_course_structure(
            course_data=course_data,
            output_dir=str(tmp_path),
            org="TestOrg",
            course_id="test_course",
            url_name="2024"
        )
        
        assert result['success'] is True
        assert result['chapters'] == 2
        assert result['sequentials'] == 2
        assert result['verticals'] == 2
        assert Path(result['tar_path']).exists()
        assert Path(result['base_path']).exists()
    
    def test_parse_course_structure_creates_directories(self, tmp_path):
        """Test that parsing creates all necessary directories."""
        service = CourseParserService()
        
        course_data = {
            'section1': {
                'type': 'text',
                'data': 'Content'
            }
        }
        
        result = service.parse_course_structure(
            course_data=course_data,
            output_dir=str(tmp_path)
        )
        
        base_path = Path(result['base_path'])
        
        # Check that all subdirectories exist
        assert (base_path / 'chapter').exists()
        assert (base_path / 'sequential').exists()
        assert (base_path / 'vertical').exists()
        assert (base_path / 'html').exists()
        assert (base_path / 'problem').exists()
        assert (base_path / 'video').exists()
        assert (base_path / 'course').exists()
    
    def test_parse_course_structure_creates_tar(self, tmp_path):
        """Test that parsing creates a tar.gz file."""
        service = CourseParserService()
        
        course_data = {
            'section1': {
                'type': 'text',
                'data': 'Content'
            }
        }
        
        result = service.parse_course_structure(
            course_data=course_data,
            output_dir=str(tmp_path),
            course_id="test_course"
        )
        
        tar_path = Path(result['tar_path'])
        assert tar_path.exists()
        assert tar_path.suffix == '.gz'
        assert tar_path.stat().st_size > 0
    
    def test_write_xml_file(self, tmp_path):
        """Test XML file writing."""
        service = CourseParserService()
        
        xml_path = tmp_path / "test.xml"
        content = '<?xml version="1.0"?><test>content</test>'
        
        service._write_xml_file(xml_path, content)
        
        assert xml_path.exists()
        assert xml_path.read_text() == content
    
    def test_create_tar_gz(self, tmp_path):
        """Test tar.gz creation."""
        service = CourseParserService()
        
        # Create a test directory with files
        test_dir = tmp_path / "test_source"
        test_dir.mkdir()
        (test_dir / "file1.txt").write_text("content1")
        (test_dir / "file2.txt").write_text("content2")
        
        tar_path = tmp_path / "test.tar.gz"
        
        service._create_tar_gz(str(tar_path), str(test_dir))
        
        assert tar_path.exists()
        assert tar_path.stat().st_size > 0
    
    def test_global_service_instance(self):
        """Test that global service instance exists."""
        assert course_parser_service is not None
        assert isinstance(course_parser_service, CourseParserService)
    
    def test_sanitize_special_characters(self):
        """Test sanitization of special XML characters."""
        service = CourseParserService()
        
        # Test all special characters
        test_cases = [
            ('&', '&amp;'),
            ('<', '&lt;'),
            ('>', '&gt;'),
            ('"', '&quot;'),
            ("'", '&apos;')
        ]
        
        for input_char, expected in test_cases:
            result = service.sanitize_for_xml(input_char)
            assert result == expected
    
    def test_parse_multiple_questions(self):
        """Test parsing multiple questions from data."""
        service = CourseParserService()
        
        data = """Question 1
2.00 Pts
First question?
Option A
Option B

Question 2
3.00 Pts
Second question?
Choice 1
Choice 2
Choice 3"""
        
        questions = service.parse_questions_from_data(data)
        
        assert len(questions) == 2
        assert 'First question?' in questions[0]['text']
        assert 'Second question?' in questions[1]['text']
        assert len(questions[0]['options']) >= 2
        assert len(questions[1]['options']) >= 3
