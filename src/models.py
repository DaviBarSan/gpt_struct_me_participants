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
import torch
# from text_generation import Client
from transformers import pipeline


from src.utils import is_json

logger = logging.getLogger(__name__)


ROOT = Path(__file__).parent.parent
MODELS_PATH = ROOT / "resources" / "models"

dotenv.load_dotenv(ROOT / ".env")

HF_KEY = os.getenv("HF_KEY")
# os.environ["REPLICATE_API_TOKEN"] = os.getenv("REPLICATE_KEY")
# Hard-disable FlashAttention
os.environ["TRANSFORMERS_NO_FLASH_ATTN"] = "1"
os.environ["TORCH_DISABLE_FLASH_ATTN"] = "1"

# Cache for the vLLM engine so qwen3_14b only pays the tensor-parallel model
# load cost once per process, not on every call.
_qwen3_14b_engine = None
_qwen3_8b_engine = None
_gemma3_12b_engine = None
_gemma3_4b_engine = None
_euro_llm_9b_engine = None

def qwen3_4b(prompt: str, temp: float):
    from transformers import pipeline
    # 1. Define the relative path you used
    relative_path = "/projects/F202500017AIVLABDEUCALION/davibsantos/gpt_struct_me_participants/resources/models/qwen3_4b"

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

# Original single-GPU (transformers pipeline) implementation, kept for reference.
# Superseded below by a vLLM version that tensor-parallelizes across 4 GPUs.
# def qwen3_14b(prompt: str, temp = 0.3):
#     from transformers import pipeline
#     # 1. Define the relative path you used
#     relative_path = "/data/davibarrel/gpt_struct_me_participants/resources/models/qwen3_14b"
#
#     # # 2. Convert the relative path to an absolute path
#     # os.path.abspath() handles relative parts like '..'
#     absolute_model_path = os.path.abspath(relative_path)
#     # absolute_model_path = 'C:/Users/davib/Desktop/MSc_DataScience/thesis/resources/models/Qwen3-4B'
#     print(f"Loading model from absolute path: {relative_path}")
#
#     # 3. Pass the ABSOLUTE path to the pipeline
#     pipe = pipeline("text-generation", model=relative_path)
#     messages = [
#         {"role": "user", "content": prompt},
#     ]
#     # 2. Call the pipeline and store the result
# # Crucial Argument: return_full_text=False
#     output = pipe(
# messages,
#         max_new_tokens=16384,
#         temperature=temp,          # Apply the temperature parameter
#         do_sample=True,            # do_sample must be True to use temperature
#         return_full_text=False
#     )
#
#     # 3. Extract the final text
#     # The output is a list of dictionaries, so we need to drill down.
#     generated_text = output[0]['generated_text']
#     print(generated_text)
#     return generated_text


def qwen3_14b(prompt: str, temp = 0.3):
    """vLLM version: tensor-parallelized across the 4 available GPUs."""
    global _qwen3_14b_engine
    from vllm import LLM, SamplingParams

    relative_path = "/data/davibarrel/gpt_struct_me_participants/resources/models/qwen3_14b"

    if _qwen3_14b_engine is None:
        print(f"Loading model from absolute path: {relative_path} (tensor_parallel_size=4)")
        _qwen3_14b_engine = LLM(model=relative_path,
                                tensor_parallel_size=4,
                                dtype="float16",                # <--- Forces FP16 for V100 GPUs)
                                enable_chunked_prefill=False,   # Bypasses Triton slice bug
                                enforce_eager=True              # Disables CUDA Graph Triton layout ops
                            )

    messages = [
        {"role": "user", "content": prompt},
    ]
    sampling_params = SamplingParams(
        temperature=temp,
        max_tokens=16384,
    )

    outputs = _qwen3_14b_engine.chat(messages, sampling_params)
    generated_text = outputs[0].outputs[0].text
    print(generated_text)
    return generated_text


