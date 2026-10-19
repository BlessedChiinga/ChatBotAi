from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

model_name = "Qwen/Qwen2.5-1.5B-Instruct"

print("Loading tokenizer...")
tokenizer = AutoTokenizer.from_pretrained(model_name)

print("Loading model...")
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype="auto",
    device_map="cpu",
)

messages = [
    {
        "role": "user",
        "content": "Explain what a computer is in one short sentence."
    }
]

prompt = tokenizer.apply_chat_template(
    messages,
    tokenize=False,
    add_generation_prompt=True,
)

inputs = tokenizer(prompt, return_tensors="pt")

print("Generating answer...")
with torch.no_grad():
    outputs = model.generate(
        **inputs,
        max_new_tokens=60,
        do_sample=False,
    )

answer_tokens = outputs[0][inputs["input_ids"].shape[1]:]
print("\nQwen answer:")
print(tokenizer.decode(answer_tokens, skip_special_tokens=True))