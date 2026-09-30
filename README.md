# Customer Feedback Analyzer

Analyze customer reviews for sentiment, a 1-to-5 score, and a one-word theme. The Streamlit interface sends each review to the FastAPI backend; the backend uses Gemini for analysis and SQLite for saved reports.

## Features

- Analyze multiple reviews, one review per line
- Show sentiment, score, and theme for each review
- Summarize average score, positive share, and most common theme
- Save successful analyses to SQLite and view saved history
- Continue a batch when an individual review fails

## How It Works

```text
Streamlit dashboard -> FastAPI backend -> Gemini API
										-> FastAPI backend -> SQLite database
```

The Streamlit app does not call Gemini directly. It communicates with the FastAPI service over HTTP.

## Requirements

- Python 3.14 (the project is pinned to this version in `.python-version`)
- [uv](https://docs.astral.sh/uv/)
- A Gemini API key
# Customer Feedback Analyzer

A Streamlit dashboard for analyzing customer reviews. It sends reviews to a FastAPI backend, which uses Gemini to identify sentiment, score, and theme. Reports are saved in SQLite.

## Run

Requires Python 3.14 and [uv](https://docs.astral.sh/uv/).

1. Install dependencies:

	```powershell
	uv sync
	```

2. Add your Gemini key to a `.env` file:

	```dotenv
	GEMINI_API_KEY=your_gemini_api_key
	```

3. Start the API in one terminal:

	```powershell
	uv run fastapi run main.py --port 8000
	```

4. Start the dashboard in a second terminal:

	```powershell
	uv run streamlit run app.py
	```

5. Open <http://localhost:8501>.

## Tech Stack and Libraries

- Python 3.14
- Streamlit for the dashboard
- FastAPI and Pydantic for the API
- Google Gen AI SDK for Gemini analysis
- SQLite for saved reports
- Requests for dashboard-to-API calls
- python-dotenv for environment variables
uv run streamlit run app.py