def qwen3_8b(prompt: str, temp = 0.3):
    """vLLM version: tensor-parallelized across the 4 available GPUs."""
    global _qwen3_8b_engine
    from vllm import LLM, SamplingParams

    relative_path = "/data/davibarrel/gpt_struct_me_participants/resources/models/qwen3_8b"

    if _qwen3_8b_engine is None:
        print(f"Loading model from absolute path: {relative_path} (tensor_parallel_size=4)")
        _qwen3_8b_engine = LLM(model=relative_path,
                                tensor_parallel_size=4,
                                dtype="float16",                # <--- Forces FP16 for V100 GPUs)
                                enable_chunked_prefill=False,   # Bypasses Triton slice bug
                                enforce_eager=True              # Disables CUDA Graph Triton layout ops
                            )

    messages = [
        {"role": "user", "content": prompt},
    ]
    sampling_params = SamplingParams(
        temperature=temp,
        max_tokens=16384,
    )

    outputs = _qwen3_8b_engine.chat(messages, sampling_params)
    generated_text = outputs[0].outputs[0].text
    print(generated_text)
    return generated_text


def gemma3_12b(prompt: str, temp=0.3):
    """vLLM version tuned for Gemma 3 stability and execution limits."""
    global _gemma3_12b_engine
    from vllm import LLM, SamplingParams

    relative_path = "/data/davibarrel/gpt_struct_me_participants/resources/models/gemma3_12b"

    if _gemma3_12b_engine is None:
        print(f"Loading model from absolute path: {relative_path} (tensor_parallel_size=4)")
        _gemma3_12b_engine = LLM(
            model=relative_path,
            tensor_parallel_size=4,
            dtype="float32",                      # Fixes FP16 NaN soft-capping bug & empty output
            enable_chunked_prefill=False,      # Avoids Triton slice bug on Volta
            limit_mm_per_prompt={"image": 0},  # Bypasses vision pipeline for pure text
            max_model_len=16384,
            max_num_batched_tokens=16384,
            enforce_eager=False,
            gpu_memory_utilization=0.90,
        )

    messages = [
        {"role": "user", "content": prompt},
    ]
    
    # Cap max output tokens to prevent runaway generation loops
    sampling_params = SamplingParams(
        temperature=temp,
        max_tokens=2048,                      # Prevents infinite generation if EOS is missed
    )

    outputs = _gemma3_12b_engine.chat(messages, sampling_params)
    result = outputs[0].outputs[0]
    print(f"[gemma3_12b] finish_reason={result.finish_reason} output_tokens={len(result.token_ids)}")
    
    generated_text = result.text
    print(generated_text)
    return generated_text


def gemma3_4b(prompt: str, temp=0.3):
    """vLLM version tuned for Gemma 3 stability and execution limits."""
    global _gemma3_4b_engine
    from vllm import LLM, SamplingParams

    relative_path = "/data/davibarrel/gpt_struct_me_participants/resources/models/gemma3_4b"

    if _gemma3_4b_engine is None:
        print(f"Loading model from absolute path: {relative_path} (tensor_parallel_size=4)")
        _gemma3_4b_engine = LLM(
            model=relative_path,
            tensor_parallel_size=4,
            dtype="float32",                      # Fixes FP16 NaN soft-capping bug & empty output
            enable_chunked_prefill=False,      # Avoids Triton slice bug on Volta
            limit_mm_per_prompt={"image": 0},  # Bypasses vision pipeline for pure text
            max_model_len=16384,
            max_num_batched_tokens=16384,
            enforce_eager=False,
            gpu_memory_utilization=0.90,
        )

    messages = [
        {"role": "user", "content": prompt},
    ]
    
    # Cap max output tokens to prevent runaway generation loops
    sampling_params = SamplingParams(
        temperature=temp,
        max_tokens=2048,                      # Prevents infinite generation if EOS is missed
    )

    outputs = _gemma3_4b_engine.chat(messages, sampling_params)
    result = outputs[0].outputs[0]
    print(f"[gemma3_4b] finish_reason={result.finish_reason} output_tokens={len(result.token_ids)}")
    
    generated_text = result.text
    print(generated_text)
    return generated_text


