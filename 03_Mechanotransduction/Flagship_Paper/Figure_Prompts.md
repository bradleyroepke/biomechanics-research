# Figure Generation Prompts

*For use with Gemini or similar AI image generation tools. Each prompt is designed to produce a publication-quality medical illustration suitable for a peer-reviewed orthopedic journal.*

---

## Figure 1: Force Vector Diagram

**Prompt:**

Create a high-resolution medical illustration for a peer-reviewed orthopedic journal showing two anterior-posterior views of the glenohumeral joint side by side, comparing the biomechanical effect of different scapular morphologies on deltoid force vectors.

LEFT PANEL: labeled "Low Critical Shoulder Angle (28 degrees)." Show a scapula with a short lateral acromion and a less-inclined glenoid. The glenohumeral joint should show a centered humeral head on the glenoid. Draw the middle deltoid muscle originating from the lateral acromion and inserting on the deltoid tuberosity of the humerus. Show the deltoid force vector as a thick yellow arrow directed mostly INTO the glenoid face (compression-dominant). Decompose this force into two component arrows at the glenoid surface: a large blue arrow perpendicular to the glenoid face labeled "Compression" and a small red arrow parallel to the glenoid face labeled "Shear." The resultant joint reaction force vector (thick green arrow labeled "F resultant") should be directed nearly perpendicular to the glenoid, indicating a compression-dominant environment. Below this panel, write "Compression-Dominant Environment" and "Predisposes to: Osteoarthritis."

RIGHT PANEL: labeled "High Critical Shoulder Angle (38 degrees)." Show a scapula with a long lateral acromion extending further over the humeral head and a more superiorly inclined glenoid. Same glenohumeral joint anatomy. Draw the middle deltoid originating from the longer lateral acromion. Show the deltoid force vector as a thick yellow arrow directed more superiorly and less into the glenoid (more shear, less compression). Decompose this force into two component arrows at the glenoid surface: a smaller blue arrow labeled "Compression" and a larger red arrow labeled "Shear." The resultant joint reaction force vector (thick green arrow labeled "F resultant") should be angled more superiorly relative to the glenoid face, indicating increased shear. Below this panel, write "Shear-Dominant Environment" and "Predisposes to: Rotator Cuff Disease."

Both panels should show the critical shoulder angle marked with a dotted line and the angle value labeled. The supraspinatus should be visible in both panels, with the right panel showing the supraspinatus working harder (perhaps drawn slightly thicker or with a notation "increased SSP demand") to resist the shear component.

Style: Clean, professional medical illustration. White background. Anatomically accurate but simplified for clarity. No photorealistic rendering. Use a consistent color scheme: yellow for muscle force vectors, blue for compression components, red for shear components, green for resultant forces. Line weight should be heavy enough to reproduce clearly at journal print resolution. All labels in clean sans-serif font (Helvetica or Arial). The illustration should be understandable without reading any accompanying text.

Dimensions: landscape orientation, approximately 7 inches wide by 4.5 inches tall, at 300 DPI minimum.

---

## Figure 2: Competing Pathway Diagram

**Prompt:**

Create a high-resolution conceptual diagram for a peer-reviewed orthopedic journal illustrating how a single morphological parameter (the critical shoulder angle) produces two diverging pathological pathways that are mutually exclusive due to their geometric consequences.

The diagram should be structured as follows:

TOP CENTER: A horizontal bar or gradient representing the critical shoulder angle spectrum from left to right: 20 degrees on the far left, 28 degrees at the left zone boundary, 33 degrees at center (labeled "Normal"), 35 degrees at the right zone boundary, and 45 degrees on the far right. Color this gradient from deep blue on the left through neutral gray in the center to deep red on the right.

LEFT PATHWAY (descending from the low-CSA zone, blue tones): A series of connected boxes or steps descending downward, each showing one stage in the osteoarthritis pathway. The sequence should be:
1. "Compression-Dominant Force Environment"
2. "Increased articular cartilage loading"
3. "Cartilage thinning and matrix changes"
4. "Subchondral sclerosis (Wolff's Law)"
5. "Joint medialization"
6. "GLENOHUMERAL OSTEOARTHRITIS" (in a prominent box at the bottom)

RIGHT PATHWAY (descending from the high-CSA zone, red tones): A parallel series of connected boxes or steps descending downward, each showing one stage in the rotator cuff disease pathway. The sequence should be:
1. "Shear-Dominant Force Environment"
2. "Supraspinatus overload"
3. "Articular-side matrix remodeling"
4. "Partial tearing at SS/IS junction"
5. "Force couple disruption (61% force drop)"
6. "Superior migration, fatty infiltration"
7. "ROTATOR CUFF DISEASE" (in a prominent box at the bottom)

CENTER ZONE (between the two pathways, at the 30-35 degree range): A shaded zone labeled "Boundary Zone" with a note: "Both pathways accessible. Other factors (tissue susceptibility, activity, scapulothoracic function) determine which threshold is crossed first."

