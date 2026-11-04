# Visual Production

## Current problem

Customer delivery for ecommerce model dressing and professional retouching often fails on demanding tasks, and repeated GPT/Astra revisions do not converge on client approval.

**Why they fail is a hypothesis until real customer cases are reviewed.** No case data or pipeline description is in the repo, and "Astra" is not documented anywhere I could access.

## What SOTA suggests

All of the following were verified at paper level:

- **No verified try-on model reliably preserves small text/logos.**
  - Leffa (best open specialist): "struggles to preserve… small text" due to latent compression.
  - CatVTON: reports VAE detail and color loss.
- **General editors are not clearly worse than specialists.**
  - On the independent OpenVTON-Bench human ratings, Nano Banana (4.60) and Qwen-Editor (4.55) sit near the top commercial try-on product (4.61).
  - All models still "hallucinate fine garment details".
  - Switching models alone is not a reliable fix.
- **Multi-turn editing drifts even in the best editors.**
  - FLUX Kontext's own paper: "excessive multi-turn editing can introduce visual artifacts."
  - OpenAI's docs: GPT Image masks are "guidance" and "may not follow its exact shape."
- **Garment fidelity can be checked per attribute.**
  - DAT checks 7 attributes: silhouette, color, neckline/sleeve, decoration, texture, fine detail, logo.
  - A prompted Gemini judge is almost as accurate as their trained checker (75.9% vs. 76.6%).
  - OpenVTON-Bench's region-based metric matches human rankings far better than SSIM (Kendall τ 0.83 vs. 0.61).
- **Licenses matter.** CatVTON, InfiniteYou, and FLUX-dev weights are non-commercial. Leffa is MIT; its training-data terms are unchecked.

## What practitioner workflows suggest

The recurring pattern (ComfyUI Crop-and-Stitch, Redux+Fill try-on, the PS-AI apparel SOP, retouching plugins):

1. Mark protected zones first.
2. Let the AI generate **only inside a region**.
3. Paste the untouched pixels back deterministically (they never pass through the model).
4. Restore detail and color deterministically (e.g. frequency "detail transfer").
5. Finish in Photoshop.
6. Run a named checklist before delivery.

- **Retouching:** professionals keep work as reversible dodge & burn / frequency-separation layers, so "a bit less" is a slider change, not a regeneration.

**Blocked sources:** Xiaohongshu (login wall) and Zhihu (403). Nothing was used from them. ZCOOL was accessible but its posts show results, not process.

## Recommended Curify direction

Replace "regenerate the whole image and hope" with a **multi-stage controlled pipeline**:

1. **Acceptance contract:** a per-order checklist built from the 7 garment attributes plus identity/background, agreed with the client, with reference assets (garment flat-lay, color swatch, logo file).
2. **Locked-region revision:** each revision edits only a masked region; everything else is copied bit-exact from the last approved version.
3. **Deterministic repair:** color-match to the swatch, logo/text patch paste-back, face paste-back from the source photo.
4. **Automated pre-checks + human region review:** color difference vs. the swatch (ΔE), logo OCR, face similarity, and a pixel diff outside the edited region.
5. **Retouching as layers/parameters,** not flattened regenerations.
6. **Generator choice by A/B on our cases.** Candidates: current GPT/Astra vs. Kontext/Qwen try-on LoRA vs. FASHN vs. Leffa.

## Next validation

Use 10–15 real rejected customer cases (about half try-on, half retouching):

1. Tag each rejection by failure type. This answers "what actually fails" with no generation.
2. Replay the hardest revision requests with the same generator in two arms:
   - **A:** whole-image edit (today)
   - **B:** localized locked-region revision + delivery-oriented QA
3. **Measure:**
   - changes outside the requested region
   - per-attribute checklist pass rate
   - rounds to internal approval (blind review)
   - time per round
4. **Decide:**
   - If B wins, productize the locked loop.
   - If the remaining failures are mostly garment fidelity, run the generator A/B next.

**Needed from you:** the customer cases (internal use), plus a description of the current GPT/Astra pipeline.