def euro_llm_9b(prompt: str, temp=0.3):
    """vLLM version, using the same tensor-parallel/stability settings as gemma3_12b/4b."""
    global _euro_llm_9b_engine
    from vllm import LLM, SamplingParams

    relative_path = "/data/davibarrel/gpt_struct_me_participants/resources/models/euro_llm_9b"

    if _euro_llm_9b_engine is None:
        print(f"Loading model from absolute path: {relative_path} (tensor_parallel_size=4)")
        _euro_llm_9b_engine = LLM(
            model=relative_path,
            tensor_parallel_size=4,
            dtype="float32",                      # Fixes FP16 NaN soft-capping bug & empty output
            enable_chunked_prefill=False,      # Avoids Triton slice bug on Volta
            limit_mm_per_prompt={"image": 0},  # Bypasses vision pipeline for pure text
            max_model_len=16384,
            max_num_batched_tokens=16384,
            enforce_eager=False,
            gpu_memory_utilization=0.90,
        )

    messages = [
        {"role": "user", "content": prompt},
    ]

    # Cap max output tokens to prevent runaway generation loops
    sampling_params = SamplingParams(
        temperature=temp,
        max_tokens=2048,                      # Prevents infinite generation if EOS is missed
    )

    outputs = _euro_llm_9b_engine.chat(messages, sampling_params)
    result = outputs[0].outputs[0]
    print(f"[euro_llm_9b] finish_reason={result.finish_reason} output_tokens={len(result.token_ids)}")

    generated_text = result.text
    print(generated_text)
    return generated_text


def qwen35_9b(prompt: str, temp: float):
    from transformers import pipeline
    # 1. Define the relative path you used
    relative_path = "/projects/F202500017AIVLABDEUCALION/davibsantos/gpt_struct_me_participants/resources/models/qwen35_9b"

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


def qwen3_30b(prompt: str, temp: float):
    from transformers import pipeline
    # 1. Define the relative path you used
    relative_path = "/projects/F202500017AIVLABDEUCALION/davibsantos/gpt_struct_me_participants/resources/models/qwen3_30b"

    # # 2. Convert the relative path to an absolute path
    # os.path.abspath() handles relative parts like '..'
    absolute_model_path = os.path.abspath(relative_path)
    # absolute_model_path = 'C:/Users/davib/Desktop/MSc_DataScience/thesis/resources/models/Qwen3-4B'
    print(f"Loading model from absolute path: {relative_path}")

    # 3. Pass the ABSOLUTE path to the pipeline
    pipe = pipeline(
        "text-generation", 
        model=relative_path, 
        device_map="auto",
        torch_dtype=torch.float16,   # or bfloat16 if supported
        trust_remote_code=True
        )
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

def qwen25_14b(prompt: str, temp: float):
    from transformers import pipeline
    # 1. Define the relative path you used
    relative_path = "/projects/F202500017AIVLABDEUCALION/davibsantos/gpt_struct_me_participants/resources/models/qwen25_14b"

    # # 2. Convert the relative path to an absolute path
    # os.path.abspath() handles relative parts like '..'
    absolute_model_path = os.path.abspath(relative_path)
    # absolute_model_path = 'C:/Users/davib/Desktop/MSc_DataScience/thesis/resources/models/Qwen3-4B'
    print(f"Loading model from absolute path: {relative_path}")

    # 3. Pass the ABSOLUTE path to the pipeline
    pipe = pipeline(
        "text-generation", 
        model=relative_path, 
        device_map="auto",
        torch_dtype=torch.float16,   # or bfloat16 if supported
        trust_remote_code=True
        )
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

def gemini(prompt: str, temp: float) -> str:
    from google import genai
    from google.genai import types
    from time import sleep
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
    # print("Sleeping for 10 seconds to avoid rate limits...")
    # sleep(10)
    return answer

