# Emotion Propagation Agent (Component 2)

Component 2: "Emotion Propagation Agent for AI-Generated Neuro-Marketing Content."

## Theoretical Foundation

This research prototype is grounded in Emotional Contagion. The system studies whether emotionally aligned AI-generated marketing content can transmit a selected emotional tone to users, and whether that alignment improves persuasiveness, trustworthiness, and engagement outcomes.

## Architecture

User Input → LLM Generator (Groq) → RoBERTa Emotion Validator → Regeneration Loop → Best-Attempt Selection → Final Content → User Study → Dashboard

The backend generates a marketing message with a large language model through the Groq API, validates the generated text with a fine-tuned RoBERTa emotion classifier, and regenerates the message up to five times if the detected emotion does not match the selected target emotion. Across the attempts, the system keeps the attempt where the target emotion scored highest.

## Tech Stack

- Frontend: React.js + Vite + Tailwind CSS
- Backend: Python Flask API with CORS
- Generation: Groq API (LLaMA, default `llama-3.1-8b-instant`)
- Validation: Fine-tuned RoBERTa sequence classification model loaded from local files
- Analytics: Pandas CSV logging + dashboard summaries

## Prerequisites

Before running the project, make sure you have:

- Python 3.10 or newer
- Node.js 18 or newer with npm
- A Groq API key (from https://console.groq.com)
- The RoBERTa model folder copied into `backend/models/roberta_emotion_model/`

Recommended checks:

```bash
python --version
node --version
npm --version
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
- relief
- admiration
- neutral

(Note: an earlier version used a separate `optimism` label. Based on emotion-taxonomy literature, optimism was merged into `confidence`, giving the current 8 labels.)

## Dataset

The RoBERTa validator is fine-tuned on the GoEmotions dataset (Google Research), which provides 27 emotions plus neutral. GoEmotions is mapped down to the 8 project emotions above, then class-balanced for training.

```text
dataset/
├── raw/          # original GoEmotions train/validation/test files
└── processed/    # mapped + balanced CSVs actually used for training
    ├── train_mapped.csv
    ├── validation_mapped.csv
    ├── test_mapped.csv
    ├── train_balanced.csv
    └── sample_mapped_rows.csv
```

## Folder Structure

```text
emotion-propagation-agent/
├── backend/
│   ├── app.py
│   ├── requirements.txt
│   ├── .env                     # holds GROQ_API_KEY (do not commit)
│   ├── models/
│   │   └── roberta_emotion_model/
│   │       ├── config.json
│   │       ├── model.safetensors or pytorch_model.bin
│   │       ├── tokenizer.json
│   │       ├── tokenizer_config.json
│   │       ├── vocab.json
│   │       ├── merges.txt
│   │       ├── special_tokens_map.json
│   │       └── label_mapping.json
│   ├── outputs/
│   │   └── user_study_responses.csv
│   └── utils/
│       ├── model_loader.py
│       └── emotion_agent.py
├── dataset/
│   ├── raw/
│   └── processed/
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

The backend looks for the tokenizer, model weights, and `label_mapping.json` in that folder. If the folder is missing, the backend still runs and returns an explanatory warning through `/health`, `/api/predict-emotion`, and the generation endpoints.

The `label_mapping.json` must match the trained model's 8 labels:

```json
{
  "0": "joy",
  "1": "excitement",
  "2": "trust",
  "3": "confidence",
  "4": "curiosity",
  "5": "relief",
  "6": "admiration",
  "7": "neutral"
}
```

## Groq API Setup

The backend generates content through the Groq API, so no local LLM is required.

1. Create an account and API key at https://console.groq.com (API Keys).
2. In the `backend` folder, create a file named `.env` containing:

```text
GROQ_API_KEY=gsk_your_actual_key_here
```

3. Add `.env` to `.gitignore` so the key is never committed.

The backend calls:

```text
https://api.groq.com/openai/v1/chat/completions
```

If the key is missing or the service is unreachable, the generation endpoints return:

`GROQ_API_KEY is not set. Add it to a .env file or your environment variables.`
or
`Groq LLM service is not available. Check your API key and internet connection.`

## How to Train in Colab

Typical workflow:

1. Fine-tune a RoBERTa sequence classification model in Google Colab on the mapped GoEmotions data.
2. Save the tokenizer and model with `save_pretrained()`.
3. Export a `label_mapping.json` file mapping model output indexes to the 8 project emotions.
4. Download the saved model folder.
5. Copy the folder into `backend/models/roberta_emotion_model/`.

## Project Setup

### Windows Setup

1. Clone or extract the project.
2. Copy your trained RoBERTa folder into:

```text
emotion-propagation-agent\backend\models\roberta_emotion_model\
```

3. Create the `.env` file in `backend\` with your `GROQ_API_KEY` (see Groq API Setup).
4. Start the backend:

```powershell
cd emotion-propagation-agent\backend
python -m venv venv
venv\Scripts\activate
python -m pip install -r requirements.txt
python app.py
```

5. Start the frontend in a new terminal:

```powershell
cd emotion-propagation-agent\frontend
npm install
npm run dev
```

### macOS Setup

1. Clone or extract the project.
2. Copy your trained RoBERTa folder into:

```text
emotion-propagation-agent/backend/models/roberta_emotion_model/
```

3. Create the `.env` file in `backend/` with your `GROQ_API_KEY` (see Groq API Setup).
4. Start the backend:

```bash
cd emotion-propagation-agent/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

5. Start the frontend in a new terminal:

```bash
cd emotion-propagation-agent/frontend
npm install
npm run dev
```

Backend URL: `http://localhost:5000`
Frontend URL: `http://localhost:5173`

If port `5173` is already in use, start Vite on another port:

```bash
npm run dev -- --port 5174
```

Then open `http://localhost:5174`.

## Quick Start Checklist

Use this checklist when setting up on a new machine:

1. Install Python, Node.js, and npm.
2. Copy the RoBERTa model folder to `backend/models/roberta_emotion_model/`.
3. Create `backend/.env` with your `GROQ_API_KEY`.
4. Start Flask in `backend/`.
5. Start Vite in `frontend/`.
6. Open the frontend in a browser.
7. Test `GET /health` to confirm `model_loaded: true` and that 8 emotions are listed.

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
  - Generates content with Groq and validates it with RoBERTa.
  - If the target emotion is not detected, the backend regenerates up to 5 attempts and keeps the best-scoring one.
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
2. Build a structured prompt for the Groq LLM, including per-emotion "convey / avoid" signals.
3. Generate one short marketing message.
4. Validate the message with the RoBERTa emotion classifier.
5. A generation counts as a match if the target emotion is the top predicted emotion (strict top-1 matching).
6. If it does not match, regenerate with corrective instructions naming the emotion to avoid.
7. Stop after a maximum of 5 attempts.
8. Keep the attempt where the target emotion scored highest, and return the final message, prediction scores, validation status, and attempt history.

If the target emotion is not matched, the API still returns the best message and sets `validation_success` to `false`.

## User Study Explanation

Participants evaluate each generated message using:

- Emotion strength
- Message clarity
- Persuasiveness
- Trustworthiness
- Engagement interest
- Purchase interest

The app also stores category, target emotion, detected top emotion, validation success flag, and number of attempts used. This supports comparison between the intended emotion, the model-detected emotion, and the human-perceived emotion.

## Final Expected Flow

1. User opens the React frontend.
2. User enters product name, category, audience, features, and target emotion.
3. React sends the request to Flask.
4. Flask builds an LLM prompt and generates a marketing message with Groq.
5. RoBERTa validates the generated message.
6. If the detected emotion matches the target emotion, the message is accepted.
7. If not, Flask regenerates the content up to 5 attempts and keeps the best one.
8. React displays the final message, detected emotion, prediction scores, validation status, attempts used, attempt history, and visual suggestions (color palette, image style, layout mood).
9. User submits evaluation ratings.
10. Dashboard summarizes the research outputs.