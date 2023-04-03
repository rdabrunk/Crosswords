import pandas as pd
import torch
from transformers import GPT2Tokenizer, GPT2Model, TFGPT2LMHeadModel

if __name__ == '__main__':
    # Load the GPT-2 model and tokenizer
    model = TFGPT2LMHeadModel.from_pretrained('gpt2')
    tokenizer = GPT2Tokenizer.from_pretrained('gpt2')

    # Generate some sample text
    input_text = 'The boy was walking down the street when he saw a'
    input_ids = tokenizer.encode(input_text, return_tensors='tf')
    output = model.generate(input_ids, max_length=50, do_sample=True)

    # Decode the output tokens back to text
    output_text = tokenizer.decode(output[0], skip_special_tokens=True)

    print('Input:', input_text)
    print('Output:', output_text)

