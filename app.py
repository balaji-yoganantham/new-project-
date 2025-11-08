"""Streamlit application for Research Assistant Agent"""

import streamlit as st
import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv
from src.agents.orchestrator import ResearchOrchestrator

# Page configuration
st.set_page_config(
    page_title="Research Assistant Agent",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load environment variables
def load_environment():
    """Load environment variables from .env file"""
    project_root = Path(__file__).parent
    env_path = project_root / ".env"
    if env_path.exists():
        load_dotenv(env_path, override=True)
    else:
        env_path = Path(".env")
        if env_path.exists():
            load_dotenv(env_path, override=True)

load_environment()

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 2rem;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: bold;
        border-radius: 10px;
        padding: 0.5rem 1rem;
    }
    .stButton>button:hover {
        background: linear-gradient(90deg, #764ba2 0%, #667eea 100%);
    }
    .metric-card {
        background: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.title("⚙️ Configuration")
    
    # API Key input
    groq_api_key = st.text_input(
        "Groq API Key",
        value=os.getenv("GROQ_API_KEY", ""),
        type="password",
        help="Enter your Groq API key"
    )
    
    if groq_api_key:
        os.environ["GROQ_API_KEY"] = groq_api_key
    
    # Research depth
    depth = st.slider(
        "Number of Sources",
        min_value=3,
        max_value=10,
        value=5,
        help="Number of sources to gather for research"
    )
    
    # Model selection
    model = st.selectbox(
        "Groq Model",
        options=[
            "llama-3.3-70b-versatile",
            "llama-3.1-8b-instant",
            "llama-4-maverick-17b-128e-instruct",
            "gpt-oss-120b"
        ],
        index=0,
        help="Select the Groq model to use"
    )
    
    st.markdown("---")
    st.markdown("### 📊 About")
    st.markdown("""
    This Research Assistant Agent uses:
    - **Groq AI** for fast inference
    - **LangSearch API** for web search
    - **Multi-agent system** for comprehensive research
    """)

# Main content
st.markdown('<h1 class="main-header">🔍 Research Assistant Agent</h1>', unsafe_allow_html=True)
st.markdown("### An AI-powered research assistant that gathers, analyzes, and synthesizes information")

# Initialize session state
if "orchestrator" not in st.session_state:
    st.session_state.orchestrator = None
if "results" not in st.session_state:
    st.session_state.results = None
if "research_in_progress" not in st.session_state:
    st.session_state.research_in_progress = False

# Research topic input
topic = st.text_input(
    "Enter Research Topic",
    placeholder="e.g., artificial intelligence trends 2024",
    help="Enter the topic you want to research"
)

# Research button
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    start_research = st.button("🚀 Start Research", use_container_width=True)

# Research execution
if start_research and topic:
    if not groq_api_key:
        st.error("❌ Please enter your Groq API key in the sidebar")
    else:
        st.session_state.research_in_progress = True
        
        # Progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Initialize orchestrator
            status_text.text("🔧 Initializing orchestrator...")
            progress_bar.progress(10)
            
            orchestrator = ResearchOrchestrator()
            st.session_state.orchestrator = orchestrator
            
            # Update model in config
            for agent_name in ["research_agent", "analysis_agent", "synthesis_agent"]:
                if agent_name in orchestrator.config["agents"]:
                    orchestrator.config["agents"][agent_name]["model"] = model
            
            # Execute research
            status_text.text("🔍 Starting research...")
            progress_bar.progress(20)
            
            # Run async function
            async def run_research():
                return await orchestrator.execute_research(topic, depth=depth)
            
            results = asyncio.run(run_research())
            
            progress_bar.progress(100)
            status_text.text("✅ Research complete!")
            
            st.session_state.results = results
            st.session_state.research_in_progress = False
            
            st.success("Research completed successfully!")
            st.rerun()
            
        except Exception as e:
            st.error(f"❌ Error during research: {str(e)}")
            st.exception(e)
            st.session_state.research_in_progress = False
            progress_bar.empty()
            status_text.empty()

# Display results
if st.session_state.results:
    results = st.session_state.results
    
    # Metrics
    st.markdown("### 📊 Research Summary")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Sources", results.get("metadata", {}).get("sources_count", 0))
    with col2:
        st.metric("Facts", results.get("metadata", {}).get("facts_count", 0))
    with col3:
        st.metric("Risks", results.get("metadata", {}).get("risks_count", 0))
    with col4:
        st.metric("Contradictions", results.get("metadata", {}).get("contradictions_count", 0))
    
    st.markdown("---")
    
    # Executive Summary
    synthesis = results.get("synthesis", {})
    if "executive_summary" in synthesis:
        st.markdown("### 📝 Executive Summary")
        summary = synthesis["executive_summary"]
        # Ensure summary is a string, not a dict
        if isinstance(summary, dict):
            # Format dict summary nicely
            formatted_summary = ""
            if "main_findings" in summary:
                formatted_summary += f"**Main Findings:**\n{summary.get('main_findings', '')}\n\n"
            if "critical_insights" in summary:
                formatted_summary += f"**Critical Insights:**\n{summary.get('critical_insights', '')}\n\n"
            if "actionable_recommendations" in summary:
                formatted_summary += f"**Recommendations:**\n{summary.get('actionable_recommendations', '')}"
            summary = formatted_summary if formatted_summary else str(summary)
        st.info(summary)
    
    # Key Highlights
    if "key_highlights" in synthesis and synthesis["key_highlights"]:
        st.markdown("### ✨ Key Highlights")
        for highlight in synthesis["key_highlights"]:
            # Handle dict highlights
            if isinstance(highlight, dict):
                highlight_text = highlight.get("text") or highlight.get("fact_text") or str(highlight)
            else:
                highlight_text = str(highlight)
            st.markdown(f"- {highlight_text}")
    
    # Tabs for detailed information
    tab1, tab2, tab3, tab4 = st.tabs(["📄 Full Report", "🔬 Analysis", "📚 Sources", "💾 Files"])
    
    with tab1:
        if "full_report" in synthesis:
            st.markdown(synthesis["full_report"])
        else:
            st.info("Full report not available")
    
    with tab2:
        analysis = results.get("analysis", {})
        
        if "facts" in analysis and analysis["facts"]:
            st.markdown("#### Key Facts")
            for i, fact in enumerate(analysis["facts"][:10], 1):
                if isinstance(fact, dict):
                    # Handle different fact formats
                    fact_text = fact.get("text") or fact.get("fact_text") or str(fact)
                    certainty = fact.get("certainty") or fact.get("certainty_level", "Medium")
                else:
                    fact_text = str(fact)
                    certainty = "Medium"
                st.markdown(f"{i}. **{fact_text}** (Certainty: {certainty})")
        
        if "risks" in analysis and analysis["risks"]:
            st.markdown("#### Risks & Concerns")
            for i, risk in enumerate(analysis["risks"], 1):
                if isinstance(risk, dict):
                    category = risk.get("category", "General")
                    description = risk.get("description", "")
                    severity = risk.get("severity", "Medium")
                    st.markdown(f"{i}. **[{category}]** {description} (Severity: {severity})")
        
        if "contradictions" in analysis and analysis["contradictions"]:
            st.markdown("#### Contradictions")
            for i, contradiction in enumerate(analysis["contradictions"], 1):
                if isinstance(contradiction, dict):
                    desc = contradiction.get("description", "")
                    st.markdown(f"{i}. {desc}")
    
    with tab3:
        research = results.get("research", {})
        sources = research.get("sources", [])
        
        if sources:
            for i, source in enumerate(sources, 1):
                with st.expander(f"Source {i}: {source.get('title', 'Untitled')}"):
                    st.markdown(f"**URL:** {source.get('url', 'N/A')}")
                    st.markdown(f"**Description:** {source.get('description', 'N/A')}")
                    if source.get('credibility_score'):
                        st.markdown(f"**Credibility:** {source.get('credibility_score')}/10")
                    if source.get('key_points'):
                        st.markdown("**Key Points:**")
                        for point in source.get('key_points', []):
                            st.markdown(f"- {point}")
        else:
            st.info("No sources available")
    
    with tab4:
        result_id = results.get("id", "unknown")
        st.markdown("### Generated Files")
        st.markdown(f"""
        - **Summary:** `data/summaries/{result_id}_summary.md`
        - **References:** `data/references/{result_id}_references.md`
        - **Full JSON:** `data/summaries/{result_id}_full.json`
        """)
        
        if st.button("📥 Download Summary"):
            summary_path = Path(f"data/summaries/{result_id}_summary.md")
            if summary_path.exists():
                with open(summary_path, 'r', encoding='utf-8') as f:
                    st.download_button(
                        label="Download Summary",
                        data=f.read(),
                        file_name=f"{result_id}_summary.md",
                        mime="text/markdown"
                    )

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666;'>"
    "Research Assistant Agent | Powered by Groq AI & LangSearch"
    "</div>",
    unsafe_allow_html=True
)

