import boto3

client = boto3.client("bedrock", region_name="us-east-1")

paginator = client.get_paginator("list_inference_profiles")

for page in paginator.paginate(typeEquals="APPLICATION"):
    for profile in page.get("inferenceProfileSummaries", []):
        print(profile["inferenceProfileArn"], "-", profile.get("name") or profile.get("inferenceProfileName"))
