import json

# Dictionary mapping past tense verbs to their base forms
past_to_base = {
    "played": "play",
    "lifted": "lift",
    "ate": "eat",
    "grabbed": "grab",
    "picked_up": "pick up",
    "shouted": "shout",
    "spied": "spy",
    "held": "hold",
    "saw": "see",
    "drew": "draw",
    "waved": "wave",
    "observed": "observe",
    "slept": "sleep",
    "frowned": "frown",
    "smiled": "smile",
    "left": "leave",
    "napped": "nap",
    "drank": "drink",
    "moved": "move",
    "walked": "walk",
    "spotted": "spot",
    "lept": "leap",
}


# Dictionary mapping verbs to their gerund forms
verb_to_gerund = {
    "grabbed": "grabbing",
    "drank": "drinking",
    "lifted": "lifting",
    "walked": "walking",
    "left": "leaving",
    "saw": "seeing",
    "ate": "eating",
    "moved": "moving",
    "napped": "napping",
    "spied": "spying",
    "picked_up": "picking up",
    "spotted": "spotting",
    "slept": "sleeping",
    "drew": "drawing",
    "observed": "observing",
    "held": "holding",
    "played": "playing",
}


# Dictionary mapping noun phrases to their plural forms
np_to_plural = {
    "hat": "hats",
    "Sherlock": "Sherlocks",
    "rock": "rocks",
    "ovenmitts": "ovenmitts",
    "Galileo": "Galileos",
    "man": "men",
    "binoculars": "binoculars",
    "Alan": "Alans",
    "boy": "boys",
    "Bill": "Bills",
    "spyglass": "spyglasses",
    "pyjamas": "pyjamas",
    "cat": "cats",
    "fish": "fish",
    "Adele": "Adeles",
    "Ada": "Adas",
    "girl": "girls",
    "pants": "pants",
    "woman": "women",
    "crayon": "crayons",
    "dog": "dogs",
    "mittens": "mittens",
    "cow": "cows",
    "Marie": "Maries",
    "Katherine": "Katherines",
    "sweater": "sweaters",
    "Watson": "Watsons",
    "gloves": "gloves",
    "Mary": "Marys",
    "table": "tables",
    "bird": "birds",
    "telescope": "telescopes",
    "book": "books",
    "elephant": "elephants",
    "camera": "cameras",
    "cup": "cups",
}

#
def add_the_if_needed(noun):
    return f"the {noun}" if noun[0].islower() else noun

# Function to convert past tense verb to base form
def to_base_form(verb):
    return past_to_base.get(verb, verb)

# Function to convert verb to gerund form
def to_gerund(verb):
    return verb_to_gerund.get(verb, f"{verb}ing")

# Function to generate clarifying questions for 'pp' entries
def generate_pp_clarifying_questions(surface, np1, np2, np3, vp1):
    vp1_gerund = to_gerund(vp1)
    return [
        {
            "answer": add_the_if_needed(np1),
            "clarifying_question": f"{surface}. Who did the {vp1_gerund} with the {np3}?",
        },
        {
            "answer": add_the_if_needed(np2),
            "clarifying_question": f"{surface}. Who was holding the {np3} when they were {vp1}?",
        },
    ]

# Function to generate open questions for 'pp' entries
def generate_pp_open_questions(surface, np1, np2, np3, vp1):
    vp1_gerund = to_gerund(vp1)
    return [
        {"question": f"{surface}. Who did the {vp1_gerund} with the {np3}?", "answer": [add_the_if_needed(np1)]},
        {
            "question": f"{surface}. Who was holding the {np3} when they were {vp1}?",
            "answer": [add_the_if_needed(np2)],
        },
    ]

# Function to generate completion questions for 'pp' entries
def generate_pp_completion_questions(surface, np1, np2, np3, vp1):
    vp1_gerund = to_gerund(vp1)
    return [
        {
            "question": f"{surface}. The answer to the question: Who did the {vp1_gerund} with the {np3}? is",
            "answer": [add_the_if_needed(np1)],
        },
        {
            "question": f"{surface}. The answer to the question: Who was holding the {np3} when they were {vp1}? is",
            "answer": [add_the_if_needed(np2)],
        },
    ]

