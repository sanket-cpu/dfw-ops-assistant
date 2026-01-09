"""
Robust .env file loader with automatic encoding detection.

This module provides a drop-in replacement for python-dotenv's load_dotenv()
that can handle files encoded in UTF-16, UTF-8, or other common encodings.
"""

import os
import logging
from pathlib import Path
from dotenv import load_dotenv, find_dotenv

logger = logging.getLogger(__name__)


def load_env_robust(env_path: str = None) -> bool:
    """
    Load .env file with automatic encoding detection.

    Attempts to load the .env file using standard UTF-8 encoding first.
    If that fails with a UnicodeDecodeError, tries alternative encodings
    commonly used on Windows systems (UTF-16, Latin-1, etc.).

    Args:
        env_path: Path to .env file. If None, uses find_dotenv() to locate it.

    Returns:
        True if .env was loaded successfully, False otherwise.

    Example:
        >>> from env_loader import load_env_robust
        >>> if not load_env_robust():
        ...     logger.warning("Failed to load .env file")
    """
    # Step 1: Find .env file
    if env_path is None:
        env_path = find_dotenv()

    if not env_path or not Path(env_path).exists():
        logger.warning(".env file not found. Using system environment variables only.")
        return False

    # Step 2: Try standard load_dotenv first (UTF-8)
    try:
        load_dotenv(env_path)
        logger.info(f"Loaded .env from {env_path}")
        return True
    except UnicodeDecodeError:
        logger.info("UTF-8 decoding failed, trying alternative encodings...")
    except Exception as e:
        logger.error(f"Unexpected error loading .env: {e}")
        return False

    # WHY this encoding order: Windows Notepad saves as UTF-16 by default when users paste
    # API keys containing non-ASCII characters. UTF-16-LE is most common on Windows.
    # Latin-1 is last resort - it "succeeds" on any byte sequence but may produce garbage.
    encodings = ['utf-16', 'utf-16-le', 'utf-16-be', 'latin-1', 'cp1252']

    for encoding in encodings:
        try:
            content = Path(env_path).read_text(encoding=encoding)
            logger.info(f"Successfully read .env using {encoding} encoding")

            # Step 4: Parse and inject into os.environ
            _parse_and_inject_env(content)

            # Step 5: Warn user about non-standard encoding
            logger.warning(
                f"\n{'='*60}\n"
                f"WARNING: .env file is encoded as {encoding.upper()}.\n"
                f"For better compatibility, convert to UTF-8 by running:\n"
                f"  python scripts/fix_env_encoding.py\n"
                f"{'='*60}"
            )
            return True

        except (UnicodeDecodeError, UnicodeError):
            continue
        except Exception as e:
            logger.error(f"Error reading .env with {encoding}: {e}")
            continue

    # Step 6: All encodings failed
    logger.error(
        f"\n{'='*60}\n"
        f"ERROR: Could not read .env file with any supported encoding.\n"
        f"The file may be corrupted or in an unsupported format.\n"
        f"\n"
        f"To fix this:\n"
        f"1. Backup your current .env file\n"
        f"2. Copy .env.example to .env\n"
        f"3. Edit .env and add your OPENAI_API_KEY\n"
        f"4. Ensure the file is saved as UTF-8 encoding\n"
        f"{'='*60}"
    )
    return False


def _parse_and_inject_env(content: str):
    """
    Parse .env file content and inject variables into os.environ.

    WHY manual parser instead of load_dotenv: python-dotenv's load_dotenv() doesn't accept
    already-decoded string content or an encoding parameter. When we detect non-UTF-8 encoding,
    we must decode the file ourselves, then parse. This minimal parser handles the common cases.

    Supports the standard KEY=VALUE format with:
    - Comments (lines starting with #)
    - Empty lines
    - Quoted values (single or double quotes)
    - Whitespace trimming

    Args:
        content: Raw content of .env file as string.
    """
    for line in content.split('\n'):
        line = line.strip()

        # Skip empty lines and comments
        if not line or line.startswith('#'):
            continue

        # Parse KEY=VALUE format
        if '=' in line:
            # WHY split('=', 1): Values can contain = signs, e.g. DATABASE_URL="postgres://...?sslmode=require"
            # Without maxsplit=1, this would break into 3 parts. Only the first = separates key from value.
            key, value = line.split('=', 1)
            key = key.strip()
            value = value.strip()

            # Remove quotes if present
            if len(value) >= 2:
                if (value.startswith('"') and value.endswith('"')) or \
                   (value.startswith("'") and value.endswith("'")):
                    value = value[1:-1]

            # Set environment variable
            os.environ[key] = value
            logger.debug(f"Set environment variable: {key}")
