from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
import os
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class CommentRequest(BaseModel):
    comment: str

@app.get("/")
def root():
    return {"status": "running"}

@app.post("/comment")
def analyze_comment(data: CommentRequest):

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=data.comment,
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "sentiment_schema",
                "schema": {
                    "type": "object",
                    "properties": {
                        "sentiment": {
                            "type": "string",
                            "enum": ["positive", "negative", "neutral"]
                        },
                        "rating": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 5
                        }
                    },
                    "required": ["sentiment", "rating"]
                }
            }
        }
    )

    # Parse JSON properly
    output_text = response.output[0].content[0].text
    return json.loads(output_text)
