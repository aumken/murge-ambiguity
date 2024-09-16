import csv
import json


def process_scopeambi_dataset(
    input_file, ambiguous_output_file, unambiguous_output_file
):
    ambiguous_data = []
    unambiguous_data = []

    with open(input_file, "r", newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # Process ambiguous version
            ambiguous_entry = create_ambiguous_entry(row)
            ambiguous_data.append(ambiguous_entry)

            # Process unambiguous version
            unambiguous_entry = create_unambiguous_entry(row)
            unambiguous_data.append(unambiguous_entry)

    # Write ambiguous data to file
    with open(ambiguous_output_file, "w", encoding="utf-8") as f:
        json.dump(ambiguous_data, f, indent=4)

    # Write unambiguous data to file
    with open(unambiguous_output_file, "w", encoding="utf-8") as f:
        json.dump(unambiguous_data, f, indent=4)


def create_ambiguous_entry(row):
    return {
        "original_dataset": "ScopeAmbi",
        "metadata": {
            "id": row["idx"],
            "ambiguity": True,
            "type": "scope",
            "surface": row["sentence"],
        },
        "mc_question": {
            "question": f"{row['sentence']} Which interpretation is correct?",
            "options": [
                {
                    "answer": row["Option A"],
                    "clarifying_question": f"{row['sentence']} Assume {row['Option A'].lower()}. Is this correct?",
                },
                {
                    "answer": row["Option B"],
                    "clarifying_question": f"{row['sentence']} Assume {row['Option B'].lower()}. Is this correct?",
                },
            ],
        },
        "open_question": {
            "question": f"{row['sentence']} What are the possible interpretations?",
            "qaPairs": [
                {
                    "question": f"{row['sentence']} What if {row['Option A'].lower()}?",
                    "answer": [row["Option A"]],
                },
                {
                    "question": f"{row['sentence']} What if {row['Option B'].lower()}?",
                    "answer": [row["Option B"]],
                },
            ],
        },
        "completion": {
            "prompt": f"{row['sentence']} The correct interpretation is",
            "qaPairs": [
                {
                    "question": f"{row['sentence']} Assuming {row['Option A'].lower()}, the correct interpretation is",
                    "answer": [row["Option A"]],
                },
                {
                    "question": f"{row['sentence']} Assuming {row['Option B'].lower()}, the correct interpretation is",
                    "answer": [row["Option B"]],
                },
            ],
        },
    }


def create_unambiguous_entry(row):
    unambiguous_sentence = "The" + row["sentence"][1:]  # Replace 'A' with 'The'
    correct_option = row["Option A"] if row["gold_ans"] == "A" else row["Option B"]
    incorrect_option = row["Option B"] if row["gold_ans"] == "A" else row["Option A"]

    return {
        "original_dataset": "ScopeAmbi",
        "metadata": {
            "id": row["idx"],
            "ambiguity": False,
            "type": "scope",
            "surface": unambiguous_sentence,
        },
        "mc_question": {
            "question": f"{unambiguous_sentence} Which interpretation is correct?",
            "options": [{"answer": correct_option}, {"answer": incorrect_option}],
        },
        "open_question": {
            "question": f"{unambiguous_sentence} What is the correct interpretation?",
            "qaPairs": [{"answer": [correct_option]}, {"answer": [incorrect_option]}],
        },
        "completion": {
            "prompt": f"{unambiguous_sentence} The correct interpretation is",
            "qaPairs": [{"answer": [correct_option]}, {"answer": [incorrect_option]}],
        },
    }


# Usage
input_file = "scopedataset/0_1b.csv"
ambiguous_output_file = "scopedataset/scopedataset_ambi.json"
unambiguous_output_file = "scopedataset/scopedataset_unambi.json"

process_scopeambi_dataset(input_file, ambiguous_output_file, unambiguous_output_file)
