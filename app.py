import json
import time
import uuid
import logging
import boto3

from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel


# =====================================================
# CONFIG
# =====================================================
BEDROCK_REGION = "us-east-1"

AIP_LIST = [
    {
        "name": "claude-sonnet-aip-1",
        "arn": "arn:aws:bedrock:us-east-1:196856463470:application-inference-profile/r59etrt038g0",
        "port": 8001
    },
    # Add more AIPs here
]


# =====================================================
# REQUEST MODEL
# =====================================================
class ChatRequest(BaseModel):
    prompt: str


# =====================================================
# CREATE APP PER AIP
# =====================================================
def create_app(aip_name: str, aip_arn: str, port: int):

    import logging
    import json
    import time
    import uuid
    import boto3

    from fastapi import FastAPI, HTTPException, Header
    from pydantic import BaseModel

    app = FastAPI(title=f"Bedrock API - {aip_name}")

    # =====================================================
    # LOGGER (PORT BASED FILE + APPEND MODE)
    # =====================================================
    logger = logging.getLogger(f"{aip_name}-{port}")
    logger.setLevel(logging.INFO)

    if not logger.handlers:

        log_file = f"bedrock_{port}.log"

        file_handler = logging.FileHandler(log_file, mode="a")
        console_handler = logging.StreamHandler()

        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(message)s"
        )

        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    # =====================================================
    # BEDROCK CLIENT
    # =====================================================
    bedrock = boto3.client(
        "bedrock-runtime",
        region_name="us-east-1"
    )

    # =====================================================
    # REQUEST MODEL
    # =====================================================
    class ChatRequest(BaseModel):
        prompt: str

    # =====================================================
    # HEALTH
    # =====================================================
    @app.get("/health")
    def health():
        return {
            "status": "healthy",
            "aip": aip_name,
            "port": port
        }

    # =====================================================
    # CHAT ENDPOINT
    # =====================================================
    @app.post("/chat")
    def chat(request: ChatRequest, x_api_key: str = Header(None)):

        request_id = str(uuid.uuid4())
        start_time = time.time()

        prompt = request.prompt

        logger.info(f"[{request_id}] REQUEST START")
        logger.info(f"[{request_id}] AIP={aip_name} PORT={port}")
        logger.info(f"[{request_id}] PROMPT={prompt}")
        logger.info(f"[{request_id}] PROMPT_LEN={len(prompt)}")

        try:

            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 4000,
                "temperature": 0.2,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }

            logger.info(f"[{request_id}] Calling Bedrock AIP")

            response = bedrock.invoke_model(
                modelId=aip_arn,
                body=json.dumps(body),
                contentType="application/json",
                accept="application/json"
            )

            raw_body = json.loads(response["body"].read())

            # =================================================
            # PARSE RESPONSE
            # =================================================
            text = ""
            for item in raw_body.get("content", []):
                if item.get("type") == "text":
                    text += item.get("text", "")

            latency_ms = round((time.time() - start_time) * 1000, 2)

            # =================================================
            # LOG OUTPUT DETAILS
            # =================================================
            logger.info(f"[{request_id}] RESPONSE_LEN={len(text)}")
            logger.info(f"[{request_id}] LATENCY_MS={latency_ms}")

            # optional: truncate raw response logging (avoid huge logs)
            safe_raw = json.dumps(raw_body)
            if len(safe_raw) > 2000:
                safe_raw = safe_raw[:2000] + "...(truncated)"

            logger.info(f"[{request_id}] RAW_RESPONSE={safe_raw}")

            logger.info(f"[{request_id}] REQUEST END SUCCESS")

            return {
                "request_id": request_id,
                "aip": aip_name,
                "port": port,
                "response": text,
                "latency_ms": latency_ms
            }

        except Exception as e:

            logger.exception(f"[{request_id}] REQUEST FAILED")
            raise HTTPException(status_code=500, detail=str(e))

    return app
