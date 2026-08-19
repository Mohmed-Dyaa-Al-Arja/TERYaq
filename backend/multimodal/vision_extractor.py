from __future__ import annotations

import base64
import json
import os
import time
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from groq import Groq


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

METADATA_FILE = (
    BASE_DIR
    / "processed"
    / "metadata"
    / "visual_evidence.json"
)

OUTPUT_FILE = (
    BASE_DIR
    / "processed"
    / "metadata"
    / "visual_extracted_evidence.json"
)

FAILED_FILE = (
    BASE_DIR
    / "processed"
    / "metadata"
    / "visual_failed_evidence.json"
)


# ============================================================
# MODEL
# ============================================================

MODEL_NAME = os.getenv(
    "MODEL_NAME",
    "qwen/qwen3.6-27b"
)

MAX_COMPLETION_TOKENS = 1600
TEMPERATURE = 0.0

# Don't hammer Groq after rate limit
RATE_LIMIT_WAIT = 60

# Number of attempts for temporary API failures
MAX_RETRIES = 2


# ============================================================
# ENV
# ============================================================

load_dotenv(
    BASE_DIR / ".env",
    override=True
)

GROQ_API_KEY = os.getenv(
    "GROQ_API_KEY"
)

if not GROQ_API_KEY:
    raise RuntimeError(
        "GROQ_API_KEY is missing from .env"
    )


client = Groq(
    api_key=GROQ_API_KEY
)


# ============================================================
# SYSTEM PROMPT
# ============================================================

VISION_SYSTEM_PROMPT = """
You are the Visual Evidence Extraction component of TERYAQ,
a grounded medical information retrieval system.

Your ONLY task is to extract information that is visibly
present in the supplied medical document image.

STRICT RULES:

1. Use ONLY information visible in the supplied image.
2. Do NOT use outside knowledge.
3. Do NOT diagnose patients.
4. Do NOT recommend treatment.
5. Do NOT recommend medication.
6. Do NOT infer patient-specific medical conditions.
7. Do NOT invent values.
8. Do NOT invent labels.
9. Do NOT invent relationships.
10. Do NOT calculate values that are not explicitly shown.
11. If something is unreadable, say "unreadable".
12. If a value cannot be confidently read, say
    "not clearly readable".
13. Never estimate chart values.
14. Never convert a visual pattern into an unsupported
    medical conclusion.

Extract:

- visual type
- visual elements
- semantic title
- source caption
- visible text
- labels
- legend
- axes
- categories
- explicitly readable values
- directly visible relationships
- directly visible observations
- uncertainties

Return ONLY valid JSON.
"""


# ============================================================
# IMAGE
# ============================================================

def image_to_data_url(
    image_path: Path
) -> str:

    image_bytes = image_path.read_bytes()

    encoded = base64.b64encode(
        image_bytes
    ).decode("utf-8")

    return (
        "data:image/png;base64,"
        + encoded
    )


# ============================================================
# PROMPT
# ============================================================

def build_prompt(
    metadata: dict[str, Any]
) -> str:

    caption = metadata.get(
        "caption",
        ""
    )

    visual_type = metadata.get(
        "visual_type",
        "unknown"
    )

    return f"""
SOURCE DOCUMENT:
{metadata.get("document", "unknown")}

DOCUMENT ID:
{metadata.get("document_id", "unknown")}

PAGE:
{metadata.get("page", "unknown")}

DETECTOR VISUAL TYPE:
{visual_type}

DETECTOR VISUAL IDS:
{", ".join(metadata.get("visual_ids", []))}

SOURCE CAPTION:
{caption if caption else "not available"}


Analyze the image itself.

Do not blindly trust the detector visual type.

Return EXACTLY:

{{
  "evidence_type": "visual",
  "visual_type": "",
  "visual_elements": [],
  "semantic_title": "",
  "source_caption": "",
  "visible_text": [],
  "labels": [],
  "legend": [],
  "axes": [],
  "categories": [],
  "explicit_values": [],
  "relationships": [],
  "visible_observations": [],
  "uncertainties": []
}}

VISUAL TYPE must be one of:

photograph
map
chart
graph
table
diagram
flowchart
timeline
illustration
text
mixed
unknown

IMPORTANT:

- Only extract visible information.
- Do not estimate values.
- Do not infer medical conclusions.
- Do not recommend treatment.
- Do not prescribe medication.
- Put unreadable information in uncertainties.
"""


# ============================================================
# JSON
# ============================================================

