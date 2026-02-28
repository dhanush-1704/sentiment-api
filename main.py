from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
import os

app = FastAPI()

# 🔥 ADD THIS
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

@app.post("/comment")
async def analyze_comment(data: CommentRequest):
    if not data.comment:
        raise HTTPException(status_code=400, detail="Comment cannot be empty")

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

    return response.output_parsed
@app.get("/comment")
async def comment_info():
    return {"message": "Use POST with JSON body { \"comment\": \"your text\" }"}
