# Component 2 — Emotion Propagation Agent

**Student:** WIDYASEKARA S P  
**ID:** IT22132482  
**Project:** R26-DS-005

## What This Component Does
Takes a product as input and generates emotionally
targeted marketing content using a 3-step pipeline:
1. Emotion Target Identification (RoBERTa + Rules)
2. Content Generation (LLaMA 3.3 70B via Groq)
3. Visual Tone Suggestions (Color Psychology Rules)

## How to Run

### Setup
```bash
cd backend
pip install -r requirements.txt
```

### Add your API key
Create a `.env` file in backend folder: