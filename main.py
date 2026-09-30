from fastapi import FastAPI
from google import genai
from google.genai import types
from dotenv import load_dotenv
from pydantic import BaseModel
 


load_dotenv()
from db import init_db, load_history as fetch_history, save_results as persist_results

init_db()

mem=[]

app=FastAPI()

class Review(BaseModel):
    text:str
    
class Analytics(BaseModel):
    label:str
    score:int
    theme:str


class ReviewResult(Analytics):
    review: str
    


@app.post("/check")
def test(query:Review):
    client = genai.Client()
    
    # mem.append({
    #     "role":"user",
    #     "parts":[{"text":query.question}]
    # })
    
    response = client.models.generate_content(
      model="gemini-3.5-flash-lite",
      contents=(
           "Analyze this customer review. n"
           "label must be 'positive', 'negative', or 'neutral'. \n"
           "score must be a number from 1 (very bad) to 5 (very good). \n"
           "theme must be ONE lowercase word for the main topic "
           "(for example: delivery, taste, price, service, quality). \n"
           f"Review:{query.text}"
          ),
      
      config=types.GenerateContentConfig(
          response_mime_type="application/json",
          response_schema=Analytics
      )
    )
    
    # mem.append({
    #            "role": "model",
    #            "parts":[{"text":response.text or ""}]
    #     })
    
    print(mem)
    return response.parsed
    

@app.post("/saveresults")
def save_results_endpoint(results: list[ReviewResult]):
    """Write all analyzed reviews into the database."""
    persist_results([result.model_dump() for result in results])
    return {"message": "Results saved successfully.", "saved": len(results)}

@app.get("/loadhistory")
def load_history_endpoint():
    """Read every review we have saved so far."""
    rows = fetch_history()
    history = [
        {"review": row[0], "label": row[1], "score": row[2], "theme": row[3]}
        for row in rows
    ]
    return {"history": history}