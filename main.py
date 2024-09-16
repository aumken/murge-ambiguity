import argparse
import subprocess
import sys
import json
import os
import torch
from torch.nn.functional import softmax
from transformers import AutoModelForCausalLM, AutoTokenizer
import logging
import math
from collections import defaultdict
import pandas as pd
import random

import locale
locale.setlocale(locale.LC_ALL, 'C.UTF-8')

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

try:
    import transformers
except ImportError:
    install("transformers")

os.environ['HF_HOME'] = "/work/users/a/u/aum/models"

logging.basicConfig(filename='/work/users/a/u/aum/debug.log', level=logging.DEBUG)

few_shot_examples = [
    {
        "question": "What is the capital of France?",
        "options": ["London", "Berlin", "Paris", "Madrid"],
        "answer": "Paris"
    },
    {
        "question": "Who wrote 'Romeo and Juliet'?",
        "options": ["Charles Dickens", "William Shakespeare", "Jane Austen", "Mark Twain"],
        "answer": "William Shakespeare"
    },
    {
        "question": "What is the largest planet in our solar system?",
        "options": ["Mars", "Jupiter", "Saturn", "Earth"],
        "answer": "Jupiter"
    },
    {
        "question": "In what year did World War II end?",
        "options": ["1943", "1944", "1945", "1946"],
        "answer": "1945"
    },
    {
        "question": "What is the chemical symbol for gold?",
        "options": ["Au", "Ag", "Fe", "Cu"],
        "answer": "Au"
    }
]

few_shot_ambiguity_examples = [
    {
        "question": "Can you meet me by the bank?",
        "options": ["Yes", "No"],
        "answer": "Yes",
        "explanation": "This is ambiguous because 'bank' could refer to a financial institution or a river bank."
    },
    {
        "question": "What is the capital of France?",
        "options": ["Yes", "No"],
        "answer": "No",
        "explanation": "This is unambiguous as it has a clear, single answer."
    },
    {
        "question": "She saw the man with binoculars.",
        "options": ["Yes", "No"],
        "answer": "Yes",
        "explanation": "This is ambiguous because it's unclear if she used the binoculars to see the man, or if the man had binoculars."
    },
    {
        "question": "How many planets are in our solar system?",
        "options": ["Yes", "No"],
        "answer": "No",
        "explanation": "This is unambiguous as it has a definite answer based on current scientific classification."
    },
    {
        "question": "The chicken is ready to eat.",
        "options": ["Yes", "No"],
        "answer": "Yes",
        "explanation": "This is ambiguous because it could mean the chicken is prepared for consumption or that the chicken itself is hungry."
    }
]

