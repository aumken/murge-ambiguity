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


# Function to convert past tense verb to base form
def to_base_form(verb):
    return past_to_base.get(verb, verb)

# Function to convert verb to gerund form
def to_gerund(verb):
    return verb_to_gerund.get(verb, f"{verb}ing")

# Function to check if a noun phrase should have "the" before it
def format_np(np):
    if np[0].islower():
        return f"the {np}"
    return np

# Function to generate unambiguous questions for 'pp' entries
def generate_pp_unambiguous_questions(surface, np1, np2, np3, vp1):
    vp1_base = to_base_form(vp1)
    return [
        {
            "answer": np3,
            "clarifying_question": f"{surface}. What did {np1} {vp1_base} the {np2} with?"
        }
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

    vp1_base = to_base_form(vp1)

    dataset = {
        "original_dataset": "Semantic Parsing",
        "metadata": {
            "surface": surface,
            "ambiguity": False,
            "type": entry["type"]
        },
        "mc_question": {
            "question": f"{surface}. What did {np1} {vp1_base} the {np2} with?",
            "options": generate_pp_unambiguous_questions(surface, np1, np2, np3, vp1),
        },
        "open_question": {
            "question": f"{surface}. What did {np1} {vp1_base} the {np2} with?",
            "qaPairs": generate_pp_unambiguous_questions(surface, np1, np2, np3, vp1),
        },
        "completion": {
            "prompt": f"{surface}. The answer to the question: What did {np1} {vp1_base} the {np2} with? is",
            "qaPairs": generate_pp_unambiguous_questions(surface, np1, np2, np3, vp1),
        },
    }

    return dataset

# Function to generate unambiguous questions for 'conj' entries
def generate_conj_unambiguous_questions(surface, np1, vp1, vp2, vp3):
    return [
        {
            "answer": np1,
            "clarifying_question": f"{surface}. Who either {vp1} and {vp2} or {vp3}?"
        }
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
            "ambiguity": False,
            "type": entry["type"]
        },
        "mc_question": {
            "question": f"{surface}. Who either {vp1} and {vp2} or {vp3}?",
            "options": generate_conj_unambiguous_questions(surface, np1, vp1, vp2, vp3),
        },
        "open_question": {
            "question": f"{surface}. Who either {vp1} and {vp2} or {vp3}?",
            "qaPairs": generate_conj_unambiguous_questions(surface, np1, vp1, vp2, vp3),
        },
        "completion": {
            "prompt": f"{surface}. The answer to the question: Who either {vp1} and {vp2} or {vp3}? is",
            "qaPairs": generate_conj_unambiguous_questions(surface, np1, vp1, vp2, vp3),
        },
    }

    return dataset

