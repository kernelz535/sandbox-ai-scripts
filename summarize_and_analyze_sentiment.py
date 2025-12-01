def summarize_and_analyze_sentiment(model_id: str, content: str) -> tuple:

    text_len = len(content)

    # Dynamic summary instruction
    if text_len > 2000:
        summary_instruction = "Write a very short summary (2–3 lines max)."
    elif text_len > 800:
        summary_instruction = "Write a short but informative summary (4–6 lines)."
    else:
        summary_instruction = "Write a detailed summary (6–8 lines) since the text is small."

    prompt = f"""
You are an expert summarizer.

{summary_instruction}

Also provide:
- Sentiment label: POSITIVE or NEGATIVE
- Sentiment score: between -1.0 and 1.0

Return exactly in this format:
SUMMARY: <text>
SENTIMENT_LABEL: <POSITIVE/NEGATIVE>
SENTIMENT_SCORE: <value>

Text to summarize:
{content}
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
