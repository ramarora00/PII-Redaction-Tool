import argparse
import os
import sys

def validate_arguments(input_path: str, output_path: str) -> None:
    """
    Validates command line arguments.
    Raises ValueError or FileNotFoundError if validation fails.
    """
    if not input_path:
        raise ValueError("Input file path must be specified.")
    if not output_path:
        raise ValueError("Output file path must be specified.")
        
    if not input_path.lower().endswith(".docx"):
        raise ValueError(f"Input file '{input_path}' must have a .docx extension.")
        
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file '{input_path}' does not exist.")
        
    if not os.path.isfile(input_path):
        raise ValueError(f"Input path '{input_path}' is not a file.")

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Redact PII from a DOCX Red Herring Prospectus."
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to the input DOCX file."
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Path where the redacted DOCX file will be saved."
    )

    args = parser.parse_args()

    try:
        validate_arguments(args.input, args.output)
        print(f"Validation successful.")
        print(f"Input: {args.input}")
        print(f"Output: {args.output}")
        # PII detection & redaction logic to be added in future milestones.
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
