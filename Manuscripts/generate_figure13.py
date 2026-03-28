#!/usr/bin/env python3
"""Generate Figure 13: Unifying Framework Schematic for the Scapula Paper."""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

fig, ax = plt.subplots(1, 1, figsize=(14, 9), dpi=300)
ax.set_xlim(0, 14)
ax.set_ylim(0, 9)
ax.axis('off')
fig.patch.set_facecolor('white')

# ── Colors ──
c_scapula = '#D6EAF8'   # light blue
c_static = '#E8E8E8'     # light gray
c_dynamic = '#E8E8E8'    # light gray
c_rct = '#FDEBD0'        # light amber
c_oa = '#D5F5E3'         # light green
c_post = '#F5B7B1'       # slightly deeper coral for emphasis
c_rtsa = '#D6EAF8'       # light blue

border_color = '#2C3E50'
text_color = '#1A1A1A'
arrow_color = '#555555'

def draw_box(x, y, w, h, color, texts, ax):
    """Draw a rounded box with centered multi-line text."""
    box = FancyBboxPatch((x, y), w, h,
                         boxstyle="round,pad=0.15",
                         facecolor=color, edgecolor=border_color,
                         linewidth=1.2, zorder=2)
    ax.add_patch(box)
    # texts is a list of (string, fontsize, fontweight, style)
    total = len(texts)
    spacing = h / (total + 1)
    for i, (txt, fs, fw, sty) in enumerate(texts):
        ty = y + h - spacing * (i + 1)
        ax.text(x + w/2, ty, txt,
                ha='center', va='center',
                fontsize=fs, fontweight=fw, fontstyle=sty,
                color=text_color, zorder=3,
                fontfamily='sans-serif')

def draw_arrow(x1, y1, x2, y2, label=None, label_side='left'):
    """Draw an arrow with optional label."""
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle='->', color=arrow_color,
                                lw=1.3, connectionstyle='arc3,rad=0'),
                zorder=1)
    if label:
        mx = (x1 + x2) / 2
        my = (y1 + y2) / 2
        # offset label to avoid overlapping arrow
        if label_side == 'left':
            offset_x = -0.15
        else:
            offset_x = 0.15
        ax.text(mx + offset_x, my, label,
                ha='center', va='center',
                fontsize=6.5, color='#333333',
                fontstyle='italic', fontfamily='sans-serif',
                zorder=3,
                bbox=dict(boxstyle='round,pad=0.1', facecolor='white',
                          edgecolor='none', alpha=0.85))

# ═══════════════════════════════════════════════════
# TIER 1: SCAPULA (top center)
# ═══════════════════════════════════════════════════
t1_x, t1_y, t1_w, t1_h = 4.5, 7.0, 5.0, 1.6
draw_box(t1_x, t1_y, t1_w, t1_h, c_scapula, [
    ('SCAPULA', 14, 'bold', 'normal'),
    ('Upstream Structure', 9, 'normal', 'normal'),
    ('No bony articulation to axial skeleton', 7, 'normal', 'normal'),
    ('Position = vector summation of all muscle tensions', 7, 'normal', 'italic'),
], ax)

# ═══════════════════════════════════════════════════
# TIER 2: TWO MECHANISMS (middle row)
# ═══════════════════════════════════════════════════
t2_w, t2_h = 4.8, 2.4
t2_left_x, t2_y = 0.8, 4.0
t2_right_x = 8.4

# Static Morphology
draw_box(t2_left_x, t2_y, t2_w, t2_h, c_static, [
    ('STATIC MORPHOLOGY', 11, 'bold', 'normal'),
    ('Innate bony architecture', 8, 'normal', 'normal'),
    ('• Critical shoulder angle (CSA)', 7, 'normal', 'normal'),
    ('• Posterior acromial height', 7, 'normal', 'normal'),
    ('• Acromial coverage & tilt', 7, 'normal', 'normal'),
    ('Not modifiable', 7, 'normal', 'italic'),
], ax)

# Dynamic Positioning
draw_box(t2_right_x, t2_y, t2_w, t2_h, c_dynamic, [
    ('DYNAMIC POSITIONING', 11, 'bold', 'normal'),
    ('Scapulothoracic orientation during movement', 7.5, 'normal', 'normal'),
    ('• Scapulohumeral rhythm', 7, 'normal', 'normal'),
    ('• Dynamic glenoid version', 7, 'normal', 'normal'),
    ('• Periscapular force couple balance', 7, 'normal', 'normal'),
    ('Potentially modifiable', 7, 'normal', 'italic'),
], ax)

# ═══════════════════════════════════════════════════
# TIER 3: FOUR DOWNSTREAM PATHOLOGIES (bottom row)
# ═══════════════════════════════════════════════════
t3_w, t3_h = 3.0, 2.0
t3_y = 1.2
t3_gap = 0.4
total_width = 4 * t3_w + 3 * t3_gap
t3_start_x = (14 - total_width) / 2

