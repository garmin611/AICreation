import os
import json
from typing import Dict, Optional
from config.config import load_config

class PromptManager:
    def __init__(self):
        self.config = load_config()
        self.prompts_path = self.config.get('prompts_path', 'prompts/')
        
    def load_template(self, template_name: str) -> Optional[str]:
        """Load a prompt template from file."""
        template_path = os.path.join(self.prompts_path, f'{template_name}.txt')
        if not os.path.exists(template_path):
            return None
            
        with open(template_path, 'r', encoding='utf-8') as f:
            return f.read()
            
    def save_template(self, template_name: str, content: str) -> bool:
        """Save a prompt template to file."""
        try:
            if not os.path.exists(self.prompts_path):
                os.makedirs(self.prompts_path)
                
            template_path = os.path.join(self.prompts_path, f'{template_name}.txt')
            with open(template_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"Error saving template: {str(e)}")
            return False
            
    def get_project_templates(self, project_name: str) -> Dict[str, str]:
        """Get all prompt templates for a project."""
        project_prompts_path = os.path.join(
            self.config.get('projects_path', 'projects/'),
            project_name,
            'prompts'
        )
        
        templates = {}
        if os.path.exists(project_prompts_path):
            for filename in os.listdir(project_prompts_path):
                if filename.endswith('.txt'):
                    template_name = filename[:-4]
                    with open(os.path.join(project_prompts_path, filename), 'r', encoding='utf-8') as f:
                        templates[template_name] = f.read()
                        
        return templates
        
    def save_project_template(self, project_name: str, template_name: str, content: str) -> bool:
        """Save a prompt template for a specific project."""
        try:
            project_prompts_path = os.path.join(
                self.config.get('projects_path', 'projects/'),
                project_name,
                'prompts'
            )
            
            if not os.path.exists(project_prompts_path):
                os.makedirs(project_prompts_path)
                
            template_path = os.path.join(project_prompts_path, f'{template_name}.txt')
            with open(template_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"Error saving project template: {str(e)}")
            return False
