# Component 3: Scarcity Optimization Agent (Research Project)

Welcome! This repository contains the foundation for your research on **Scarcity Optimization** within the Neuro-Marketing AI Framework.

## Project Structure
- `scarcity_agent.py`: The core logic for the Scarcity Agent.
- `main.py`: A demonstration of how this agent integrates into the wider system.
- `requirements.txt`: Python dependencies.
- `scarcity_agent_plan.md`: The high-level research implementation plan (Link: [Plan](file:///C:/Users/kavishka/.gemini/antigravity/brain/a17c8c32-6dad-4236-8e56-9a53d0cb8bf4/scarcity_agent_plan.md)).

## Recent Optimizations
- **LLM Integration**: Real xAI Grok API calls for scarcity copy generation with heuristic fallback
- **Error Handling**: Added logging and exception handling
- **Testing**: Basic unit tests with pytest
- **UI Enhancements**: Mode selector for AI vs heuristic generation
- **Dependencies**: Updated with testing and ML libraries

## How to proceed with your Research?

### 1. Refine the Theoretical Foundation
Deep dive into the **Scarcity Principle** (Cialdini). Your agent should be able to distinguish between:
- **Quantity Scarcity**: "Last items remaining."
- **Time Scarcity**: "Limited time offer."
- **Exclusivity**: "Invite-only access."

### 2. Implement LLM Logic
In `scarcity_agent.py`, replace the placeholder text generation with real LLM calls (e.g., OpenAI API). You will need to construct "System Prompts" that embody the persona of a psychological marketing expert.

### 3. Conduct Evaluation
As per your research objective, you need to measure:
- **Conversion Rates**: Does the scarcity version perform better?
- **User Trust**: Does excessive scarcity drive customers away?

### 4. Future Enhancements
- Add A/B testing framework
- Implement user feedback collection
- Expand dataset processing for more categories
- Add performance metrics and analytics dashboard

## Getting Started
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the demonstration:
   ```bash
   python main.py
   ```
