import argparse
import gc
import locale
import logging
import os

import accelerate
import numpy as np
import pandas as pd
import torch
from modded_scorer import modded_scorer
from transformers import AutoModelForCausalLM, AutoTokenizer

locale.setlocale(locale.LC_ALL, "C.UTF-8")
os.environ["HF_HOME"] = "/work/users/a/u/aum/models"
logging.basicConfig(filename="/work/users/a/u/aum/debug.log", level=logging.DEBUG)


def generate_followup(model, tokenizer, sentence, max_length=30):
    input_text = f"{sentence} The answer to the question: Who"
    input_ids = tokenizer.encode(input_text, return_tensors="pt").to("cuda")

    output = model.generate(
        input_ids,
        max_length=max_length,
        num_return_sequences=1,
        do_sample=True,
        temperature=0.7,
        top_p=0.95,
    )

    generated_text = tokenizer.decode(output[0], skip_special_tokens=True)
    followup = generated_text[len(input_text) :].strip()
    return followup


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--auth-token", type=str)
    parser.add_argument("--path-to-model-stimuli", type=str)
    parser.add_argument("--output-file-path", type=str)
    args = parser.parse_args()
    get_model_results(args)


def get_model_results(args):
    path_to_model_stimuli = args.path_to_model_stimuli
    output_file_path = args.output_file_path
    auth_token = args.auth_token

    dataset_df = pd.read_csv(path_to_model_stimuli)
    sentences = dataset_df["sentence"].tolist()
    predefined_followups = dataset_df["followup"].tolist()
    print("Data ready!")

    model_name = "meta-llama/Meta-Llama-3-8B"
    quantization_bool = False
    print(f"Loading model: {model_name}")
    print(f"Using quantization: {quantization_bool}")

    # Load model and tokenizer for generation
    tokenizer = AutoTokenizer.from_pretrained(model_name, use_auth_token=auth_token)
    generator_model = AutoModelForCausalLM.from_pretrained(
        model_name,
        use_auth_token=auth_token,
        device_map="auto",
        load_in_8bit=quantization_bool,
    )

    # Generate followups
    generated_followups = [
        generate_followup(generator_model, tokenizer, sentence)
        for sentence in sentences
    ]

    # Score both predefined and generated followups
    modelscorer = modded_scorer.IncrementalLMScorer(
        model_name, auth_token=auth_token, device="cuda", load_in_8bit=quantization_bool
    )

    predefined_scores = [
        sum(x)
        for x in modelscorer.compute_stats(
            modelscorer.prime_text(sentences, predefined_followups)
        )
    ]
    generated_scores = [
        sum(x)
        for x in modelscorer.compute_stats(
            modelscorer.prime_text(sentences, generated_followups)
        )
    ]

    # Add results to dataframe
    dataset_df["Meta-Llama-3-8B_predefined"] = predefined_scores
    dataset_df["Meta-Llama-3-8B_generated"] = generated_scores
    dataset_df["generated_followup"] = generated_followups

    # Clean up
    del generator_model, modelscorer.model
    gc.collect()
    torch.cuda.empty_cache()

    dataset_df.to_csv(output_file_path, index=False)
    print(f"Results saved to {output_file_path}")
    return


if __name__ == "__main__":
    main()
