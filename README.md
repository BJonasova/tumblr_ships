To be completely transparent, I used AI to write this README and the whole project was meant to be a funny addition into bi-monthly PowerPoint night with friends so it is probably not readable to anyone else.
# 🚢 Tumblr Ship Analyzer

## Overview

This project is a Python-based pipeline designed to ingest historical Tumblr Fandometrics data (specifically, annual "Top Ships" rankings) and transform it into a structured format for quantitative analysis and visualization.

The primary goal is to humorously track the **longevity, volatility, and categorical dominance** of popular ships across a decade of fandom history.

---

## 🔬 Analysis Focus

This pipeline generates detailed insights by cleaning and processing **10+ years of ranked data** into a single master file.

* **Line Gaps:** Lines on the generated graphs are **broken** (`NaN`) during years when a ship did not rank in the Top 100, preventing misleading trend lines.
* **Recurrence:** Tracks the total number of years each ship appeared on the list.
* **Media Longevity:** Analyzes whether ships originating from specific media (e.g., TV, Books, Anime) have higher long-term consistency.
* **Top Trends:** Generates a series of highly focused charts showing the rank evolution of the most consistent ships (e.g., ships appearing 5+ years).

---

## 📂 Project Structure

| File | Purpose |
| :--- | :--- |
| `main.py` | The **orchestrator**. Executes the entire pipeline: cleans data, runs analysis, and calls graph generation. |
| `process_data.py` | Handles all ETL (Extract, Transform, Load) operations, including reading raw files, merging data, and standardizing ship names (removing rank change noise). |
| `fandom_config.py` | **Configuration file.** Contains the master dictionary mapping Fandoms to standardized, multi-category media types (e.g., `'The Witcher': 'Books/TV/Video Games'`). |
| `ship_graphs.py` | Contains all Matplotlib/Seaborn functions for visualization, including the specialized gap-plotting and direct-labeling logic. |
| `XXXX_data.txt` | **Raw input files** (e.g., `2022_data.txt`). |

---

## 🚀 To Run the Analysis

1.  **Dependencies:** Ensure you have Python, Conda/Miniconda, and the required libraries:
    ```bash
    pip install pandas matplotlib seaborn
    ```
2.  **Execution:** Run the main file from your terminal (preferably in your activated Conda environment):
    ```bash
    python main.py
    ```

### Output Files

* `master_shipping_data_combined.csv`: The complete, cleaned dataset used for all analysis.
* `recurrent_ships_dip_to_edge.png`: The primary trend chart showing the most consistent ships.