# Function to generate unambiguous questions for 'bound' entries
def generate_bound_unambiguous_questions(surface, np1, np2, vp1, vp2):
    formatted_np2 = format_np(np2)
    return [
        {
            "answer": np2,
            "clarifying_question": f"{surface}. What did {np1} do after they {vp1} {formatted_np2}?"
        }
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

    formatted_np2 = format_np(np2)

    dataset = {
        "original_dataset": "Semantic Parsing",
        "metadata": {
            "surface": surface,
            "ambiguity": False,
            "type": entry["type"]
        },
        "mc_question": {
            "question": f"{surface}. What did {np1} do after they {vp1} {formatted_np2}?",
            "options": generate_bound_unambiguous_questions(surface, np1, np2, vp1, vp2),
        },
        "open_question": {
            "question": f"{surface}. What did {np1} do after they {vp1} {formatted_np2}?",
            "qaPairs": generate_bound_unambiguous_questions(surface, np1, np2, vp1, vp2),
        },
        "completion": {
            "prompt": f"{surface}. The answer to the question: What did {np1} do after they {vp1} {formatted_np2}? is",
            "qaPairs": generate_bound_unambiguous_questions(surface, np1, np2, vp1, vp2),
        },
    }

    return dataset

# Function to generate unambiguous questions for 'scope' entries
def generate_scope_unambiguous_questions(surface, np1, np2, vp1):
    vp1_base = to_base_form(vp1)
    return [
        {
            "answer": np2,
            "clarifying_question": f"{surface}. What did every {np1} {vp1_base}?"
        }
    ]

# Function to generate dataset for 'scope' entry
def generate_scope_dataset(entry):
    surface = entry["surface"]
    var_bindings = entry["var_bindings"]
    np1 = var_bindings.get("np1")
    np2 = var_bindings.get("np2")
    vp1 = var_bindings.get("vp1")

    if not np1 or not np2 or not vp1:
        return None

    vp1_base = to_base_form(vp1)

    dataset = {
        "original_dataset": "Semantic Parsing",
        "metadata": {
            "surface": surface,
            "ambiguity": False,
            "type": entry["type"]
        },
        "mc_question": {
            "question": f"{surface}. What did every {np1} {vp1_base}?",
            "options": generate_scope_unambiguous_questions(surface, np1, np2, vp1),
        },
        "open_question": {
            "question": f"{surface}. What did every {np1} {vp1_base}?",
            "qaPairs": generate_scope_unambiguous_questions(surface, np1, np2, vp1),
        },
        "completion": {
            "prompt": f"{surface}. The answer to the question: What did every {np1} {vp1_base}? is",
            "qaPairs": generate_scope_unambiguous_questions(surface, np1, np2, vp1),
        },
    }

    return dataset

# Function to generate unambiguous questions for 'scope_reverse' entries
def generate_scope_reverse_unambiguous_questions(surface, np1, np2, vp1):
    return [
        {
            "answer": np1,
            "clarifying_question": f"{surface}. What {vp1} each {np2}?"
        }
    ]

# Function to generate dataset for 'scope_reverse' entry
def generate_scope_reverse_dataset(entry):
    surface = entry["surface"]
    var_bindings = entry["var_bindings"]
    np1 = var_bindings.get("np1")
    np2 = var_bindings.get("np2")
    vp1 = var_bindings.get("vp1")

    if not np1 or not np2 or not vp1:
        return None

    dataset = {
        "original_dataset": "Semantic Parsing",
        "metadata": {
            "surface": surface,
            "ambiguity": False,
            "type": entry["type"]
        },
        "mc_question": {
            "question": f"{surface}. What {vp1} each {np2}?",
            "options": generate_scope_reverse_unambiguous_questions(surface, np1, np2, vp1),
        },
        "open_question": {
            "question": f"{surface}. What {vp1} each {np2}?",
            "qaPairs": generate_scope_reverse_unambiguous_questions(surface, np1, np2, vp1),
        },
        "completion": {
            "prompt": f"The answer to the question: What {vp1} each {np2}? is",
            "qaPairs": generate_scope_reverse_unambiguous_questions(surface, np1, np2, vp1),
        },
    }

    return dataset


# Function to process the data and separate by type
def process_data_by_type(files):
    processed_data = {
        "pp": [],
        "conj": [],
        "bound": [],
        "scope": [],
        "scope_reverse": [],
    }

    for file_path in files:
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
def main(input_files, output_prefix):
    processed_data = process_data_by_type(input_files)

    for entry_type, data in processed_data.items():
        output_file = f"{output_prefix}{entry_type}_unambi.json"
        with open(output_file, "w") as f:
            json.dump(data, f, indent=4)


# List of input files
input_files = [
    "semanticparsing/0_unambig_pp.jsonl",
    "semanticparsing/0_unambig_conj.jsonl",
    "semanticparsing/0_unambig_bound.jsonl",
    "semanticparsing/0_unambig_scope.jsonl",
    "semanticparsing/0_unambig_revscope.jsonl",
]
# Output file prefix
output_prefix = "semanticparsing/"

# Run the main function
main(input_files, output_prefix)
