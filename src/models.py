"""Models to be used in the research."""

import json
import os
import logging
import requests
from pathlib import Path

# import replicate
# import boto3
import dotenv
# import openai
# import transformers
from transformers import AutoTokenizer, AutoModelForCausalLM
# import torch
# from text_generation import Client
from transformers import pipeline


from src.utils import is_json

logger = logging.getLogger(__name__)


ROOT = Path(__file__).parent.parent
MODELS_PATH = ROOT / "resources" / "models"

dotenv.load_dotenv(ROOT / ".env")

HF_KEY = os.getenv("HF_KEY")
# os.environ["REPLICATE_API_TOKEN"] = os.getenv("REPLICATE_KEY")


def qwen3_4b(prompt: str):
    from transformers import pipeline
    # 1. Define the relative path you used
    relative_path = "/projects/F202500017AIVLABDEUCALION/davibsantos/gpt_struct_me_participants/resources/models/Qwen3-4B/Qwen3_4B"

    # # 2. Convert the relative path to an absolute path
    # os.path.abspath() handles relative parts like '..'
    absolute_model_path = os.path.abspath(relative_path)
    # absolute_model_path = 'C:/Users/davib/Desktop/MSc_DataScience/thesis/resources/models/Qwen3-4B'
    print(f"Loading model from absolute path: {relative_path}")

    # 3. Pass the ABSOLUTE path to the pipeline
    pipe = pipeline("text-generation", model=relative_path)
    messages = [
        {"role": "user", "content": prompt},
    ]
    # 2. Call the pipeline and store the result
# Crucial Argument: return_full_text=False
    output = pipe(
        messages,
        max_new_tokens=16384,
        return_full_text=False      # Tells the pipeline to return ONLY the generated text
    )

    # 3. Extract the final text
    # The output is a list of dictionaries, so we need to drill down.
    generated_text = output[0]['generated_text']
    print(generated_text)
    return generated_text


def gemini(prompt: str) -> str:
    from google import genai
    from google.genai import types
    """Generate text with the Gemini API."""
    
    # 1. Initialize the client. The client will automatically look for the 
    # GEMINI_API_KEY environment variable.
    client = genai.Client()

    # 2. Configure generation parameters like temperature and max_output_tokens.
    # The max_tokens parameter is mapped to max_output_tokens in Gemini.
    # The temperature is a direct equivalent.
    config = types.GenerateContentConfig(
        temperature=0,  # Matches the original temperature
         # Matches the original max_tokens
    )
    print(f"Gemini Prompt: {prompt}")
    print(f"Gemini Config: {config}")
    # 3. Call the models.generate_content method.
    response = client.models.generate_content(
        model="gemini-2.5-flash",  # A modern, fast, and capable model
        contents=prompt,           # The input prompt
        config=config,             # The generation parameters
    )

    # 4. Extract the generated text.
    # Unlike OpenAI's Completion API, the Gemini generate_content response 
    # provides the text directly via the .text attribute.
    answer = response.text
    print(f"Gemini Response: {response}")
    return answer

# Example Usage (assuming you have your API key set as an environment variable)
# print(gemini_generate_text("Explain the concept of quantum entanglement in simple terms."))

def mistral_7b(prompt: str) -> str:    

   ##MISTRAL
    from mistral_inference.transformer import Transformer
    from mistral_inference.generate import generate

    from mistral_common.tokens.tokenizers.mistral import MistralTokenizer
    from mistral_common.protocol.instruct.messages import UserMessage
    from mistral_common.protocol.instruct.request import ChatCompletionRequest
    relative_path = "C:\\Users\davib\Desktop\\MSc_DataScience\\thesis\gpt_struct_me\\resources\\models\\Mistral-7B"

    tokenizer = MistralTokenizer.from_file(f"{relative_path}\\tokenizer.model.v3")
    model = Transformer.from_folder(relative_path)
    completion_request = ChatCompletionRequest(messages=[UserMessage(content=prompt)])
    tokens = tokenizer.encode_chat_completion(completion_request).tokens

    out_tokens, _ = generate([tokens], model, max_tokens=16384, temperature=0.0, eos_id=tokenizer.instruct_tokenizer.tokenizer.eos_id)
    result = tokenizer.instruct_tokenizer.tokenizer.decode(out_tokens[0])

    print(result)
    return result

def phi_4_6b(prompt: str):
    # 1. Define the relative path you used
    relative_path = "C:\\Users\davib\Desktop\\MSc_DataScience\\thesis\gpt_struct_me\\resources\models\Phi4-6B"

    # # 2. Convert the relative path to an absolute path
    # os.path.abspath() handles relative parts like '..'
    absolute_model_path = os.path.abspath(relative_path)
    print(f"Loading model from absolute path: {relative_path}")

    # 3. Pass the ABSOLUTE path to the pipeline
    pipe = pipeline("text-generation", model=relative_path)
    messages = [
        {"role": "user", "content": prompt},
    ]
    # 2. Call the pipeline and store the result
# Crucial Argument: return_full_text=False
    output = pipe(
        messages,
        max_new_tokens=16384,
        return_full_text=False      # Tells the pipeline to return ONLY the generated text
    )

    # 3. Extract the final text
    # The output is a list of dictionaries, so we need to drill down.
    generated_text = output[0]['generated_text']
    print(generated_text)
    return generated_text
