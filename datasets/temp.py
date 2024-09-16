import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

# Read the CSV file
df = pd.read_csv("3aDSout.csv")

# Calculate average log probabilities for each category
avg_probs = (
    df.groupby(["question_type", "ambiguity"])["Meta-Llama-3-8B"].mean().unstack()
)

# Calculate normalized probabilities
normalized_probs = avg_probs.apply(
    lambda x: (x - x.min()) / (x.max() - x.min()), axis=1
)

# Set up the plot style
plt.style.use("seaborn")
sns.set_palette("pastel")


# Function to create plots
def create_plots(data, title, ylabel, filename):
    fig, axes = plt.subplots(1, 5, figsize=(20, 6))
    fig.suptitle(title, fontsize=16)

    for i, question_type in enumerate(data.index):
        ax = axes[i]
        data.loc[question_type].plot(kind="bar", ax=ax)
        ax.set_title(question_type.capitalize())
        ax.set_ylabel(ylabel)
        ax.set_xticklabels(["Ambiguous", "Unambiguous"], rotation=0)

        # Add value labels on the bars
        for j, v in enumerate(data.loc[question_type]):
            ax.text(j, v, f"{v:.2f}", ha="center", va="bottom")

    plt.tight_layout()
    plt.subplots_adjust(top=0.88)
    plt.savefig(filename, dpi=300, bbox_inches="tight")
    plt.close()


# Create plot for log probabilities
create_plots(
    avg_probs,
    "Average Log Probabilities by Question Type and Ambiguity",
    "Average Log Probability",
    "log_probability_comparison.png",
)

# Create plot for normalized probabilities
create_plots(
    normalized_probs,
    "Normalized Probabilities by Question Type and Ambiguity",
    "Normalized Probability",
    "normalized_probability_comparison.png",
)

# Calculate and print the differences between ambiguous and unambiguous cases
diff_probs = avg_probs["ambi"] - avg_probs["unambi"]
print("Differences in log probabilities (ambiguous - unambiguous):")
print(diff_probs)

diff_norm_probs = normalized_probs["ambi"] - normalized_probs["unambi"]
print("\nDifferences in normalized probabilities (ambiguous - unambiguous):")
print(diff_norm_probs)
