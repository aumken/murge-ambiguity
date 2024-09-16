import json

def extract_nps(file_paths):
    nps = set()
    for file_path in file_paths:
        with open(file_path, 'r') as f:
            for line in f:
                entry = json.loads(line)
                var_bindings = entry.get("var_bindings", {})
                np1 = var_bindings.get("np1")
                np2 = var_bindings.get("np2")
                np3 = var_bindings.get("np3")

                if np1:
                    nps.add(np1)
                if np2:
                    nps.add(np2)
                if np3:
                    nps.add(np3)

    return list(nps)

def main(input_files, output_file):
    nps = extract_nps(input_files)

    with open(output_file, 'w') as f:
        f.write("np_to_plural = {\n")
        for np in nps:
            f.write(f'    "{np}": "",\n')
        f.write("}\n")

# Replace the paths with the actual paths to your input jsonl files
input_files = [
    'semanticparsing/0_ambig.jsonl',
    'semanticparsing/0_unambig_bound.jsonl',
    'semanticparsing/0_unambig_conj.jsonl',
    'semanticparsing/0_unambig_pp.jsonl',
    'semanticparsing/0_unambig_scope.jsonl',
    'semanticparsing/0_unambig_revscope.jsonl'
]
output_file = 'semanticparsing/1_plural.txt'

# Run the main function
main(input_files, output_file)
