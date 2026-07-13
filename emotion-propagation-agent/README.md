# Emotion Propagation Agent (Component 2)

Component 2: “Emotion Propagation Agent for AI-Generated Neuro-Marketing Content.”

## Theoretical Foundation

This research prototype is grounded in Emotional Contagion. The system studies whether emotionally aligned AI-generated marketing content can transmit a selected emotional tone to users and whether that alignment improves persuasiveness, trustworthiness, and engagement outcomes.

## Updated Architecture

User Input → LLM Generator → RoBERTa Emotion Validator → Regeneration Loop → Final Content → User Study → Dashboard

The backend generates a message with a local LLM through Ollama, validates the generated text with a RoBERTa-based emotion classifier, and regenerates the message up to three times if the detected emotion does not match the selected target emotion.

## Tech Stack

- Frontend: React.js + Vite + Tailwind CSS
- Backend: Python Flask API with CORS
- Generation: Local Ollama LLM (`llama3.1`)
- Validation: RoBERTa sequence classification model loaded from local files
- Analytics: Pandas CSV logging + dashboard summaries

## Prerequisites

Before running the project, make sure you have:

- Python 3.10 or newer
- Node.js 18 or newer with npm
- Ollama installed locally
- The RoBERTa model folder copied into `backend/models/roberta_emotion_model/`

Recommended checks:

```bash
python --version
node --version
npm --version
ollama --version
```

## Supported Product Categories

- Baby
- Beauty
- Apparel
- Electronics
- Sports
- Pet
- Groceries

## Supported Emotion Labels

- joy
- excitement
- trust
- confidence
- curiosity
- optimism
- relief
- admiration
- neutral

## Folder Structure

```text
emotion-propagation-agent/
├── backend/
│   ├── app.py
│   ├── requirements.txt
│   ├── models/
│   │   └── roberta_emotion_model/
│   │       ├── config.json
│   │       ├── model.safetensors or pytorch_model.bin
│   │       ├── tokenizer.json
│   │       ├── tokenizer_config.json
│   │       ├── vocab.json
│   │       ├── merges.txt
│   │       ├── special_tokens_map.json
│   │       ├── label_mapping.json
│   │       └── MODEL_CARD.txt
│   ├── outputs/
│   │   └── user_study_responses.csv
│   └── utils/
│       ├── model_loader.py
│       └── emotion_agent.py
└── frontend/
    ├── package.json
    ├── index.html
    └── src/
        ├── api/
        ├── components/
        └── pages/
```

## RoBERTa Model Placement

Copy the full model folder into:

```text
emotion-propagation-agent/backend/models/roberta_emotion_model/
```

The backend looks for the tokenizer, model weights, and optional `label_mapping.json` in that folder. If the folder is missing, the backend still runs and returns an explanatory warning through `/health`, `/api/predict-emotion`, and generation endpoints.

## How to Train in Colab

Typical workflow:

1. Fine-tune a RoBERTa sequence classification model in Google Colab.
2. Save the tokenizer and model with `save_pretrained()`.
3. Export a `label_mapping.json` file that maps model output indexes to project emotion labels.
4. Download the saved model folder.
5. Copy the folder into `backend/models/roberta_emotion_model/`.

Example save commands in Colab:

```python
model.save_pretrained("roberta_emotion_model")
tokenizer.save_pretrained("roberta_emotion_model")
```

Example label mapping file:

```json
{
  "0": "joy",
  "1": "excitement",
  "2": "trust",
  "3": "confidence",
  "4": "curiosity",
  "5": "optimism",
  "6": "relief",
  "7": "admiration",
  "8": "neutral"
}
```

## Ollama Setup

Install and run the local LLM before generating content.

### macOS

