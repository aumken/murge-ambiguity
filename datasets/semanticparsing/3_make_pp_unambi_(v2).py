import json
import random

# List of unambiguous objects
unambiguous_objects = ["apple", "hat", "book", "pen", "scarf", "jacket", "umbrella", "bag", "watch", "glasses"]

def add_the_if_needed(noun):
    return f"the {noun}" if noun[0].islower() else noun

def generate_unambiguous_pp_dataset(entry):
    surface = entry["surface"]
    var_bindings = entry["var_bindings"]
    np1 = var_bindings.get("np1")
    np2 = var_bindings.get("np2")
    vp1 = var_bindings.get("vp1")
    np3 = var_bindings.get("np3")

    if not np1 or not np2 or not np3 or not vp1:
        return None

    # Replace the ambiguous object with an unambiguous one
    unambiguous_object = random.choice(unambiguous_objects)
    new_surface = surface.replace(f"the {np3}", f"the {unambiguous_object}")

    np1_with_the = add_the_if_needed(np1)
    np2_with_the = add_the_if_needed(np2)

    dataset = {
        "original_dataset": "Semantic Parsing",
        "metadata": {
            "surface": new_surface,
            "ambiguity": False,
            "type": "pp"
        },
        "mc_question": {
            "question": f"{new_surface}. Who has the {unambiguous_object}?",
            "options": [
                {"answer": np2_with_the},
                {"answer": np1_with_the}
            ]
        },
        "open_question": {
            "question": f"{new_surface}. Who has the {unambiguous_object}?",
            "qaPairs": [
                {"answer": [np2_with_the]},
                {"answer": [np1_with_the]}
            ]
        },
        "completion": {
            "prompt": f"{new_surface}. The answer to the question: Who has the {unambiguous_object}? is",
            "qaPairs": [
                {"answer": [np2_with_the]},
                {"answer": [np1_with_the]}
            ]
        }
    }

    return dataset

def process_pp_data(file_path):
    unambiguous_data = []

    with open(file_path, "r") as f:
        for line in f:
            entry = json.loads(line)
            if entry["type"] == "pp":
                unambiguous_entry = generate_unambiguous_pp_dataset(entry)
                if unambiguous_entry:
                    unambiguous_data.append(unambiguous_entry)

    return unambiguous_data

def main(input_file, output_file):
    unambiguous_data = process_pp_data(input_file)

    with open(output_file, "w") as f:
        json.dump(unambiguous_data, f, indent=4)

# Replace these with your actual file paths
input_file = "semanticparsing/0_ambig.jsonl"
output_file = "semanticparsing/pp_unambi.json"

main(input_file, output_file)
