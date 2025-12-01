#!/usr/bin/env python3
"""
Address Detection and Summarization API using AWS Bedrock (Anthropic + Llama support)
Supports HTTPS and multiple instances with different model ARNs and ports.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from enum import Enum
from typing import Dict, Optional
import boto3
import json
import argparse
import os
import logging

# ---------- Enums ----------
class Actions(Enum):
    DETECT_ADDRESS = "detect_address"
    SUMMARIZE = "summarize"

# ---------- Models ----------
class RequestModel(BaseModel):
    entity_urn: str = Field(..., description="Unique identifier for the entity")
    content: str = Field(..., description="Content to be processed")

class ResponseModel(BaseModel):
    message: str = Field(description="Result of the operation, e.g., 'success' or 'failure'")
    result: str = Field(description="Summary or || separated addresses")
    action_type: Actions = Field(..., description="Type of action performed")
    entity_urn: str = Field(..., description="Unique identifier for the entity")
    sentiment: Optional[Dict] = Field(default=None, description="Sentiment analysis result")

# ---------- FastAPI Setup ----------
app = FastAPI(title="Address Detection & Summarization API (Bedrock)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- AWS Bedrock Client ----------
def get_bedrock_client():
    return boto3.client("bedrock-runtime", region_name="us-east-1")

def is_llama_model(model_id: str) -> bool:
    """
    Detect Meta Llama or Scout models, including AIP wrappers.
    """
    model_id = model_id.lower()
    return any(x in model_id for x in ["llama", "meta", "scout"])

def get_bedrock_response(model_id: str, prompt_text: str, max_tokens: int = 1000, temperature: float = 0.3) -> str:
    """Send prompt to AWS Bedrock model and return parsed text output."""

    logger.info(f"Sending prompt to Bedrock model {model_id}")
    logger.debug(f"Prompt text: {prompt_text}")

    client = get_bedrock_client()
    llama_mode = is_llama_model(model_id)

    # ---------- Construct correct body ----------
    if llama_mode:
        body = {
            "prompt": prompt_text,
            "max_gen_len": max_tokens,
            "temperature": temperature,
            "top_p": 0.9,
        }
    else:
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [
                {"role": "user", "content": [{"type": "text", "text": prompt_text}]}
            ],
        }

    # ---------- Invoke model ----------
    try:
        response = client.invoke_model(
            modelId=model_id,
            contentType="application/json",
            accept="application/json",
            body=json.dumps(body),
        )

        resp_body = json.loads(response["body"].read())
        logger.info(f"Raw Bedrock response: {json.dumps(resp_body)[:500]}")

    except Exception as e:
        logger.error(f"Bedrock API error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to connect to AWS Bedrock: {str(e)}")

    # ---------- Parse response ----------
    if llama_mode:
        # Llama returns: {"generation": "text output"}
        return resp_body.get("generation", "").strip()

    # Anthropic returns: {"content": [{"text": "..."}]}
    contents = resp_body.get("content", [])
    text_chunks = [c.get("text", "") for c in contents if "text" in c]
    return "\n".join(text_chunks).strip()


# ---------- Core Functions ----------
def detect_addresses(model_id: str, content: str) -> str:
    prompt = f"""
Extract all addresses from the following text. Return only the addresses, separated by ' || '.
If no addresses are found, return empty string.

Text: {content}

Addresses:
"""
    return get_bedrock_response(model_id, prompt)

def summarize_and_analyze_sentiment(model_id: str, content: str) -> tuple:
    prompt = f"""
Please provide:
1. A concise summary of the following text
2. Sentiment analysis with label (POSITIVE/NEGATIVE) and score (-1.0 to 1.0)

Format:
SUMMARY: ...
SENTIMENT_LABEL: ...
SENTIMENT_SCORE: ...

