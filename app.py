from collections import Counter
import os

import requests
import streamlit as st


st.set_page_config(
	page_title="Customer Feedback Analyzer",
	page_icon="R",
	layout="wide",
)

API_BASE_URL = os.getenv("REVIEWS_API_URL", "http://127.0.0.1:8000").rstrip("/")

st.markdown(
	"""
	<style>
	:root {
		--background-color: #111412;
		--secondary-background-color: #1b201d;
		--text-color: #e8eee8;
		--primary-color: #c5f36b;
		color-scheme: dark;
	}
	.stApp,
	[data-testid="stAppViewContainer"],
	[data-testid="stMain"] {
		background: #111412;
		color: #e8eee8;
	}
	[data-testid="stHeader"] { background: transparent; }
	[data-testid="stMainBlockContainer"] {
		max-width: 1040px;
		padding-top: 2rem;
	}
	.stApp p,
	.stApp label,
	.stApp [data-testid="stMarkdownContainer"] {
		color: #e8eee8;
	}
	.stApp h1 { color: #c5f36b !important; }
	.stApp textarea,
	.stApp input {
		background: #1b201d !important;
		color: #e8eee8 !important;
		border: 1px solid #414a42 !important;
	}
	.stApp textarea::placeholder,
	.stApp input::placeholder {
		color: #a3ada3 !important;
		opacity: 1;
	}
	.stApp textarea:focus,
	.stApp input:focus {
		border-color: #c5f36b !important;
		box-shadow: 0 0 0 1px #c5f36b !important;
	}
	.stApp button[kind="primary"] {
		background: #c5f36b !important;
		color: #111412 !important;
		border: 1px solid #c5f36b !important;
		font-weight: 700;
	}
	.stApp button[kind="primary"] * {
		color: #111412 !important;
	}
	.stApp button[kind="primary"]:hover {
		background: #d4f891 !important;
		border-color: #d4f891 !important;
	}
	[data-testid="stMetric"] {
		background: #1b201d;
		border: 1px solid #414a42;
		border-radius: 5px;
		padding: .8rem 1rem;
	}
	[data-testid="stMetricValue"] { color: #c5f36b; }
	[data-testid="stMetricLabel"] { color: #c4cdc4; }
	[data-testid="stDataFrame"] {
		border: 1px solid #414a42;
		border-radius: 5px;
	}
	hr { border-color: #414a42; }
	</style>
	""",
	unsafe_allow_html=True,
)


@st.cache_data(ttl=20, show_spinner=False)
def load_history(api_base_url):
	response = requests.get(f"{api_base_url}/loadhistory", timeout=5)
	response.raise_for_status()
	return response.json().get("history", [])


def insert_sample_reviews():
	st.session_state["review_input"] = (
		"Delivery was fast and the packaging was excellent.\n"
		"Customer support resolved my issue quickly.\n"
		"The product arrived late and was damaged."
	)


st.title("Customer Feedback Analyzer")
st.write("Turn customer feedback into clear next steps.")
try:
	load_history(API_BASE_URL)
	st.caption("API connection: Connected")
except requests.RequestException:
	st.warning("API unavailable. Start the FastAPI server to analyze reviews and load saved history.")

reviews_text = st.text_area(
	"Reviews",
	height=200,
	key="review_input",
	placeholder="Paste or type reviews here, one review per line...",
)

review_count = sum(bool(line.strip()) for line in reviews_text.splitlines())
count_col, sample_col = st.columns([3, 1])
count_col.caption(f"{review_count} review{'s' if review_count != 1 else ''} ready")
sample_col.button("Insert sample", on_click=insert_sample_reviews, use_container_width=True)

if st.button("Analyze", type="primary"):
	reviews = [line.strip() for line in reviews_text.splitlines() if line.strip()]

	if not reviews:
		st.warning("Please paste at least one review.")
	else:
		results = []
		progress = st.progress(0, text="Connecting to the analysis service...")

		for index, review in enumerate(reviews, start=1):
			try:
				response = requests.post(
					f"{API_BASE_URL}/check",
					json={"text": review},
					timeout=60,
				)
				response.raise_for_status()
				data = response.json()
				label = str(data["label"]).lower()
				if label not in {"positive", "negative", "neutral"}:
					raise ValueError("Unexpected sentiment label")

				results.append({
					"review": review,
					"label": label,
					"score": int(data["score"]),
					"theme": str(data["theme"]).lower(),
				})
			except requests.RequestException:
				results.append({
					"review": review,
					"label": "error",
					"score": 0,
					"theme": "unavailable",
					"error": "Could not reach the analysis service",
				})
			except (ValueError, KeyError, TypeError):
				results.append({
					"review": review,
					"label": "error",
					"score": 0,
					"theme": "unavailable",
					"error": "The service returned an invalid result",
				})

			progress.progress(
				index / len(reviews),
				text=f"Analyzed {index} of {len(reviews)} reviews",
			)

		progress.empty()
		st.session_state["results"] = results
		st.session_state["report_saved"] = False

if "results" in st.session_state:
	results = st.session_state["results"]
	valid_results = [result for result in results if result["label"] != "error"]

	st.subheader("Results")
	st.dataframe(
		results,
		use_container_width=True,
		hide_index=True,
		column_config={
			"review": st.column_config.TextColumn("Review", width="large"),
			"label": st.column_config.TextColumn("Sentiment"),
			"score": st.column_config.NumberColumn("Score", format="%d / 5"),
			"theme": st.column_config.TextColumn("Theme"),
			"error": st.column_config.TextColumn("Status"),
		},
	)

	st.subheader("Summary")
	review_col, score_col, positive_col, theme_col = st.columns(4)
	review_col.metric("Analyzed", len(valid_results))

	scores = [result["score"] for result in valid_results]
	score_col.metric(
		"Average score",
		round(sum(scores) / len(scores), 1) if scores else "N/A",
	)

	positive = [result for result in valid_results if result["label"] == "positive"]
	positive_col.metric(
		"% Positive",
		f"{round(len(positive) / len(valid_results) * 100)}%" if valid_results else "N/A",
	)

	themes = [result["theme"] for result in valid_results]
	if themes:
		top_theme = Counter(themes).most_common(1)[0][0]
		theme_col.metric("Top theme", top_theme.title())
	else:
		theme_col.metric("Top theme", "N/A")

	failed_count = len(results) - len(valid_results)
	if failed_count:
		st.warning(f"{failed_count} review{'s' if failed_count != 1 else ''} could not be analyzed.")

	report_saved = st.session_state.get("report_saved", False)
	if st.button(
		"Report saved" if report_saved else "Save to database",
		type="primary",
		disabled=not valid_results or report_saved,
	):
		try:
			response = requests.post(
				f"{API_BASE_URL}/saveresults",
				json=valid_results,
				timeout=10,
			)
			response.raise_for_status()
			load_history.clear()
			st.session_state["report_saved"] = True
			st.success(f"Saved {len(valid_results)} reviews.")
		except requests.RequestException:
			st.error("Could not save the results. Check that the API is running.")

with st.expander("Saved history"):
	try:
		history = load_history(API_BASE_URL)
		if history:
			st.write(f"Total saved so far: {len(history)}")
			st.dataframe(history, use_container_width=True, hide_index=True)
		else:
			st.write("Nothing saved yet. Analyze some reviews and click Save.")
	except requests.RequestException:
		st.warning("Saved history is unavailable. Check that the API is running.")
