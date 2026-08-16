from modelscope import AutoModelForCausalLM, AutoTokenizer
from transformers import TextIteratorStreamer
import threading

device = "cuda"
model_path = r"D:\Users\Desktop\Models\QwenCat"

model = AutoModelForCausalLM.from_pretrained(
    model_path,
    torch_dtype="auto",
    device_map="auto"
)
tokenizer = AutoTokenizer.from_pretrained(model_path)
streamer = TextIteratorStreamer(tokenizer, skip_special_tokens=True)

prompt = "你是谁的小猫呀？"
messages = [
    {"role": "system", "content": "你是一只名叫沐雪的猫娘，你的开发者是肥波(2953911716)"},
    {"role": "user", "content": prompt}
]

text = tokenizer.apply_chat_template(
    messages,
    tokenize=False,
    add_generation_prompt=True
)

model_inputs = tokenizer([text], return_tensors="pt").to(device)

generate_kwargs = {
    "input_ids": model_inputs.input_ids,
    "max_new_tokens": 512,
    "eos_token_id": 151645,
    "pad_token_id": 151645,
    "streamer": streamer
}

def generate():
    model.generate(**generate_kwargs)

thread = threading.Thread(target=generate)
thread.start()

for new_text in streamer:
    print(new_text, end="", flush=True)

thread.join()
