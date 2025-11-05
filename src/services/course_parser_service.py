"""
Course parser service for converting EdX course data to OpenHPI format.

This service provides functionality to parse EdX course exports and generate
OpenHPI-compatible course structures with custom video players and problem sets.
"""

import os
import json
import re
import tarfile
import uuid
from pathlib import Path
from typing import Dict, List, Optional
import xml.etree.ElementTree as ET


class CourseParserService:
    """Service for parsing and converting course data."""
    
    @staticmethod
    def validate_xml_file(file_path: str) -> bool:
        """
        Validate an XML file for well-formedness.
        
        Args:
            file_path: Path to the XML file to validate
            
        Returns:
            True if the XML is well-formed, False otherwise
        """
        try:
            ET.parse(file_path)
            return True
        except ET.ParseError:
            return False
    
    @staticmethod
    def sanitize_for_xml(content: str) -> str:
        """
        Sanitize content for safe XML inclusion.
        
        Args:
            content: Text content to sanitize
            
        Returns:
            Sanitized content safe for XML
        """
        return (content.replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;')
                .replace('"', '&quot;')
                .replace("'", '&apos;'))
    
    @staticmethod
    def extract_video_urls(video_data_str: str) -> List[str]:
        """
        Extract video URLs from a video data string.
        
        Args:
            video_data_str: String containing video URLs
            
        Returns:
            List of extracted video URLs
        """
        urls = re.findall(r'https?://\S+', video_data_str)
        cleaned_urls = [url.rstrip(",") for url in urls]
        return cleaned_urls
    
    @staticmethod
    def parse_questions_from_data(data: str) -> List[Dict]:
        """
        Parse questions and their options from data string.
        
        Args:
            data: String containing question data
            
        Returns:
            List of parsed question dictionaries
        """
        questions_blocks = re.findall(r"Question \d+.*?(?=Question \d+|$)", data, re.DOTALL)
        
        parsed_questions = []
        for block in questions_blocks:
            lines = block.strip().split("\n")
            
            # Check if the block has the expected multiple choice format
            if len(lines) >= 4 and "Pts" in lines[1]:
                question_text = lines[2]
                options = lines[3:]
            else:
                # Treat as an open-ended question
                question_text = lines[1] if len(lines) > 1 else lines[0]
                options = []
            
            parsed_questions.append({"text": question_text, "options": options})
        
        return parsed_questions
    
    def create_problem_xml(self, vertical_id: str, questions: List[Dict]) -> str:
        """
        Generate XML for a problem content block.
        
        Args:
            vertical_id: Identifier for the vertical container
            questions: List of question dictionaries
            
        Returns:
            XML string for the problem
        """
        problems_xml = f'<vertical url_name="{vertical_id}">\n'
        
        for question in questions:
            question_id = uuid.uuid4().hex
            
            if question.get("options"):
                # Multiple choice question
                choices_xml = "\n".join([
                    f'      <choice correct="false">{choice}</choice>' 
                    for choice in question["options"]
                ])
                problem_structure = f"""
    <problem url_name="problem_{question_id}">
      <label>{self.sanitize_for_xml(question['text'])}</label>
      <multiplechoiceresponse>
        <choicegroup type="MultipleChoice">
{choices_xml}
        </choicegroup>
      </multiplechoiceresponse>
    </problem>\n"""
                problems_xml += problem_structure
            else:
                # Open-ended question
                problem_structure = f"""
    <problem url_name="problem_{question_id}">
      <label>{self.sanitize_for_xml(question['text'])}</label>
      <stringresponse answer=".*" type="text">
        <textline size="40"/>
      </stringresponse>
    </problem>\n"""
                problems_xml += problem_structure
        
        problems_xml += '</vertical>'
        return problems_xml
    
    def parse_course_structure(
        self,
        course_data: Dict,
        output_dir: str,
        org: str = "HPI",
        course_id: str = "course",
        url_name: str = "2024"
    ) -> Dict[str, any]:
        """
        Parse course data and generate OpenHPI-compatible structure.
        
        Args:
            course_data: Dictionary containing course content
            output_dir: Output directory for generated files
            org: Organization identifier
            course_id: Course identifier
            url_name: URL name for the course
            
        Returns:
            Dictionary with parsing results and file paths
        """
        base_path = Path(output_dir) / "openedx_course_structure"
        subdirectories = [
            'chapter', 'course', 'sequential', 'vertical', 
            'html', 'problem', 'video', 'about', 'policies', 'assets', 'info'
        ]
        
        # Create directory structure
        for subdir in subdirectories:
            (base_path / subdir).mkdir(parents=True, exist_ok=True)
        
        chapters = []
        sequentials = []
        verticals = []
        
        # Process each section
        for section_id, section_data in course_data.items():
            chapter_id = f"chapter_{section_id}"
            chapters.append(chapter_id)
            
            # Generate chapter XML
            chapter_xml = f'<chapter url_name="{chapter_id}" display_name="{self.sanitize_for_xml(chapter_id)}"></chapter>'
            self._write_xml_file(base_path / 'chapter' / f'{chapter_id}.xml', chapter_xml)
            
            content_type = section_data.get("type", "").lower()
            
            if content_type in ["text", "self-test", "survey", "problem"]:
                sequential_id = f"sequential_{section_id}"
                vertical_id = f"vertical_{section_id}"
                
                sequentials.append(sequential_id)
                verticals.append(vertical_id)
                
                # Generate sequential and vertical XMLs
                sequential_xml = f'<sequential url_name="{sequential_id}"><vertical url_name="{vertical_id}" /></sequential>'
                self._write_xml_file(base_path / 'sequential' / f'{sequential_id}.xml', sequential_xml)
                
                if content_type == "text":
                    content_xml = f'<html url_name="text_{vertical_id}">{self.sanitize_for_xml(section_data.get("data", ""))}</html>'
                    self._write_xml_file(base_path / 'html' / f'text_{vertical_id}.xml', content_xml)
                elif content_type in ["self-test", "survey", "problem"]:
                    questions = self.parse_questions_from_data(section_data.get("data", ""))
                    content_xml = self.create_problem_xml(f"problem_{vertical_id}", questions)
                    self._write_xml_file(base_path / 'problem' / f'problem_{vertical_id}.xml', content_xml)
        
        # Generate course files
        course_xml = f'<course url_name="{url_name}" org="{org}" course="{course_id}"/>'
        self._write_xml_file(base_path / 'course.xml', course_xml)
        
        # Create tar.gz package
        tar_path = Path(output_dir) / "openedx_course_structure.tar.gz"
        self._create_tar_gz(str(tar_path), str(base_path))
        
        return {
            'success': True,
            'base_path': str(base_path),
            'tar_path': str(tar_path),
            'chapters': len(chapters),
            'sequentials': len(sequentials),
            'verticals': len(verticals)
        }
    
    @staticmethod
    def _write_xml_file(path: Path, content: str):
        """Write content to XML file."""
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    @staticmethod
    def _create_tar_gz(output_filename: str, source_dir: str):
        """Create a tar.gz archive of the source directory."""
        with tarfile.open(output_filename, "w:gz") as tar:
            tar.add(source_dir, arcname=os.path.basename(source_dir))


# Global service instance
course_parser_service = CourseParserService()
