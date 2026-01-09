#!/usr/bin/env python3
"""
Fix .env file encoding by converting it to UTF-8.

This script safely converts a .env file from any encoding (UTF-16, Latin-1, etc.)
to UTF-8 encoding, which is the standard expected by python-dotenv.

Usage:
    python scripts/fix_env_encoding.py
"""

import os
import sys
from pathlib import Path
from datetime import datetime


def detect_and_read_env(env_path: Path) -> str:
    """
    Try to read .env file with multiple encodings.

    Args:
        env_path: Path to the .env file

    Returns:
        Content of the .env file as a string

    Raises:
        ValueError: If file cannot be read with any supported encoding
    """
    encodings = ['utf-8', 'utf-16', 'utf-16-le', 'utf-16-be', 'latin-1', 'cp1252']

    for encoding in encodings:
        try:
            content = env_path.read_text(encoding=encoding)
            print(f"[OK] Successfully read .env using {encoding.upper()} encoding")
            return content
        except (UnicodeDecodeError, UnicodeError):
            continue
        except Exception as e:
            print(f"  Error reading with {encoding}: {e}")
            continue

    raise ValueError(
        "Could not read .env file with any supported encoding. "
        "File may be corrupted."
    )


def create_backup(env_path: Path) -> Path:
    """
    Create a timestamped backup of the .env file.

    Args:
        env_path: Path to the .env file

    Returns:
        Path to the backup file
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = env_path.parent / f".env.backup-{timestamp}"

    # Copy original file as-is (binary mode to preserve encoding)
    backup_path.write_bytes(env_path.read_bytes())

    print(f"[OK] Created backup: {backup_path.name}")
    return backup_path


def write_utf8_env(env_path: Path, content: str):
    """
    Write .env file with UTF-8 encoding (no BOM).

    Args:
        env_path: Path to the .env file
        content: Content to write
    """
    env_path.write_text(content, encoding='utf-8')
    print(f"[OK] Wrote new .env file with UTF-8 encoding")


def verify_env_file(env_path: Path) -> bool:
    """
    Verify the .env file can be read correctly with python-dotenv.

    Args:
        env_path: Path to the .env file

    Returns:
        True if file is valid, False otherwise
    """
    try:
        from dotenv import load_dotenv
        import tempfile

        # Create a temporary copy to test
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False, encoding='utf-8') as tmp:
            tmp.write(env_path.read_text(encoding='utf-8'))
            tmp_path = tmp.name

        try:
            # Try loading with dotenv
            load_dotenv(tmp_path)
            print("[OK] Verified: File loads correctly with python-dotenv")
            return True
        finally:
            os.unlink(tmp_path)

    except Exception as e:
        print(f"[ERROR] Verification failed: {e}")
        return False


def main():
    """Main function to fix .env encoding."""
    print("=" * 60)
    print("Fix .env File Encoding")
    print("=" * 60)
    print()

    # Find .env file
    env_path = Path(__file__).parent.parent / ".env"

    if not env_path.exists():
        print(f"[ERROR] .env file not found at {env_path}")
        print()
        print("To create a .env file:")
        print("  1. Copy .env.example to .env")
        print("  2. Edit .env and add your OPENAI_API_KEY")
        print("  3. Ensure the file is saved as UTF-8 encoding")
        sys.exit(1)

    print(f"Found .env at: {env_path}")
    print()

    try:
        # Step 1: Read current .env with encoding detection
        print("Step 1: Reading current .env file...")
        content = detect_and_read_env(env_path)
        print()

        # Step 2: Create backup
        print("Step 2: Creating backup...")
        backup_path = create_backup(env_path)
        print()

        # Step 3: Write UTF-8 version
        print("Step 3: Writing UTF-8 encoded .env file...")
        write_utf8_env(env_path, content)
        print()

        # Step 4: Verify
        print("Step 4: Verifying new .env file...")
        if verify_env_file(env_path):
            print()
            print("=" * 60)
            print("SUCCESS!")
            print("=" * 60)
            print()
            print("Your .env file has been converted to UTF-8 encoding.")
            print(f"Original file backed up as: {backup_path.name}")
            print()
            print("Next steps:")
            print("  1. Start your backend: cd backend && uvicorn api:app --reload")
            print("  2. The encoding warning should no longer appear")
            print()
        else:
            print()
            print("=" * 60)
            print("WARNING")
            print("=" * 60)
            print()
            print("The file was converted but verification failed.")
            print("Please check the .env file manually.")
            print(f"You can restore from backup: {backup_path.name}")
            sys.exit(1)

    except ValueError as e:
        print(f"[ERROR] {e}")
        print()
        print("Unable to read .env file. Try these steps:")
        print("  1. Delete the current .env file")
        print("  2. Copy .env.example to .env")
        print("  3. Edit .env and add your OPENAI_API_KEY")
        print("  4. Save the file as UTF-8 encoding")
        sys.exit(1)

    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        print()
        print("If the problem persists:")
        print("  1. Manually delete .env")
        print("  2. Copy .env.example to .env")
        print("  3. Edit with a text editor that supports UTF-8")
        sys.exit(1)


if __name__ == "__main__":
    main()
