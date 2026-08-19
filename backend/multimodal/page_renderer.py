from pathlib import Path
import json
import re

import pymupdf


# ============================================================
# Paths
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

DATA_DIR = BASE_DIR / "data" / "pdf"
OUTPUT_DIR = BASE_DIR / "processed" / "pages"
METADATA_DIR = BASE_DIR / "processed" / "metadata"

VISUAL_METADATA_FILE = METADATA_DIR / "visual_evidence.json"


# ============================================================
# Configuration
# ============================================================

MIN_IMAGE_AREA_RATIO = 0.03

CAPTION_PATTERNS = [
    r"^\s*(figure|fig\.?)\s*\d+[A-Za-z]*",
    r"^\s*fig\s+\d+[A-Za-z]*",
    r"^\s*(map)\s*\d+[A-Za-z]*",
    r"^\s*(chart)\s*\d+[A-Za-z]*",
    r"^\s*(graph)\s*\d+[A-Za-z]*",
]


# ============================================================
# Filename helpers
# ============================================================

def slugify(text: str, max_length: int = 100) -> str:
    """
    Convert text into a safe filename fragment.
    """

    text = text.lower()

    text = re.sub(
        r"[^a-z0-9]+",
        "_",
        text,
    )

    text = re.sub(
        r"_+",
        "_",
        text,
    )

    text = text.strip("_")

    return text[:max_length].rstrip("_")


def get_document_name(pdf_path: Path) -> str:
    """
    Convert PDF filename into a short document identifier.
    """

    name = pdf_path.stem.lower()

    if "9789240065987" in name:
        return "WHO_GBCI"

    if "breast-cancer-screening" in name:
        return "USPSTF_BC"

    return slugify(pdf_path.stem, 30).upper()


# ============================================================
# Embedded image detection
# ============================================================

def get_large_embedded_images(page):

    page_area = page.rect.width * page.rect.height

    if page_area <= 0:
        return []

    large_images = []

    for image in page.get_images(full=True):

        xref = image[0]

        try:
            rects = page.get_image_rects(xref)
        except Exception:
            continue

        for rect in rects:

            image_area = rect.width * rect.height

            area_ratio = image_area / page_area

            if area_ratio >= MIN_IMAGE_AREA_RATIO:

                large_images.append({
                    "xref": xref,
                    "area_ratio": area_ratio,
                    "rect": rect,
                })

    return large_images


# ============================================================
# Caption detection
# ============================================================

def find_visual_captions(page):

    captions = []

    blocks = page.get_text("blocks")

    for block in blocks:

        if len(block) < 5:
            continue

        text = block[4].strip()

        if not text:
            continue

        first_line = text.splitlines()[0].strip()

        for pattern in CAPTION_PATTERNS:

            if re.match(
                pattern,
                first_line,
                flags=re.IGNORECASE,
            ):

                captions.append({
                    "text": text,
                    "bbox": block[:4],
                })

                break

    return captions


# ============================================================
# Visual type
# ============================================================

def detect_visual_type(captions):

    if not captions:
        return "visual"

    caption_text = " ".join(
        c["text"].lower()
        for c in captions
    )

    if "map" in caption_text:
        return "map"

    if "table" in caption_text:
        return "table"

    if "chart" in caption_text:
        return "chart"

    if "graph" in caption_text:
        return "graph"

    if "fig." in caption_text or "figure" in caption_text:
        return "figure"

    return "visual"


# ============================================================
# Visual IDs
# ============================================================

def extract_visual_ids(captions):

    ids = []

    pattern = re.compile(
        r"\b(?:figure|fig\.?|map|chart|graph)\s+\d+[A-Za-z]*",
        flags=re.IGNORECASE,
    )

    for caption in captions:

        matches = pattern.findall(
            caption["text"]
        )

        for match in matches:

            normalized = re.sub(
                r"\s+",
                " ",
                match.strip(),
            )

            if normalized not in ids:
                ids.append(normalized)

    return ids


# ============================================================
# Detection
# ============================================================

def detect_visual_page(page):

    large_images = get_large_embedded_images(page)

    captions = find_visual_captions(page)

    if not large_images and not captions:
        return None

    return {
        "large_images": large_images,
        "captions": captions,
    }


# ============================================================
# Build meaningful filename
# ============================================================

def build_image_filename(
    pdf_path: Path,
    page_number: int,
    visual_type: str,
    captions,
):

    document_name = get_document_name(
        pdf_path
    )

    visual_ids = extract_visual_ids(
        captions
    )

    if visual_ids:

        ids_text = "_".join(
            slugify(v)
            for v in visual_ids
        )

    else:

        ids_text = "visual"

    # Build semantic description
    description_parts = []

    for caption in captions:

        text = caption["text"]

        # Remove visual ID from beginning
        text = re.sub(
            r"^\s*(figure|fig\.?|map|chart|graph)\s+\d+[A-Za-z]*\.?\s*",
            "",
            text,
            flags=re.IGNORECASE,
        )

        description_parts.append(text)

    description = " ".join(
        description_parts
    )

    description = slugify(
        description,
        max_length=80,
    )

    if not description:
        description = "visual"

    filename = (
        f"{document_name}"
        f"_p{page_number:03d}"
        f"_{visual_type}"
        f"_{ids_text}"
        f"_{description}"
        f".png"
    )

    return filename


