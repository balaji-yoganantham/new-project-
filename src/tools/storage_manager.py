"""Storage manager for research data using ChromaDB and file system"""

import chromadb
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List
import os


class StorageManager:
    """Manages storage of research data in vector DB and file system"""
    
    def __init__(self, config: Dict):
        self.vector_db_path = config.get("vector_db_path", "./data/vector_db")
        self.references_path = Path(config.get("references_path", "./data/references"))
        self.summaries_path = Path(config.get("summaries_path", "./data/summaries"))
        
        # Create directories if they don't exist
        self.references_path.mkdir(parents=True, exist_ok=True)
        self.summaries_path.mkdir(parents=True, exist_ok=True)
        Path(self.vector_db_path).mkdir(parents=True, exist_ok=True)
        
        # Initialize ChromaDB
        self.vector_db = chromadb.PersistentClient(path=self.vector_db_path)
        self.collection = self.vector_db.get_or_create_collection(
            name="research",
            metadata={"hnsw:space": "cosine"}
        )
    
    async def save_research(
        self,
        topic: str,
        research: Dict,
        analysis: Dict,
        synthesis: Dict
    ) -> str:
        """Save complete research data
        
        Args:
            topic: Research topic
            research: Research data dictionary
            analysis: Analysis data dictionary
            synthesis: Synthesis data dictionary
        
        Returns:
            Research ID string
        """
        research_id = f"{topic.replace(' ', '_').replace('/', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Save to vector database
        self._save_to_vector_db(research_id, research, analysis, synthesis)
        
        # Save references
        self._save_references(research_id, research.get("sources", []))
        
        # Save summary
        self._save_summary(research_id, synthesis)
        
        # Save full JSON
        self._save_full_json(research_id, {
            "topic": topic,
            "research": research,
            "analysis": analysis,
            "synthesis": synthesis
        })
        
        return research_id
    
    def _save_to_vector_db(
        self,
        research_id: str,
        research: Dict,
        analysis: Dict,
        synthesis: Dict
    ):
        """Store embeddings in ChromaDB"""
        documents = []
        metadatas = []
        ids = []
        
        # Add summary
        if "executive_summary" in synthesis:
            documents.append(synthesis["executive_summary"])
            metadatas.append({"type": "summary", "research_id": research_id, "topic": research.get("topic", "")})
            ids.append(f"{research_id}_summary")
        
        # Add facts
        facts = analysis.get("facts", [])
        for i, fact in enumerate(facts):
            fact_text = fact.get("text", "") if isinstance(fact, dict) else str(fact)
            if fact_text:
                documents.append(fact_text)
                metadatas.append({"type": "fact", "research_id": research_id})
                ids.append(f"{research_id}_fact_{i}")
        
        # Add key highlights
        highlights = synthesis.get("key_highlights", [])
        for i, highlight in enumerate(highlights):
            if highlight:
                documents.append(highlight)
                metadatas.append({"type": "highlight", "research_id": research_id})
                ids.append(f"{research_id}_highlight_{i}")
        
        if documents:
            try:
                self.collection.add(
                    documents=documents,
                    metadatas=metadatas,
                    ids=ids
                )
            except Exception as e:
                print(f"Warning: Could not save to vector DB: {str(e)}")
    
    def _save_references(self, research_id: str, sources: List[Dict]):
        """Save formatted references"""
        references_file = self.references_path / f"{research_id}_references.md"
        
        with open(references_file, 'w', encoding='utf-8') as f:
            f.write(f"# References for {research_id}\n\n")
            for i, source in enumerate(sources, 1):
                title = source.get("title", "Untitled")
                url = source.get("url", "")
                credibility = source.get("credibility_score", "N/A")
                date = source.get("date", "N/A")
                
                f.write(f"{i}. [{title}]({url})\n")
                f.write(f"   - Credibility: {credibility}/10\n")
                f.write(f"   - Date: {date}\n")
                
                key_points = source.get("key_points", [])
                if key_points:
                    f.write(f"   - Key Points:\n")
                    for point in key_points:
                        f.write(f"     - {point}\n")
                
                f.write("\n")
    
    def _save_summary(self, research_id: str, synthesis: Dict):
        """Save summary to markdown file"""
        summary_file = self.summaries_path / f"{research_id}_summary.md"
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(f"# Research Summary: {research_id}\n\n")
            
            if "executive_summary" in synthesis:
                f.write("## Executive Summary\n\n")
                f.write(f"{synthesis['executive_summary']}\n\n")
            
            if "key_highlights" in synthesis:
                f.write("## Key Highlights\n\n")
                for highlight in synthesis["key_highlights"]:
                    f.write(f"- {highlight}\n")
                f.write("\n")
            
            if "full_report" in synthesis:
                f.write("## Full Report\n\n")
                f.write(f"{synthesis['full_report']}\n")
    
    def _save_full_json(self, research_id: str, data: Dict):
        """Save complete data as JSON"""
        json_file = self.summaries_path / f"{research_id}_full.json"
        
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def search_similar(self, query: str, n_results: int = 5) -> List[Dict]:
        """Search for similar research in vector DB
        
        Args:
            query: Search query
            n_results: Number of results to return
        
        Returns:
            List of similar research results
        """
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results
            )
            
            return [
                {
                    "document": doc,
                    "metadata": meta,
                    "distance": dist
                }
                for doc, meta, dist in zip(
                    results["documents"][0],
                    results["metadatas"][0],
                    results["distances"][0] if "distances" in results else [0] * len(results["documents"][0])
                )
            ]
        except Exception as e:
            print(f"Error searching vector DB: {str(e)}")
            return []

