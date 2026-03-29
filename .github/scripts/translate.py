#!/usr/bin/env python3
"""
Translate MDX documentation files to Bulgarian using Claude API.
Preserves MDX syntax, frontmatter structure, code blocks, and component tags.
Uses Anthropic Claude for high-quality, context-aware translation.
"""

import os
import re
import sys
import json
import time
import yaml
from pathlib import Path

try:
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False

try:
    from deep_translator import GoogleTranslator
    HAS_GOOGLE = True
except ImportError:
    HAS_GOOGLE = False

# Configuration
SOURCE_DIR = os.environ.get("SOURCE_DIR", ".")
TARGET_LANG = os.environ.get("TARGET_LANG", "bg")
TARGET_DIR = os.environ.get("TARGET_DIR", "bg")
TRANSLATOR = os.environ.get("TRANSLATOR", "claude")  # "claude" or "google"

# Language names for prompts
LANG_NAMES = {
    "bg": "Bulgarian",
    "de": "German",
    "fr": "French",
    "es": "Spanish",
    "it": "Italian",
    "pt": "Portuguese",
    "ro": "Romanian",
    "tr": "Turkish",
    "ru": "Russian",
}

# Directories to skip
SKIP_DIRS = {".git", ".github", "node_modules", TARGET_DIR}

FRONTMATTER_PATTERN = re.compile(r'^---\n([\s\S]*?)\n---', re.MULTILINE)

# Initialize translators
claude_client = None
google_translator = None

if TRANSLATOR == "claude" and HAS_ANTHROPIC:
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if api_key:
        claude_client = anthropic.Anthropic(api_key=api_key)
        print("Using Claude API for translation (high quality)")
    else:
        print("Warning: ANTHROPIC_API_KEY not set, falling back to Google Translate")
        TRANSLATOR = "google"

if TRANSLATOR == "google" or not claude_client:
    if HAS_GOOGLE:
        google_translator = GoogleTranslator(source='en', target=TARGET_LANG)
        print("Using Google Translate (fallback)")
    else:
        print("ERROR: No translation backend available. Install anthropic or deep-translator.")
        sys.exit(1)


def translate_with_claude(text, context="documentation"):
    """Translate text using Claude API with context awareness."""
    lang_name = LANG_NAMES.get(TARGET_LANG, TARGET_LANG)

    response = claude_client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=8000,
        messages=[{
            "role": "user",
            "content": f"""Translate the following MDX documentation content from English to {lang_name}.

CRITICAL RULES:
1. Translate ALL prose text naturally into {lang_name} — use proper grammar and natural phrasing
2. DO NOT translate: code blocks (```...```), inline code (`...`), URLs, file paths, API endpoints, variable names, parameter names, JSON keys
3. DO NOT translate: MDX/JSX component tags like <Card>, <Tabs>, <Note>, <Warning>, <Tip>, etc.
4. DO NOT translate: import statements
5. DO translate: titles, descriptions, headings, paragraphs, list items, link text, button labels
6. Keep the EXACT same MDX structure and formatting (headings, lists, bold, italic, etc.)
7. Keep frontmatter YAML keys in English, only translate the string VALUES of title, description, and sidebarTitle
8. Brand names like "Aiplocalls" should stay as-is
9. Technical terms that are commonly used in English in {lang_name} IT context can stay in English (e.g., API, webhook, SIP, etc.)

Return ONLY the translated content, nothing else. No explanations or notes.

Content to translate:
---
{text}
---"""
        }]
    )

    return response.content[0].text.strip()


def translate_with_google(text):
    """Translate text using Google Translate (fallback)."""
    if len(text) > 4500:
        # Split into chunks
        chunks = []
        current = []
        current_len = 0
        for line in text.split('\n'):
            if current_len + len(line) > 4000:
                chunks.append('\n'.join(current))
                current = [line]
                current_len = len(line)
            else:
                current.append(line)
                current_len += len(line) + 1
        if current:
            chunks.append('\n'.join(current))

        translated_chunks = []
        for chunk in chunks:
            try:
                result = google_translator.translate(chunk)
                translated_chunks.append(result)
                time.sleep(0.5)
            except Exception as e:
                print(f"    Google Translate error: {e}")
                translated_chunks.append(chunk)
        return '\n'.join(translated_chunks)
    else:
        return google_translator.translate(text)


