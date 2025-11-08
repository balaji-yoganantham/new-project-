# Quick Start Guide

## Installation

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment:**
   The `.env` file has been created with your Groq and LangSearch API keys. If you need to update it:
   ```bash
   # Edit .env file
   GROQ_API_KEY=your_groq_api_key_here
   LANGSEARCH_API_KEY=your_langsearch_api_key  # Default search provider
   BRAVE_API_KEY=your_brave_search_api_key  # Optional, alternative search provider
   LOG_LEVEL=INFO
   ```

## Running the Research Assistant

### Command Line Usage

**Option 1: Pass topic as argument**
```bash
python src/main.py "artificial intelligence trends 2024"
```

**Option 2: Interactive mode**
```bash
python src/main.py
# Then enter your research topic when prompted
```

### Example Output

The research assistant will:
1. 🔍 Search for sources on your topic
2. 📚 Extract and analyze content
3. 🔬 Identify facts, risks, and contradictions
4. 📝 Generate executive summary and full report
5. 💾 Save results to `data/` directory

### Output Files

After running, you'll find:
- `data/summaries/{research_id}_summary.md` - Executive summary and highlights
- `data/references/{research_id}_references.md` - Formatted citations
- `data/summaries/{research_id}_full.json` - Complete research data

## Programmatic Usage

```python
import asyncio
from src.agents.orchestrator import ResearchOrchestrator

async def main():
    orchestrator = ResearchOrchestrator()
    results = await orchestrator.execute_research(
        "Your research topic here",
        depth=5  # Number of sources to gather
    )
    
    # Access results
    print(results['synthesis']['executive_summary'])
    print(results['metadata'])

asyncio.run(main())
```

## Troubleshooting

### "GROQ_API_KEY not set" error
- Make sure `.env` file exists in the project root
- Verify the API key is correct

### Import errors
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check Python version (requires 3.10+)

### Web search issues
- The system uses LangSearch API by default (configured in `.env`)
- If LangSearch API key is not set, the system uses mock results for testing
- To use Brave Search instead, modify `WebSearchTool` initialization in `src/agents/research_agent.py`
- Get LangSearch API key from: https://langsearch.com/api-keys
- Get Brave API key from: https://brave.com/search/api/

## Next Steps

- Customize agent behavior in `config/agent_config.yaml`
- Modify prompt templates in `src/utils/prompt_templates.py`
- Add custom tools in `src/tools/`
- Extend agent capabilities in `src/agents/`

