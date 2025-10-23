#!/usr/bin/env python3
"""
Script to create an Application Inference Profile (AIP) for a given model ARN in Bedrock
"""

import boto3
import json
import argparse

def create_aip(model_arn: str, aip_name: str, region: str = "us-east-1", description: str = None):
    """
    Create an Application Inference Profile for a given Bedrock model
    """
    client = boto3.client("bedrock", region_name=region)

    try:
        params = {
            "inferenceProfileName": aip_name,
            "modelSource": {
                "copyFrom": model_arn
            }
        }
        if description:
            params["description"] = description

        response = client.create_inference_profile(**params)

        print("✅ AIP created successfully!")
        print(json.dumps(response, indent=2, default=str))

    except client.exceptions.ConflictException:
        print(f"❌ AIP with name '{aip_name}' already exists.")
    except Exception as e:
        print(f"❌ Error creating AIP: {str(e)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a Bedrock Application Inference Profile (AIP)")
    parser.add_argument("--model-arn", required=True, help="The ARN of the Bedrock model")
    parser.add_argument("--name", required=True, help="Name of the AIP to create")
    parser.add_argument("--region", default="us-east-1", help="AWS region (default: us-east-1)")
    parser.add_argument("--description", help="Optional description for the AIP")

    args = parser.parse_args()

    create_aip(args.model_arn, args.name, args.region, args.description)
