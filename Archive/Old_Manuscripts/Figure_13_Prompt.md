# Figure 13 — Framework Schematic Generation Prompt

Paste the following into Gemini, ChatGPT/DALL-E, or another AI image generator:

---

Create a clean, professional medical diagram on a white background. No 3D effects, no gradients, no decorative elements. Use only black text, thin black lines/arrows, and muted fill colors (light blue, light gray, light amber/gold, light green, light red/coral). The diagram should look like it belongs in a peer-reviewed orthopedic surgery journal. All text must be legible, spelled correctly, and in a clean sans-serif font.

## Layout

The diagram is a top-to-bottom flowchart with three tiers connected by arrows.

### TIER 1 — TOP CENTER: The Upstream Structure

A single rounded rectangle centered at the top of the image, filled with light blue. Inside it:
- Large bold text: "SCAPULA"
- Smaller text below: "Upstream Structure"
- Below that, even smaller: "No bony articulation to axial skeleton"
- Below that: "Position = vector summation of all muscle tensions"

From the bottom of this box, two diverging arrows (angled downward-left and downward-right) lead to Tier 2.

### TIER 2 — MIDDLE ROW: Two Mechanisms

Two rounded rectangles side by side, evenly spaced below the scapula box.

**Left box** (filled light gray):
- Bold text: "STATIC MORPHOLOGY"
- Below in smaller text: "Innate bony architecture"
- Below that, three bullet items:
  - "Critical shoulder angle (CSA)"
  - "Posterior acromial height"
  - "Acromial coverage & tilt"
- At the very bottom of the box in italic: "Not modifiable"

**Right box** (filled light gray):
- Bold text: "DYNAMIC POSITIONING"
- Below in smaller text: "Scapulothoracic orientation during movement"
- Below that, three bullet items:
  - "Scapulohumeral rhythm"
  - "Dynamic glenoid version"
  - "Periscapular force couple balance"
- At the very bottom of the box in italic: "Potentially modifiable"

### TIER 3 — BOTTOM ROW: Four Downstream Pathologies

Four rounded rectangles arranged in a horizontal row at the bottom.

From the LEFT "Static Morphology" box, three arrows descend to the first three pathology boxes. From the RIGHT "Dynamic Positioning" box, two arrows descend to the third and fourth pathology boxes. (The third box receives arrows from both mechanisms — this is important.)

**Box 1** (filled light amber/gold, leftmost):
- Bold text: "ROTATOR CUFF TEARS"
- Below: "High CSA → ↑ shear force"
- Below: "Supraspinatus overloaded"

**Box 2** (filled light green):
- Bold text: "OSTEOARTHRITIS"
- Below: "Low CSA → ↑ compression"
- Below: "Articular cartilage overloaded"

**Box 3** (filled light red/coral):
- Bold text: "POSTERIOR INSTABILITY → GLENOID EROSION"
- Below: "High posterior acromion → ↓ restraint"
- Below: "Dynamic version → cumulative posterior loading"
- This box should have a small internal arrow or progression notation showing: "C1 → B0 → B1 → B2/B3"

**Box 4** (filled light blue, rightmost):
- Bold text: "SUBOPTIMAL rTSA OUTCOMES"
- Below: "SHR 1.3:1 (vs. normal 3:1)"
- Below: "Increased scapulothoracic demand"

### Arrow labels

On the arrow from Static Morphology to Box 1, small label: "High CSA"
On the arrow from Static Morphology to Box 2, small label: "Low CSA"
On the arrow from Static Morphology to Box 3, small label: "Posterior acromial morphology"
On the arrow from Dynamic Positioning to Box 3, small label: "Altered scapulothoracic orientation"
On the arrow from Dynamic Positioning to Box 4, small label: "Altered scapulohumeral rhythm"

### Bottom annotation

Below all four boxes, a single thin horizontal line spanning the width of the diagram, with centered text below it in italic:

"The specific downstream pathology depends on which structure bears the consequence of the upstream alteration."

## Style specifications

- Dimensions: landscape orientation, approximately 10 inches wide by 7 inches tall (or 2400 x 1680 pixels)
- Resolution: 300 DPI minimum
- Font: clean sans-serif (Helvetica, Arial, or similar)
- All boxes have thin (1-2pt) black borders with rounded corners
- Arrows are thin (1.5pt), black, with small arrowheads
- No shadows, no 3D effects, no textures
- White background only
- The overall aesthetic should match figures published in JBJS, Arthroscopy, or JSES

---

## Notes for iteration

If the first output has issues, common corrections to request:
- "Make all text larger and more legible"
- "Ensure Box 3 (Posterior Instability) receives arrows from BOTH the Static Morphology and Dynamic Positioning boxes"
- "Straighten the alignment — all Tier 3 boxes should have their tops aligned horizontally"
- "Remove any decorative elements, keep it strictly diagrammatic"
- "The C1 → B0 → B1 → B2/B3 progression should read left to right inside Box 3"
