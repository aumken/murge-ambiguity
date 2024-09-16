import json


def transform_to_unambiguous(ambiguous_data):
    unambiguous_data = []

    for entry in ambiguous_data:
        original_question = entry["mc_question"]["question"]
        options = entry["mc_question"]["options"]

        for option in options:
            unambiguous_entry = {
                "original_dataset": entry["original_dataset"],
                "metadata": {"id": entry["metadata"]["id"], "ambiguity": False},
                "mc_question": {
                    "question": option["clarifying_question"],
                    "options": [{"answer": opt["answer"]} for opt in options],
                },
                "open_question": {
                    "question": option["clarifying_question"],
                    "qaPairs": [{"answer": [opt["answer"]]} for opt in options],
                },
                "completion": {
                    "prompt": f"The answer to the question: {option['clarifying_question']} is",
                    "qaPairs": [{"answer": [opt["answer"]]} for opt in options],
                },
            }
            unambiguous_data.append(unambiguous_entry)

    return unambiguous_data


def main():
    # Read the input JSON file
    with open("ambigqa/ambigqa_ambi.json", "r") as f:
        ambiguous_data = json.load(f)

    # Transform the data
    unambiguous_data = transform_to_unambiguous(ambiguous_data)

    # Write the output JSON file
    with open("ambigqa/ambigqa_unambi.json", "w") as f:
        json.dump(unambiguous_data, f, indent=2)

    print("Transformation complete. Output written to ambigqa_unambi.json")


if __name__ == "__main__":
    main()
