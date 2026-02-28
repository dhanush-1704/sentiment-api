from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
import os

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
    return {"status": "API running"}

@app.get("/comment")
def comment_get():
    return {"message": "Use POST with JSON body {\"comment\":\"text\"}"}

@app.post("/comment")
def analyze_comment(data: CommentRequest):
    try:
        if not data.comment or data.comment.strip() == "":
            return {"sentiment": "neutral", "rating": 3}

        response = client.responses.parse(
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

        return response.output_parsed

    except Exception:
        # Never crash — always return valid JSON
        return {"sentiment": "neutral", "rating": 3}
