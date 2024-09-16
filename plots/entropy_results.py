import os

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def plot_entropy_from_csv(csv_file, output_image):
    # Read the CSV file
    df = pd.read_csv(csv_file)

    # Identify all relevant columns
    relevant_columns = [col for col in df.columns if "_ambi" in col or "_unambi" in col]

    # Check if we have the new format or the old format
    if len(relevant_columns) == 2 and "scopedataset_ambi" in relevant_columns:
        # New format
        base_names = ["scopedataset"]
    else:
        # Old format
        base_names = sorted(set(col.split("_")[0] for col in relevant_columns))
        if "scope_reverse" in base_names:
            base_names.remove("scope_reverse")
            base_names.append("rev_scope")

    # Create a figure with subplots
    fig, axes = plt.subplots(2, len(base_names), figsize=(5 * len(base_names), 10))

    # If there's only one base_name, axes will be 1D, so we need to reshape it
    if len(base_names) == 1:
        axes = axes.reshape(-1, 1)

    # Define color palette
    color_palette = {"Ambiguous": "#3498db", "Unambiguous": "#2ecc71"}

    # Loop through each base name and question type to create individual plots
    for i, base in enumerate(base_names):
        for j, question_type in enumerate(["mcq", "completion"]):
            # Select the required columns
            if base == "rev_scope":
                ambi_col = "scope_reverse_ambi"
                unambi_col = "scope_reverse_unambi"
            else:
                ambi_col = f"{base}_ambi"
                unambi_col = f"{base}_unambi"

            selected_columns = ["Question Type", "Method", ambi_col, unambi_col]
            df_selected = df[df["Question Type"] == question_type][selected_columns]

            # Melt the DataFrame for easier plotting with seaborn
            df_melted = pd.melt(
                df_selected,
                id_vars=["Question Type", "Method"],
                var_name="Category",
                value_name="Entropy",
            )

            # Create a new column for grouping
            df_melted["Group"] = df_melted["Method"]
            df_melted["Ambiguity"] = df_melted["Category"].apply(
                lambda x: (
                    "Ambiguous" if "ambi" in x and "unambi" not in x else "Unambiguous"
                )
            )

            # Create a bar plot for the entropy values with specified colors
            sns.barplot(
                data=df_melted,
                x="Group",
                y="Entropy",
                hue="Ambiguity",
                ax=axes[j, i],
                palette=color_palette,
                errorbar=None,
            )

            # Add titles and labels
            axes[j, i].set_title(f"{base} - {question_type}")
            axes[j, i].set_xlabel("Method")
            axes[j, i].set_ylabel("Entropy")
            axes[j, i].legend(title="Ambiguity")

            # Rotate x-axis labels
            for label in axes[j, i].get_xticklabels():
                label.set_rotation(45)

    # Adjust layout
    plt.tight_layout()

    # Add the filename to the plot
    plt.suptitle(os.path.basename(csv_file), fontsize=16, y=1.02)

    plt.savefig(output_image, bbox_inches="tight")
    plt.close()


# The process_csv_folder function remains the same

def process_csv_folder(input_folder, output_folder):
    # Create output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Process each CSV file in the input folder
    for filename in os.listdir(input_folder):
        if filename.endswith('.csv'):
            csv_path = os.path.join(input_folder, filename)
            output_image = os.path.join(output_folder, f"{os.path.splitext(filename)[0]}.png")
            plot_entropy_from_csv(csv_path, output_image)
            print(f"Processed {filename}")

# Usage
input_folder = 'entropy_results'  # Update this to your input folder path
output_folder = 'entropy_results_img'  # Update this to your desired output folder path

process_csv_folder(input_folder, output_folder)