# Function to generate dataset for 'pp' entry
def generate_pp_dataset(entry):
    surface = entry["surface"]
    var_bindings = entry["var_bindings"]
    np1 = var_bindings.get("np1")
    np2 = var_bindings.get("np2")
    np3 = var_bindings.get("np3")
    vp1 = var_bindings.get("vp1")

    if not np1 or not np2 or not np3 or not vp1:
        return None

    dataset = {
        "original_dataset": "Semantic Parsing",
        "metadata": {
            "surface": surface,
            "ambiguity": True,
            "type": entry["type"]
        },
        "mc_question": {
            "question": f"{surface}. Who has the {np3}?",
            "options": generate_pp_clarifying_questions(surface, np1, np2, np3, vp1),
        },
        "open_question": {
            "question": f"{surface}. Who has the {np3}?",
            "qaPairs": generate_pp_open_questions(surface, np1, np2, np3, vp1),
        },
        "completion": {
            "prompt": f"{surface}. The answer to the question: Who has the {np3}? is",
            "qaPairs": generate_pp_completion_questions(surface, np1, np2, np3, vp1),
        },
    }

    return dataset

# Function to generate clarifying questions for 'conj' entries
def generate_conj_clarifying_questions(surface, np1, vp1, vp2, vp3):
    vp1_base = to_base_form(vp1)
    vp2_base = to_base_form(vp2)
    vp3_base = to_base_form(vp3)
    return [
        {
            "answer": f"The {np1} either {vp1} and {vp2} or {vp3}",
            "clarifying_question": f"the {np1} {vp1} and {vp2} or {vp3}. Did the {np1} either {vp1_base} and {vp2_base}, or {vp3_base}?"
        },
        {
            "answer": f"The {np1} {vp1} and then either {vp2} or {vp3}",
            "clarifying_question": f"the {np1} {vp1} and {vp2} or {vp3}. Did the {np1} {vp1_base} first, and then either {vp2_base} or {vp3_base}?"
        }
    ]

# Function to generate open questions for 'conj' entries
def generate_conj_open_questions(surface, np1, vp1, vp2, vp3):
    vp1_base = to_base_form(vp1)
    vp2_base = to_base_form(vp2)
    vp3_base = to_base_form(vp3)
    return [
        {"question": f"{surface}. Did the {np1} either {vp1_base} and {vp2_base}, or {vp3_base}?", "answer": [f"The {np1} either {vp1} and {vp2} or {vp3}"]},
        {"question": f"{surface}. Did the {np1} {vp1_base} first, and then either {vp2_base} or {vp3_base}?", "answer": [f"The {np1} {vp1} and then either {vp2} or {vp3}"]}
    ]

# Function to generate completion questions for 'conj' entries
def generate_conj_completion_questions(surface, np1, vp1, vp2, vp3):
    vp1_base = to_base_form(vp1)
    vp2_base = to_base_form(vp2)
    vp3_base = to_base_form(vp3)
    return [
        {"question": f"{surface}. The answer to the question: Did the {np1} either {vp1_base} and {vp2_base}, or {vp3_base}? is", "answer": [f"The {np1} either {vp1} and {vp2} or {vp3}"]},
        {"question": f"{surface}. The answer to the question: Did the {np1} {vp1_base} first, and then either {vp2_base} or {vp3_base}? is", "answer": [f"The {np1} {vp1} and then either {vp2} or {vp3}"]}
    ]

# Function to generate dataset for 'conj' entry
def generate_conj_dataset(entry):
    surface = entry["surface"]
    var_bindings = entry["var_bindings"]
    np1 = var_bindings.get("np1")
    vp1 = var_bindings.get("vp1")
    vp2 = var_bindings.get("vp2")
    vp3 = var_bindings.get("vp3")

    if not np1 or not vp1 or not vp2 or not vp3:
        return None

    dataset = {
        "original_dataset": "Semantic Parsing",
        "metadata": {
            "surface": surface,
            "ambiguity": True,
            "type": entry["type"]
        },
        "mc_question": {
            "question": f"{surface}. What did the {np1} do?",
            "options": generate_conj_clarifying_questions(surface, np1, vp1, vp2, vp3),
        },
        "open_question": {
            "question": f"{surface}. What did the {np1} do?",
            "qaPairs": generate_conj_open_questions(surface, np1, vp1, vp2, vp3),
        },
        "completion": {
            "prompt": f"{surface}. The answer to the question: What did the {np1} do? is",
            "qaPairs": generate_conj_completion_questions(surface, np1, vp1, vp2, vp3),
        },
    }

    return dataset

