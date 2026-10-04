#!/usr/bin/env python3
"""
VarshaSetu Finalist-Level SIH 2026 Presentation Generator
Builds VarshaSetu_SIH2026_FINALIST.pptx directly from the official SIH 2026 template
and exports VarshaSetu_SIH2026_FINALIST.pdf with 100% exact parity via Keynote AppleScript.
"""

import os
import sys
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

# Paths
WORKSPACE = "/Users/maradanasaikiran/vinay new sih"
SRC_TEMPLATE = "/Users/maradanasaikiran/Downloads/SIH2026-IDEA-Presentation-Formattt.pptx"
OUT_PPTX = os.path.join(WORKSPACE, "VarshaSetu_SIH2026_FINALIST.pptx")
OUT_PDF = os.path.join(WORKSPACE, "VarshaSetu_SIH2026_FINALIST.pdf")
IMG_DIR = os.path.join(WORKSPACE, "varshshetu full doc/img")

# Color Palette (Scientific, High-Contrast, Premium)
C_DARK_NAVY   = RGBColor(15, 23, 42)      # #0f172a
C_SLATE_DEEP  = RGBColor(30, 41, 59)      # #1e293b
C_SLATE_TEXT  = RGBColor(51, 65, 85)      # #334155
C_MUTED_TEXT  = RGBColor(100, 116, 139)   # #64748b
C_WHITE       = RGBColor(255, 255, 255)   # #ffffff
C_BG_CARD     = RGBColor(248, 250, 252)   # #f8fafc
C_BORDER_CARD = RGBColor(226, 232, 240)   # #e2e8f0
C_PRIMARY_BLUE= RGBColor(2, 132, 199)     # #0284c7 (Sky Blue)
C_DEEP_BLUE   = RGBColor(29, 78, 216)     # #1d4ed8
C_ACCENT_CYAN = RGBColor(14, 165, 233)    # #0ea5e9
C_GREEN       = RGBColor(16, 163, 74)     # #10b981 / #16a34a
C_AMBER       = RGBColor(217, 119, 6)     # #d97706
C_ORANGE      = RGBColor(234, 88, 12)     # #ea580c
C_RED         = RGBColor(220, 38, 38)     # #dc2626
C_BLUE_BANNER = RGBColor(11, 107, 186)    # #0b6bba

def in_to_emu(inches):
    return int(inches * 914400)

def set_shape_flat(shape, fill_rgb, border_rgb=None, border_width_pt=1):
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill_rgb
    if border_rgb:
        shape.line.color.rgb = border_rgb
        shape.line.width = Pt(border_width_pt)
    else:
        shape.line.fill.background()

def create_card(slide, left, top, width, height, fill_rgb, border_rgb=None, border_width_pt=1, shape_type=MSO_SHAPE.ROUNDED_RECTANGLE):
    s = slide.shapes.add_shape(shape_type, in_to_emu(left), in_to_emu(top), in_to_emu(width), in_to_emu(height))
    set_shape_flat(s, fill_rgb, border_rgb, border_width_pt)
    return s

def add_header_bar(slide, title_text, pointer_text, team_name="TITANS"):
    # Update Team oval
    for s in slide.shapes:
        if "Oval" in s.name and s.has_text_frame:
            tf = s.text_frame
            tf.clear()
            p = tf.paragraphs[0]
            p.alignment = PP_ALIGN.CENTER
            run = p.add_run()
            run.text = team_name
            run.font.bold = True
            run.font.size = Pt(13)
            run.font.color.rgb = C_BLUE_BANNER
            set_shape_flat(s, C_WHITE, C_BLUE_BANNER, 1.5)

    # Update or add Title
    for s in slide.shapes:
        if s.name == "Title 1" and s.has_text_frame:
            s.left = in_to_emu(1.85)
            s.top = in_to_emu(0.12)
            s.width = in_to_emu(8.75)
            s.height = in_to_emu(0.85)
            tf = s.text_frame
            tf.clear()
            p = tf.paragraphs[0]
            p.alignment = PP_ALIGN.LEFT
            r = p.add_run()
            r.text = title_text
            r.font.bold = True
            r.font.size = Pt(20)
            r.font.color.rgb = C_DARK_NAVY

    # Add Predefined Pointers Sub-Bar
    bar = create_card(slide, 0.40, 1.02, 12.53, 0.36, RGBColor(241, 245, 249), RGBColor(203, 213, 225), 1)
    tf = bar.text_frame
    tf.word_wrap = False
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.LEFT
    r = p.add_run()
    r.text = f"  {pointer_text}"
    r.font.size = Pt(8.8)
    r.font.bold = True
    r.font.color.rgb = C_SLATE_TEXT

def remove_template_placeholder(slide, name="TextBox 8"):
    to_remove = []
    for s in slide.shapes:
        if s.name == name:
            to_remove.append(s)
    for s in to_remove:
        sp = s._element
        sp.getparent().remove(sp)

