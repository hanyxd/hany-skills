---
name: image-text-extraction
description: "Use when an image needs text extraction via OCR."
---

# Image Text Extraction (OCR fallback)

When the user attaches an image and asks what it contains, and `vision_analyze` is not returning content, extract the text locally with tesseract. This works for dark-mode screenshots, photos of screens, and UI dashboards.

## Procedure

1. **Validate the file once.** `file <path>` (confirm real JPEG/PNG) and open it in Pillow — if Pillow opens it with sane dimensions, the file is fine; any failure is downstream of the file.

2. **Try vision_analyze exactly ONCE.** If it returns generic boilerplate ("I don't see an image attached", "describe it or provide context") it is a backend failure, not a bad file. Do NOT retry it on resized/converted variants — that burns calls and never succeeds. Go straight to OCR.

3. **Locate the content region before OCR.** Run a pure-Pillow row-profile scan (no numpy — it is commonly absent; `px.load()` loops at step-8 sampling are fast enough): for each sampled row, percent of pixels above a brightness threshold plus the x-extent of those pixels. Text/content shows as contiguous bands bounded by near-empty rows. The bbox tells you what to crop.

4. **Preprocess the crop** (mandatory for dark-background / dark-mode images):
   - `convert('L')` grayscale
   - resize 2–3× with `Image.LANCZOS`
   - `ImageOps.autocontrast`
   - optional `ImageFilter.SHARPEN`
   - tesseract on the RAW dark image returns nothing — preprocessing is not optional decoration.

5. **OCR region-by-region, not whole-image.** Split the content into bands (header / table rows / footer) and OCR each crop separately. Whole-image OCR on a large photo (4032×3024) returns nothing even when each region reads cleanly. Use `--psm 3` for general text, `--psm 6` for row-oriented tables.

6. **Report honestly what is readable.** When OCR produces garbage on a graphics-heavy region (charts, bars, gradient graphs), stop re-tweaking thresholds — the bars defeat tesseract. State what was extracted and what was not.

## Pitfalls

- A boilerplate vision_analyze response means the vision backend is down, not that the image is invalid. Re-uploading resized/PNG versions of the same file reproduces the same boilerplate; switch to OCR after the first occurrence.
- Dark background + light text is the failure mode where tesseract returns empty output on the original — grayscale + crop + 2–3× LANCZOS upscale + autocontrast is the minimal working recipe.
- OCR digit misreads on plain-text tables are common (e.g. `66.2M` → `66.2H`): digits and order of magnitude are reliable, unit letters are not; cross-check row labels across multiple crops when values look off.
- Do not reach for numpy for pixel profiling; Pillow-only loops are faster to write and run on boxes without numpy.

## Scripts

- `scripts/ocr_prep.py` — profile an image to find the content-region bbox and/or write a preprocessed (grayscale, upscaled, autocontrasted) crop ready for tesseract. Pillow only, no numpy.
