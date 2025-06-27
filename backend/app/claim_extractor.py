# backend/app/claim_extractor.py
import json
from transformers import (
  AutoTokenizer,
  AutoModelForCausalLM,
  BitsAndBytesConfig,
  pipeline,
)
from typing import List

# 1) Setup 4-bit quantization to reduce VRAM (<6 GB)
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype="float16",
    bnb_4bit_use_double_quant=True,
)

# 2) Load tokenizer & model once
tokenizer = AutoTokenizer.from_pretrained("mistral-inference/mistral-7b")
model = AutoModelForCausalLM.from_pretrained(
    "mistral-inference/mistral-7b",
    quantization_config=bnb_config,
    device_map="auto",
    trust_remote_code=True,
)

# 3) Wrap in a pipeline
extractor = pipeline(
    "text2text-generation",
    model=model,
    tokenizer=tokenizer,
    max_new_tokens=512,
    temperature=0.0,
    device_map="auto",
)

def extract_claims(transcript: str) -> List[str]:
    prompt = (
        "You are a medical researcher. Extract every discrete medical claim "
        "or recommendation from the text below. Return a JSON array of concise statements.\n\n"
        f"Transcript:\n'''{transcript}'''\n\nOutput:"
    )
    raw = extractor(prompt)[0]["generated_text"]
    # 4) Try to parse JSON
    try:
        return [c.strip() for c in json.loads(raw)]
    except json.JSONDecodeError:
        # Fallback: split lines
        return [ln.strip("-* ") for ln in raw.splitlines() if len(ln) > 20]
