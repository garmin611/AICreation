import os
import json
from typing import Dict, List, Optional
from config.config import load_config

class ContextManager:
    def __init__(self):
        self.config = load_config()
        
    def get_project_context(self, project_name: str) -> Dict:
        """Get the full context for a project including knowledge graph."""
        projects_path = self.config.get('projects_path', 'projects/')
        kg_path = os.path.join(projects_path, project_name, 'kg.json')
        
        context = {
            'project_name': project_name,
            'knowledge_graph': {},
            'characters': [],
            'locations': [],
            'events': []
        }
        
        if os.path.exists(kg_path):
            with open(kg_path, 'r', encoding='utf-8') as f:
                kg_data = json.load(f)
                context.update(kg_data)
                
        return context
        
    def update_knowledge_graph(self, project_name: str, data: Dict) -> bool:
        """Update the project's knowledge graph."""
        try:
            projects_path = self.config.get('projects_path', 'projects/')
            kg_path = os.path.join(projects_path, project_name, 'kg.json')
            
            with open(kg_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
            return True
        except Exception as e:
            print(f"Error updating knowledge graph: {str(e)}")
            return False
            
    def get_chapter_context(self, project_name: str, chapter_id: str) -> Dict:
        """Get context specific to a chapter."""
        context = self.get_project_context(project_name)
        
        # Add chapter-specific information
        projects_path = self.config.get('projects_path', 'projects/')
        chapter_path = os.path.join(projects_path, project_name, 'chapters', chapter_id)
        
        if os.path.exists(chapter_path):
            # Get chapter content if available
            content_path = os.path.join(chapter_path, 'content.txt')
            if os.path.exists(content_path):
                with open(content_path, 'r', encoding='utf-8') as f:
                    context['chapter_content'] = f.read()
                    
            # Get all spans and their associated media
            spans = []
            for span_id in os.listdir(chapter_path):
                if span_id.isdigit():
                    span_path = os.path.join(chapter_path, span_id)
                    span_data = {
                        'id': span_id,
                        'text': '',
                        'prompt': '',
                        'images': [],
                        'audio': None
                    }
                    
                    # Get span text
                    span_text_path = os.path.join(span_path, 'span.txt')
                    if os.path.exists(span_text_path):
                        with open(span_text_path, 'r', encoding='utf-8') as f:
                            span_data['text'] = f.read()
                            
                    # Get prompt
                    prompt_path = os.path.join(span_path, 'prompt.txt')
                    if os.path.exists(prompt_path):
                        with open(prompt_path, 'r', encoding='utf-8') as f:
                            span_data['prompt'] = f.read()
                            
                    # Get images
                    span_data['images'] = [
                        f for f in os.listdir(span_path)
                        if f.startswith('image_') and f.endswith('.png')
                    ]
                    
                    # Get audio
                    audio_files = [
                        f for f in os.listdir(span_path)
                        if f.startswith('audio_') and f.endswith('.wav')
                    ]
                    if audio_files:
                        span_data['audio'] = audio_files[0]
                        
                    spans.append(span_data)
                    
            context['spans'] = sorted(spans, key=lambda x: int(x['id']))
            
        return context
        
    def get_span_context(self, project_name: str, chapter_id: str, span_id: str) -> Dict:
        """Get context specific to a span."""
        context = self.get_chapter_context(project_name, chapter_id)
        
        # Filter to get only the specific span
        span_data = next(
            (span for span in context.get('spans', []) if span['id'] == span_id),
            None
        )
        
        if span_data:
            context['current_span'] = span_data
            context['spans'] = [span_data]  # Keep only the current span
            
        return context
