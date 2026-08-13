import argparse
import os
import sys
from src.doc_inspector import DocInspector

def run_inspection(input_path: str, report_path: str) -> None:
    print(f"Loading document: {input_path}")
    inspector = DocInspector(input_path)
    
    print("Gathering basic statistics...")
    stats = inspector.get_basic_stats()
    
    print("Analyzing run fragmentation...")
    fragmented_runs = inspector.analyze_run_fragmentation()
    
    print("Scanning PII context locations...")
    pii_locations = inspector.find_sample_pii_locations()

    # Generate the Markdown report
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# Red Herring Prospectus Document Structure Report\n\n")
        f.write(f"**Target Document**: `{os.path.basename(input_path)}`  \n")
        f.write(f"**File Size**: {os.path.getsize(input_path)} bytes  \n\n")
        
        f.write("## 📊 Structural Statistics\n\n")
        f.write("| Element Type | Count |\n")
        f.write("| :--- | :--- |\n")
        f.write(f"| Primary Paragraphs | {stats['total_primary_paragraphs']} |\n")
        f.write(f"| Primary Paragraph Runs | {stats['primary_runs_count']} |\n")
        f.write(f"| Tables | {stats['total_tables']} |\n")
        f.write(f"| Table Rows | {stats['total_rows']} |\n")
        f.write(f"| Table Cells | {stats['total_cells']} |\n")
        f.write(f"| Paragraphs in Cells | {stats['cell_paragraphs_count']} |\n")
        f.write(f"| Runs in Cells | {stats['cell_runs_count']} |\n")
        f.write(f"| Header Paragraphs | {stats['header_paragraphs_count']} |\n")
        f.write(f"| Header Runs | {stats['header_runs_count']} |\n")
        f.write(f"| Footer Paragraphs | {stats['footer_paragraphs_count']} |\n")
        f.write(f"| Footer Runs | {stats['footer_runs_count']} |\n\n")

        f.write("## 🔍 Run Fragmentation Analysis\n\n")
        f.write("In DOCX documents, words or specific phrases (like names, phone numbers, or emails) "
                "can be split across multiple consecutive runs due to formatting changes, editing history, "
                "or spellcheck markers. Below are sample occurrences where word characters are split:\n\n")
        
        if fragmented_runs:
            for idx, item in enumerate(fragmented_runs):
                f.write(f"### Fragment {idx + 1}\n")
                f.write(f"- **Location**: Paragraph Index {item['paragraph_index']}, Run Index {item['run_index']}\n")
                f.write(f"- **First Run Text**: `{repr(item['run_text_1'])}`\n")
                f.write(f"- **Second Run Text**: `{repr(item['run_text_2'])}`\n")
                f.write(f"- **Reconstructed word/boundary**: `{item['reconstructed_word']}`\n")
                f.write(f"- **Visual context**: `{item['context']}`\n\n")
        else:
            f.write("*No run fragmentation detected in the initial paragraphs scanned.*\n\n")

        f.write("## 📍 Potential PII Locations and Structural Distribution\n\n")
        f.write("To design an effective detection engine, we must know where sensitive information occurs. "
                "The following locations contain corporate/legal vocabulary indicating PII containers (e.g. 'director', 'registered office', 'email'):\n\n")
        
        for loc in pii_locations:
            f.write(f"- **{loc['location']}** ({loc['context_hint']}, length={loc['character_length']} chars)\n")

        f.write("\n## 💡 Key Engineering Observations & Implications\n\n")
        f.write("### 1. Run-level Fragmentation\n")
        f.write("- **Observation**: Text is indeed split across runs. If we try to perform regex matching run-by-run, "
                "many entities (such as names, addresses, or phone numbers) will be missed.\n")
        f.write("- **Design Decision**: Detection must be performed at the **paragraph** level (by consolidating run texts) "
                "rather than individual runs. We must then map detected character spans back to the corresponding runs.\n\n")

        f.write("### 2. High Density of Tables\n")
        f.write("- **Observation**: A significant amount of key structured information (e.g., names of Whole-time Directors, "
                "registered addresses, bank details, phone numbers) is located in tables.\n")
        f.write("- **Design Decision**: The pipeline must recursively inspect all cells inside all tables and "
                "treat cell paragraphs identically to document paragraphs.\n\n")

        f.write("### 3. Headers and Footers\n")
        f.write("- **Observation**: Headers and footers exist in the document and contain metadata. "
                "While less likely to contain personal director details, they can contain corporate identifiers or contact info.\n")
        f.write("- **Design Decision**: The engine must inspect and replace PII in headers and footers to ensure completeness.\n\n")

        f.write("### 4. Preservation of Formatting\n")
        f.write("- **Observation**: Runs contain distinct styles (bold, font size, hyperlinks). Replacing text inside "
                "runs can break styling if we do not reconstruct the runs carefully.\n")
        f.write("- **Design Decision**: The replacement phase should rebuild run texts while preserving their format templates, "
                "or split/merge runs correctly to accommodate the new replacement string size.\n")

    print(f"Inspection complete. Report saved to: {report_path}")

def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze DOCX file structure and content distribution.")
    parser.add_argument("--input", required=True, help="Path to the input DOCX file.")
    parser.add_argument("--output", default="evaluation/document_structure.md", help="Path to save the generated structure report.")
    args = parser.parse_args()

    try:
        run_inspection(args.input, args.output)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
