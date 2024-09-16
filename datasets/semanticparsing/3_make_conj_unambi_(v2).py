import json

def add_the_if_needed(noun):
    return f"the {noun}" if noun[0].islower() else noun

def generate_unambiguous_conj_dataset(entry):
    surface = entry["surface"]
    var_bindings = entry["var_bindings"]
    np1 = var_bindings.get("np1")
    vp1 = var_bindings.get("vp1")
    vp2 = var_bindings.get("vp2")
    vp3 = var_bindings.get("vp3")

    if not np1 or not vp1 or not vp2 or not vp3:
        return None

    # Replace 'and' with 'then'
    np1_with_the = add_the_if_needed(np1)
    new_surface = surface.replace(f"{vp1} and", f"{vp1}. then {np1_with_the}")

    dataset = {
        "original_dataset": "Semantic Parsing",
        "metadata": {
            "surface": new_surface,
            "ambiguity": False,
            "type": "conj"
        },
        "mc_question": {
            "question": f"{new_surface}. What did {np1_with_the} do?",
            "options": [
                {"answer": f"{np1_with_the} {vp1} and then either {vp2} or {vp3}"},
                {"answer": f"{np1_with_the} either {vp1} and {vp2} or {vp3}"}
            ]
        },
        "open_question": {
            "question": f"{new_surface}. What did {np1_with_the} do?",
            "qaPairs": [
                {"answer": [f"{np1_with_the} {vp1} and then either {vp2} or {vp3}"]},
                {"answer": [f"{np1_with_the} either {vp1} and {vp2} or {vp3}"]}
            ]
        },
        "completion": {
            "prompt": f"{new_surface}. The answer to the question: What did {np1_with_the} do? is",
            "qaPairs": [
                {"answer": [f"{np1_with_the} {vp1} and then either {vp2} or {vp3}"]},
                {"answer": [f"{np1_with_the} either {vp1} and {vp2} or {vp3}"]}
            ]
        }
    }

    return dataset

def process_conj_data(file_path):
    unambiguous_data = []

    with open(file_path, "r") as f:
        for line in f:
            entry = json.loads(line)
            if entry["type"] == "conj":
                unambiguous_entry = generate_unambiguous_conj_dataset(entry)
                if unambiguous_entry:
                    unambiguous_data.append(unambiguous_entry)

    return unambiguous_data

def main(input_file, output_file):
    unambiguous_data = process_conj_data(input_file)

    with open(output_file, "w") as f:
        json.dump(unambiguous_data, f, indent=4)

# Replace these with your actual file paths
input_file = "semanticparsing/0_ambig.jsonl"
output_file = "semanticparsing/conj_unambi.json"

main(input_file, output_file)