- Option 1: download Ollama from [https://ollama.com/download](https://ollama.com/download)
- Option 2: install with Homebrew:

```bash
brew install ollama
```

### Windows

- Download the Windows installer from [https://ollama.com/download](https://ollama.com/download)
- Run the installer
- Open a new terminal after installation

### Start Ollama and pull the model

Keep Ollama running in one terminal:

```bash
ollama serve
```

In another terminal, download the required model:

```bash
ollama pull llama3.1
ollama run llama3.1
```

The backend calls:

```text
http://localhost:11434/api/generate
```

If Ollama is not running, generation endpoints return:

`LLM service is not available. Please start Ollama and ensure llama3.1 is installed.`

## Project Setup

### macOS Setup

1. Clone or extract the project.
2. Copy your trained RoBERTa folder into:

```text
emotion-propagation-agent/backend/models/roberta_emotion_model/
```

3. Start Ollama:

```bash
ollama serve
```

4. In another terminal, pull the model if it is not already installed:

```bash
ollama pull llama3.1
```

5. Start the backend:

```bash
cd emotion-propagation-agent/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

6. Start the frontend in a new terminal:

```bash
cd emotion-propagation-agent/frontend
npm install
npm run dev
```

### Windows Setup

1. Clone or extract the project.
2. Copy your trained RoBERTa folder into:

```text
emotion-propagation-agent\backend\models\roberta_emotion_model\
```

3. Start Ollama from the Start menu or a terminal:

```powershell
ollama serve
```

4. In another terminal, pull the model if it is not already installed:

```powershell
ollama pull llama3.1
```

5. Start the backend:

```powershell
cd emotion-propagation-agent\backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

6. Start the frontend in a new terminal:

```powershell
cd emotion-propagation-agent\frontend
npm install
npm run dev
```

## Backend Run Commands

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

For Windows activation:

```bash
venv\Scripts\activate
```

Backend URL: `http://localhost:5000`

## Frontend Run Commands

```bash
cd frontend
npm install
npm run dev
```

Frontend URL: `http://localhost:5173`

If port `5173` is already in use, start Vite on another port:

```bash
npm run dev -- --port 5174
```

Then open `http://localhost:5174`.

## Quick Start Checklist

Use this checklist when setting up on a new machine:

1. Install Python, Node.js, npm, and Ollama.
2. Copy the RoBERTa model folder to `backend/models/roberta_emotion_model/`.
3. Run `ollama serve`.
4. Run `ollama pull llama3.1`.
5. Start Flask in `backend/`.
6. Start Vite in `frontend/`.
7. Open the frontend in a browser.
8. Test `GET /health` to confirm `model_loaded: true`.

## API Endpoints

- `GET /`
  - Returns project status, model type, and generation strategy.
- `GET /health`
  - Returns backend health, whether the RoBERTa model is loaded, any model warning, and the allowed categories/emotions.
- `POST /api/predict-emotion`
  - Input:
    ```json
    { "text": "This product feels reliable and secure." }
    ```
  - Output:
    ```json
    {
      "text": "This product feels reliable and secure.",
      "predictions": [{ "emotion": "trust", "score": 0.82 }],
      "top_emotion": "trust",
      "warning": null
    }
    ```
- `POST /api/generate-message`
  - Generates content with Ollama and validates it with RoBERTa.
  - If the target emotion is not detected, the backend regenerates up to 3 attempts.
- `POST /api/generate-variations`
  - Runs the same LLM + validation loop for multiple requested emotions.
- `POST /api/user-study`
  - Saves user study responses to CSV, including optional `category`, `top_emotion`, `validation_success`, and `attempts_used`.
- `GET /api/user-study-summary`
  - Returns averages by emotion, validation success rate, and average attempts used.
- `GET /api/user-study-responses`
  - Returns raw CSV rows for the dashboard table.
- `POST /api/reload-model`
  - Reloads the RoBERTa model from disk without restarting Flask.

## Validation Loop Explanation

The generation endpoint follows this process:

1. Accept product details and target emotion.
2. Build a structured prompt for the local LLM.
3. Generate one short marketing message.
4. Validate the message with the RoBERTa emotion classifier.
5. If the detected top emotion matches the target emotion, accept the message.
6. If it does not match, regenerate the message with corrective instructions.
7. Stop after a maximum of 3 attempts.
8. Return the final message, prediction scores, validation status, and attempt history.

If the target emotion is not matched after 3 attempts, the API still returns the latest message and sets `validation_success` to `false`.

## User Study Explanation

Participants evaluate each generated message using:

- Emotion strength
- Message clarity
- Persuasiveness
- Trustworthiness
- Engagement interest
- Purchase interest

The app also stores:

- category
- target emotion
- detected top emotion
- validation success flag
- number of attempts used

This supports comparison between intended emotion, model-detected emotion, and human-perceived emotion.

## Final Expected Flow

1. User opens the React frontend.
2. User enters product name, category, audience, features, and target emotion.
3. React sends the request to Flask.
4. Flask builds an LLM prompt and generates a marketing message with Ollama.
5. RoBERTa validates the generated message.
6. If the detected emotion matches the target emotion, the message is accepted.
7. If not, Flask regenerates the content up to 3 attempts.
8. React displays the final message, detected emotion, prediction scores, validation status, attempts used, attempt history, CTA, and visual suggestions.
9. User submits evaluation ratings.
10. Dashboard summarizes the research outputs.