# ============================================================
# Render page
# ============================================================

def render_page(
    page,
    pdf_path: Path,
    page_number: int,
    visual_type: str,
    captions,
    output_dir: Path = OUTPUT_DIR,
    dpi: int = 150,
):

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    filename = build_image_filename(
        pdf_path=pdf_path,
        page_number=page_number,
        visual_type=visual_type,
        captions=captions,
    )

    output_path = (
        output_dir / filename
    )

    zoom = dpi / 72

    matrix = pymupdf.Matrix(
        zoom,
        zoom,
    )

    pixmap = page.get_pixmap(
        matrix=matrix,
        alpha=False,
    )

    pixmap.save(
        str(output_path)
    )

    return output_path


# ============================================================
# Process PDF
# ============================================================

def process_pdf(
    pdf_path: Path,
    output_dir: Path = OUTPUT_DIR,
    dpi: int = 150,
):

    doc = pymupdf.open(
        str(pdf_path)
    )

    total_pages = len(doc)

    selected_pages = []
    generated_images = []

    print("\n" + "=" * 70)
    print(f"PDF: {pdf_path.name}")
    print(f"Total pages: {total_pages}")
    print("=" * 70)

    for page_index in range(total_pages):

        page = doc[page_index]

        page_number = page_index + 1

        visual_data = detect_visual_page(
            page
        )

        if visual_data is None:
            continue

        captions = visual_data["captions"]

        visual_type = detect_visual_type(
            captions
        )

        image_path = render_page(
            page=page,
            pdf_path=pdf_path,
            page_number=page_number,
            visual_type=visual_type,
            captions=captions,
            output_dir=output_dir,
            dpi=dpi,
        )

        visual_ids = extract_visual_ids(
            captions
        )

        caption_text = " ".join(
            c["text"]
            for c in captions
        ).strip()

        metadata = {
            "image_path": str(
                image_path.relative_to(
                    BASE_DIR
                )
            ).replace("\\", "/"),

            "document": pdf_path.name,

            "document_id": get_document_name(
                pdf_path
            ),

            "page": page_number,

            "visual_type": visual_type,

            "visual_ids": visual_ids,

            "caption": caption_text,

            "has_embedded_image": bool(
                visual_data["large_images"]
            ),

            "image_count": len(
                visual_data["large_images"]
            ),
        }

        selected_pages.append(
            metadata
        )

        generated_images.append(
            image_path
        )

        print(
            f"[VISUAL] Page {page_number:03d}"
            f" | {visual_type}"
            f" | {image_path.name}"
        )

    doc.close()

    print("\nSummary:")
    print(
        f"  Total pages:      {total_pages}"
    )
    print(
        f"  Visual pages:     {len(selected_pages)}"
    )
    print(
        f"  Images generated: {len(generated_images)}"
    )

    return selected_pages, generated_images


# ============================================================
# Process all PDFs
# ============================================================

def render_visual_pages():

    pdf_files = sorted(
        DATA_DIR.glob("*.pdf")
    )

    if not pdf_files:

        raise FileNotFoundError(
            f"No PDF files found at: {DATA_DIR}"
        )

    all_metadata = []

    for pdf_path in pdf_files:

        metadata, _ = process_pdf(
            pdf_path
        )

        all_metadata.extend(
            metadata
        )

    return all_metadata


# ============================================================
# Save metadata
# ============================================================

def save_visual_metadata(metadata):

    METADATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        VISUAL_METADATA_FILE,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            metadata,
            file,
            ensure_ascii=False,
            indent=2,
        )

    print(
        f"\nMetadata saved to:"
        f"\n{VISUAL_METADATA_FILE}"
    )


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":

    print("=" * 70)
    print("TERYaq - SEMANTIC VISUAL EXTRACTION")
    print("=" * 70)

    # Remove old PNG files
    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    for old_file in OUTPUT_DIR.glob(
        "*.png"
    ):
        old_file.unlink()

    metadata = render_visual_pages()

    save_visual_metadata(
        metadata
    )

    print("\n" + "=" * 70)
    print("FINAL SUMMARY")
    print("=" * 70)

    print(
        f"Visual images: "
        f"{len(metadata)}"
    )

    print(
        f"Images directory:"
        f"\n{OUTPUT_DIR}"
    )

    print(
        f"\nMetadata:"
        f"\n{VISUAL_METADATA_FILE}"
    )

    print("=" * 70)