def translate_file(source_path, target_path):
    """Translate a single MDX file."""
    print(f"  Translating: {source_path}")

    with open(source_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Skip very small files or files with no translatable content
    if len(content.strip()) < 20:
        write_file(target_path, content)
        return

    if TRANSLATOR == "claude" and claude_client:
        try:
            translated = translate_with_claude(content)
            # Basic sanity check — make sure frontmatter is preserved
            if content.startswith('---') and not translated.startswith('---'):
                translated = '---\n' + translated
            write_file(target_path, translated)
            time.sleep(1)  # Rate limiting for Claude API
            return
        except Exception as e:
            print(f"    Claude error: {e}, falling back to Google Translate")

    # Fallback: Google Translate with MDX protection
    if HAS_GOOGLE:
        try:
            # Extract frontmatter
            fm_match = FRONTMATTER_PATTERN.match(content)
            if fm_match:
                fm_text = fm_match.group(1)
                body = content[fm_match.end():]

                # Translate frontmatter fields
                translated_fm = translate_frontmatter_google(fm_text)
                translated_body = translate_with_google(body) if body.strip() else ""

                result = f"---\n{translated_fm}\n---{translated_body}"
            else:
                result = translate_with_google(content)

            write_file(target_path, result)
            time.sleep(0.5)
        except Exception as e:
            print(f"    Translation error: {e}, copying original")
            write_file(target_path, content)
    else:
        write_file(target_path, content)


def translate_frontmatter_google(fm_text):
    """Translate frontmatter title/description using Google Translate."""
    try:
        fm = yaml.safe_load(fm_text)
        if not isinstance(fm, dict):
            return fm_text

        for key in ['title', 'description', 'sidebarTitle']:
            if key in fm and isinstance(fm[key], str) and fm[key].strip():
                try:
                    fm[key] = google_translator.translate(fm[key])
                    time.sleep(0.3)
                except:
                    pass

        lines = []
        for line in fm_text.split('\n'):
            matched = False
            for key in ['title', 'description', 'sidebarTitle']:
                if line.strip().startswith(f'{key}:') and key in fm:
                    indent = len(line) - len(line.lstrip())
                    val = fm[key]
                    if isinstance(val, str):
                        lines.append(f'{" " * indent}{key}: "{val}"')
                        matched = True
                        break
            if not matched:
                lines.append(line)
        return '\n'.join(lines)
    except:
        return fm_text


def write_file(path, content):
    """Write content to file, creating directories as needed."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)


def get_mdx_files(source_dir):
    """Get all MDX files to translate."""
    files = []
    for root, dirs, filenames in os.walk(source_dir):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for filename in filenames:
            if filename.endswith('.mdx'):
                filepath = os.path.join(root, filename)
                rel_path = os.path.relpath(filepath, source_dir)
                files.append(rel_path)
    return sorted(files)


def main():
    only_files = os.environ.get("ONLY_FILES", "")
    lang_name = LANG_NAMES.get(TARGET_LANG, TARGET_LANG)

    print(f"\n{'='*60}")
    print(f"  Documentation Translation to {lang_name}")
    print(f"  Backend: {TRANSLATOR}")
    print(f"  Source: {SOURCE_DIR}")
    print(f"  Target: {TARGET_DIR}/")
    print(f"{'='*60}\n")

    if only_files:
        files = [f.strip() for f in only_files.split(',') if f.strip()]
        print(f"Translating {len(files)} specific files...\n")
    else:
        files = get_mdx_files(SOURCE_DIR)
        print(f"Found {len(files)} MDX files to translate\n")

    translated = 0
    errors = 0

    for i, rel_path in enumerate(files):
        source_path = os.path.join(SOURCE_DIR, rel_path)
        target_path = os.path.join(SOURCE_DIR, TARGET_DIR, rel_path)

        if not os.path.exists(source_path):
            print(f"  Skipping (not found): {source_path}")
            continue

        try:
            print(f"[{i+1}/{len(files)}]", end="")
            translate_file(source_path, target_path)
            translated += 1
        except Exception as e:
            print(f"  ERROR: {rel_path}: {e}")
            errors += 1
            # Copy original as fallback
            with open(source_path, 'r') as src:
                write_file(target_path, src.read())

    print(f"\n{'='*60}")
    print(f"  Translation complete!")
    print(f"  Translated: {translated}")
    print(f"  Errors: {errors}")
    print(f"  Output: {TARGET_DIR}/")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
