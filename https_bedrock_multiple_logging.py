#!/usr/bin/env python3
"""
Address Detection and Summarization API using AWS Bedrock (Anthropic Claude model)
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
app = FastAPI(title="Address Detection and Summarization API (Bedrock)")

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

def get_bedrock_response(model_id: str, prompt_text: str, max_tokens: int = 1000, temperature: float = 0.3) -> str:
    """Send prompt to AWS Bedrock model and return text output"""
    logger.info(f"Sending prompt to Bedrock model {model_id}")
    logger.debug(f"Prompt text: {prompt_text}")

    client = get_bedrock_client()
    try:
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [
                {"role": "user", "content": [{"type": "text", "text": prompt_text}]}
            ],
        }

        response = client.invoke_model(
            modelId=model_id,
            contentType="application/json",
            accept="application/json",
            body=json.dumps(body),
        )

        raw_body = response["body"].read()
        resp_body = json.loads(raw_body)
        logger.info(f"Raw Bedrock response JSON: {json.dumps(resp_body)[:1000]}")

        # Handle both Anthropic and Bedrock content styles
        output_text = ""
        if "results" in resp_body:
            output_text = resp_body.get("results", [{}])[0].get("outputText", "").strip()
        elif "content" in resp_body:
            contents = resp_body.get("content", [])
            if contents and isinstance(contents, list):
                text_chunks = [c.get("text", "") for c in contents if "text" in c]
                output_text = "\n".join(text_chunks).strip()

        if not output_text:
            logger.warning(f"No recognizable text output in Bedrock response: {resp_body}")
            output_text = str(resp_body)

        logger.info(f"Parsed Bedrock output: {output_text[:500]}")
        return output_text

    except Exception as e:
        logger.error(f"Bedrock API error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to connect to AWS Bedrock: {str(e)}")

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
3. Ensure the summary is clear and captures the main points
Format your response as:
SUMMARY: [your summary here]
SENTIMENT_LABEL: [POSITIVE or NEGATIVE]
SENTIMENT_SCORE: [score between -1.0 and 1.0]

Text: {content}
"""
    response = get_bedrock_response(model_id, prompt)

    logger.info(f"Full model text response for summarization:\n{response}")

    summary = ""
    sentiment_label = "neutral"
    sentiment_score = 0.0

    for line in response.splitlines():
        if line.strip().startswith("SUMMARY:"):
            summary = line.split("SUMMARY:", 1)[-1].strip()
        elif line.strip().startswith("SENTIMENT_LABEL:"):
            sentiment_label = line.split("SENTIMENT_LABEL:", 1)[-1].strip()
        elif line.strip().startswith("SENTIMENT_SCORE:"):
            try:
                sentiment_score = float(line.split("SENTIMENT_SCORE:", 1)[-1].strip())
                sentiment_score = max(-1.0, min(1.0, sentiment_score))
            except ValueError:
                sentiment_score = 0.0

    if not summary:
        logger.warning("⚠️ No SUMMARY found in Bedrock response.")
    if sentiment_label not in ["POSITIVE", "NEGATIVE"]:
        sentiment_label = "POSITIVE" if sentiment_score >= 0 else "NEGATIVE"

    return summary, {"label": sentiment_label, "score": sentiment_score}

# ---------- API Endpoints ----------
@app.get("/")
async def root():
    return {
        "message": "Address Detection and Summarization API (Bedrock)",
        "version": "1.1.0",
        "status": "healthy",
        "endpoints": {
            "address_detection": "/address-detection",
            "summarization": "/summarize",
            "health": "/health",
            "docs": "/docs",
        },
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "Address Detection and Summarization API (Bedrock)", "version": "1.1.0"}

@app.post("/address-detection", response_model=ResponseModel)
async def address_detection(request: RequestModel):
    logger.info(f"Received /address-detection request: entity_urn={request.entity_urn}")
    logger.debug(f"Request content: {request.content[:500]}")

    try:
        if not request.content.strip():
            logger.warning(f"Empty content for entity_urn={request.entity_urn}")
            return ResponseModel(
                message="failure",
                result="Content is empty",
                action_type=Actions.DETECT_ADDRESS,
                entity_urn=request.entity_urn,
                sentiment=None,
            )

        addresses = detect_addresses(DEFAULT_MODEL_ARN, request.content)
        logger.info(f"/address-detection result for entity_urn={request.entity_urn}: {addresses}")

        return ResponseModel(
            message="success",
            result=addresses,
            action_type=Actions.DETECT_ADDRESS,
            entity_urn=request.entity_urn,
            sentiment=None,
        )

    except Exception as e:
        logger.error(f"/address-detection failed for entity_urn={request.entity_urn}: {str(e)}")
        return ResponseModel(
            message="failure",
            result=f"Error: {str(e)}",
            action_type=Actions.DETECT_ADDRESS,
            entity_urn=request.entity_urn,
            sentiment=None,
        )

@app.post("/summarize", response_model=ResponseModel)
async def summarize(request: RequestModel):
    logger.info(f"Received /summarize request: entity_urn={request.entity_urn}")
    logger.debug(f"Request content: {request.content[:500]}")

    try:
        if not request.content.strip():
            logger.warning(f"Empty content for entity_urn={request.entity_urn}")
            return ResponseModel(
                message="failure",
                result="Content is empty",
                action_type=Actions.SUMMARIZE,
                entity_urn=request.entity_urn,
                sentiment={},
            )

        summary, sentiment = summarize_and_analyze_sentiment(DEFAULT_MODEL_ARN, request.content)
        logger.info(f"/summarize result for entity_urn={request.entity_urn}: summary={summary}, sentiment={sentiment}")

        return ResponseModel(
            message="success",
            result=summary,
            sentiment=sentiment,
            action_type=Actions.SUMMARIZE,
            entity_urn=request.entity_urn,
        )

    except Exception as e:
        logger.error(f"/summarize failed for entity_urn={request.entity_urn}: {str(e)}")
        return ResponseModel(
            message="failure",
            result=f"Error: {str(e)}",
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
    parser.add_argument("--certfile", type=str, help="Path to SSL certificate file (.crt or .pem)")
    parser.add_argument("--keyfile", type=str, help="Path to SSL private key file (.key)")
    args = parser.parse_args()

    DEFAULT_MODEL_ARN = args.model_id

    # ---------- Dynamic log file based on port ----------
    LOG_FILE_PATH = f"/home/ssm-user/bedrock/bedrock{args.port}_api.log"

    # Configure logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', '%Y-%m-%d %H:%M:%S')

    # File handler
    file_handler = logging.FileHandler(LOG_FILE_PATH)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    logger.info(f"Starting Bedrock FastAPI server on port {args.port} with model {DEFAULT_MODEL_ARN}")

    ssl_options = {}
    if args.certfile and args.keyfile:
        if not os.path.exists(args.certfile) or not os.path.exists(args.keyfile):
            raise FileNotFoundError("Certificate or key file not found. Check paths.")
        ssl_options = {"ssl_certfile": args.certfile, "ssl_keyfile": args.keyfile}
        logger.info(f"🔒 HTTPS enabled on port {args.port}")
    else:
        logger.warning("⚠️ No certificate provided — running in HTTP mode")

    uvicorn.run(app, host="0.0.0.0", port=args.port, **ssl_options)
