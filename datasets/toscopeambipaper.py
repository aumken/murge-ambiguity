import csv
import json
import os
from collections import defaultdict


def get_question_type(filename):
    if "bound" in filename:
        return "bound"
    elif "pp" in filename:
        return "pp"
    elif "scope_reverse" in filename:
        return "reverse_scope"
    elif "scope" in filename:
        return "scope"
    elif "conj" in filename:
        return "conj"
    else:
        return "unknown"


def process_file(file_path, dataset_type, question_type):
    print(f"Processing file: {file_path}")
    try:
        with open(file_path, "r") as f:
            data = json.load(f)
    except json.JSONDecodeError:
        print(f"Error: Unable to parse JSON in file {file_path}")
        return []
    except FileNotFoundError:
        print(f"Error: File not found: {file_path}")
        return []

    print(f"Number of items in file: {len(data)}")
    results = []
    for idx, item in enumerate(data, start=1):
        print(f"Processing item {idx}")
        completion = item.get("completion", {})
        prompt = completion.get("prompt", "")
        qa_pairs = completion.get("qaPairs", [])

        main_question = prompt.strip()
        print(f"Extracted main question: {main_question}")

        is_ambiguous = dataset_type == "ambi"

        if is_ambiguous:
            if len(qa_pairs) != 2:
                print(f"Skipping item {idx} due to incorrect number of qaPairs")
                continue

            followup1 = qa_pairs[0].get("answer", [""])[0]
            followup2 = qa_pairs[1].get("answer", [""])[0]

            print(f"Extracted followup1: {followup1}")
            print(f"Extracted followup2: {followup2}")

            results.append(
                {
                    "idx": idx,
                    "sentence": main_question,
                    "followup": followup1,
                    "stype": "S",
                    "ftype": "F1",
                    "OP1": "NA_CONTROL",
                    "OP1_type": "NA_CONTROL",
                    "OP2": "NA_CONTROL",
                    "OP2_type": "NA_CONTROL",
                    "ambiguity": "ambi",
                    "question_type": question_type,
                }
            )
            results.append(
                {
                    "idx": idx,
                    "sentence": main_question,
                    "followup": followup2,
                    "stype": "S",
                    "ftype": "F2",
                    "OP1": "NA_CONTROL",
                    "OP1_type": "NA_CONTROL",
                    "OP2": "NA_CONTROL",
                    "OP2_type": "NA_CONTROL",
                    "ambiguity": "ambi",
                    "question_type": question_type,
                }
            )
        else:
            if not qa_pairs:
                print(f"Skipping item {idx} due to missing qaPairs")
                continue

            followup1 = qa_pairs[0].get("answer", [""])[0]
            followup2 = qa_pairs[1].get("answer", [""])[0]

            print(f"Extracted followup1: {followup1}")
            print(f"Extracted followup2: {followup2}")

            results.append(
                {
                    "idx": idx,
                    "sentence": main_question,
                    "followup": followup1,
                    "stype": "Sc",
                    "ftype": "F1",
                    "OP1": "NA_CONTROL",
                    "OP1_type": "NA_CONTROL",
                    "OP2": "NA_CONTROL",
                    "OP2_type": "NA_CONTROL",
                    "ambiguity": "unambi",
                    "question_type": question_type,
                }
            )
            results.append(
                {
                    "idx": idx,
                    "sentence": main_question,
                    "followup": followup2,
                    "stype": "Sc",
                    "ftype": "F2",
                    "OP1": "NA_CONTROL",
                    "OP1_type": "NA_CONTROL",
                    "OP2": "NA_CONTROL",
                    "OP2_type": "NA_CONTROL",
                    "ambiguity": "unambi",
                    "question_type": question_type,
                }
            )

    print(f"Number of results from this file: {len(results)}")
    return results


def write_csv(filename, data, fieldnames):
    print(f"Writing results to {filename}")
    with open(filename, "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            writer.writerow(row)


def main():
    input_folder = "dataset"
    output_folder = "dataset_reformatted"
    print(f"Creating output folder: {output_folder}")
    os.makedirs(output_folder, exist_ok=True)

    all_results = []
    subset_results = defaultdict(lambda: defaultdict(list))

    print(f"Scanning input folder: {input_folder}")
    for filename in os.listdir(input_folder):
        if filename.endswith(".json"):
            file_path = os.path.join(input_folder, filename)
            dataset_type = "ambi" if "_ambi" in filename else "unambi"
            question_type = get_question_type(filename)
            print(
                f"Processing file {filename} as {dataset_type}, type: {question_type}"
            )
            results = process_file(file_path, dataset_type, question_type)
            all_results.extend(results)

            # Add to subset results
            for result in results:
                if len(subset_results[question_type][dataset_type]) < 20:
                    subset_results[question_type][dataset_type].append(result)

    print(f"Total results: {len(all_results)}")

    fieldnames = [
        "idx",
        "sentence",
        "followup",
        "stype",
        "ftype",
        "OP1",
        "OP1_type",
        "OP2",
        "OP2_type",
        "ambiguity",
        "question_type",
    ]

    # Write full dataset
    output_file = os.path.join(output_folder, "reformatted_dataset.csv")
    write_csv(output_file, all_results, fieldnames)

    # Write subset dataset
    subset_output = []
    for question_type in subset_results:
        subset_output.extend(subset_results[question_type]["ambi"])
        subset_output.extend(subset_results[question_type]["unambi"])

    subset_output_file = os.path.join(output_folder, "reformatted_dataset_subset.csv")
    write_csv(subset_output_file, subset_output, fieldnames)

    print("Script execution completed")


if __name__ == "__main__":
    main()
