# AI UX Critic

An AI-powered tool that analyzes UI screenshots and returns a structured usability critique — grounded in real UX heuristics and accessibility guidelines, not just generic AI opinions.

**[Live Demo](https://ai-ux-critic-jsvu4nubqb8mnep56svg57.streamlit.app/)** · Built by Fatima Naseer, UX Designer transitioning into AI Engineering

![Demo](demo/Diagen2.png)

## The Problem

Early-stage UX feedback is often slow to get — design reviews get scheduled days out, and junior designers don't always have a senior reviewer on hand for a quick sanity check. This tool gives instant, guideline-grounded feedback on a screenshot, so designers can catch obvious usability and accessibility issues before a formal review.

## How It Works

1. **Upload** a UI screenshot
2. Gemini's vision model analyzes it against usability heuristics
3. A **RAG (Retrieval-Augmented Generation)** layer retrieves relevant passages from a knowledge base of Nielsen's 10 usability heuristics, WCAG contrast guidelines, and UX best practices — so the critique is grounded in real standards, not just the model's general opinion
4. Gemini returns **structured JSON** (not free text) with each issue's rule violated, plain-language explanation, severity, location, and suggested fix
5. Severity is calibrated by the *role* of the affected element (primary/secondary/tertiary) rather than just the type of rule violated, so a navigation bar issue is rated more seriously than a decorative label issue
6. Results render as clean, color-coded cards in a Streamlit interface

## Architecture

```
Screenshot Upload
      ↓
Gemini Vision Model ←──── Retrieved guideline chunks
      ↓                         ↑
Structured JSON Output    Chroma Vector DB
      ↓                         ↑
Streamlit UI              Embedded knowledge base
                        (Nielsen heuristics, WCAG, UX best practices)
```

## Tech Stack

- **Gemini API** (`gemini-3.6-flash`) — vision-capable critique generation with structured JSON output
- **Gemini Embeddings** (`gemini-embedding-001`) — for the RAG retrieval layer
- **ChromaDB** — local vector database for the knowledge base
- **Streamlit** — UI and deployment
- **Python** (PIL, python-dotenv)

## What I'd Build Next

- Multi-page flow analysis (critique an entire user journey, not just one screen)
- Agentic mode: let the model decide which guidelines to retrieve based on what it sees, rather than a fixed retrieval query
- Comparison mode: upload two versions of a design and get a before/after critique
- Export critique as a shareable PDF report

## Run It Locally

```bash
git clone https://github.com/your-username/ai-ux-critic.git
cd ai-ux-critic
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
python build_knowledge_base.py
streamlit run app.py
```

You'll need a free Gemini API key from [Google AI Studio](https://aistudio.google.com), added to a `.env` file as `GEMINI_API_KEY=your_key`.