def parse_json(
    text: str
) -> dict[str, Any]:

    text = text.strip()

    if text.startswith("```"):

        lines = text.splitlines()

        if len(lines) > 1:
            lines = lines[1:]

        if (
            lines
            and lines[-1].strip() == "```"
        ):
            lines = lines[:-1]

        text = "\n".join(lines).strip()

    try:

        result = json.loads(text)

        if isinstance(result, dict):
            return result

    except json.JSONDecodeError:
        pass

    return {
        "evidence_type": "visual",
        "parse_error": True,
        "raw_response": text
    }


# ============================================================
# NORMALIZE
# ============================================================

def normalize(
    evidence: dict[str, Any]
) -> dict[str, Any]:

    fields = [
        "visual_elements",
        "visible_text",
        "labels",
        "legend",
        "axes",
        "categories",
        "explicit_values",
        "relationships",
        "visible_observations",
        "uncertainties",
    ]

    result = {
        "evidence_type": "visual",

        "visual_type": evidence.get(
            "visual_type",
            "unknown"
        ),

        "visual_elements": evidence.get(
            "visual_elements",
            []
        ),

        "semantic_title": evidence.get(
            "semantic_title",
            ""
        ),

        "source_caption": evidence.get(
            "source_caption",
            ""
        ),

        "visible_text": evidence.get(
            "visible_text",
            []
        ),

        "labels": evidence.get(
            "labels",
            []
        ),

        "legend": evidence.get(
            "legend",
            []
        ),

        "axes": evidence.get(
            "axes",
            []
        ),

        "categories": evidence.get(
            "categories",
            []
        ),

        "explicit_values": evidence.get(
            "explicit_values",
            []
        ),

        "relationships": evidence.get(
            "relationships",
            []
        ),

        "visible_observations": evidence.get(
            "visible_observations",
            []
        ),

        "uncertainties": evidence.get(
            "uncertainties",
            []
        ),
    }

    for field in fields:

        if not isinstance(
            result[field],
            list
        ):

            result[field] = [
                str(result[field])
            ]

    return result


# ============================================================
# GROQ CALL
# ============================================================

def extract_visual_evidence(
    image_path: Path,
    metadata: dict[str, Any]
) -> dict[str, Any]:

    image_url = image_to_data_url(
        image_path
    )

    prompt = build_prompt(
        metadata
    )

    response = client.chat.completions.create(

        model=MODEL_NAME,

        messages=[
            {
                "role": "system",
                "content": VISION_SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_url
                        }
                    }
                ]
            }
        ],

        temperature=TEMPERATURE,

        max_completion_tokens=(
            MAX_COMPLETION_TOKENS
        ),

        reasoning_effort="none",

        response_format={
            "type": "json_object"
        }
    )

    content = (
        response
        .choices[0]
        .message
        .content
    )

    return normalize(
        parse_json(content)
    )


# ============================================================
# LOAD JSON
# ============================================================

def load_json(
    path: Path,
    default: Any
) -> Any:

    if not path.exists():
        return default

    try:

        with open(
            path,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    except Exception:

        return default


# ============================================================
# SAVE JSON
# ============================================================

def save_json(
    path: Path,
    data: Any
):

    path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            ensure_ascii=False,
            indent=2
        )


# ============================================================
# RESULT ID
# ============================================================

def make_evidence_id(
    metadata: dict[str, Any]
) -> str:

    return (
        f"{metadata.get('document_id', 'DOC')}"
        f"_p{metadata.get('page', 'unknown')}"
        f"_visual"
    )


# ============================================================
# MAIN PROCESS
# ============================================================

