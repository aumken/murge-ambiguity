import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def visualize_ambiguity_results(csv_path):
    # Load the data
    df = pd.read_csv(csv_path)

    # Confusion matrix
    confusion_matrix = pd.crosstab(df["Actual Ambiguity"], df["Is Ambiguous"])
    plt.figure(figsize=(10, 8))
    sns.heatmap(confusion_matrix, annot=True, fmt="d", cmap="Blues")
    plt.title("Confusion Matrix: Actual vs. Predicted Ambiguity")
    plt.savefig("confusion_matrix.png")
    plt.close()

    # Probability difference distribution
    plt.figure(figsize=(10, 6))
    sns.histplot(
        data=df,
        x="Probability Difference",
        hue="Actual Ambiguity",
        element="step",
        stat="density",
        common_norm=False,
    )
    plt.title("Distribution of Probability Differences")
    plt.savefig("prob_diff_distribution.png")
    plt.close()

    # Scatter plot of Yes Probability vs No Probability
    plt.figure(figsize=(10, 8))
    sns.scatterplot(
        data=df, x="Yes Probability", y="No Probability", hue="Actual Ambiguity"
    )
    plt.title("Yes Probability vs No Probability")
    plt.savefig("yes_no_prob_scatter.png")
    plt.close()

    # Category-wise accuracy
    category_accuracy = df.groupby("Category").apply(
        lambda x: (x["Is Ambiguous"] == x["Actual Ambiguity"]).mean()
    )
    plt.figure(figsize=(12, 6))
    sns.barplot(x=category_accuracy.index, y=category_accuracy.values)
    plt.title("Accuracy by Category")
    plt.ylabel("Accuracy")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("category_accuracy.png")
    plt.close()

    print("Visualizations have been saved as PNG files.")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "csv_path", type=str, help="Path to the CSV file with ambiguity results"
    )
    args = parser.parse_args()

    visualize_ambiguity_results(args.csv_path)