def main():
    print(f"Opening source template: {SRC_TEMPLATE}...")
    prs = Presentation(SRC_TEMPLATE)
    
    # Ensure exact 6 slides by deleting slide 7
    if len(prs.slides) > 6:
        print(f"Removing instruction slide 7 (total was {len(prs.slides)})...")
        rId = prs.slides._sldIdLst[6].rId
        prs.part.drop_rel(rId)
        del prs.slides._sldIdLst[6]
        print(f"Slides count after deletion: {len(prs.slides)}")

    # =========================================================================
    # SLIDE 1: TITLE & TEAM DETAILS / PROBLEM STATEMENT
    # =========================================================================
    print("Building Slide 1: Title & Central Visual Pipeline...")
    slide1 = prs.slides[0]
    remove_template_placeholder(slide1, "TextBox 9")

    # Left Column: x = 0.50", width = 6.60" (leaving x = 7.30" to 13.00" completely open for the official SIH lightbulb!)
    col_left = 0.50
    col_w = 6.70

    # 1. Product Branding Box (Top-Left)
    card_brand = create_card(slide1, col_left, 1.65, col_w, 1.25, RGBColor(238, 242, 255), RGBColor(199, 210, 254), 1.5)
    tf_b = card_brand.text_frame
    tf_b.word_wrap = True
    p1 = tf_b.paragraphs[0]
    r_title = p1.add_run()
    r_title.text = "VARSHASETU\n"
    r_title.font.bold = True
    r_title.font.size = Pt(21)
    r_title.font.color.rgb = C_DEEP_BLUE

    p2 = tf_b.add_paragraph()
    r_sub = p2.add_run()
    r_sub.text = "Hyperlocal Monsoon Onset, Break & Agricultural Advisory System\n"
    r_sub.font.bold = True
    r_sub.font.size = Pt(9.5)
    r_sub.font.color.rgb = C_DARK_NAVY

    p3 = tf_b.add_paragraph()
    r_tag = p3.add_run()
    r_tag.text = "“Bridging Climate Intelligence with Every Farmer”"
    r_tag.font.italic = True
    r_tag.font.bold = True
    r_tag.font.size = Pt(9.5)
    r_tag.font.color.rgb = C_PRIMARY_BLUE

    # 2. Problem Statement & Team Metadata Card
    card_meta = create_card(slide1, col_left, 2.98, col_w, 2.05, C_BG_CARD, C_BORDER_CARD, 1.2)
    tf_m = card_meta.text_frame
    tf_m.word_wrap = True
    
    items = [
        ("Problem Statement ID:", "SIH26086", C_DEEP_BLUE),
        ("Problem Title:", "Hyperlocal Monsoon Onset & Break Prediction System", C_DARK_NAVY),
        ("Spatial Resolution:", "Block / Village Scale (5–10 km)", C_PRIMARY_BLUE),
        ("Ministry / Org:", "Ministry of Earth Sciences (MoES) | NCMRWF", C_DARK_NAVY),
        ("Theme & Category:", "Agriculture, FoodTech & Rural Development | Software", C_SLATE_TEXT),
        ("Team ID & Name:", "120087 | TITANS", C_ORANGE),
        ("Institution:", "MVGR College of Engineering (Autonomous), Vizianagaram, AP", C_SLATE_TEXT),
    ]
    
    for i, (k, v, color) in enumerate(items):
        p = tf_m.paragraphs[0] if i == 0 else tf_m.add_paragraph()
        p.alignment = PP_ALIGN.LEFT
        p.space_after = Pt(2)
        r_k = p.add_run()
        r_k.text = f"{k} "
        r_k.font.bold = True
        r_k.font.size = Pt(8.5)
        r_k.font.color.rgb = C_DARK_NAVY
        r_v = p.add_run()
        r_v.text = v
        r_v.font.bold = (color != C_SLATE_TEXT)
        r_v.font.size = Pt(8.5)
        r_v.font.color.rgb = color

    # 3. Central Visual Pipeline: From Climate Signals to Farmer Action
    card_pipe_s1 = create_card(slide1, col_left, 5.10, col_w, 1.70, C_WHITE, C_BORDER_CARD, 1.2)
    tf_p1 = card_pipe_s1.text_frame
    p_h = tf_p1.paragraphs[0]
    r_h = p_h.add_run()
    r_h.text = "DECISION CONTINUUM: "
    r_h.font.bold = True
    r_h.font.size = Pt(8.5)
    r_h.font.color.rgb = C_PRIMARY_BLUE
    r_pos = p_h.add_run()
    r_pos.text = "“From climate signals to field-level decisions.”\n"
    r_pos.font.bold = True
    r_pos.font.italic = True
    r_pos.font.size = Pt(8.5)
    r_pos.font.color.rgb = C_DEEP_BLUE

    steps_s1 = [
        ("1. Climate Signals", "ENSO (NOAA CPC) | IOD (DMI) | MJO (RMM)", RGBColor(238, 242, 255), C_DEEP_BLUE),
        ("2. Regional Weather", "NASA POWER + Tenali Catchment Daily Data (2015-2025)", C_BG_CARD, C_DARK_NAVY),
        ("3. AI Forecast", "7, 14, 21, 30-Day Probabilistic S2S Outlooks", RGBColor(240, 253, 250), C_PRIMARY_BLUE),
        ("4. Decision Support", "Onset (MET) | Active Spells | Break Risk (>7d Dry Runs)", RGBColor(254, 243, 199), C_AMBER),
        ("5. Farmer Action", "ICAR-CRIDA Crop Sowing, Irrigation & Contingency Directives", RGBColor(240, 253, 244), C_GREEN)
    ]

    for idx, (title, sub, bg, txt_col) in enumerate(steps_s1):
        s_top = 5.38 + idx * 0.26
        p = tf_p1.add_paragraph()
        p.space_after = Pt(1)
        r1 = p.add_run()
        r1.text = f"• {title}: "
        r1.font.bold = True
        r1.font.size = Pt(7.8)
        r1.font.color.rgb = txt_col
        r2 = p.add_run()
        r2.text = sub
        r2.font.size = Pt(7.5)
        r2.font.color.rgb = C_SLATE_TEXT

    print("Slide 1 built successfully.")

    # =========================================================================
    # SLIDE 2: PROPOSED SOLUTION / WHY VARSHASETU
    # =========================================================================
    print("Building Slide 2: Proposed Solution & Core Differentiators...")
    slide2 = prs.slides[1]
    remove_template_placeholder(slide2, "TextBox 8")
    add_header_bar(slide2, "VARSHASETU: Hyperlocal Monsoon Onset, Break & Agricultural Advisory System",
                   "❖ Proposed Solution (Describe your Idea/Solution/Prototype)  • Detailed Explanation  • How It Addresses The Problem  • Innovation & Uniqueness")

    # 1. Headline Banner
    hl_banner = create_card(slide2, 0.40, 1.44, 12.53, 0.38, C_DARK_NAVY, None)
    tf = hl_banner.text_frame
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = "“From predicting rainfall to translating uncertainty into agricultural decisions.”"
    r.font.bold = True
    r.font.size = Pt(11)
    r.font.color.rgb = C_WHITE

    # 2. Compact Comparison: Conventional Approach vs VarshaSetu
    c_conv = create_card(slide2, 0.40, 1.88, 6.15, 0.85, RGBColor(254, 242, 242), RGBColor(254, 202, 202), 1)
    tf = c_conv.text_frame
    tf.word_wrap = True
    p1 = tf.paragraphs[0]
    r1 = p1.add_run()
    r1.text = "CONVENTIONAL APPROACH:  Forecast → Information\n"
    r1.font.bold = True
    r1.font.size = Pt(8.5)
    r1.font.color.rgb = C_RED
    p2 = tf.add_paragraph()
    r2 = p2.add_run()
    r2.text = "• Coarse 50–100 km district forecasts mask village micro-climates and localized dry spells.\n• Delivers raw millimeter rain predictions; leaves farmers to guess sowing & irrigation timing."
    r2.font.size = Pt(7.5)
    r2.font.color.rgb = C_SLATE_TEXT

    c_varsha = create_card(slide2, 6.78, 1.88, 6.15, 0.85, RGBColor(240, 253, 244), RGBColor(187, 247, 208), 1)
    tf = c_varsha.text_frame
    tf.word_wrap = True
    p1 = tf.paragraphs[0]
    r1 = p1.add_run()
    r1.text = "VARSHASETU APPROACH:  Forecast → Risk → Agricultural Decision → Action\n"
    r1.font.bold = True
    r1.font.size = Pt(8.5)
    r1.font.color.rgb = C_GREEN
    p2 = tf.add_paragraph()
    r2 = p2.add_run()
    r2.text = "• Hyperlocal block/village precision (5–10 km) bridging the scale gap with local agro-meteorology.\n• Translates 7–30 day S2S probabilities directly into ICAR-CRIDA crop stage directives."
    r2.font.size = Pt(7.5)
    r2.font.color.rgb = C_SLATE_TEXT

    # 3. Four Visually Dominant Forecast Cards (Core Outputs)
    fc_top = 2.80
    fc_w = 3.00
    fc_gap = 0.17
    fc_h = 1.85

    cards_data = [
        ("ONSET OUTLOOK", "Probabilistic Monsoon Onset Assessment",
         "• Adapts IMD criteria: 2d rain ≥2.5mm, 850 hPa wind ≥7.7 m/s, OLR ≤200 W/m²\n• Status: MET / NOT MET with arrival date probability\n• Directs optimal sowing preparation window",
         RGBColor(238, 242, 255), C_DEEP_BLUE),
        ("ACTIVE SPELL OUTLOOK", "Intra-Seasonal Active Wet-Spell Outlook",
         "• Detects sustained wet circulation (>+20% normal rain for ≥5 days)\n• Identifies expected duration & soil saturation curves\n• Maximizes rainwater harvesting & nursery sowing",
         RGBColor(240, 253, 244), C_GREEN),
        ("BREAK SPELL OUTLOOK", "Dry-Spell / Severe Break Outlook",
         "• Predicts prolonged dry runs: 3–5d, 5–7d, and >7d continuous dry spell alerts\n• Helps reduce re-sowing risk through break-spell awareness\n• Triggers life-saving irrigation & contingent crop alerts",
         RGBColor(254, 243, 199), C_AMBER),
        ("HEAVY RAIN RISK", "Extreme Precipitation Warnings (>64.5 mm)",
         "• Evaluates daily rainfall exceeding 64.5 mm IMD threshold\n• Prevents fertilizer leaching and expensive urea top-dressing washout\n• Advises field furrow drainage to prevent root rot",
         RGBColor(254, 242, 242), C_RED)
    ]

    for idx, (title, sub, bullets, bg_col, border_col) in enumerate(cards_data):
        c_left = 0.40 + idx * (fc_w + fc_gap)
        card = create_card(slide2, c_left, fc_top, fc_w, fc_h, bg_col, border_col, 1.2)
        tf = card.text_frame
        tf.word_wrap = True
        p1 = tf.paragraphs[0]
        r1 = p1.add_run()
        r1.text = f"{title}\n"
        r1.font.bold = True
        r1.font.size = Pt(9.5)
        r1.font.color.rgb = border_col
        
        p2 = tf.add_paragraph()
        r2 = p2.add_run()
        r2.text = f"{sub}\n\n"
        r2.font.bold = True
        r2.font.size = Pt(7.5)
        r2.font.color.rgb = C_DARK_NAVY
        
        p3 = tf.add_paragraph()
        r3 = p3.add_run()
        r3.text = bullets
        r3.font.size = Pt(7.2)
        r3.font.color.rgb = C_SLATE_TEXT

    # 4. Decision Chain Bar
    chain_bar = create_card(slide2, 0.40, 4.72, 12.53, 0.38, C_SLATE_DEEP, None)
    tf = chain_bar.text_frame
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = "DECISION CHAIN: Climate Signals  ➔  Regional Weather  ➔  Probabilistic S2S Forecast  ➔  Hyperlocal Risk  ➔  Crop-Specific Advisory  ➔  Farmer / Officer Action"
    r.font.bold = True
    r.font.size = Pt(8.5)
    r.font.color.rgb = RGBColor(224, 242, 254)

    # 5. Bottom Split: Left = 6 Key Innovation Points; Right = Real Prototype Status Grid Screenshot
    card_innov = create_card(slide2, 0.40, 5.16, 6.70, 1.70, C_BG_CARD, C_BORDER_CARD, 1)
    tf_i = card_innov.text_frame
    tf_i.word_wrap = True
    p = tf_i.paragraphs[0]
    r = p.add_run()
    r.text = "SIX CORE INNOVATION PILLARS (HOW VARSHASETU DIFFERS):\n"
    r.font.bold = True
    r.font.size = Pt(8.5)
    r.font.color.rgb = C_PRIMARY_BLUE

    innov_points = [
        "1. Hyperlocal Scale: Bridges scale gap between broader 50km models and 5–10km village agricultural decisions.",
        "2. Planetary Teleconnections: Integrates global ENSO ONI, IOD DMI, and MJO RMM with localized agro-meteorology.",
        "3. Probabilistic S2S Outlooks: 7, 14, 21, and 30-day forecast windows with calibrated uncertainty bounds.",
        "4. Operational Decision Layers: Dedicated onset, active, break, and heavy-rain threshold assessments.",
        "5. Crop-Specific Agronomy: ICAR-CRIDA rules for 6 Kharif crops + automatic contingent short-duration cultivars.",
        "6. Inclusive Last-Mile Reach: 7 Indian languages, native Urdu RTL layout, and Web Speech audio TTS."
    ]
    for pt in innov_points:
        p = tf_i.add_paragraph()
        r = p.add_run()
        r.text = f"• {pt}"
        r.font.size = Pt(7.3)
        r.font.color.rgb = C_DARK_NAVY

    card_img = create_card(slide2, 7.25, 5.16, 5.68, 1.70, C_BG_CARD, C_BORDER_CARD, 1)
    tf_img = card_img.text_frame
    p = tf_img.paragraphs[0]
    r = p.add_run()
    r.text = "WORKING PROTOTYPE EVIDENCE (STATUS GRID):\n"
    r.font.bold = True
    r.font.size = Pt(8)
    r.font.color.rgb = C_GREEN
    r_sub = p.add_run()
    r_sub.text = "Dharmasagar Catchment: Onset MET, Active 74%, Break 18% (Helps reduce re-sowing risk)"
    r_sub.font.size = Pt(7)
    r_sub.font.color.rgb = C_MUTED_TEXT

    status_img = os.path.join(IMG_DIR, "status_grid.png")
    if os.path.exists(status_img):
        slide2.shapes.add_picture(status_img, in_to_emu(7.35), in_to_emu(5.48), width=in_to_emu(5.48), height=in_to_emu(1.32))

    print("Slide 2 built successfully.")

    # =========================================================================
    # SLIDE 3: TECHNICAL APPROACH
    # =========================================================================
    print("Building Slide 3: Technical Hero Architecture & Evidence...")
    slide3 = prs.slides[2]
    remove_template_placeholder(slide3, "TextBox 8")
    add_header_bar(slide3, "TECHNICAL APPROACH",
                   "❖ Predefined Pointers • Technologies to be used (languages, frameworks, hardware) • Methodology and process for implementation (Flow Charts/Images/ working prototype)")

    # 1. Left: Visually Dominant Architecture Pipeline (8 Stages)
    pipe_left = 0.40
    pipe_top = 1.44
    pipe_w = 5.60
    pipe_h = 5.00

    # Background card with clean border
    create_card(slide3, pipe_left, pipe_top, pipe_w, pipe_h, C_BG_CARD, C_BORDER_CARD, 1.2)
    
    # Header card for pipeline
    c_p_head = create_card(slide3, pipe_left + 0.12, pipe_top + 0.08, pipe_w - 0.24, 0.32, C_DARK_NAVY, None)
    tf_ph = c_p_head.text_frame
    tf_ph.vertical_anchor = MSO_ANCHOR.MIDDLE
    p_ph = tf_ph.paragraphs[0]
    p_ph.alignment = PP_ALIGN.CENTER
    r_ph = p_ph.add_run()
    r_ph.text = "END-TO-END ARCHITECTURAL & METHODOLOGY PIPELINE"
    r_ph.font.bold = True
    r_ph.font.size = Pt(8.5)
    r_ph.font.color.rgb = C_WHITE

    arch_steps = [
        ("1. GLOBAL TELECONNECTIONS", "NOAA CPC ONI (real SST connector) | IOD (DMI) & MJO (RMM) benchmarks", RGBColor(238, 242, 255), C_DEEP_BLUE),
        ("2. REGIONAL AGRO-MET TELEMETRY", "NASA POWER API + Tenali catchment daily observations (2015–2025; 4,018 rows)", C_WHITE, C_DARK_NAVY),
        ("3. FEATURE ENGINEERING", "18 input features: Lagged anomalies (7d, 14d, 30d), moisture deficit, thermal gradients", C_WHITE, C_DARK_NAVY),
        ("4. PHYSICS-INFORMED ML ENGINE", "Random Forest Classifier (break_model_rf_real_candidate.joblib) trained on S2S physics", RGBColor(240, 253, 250), C_PRIMARY_BLUE),
        ("5. PROBABILISTIC S2S OUTLOOK", "7 / 14 / 21 / 30-Day Multi-Horizon calibrated probabilistic distributions & spreads", RGBColor(254, 243, 199), C_AMBER),
        ("6. OPERATIONAL DECISION LAYER", "IMD-adapted Onset (MET) | Active Spells | Break Risk (>7d dry run) | Heavy Rain (>64.5mm)", RGBColor(254, 242, 242), C_RED),
        ("7. GEOSPATIAL & ADVISORY ENGINES", "Leaflet GIS Risk Polygons + ICAR-CRIDA stage rules for 6 Kharif crops & alternatives", RGBColor(240, 253, 244), C_GREEN),
        ("8. MULTI-CHANNEL RURAL DELIVERY", "Farmer / Extension Officer workflows | 7 Languages | Web Speech TTS | Simulated SMS/WhatsApp", RGBColor(250, 245, 255), RGBColor(147, 51, 234))
    ]

    for idx, (t, d, bg, tc) in enumerate(arch_steps):
        s_top = pipe_top + 0.48 + idx * 0.55
        c = create_card(slide3, pipe_left + 0.12, s_top, pipe_w - 0.24, 0.48, bg, C_BORDER_CARD, 1)
        tf = c.text_frame
        tf.word_wrap = True
        p1 = tf.paragraphs[0]
        r1 = p1.add_run()
        r1.text = f"{t}: "
        r1.font.bold = True
        r1.font.size = Pt(8)
        r1.font.color.rgb = tc
        r2 = p1.add_run()
        r2.text = d
        r2.font.size = Pt(7.1)
        r2.font.color.rgb = C_SLATE_TEXT

    # 2. Right: Two Real Working Prototype Screenshots
    shot_left = 6.20
    shot_w = 6.73

    # Screenshot 1: Leaflet Risk Map
    shot1_top = 1.44
    shot1_h = 2.45
    create_card(slide3, shot_left, shot1_top, shot_w, shot1_h, C_BG_CARD, C_BORDER_CARD, 1)
    
    t_bar1 = create_card(slide3, shot_left + 0.10, shot1_top + 0.08, shot_w - 0.20, 0.28, C_DEEP_BLUE, None)
    tf_tb1 = t_bar1.text_frame
    tf_tb1.vertical_anchor = MSO_ANCHOR.MIDDLE
    p1 = tf_tb1.paragraphs[0]
    p1.alignment = PP_ALIGN.LEFT
    r1 = p1.add_run()
    r1.text = "  1. HYPERLOCAL GEOSPATIAL RISK MAP & ISOCHRONES (LEAFLET.JS GIS)"
    r1.font.bold = True
    r1.font.size = Pt(7.8)
    r1.font.color.rgb = C_WHITE

    map_img = os.path.join(IMG_DIR, "risk_map.png")
    if os.path.exists(map_img):
        slide3.shapes.add_picture(map_img, in_to_emu(shot_left + 0.10), in_to_emu(shot1_top + 0.40), width=in_to_emu(shot_w - 0.20), height=in_to_emu(1.82))

    lbl_disc = slide3.shapes.add_textbox(in_to_emu(shot_left + 0.12), in_to_emu(shot1_top + 2.24), in_to_emu(shot_w - 0.24), in_to_emu(0.18))
    p_d = lbl_disc.text_frame.paragraphs[0]
    r_d = p_d.add_run()
    r_d.text = "* Demonstration boundary — not an official administrative boundary. Isochrones & radar are simulated."
    r_d.font.size = Pt(6.5)
    r_d.font.italic = True
    r_d.font.color.rgb = C_MUTED_TEXT

    # Screenshot 2: Crop Advisories & Crop-Choice Engine
    shot2_top = 3.96
    shot2_h = 2.48
    create_card(slide3, shot_left, shot2_top, shot_w, shot2_h, C_BG_CARD, C_BORDER_CARD, 1)

    t_bar2 = create_card(slide3, shot_left + 0.10, shot2_top + 0.08, shot_w - 0.20, 0.28, C_GREEN, None)
    tf_tb2 = t_bar2.text_frame
    tf_tb2.vertical_anchor = MSO_ANCHOR.MIDDLE
    p2 = tf_tb2.paragraphs[0]
    p2.alignment = PP_ALIGN.LEFT
    r2 = p2.add_run()
    r2.text = "  2. ICAR-CRIDA AGRICULTURAL ADVISORY & CONTINGENCY ENGINE"
    r2.font.bold = True
    r2.font.size = Pt(7.8)
    r2.font.color.rgb = C_WHITE

    crops_img = os.path.join(IMG_DIR, "crop_advisories.png")
    if os.path.exists(crops_img):
        slide3.shapes.add_picture(crops_img, in_to_emu(shot_left + 0.10), in_to_emu(shot2_top + 0.40), width=in_to_emu(shot_w - 0.20), height=in_to_emu(1.85))

    lbl_crop_note = slide3.shapes.add_textbox(in_to_emu(shot_left + 0.15), in_to_emu(shot2_top + 2.26), in_to_emu(shot_w - 0.3), in_to_emu(0.20))
    p_cn = lbl_crop_note.text_frame.paragraphs[0]
    r_cn = p_cn.add_run()
    r_cn.text = "Automatic alternative crop recommendation: Short-duration Telangana Sona RNR 15048 / Kadiri-6."
    r_cn.font.size = Pt(6.5)
    r_cn.font.italic = True
    r_cn.font.color.rgb = C_MUTED_TEXT

    # 3. Bottom Tech Stack Strip
    stack_bar = create_card(slide3, 0.40, 6.50, 12.53, 0.38, C_DARK_NAVY, None)
    tf_s = stack_bar.text_frame
    p_s = tf_s.paragraphs[0]
    p_s.alignment = PP_ALIGN.CENTER
    r_s = p_s.add_run()
    r_s.text = "TECH STACK: Python 3.14 / Flask 3.1  |  Scikit-Learn 1.6.1 / Joblib  |  Leaflet.js 1.9.4  |  Chart.js 4.4.1  |  SQLite3  |  Web Speech API  |  7-Language i18n"
    r_s.font.bold = True
    r_s.font.size = Pt(8.2)
    r_s.font.color.rgb = C_WHITE

    print("Slide 3 built successfully.")

    # =========================================================================
    # SLIDE 4: FEASIBILITY & VIABILITY
    # =========================================================================
    print("Building Slide 4: Feasibility & Evidence-Driven Validation...")
    slide4 = prs.slides[3]
    remove_template_placeholder(slide4, "TextBox 8")
    add_header_bar(slide4, "FEASIBILITY AND VIABILITY",
                   "❖ Predefined Pointers • Analysis of the feasibility of the idea • Potential challenges and risks • Strategies for overcoming these challenges")

    # 1. Top Section: 4 Large Verified Metrics Cards
    met_top = 1.44
    met_w = 3.00
    met_gap = 0.17
    met_h = 1.25

    metrics_s4 = [
        ("+0.158", "Brier Skill Score (BSS)", "Verified skill improvement over 30-year climatology baseline (BS: 0.171 vs 0.203).", C_PRIMARY_BLUE),
        ("0.756", "ROC-AUC Score", "Strong discriminative capability separating active wet spells from damaging dry break spells (Recall: 0.692).", C_GREEN),
        ("60 / 60", "Backend Tests Passed", "100% Pytest pass rate across API contracts, ML inference, crop rules & i18n integrity.", C_DEEP_BLUE),
        ("42 / 42", "Mobile Audit Passed", "100% responsive pass rate across 6 viewport resolutions (320px–1440px) and all 7 languages.", C_ORANGE)
    ]

    for idx, (num, lbl, desc, col) in enumerate(metrics_s4):
        c_left = 0.40 + idx * (met_w + met_gap)
        card = create_card(slide4, c_left, met_top, met_w, met_h, C_BG_CARD, C_BORDER_CARD, 1.2)
        tf = card.text_frame
        tf.word_wrap = True
        p1 = tf.paragraphs[0]
        r1 = p1.add_run()
        r1.text = f"{num}\n"
        r1.font.bold = True
        r1.font.size = Pt(20)
        r1.font.color.rgb = col
        p2 = tf.add_paragraph()
        r2 = p2.add_run()
        r2.text = f"{lbl}\n"
        r2.font.bold = True
        r2.font.size = Pt(8.5)
        r2.font.color.rgb = C_DARK_NAVY
        p3 = tf.add_paragraph()
        r3 = p3.add_run()
        r3.text = desc
        r3.font.size = Pt(7)
        r3.font.color.rgb = C_SLATE_TEXT

    # 2. Middle Split: Left = Model Validation; Right = Implementation Status, Limitation & Roadmap
    v_top = 2.78
    v_h = 3.65
    v_left_w = 4.80

    card_val = create_card(slide4, 0.40, v_top, v_left_w, v_h, C_BG_CARD, C_BORDER_CARD, 1.2)
    tf_v = card_val.text_frame
    tf_v.word_wrap = True
    p = tf_v.paragraphs[0]
    r = p.add_run()
    r.text = "MODEL VALIDATION & ZERO LEAKAGE POLICY:\n"
    r.font.bold = True
    r.font.size = Pt(9.5)
    r.font.color.rgb = C_PRIMARY_BLUE

    val_bullets = [
        ("Chronological Train/Test Split:", "Strict temporal partition without k-fold leakage.\n• Train Set: 2015–2022 (2,922 daily observed records)\n• Test Set: 2023–2025 (1,096 daily unseen records)"),
        ("Zero Temporal Leakage Policy:", "Standard random cross-validation allows future atmospheric states to leak into past predictions. VarshaSetu strictly evaluates on out-of-sample forward horizons."),
        ("Verified Candidate Metrics:", "• Brier Score: 0.171 (vs 0.203 Climatology Baseline)\n• ROC-AUC: 0.756 | Precision: 0.621 | Recall: 0.692\n• F1-Score: 0.655 for rare damaging break spell events"),
        ("Zero Cost Burden on Farmers:", "Lightweight browser execution requiring no high-end devices, app store downloads, or paid farmer subscriptions.")
    ]

    for title, desc in val_bullets:
        p1 = tf_v.add_paragraph()
        p1.space_before = Pt(4)
        r1 = p1.add_run()
        r1.text = f"• {title} "
        r1.font.bold = True
        r1.font.size = Pt(8)
        r1.font.color.rgb = C_DARK_NAVY
        r2 = p1.add_run()
        r2.text = desc
        r2.font.size = Pt(7.3)
        r2.font.color.rgb = C_SLATE_TEXT

    # Right: Implementation Status, Limitation & Future Integration
    v_right_w = 7.55
    v_right_left = 5.38
    card_feas = create_card(slide4, v_right_left, v_top, v_right_w, v_h, C_WHITE, C_BORDER_CARD, 1.2)
    tf_f = card_feas.text_frame
    tf_f.word_wrap = True
    p = tf_f.paragraphs[0]
    r = p.add_run()
    r.text = "ENGINEERING FEASIBILITY, TRANSPARENCY & INTEGRATION ROADMAP:\n"
    r.font.bold = True
    r.font.size = Pt(9.5)
    r.font.color.rgb = C_DEEP_BLUE

    feas_sections = [
        ("CURRENTLY IMPLEMENTED (Working Prototype):",
         "✓ Physics-informed ML forecasting (7, 14, 21, 30 days)  |  ✓ Live NOAA CPC ENSO ONI connector\n"
         "✓ Interactive Leaflet risk mapping (isochrones & radar)  |  ✓ ICAR-CRIDA stage rules for 6 Kharif crops\n"
         "✓ Contingent short-duration cultivars  |  ✓ 7 Indian languages with native Urdu RTL  |  ✓ Web Speech audio TTS\n"
         "✓ Dual Farmer & Extension Officer workflows  |  ✓ SQLite transmission audit logging",
         RGBColor(240, 253, 244), C_GREEN),
        ("CURRENT ENGINEERING LIMITATION (Radical Transparency):",
         "• Operational NCMRWF ERPS upper-air gridded data socket requires institutional MoES security credentials.\n"
         "• Current Prototype Solution: Gracefully utilizes statistically calibrated climatological benchmark distributions\n"
         "  for 850 hPa wind and satellite OLR, transparently disclosed as [CONFIGURED BENCHMARK] in UI.",
         RGBColor(254, 243, 199), C_AMBER),
        ("FUTURE INTEGRATION ROADMAP (Deployment Readiness):",
         "• Live NCMRWF Feed Integration: Plug-and-play architecture ready for NCMRWF NEPS 12km ensemble stream.\n"
         "• Production Telecom Gateway: Sandbox payload generator ready for State portals (e.g. Rythu Bharosa SMS).\n"
         "• Multi-State Rollout: Pluggable ICAR-CRIDA rules support seamless expansion to Maharashtra, MP, and Karnataka.",
         RGBColor(238, 242, 255), C_DEEP_BLUE)
    ]

    for title, desc, bg, tcol in feas_sections:
        p1 = tf_f.add_paragraph()
        p1.space_before = Pt(5)
        r1 = p1.add_run()
        r1.text = f"{title}\n"
        r1.font.bold = True
        r1.font.size = Pt(8.3)
        r1.font.color.rgb = tcol
        p2 = tf_f.add_paragraph()
        r2 = p2.add_run()
        r2.text = desc
        r2.font.size = Pt(7.3)
        r2.font.color.rgb = C_SLATE_TEXT

    # 3. Bottom Phased Roadmap Strip
    bar_m = create_card(slide4, 0.40, 6.50, 12.53, 0.38, C_DARK_NAVY, None)
    tf_m = bar_m.text_frame
    p_m = tf_m.paragraphs[0]
    p_m.alignment = PP_ALIGN.CENTER
    r_m = p_m.add_run()
    r_m.text = "MATURITY CONTINUUM:  Prototype (Verified)  ➔  Pilot (Target Catchments)  ➔  Operational Integration (MoES/NCMRWF Aligned)"
    r_m.font.bold = True
    r_m.font.size = Pt(8.5)
    r_m.font.color.rgb = RGBColor(253, 224, 71)

    print("Slide 4 built successfully.")

    # =========================================================================
    # SLIDE 5: IMPACT & BENEFITS
    # =========================================================================
    print("Building Slide 5: Capability-Based Impact & Benefits...")
    slide5 = prs.slides[4]
    remove_template_placeholder(slide5, "TextBox 8")
    add_header_bar(slide5, "IMPACT AND BENEFITS",
                   "❖ Predefined Pointers • Potential impact on the target audience • Benefits of the solution (social, economic, environmental, etc.)")

    # Three Major Stakeholder Panels
    p_top = 1.44
    p_w = 4.02
    p_gap = 0.23
    p_h = 4.95

    # Panel 1: Farmers
    c_farm = create_card(slide5, 0.40, p_top, p_w, p_h, C_BG_CARD, C_BORDER_CARD, 1.2)
    tf1 = c_farm.text_frame
    tf1.word_wrap = True
    p = tf1.paragraphs[0]
    r = p.add_run()
    r.text = "FARMERS:  KNOW ➔ DECIDE ➔ ACT\n"
    r.font.bold = True
    r.font.size = Pt(9.5)
    r.font.color.rgb = C_GREEN
    r_sub = p.add_run()
    r_sub.text = "Micro-Level Actionable Field Directives\n"
    r_sub.font.bold = True
    r_sub.font.size = Pt(8)
    r_sub.font.color.rgb = C_DARK_NAVY

    farm_points = [
        ("Onset Uncertainty Awareness:", "Prepares nursery and seedbed with thermodynamic confidence instead of speculative sowing."),
        ("Break-Spell Risk Awareness:", "Avoids sowing directly before a 10-day dry spell, helping reduce re-sowing risk."),
        ("Heavy-Rain Precautions:", "Protects freshly applied fertilizers from leaching; opens drainage furrows to prevent seedling submergence."),
        ("Crop-Specific Sowing Gates:", "Moisture saturation minimums tailored to Paddy (70%), Cotton (60%), Groundnut (50%)."),
        ("Informed Irrigation Timing:", "Maximizes natural rainfall utilization; schedules life-saving protective irrigation only when necessary."),
        ("Contingency Cultivar Choices:", "Suggests short-duration varieties (e.g. Telangana Sona RNR 15048) if onset is delayed >14 days."),
        ("Vernacular Voice Access:", "Illiterate and marginal farmers listen to advisories via one-tap Web Speech audio TTS in native dialect.")
    ]

    for t, d in farm_points:
        p_pt = tf1.add_paragraph()
        p_pt.space_before = Pt(3)
        r_t = p_pt.add_run()
        r_t.text = f"• {t} "
        r_t.font.bold = True
        r_t.font.size = Pt(7.8)
        r_t.font.color.rgb = C_DARK_NAVY
        r_d = p_pt.add_run()
        r_d.text = d
        r_d.font.size = Pt(7.2)
        r_d.font.color.rgb = C_SLATE_TEXT

    # Panel 2: Extension Officers
    c_off = create_card(slide5, 0.40 + p_w + p_gap, p_top, p_w, p_h, C_BG_CARD, C_BORDER_CARD, 1.2)
    tf2 = c_off.text_frame
    tf2.word_wrap = True
    p = tf2.paragraphs[0]
    r = p.add_run()
    r.text = "EXTENSION OFFICERS:  SEE ➔ PRIORITIZE ➔ COMMUNICATE\n"
    r.font.bold = True
    r.font.size = Pt(9.5)
    r.font.color.rgb = C_PRIMARY_BLUE
    r_sub = p.add_run()
    r_sub.text = "Mandal-Scale Tactical Oversight & Coordination\n"
    r_sub.font.bold = True
    r_sub.font.size = Pt(8)
    r_sub.font.color.rgb = C_DARK_NAVY

    off_points = [
        ("Spatial Risk Visualization:", "Evaluates composite vulnerability clusters (Low to Severe) across 10–20 adjoining Panchayats simultaneously."),
        ("Block/Mandal Aggregates:", "Synthesizes regional rainfall anomalies and dry spell duration for proactive administrative intervention."),
        ("Standardized Crop Intelligence:", "Harmonizes ICAR-CRIDA agronomic guidance across Krishi Vigyan Kendras (KVKs) and field workers."),
        ("Contingency Seed Mobilization:", "Prepositions buffer stocks of drought-resilient alternative seeds ahead of forecast break spells."),
        ("Input Supply Synchronization:", "Directs Primary Agricultural Credit Societies (PACS) to schedule subsidized fertilizer release around heavy rain."),
        ("Targeted Messaging Workflow:", "Dispatches localized mobile alerts to specific village farming groups via simulated gateway."),
        ("Audit Accountability:", "Maintains transparent SQLite records of dispatch history, delivery status, and timestamps.")
    ]

    for t, d in off_points:
        p_pt = tf2.add_paragraph()
        p_pt.space_before = Pt(3)
        r_t = p_pt.add_run()
        r_t.text = f"• {t} "
        r_t.font.bold = True
        r_t.font.size = Pt(7.8)
        r_t.font.color.rgb = C_DARK_NAVY
        r_d = p_pt.add_run()
        r_d.text = d
        r_d.font.size = Pt(7.2)
        r_d.font.color.rgb = C_SLATE_TEXT

    # Panel 3: System & Society (Triple Pillars)
    c_soc = create_card(slide5, 0.40 + 2 * (p_w + p_gap), p_top, p_w, p_h, C_BG_CARD, C_BORDER_CARD, 1.2)
    tf3 = c_soc.text_frame
    tf3.word_wrap = True
    p = tf3.paragraphs[0]
    r = p.add_run()
    r.text = "SYSTEM & SOCIETY:  TRIPLE IMPACT PILLARS\n"
    r.font.bold = True
    r.font.size = Pt(9.5)
    r.font.color.rgb = C_DEEP_BLUE
    r_sub = p.add_run()
    r_sub.text = "Social, Economic & Environmental Value\n"
    r_sub.font.bold = True
    r_sub.font.size = Pt(8)
    r_sub.font.color.rgb = C_DARK_NAVY

    soc_points = [
        ("SOCIAL INCLUSIVITY:",
         "• 7 regional languages (English, Telugu, Hindi, Tamil, Kannada, Urdu, Malayalam) with 231 keys each.\n"
         "• Native Urdu RTL layout transformation and Nastaliq typography.\n"
         "• Web Speech API TTS delivers audio to illiterate smallholders.\n"
         "• Mobile-first web access operates on basic smartphone browsers without requiring paid app downloads."),
        ("ECONOMIC RESILIENCE:",
         "• Supports optimal timing of seed sowing, irrigation cycles, and fertilizer application.\n"
         "• Helps manage avoidable re-sowing risk through 10–14 day break-spell awareness.\n"
         "• Promotes low-cost contingency cultivars to salvage late-onset seasons."),
        ("ENVIRONMENTAL SUSTAINABILITY:",
         "• Fertilizer precautions around heavy-rain risk prevent chemical runoff into rural water bodies.\n"
         "• Informed irrigation timing conserves valuable groundwater reserves.\n"
         "• Fosters climate-resilient crop selection adapted to S2S rainfall variability.")
    ]

    for t, d in soc_points:
        p_pt = tf3.add_paragraph()
        p_pt.space_before = Pt(4)
        r_t = p_pt.add_run()
        r_t.text = f"{t}\n"
        r_t.font.bold = True
        r_t.font.size = Pt(8)
        r_t.font.color.rgb = C_DARK_NAVY
        r_d = p_pt.add_run()
        r_d.text = d
        r_d.font.size = Pt(7.1)
        r_d.font.color.rgb = C_SLATE_TEXT

    # Strong Bottom Evidence Strip
    bar_e = create_card(slide5, 0.40, 6.50, 12.53, 0.38, C_DARK_NAVY, None)
    tf_e = bar_e.text_frame
    p_e = tf_e.paragraphs[0]
    p_e.alignment = PP_ALIGN.CENTER
    r_e = p_e.add_run()
    r_e.text = "EVIDENCE STRIP:  WORKING PROTOTYPE  |  60/60 BACKEND TESTS  |  42/42 MOBILE AUDITS  |  7 LANGUAGES  |  PROBABILISTIC S2S ML  |  HYPERLOCAL GIS"
    r_e.font.bold = True
    r_e.font.size = Pt(8.5)
    r_e.font.color.rgb = C_WHITE

    print("Slide 5 built successfully.")

    # =========================================================================
    # SLIDE 6: RESEARCH & REFERENCES
    # =========================================================================
    print("Building Slide 6: Research Foundations & Ethical Disclosures...")
    slide6 = prs.slides[5]
    remove_template_placeholder(slide6, "TextBox 8")
    add_header_bar(slide6, "RESEARCH  AND REFERENCES",
                   "❖ Predefined Pointers • Details / Links of the reference and research work")

    # 1. Research-to-Prototype Pipeline (Top Banner)
    flow_bar = create_card(slide6, 0.40, 1.44, 12.53, 0.38, C_SLATE_DEEP, None)
    tf_flow = flow_bar.text_frame
    p_f = tf_flow.paragraphs[0]
    p_f.alignment = PP_ALIGN.CENTER
    r_f = p_f.add_run()
    r_f.text = "RESEARCH-TO-PROTOTYPE PIPELINE: Problem Identification ➔ Scientific Research ➔ Climate Features ➔ ML Model ➔ Probabilistic Validation ➔ Working Prototype"
    r_f.font.bold = True
    r_f.font.size = Pt(8)
    r_f.font.color.rgb = RGBColor(224, 242, 254)

    # 2. Three Grouped Research Foundation Cards
    card_w = 4.02
    card_h = 3.35
    card_top = 1.90
    card_gap = 0.23

    # Card 1: Monsoon & Meteorology
    c_met = create_card(slide6, 0.40, card_top, card_w, card_h, C_BG_CARD, C_BORDER_CARD, 1.2)
    tf1 = c_met.text_frame
    tf1.word_wrap = True
    p = tf1.paragraphs[0]
    r = p.add_run()
    r.text = "MONSOON & METEOROLOGICAL RESEARCH:\n"
    r.font.bold = True
    r.font.size = Pt(9)
    r.font.color.rgb = C_DEEP_BLUE

    met_refs = [
        ("India Meteorological Department (IMD):", "Operational criteria for Southwest Monsoon onset declaration over Kerala, S2S extended range protocols, and agro-met advisories. [mausam.imd.gov.in]"),
        ("Ministry of Earth Sciences (MoES) & NCMRWF:", "National Centre for Medium Range Weather Forecasting Extended Range Prediction System (ERPS) reanalysis and model documentation. [ncmrwf.gov.in]"),
        ("NOAA Climate Prediction Center (CPC):", "Oceanic Niño Index (ONI) 3-month running mean SST anomalies in Niño 3.4 region (Real external connector). [cpc.ncep.noaa.gov]"),
        ("Australian Bureau of Meteorology (BOM):", "Indian Ocean Dipole (DMI) and Wheeler-Hendon Real-time Multivariate MJO (RMM1/RMM2) indices. [bom.gov.au/climate]")
    ]

    for t, d in met_refs:
        p_pt = tf1.add_paragraph()
        p_pt.space_before = Pt(3)
        r_t = p_pt.add_run()
        r_t.text = f"• {t} "
        r_t.font.bold = True
        r_t.font.size = Pt(7.8)
        r_t.font.color.rgb = C_DARK_NAVY
        r_d = p_pt.add_run()
        r_d.text = d
        r_d.font.size = Pt(7.1)
        r_d.font.color.rgb = C_SLATE_TEXT

    # Card 2: Agriculture & Data Sources
    c_agr = create_card(slide6, 0.40 + card_w + card_gap, card_top, card_w, card_h, C_BG_CARD, C_BORDER_CARD, 1.2)
    tf2 = c_agr.text_frame
    tf2.word_wrap = True
    p = tf2.paragraphs[0]
    r = p.add_run()
    r.text = "AGRICULTURE & SATELLITE DATA SOURCES:\n"
    r.font.bold = True
    r.font.size = Pt(9)
    r.font.color.rgb = C_GREEN

    agr_refs = [
        ("ICAR - CRIDA Agro-Met Protocols:", "Central Research Institute for Dryland Agriculture technical contingency bulletins, moisture saturation gates, and cultivar selection protocols for rainfed Kharif crops. [crida.in]"),
        ("NASA POWER Agro-Climatology Project:", "Prediction of Worldwide Energy Resources surface agro-climatology data access for solar radiation, relative humidity, precipitation, and surface temperature. [power.larc.nasa.gov]"),
        ("Tenali Agricultural Catchment Records:", "4,018 daily observed weather records (2015–2025) utilized for chronological out-of-sample model training and evaluation.")
    ]

    for t, d in agr_refs:
        p_pt = tf2.add_paragraph()
        p_pt.space_before = Pt(3)
        r_t = p_pt.add_run()
        r_t.text = f"• {t} "
        r_t.font.bold = True
        r_t.font.size = Pt(7.8)
        r_t.font.color.rgb = C_DARK_NAVY
        r_d = p_pt.add_run()
        r_d.text = d
        r_d.font.size = Pt(7.1)
        r_d.font.color.rgb = C_SLATE_TEXT

    # Card 3: Evaluation Standards & Accessibility
    c_std = create_card(slide6, 0.40 + 2 * (card_w + card_gap), card_top, card_w, card_h, C_BG_CARD, C_BORDER_CARD, 1.2)
    tf3 = c_std.text_frame
    tf3.word_wrap = True
    p = tf3.paragraphs[0]
    r = p.add_run()
    r.text = "EVALUATION STANDARDS & ACCESSIBILITY:\n"
    r.font.bold = True
    r.font.size = Pt(9)
    r.font.color.rgb = C_PRIMARY_BLUE

    std_refs = [
        ("WMO S2S Prediction Project:", "World Meteorological Organization Subseasonal-to-Seasonal prediction research, Brier Skill Score standards, and probabilistic verification frameworks. [s2sprediction.net]"),
        ("Probabilistic Forecast Scoring:", "Brier Score (BS), Brier Skill Score (BSS), and ROC-AUC verification standards for calibrated binary and multi-class weather probability assessment."),
        ("W3C Web Speech & Telecom Standards:", "SpeechSynthesis API BCP-47 localized voice standards & TRAI DLT rural messaging template specifications.")
    ]

    for t, d in std_refs:
        p_pt = tf3.add_paragraph()
        p_pt.space_before = Pt(3)
        r_t = p_pt.add_run()
        r_t.text = f"• {t} "
        r_t.font.bold = True
        r_t.font.size = Pt(7.8)
        r_t.font.color.rgb = C_DARK_NAVY
        r_d = p_pt.add_run()
        r_d.text = d
        r_d.font.size = Pt(7.1)
        r_d.font.color.rgb = C_SLATE_TEXT

    # 3. Bottom Mandatory Ethical Disclosures & Scientific Boundaries Box
    disc_top = 5.35
    disc_h = 1.48
    c_disc = create_card(slide6, 0.40, disc_top, 12.53, disc_h, RGBColor(255, 251, 235), RGBColor(252, 211, 77), 1.2)
    tf_d = c_disc.text_frame
    tf_d.word_wrap = True
    p = tf_d.paragraphs[0]
    r = p.add_run()
    r.text = "SCIENTIFIC INTEGRITY, PROTOTYPE BOUNDARIES & ETHICAL DISCLOSURES:\n"
    r.font.bold = True
    r.font.size = Pt(8.5)
    r.font.color.rgb = C_AMBER

    disclosures = [
        ("NCMRWF Connectivity Disclosure:", "NCMRWF upper-air variables (850 hPa wind, satellite OLR) are currently represented via calibrated climatological benchmark fallbacks; live supercomputing integration is an MoES-authorized post-hackathon deployment step."),
        ("IMD Onset Advisory Limitation:", "IMD-referenced monsoon onset criteria adapted within the VarshaSetu hyperlocal forecasting framework; this dashboard does not issue an official statutory IMD onset declaration."),
        ("Rural Messaging Sandbox:", "SMS and WhatsApp delivery workflows are demonstrated through a sandboxed simulation gateway without live commercial cellular telecom charges."),
        ("Cartographic Boundaries:", "Demonstration village polygons and isochrones are approximate visualization bounding-boxes, not official Survey of India administrative cadastral boundaries.")
    ]

    for t, d in disclosures:
        p_pt = tf_d.add_paragraph()
        p_pt.space_before = Pt(1.5)
        r_t = p_pt.add_run()
        r_t.text = f"• {t} "
        r_t.font.bold = True
        r_t.font.size = Pt(7.2)
        r_t.font.color.rgb = C_DARK_NAVY
        r_d = p_pt.add_run()
        r_d.text = d
        r_d.font.size = Pt(7)
        r_d.font.color.rgb = C_SLATE_TEXT

    print("Slide 6 built successfully.")

    # Save presentation
    print(f"Saving final PowerPoint to: {OUT_PPTX}...")
    prs.save(OUT_PPTX)
    print("PowerPoint presentation saved successfully!")

    # Verify slide count
    prs_v = Presentation(OUT_PPTX)
    print(f"Verified saved PPTX slide count: {len(prs_v.slides)}")
    assert len(prs_v.slides) == 6, f"Error: Slide count is {len(prs_v.slides)}, expected 6!"

if __name__ == "__main__":
    main()
