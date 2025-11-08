# Research Assistant Agent

An AI-powered Research Assistant Agent that autonomously gathers web information, synthesizes findings, identifies key facts and risks, and maintains organized reference libraries using Microsoft's Autogen framework with Groq AI integration.

## Features

- 🔍 **Autonomous Web Research**: Automatically searches and gathers information from multiple sources
- 🧠 **Intelligent Analysis**: Extracts facts, identifies risks, and detects contradictions
- 📝 **Comprehensive Synthesis**: Creates executive summaries and detailed reports
- 💾 **Organized Storage**: Maintains vector database and reference libraries
- 🤖 **Multi-Agent System**: Specialized agents for research, analysis, and synthesis

## Technology Stack

- **Autogen (Microsoft)**: Multi-agent orchestration framework
- **Groq AI**: Fast LLM inference for reasoning and synthesis
- **Python 3.10+**: Primary language
- **ChromaDB**: Vector storage for embeddings
- **BeautifulSoup4**: Web scraping
- **LangSearch API**: Default web search provider
- **Brave Search API**: Alternative web search provider (optional)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd research-assistant
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
Create a `.env` file in the root directory:
```bash
GROQ_API_KEY=your_groq_api_key_here
LANGSEARCH_API_KEY=your_langsearch_api_key  # Default search provider
BRAVE_API_KEY=your_brave_search_api_key  # Optional, alternative search provider
LOG_LEVEL=INFO
```

## Usage

### Streamlit Web UI (Recommended)

Run the Streamlit web interface:

```bash
# Windows
.\venv\Scripts\python.exe -m streamlit run app.py

# Or use the batch file
run_streamlit.bat
```

The app will open in your default web browser at `http://localhost:8501`

### Command Line Usage

Run the research assistant from the command line:

```bash
python src/main.py "Your research topic here"
```

Or run interactively:
```bash
python src/main.py
# Then enter your research topic when prompted
```

### Programmatic Usage

```python
import asyncio
from src.agents.orchestrator import ResearchOrchestrator

async def main():
    orchestrator = ResearchOrchestrator()
    results = await orchestrator.execute_research("Your research topic", depth=5)
    print(results)

asyncio.run(main())
```

## Project Structure

```
research-assistant/
├── src/
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── research_agent.py      # Web research agent
│   │   ├── analysis_agent.py       # Fact extraction and risk analysis
│   │   ├── synthesis_agent.py      # Report generation
│   │   └── orchestrator.py        # Workflow coordination
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── web_search.py          # Web search tool
│   │   ├── web_scraper.py          # Content scraping
│   │   └── storage_manager.py      # Data storage
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py              # Data models
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── groq_client.py          # Groq AI client
│   │   └── prompt_templates.py     # Prompt templates
│   └── main.py                     # Application entry point
├── config/
│   └── agent_config.yaml           # Agent configuration
├── data/
│   ├── references/                 # Reference files
│   ├── summaries/                  # Summary files
│   └── vector_db/                  # ChromaDB storage
├── .env                            # Environment variables
├── requirements.txt
└── README.md
```

## Configuration

Edit `config/agent_config.yaml` to customize agent behavior:

```yaml
agents:
  research_agent:
    model: "llama-3.1-70b-versatile"
    max_tokens: 4000
    temperature: 0.3
  # ... other agents
```

## Output

The research assistant generates:

1. **Executive Summary**: High-level overview of findings
2. **Key Highlights**: Most important facts and risks
3. **Full Report**: Detailed analysis with sections
4. **References**: Formatted citations and source information
5. **Vector Embeddings**: Stored in ChromaDB for similarity search

All outputs are saved in the `data/` directory:
- `data/summaries/{research_id}_summary.md`
- `data/references/{research_id}_references.md`
- `data/summaries/{research_id}_full.json`

## API Keys

### Groq API Key (Required)
Get your API key from: https://console.groq.com/

### LangSearch API Key (Default Search Provider)
The system uses LangSearch API by default for web searches.
Get your API key from: https://langsearch.com/api-keys

### Brave Search API Key (Optional)
Alternative search provider. To use Brave instead of LangSearch, modify the `WebSearchTool` initialization in `src/agents/research_agent.py` to use `search_provider="brave"`.
Get your API key from: https://brave.com/search/api/

## Models

The system uses Groq's fast inference models. Default model: `llama-3.3-70b-versatile`

Available production models:
- `llama-3.3-70b-versatile` (Default - Best for research)
- `llama-3.1-8b-instant` (Fast, smaller model)
- `llama-4-maverick-17b-128e-instruct` (Preview)
- `gpt-oss-120b` (OpenAI's open-weight model)

You can change the model in the Streamlit sidebar or in `config/agent_config.yaml`

## Troubleshooting

### API Key Issues
- Ensure `GROQ_API_KEY` is set in `.env` file
- Check that the API key is valid and has sufficient credits

### Import Errors
- Make sure all dependencies are installed: `pip install -r requirements.txt`
- Verify Python version is 3.10 or higher

### Web Search Issues
- If Brave API key is not set, the system will use mock results
- Check internet connection for web scraping

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues and questions, please open an issue on the repository.