# Function to generate clarifying questions for 'bound' entries
def generate_bound_clarifying_questions(surface, np1, np2, vp1, vp2):
    vp1_gerund = to_gerund(vp1)
    return [
        {
            "answer": add_the_if_needed(np2),
            "clarifying_question": f"{surface}. Who {vp2} after they were {vp1}?"
        },
        {
            "answer": add_the_if_needed(np1),
            "clarifying_question": f"{surface}. Who {vp2} after they did the {vp1_gerund}?"
        },
    ]

# Function to generate open questions for 'bound' entries
def generate_bound_open_questions(surface, np1, np2, vp1, vp2):
    vp1_gerund = to_gerund(vp1)
    return [
        {"question": f"{surface}. Who {vp2} after they were {vp1}?", "answer": [add_the_if_needed(np2)]},
        {"question": f"{surface}. Who {vp2} after they did the {vp1_gerund}?", "answer": [add_the_if_needed(np1)]},
    ]

# Function to generate completion questions for 'bound' entries
def generate_bound_completion_questions(surface, np1, np2, vp1, vp2):
    vp1_gerund = to_gerund(vp1)
    return [
        {"question": f"{surface}. The answer to the question: Who {vp2} after they were {vp1}? is", "answer": [add_the_if_needed(np2)]},
        {"question": f"{surface}. The answer to the question: Who {vp2} after they did the {vp1_gerund}? is", "answer": [add_the_if_needed(np1)]},
    ]

# Function to generate dataset for 'bound' entry
def generate_bound_dataset(entry):
    surface = entry["surface"]
    var_bindings = entry["var_bindings"]
    np1 = var_bindings.get("np1")
    np2 = var_bindings.get("np2")
    vp1 = var_bindings.get("vp1")
    vp2 = var_bindings.get("vp2")

    if not np1 or not np2 or not vp1 or not vp2:
        return None

    dataset = {
        "original_dataset": "Semantic Parsing",
        "metadata": {
            "surface": surface,
            "ambiguity": True,
            "type": entry["type"]
        },
        "mc_question": {
            "question": f"{surface}. Who {vp2}?",
            "options": generate_bound_clarifying_questions(surface, np1, np2, vp1, vp2),
        },
        "open_question": {
            "question": f"{surface}. Who {vp2}?",
            "qaPairs": generate_bound_open_questions(surface, np1, np2, vp1, vp2),
        },
        "completion": {
            "prompt": f"{surface}. The answer to the question: Who {vp2}? is",
            "qaPairs": generate_bound_completion_questions(surface, np1, np2, vp1, vp2),
        },
    }

    return dataset

# Function to generate dataset for 'scope' entry
def generate_scope_dataset(entry):
    surface = entry["surface"]
    var_bindings = entry["var_bindings"]
    np1 = var_bindings.get("np1")
    np2 = var_bindings.get("np2")
    vp1 = var_bindings.get("vp1")

    np2_plural = np_to_plural.get(np2, f"{np2}s")

    if not np1 or not np2 or not vp1:
        return None

    dataset = {
        "original_dataset": "Semantic Parsing",
        "metadata": {
            "surface": surface,
            "ambiguity": True,
            "type": entry["type"]
        },
        "mc_question": {
            "question": f"{surface}. How many {np2_plural} were {vp1}?",
            "options": [
                {
                    "answer": f"one {np2}",
                    "clarifying_question": f"{surface}, each {np1} {vp1} the same {np2}. How many {np2_plural} were {vp1}?"
                },
                {
                    "answer": f"many {np2_plural}",
                    "clarifying_question": f"{surface}, each {np1} {vp1} different {np2_plural}. How many {np2_plural} were {vp1}?"
                }
            ]
        },
        "open_question": {
            "question": f"{surface}. How many {np2_plural} were {vp1}?",
            "qaPairs": [
                {
                    "question": f"{surface}, each {np1} {vp1} the same {np2}. How many {np2_plural} were {vp1}?",
                    "answer": [
                        f"one {np2}"
                    ]
                },
                {
                    "question": f"{surface}, each {np1} {vp1} different {np2_plural}. How many {np2_plural} were {vp1}?",
                    "answer": [
                        f"many {np2_plural}"
                    ]
                }
            ]
        },
        "completion": {
            "prompt": f"{surface}. The answer to the question: How many {np2_plural} were {vp1}? is",
            "qaPairs": [
                {
                    "question": f"{surface}, each {np1} {vp1} the same {np2}. The answer to the question: How many {np2_plural} were {vp1}? is",
                    "answer": [
                        f"one {np2}"
                    ]
                },
                {
                    "question": f"{surface}, each {np1} {vp1} different {np2_plural}. The answer to the question: How many {np2_plural} were {vp1}? is",
                    "answer": [
                        f"many {np2_plural}"
                    ]
                }
            ]
        }
    }

    return dataset

