import os
import shutil
from typing import List, Dict, Optional
from datetime import datetime
from config.config import load_config

class FileManager:
    def __init__(self):
        self.config = load_config()
        self.projects_path = self.config.get('projects_path', 'projects/')
        
    def create_project_structure(self, project_name: str) -> bool:
        """Create the basic project directory structure."""
        try:
            project_path = os.path.join(self.projects_path, project_name)
            if os.path.exists(project_path):
                return False
                
            # Create main project directory
            os.makedirs(project_path)
            
            # Create subdirectories
            os.makedirs(os.path.join(project_path, 'chapters'))
            os.makedirs(os.path.join(project_path, 'prompts'))
            
            # Create empty knowledge graph file
            with open(os.path.join(project_path, 'kg.json'), 'w', encoding='utf-8') as f:
                f.write('{}')
                
            return True
        except Exception as e:
            print(f"Error creating project structure: {str(e)}")
            return False
            
    def create_chapter_structure(self, project_name: str, chapter_id: str) -> bool:
        """Create the directory structure for a new chapter."""
        try:
            chapter_path = os.path.join(self.projects_path, project_name, 'chapters', chapter_id)
            if os.path.exists(chapter_path):
                return False
                
            os.makedirs(chapter_path)
            return True
        except Exception as e:
            print(f"Error creating chapter structure: {str(e)}")
            return False
            
    def create_span_structure(self, project_name: str, chapter_id: str, span_id: str) -> bool:
        """Create the directory structure for a new span."""
        try:
            span_path = os.path.join(self.projects_path, project_name, 'chapters', chapter_id, span_id)
            if os.path.exists(span_path):
                return False
                
            os.makedirs(span_path)
            return True
        except Exception as e:
            print(f"Error creating span structure: {str(e)}")
            return False
            
    def save_file(self, file_path: str, content: bytes) -> bool:
        """Save binary content to a file."""
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'wb') as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"Error saving file: {str(e)}")
            return False
            
    def save_text(self, file_path: str, content: str) -> bool:
        """Save text content to a file."""
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"Error saving text: {str(e)}")
            return False
            
    def delete_project(self, project_name: str) -> bool:
        """Delete a project and all its contents."""
        try:
            project_path = os.path.join(self.projects_path, project_name)
            if not os.path.exists(project_path):
                return False
                
            shutil.rmtree(project_path)
            return True
        except Exception as e:
            print(f"Error deleting project: {str(e)}")
            return False
            
    def list_projects(self) -> List[Dict]:
        """List all projects and their basic information."""
        try:
            if not os.path.exists(self.projects_path):
                return []
                
            projects = []
            for project_name in os.listdir(self.projects_path):
                project_path = os.path.join(self.projects_path, project_name)
                if os.path.isdir(project_path):
                    # Get project information
                    chapters_path = os.path.join(project_path, 'chapters')
                    chapter_count = len(os.listdir(chapters_path)) if os.path.exists(chapters_path) else 0
                    
                    # Get creation time
                    created_time = datetime.fromtimestamp(os.path.getctime(project_path))
                    
                    projects.append({
                        'project_name': project_name,
                        'chapter_count': chapter_count,
                        'created_at': created_time.isoformat(),
                        'path': project_path
                    })
                    
            return projects
        except Exception as e:
            print(f"Error listing projects: {str(e)}")
            return []