# Example Usage (assuming you have your API key set as an environment variable)
# print(gemini_generate_text("Explain the concept of quantum entanglement in simple terms."))

def amalia(prompt: str, temp: float = 0.0) -> str:
    """Generate text with the Amalia API (OpenAI-compatible, self-hosted at INESC-TEC)."""
    import openai

    # Bump to DEBUG so the request/response wire trace (connection open/reuse,
    # headers, retries) shows up in the log for debugging hangs/timeouts.
    client = openai.OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url="http://amalia.inesctec.pt:8000/v1",
        timeout=90,      # fail fast instead of hanging on a stale/broken connection over VPN
        max_retries=3,
    )

    completion = client.chat.completions.create(
        model="amalia-base",
        messages=[{"role": "user", "content": prompt}],
    )

    answer = completion.choices[0].message.content
    print(answer)
    return answer


def mistral_7b(prompt: str, temp: float) -> str:

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
    return  result
 
def phi_4_6b(prompt: str, temp: float):
    # 1. Path to the locally downloaded model
    relative_path = r"/projects/F202500017AIVLABDEUCALION/davibsantos/gpt_struct_me_participants/resources/models/Phi4-6B/Phi4_6b"
    absolute_model_path = os.path.abspath(relative_path)

    print(f"Loading model from: {absolute_model_path}")

    # 2. Create text-generation pipeline
    # IMPORTANT:
    # - Use text-generation (NOT vision2seq)
    # - Do NOT use AutoProcessor
    # - trust_remote_code=True is required for Phi models
    pipe = pipeline(
        task="text-generation",
        model=absolute_model_path,
        tokenizer=absolute_model_path,
        torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
        device_map="auto",
        trust_remote_code=True,
	model_kwargs={
        	"attn_implementation": "sdpa"
    	}
    )

    # 3. Chat-style messages (Phi-4 supports this natively)
    messages = [
        {"role": "user", "content": prompt}
    ]

    # 4. Run generation
    output = pipe(
        messages,
        max_new_tokens=2048,
        return_full_text=False,   # return only the assistant answer
        do_sample=False
    )

    # 5. Extract generated text
    generated_text = output[0]["generated_text"]
    return generated_text


def gemma3_1b(prompt : str):

	path_to_model = "/projects/F202500017AIVLABDEUCALION/davibsantos/gpt_struct_me_participants/resources/models/gemma3-1b"
	tokenizer = AutoTokenizer.from_pretrained(path_to_model)
	model = AutoModelForCausalLM.from_pretrained(path_to_model)
	messages = [
	    {"role": "user", "content": prompt},
	]
	inputs = tokenizer.apply_chat_template(
		messages,
		add_generation_prompt=True,
		tokenize=True,
		return_dict=True,
		return_tensors="pt",
	).to(model.device)

	outputs = model.generate(**inputs, max_new_tokens=4096)
	response = tokenizer.decode(outputs[0][inputs["input_ids"].shape[-1]:])
	return response

def llama32_3b(prompt:str) -> str:
    relative_path = "/projects/F202500017AIVLABDEUCALION/davibsantos/gpt_struct_me_participants/resources/models/llama32-3b"

    tokenizer = AutoTokenizer.from_pretrained(relative_path)
    model = AutoModelForCausalLM.from_pretrained(relative_path,    
    device_map="auto",
    torch_dtype=torch.float16,   # or bfloat16 if supported
    trust_remote_code=True
    )
    messages = [
        {"role": "user", "content": prompt},
    ]
    inputs = tokenizer.apply_chat_template(
        messages,
        add_generation_prompt=True,
        tokenize=True,
        return_dict=True,
        return_tensors="pt",
    ).to(model.device)

    outputs = model.generate(**inputs, max_new_tokens=4096)
    result = tokenizer.decode(outputs[0][inputs["input_ids"].shape[-1]:])
    return result
