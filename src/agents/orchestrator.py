"""Orchestrator Agent for coordinating all agents"""

try:
    import autogen
except ImportError:
    autogen = None  # Autogen is optional

from typing import Dict
import os
import yaml
from pathlib import Path
from src.agents.research_agent import ResearchAgent
from src.agents.analysis_agent import AnalysisAgent
from src.agents.synthesis_agent import SynthesisAgent
from src.tools.storage_manager import StorageManager


class ResearchOrchestrator:
    """Orchestrator for coordinating research workflow"""
    
    def __init__(self, config_path: str = "config/agent_config.yaml"):
        """Initialize orchestrator with configuration
        
        Args:
            config_path: Path to configuration file
        """
        # Load configuration
        self.config = self._load_config(config_path)
        
        # Get API key
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable not set")
        
        # Initialize agents with API key
        research_config = self.config["agents"]["research_agent"].copy()
        research_config["api_key"] = api_key
        
        analysis_config = self.config["agents"]["analysis_agent"].copy()
        analysis_config["api_key"] = api_key
        
        synthesis_config = self.config["agents"]["synthesis_agent"].copy()
        synthesis_config["api_key"] = api_key
        
        # Initialize agents
        self.research_agent = ResearchAgent(research_config)
        self.analysis_agent = AnalysisAgent(analysis_config)
        self.synthesis_agent = SynthesisAgent(synthesis_config)
        
        # Initialize storage
        self.storage = StorageManager(self.config["storage"])
        
        # Autogen GroupChat setup (optional, for future multi-agent conversations)
        if autogen:
            try:
                agents_list = []
                if self.research_agent.agent:
                    agents_list.append(self.research_agent.agent)
                if self.analysis_agent.agent:
                    agents_list.append(self.analysis_agent.agent)
                if self.synthesis_agent.agent:
                    agents_list.append(self.synthesis_agent.agent)
                
                if agents_list:
                    self.group_chat = autogen.GroupChat(
                        agents=agents_list,
                        messages=[],
                        max_round=10
                    )
                    
                    orchestrator_config = self.config["agents"]["orchestrator"].copy()
                    orchestrator_config["api_key"] = api_key
                    
                    self.manager = autogen.GroupChatManager(
                        groupchat=self.group_chat,
                        llm_config={
                            "config_list": [{
                                "model": orchestrator_config.get("model", "llama-3.3-70b-versatile"),
                                "api_key": api_key,
                                "api_type": "groq",
                                "base_url": "https://api.groq.com/openai/v1"
                            }],
                            "temperature": orchestrator_config.get("temperature", 0.3)
                        }
                    )
                else:
                    self.group_chat = None
                    self.manager = None
            except Exception as e:
                print(f"Warning: Could not initialize GroupChat: {str(e)}")
                self.group_chat = None
                self.manager = None
        else:
            self.group_chat = None
            self.manager = None
    
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file
        
        Args:
            config_path: Path to config file
        
        Returns:
            Configuration dictionary
        """
        config_file = Path(config_path)
        if not config_file.exists():
            # Return default config
            return {
                "agents": {
                    "research_agent": {
                        "name": "WebResearcher",
                        "model": "llama-3.3-70b-versatile",
                        "max_tokens": 4000,
                        "temperature": 0.3
                    },
                    "analysis_agent": {
                        "name": "FactAnalyzer",
                        "model": "llama-3.3-70b-versatile",
                        "max_tokens": 3000,
                        "temperature": 0.2
                    },
                    "synthesis_agent": {
                        "name": "Synthesizer",
                        "model": "llama-3.3-70b-versatile",
                        "max_tokens": 5000,
                        "temperature": 0.4
                    },
                    "orchestrator": {
                        "name": "Orchestrator",
                        "model": "llama-3.3-70b-versatile",
                        "max_tokens": 2000,
                        "temperature": 0.3
                    }
                },
                "search": {
                    "max_results": 10,
                    "timeout": 30
                },
                "storage": {
                    "vector_db_path": "./data/vector_db",
                    "references_path": "./data/references",
                    "summaries_path": "./data/summaries"
                }
            }
        
        with open(config_file, 'r') as f:
            return yaml.safe_load(f)
    
    async def execute_research(self, topic: str, depth: int = 5) -> Dict:
        """Main orchestration method
        
        Args:
            topic: Research topic
            depth: Number of sources to gather
        
        Returns:
            Complete research results dictionary
        """
        print(f"\n{'='*60}")
        print(f"🔍 Starting research on: {topic}")
        print(f"{'='*60}\n")
        
        try:
            # Step 1: Research
            print("📚 Step 1: Research Phase")
            research_data = await self.research_agent.research_topic(topic, depth=depth)
            print("✅ Research complete\n")
            
            # Step 2: Analysis
            print("🔬 Step 2: Analysis Phase")
            analysis_data = await self.analysis_agent.analyze_research(research_data)
            print("✅ Analysis complete\n")
            
            # Step 3: Synthesis
            print("📝 Step 3: Synthesis Phase")
            synthesis_data = await self.synthesis_agent.synthesize(research_data, analysis_data)
            print("✅ Synthesis complete\n")
            
            # Step 4: Storage
            print("💾 Step 4: Storage Phase")
            result_id = await self.storage.save_research(
                topic, research_data, analysis_data, synthesis_data
            )
            print(f"✅ Results stored: {result_id}\n")
            
            return {
                "id": result_id,
                "topic": topic,
                "synthesis": synthesis_data,
                "research": research_data,
                "analysis": analysis_data,
                "metadata": {
                    "sources_count": len(research_data.get("sources", [])),
                    "facts_count": len(analysis_data.get("facts", [])),
                    "risks_count": len(analysis_data.get("risks", [])),
                    "contradictions_count": len(analysis_data.get("contradictions", []))
                }
            }
        except Exception as e:
            print(f"\n❌ Error during research execution: {str(e)}")
            raise

