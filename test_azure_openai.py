#!/usr/bin/env python3
"""Test script to debug Azure OpenAI content filtering."""

from __future__ import annotations

import json
import os

from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI

load_dotenv()


def _test_prompts(llm: AzureChatOpenAI) -> None:
    test_prompts = [
        "Hello, how are you?",
        "What is 2 + 2?",
        "You bruh",  # The message that triggered filtering in langclaw
    ]

    for prompt in test_prompts:
        print(f"\n>>> Prompt: {prompt!r}")
        try:
            response = llm.invoke(prompt)
            print(f"<<< Response: {response.content}")
            # Check for content filter indicators
            meta = response.response_metadata
            if meta.get("incomplete_details"):
                print(f"    !!! FILTERED: {meta['incomplete_details']}")
            if meta.get("finish_reason") != "stop":
                print(f"    finish_reason: {meta.get('finish_reason')}")
        except Exception as e:
            print(f"!!! Error: {e}")


def main() -> None:
    # Parse model name from LANGCLAW__AGENTS__MODEL (format: "azure_openai:gpt-5.1-chat")
    model_config = os.environ.get("LANGCLAW__AGENTS__MODEL", "azure_openai:gpt-5.1-chat")
    _, deployment_name = model_config.split(":", 1) if ":" in model_config else ("", model_config)

    # Parse model_kwargs from env (langclaw config)
    model_kwargs_str = os.environ.get("LANGCLAW__AGENTS__MODEL_KWARGS", "{}")
    model_kwargs = json.loads(model_kwargs_str)

    # Extract langclaw-specific settings
    use_responses_api = model_kwargs.pop("use_responses_api", False)
    responses_api_version = model_kwargs.pop("api_version", "2025-03-01-preview")
    chat_api_version = os.environ.get("OPENAI_API_VERSION", "2025-01-01-preview")

    print(f"Endpoint: {os.environ.get('AZURE_OPENAI_ENDPOINT')}")
    print(f"Deployment: {deployment_name}")
    print(f"Langclaw use_responses_api: {use_responses_api}")
    print(f"Langclaw api_version: {responses_api_version}")
    print(f"Default api_version: {chat_api_version}")
    print("=" * 60)

    # Test 1: Chat Completions API (default)
    print("\n### Test 1: Chat Completions API ###")
    print(f"(use_responses_api=False, api_version={chat_api_version})")
    llm_chat = AzureChatOpenAI(
        azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
        api_key=os.environ["AZURE_OPENAI_API_KEY"],
        api_version=chat_api_version,
        azure_deployment=deployment_name,
        use_responses_api=False,
    )
    _test_prompts(llm_chat)

    # Test 2: Responses API (langclaw config)
    print("\n" + "=" * 60)
    print("\n### Test 2: Responses API (langclaw config) ###")
    print(f"(use_responses_api={use_responses_api}, api_version={responses_api_version})")
    llm_responses = AzureChatOpenAI(
        azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
        api_key=os.environ["AZURE_OPENAI_API_KEY"],
        api_version=responses_api_version,
        azure_deployment=deployment_name,
        use_responses_api=use_responses_api,
    )
    _test_prompts(llm_responses)


if __name__ == "__main__":
    main()
