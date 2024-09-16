import json

def extract_verbs(file_paths):
    verbs = set()
    for file_path in file_paths:
        with open(file_path, 'r') as f:
            for line in f:
                entry = json.loads(line)
                var_bindings = entry.get("var_bindings", {})
                vp1 = var_bindings.get("vp1")
                if vp1:
                    verbs.add(vp1)
    return list(verbs)

def main(input_files, output_file):
    verbs = extract_verbs(input_files)
    with open(output_file, 'w') as f:
        f.write("verb_to_gerund = {\n")
        for verb in verbs:
            f.write(f'    "{verb}": "",\n')
        f.write("}\n")

# Replace 'input_files' with the list of your input jsonl files
# Replace 'output_gerund.txt' with the desired path for your output text file
input_files = [
    'semanticparsing/0_ambig.jsonl',
    'semanticparsing/0_unambig_bound.jsonl',
    'semanticparsing/0_unambig_conj.jsonl',
    'semanticparsing/0_unambig_pp.jsonl',
    'semanticparsing/0_unambig_scope.jsonl',
    'semanticparsing/0_unambig_revscope.jsonl'
]
output_file = 'semanticparsing/1_gerund.txt'

# Run the main function
main(input_files, output_file)
