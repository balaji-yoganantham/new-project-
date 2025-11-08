"""Main application entry point for Research Assistant Agent"""

import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from src.agents.orchestrator import ResearchOrchestrator


def load_environment():
    """Load environment variables from .env file"""
    # Get the project root directory (parent of src/)
    project_root = Path(__file__).parent.parent
    env_path = project_root / ".env"
    if env_path.exists():
        load_dotenv(env_path)
    else:
        # Also try current directory
        env_path = Path(".env")
        if env_path.exists():
            load_dotenv(env_path)
        else:
            print("Warning: .env file not found. Using environment variables.")


async def main():
    """Main application function"""
    # Load environment variables
    load_environment()
    
    # Check for API key
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        # Try loading again with explicit path
        project_root = Path(__file__).parent.parent
        env_path = project_root / ".env"
        if env_path.exists():
            load_dotenv(env_path, override=True)
            api_key = os.getenv("GROQ_API_KEY")
    
    if not api_key:
        print("Error: GROQ_API_KEY environment variable not set.")
        print("Please set it in your .env file or environment variables.")
        print(f"Looking for .env at: {Path(__file__).parent.parent / '.env'}")
        sys.exit(1)
    
    # Initialize orchestrator
    try:
        orchestrator = ResearchOrchestrator()
    except Exception as e:
        print(f"Error initializing orchestrator: {str(e)}")
        sys.exit(1)
    
    # Get research topic from command line or prompt
    if len(sys.argv) > 1:
        topic = " ".join(sys.argv[1:])
    else:
        topic = input("Enter research topic: ").strip()
        if not topic:
            print("Error: No topic provided.")
            sys.exit(1)
    
    # Execute research
    try:
        results = await orchestrator.execute_research(topic, depth=5)
        
        # Display results
        print(f"\n{'='*60}")
        print("📊 RESEARCH RESULTS")
        print(f"{'='*60}\n")
        
        print(f"Topic: {results['topic']}")
        print(f"Research ID: {results['id']}\n")
        
        print("📈 Summary Statistics:")
        metadata = results.get("metadata", {})
        print(f"  - Sources analyzed: {metadata.get('sources_count', 0)}")
        print(f"  - Facts extracted: {metadata.get('facts_count', 0)}")
        print(f"  - Risks identified: {metadata.get('risks_count', 0)}")
        print(f"  - Contradictions found: {metadata.get('contradictions_count', 0)}\n")
        
        synthesis = results.get("synthesis", {})
        
        if "executive_summary" in synthesis:
            print("📝 Executive Summary:")
            print(f"{synthesis['executive_summary']}\n")
        
        if "key_highlights" in synthesis:
            print("✨ Key Highlights:")
            for highlight in synthesis["key_highlights"]:
                print(f"  • {highlight}")
            print()
        
        print(f"\n💾 Results saved to:")
        print(f"  - Summary: data/summaries/{results['id']}_summary.md")
        print(f"  - References: data/references/{results['id']}_references.md")
        print(f"  - Full JSON: data/summaries/{results['id']}_full.json")
        
        print(f"\n{'='*60}")
        print("✅ Research complete!")
        print(f"{'='*60}\n")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Research interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error during research: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())

