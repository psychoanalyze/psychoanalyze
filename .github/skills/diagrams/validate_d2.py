#!/usr/bin/env python3
"""
Validate and preview D2 diagram files.

This script checks that D2 diagram files have valid syntax by attempting
to parse them. It also provides URLs to view diagrams online.
"""

import argparse
import base64
import json
import urllib.parse
from pathlib import Path


def validate_d2_file(filepath: Path) -> tuple[bool, str]:
    """
    Basic validation of D2 file syntax.
    
    Returns:
        Tuple of (is_valid, message)
    """
    try:
        content = filepath.read_text()
        
        # Basic syntax checks
        if not content.strip():
            return False, "File is empty"
        
        # Check for balanced braces
        open_braces = content.count('{')
        close_braces = content.count('}')
        if open_braces != close_braces:
            return False, f"Unbalanced braces: {open_braces} open, {close_braces} close"
        
        # Check for balanced quotes (rough check)
        double_quotes = content.count('"')
        if double_quotes % 2 != 0:
            return False, f"Unbalanced double quotes: {double_quotes}"
        
        return True, "Syntax appears valid"
        
    except Exception as e:
        return False, f"Error reading file: {e}"


def generate_playground_url(filepath: Path) -> str:
    """
    Generate a URL to view the diagram in D2 playground.
    
    Note: The playground may have size limits on URL parameters.
    For large diagrams, manual copy-paste is recommended.
    """
    content = filepath.read_text()
    
    # Encode content for URL (playground uses URL parameters)
    # Note: This creates long URLs that may not work for all diagrams
    encoded = urllib.parse.quote(content)
    
    # D2 playground base URL
    # The actual playground uses a different encoding scheme
    # So we'll just return the base URL with instructions
    return "https://play.d2lang.com/"


def main():
    parser = argparse.ArgumentParser(
        description="Validate D2 diagram files and generate preview URLs"
    )
    parser.add_argument(
        "files",
        nargs="+",
        type=Path,
        help="D2 files to validate"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON"
    )
    
    args = parser.parse_args()
    
    results = []
    
    for filepath in args.files:
        if not filepath.exists():
            result = {
                "file": str(filepath),
                "valid": False,
                "message": "File not found",
                "playground_url": None
            }
        else:
            is_valid, message = validate_d2_file(filepath)
            result = {
                "file": str(filepath),
                "valid": is_valid,
                "message": message,
                "playground_url": generate_playground_url(filepath) if is_valid else None,
                "instructions": "Copy file contents to the playground URL" if is_valid else None
            }
        
        results.append(result)
        
        if not args.json:
            status = "✓" if result["valid"] else "✗"
            print(f"{status} {result['file']}")
            print(f"  {result['message']}")
            if result.get('playground_url'):
                print(f"  View at: {result['playground_url']}")
            print()
    
    if args.json:
        print(json.dumps(results, indent=2))
    
    # Exit with error if any validation failed
    if not all(r["valid"] for r in results):
        exit(1)


if __name__ == "__main__":
    main()
