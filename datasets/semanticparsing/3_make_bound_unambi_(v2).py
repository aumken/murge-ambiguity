import json
import random

# Predefined groups of male and female nouns
male_nouns = ["Mark", "John", "Bill", "Sherlock", "Galileo", "the man", "the boy"]
female_nouns = ["Katherine", "Mary", "Ada", "Adele", "the woman", "the girl"]

def generate_unambiguous_bound_dataset(entry):
    surface = entry["surface"]
    var_bindings = entry["var_bindings"]
    np1 = var_bindings.get("np1")
    np2 = var_bindings.get("np2")
    vp1 = var_bindings.get("vp1")
    vp2 = var_bindings.get("vp2")

    if not np1 or not np2 or not vp1 or not vp2:
        return None

    # Ensure we have one male and one female character
    if random.choice([True, False]):
        np1 = random.choice(male_nouns)
        np2 = random.choice(female_nouns)
        pronoun = "he"
    else:
        np1 = random.choice(female_nouns)
        np2 = random.choice(male_nouns)
        pronoun = "she"

    # Create the new unambiguous surface
    new_surface = f"{np1} {vp1} {np2} and {pronoun} {vp2}"

    dataset = {
        "original_dataset": "Semantic Parsing",
        "metadata": {
            "surface": new_surface,
            "ambiguity": False,
            "type": "bound"
        },
        "mc_question": {
            "question": f"{new_surface}. Who {vp2}?",
            "options": [
                {"answer": np1},
                {"answer": np2}
            ]
        },
        "open_question": {
            "question": f"{new_surface}. Who {vp2}?",
            "qaPairs": [
                {"answer": [np1]},
                {"answer": [np2]}
            ]
        },
        "completion": {
            "prompt": f"{new_surface}. The answer to the question: Who {vp2}? is",
            "qaPairs": [
                {"answer": [np1]},
                {"answer": [np2]}
            ]
        }
    }

    return dataset

def process_bound_data(file_path):
    unambiguous_data = []

    with open(file_path, "r") as f:
        for line in f:
            entry = json.loads(line)
            if entry["type"] == "bound":
                unambiguous_entry = generate_unambiguous_bound_dataset(entry)
                if unambiguous_entry:
                    unambiguous_data.append(unambiguous_entry)

    return unambiguous_data

def main(input_file, output_file):
    unambiguous_data = process_bound_data(input_file)

    with open(output_file, "w") as f:
        json.dump(unambiguous_data, f, indent=4)

# Replace these with your actual file paths
input_file = "semanticparsing/0_ambig.jsonl"
output_file = "semanticparsing/bound_unambi.json"

main(input_file, output_file)