box_positions = []
for i in range(4):
    bx = t3_start_x + i * (t3_w + t3_gap)
    box_positions.append(bx)

# Box 1: Rotator Cuff Tears
draw_box(box_positions[0], t3_y, t3_w, t3_h, c_rct, [
    ('ROTATOR CUFF', 9, 'bold', 'normal'),
    ('TEARS', 9, 'bold', 'normal'),
    ('High CSA → ↑ shear force', 7, 'normal', 'normal'),
    ('Supraspinatus overloaded', 7, 'normal', 'normal'),
], ax)

# Box 2: Osteoarthritis
draw_box(box_positions[1], t3_y, t3_w, t3_h, c_oa, [
    ('OSTEOARTHRITIS', 9, 'bold', 'normal'),
    ('', 4, 'normal', 'normal'),
    ('Low CSA → ↑ compression', 7, 'normal', 'normal'),
    ('Articular cartilage overloaded', 7, 'normal', 'normal'),
], ax)

# Box 3: Posterior Instability → Glenoid Erosion
draw_box(box_positions[2], t3_y, t3_w, t3_h, c_post, [
    ('POSTERIOR INSTABILITY', 8, 'bold', 'normal'),
    ('→ GLENOID EROSION', 8, 'bold', 'normal'),
    ('↓ posterior restraint', 7, 'normal', 'normal'),
    ('C1 → B0 → B1 → B2/B3', 7, 'bold', 'normal'),
], ax)

# Box 4: Suboptimal rTSA Outcomes
draw_box(box_positions[3], t3_y, t3_w, t3_h, c_rtsa, [
    ('SUBOPTIMAL rTSA', 9, 'bold', 'normal'),
    ('OUTCOMES', 9, 'bold', 'normal'),
    ('SHR 1.3:1 (vs. normal 3:1)', 7, 'normal', 'normal'),
    ('↑ scapulothoracic demand', 7, 'normal', 'normal'),
], ax)

# ═══════════════════════════════════════════════════
# ARROWS: Tier 1 → Tier 2
# ═══════════════════════════════════════════════════
# Scapula → Static Morphology
draw_arrow(t1_x + t1_w * 0.3, t1_y,
           t2_left_x + t2_w / 2, t2_y + t2_h)

# Scapula → Dynamic Positioning
draw_arrow(t1_x + t1_w * 0.7, t1_y,
           t2_right_x + t2_w / 2, t2_y + t2_h)

# ═══════════════════════════════════════════════════
# ARROWS: Tier 2 → Tier 3 (with labels)
# ═══════════════════════════════════════════════════
static_cx = t2_left_x + t2_w / 2
dynamic_cx = t2_right_x + t2_w / 2

# Static → Box 1 (RCT)
draw_arrow(static_cx - 0.8, t2_y,
           box_positions[0] + t3_w / 2, t3_y + t3_h,
           label='High CSA', label_side='left')

# Static → Box 2 (OA)
draw_arrow(static_cx, t2_y,
           box_positions[1] + t3_w / 2, t3_y + t3_h,
           label='Low CSA', label_side='left')

# Static → Box 3 (Posterior)
draw_arrow(static_cx + 0.8, t2_y,
           box_positions[2] + t3_w * 0.35, t3_y + t3_h,
           label='Posterior acromial\nmorphology', label_side='left')

# Dynamic → Box 3 (Posterior)
draw_arrow(dynamic_cx - 0.6, t2_y,
           box_positions[2] + t3_w * 0.65, t3_y + t3_h,
           label='Altered scapulothoracic\norientation', label_side='right')

# Dynamic → Box 4 (rTSA)
draw_arrow(dynamic_cx + 0.6, t2_y,
           box_positions[3] + t3_w / 2, t3_y + t3_h,
           label='Altered scapulohumeral\nrhythm', label_side='right')

# ═══════════════════════════════════════════════════
# BOTTOM ANNOTATION
# ═══════════════════════════════════════════════════
ax.plot([0.8, 13.2], [0.7, 0.7], color=border_color, linewidth=0.8, zorder=1)
ax.text(7.0, 0.35,
        'The specific downstream pathology depends on which structure '
        'bears the consequence of the upstream alteration.',
        ha='center', va='center',
        fontsize=8, fontstyle='italic', color=text_color,
        fontfamily='sans-serif')

# ═══════════════════════════════════════════════════
# SAVE
# ═══════════════════════════════════════════════════
out_path = '/Users/bradroepke/Documents/Biomechanics Research/Manuscripts/Scapula_Paper_Figures/Framework_Schematic.png'
plt.tight_layout(pad=0.5)
plt.savefig(out_path, dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')
print(f'Saved to {out_path}')
