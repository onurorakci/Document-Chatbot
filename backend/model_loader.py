from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from rag import get_relevant_context, get_chunk_count
import torch

_loaded_model = None
_loaded_tokenizer = None

rule_text = """You are a strict document-based assistant.

        Critical rules:
        - Answer ONLY using the provided document
        - Do NOT use prior knowledge 
        - If you find relevant information in the document, YOU MUST use it to answer
        - If you cannot find the information in the document, only say "This information is not in the document." 
        Document:"""

def _get_trimmed_messages(tokenizer, context_messages, chat_history, current_message, max_tokens):
    trimmed_history = chat_history.copy()
    
    while True:
        # Merge context, trimmed history, and current message to test token count
        test_messages = context_messages + trimmed_history + [{"role": "user", "content": current_message}]
        
        # Calculate total tokens for the test messages
        text = tokenizer.apply_chat_template(
            test_messages,
            tokenize=False,
            add_generation_prompt=False,
            enable_thinking=False
        )
        total_tokens = len(tokenizer.encode(text))
        
        # If total tokens are within the limit, return the messages; otherwise, trim the history
        if total_tokens <= max_tokens or len(trimmed_history) == 0:
            return test_messages, total_tokens, len(trimmed_history)
            
        # En eski mesaj çiftini sil (User + Assistant)
        trimmed_history = trimmed_history[2:]

# Load the model with 4-bit quantization for efficient inference
def load_model(model_name="Qwen/Qwen3-1.7B"):
    global _loaded_model, _loaded_tokenizer, rule_text
    
    print(f"Loading model: {model_name} with 4-bit quantization...")

    # 4-bit quantization configuration for memory efficiency
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_use_double_quant=True,
        bnb_4bit_quant_type="nf4"
    )
    tokenizer = AutoTokenizer.from_pretrained(model_name)

    # Load the model with the specified quantization configuration and memory optimizations
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        device_map="auto",
        quantization_config=bnb_config,
        torch_dtype=torch.float16,
        low_cpu_mem_usage=True
    )
    _loaded_model = model
    _loaded_tokenizer = tokenizer
    return model, tokenizer

# Generate a response based on the provided context, user message, and chat history
def generate_response(chat_id: str, context: str, message: str, chat_history: list, max_tokens: int = 2048) -> str: 
    
    # Retrieve relevant context chunks from the RAG vectorstore based on the user message
    k = max(3, int(get_chunk_count(chat_id) / 20))  # minimum 3
    context = get_relevant_context(chat_id=chat_id, question=message, k=k)
    
    # Prepare the messages for the model, starting with the system prompt that includes the rules and retrieved context, followed by the chat history and current user message
    context_messages = [{
        "role": "system",
        "content": f"{rule_text}\n{context}"
    }]

    # Trim the chat history if the total token count exceeds the model's maximum context length, 
    # ensuring that the most recent interactions are prioritized while still including as much relevant history as possible within the token limit
    final_messages, total_tokens, final_history_len = _get_trimmed_messages(
        _loaded_tokenizer, context_messages, chat_history, message, max_tokens
    )

    # Debugging output to check token counts and history length after trimming
    #print(f"[DEBUG] Total tokens after trimming: {total_tokens} | History length: {final_history_len}")

    # The final text is created by applying the chat template to the combined messages, and then tokenized for input into the model.
    final_text = _loaded_tokenizer.apply_chat_template(
        final_messages,
        tokenize=False,
        add_generation_prompt=True
    )
    
    # Generate the model's response 
    inputs = _loaded_tokenizer(final_text, return_tensors="pt").to(_loaded_model.device)
    
    with torch.no_grad():
        output = _loaded_model.generate(
            inputs.input_ids,
            max_new_tokens=512, # Limit the response length to prevent excessive generation and potential token limit issues
            do_sample=False,    # Disable sampling for deterministic output
            #temperature=0.1,   # Lower temperature for more focused responses, when do_sampple is enabled
            pad_token_id=_loaded_tokenizer.eos_token_id, # Ensure proper padding
            repetition_penalty=1.1,
        )

    # Decoding
    new_tokens = output[0][inputs.input_ids.shape[1]:]
    full_response = _loaded_tokenizer.decode(new_tokens, skip_special_tokens=True)
    
    # Deleting the "think" part if it exists
    content = _parse_model_response(full_response)

    return content

def _parse_model_response(response: str) -> str:
    if "</think>" in response:
        return response.split("</think>")[1].strip()
    if "<think>" in response:
        return "⚠️ The model is trying to think but did not finish. This may be due to token limits. Here's the partial response:\n\n" + response.split("<think>")[0].strip()
    return response