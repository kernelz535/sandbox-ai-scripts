import json
import time
import uuid
import logging
import boto3

from fastapi import FastAPI
from pydantic import BaseModel


# =====================================================
# CONFIG
# =====================================================
BEDROCK_REGION = "us-east-1"

AIP_LIST = [
    {
        "name": "claude-sonnet-chat",
        "type": "chat",
        "arn": "arn:aws:bedrock:us-east-1:196856463470:application-inference-profile/r59etrt038g0",
        "port": 8001
    },
    {
        "name": "titan-embeddings",
        "type": "embedding",
        "arn": "arn:aws:bedrock:us-east-1:196856463470:application-inference-profile/okts96tw2u7u",
        "port": 8002
    }
]


# =====================================================
# REQUEST MODEL
# =====================================================
class InvokeRequest(BaseModel):
    text: str


# =====================================================
# APP FACTORY
# =====================================================
def create_app(aip_name: str, aip_type: str, aip_arn: str, port: int):

    app = FastAPI(title=f"{aip_name} ({aip_type})")

    # =================================================
    # LOGGER (PORT BASED FILE + APPEND MODE)
    # =================================================
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

    # =================================================
    # BEDROCK CLIENT
    # =================================================
    bedrock = boto3.client(
        "bedrock-runtime",
        region_name=BEDROCK_REGION
    )

    # =================================================
    # HEALTH CHECK
    # =================================================
    @app.get("/health")
    def health():
        return {
            "status": "healthy",
            "model": aip_name,
            "type": aip_type,
            "port": port
        }

    # =================================================
    # MAIN ENDPOINT
    # =================================================
    @app.post("/invoke")
    def invoke(request: InvokeRequest):

        request_id = str(uuid.uuid4())
        start_time = time.time()

        text = request.text

        logger.info(f"[{request_id}] REQUEST START")
        logger.info(f"[{request_id}] MODEL={aip_name}")
        logger.info(f"[{request_id}] TYPE={aip_type}")
        logger.info(f"[{request_id}] INPUT={text}")
        logger.info(f"[{request_id}] INPUT_LENGTH={len(text)}")

        try:

            # =================================================
            # CHAT MODEL (CLAUDE)
            # =================================================
            if aip_type == "chat":

                body = {
                    "anthropic_version": "bedrock-2023-05-31",
                    "temperature": 0.2,
                    "messages": [
                        {
                            "role": "user",
                            "content": text
                        }
                    ]
                }

                response = bedrock.invoke_model(
                    modelId=aip_arn,
                    body=json.dumps(body),
                    contentType="application/json",
                    accept="application/json"
                )

                result = json.loads(response["body"].read())

                output = ""
                for item in result.get("content", []):
                    if item.get("type") == "text":
                        output += item.get("text", "")

            # =================================================
            # EMBEDDING MODEL (TITAN)
            # =================================================
            elif aip_type == "embedding":

                body = {
                    "inputText": text
                }

                response = bedrock.invoke_model(
                    modelId=aip_arn,
                    body=json.dumps(body),
                    contentType="application/json",
                    accept="application/json"
                )

                result = json.loads(response["body"].read())

                output = result.get("embedding", [])

            else:
                raise Exception("Unsupported model type")

            # =================================================
            # METRICS
            # =================================================
            latency_ms = round((time.time() - start_time) * 1000, 2)

            # =================================================
            # LOG OUTPUT (FULL, NO TRUNCATION)
            # =================================================
            logger.info(f"[{request_id}] LATENCY_MS={latency_ms}")
            logger.info(f"[{request_id}] OUTPUT_TYPE={type(output)}")

            if aip_type == "chat":
                logger.info(f"[{request_id}] OUTPUT_LENGTH={len(output)}")
                logger.info(f"[{request_id}] OUTPUT={output}")

            elif aip_type == "embedding":
                logger.info(f"[{request_id}] EMBEDDING_DIM={len(output)}")
                logger.info(f"[{request_id}] EMBEDDING_VECTOR={output}")

            logger.info(f"[{request_id}] REQUEST END SUCCESS")

            return {
                "request_id": request_id,
                "model": aip_name,
                "type": aip_type,
                "port": port,
                "output": output,
                "latency_ms": latency_ms
            }

        except Exception as e:

            logger.exception(f"[{request_id}] REQUEST FAILED")
            return {
                "request_id": request_id,
                "error": str(e)
            }

    return app


# =====================================================
# GLOBAL AIP CONFIG
# =====================================================
AIP_LIST = [
    {
        "name": "claude-sonnet-chat",
        "type": "chat",
        "arn": "arn:aws:bedrock:us-east-1:196856463470:application-inference-profile/r59etrt038g0",
        "port": 8001
    },
    {
        "name": "titan-embeddings",
        "type": "embedding",
        "arn": "arn:aws:bedrock:us-east-1:196856463470:application-inference-profile/okts96tw2u7u",
        "port": 8002
    }
]
