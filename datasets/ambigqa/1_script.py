import json


def transform_data(input_file, ambiguous_output_file, unambiguous_output_file):
    with open(input_file, 'r') as infile:
        data = json.load(infile)

    ambiguous_data = []
    unambiguous_data = []

    for entry in data:
        # Determine the ambiguity based on the annotations
        ambiguity = any(annotation["type"] == "multipleQAs" for annotation in entry["annotations"])

        transformed_entry = {
            "original_dataset": "AmbigQA",
            "metadata": {
                "id": entry["id"],
                "ambiguity": ambiguity
            },
            "mc_question": {
                "question": entry["question"],
                "options": []
            },
            "open_question": {
                "question": entry["question"],
                "qaPairs": []
            },
            "completion": {
                "prompt": f"The answer to the question: {entry['question']} is",
                "qaPairs": []
            }
        }

        # Group answers for the same question
        qa_dict = {}
        for annotation in entry["annotations"]:
            if annotation["type"] == "multipleQAs":
                for pair in annotation["qaPairs"]:
                    if pair["question"] not in qa_dict:
                        qa_dict[pair["question"]] = set()
                    qa_dict[pair["question"]].update(pair["answer"])
            else:  # type is "singleAnswer"
                if entry["question"] not in qa_dict:
                    qa_dict[entry["question"]] = set()
                qa_dict[entry["question"]].update(annotation["answer"])

        for question, answers in qa_dict.items():
            answer_list = list(answers)
            joined_answers = ", ".join(answer_list)
            transformed_entry["mc_question"]["options"].append({
                "answer": joined_answers,
                "clarifying_question": question
            })
            transformed_entry["open_question"]["qaPairs"].append({
                "question": question,
                "answer": answer_list
            })
            transformed_entry["completion"]["qaPairs"].append({
                "question": f"The answer to the question: {question} is",
                "answer": answer_list
            })

        if ambiguity:
            ambiguous_data.append(transformed_entry)
        else:
            unambiguous_data.append(transformed_entry)

    with open(ambiguous_output_file, 'w') as ambiguous_outfile:
        json.dump(ambiguous_data, ambiguous_outfile, indent=4)

    with open(unambiguous_output_file, 'w') as unambiguous_outfile:
        json.dump(unambiguous_data, unambiguous_outfile, indent=4)


# Example usage
input_file = 'ambigqa/0_data.json'
ambiguous_output_file = 'ambigqa/ambigqa_ambi.json'
unambiguous_output_file = 'ambigqa/ambigqa_unambi.json'
transform_data(input_file, ambiguous_output_file, unambiguous_output_file)