CRITICAL FEATURE (the novel contribution): Draw two curved arrows crossing between the pathways:
- From the OA pathway (specifically from "Joint medialization"), a dashed arrow curving to the right side with the label: "Medialization reduces deltoid moment arm, decreasing shear on cuff" with an X or prohibition symbol on the cuff tear pathway, indicating protection.
- From the Cuff Tear pathway (specifically from "Superior migration"), a dashed arrow curving to the left side with the label: "Superior migration unloads articular surface, reducing compression on cartilage" with an X or prohibition symbol on the OA pathway, indicating protection.

These crossing arrows visually demonstrate why the two conditions are mutually exclusive: each pathway's geometric consequences protect against the other.

Style: Clean, modern infographic style suitable for medical journal publication. White background. Use blue tones for the OA pathway, red tones for the cuff tear pathway, and neutral gray for the boundary zone. Boxes should have subtle rounded corners with light drop shadows. Arrows connecting the steps should be clean and directional. The crossing protection arrows should be visually distinct (dashed, different color such as dark gray or gold) to stand out from the pathway arrows. All text should be in a clean sans-serif font. The diagram should tell the complete story of the competing pathway model without any accompanying text.

Dimensions: portrait orientation, approximately 6 inches wide by 8 inches tall, at 300 DPI minimum.

---

## Figure 3: Morphological Parameter Space

**Prompt:**

Create a high-resolution two-dimensional scatter plot or zone diagram for a peer-reviewed orthopedic journal showing how two independent scapular morphological parameters predict different pathological endpoints.

AXES:
- Horizontal axis (X): "Critical Shoulder Angle (degrees)" ranging from 20 on the left to 45 on the right, with tick marks at 25, 28, 30, 33, 35, 38, 40, 45. Label key zones along this axis: below 28 labeled "OA zone," 30-35 labeled "Normal," above 35 labeled "RCT zone."
- Vertical axis (Y): "Posterior Acromial Height (mm)" ranging from 10 at the bottom to 35 at the top, with tick marks at 15, 19, 23, 27, 30, 35. Draw a horizontal dashed line at 23 mm labeled "Instability threshold (OR = 39)."

ZONES (colored regions on the plot):
- BOTTOM LEFT quadrant (low CSA, low PAH): colored blue, labeled "OSTEOARTHRITIS." This region represents shoulders with short acromia and normal posterior acromial coverage, predisposed to compression-dominant articular disease.
- BOTTOM RIGHT quadrant (high CSA, low PAH): colored red, labeled "ROTATOR CUFF DISEASE." This region represents shoulders with long lateral acromia but normal posterior coverage, predisposed to shear-dominant tendon disease.
- TOP region (high PAH, any CSA): colored green or teal, labeled "POSTERIOR INSTABILITY." This region represents shoulders with high, flat posterior acromia regardless of CSA, predisposed to posterior decentering.
- CENTER region (CSA 30-35, PAH 15-23): colored light gray, labeled "NORMAL / LOW RISK."

The boundaries between zones should be gradients or soft transitions, not sharp lines, to indicate that the transitions are probabilistic rather than deterministic.

Include a note in the bottom margin: "Individual disease trajectory determined by composite effect of multiple morphological parameters, tissue susceptibility, activity level, and systemic health. This diagram illustrates two of the most studied parameters; other variables (glenoid version, tuberosity geometry, scapulothoracic posture) contribute independently."

Optionally, scatter a few representative data points in each zone to suggest where clinical populations might fall, but keep this minimal so the zones remain the visual focus.

Style: Clean scientific figure style. White background with subtle grid lines. Zone colors should be soft and semi-transparent so grid lines and labels remain visible through them. Axis labels in clean sans-serif font. Zone labels in bold. The overall impression should be of a clinical decision-support tool: a surgeon should be able to look at a patient's CSA and PAH and immediately see which zone they fall in. This should look like a figure from a high-quality orthopedic journal, not a textbook illustration.

Dimensions: square orientation, approximately 6 inches by 6 inches, at 300 DPI minimum.

---

## General Notes for All Figures

- All figures must be suitable for reproduction in both color (online) and grayscale (print). Ensure zone distinctions are visible in grayscale through pattern or shade differences, not color alone.
- All text within figures must be legible at the final reproduction size (minimum 8pt font for labels, 10pt for major headings).
- Include figure legends below each figure:
  - Figure 1: "The critical shoulder angle determines the direction of the deltoid force vector relative to the glenoid. A low angle creates a compression-dominant environment associated with osteoarthritis. A high angle creates a shear-dominant environment associated with rotator cuff disease."
  - Figure 2: "Competing pathological pathways from a shared morphological parameter. The critical shoulder angle determines which tissue's mechanical threshold is reached first. Each pathway's geometric consequences alter the joint in ways that reduce the likelihood of the other pathway, explaining the observed mutual exclusivity of rotator cuff tears and glenohumeral osteoarthritis."
  - Figure 3: "Two-dimensional morphological parameter space defined by the critical shoulder angle and posterior acromial height. Different regions predict different pathological endpoints. These two parameters illustrate the broader principle that skeletal morphology determines the mechanical environment, which in turn determines tissue adaptation trajectories."