Text: {content}
"""

    response = get_bedrock_response(model_id, prompt)
    logger.info(f"Full model text response:\n{response}")

    summary = ""
    sentiment_label = "neutral"
    sentiment_score = 0.0

    for line in response.splitlines():
        if line.startswith("SUMMARY:"):
            summary = line.replace("SUMMARY:", "").strip()
        elif line.startswith("SENTIMENT_LABEL:"):
            sentiment_label = line.replace("SENTIMENT_LABEL:", "").strip()
        elif line.startswith("SENTIMENT_SCORE:"):
            try:
                sentiment_score = float(line.replace("SENTIMENT_SCORE:", "").strip())
            except:
                sentiment_score = 0.0

    if sentiment_label not in ["POSITIVE", "NEGATIVE"]:
        sentiment_label = "POSITIVE" if sentiment_score >= 0 else "NEGATIVE"

    return summary, {"label": sentiment_label, "score": sentiment_score}


# ---------- API Endpoints ----------
@app.get("/")
async def root():
    return {
        "message": "Address Detection & Summarization API",
        "version": "1.1.0",
        "status": "healthy",
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.1.0"}

@app.post("/address-detection", response_model=ResponseModel)
async def address_detection(request: RequestModel):
    logger.info(f"Received /address-detection request: {request.entity_urn}")

    if not request.content.strip():
        return ResponseModel(
            message="failure",
            result="Content is empty",
            action_type=Actions.DETECT_ADDRESS,
            entity_urn=request.entity_urn,
            sentiment=None,
        )

    try:
        addresses = detect_addresses(DEFAULT_MODEL_ARN, request.content)
        return ResponseModel(
            message="success",
            result=addresses,
            action_type=Actions.DETECT_ADDRESS,
            entity_urn=request.entity_urn,
            sentiment=None,
        )
    except Exception as e:
        logger.error(f"Address detection error: {str(e)}")
        return ResponseModel(
            message="failure",
            result=str(e),
            action_type=Actions.DETECT_ADDRESS,
            entity_urn=request.entity_urn,
            sentiment=None,
        )

@app.post("/summarize", response_model=ResponseModel)
async def summarize(request: RequestModel):
    logger.info(f"Received /summarize request: {request.entity_urn}")

    if not request.content.strip():
        return ResponseModel(
            message="failure",
            result="Content is empty",
            action_type=Actions.SUMMARIZE,
            entity_urn=request.entity_urn,
            sentiment={},
        )

    try:
        summary, sentiment = summarize_and_analyze_sentiment(DEFAULT_MODEL_ARN, request.content)
        return ResponseModel(
            message="success",
            result=summary,
            sentiment=sentiment,
            action_type=Actions.SUMMARIZE,
            entity_urn=request.entity_urn,
        )
    except Exception as e:
        logger.error(f"Summarization error: {str(e)}")
        return ResponseModel(
            message="failure",
            result=str(e),
            sentiment={},
            action_type=Actions.SUMMARIZE,
            entity_urn=request.entity_urn,
        )


# ---------- Main ----------
if __name__ == "__main__":
    import uvicorn

    parser = argparse.ArgumentParser(description="Bedrock FastAPI multi-model HTTPS server")
    parser.add_argument("--model-id", type=str, required=True, help="AWS Bedrock model ARN")
    parser.add_argument("--port", type=int, required=True, help="Port to run FastAPI server on")
    parser.add_argument("--certfile", type=str, help="Path to SSL certificate (.crt or .pem)")
    parser.add_argument("--keyfile", type=str, help="Path to SSL private key (.key)")
    args = parser.parse_args()

    DEFAULT_MODEL_ARN = args.model_id

    # Logging
    LOG_FILE_PATH = f"/home/ssm-user/bedrock/bedrock{args.port}_api.log"
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    fmt = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', '%Y-%m-%d %H:%M:%S')

    fh = logging.FileHandler(LOG_FILE_PATH)
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    ch = logging.StreamHandler()
    ch.setFormatter(fmt)
    logger.addHandler(ch)

    ssl_options = {}
    if args.certfile and args.keyfile:
        ssl_options = {"ssl_certfile": args.certfile, "ssl_keyfile": args.keyfile}

    uvicorn.run(app, host="0.0.0.0", port=args.port, **ssl_options)
