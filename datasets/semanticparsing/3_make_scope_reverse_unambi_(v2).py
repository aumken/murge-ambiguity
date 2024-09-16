import json
import re

def add_the_if_needed(noun):
    return f"the {noun}" if noun[0].islower() else noun

def generate_unambiguous_scope_reverse_dataset(entry):
    surface = entry["surface"]
    var_bindings = entry["var_bindings"]
    np1 = var_bindings.get("np1")
    np2 = var_bindings.get("np2")
    vp1 = var_bindings.get("vp1")

    if not np1 or not np2 or not vp1:
        return None

    # Replace 'a' or 'an' with 'the' at the beginning of the sentence
    new_surface = re.sub(r'^a ', 'the ', surface)
    new_surface = re.sub(r'^an ', 'the ', new_surface)

    np1_plural = f"{np1}s" if np1[-1] != 's' else np1
    np2_plural = f"{np2}s" if np2[-1] != 's' else np2

    dataset = {
        "original_dataset": "Semantic Parsing",
        "metadata": {
            "surface": new_surface,
            "ambiguity": False,
            "type": "scope_reverse"
        },
        "mc_question": {
            "question": f"{new_surface}. How many {np1_plural} {vp1} {np2_plural}?",
            "options": [
                {"answer": f"one {np1}"},
                {"answer": f"many {np1_plural}"}
            ]
        },
        "open_question": {
            "question": f"{new_surface}. How many {np1_plural} {vp1} {np2_plural}?",
            "qaPairs": [
                {"answer": [f"one {np1}"]},
                {"answer": [f"many {np1_plural}"]}
            ]
        },
        "completion": {
            "prompt": f"{new_surface}. The answer to the question: How many {np1_plural} {vp1} {np2_plural}? is",
            "qaPairs": [
                {"answer": [f"one {np1}"]},
                {"answer": [f"many {np1_plural}"]}
            ]
        }
    }

    return dataset

def process_scope_reverse_data(file_path):
    unambiguous_data = []

    with open(file_path, "r") as f:
        for line in f:
            entry = json.loads(line)
            if entry["type"] == "scope_reverse":
                unambiguous_entry = generate_unambiguous_scope_reverse_dataset(entry)
                if unambiguous_entry:
                    unambiguous_data.append(unambiguous_entry)

    return unambiguous_data

def main(input_file, output_file):
    unambiguous_data = process_scope_reverse_data(input_file)

    with open(output_file, "w") as f:
        json.dump(unambiguous_data, f, indent=4)

# Replace these with your actual file paths
input_file = "semanticparsing/0_ambig.jsonl"
output_file = "semanticparsing/scope_reverse_unambi.json"

main(input_file, output_file)