# Function to generate dataset for 'scope_reverse' entry
def generate_scope_reverse_dataset(entry):
    surface = entry["surface"]
    var_bindings = entry["var_bindings"]
    np1 = var_bindings.get("np1")
    np2 = var_bindings.get("np2")
    vp1 = var_bindings.get("vp1")

    np1_plural = np_to_plural.get(np1, f"{np1}s")
    np2_plural = np_to_plural.get(np2, f"{np2}s")

    if not np1 or not np2 or not vp1:
        return None

    dataset = {
        "original_dataset": "Semantic Parsing",
        "metadata": {
            "surface": surface,
            "ambiguity": True,
            "type": entry["type"]
        },
        "mc_question": {
            "question": f"{surface}. How many {np1_plural} {vp1} {np2_plural}?",
            "options": [
                {
                    "answer": f"one {np1}",
                    "clarifying_question": f"{surface}, the same {np1} {vp1} each {np2}. How many {np1_plural} {vp1} {np2_plural}?"
                },
                {
                    "answer": f"many {np1_plural}",
                    "clarifying_question": f"{surface}, different {np1_plural} {vp1} each {np2}. How many {np1_plural} {vp1} {np2_plural}?"
                }
            ]
        },
        "open_question": {
            "question": f"{surface}. How many {np1_plural} {vp1} {np2_plural}?",
            "qaPairs": [
                {
                    "question": f"{surface}, the same {np1} {vp1} each {np2}. How many {np1_plural} {vp1} {np2_plural}?",
                    "answer": [
                        f"one {np1}"
                    ]
                },
                {
                    "question": f"{surface}, different {np1_plural} {vp1} each {np2}. How many {np1_plural} {vp1} {np2_plural}?",
                    "answer": [
                        f"many {np1_plural}"
                    ]
                }
            ]
        },
        "completion": {
            "prompt": f"{surface}. The answer to the question: How many {np1_plural} {vp1} {np2_plural}? is",
            "qaPairs": [
                {
                    "question": f"{surface}, the same {np1} {vp1} each {np2}. The answer to the question: How many {np1_plural} {vp1} {np2_plural}? is",
                    "answer": [
                        f"one {np1}"
                    ]
                },
                {
                    "question": f"{surface}, different {np1_plural} {vp1} each {np2}. The answer to the question: How many {np1_plural} {vp1} {np2_plural}? is",
                    "answer": [
                        f"many {np1_plural}"
                    ]
                }
            ]
        }
    }

    return dataset


def process_data_by_type(file_path):
    processed_data = {
        "pp": [],
        "conj": [],
        "bound": [],
        "scope": [],
        "scope_reverse": [],
    }

    with open(file_path, "r") as f:
        for line in f:
            entry = json.loads(line)
            if entry["type"] == "pp":
                processed_entry = generate_pp_dataset(entry)
            elif entry["type"] == "conj":
                processed_entry = generate_conj_dataset(entry)
            elif entry["type"] == "bound":
                processed_entry = generate_bound_dataset(entry)
            elif entry["type"] == "scope":
                processed_entry = generate_scope_dataset(entry)
            elif entry["type"] == "scope_reverse":
                processed_entry = generate_scope_reverse_dataset(entry)
            else:
                processed_entry = None

            if processed_entry:
                processed_data[entry["type"]].append(processed_entry)

    return processed_data


# Main function to read, process and save the processed data into 5 different files
def main(input_file, output_prefix):
    processed_data = process_data_by_type(input_file)

    for entry_type, data in processed_data.items():
        output_file = f"{output_prefix}{entry_type}_ambi.json"
        with open(output_file, "w") as f:
            json.dump(data, f, indent=4)


# Replace 'input.jsonl' with the path to your input jsonl file
# Replace 'output' with the desired prefix for your output json files
input_file = "semanticparsing/0_ambig.jsonl"
output_prefix = "semanticparsing/"

# Run the main function
main(input_file, output_prefix)
