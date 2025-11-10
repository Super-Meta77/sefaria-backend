"""
Sugya Management System
Identifies, stores, and retrieves real Talmudic sugyot from Neo4j database
"""
import os
os.environ["NEO4J_URI"] = os.getenv("NEO4J_URI", "neo4j+s://8260863b.databases.neo4j.io")
os.environ["NEO4J_USER"] = os.getenv("NEO4J_USER", "neo4j")
os.environ["NEO4J_PASSWORD"] = os.getenv("NEO4J_PASSWORD", "IJYDpas_0uO5jbjB6Upk7uiEn_Gs-nb9vyO3oUH6v5c")

from database import get_driver
from typing import List, Dict, Optional
import re

class SugyaManager:
    """
    Manages Talmudic sugyot in the Neo4j database.
    
    A sugya is a thematic unit of Talmudic discussion, typically spanning
    multiple text nodes (verses) within a single page or topic.
    """
    
    def __init__(self):
        self.driver = get_driver()
    
    def identify_sugyot(self, tractate: str = "Berakhot", limit: int = 50) -> List[Dict]:
        """
        Identify sugyot from Talmudic texts in the database.
        Groups consecutive text nodes by page number (e.g., "2a", "2b", "3a")
        
        Returns list of sugyot with their text ranges.
        """
        with self.driver.session() as session:
            # Find all Talmud texts for this tractate, grouped by page
            query = """
            MATCH (t:Text)
            WHERE t.id CONTAINS $tractate
            AND (t.id CONTAINS 'Talmud' OR t.id =~ '.*\\d+[ab]:.*')
            RETURN t.id as text_id, 
                   t.content_he as content,
                   t.content_en as content_en
            ORDER BY t.id
            LIMIT $limit
            """
            
            results = session.run(query, {"tractate": tractate, "limit": limit})
            texts = list(results)
            
            # Group texts by page (e.g., "Berakhot 2a", "Berakhot 2b")
            sugyot = {}
            for text in texts:
                text_id = text['text_id']
                
                # Extract page reference (e.g., "2a", "2b")
                page_match = re.search(r'(\d+[ab])', text_id)
                if page_match:
                    page = page_match.group(1)
                    sugya_key = f"{tractate} {page}"
                    
                    if sugya_key not in sugyot:
                        sugyot[sugya_key] = {
                            'ref': sugya_key,
                            'texts': [],
                            'page': page
                        }
                    
                    sugyot[sugya_key]['texts'].append({
                        'id': text_id,
                        'content_he': text.get('content', ''),
                        'content_en': text.get('content_en', [])
                    })
            
            return list(sugyot.values())
    
    def create_sugya_node(self, sugya_ref: str, title: str, summary: str = "") -> bool:
        """
        Create a Sugya node in Neo4j to represent a thematic unit.
        Links it to its component Text nodes.
        """
        with self.driver.session() as session:
            # Create the Sugya node
            query = """
            MERGE (s:Sugya {ref: $ref})
            ON CREATE SET 
                s.title = $title,
                s.summary = $summary,
                s.created_at = datetime()
            ON MATCH SET
                s.title = $title,
                s.summary = $summary,
                s.updated_at = datetime()
            RETURN s
            """
            
            session.run(query, {
                "ref": sugya_ref,
                "title": title,
                "summary": summary
            })
            
            # Link Sugya to its Text nodes
            link_query = """
            MATCH (s:Sugya {ref: $ref})
            MATCH (t:Text)
            WHERE t.id CONTAINS $ref OR t.id STARTS WITH $ref
            MERGE (s)-[:CONTAINS_TEXT]->(t)
            """
            
            session.run(link_query, {"ref": sugya_ref})
            
            return True
    
    def get_sugya_structure(self, sugya_ref: str) -> Optional[Dict]:
        """
        Get the structure of a sugya with its texts and dialectic flow.
        Returns a tree structure for visualization.
        """
        with self.driver.session() as session:
            # Check if Sugya node exists
            sugya_query = """
            MATCH (s:Sugya {ref: $ref})
            RETURN s.title as title, s.summary as summary, s.ref as ref
            """
            
            sugya_result = session.run(sugya_query, {"ref": sugya_ref})
            sugya_node = sugya_result.single()
            
            if sugya_node:
                # Sugya node exists, get its structure
                title = sugya_node['title']
                summary = sugya_node['summary']
            else:
                # Sugya doesn't exist yet, infer from texts
                title = f"Discussion on {sugya_ref}"
                summary = f"Talmudic discussion from {sugya_ref}"
            
            # Get all texts for this sugya
            texts_query = """
            MATCH (t:Text)
            WHERE t.id CONTAINS $ref
            RETURN t.id as id, 
                   t.content_he as content_he,
                   t.content_en as content_en
            ORDER BY t.id
            LIMIT 20
            """
            
            texts_result = session.run(texts_query, {"ref": sugya_ref})
            texts = list(texts_result)
            
            if not texts:
                return None
            
            # Build a simple dialectic structure
            # In a real implementation, this would use NLP to detect questions/answers
            root = self._build_dialectic_tree(texts, sugya_ref)
            
            return {
                "ref": sugya_ref,
                "title": title,
                "summary": summary,
                "root": root
            }
    
    def _build_dialectic_tree(self, texts: List[Dict], sugya_ref: str) -> Dict:
        """
        Build a dialectic tree structure from text nodes.
        This is a simplified version - real implementation would use NLP.
        """
        # Create a root question
        root = {
            "id": f"{sugya_ref}-root",
            "type": "question",
            "label": self._extract_main_question(texts),
            "sugyaLocation": sugya_ref,
            "children": []
        }
        
        # Group texts into logical sections
        for i, text in enumerate(texts[:5]):  # Limit to first 5 for demo
            content = text.get('content_he', '')
            text_id = text.get('id', '')
            
            # Simplified heuristics for detecting dialectic elements
            node_type = self._detect_node_type(content, i)
            
            child = {
                "id": text_id,
                "type": node_type,
                "label": self._extract_label(content, node_type),
                "sugyaLocation": text_id,
                "children": []
            }
            
            root["children"].append(child)
        
        return root
    
    def _extract_main_question(self, texts: List[Dict]) -> str:
        """Extract or infer the main question of the sugya"""
        if texts and texts[0].get('content_he'):
            content = texts[0]['content_he']
            # Handle list content
            if isinstance(content, list):
                content = ' '.join(str(c) for c in content if c)
            # Remove HTML tags
            content = re.sub(r'<[^>]+>', '', str(content))
            # Take first 100 characters
            return content[:100].strip() + "..."
        return "What is the main topic of discussion?"
    
    def _detect_node_type(self, content, index: int) -> str:
        """
        Detect the type of dialectic node based on content.
        This is simplified - real implementation would use NLP.
        """
        # Handle list content
        if isinstance(content, list):
            content = ' '.join(str(c) for c in content if c)
        content_lower = str(content).lower() if content else ""
        
        # Hebrew keywords for different types
        if any(word in content_lower for word in ['למה', 'מאי', 'מנא', 'היכי']):
            return "kasha"  # question/challenge
        elif any(word in content_lower for word in ['אמר', 'תנן', 'תניא']):
            return "answer"
        elif any(word in content_lower for word in ['פלוגתא', 'מחלוקת']):
            return "dispute"
        elif index == 0:
            return "question"
        elif index % 3 == 1:
            return "answer"
        elif index % 3 == 2:
            return "terutz"  # resolution
        else:
            return "answer"
    
    def _extract_label(self, content, node_type: str) -> str:
        """Extract a readable label from the content"""
        if not content:
            return f"[{node_type.title()}]"
        
        # Handle list content
        if isinstance(content, list):
            content = ' '.join(str(c) for c in content if c)
        
        # Remove HTML tags
        clean = re.sub(r'<[^>]+>', '', str(content))
        # Take first 80 characters
        label = clean[:80].strip()
        if len(clean) > 80:
            label += "..."
        return label
    
    def list_all_sugyot(self) -> List[Dict]:
        """
        List all sugyot in the database (both created Sugya nodes and inferred ones).
        """
        with self.driver.session() as session:
            # First, get explicitly created Sugya nodes
            sugya_nodes_query = """
            MATCH (s:Sugya)
            RETURN s.ref as ref, s.title as title
            ORDER BY s.ref
            """
            
            explicit_sugyot = []
            result = session.run(sugya_nodes_query)
            for record in result:
                explicit_sugyot.append({
                    "ref": record['ref'],
                    "title": record['title'],
                    "normalized": record['ref'].replace(" ", "_")
                })
            
            # If we have explicit Sugya nodes, return them
            if explicit_sugyot:
                return explicit_sugyot
            
            # Otherwise, infer from Text nodes
            # Group by page number
            texts_query = """
            MATCH (t:Text)
            WHERE t.id =~ '.*Berakhot \\d+[ab]:.*'
            RETURN DISTINCT split(split(t.id, ':')[0], ' ')[1] as page
            ORDER BY page
            LIMIT 20
            """
            
            inferred_sugyot = []
            result = session.run(texts_query)
            for record in result:
                page = record['page']
                if page:
                    ref = f"Berakhot {page}"
                    inferred_sugyot.append({
                        "ref": ref,
                        "title": f"Discussion on {ref}",
                        "normalized": ref.replace(" ", "_")
                    })
            
            return inferred_sugyot

# Singleton instance
_manager = None

def get_sugya_manager() -> SugyaManager:
    """Get singleton SugyaManager instance"""
    global _manager
    if _manager is None:
        _manager = SugyaManager()
    return _manager

