# Emotion Propagation Agent (Component 2)

Component 2: “Emotion Propagation Agent for AI-Generated Neuro-Marketing Content.”

## Theoretical Foundation

This prototype is grounded in Emotional Contagion: emotions can be transmitted through exposure to emotionally-laden cues. In a neuro-marketing context, emotion-aligned language can influence perceived clarity, engagement, trust, and purchase intent.

## Tech Stack

- Frontend: React.js + Vite + Tailwind CSS
- Backend: Python Flask API (CORS enabled for React dev server)
- Model: Trained emotion classifier from Google Colab (TF-IDF + Logistic Regression) + label binarizer

## Folder Structure

```
emotion-propagation-agent/
├── backend/
│   ├── app.py
│   ├── requirements.txt
│   ├── models/
│   │   ├── emotion_classifier_tfidf_logreg.pkl
│   │   └── emotion_label_binarizer.pkl
│   ├── outputs/
│   │   └── user_study_responses.csv
│   └── utils/
│       ├── model_loader.py
│       └── emotion_agent.py
└── frontend/
    ├── package.json
    ├── index.html
    └── src/
        ├── main.jsx
        ├── App.jsx
        ├── api/
        │   └── emotionApi.js
        ├── components/
        └── pages/
```

## Model File Placement

Place your trained `.pkl` files here:

```
emotion-propagation-agent/backend/models/
  emotion_classifier_tfidf_logreg.pkl
  emotion_label_binarizer.pkl
```

If the model files are missing, the backend will not crash. Prediction endpoints return empty predictions with:

`Model files not found. Please place the trained .pkl files inside backend/models.`

## Backend (Flask) Run Commands

```bash
cd emotion-propagation-agent/backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

Windows venv activation:

```bash
venv\Scripts\activate
```

Backend URL: `http://localhost:5000`

## Frontend (React) Run Commands

```bash
cd emotion-propagation-agent/frontend
npm install
npm run dev
```

Frontend URL: `http://localhost:5173`

## API Endpoints

- `GET /`
  - Returns API status payload for Component 2.
- `GET /health`
  - Returns `{ status, model_loaded }`.
- `POST /api/predict-emotion`
  - Input: `{ "text": "..." }`
  - Output: `{ "text": "...", "predictions": [{ "emotion": "...", "score": 0.85 }, ...] }`
- `POST /api/generate-message`
  - Generates an emotion-aligned marketing message + CTA + visual suggestions.
  - If a model is loaded, returns `emotion_predictions` for the generated message.
- `POST /api/generate-variations`
  - Generates multiple messages for multiple target emotions.
- `POST /api/user-study`
  - Saves participant ratings to `backend/outputs/user_study_responses.csv`.
- `GET /api/user-study-summary`
  - Returns averages by emotion and best-performing emotion.
- `GET /api/user-study-responses`
  - Returns raw CSV rows for the dashboard table.

## How to Use the System (Expected Flow)

1. Start the Flask backend on port 5000.
2. Start the React frontend on port 5173.
3. Go to **Generate** and enter product details and a target emotion.
4. Generate an emotion-aligned marketing message.
5. Review the model validation predictions and chart.
6. Submit **User Study Evaluation** ratings (1–5 scale).
7. Open **Dashboard** to view aggregated results and the response table.

## User Study Explanation

Participants evaluate each generated message using:

- Emotion strength
- Message clarity
- Persuasiveness
- Trustworthiness
- Engagement interest
- Purchase interest

The dashboard summarizes performance across target emotions and helps identify which target emotion produces the best outcomes in your study.
