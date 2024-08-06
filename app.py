from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.tools import BraveSearch
import json
import os
from mangum import Mangum

searcher = BraveSearch.from_api_key(api_key='BSAdN7aGXyzhxdgh76DgIgVXIbY0qdR', search_kwargs={"count": 10})
model = ChatGroq(model_name='llama-3.1-70b-versatile', api_key='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')

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful AI assistant. Answer all questions."),
    ("human", "{input}")
])

chain = prompt | model

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory=".")

class UserInput(BaseModel):
    user_input: str

def generate_responses(input_text: str):
    search_results = searcher.run(input_text)
    search_results = json.loads(search_results)
    context = [result['snippet'] for result in search_results]
    context = ' '.join(context)
    input_text = input_text + "\n\nUse this context:\n\n" + context
    response = chain.invoke({'input':input_text})
    return response.content

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post('/chat')
async def chat(user_input: UserInput):
    response = generate_responses(user_input.user_input)
    return {"status": "success", "content": response}

handler = Mangum(app)