def process_visuals():

    metadata = load_json(
        METADATA_FILE,
        []
    )

    if not metadata:

        raise RuntimeError(
            "No visual metadata found."
        )

    existing_results = load_json(
        OUTPUT_FILE,
        []
    )

    failed_results = load_json(
        FAILED_FILE,
        []
    )

    # --------------------------------------------------------
    # Build indexes
    # --------------------------------------------------------

    completed_ids = {
        item.get("evidence_id")
        for item in existing_results
        if item.get("evidence_id")
    }

    failed_ids = {
        item.get("evidence_id")
        for item in failed_results
        if item.get("evidence_id")
    }

    print("=" * 70)
    print("TERYaq - RESUMABLE VISUAL EXTRACTION")
    print("=" * 70)

    print(
        f"Total visuals: {len(metadata)}"
    )

    print(
        f"Already completed: "
        f"{len(completed_ids)}"
    )

    print(
        f"Previously failed: "
        f"{len(failed_ids)}"
    )

    # --------------------------------------------------------
    # Process only missing visuals
    # --------------------------------------------------------

    pending = []

    for item in metadata:

        evidence_id = make_evidence_id(
            item
        )

        if evidence_id in completed_ids:
            continue

        pending.append(item)

    print(
        f"Pending visuals: "
        f"{len(pending)}"
    )

    if not pending:

        print(
            "\nAll visual evidence already extracted."
        )

        return existing_results

    # --------------------------------------------------------
    # Process
    # --------------------------------------------------------

    for index, item in enumerate(
        pending,
        start=1
    ):

        evidence_id = make_evidence_id(
            item
        )

        image_path = (
            BASE_DIR
            / item["image_path"]
        )

        print("\n" + "=" * 70)

        print(
            f"[{index}/{len(pending)}]"
        )

        print(
            f"Page: "
            f"{item.get('page')}"
        )

        print(
            f"Type: "
            f"{item.get('visual_type')}"
        )

        print(
            f"Image: "
            f"{image_path.name}"
        )

        print("=" * 70)

        if not image_path.exists():

            failed_results.append({

                "evidence_id":
                    evidence_id,

                "page":
                    item.get("page"),

                "image_path":
                    item.get("image_path"),

                "error":
                    "image_not_found"
            })

            save_json(
                FAILED_FILE,
                failed_results
            )

            continue

        success = False

        for attempt in range(
            1,
            MAX_RETRIES + 1
        ):

            try:

                evidence = (
                    extract_visual_evidence(
                        image_path,
                        item
                    )
                )

                result = {

                    "evidence_id":
                        evidence_id,

                    "document_id":
                        item.get(
                            "document_id",
                            "unknown"
                        ),

                    "document":
                        item.get(
                            "document",
                            "unknown"
                        ),

                    "page":
                        item.get(
                            "page",
                            "unknown"
                        ),

                    "image_path":
                        item.get(
                            "image_path",
                            ""
                        ),

                    "source_detector_type":
                        item.get(
                            "visual_type",
                            "unknown"
                        ),

                    "extraction_model":
                        MODEL_NAME,

                    "visual_evidence":
                        evidence
                }

                existing_results.append(
                    result
                )

                # Save immediately.
                save_json(
                    OUTPUT_FILE,
                    existing_results
                )

                # Remove from failed list if
                # it succeeded now.
                failed_results = [
                    item
                    for item in failed_results
                    if item.get(
                        "evidence_id"
                    ) != evidence_id
                ]

                save_json(
                    FAILED_FILE,
                    failed_results
                )

                print(
                    "\nSUCCESS"
                )

                print(
                    json.dumps(
                        evidence,
                        ensure_ascii=False,
                        indent=2
                    )
                )

                success = True

                break

            except Exception as exc:

                error_text = str(exc)

                print(
                    f"\nAttempt {attempt} failed:"
                )

                print(
                    error_text
                )

                # ------------------------------------------------
                # Rate limit
                # ------------------------------------------------

                if (
                    "429"
                    in error_text
                    or "rate_limit"
                    in error_text.lower()
                    or "rate limit"
                    in error_text.lower()
                ):

                    print(
                        "\nRATE LIMIT DETECTED."
                    )

                    print(
                        "Stopping safely."
                    )

                    print(
                        "Already completed "
                        "results were saved."
                    )

                    save_json(
                        OUTPUT_FILE,
                        existing_results
                    )

                    save_json(
                        FAILED_FILE,
                        failed_results
                    )

                    return existing_results

                # ------------------------------------------------
                # Temporary retry
                # ------------------------------------------------

                if attempt < MAX_RETRIES:

                    print(
                        f"Retrying in "
                        f"{RATE_LIMIT_WAIT} seconds..."
                    )

                    time.sleep(
                        RATE_LIMIT_WAIT
                    )

        # --------------------------------------------------------
        # Permanent failure
        # --------------------------------------------------------

        if not success:

            failed_results.append({

                "evidence_id":
                    evidence_id,

                "document_id":
                    item.get(
                        "document_id"
                    ),

                "page":
                    item.get(
                        "page"
                    ),

                "image_path":
                    item.get(
                        "image_path"
                    ),

                "error":
                    "vision_extraction_failed"
            })

            save_json(
                FAILED_FILE,
                failed_results
            )

    return existing_results


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    results = process_visuals()

    print("\n" + "=" * 70)
    print("VISUAL EXTRACTION STATUS")
    print("=" * 70)

    print(
        f"Saved evidence: "
        f"{len(results)}"
    )

    print(
        f"Output: "
        f"{OUTPUT_FILE}"
    )

    print(
        f"Failed log: "
        f"{FAILED_FILE}"
    )

    print("=" * 70)

