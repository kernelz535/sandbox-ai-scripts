import requests
import json

BASE_URLS = [
    "http://172.17.197.211:8001/invoke",  # chat
    "http://172.17.197.211:8002/invoke"   # embedding
]

prompts = [
    "What is AWS Bedrock?",
    "Explain ECS Fargate",
    "Write Python code for CSV parsing",
    "What is DynamoDB?",
    "Compare ECS and EKS"
]

headers = {
    "Content-Type": "application/json"
}

for url in BASE_URLS:

    print("\n" + "=" * 100)
    print(f"TESTING MODEL: {url}")

    for prompt in prompts:

        payload = {
            "text": prompt
        }

        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=120
        )

        data = response.json()

        print("\n---")
        print("PROMPT:", prompt)
        print("TYPE:", data.get("type"))
        print("LATENCY:", data.get("latency_ms"))

        output = data.get("output")

        if isinstance(output, list):
            print("EMBEDDING SIZE:", len(output))
            print("FIRST 5 VALUES:", output[:5])
        else:
            print("RESPONSE:")
            print(output)
