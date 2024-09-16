import os

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def plot_entropy(
    df,
    category,
    question_type,
    ax,
    use_violin=False,
    show_outliers=False,
    y_min=0,
    y_max=None,
):
    # Define color palette for ambiguity
    ambiguity_palette = {"ambi": "#3498db", "unambi": "#2ecc71"}

    if use_violin:
        # Combine 'Method' and 'Ambiguity' into a single column for proper violin plotting
        df["Method_Ambiguity"] = df["Method"] + "_" + df["Ambiguity"]

        # Create a custom palette that alternates between ambi and unambi colors for each method
        methods = df["Method"].unique()
        custom_palette = []
        for method in methods:
            custom_palette.extend(
                [ambiguity_palette["ambi"], ambiguity_palette["unambi"]]
            )

        sns.violinplot(
            data=df,
            x="Method_Ambiguity",
            y="Entropy",
            ax=ax,
            palette=custom_palette,
            inner="box",
            cut=2,
        )

        # Adjust x-axis labels
        current_labels = [t.get_text() for t in ax.get_xticklabels()]
        new_labels = [label.split("_")[0] for label in current_labels]
        ax.set_xticklabels(new_labels)
    else:
        sns.boxplot(
            data=df,
            x="Method",
            y="Entropy",
            hue="Ambiguity",
            ax=ax,
            palette=ambiguity_palette,
            width=0.7,
            fliersize=(2 if show_outliers else 0),
            showfliers=show_outliers,
        )

    # Add titles and labels
    ax.set_title(f"{category} - {question_type}", fontsize=12, fontweight="bold")
    ax.set_xlabel("Method", fontsize=10)
    ax.set_ylabel("Entropy", fontsize=10)

    # Rotate x-axis labels
    for label in ax.get_xticklabels():
        label.set_rotation(45)
        label.set_ha("right")

    # Set y-axis limits
    if y_min is not None:
        ax.set_ylim(bottom=y_min)
    if y_max is None:
        y_max = df["Entropy"].max() * 1.1  # Add 10% padding
    ax.set_ylim(top=y_max)

    # Add more ticks on the y-axis for better readability
    ax.yaxis.set_major_locator(plt.MultipleLocator((y_max - y_min) / 10))
    ax.yaxis.set_minor_locator(plt.MultipleLocator((y_max - y_min) / 20))

    # Adjust legend
    if use_violin:
        # Create a custom legend for violin plots
        from matplotlib.patches import Patch

        legend_elements = [
            Patch(
                facecolor=ambiguity_palette["ambi"], edgecolor="w", label="Ambiguous"
            ),
            Patch(
                facecolor=ambiguity_palette["unambi"],
                edgecolor="w",
                label="Unambiguous",
            ),
        ]
        ax.legend(
            handles=legend_elements, title="Ambiguity", loc="upper right", fontsize=8
        )
    else:
        ax.legend(title="Ambiguity", loc="upper right", fontsize=8)

    # Remove top and right spines
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    # Set background color to light gray
    ax.set_facecolor("#f0f0f0")


def plot_entropy_from_csv(
    csv_file,
    output_image,
    use_violin=False,
    separate_plots=False,
    show_outliers=False,
    y_min=0,
):
    # Read the CSV file
    df = pd.read_csv(csv_file)

    # Identify all unique categories
    categories = sorted(df["Category"].unique())

    if separate_plots:
        # Create output subfolder for this CSV
        csv_name = os.path.splitext(os.path.basename(csv_file))[0]
        csv_output_folder = os.path.join(os.path.dirname(output_image), csv_name)
        if not os.path.exists(csv_output_folder):
            os.makedirs(csv_output_folder)

        # Create individual plots for each category and question type
        for category in categories:
            for question_type in ["mcq", "completion"]:
                mask = (df["Category"] == category) & (
                    df["Question Type"] == question_type
                )
                df_selected = df[mask].copy()

                plt.figure(figsize=(10, 6))
                ax = plt.gca()
                plot_entropy(
                    df_selected,
                    category,
                    question_type,
                    ax,
                    use_violin,
                    show_outliers,
                    y_min,
                    y_max=None,
                )

                plot_type = "violinplot" if use_violin else "boxplot"
                output_file = os.path.join(
                    csv_output_folder,
                    f"{category}_{question_type}_{plot_type}_{'with_outliers' if show_outliers else 'without_outliers'}.png",
                )

                plt.tight_layout()
                plt.savefig(output_file, dpi=300)
                plt.close()
    else:
        # Create a figure with subplots
        fig, axes = plt.subplots(2, len(categories), figsize=(7 * len(categories), 14))

        # If there's only one category, axes will be 1D, so we need to reshape it
        if len(categories) == 1:
            axes = axes.reshape(-1, 1)

        # Loop through each category and question type to create individual plots
        for i, category in enumerate(categories):
            for j, question_type in enumerate(["mcq", "completion"]):
                # Select the required data
                mask = (df["Category"] == category) & (
                    df["Question Type"] == question_type
                )
                df_selected = df[mask].copy()

                plot_entropy(
                    df_selected,
                    category,
                    question_type,
                    axes[j, i],
                    use_violin,
                    show_outliers,
                    y_min,
                    y_max=None,
                )

        # Adjust layout
        plt.tight_layout()

        # Add the filename to the plot
        plt.suptitle(os.path.basename(csv_file), fontsize=16, y=1.02)

        plt.savefig(output_image, bbox_inches="tight", dpi=300)
        plt.close()


def process_csv_folder(
    input_folder,
    output_folder,
    use_violin=False,
    separate_plots=False,
    show_outliers=False,
    y_min=0,
):
    # Create output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Process each CSV file in the input folder
    for filename in os.listdir(input_folder):
        if filename.endswith(".csv"):
            csv_path = os.path.join(input_folder, filename)
            plot_type = "violinplot" if use_violin else "boxplot"
            output_image = os.path.join(
                output_folder,
                f"{os.path.splitext(filename)[0]}_{plot_type}_{'with_outliers' if show_outliers else 'without_outliers'}.png",
            )
            plot_entropy_from_csv(
                csv_path,
                output_image,
                use_violin,
                separate_plots,
                show_outliers,
                y_min,
            )
            print(f"Processed {filename}")


input_folder = "prob_diff_results"  # Update this to your input folder path
output_folder = (
    "prob_diff_results_img"  # Update this to your desired output folder path
)

# Set use_violin to True to generate violin plots, False for box plots
# Set separate_plots to True to create individual plot files in separate folders
# Set show_outliers to True to include outliers in the plots
# Set y_min to manually set the minimum y-axis limit for all graphs
process_csv_folder(
    input_folder,
    output_folder,
    use_violin=True,
    separate_plots=False,
    show_outliers=True,
    y_min=0,
)