class AmbiguityTester:
    def __init__(self, model_name, data_dir, eval_type, ambiguity_mode, test_mode=False, verbose=False, open_ended=False, randomize_options=False):
        self.model_name = model_name
        self.data_dir = data_dir
        self.eval_type = eval_type
        self.ambiguity_mode = ambiguity_mode
        self.randomize_options = randomize_options
        self.tokenizer = AutoTokenizer.from_pretrained(model_name, token="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")
        self.model = AutoModelForCausalLM.from_pretrained(model_name, token="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")
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)
        self.stats = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(float))))
        self.counts = defaultdict(lambda: defaultdict(int))
        self.prob_diff_stats = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
        self.test_mode = test_mode
        self.verbose = verbose
        self.open_ended = open_ended
        self.tokenizer.pad_token = self.tokenizer.eos_token
        self.model.config.pad_token_id = self.model.config.eos_token_id

    def format_question(self, question, options):
        prompt = f"{question}\n"
        for option in options:
            prompt += f"- {option}\n"
        return prompt

    def format_few_shot_example(self, example):
        prompt = self.format_question(example['question'], example['options'])
        prompt += f" {example['answer']}\n\n"
        return prompt

    def gen_prompt(self, question, options):
        if self.ambiguity_mode == "prompt":
            prompt = "Pay special attention to ambiguity in the question.\n\n"
        elif self.ambiguity_mode == "direct":
            prompt = "Determine if the following question is ambiguous. Answer with 'Yes' if it is ambiguous, or 'No' if it is not ambiguous.\n\n"
            options = ["Yes", "No"]
            
            if self.eval_type == "few_shot":
                prompt += "Here are some examples:\n\n"
                for example in few_shot_ambiguity_examples:
                    prompt += f"Question: {example['question']}\n"
                    prompt += f"Is this question ambiguous? {example['answer']}\n"
                    prompt += f"Explanation: {example['explanation']}\n\n"
        else:
            prompt = ""
        
        if self.eval_type == "original":
            prompt += self.format_question(question, options)
        elif self.eval_type == "zero_shot":
            if self.ambiguity_mode == "direct":
                prompt += f"Question: {question}\nIs this question ambiguous? (Yes/No)\n"
            else:
                prompt += "Answer the following question by choosing one of the provided options:\n\n" + self.format_question(question, options)
        elif self.eval_type == "few_shot":
            if self.ambiguity_mode != "direct":
                prompt += "Answer the following questions by choosing one of the provided options:\n\n"
                for example in few_shot_examples:
                    prompt += self.format_few_shot_example(example)
            prompt += self.format_question(question, options)
        
        return prompt, options
    
    def get_answer_probs(self, prompt, answers):
        inputs = self.tokenizer(prompt, return_tensors="pt", padding=True, truncation=True).to(self.device)
        
        with torch.no_grad():
            outputs = self.model(**inputs)
        
        last_token_logits = outputs.logits[0, -1, :]
        
        answer_probs = []
        for answer in answers:
            answer_tokens = self.tokenizer.encode(f" {answer}", add_special_tokens=False)
            full_seq_prob = 1.0
            min_prob = float('inf')
            avg_prob = 0
            first_token_prob = None
            
            for i, token in enumerate(answer_tokens):
                token_prob = softmax(last_token_logits, dim=-1)[token].item()
                full_seq_prob *= token_prob
                min_prob = min(min_prob, token_prob)
                avg_prob += token_prob
                if i == 0:
                    first_token_prob = token_prob
            
            avg_prob /= len(answer_tokens)
            answer_probs.append((full_seq_prob, min_prob, avg_prob, first_token_prob))

        total_full = sum(p[0] for p in answer_probs)
        total_min = sum(p[1] for p in answer_probs)
        total_avg = sum(p[2] for p in answer_probs)
        total_first = sum(p[3] for p in answer_probs)

        normalized_probs = [
            (p[0] / total_full, p[1] / total_min, p[2] / total_avg, p[3] / total_first)
            for p in answer_probs
        ]

        return normalized_probs

    def calculate_entropy(self, probs):
        return -sum(p * math.log(p) for p in probs if p > 0)

    def calculate_entropies_and_prob_diff(self, probs):
        methods = ['full', 'min', 'avg', 'first']
        entropies = {}
        prob_diffs = {}
        for i, method in enumerate(methods):
            method_probs = [p[i] for p in probs]
            total_prob = sum(method_probs)
            normalized_probs = [p / total_prob for p in method_probs]
            entropies[method] = self.calculate_entropy(normalized_probs)
            
            if len(normalized_probs) > 1:
                sorted_probs = sorted(normalized_probs, reverse=True)
                prob_diffs[method] = sorted_probs[0] - sorted_probs[1]
            else:
                prob_diffs[method] = 0
        
        return entropies, prob_diffs

    def generate_open_ended_response(self, prompt, answers, max_length=50):
        # Modify the prompt to encourage a direct answer
        modified_prompt = prompt + "\nAnswer: "
        
        inputs = self.tokenizer(modified_prompt, return_tensors="pt", padding=True, truncation=True).to(self.device)
        
        with torch.no_grad():
            outputs = self.model.generate(
                input_ids=inputs.input_ids,
                attention_mask=inputs.attention_mask,
                max_new_tokens=max_length,  # Use max_new_tokens instead of max_length
                num_return_sequences=1,
                do_sample=True,
                temperature=0.5,
                top_p=0.7,  # Add top_p sampling
                pad_token_id=self.tokenizer.pad_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
            )
        
        response = self.tokenizer.decode(outputs[0][inputs.input_ids.shape[1]:], skip_special_tokens=True)
        
        # Clean up the response
        response = response.strip()
        if response.lower().startswith("answer:"):
            response = response[7:].strip()
        
        return response
    
    def process_file(self, file_path, category, ambiguity):
        with open(file_path, "r") as file:
            data = json.load(file)

        if self.test_mode:
            data = random.sample(data, min(100, len(data)))

        self.counts[category][ambiguity] = len(data)

        for item in data:
            mcq_question = item['mc_question']['question']
            mcq_options = [option['answer'] for option in item['mc_question']['options']]
            
            if self.randomize_options:
                random.shuffle(mcq_options)
            
            mcq_prompt, mcq_options = self.gen_prompt(mcq_question, mcq_options)
            mcq_probs = self.get_answer_probs(mcq_prompt, mcq_options)
            mcq_entropies, mcq_prob_diffs = self.calculate_entropies_and_prob_diff(mcq_probs)
            
            mcq_open_response = self.generate_open_ended_response(mcq_prompt, mcq_options) if self.open_ended else "Open-ended responses not enabled"

            comp_question = item['completion']['prompt']
            comp_options = [pair['answer'][0] for pair in item['completion']['qaPairs']]
            
            if self.randomize_options:
                random.shuffle(comp_options)
            
            comp_prompt, comp_options = self.gen_prompt(comp_question, comp_options)
            comp_probs = self.get_answer_probs(comp_prompt, comp_options)
            comp_entropies, comp_prob_diffs = self.calculate_entropies_and_prob_diff(comp_probs)
            
            comp_open_response = self.generate_open_ended_response(comp_prompt, comp_options) if self.open_ended else "Open-ended responses not enabled"

            if self.verbose:
                print(f"\nDataset: {category}")
                print(f"Ambiguity: {ambiguity}")
                print(f"MCQ Full Prompt:")
                print(mcq_prompt)
                print("\nMCQ Answer Choices and Probabilities:")
                for answer, probs in zip(mcq_options, mcq_probs):
                    print(f"  Answer: {answer}")
                    print(f"    Full: {probs[0]:.6f}")
                    print(f"    Min: {probs[1]:.6f}")
                    print(f"    Avg: {probs[2]:.6f}")
                    print(f"    First: {probs[3]:.6f}")
                print("MCQ Entropies:")
                for method, entropy in mcq_entropies.items():
                    print(f"  {method.capitalize()}: {entropy:.6f}")
                print(f"MCQ Open-ended Response: {mcq_open_response}")
                
                print(f"\nCompletion Full Prompt:")
                print(comp_prompt)
                print("\nCompletion Answer Choices and Probabilities:")
                for answer, probs in zip(comp_options, comp_probs):
                    print(f"  Answer: {answer}")
                    print(f"    Full: {probs[0]:.6f}")
                    print(f"    Min: {probs[1]:.6f}")
                    print(f"    Avg: {probs[2]:.6f}")
                    print(f"    First: {probs[3]:.6f}")
                print("Completion Entropies:")
                for method, entropy in comp_entropies.items():
                    print(f"  {method.capitalize()}: {entropy:.6f}")
                print(f"Completion Open-ended Response: {comp_open_response}")
                print("-" * 50)

            for method in ['full', 'min', 'avg', 'first']:
                self.stats[category][ambiguity]['mcq'][method] += mcq_entropies[method]
                self.stats[category][ambiguity]['completion'][method] += comp_entropies[method]

                self.prob_diff_stats[category]['mcq'][method].append((mcq_entropies[method], mcq_prob_diffs[method], ambiguity))
                self.prob_diff_stats[category]['completion'][method].append((comp_entropies[method], comp_prob_diffs[method], ambiguity))

    def process_all_files(self):
        file_mapping = {
            'ambigqa': ('ambigqa_ambi.json', 'ambigqa_unambi.json'),
            'bound': ('bound_ambi.json', 'bound_unambi.json'),
            'conj': ('conj_ambi.json', 'conj_unambi.json'),
            'pp': ('pp_ambi.json', 'pp_unambi.json'),
            'scope': ('scope_ambi.json', 'scope_unambi.json'),
            'scope_reverse': ('scope_reverse_ambi.json', 'scope_reverse_unambi.json'),
            'scopedataset': ('scopedataset_ambi.json', 'scopedataset_unambi.json')
        }

        for category, (ambi_file, unambi_file) in file_mapping.items():
            ambi_path = os.path.join(self.data_dir, ambi_file)
            unambi_path = os.path.join(self.data_dir, unambi_file)
            
            self.process_file(ambi_path, category, 'ambi')
            self.process_file(unambi_path, category, 'unambi')

    def generate_table(self):
        rows = []
        for question_type in ['mcq', 'completion']:
            for method in ['full', 'min', 'avg', 'first']:
                row = {'Question Type': question_type, 'Method': method}
                for category in self.stats:
                    for ambiguity in ['ambi', 'unambi']:
                        count = self.counts[category][ambiguity]
                        if count > 0:
                            avg_entropy = self.stats[category][ambiguity][question_type][method] / count
                            row[f"{category}_{ambiguity}"] = avg_entropy
                        else:
                            row[f"{category}_{ambiguity}"] = None
                rows.append(row)
        return pd.DataFrame(rows)
    
    def print_counts(self):
        print("Counts of entries in each category:")
        for category in self.counts:
            for ambiguity in ['ambi', 'unambi']:
                print(f"{category} {ambiguity}: {self.counts[category][ambiguity]}")

    def generate_prob_diff_table(self):
        rows = []
        for category in self.prob_diff_stats:
            for question_type in ['mcq', 'completion']:
                for method in ['full', 'min', 'avg', 'first']:
                    for entry in self.prob_diff_stats[category][question_type][method]:
                        entropy, prob_diff, ambiguity = entry
                        rows.append({
                            'Category': category,
                            'Question Type': question_type,
                            'Method': method,
                            'Ambiguity': ambiguity,
                            'Entropy': entropy,
                            'Probability Difference': prob_diff
                        })
        return pd.DataFrame(rows)

    def run(self):
        self.process_all_files()
        self.print_counts()
        
        entropy_table = self.generate_table()
        print("\nEntropy Table:")
        print(entropy_table.to_string())
        
        prob_diff_table = self.generate_prob_diff_table()
        print("\nProbability Difference Table (Ambiguous Questions Only):")
        print(prob_diff_table.to_string())
        
        mode_suffix = "_test" if self.test_mode else ""
        eval_suffix = f"_{self.eval_type}"
        ambiguity_suffix = f"_{self.ambiguity_mode}"
        
        randomize_suffix = "_randomized" if self.randomize_options else ""
    
        file_prefix = f'{self.model_name}{eval_suffix}{ambiguity_suffix}{randomize_suffix}'
        
        entropy_csv_path = f'/work/users/a/u/aum/{file_prefix}_entropy_results{mode_suffix}.csv'
        prob_diff_csv_path = f'/work/users/a/u/aum/{file_prefix}_prob_diff_results{mode_suffix}.csv'
        
        entropy_table.to_csv(entropy_csv_path, index=False)
        prob_diff_table.to_csv(prob_diff_csv_path, index=False)
        
        print(f"\nEntropy results saved to {entropy_csv_path}")
        print(f"Probability difference results saved to {prob_diff_csv_path}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_name", type=str, default="mistralai/Mistral-7B-v0.1", help="Name of the model to use")
    parser.add_argument("--data_dir", type=str, default="datasets", help="Directory containing the dataset files")
    parser.add_argument("--eval_type", choices=["original", "zero_shot", "few_shot"], default="original", help="Type of evaluation to perform")
    parser.add_argument("--ambiguity_mode", choices=["none", "prompt", "direct"], default="none", help="Mode for handling ambiguity")
    parser.add_argument("--test_mode", action="store_true", help="Run in test mode with a small sample of data")
    parser.add_argument("--verbose", action="store_true", help="Print detailed information for each question")
    parser.add_argument("--open_ended", action="store_true", help="Generate open-ended responses")
    parser.add_argument("--randomize_options", action="store_true", help="Randomize the order of answer options")
    
    args = parser.parse_args()

    tester = AmbiguityTester(args.model_name, args.data_dir, args.eval_type, args.ambiguity_mode,
                             args.test_mode, args.verbose, args.open_ended, args.randomize_options)
    tester.run()

if __name__ == "__main__":
    main()