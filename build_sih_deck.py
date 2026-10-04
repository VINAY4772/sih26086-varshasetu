import os
import sys
import pptx
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

SRC_PPTX = '/Users/maradanasaikiran/Downloads/Smart India Hackathon 2026 - VarshaSetu Presentation (1).pptx'
OUT_DIR = '/Users/maradanasaikiran/vinay new sih/SIH_PPT'
OUT_PPTX = os.path.join(OUT_DIR, 'VarshaSetu_SIH2026_6Slide_Official.pptx')
IMG_DIR = '/Users/maradanasaikiran/vinay new sih/varshshetu full doc/img'

os.makedirs(OUT_DIR, exist_ok=True)
prs = Presentation(SRC_PPTX)
print("Opened presentation successfully.")

# Colors
COLOR_DARK_BLUE = RGBColor(17, 24, 39)     # #111827
COLOR_NAVY = RGBColor(30, 41, 59)          # #1e293b
COLOR_WHITE = RGBColor(255, 255, 255)
COLOR_ORANGE = RGBColor(234, 88, 12)       # #ea580c
COLOR_GREEN = RGBColor(22, 163, 74)        # #16a34a
COLOR_LIGHT_BG = RGBColor(248, 250, 252)   # #f8fafc
COLOR_CARD_BORDER = RGBColor(226, 232, 240)# #e2e8f0
COLOR_TEXT_MUTED = RGBColor(100, 116, 139) # #64748b
COLOR_TEXT_DARK = RGBColor(15, 23, 42)     # #0f172a
COLOR_ACCENT_BLUE = RGBColor(37, 99, 235)  # #2563eb
COLOR_ACCENT_CYAN = RGBColor(14, 165, 233) # #0ea5e9
COLOR_AMBER = RGBColor(217, 119, 6)        # #d97706

def update_header_badge(slide, shape_name):
    for s in slide.shapes:
        if s.name == shape_name and s.has_text_frame:
            tf = s.text_frame
            tf.clear()
            p = tf.paragraphs[0]
            p.alignment = PP_ALIGN.RIGHT
            run = p.add_run()
            run.text = "PS ID: SIH26086 | Team: TITANS (ID: 120087)"
            run.font.size = Pt(8.5)
            run.font.bold = True
            run.font.color.rgb = COLOR_TEXT_DARK

# ==========================================
# SLIDE 1: TITLE PAGE
# ==========================================
slide1 = prs.slides[0]
print("Processing Slide 1...")

# Update Team ID, Team Name, Theme, and Titles
for s in slide1.shapes:
    if s.has_text_frame:
        t = s.text_frame.text.strip()
        if "SIH2026-TEAM-VARSHASETU" in t or "Team ID:" in t:
            s.text_frame.clear()
            p = s.text_frame.paragraphs[0]
            r1 = p.add_run()
            r1.text = "Team ID: "
            r1.font.bold = False
            r1.font.size = Pt(11)
            r1.font.color.rgb = COLOR_TEXT_MUTED
            r2 = p.add_run()
            r2.text = "120087"
            r2.font.bold = True
            r2.font.size = Pt(11)
            r2.font.color.rgb = COLOR_WHITE
        elif "Team Name:" in t:
            s.text_frame.clear()
            p = s.text_frame.paragraphs[0]
            r1 = p.add_run()
            r1.text = "Team Name: "
            r1.font.bold = False
            r1.font.size = Pt(11)
            r1.font.color.rgb = COLOR_TEXT_MUTED
            r2 = p.add_run()
            r2.text = "TITANS"
            r2.font.bold = True
            r2.font.size = Pt(11)
            r2.font.color.rgb = COLOR_ORANGE
        elif "Theme:" in t:
            s.text_frame.clear()
            p = s.text_frame.paragraphs[0]
            r1 = p.add_run()
            r1.text = "Theme: "
            r1.font.bold = False
            r1.font.size = Pt(11)
            r1.font.color.rgb = COLOR_TEXT_MUTED
            r2 = p.add_run()
            r2.text = "Agriculture, FoodTech & Rural Development"
            r2.font.bold = True
            r2.font.size = Pt(11)
            r2.font.color.rgb = COLOR_WHITE
        elif "Bridging Subseasonal" in t:
            s.text_frame.clear()
            p = s.text_frame.paragraphs[0]
            r = p.add_run()
            r.text = "“Bridging Climate Intelligence with Every Farmer”"
            r.font.size = Pt(13)
            r.font.italic = True
            r.font.color.rgb = RGBColor(148, 163, 184) # light slate

# Add College / Institute box on Slide 1
# Position: left=609600, top=3550000, width=10972800, height=380000
inst_card = slide1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Emu(609600), Emu(3550000), Emu(10972800), Emu(420000))
inst_card.fill.solid()
inst_card.fill.fore_color.rgb = RGBColor(24, 33, 52)
inst_card.line.color.rgb = RGBColor(51, 65, 85)
inst_card.line.width = Pt(1)

tf_inst = inst_card.text_frame
tf_inst.vertical_anchor = MSO_ANCHOR.MIDDLE
p_inst = tf_inst.paragraphs[0]
p_inst.alignment = PP_ALIGN.LEFT
r_lbl = p_inst.add_run()
r_lbl.text = "   INSTITUTE / COLLEGE:  "
r_lbl.font.size = Pt(10)
r_lbl.font.bold = True
r_lbl.font.color.rgb = COLOR_ORANGE

r_val = p_inst.add_run()
r_val.text = "MVGR College of Engineering (Autonomous), Vizianagaram, Andhra Pradesh"
r_val.font.size = Pt(11)
r_val.font.bold = True
r_val.font.color.rgb = COLOR_WHITE

print("Slide 1 updated successfully.")

# ==========================================
# SLIDE 2: PROPOSED SOLUTION
# ==========================================
slide2 = prs.slides[1]
print("Processing Slide 2...")
update_header_badge(slide2, "TextBox 27")

# Add Prototype Evidence & Decision Flow in bottom area of Slide 2
# top = 4300000, height = 2050000, width = 11277600
# Left card: Prototype Status Grid screenshot
status_grid_img = os.path.join(IMG_DIR, 'status_grid.png')
if os.path.exists(status_grid_img):
    card_left = slide2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Emu(457200), Emu(4350000), Emu(6300000), Emu(1980000))
    card_left.fill.solid()
    card_left.fill.fore_color.rgb = COLOR_LIGHT_BG
    card_left.line.color.rgb = COLOR_CARD_BORDER
    card_left.line.width = Pt(1)
    
    # Title banner for left card
    tb_l = slide2.shapes.add_textbox(Emu(550000), Emu(4380000), Emu(6100000), Emu(250000))
    p = tb_l.text_frame.paragraphs[0]
    r1 = p.add_run()
    r1.text = "LIVE WORKING PROTOTYPE EVIDENCE: "
    r1.font.bold = True
    r1.font.size = Pt(8.5)
    r1.font.color.rgb = COLOR_ACCENT_BLUE
    r2 = p.add_run()
    r2.text = "Dharmasagar Catchment (Adapted Onset, Active/Break Spells & Telemetry)"
    r2.font.bold = False
    r2.font.size = Pt(8.5)
    r2.font.color.rgb = COLOR_TEXT_DARK
    
    # Insert screenshot
    slide2.shapes.add_picture(status_grid_img, Emu(550000), Emu(4650000), width=Emu(6115000), height=Emu(1560000))

# Right card: Value Chain / Problem -> Solution Flow
card_right = slide2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Emu(6900000), Emu(4350000), Emu(4834800), Emu(1980000))
card_right.fill.solid()
card_right.fill.fore_color.rgb = COLOR_LIGHT_BG
card_right.line.color.rgb = COLOR_CARD_BORDER
card_right.line.width = Pt(1)

tb_r = slide2.shapes.add_textbox(Emu(7020000), Emu(4380000), Emu(4600000), Emu(250000))
p = tb_r.text_frame.paragraphs[0]
r = p.add_run()
r.text = "DECISION-MAKING LOGIC: CLIMATE SCIENCE TO LAST-MILE ACTION"
r.font.bold = True
r.font.size = Pt(8.5)
r.font.color.rgb = COLOR_GREEN

steps = [
    ("1. Global Teleconnections", "NOAA CPC ONI (real SST connector) + IOD/MJO benchmarks"),
    ("2. Physics-Informed ML", "Random Forest calibrated across 7, 14, 21, and 28-day S2S horizons"),
    ("3. ICAR-CRIDA Agro Engine", "Soil moisture gates, sowing safety, & contingent crop choices"),
    ("4. Vernacular Dispatches", "7 Indian languages, Urdu RTL layout, Web Speech TTS & SMS sandbox")
]

for idx, (title, desc) in enumerate(steps):
    step_box = slide2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Emu(7020000), Emu(4660000 + idx * 380000), Emu(4600000), Emu(330000))
    step_box.fill.solid()
    step_box.fill.fore_color.rgb = COLOR_WHITE
    step_box.line.color.rgb = COLOR_CARD_BORDER
    step_box.line.width = Pt(1)
    
    tf = step_box.text_frame
    tf.word_wrap = True
    p1 = tf.paragraphs[0]
    p1.alignment = PP_ALIGN.LEFT
    r1 = p1.add_run()
    r1.text = f"{title}: "
    r1.font.bold = True
    r1.font.size = Pt(8)
    r1.font.color.rgb = COLOR_TEXT_DARK
    
    r2 = p1.add_run()
    r2.text = desc
    r2.font.bold = False
    r2.font.size = Pt(7.5)
    r2.font.color.rgb = COLOR_TEXT_MUTED

print("Slide 2 updated successfully.")

# ==========================================
# SLIDE 3: TECHNICAL APPROACH
# ==========================================
slide3 = prs.slides[2]
print("Processing Slide 3...")
update_header_badge(slide3, "TextBox 20")

# In Slide 3 bottom area:
# Left: Risk Map Screenshot with Cartographic Disclaimer
# Right: Crop Advisories Prototype Card
risk_map_img = os.path.join(IMG_DIR, 'risk_map.png')
crop_adv_img = os.path.join(IMG_DIR, 'crop_advisories.png')

if os.path.exists(risk_map_img):
    card_map = slide3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Emu(457200), Emu(4650000), Emu(6800000), Emu(1700000))
    card_map.fill.solid()
    card_map.fill.fore_color.rgb = COLOR_LIGHT_BG
    card_map.line.color.rgb = COLOR_CARD_BORDER
    card_map.line.width = Pt(1)
    
    tb_map = slide3.shapes.add_textbox(Emu(550000), Emu(4670000), Emu(6600000), Emu(240000))
    p = tb_map.text_frame.paragraphs[0]
    r1 = p.add_run()
    r1.text = "GEOSPATIAL RISK ENGINE & RAINFALL TRAJECTORY: "
    r1.font.bold = True
    r1.font.size = Pt(8)
    r1.font.color.rgb = COLOR_ACCENT_BLUE
    r2 = p.add_run()
    r2.text = "Leaflet.js GIS, Isochrones (NLM), Radar & Soil Moisture"
    r2.font.bold = False
    r2.font.size = Pt(8)
    r2.font.color.rgb = COLOR_TEXT_DARK
    
    slide3.shapes.add_picture(risk_map_img, Emu(550000), Emu(4920000), width=Emu(6615000), height=Emu(1250000))
    
    # Disclaimer note
    tb_disc = slide3.shapes.add_textbox(Emu(550000), Emu(6180000), Emu(6600000), Emu(160000))
    p_disc = tb_disc.text_frame.paragraphs[0]
    r_disc = p_disc.add_run()
    r_disc.text = "* Demonstration boundaries — approximate visualization, not official administrative boundaries."
    r_disc.font.size = Pt(6.5)
    r_disc.font.italic = True
    r_disc.font.color.rgb = COLOR_TEXT_MUTED

# Right box: Full-Stack Verification & Crop Engine
card_crop = slide3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Emu(7400000), Emu(4650000), Emu(4334800), Emu(1700000))
card_crop.fill.solid()
card_crop.fill.fore_color.rgb = COLOR_LIGHT_BG
card_crop.line.color.rgb = COLOR_CARD_BORDER
card_crop.line.width = Pt(1)

tb_cr = slide3.shapes.add_textbox(Emu(7500000), Emu(4670000), Emu(4100000), Emu(240000))
p_cr = tb_cr.text_frame.paragraphs[0]
r_cr = p_cr.add_run()
r_cr.text = "ICAR-CRIDA ADVISORY ENGINE & DATA PROVENANCE"
r_cr.font.bold = True
r_cr.font.size = Pt(8)
r_cr.font.color.rgb = COLOR_GREEN

advisory_highlights = [
    ("6 Kharif Crops Supported", "Paddy, Cotton, Soybean, Groundnut, Maize, Redgram"),
    ("Phenology Stage Rules", "Sowing window soil gates (≥50-70%), fertilizer safeguards, pest watches"),
    ("Contingent Cultivar Pivot", "Recommends short-duration varieties (Telangana Sona RNR 15048, Kadiri-6)"),
    ("Transparent Data Provenance", "NOAA ONI (Live), NASA POWER (Observed), Climatology Benchmark (Upper-Air)")
]

for idx, (title, desc) in enumerate(advisory_highlights):
    row_box = slide3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Emu(7500000), Emu(4930000 + idx * 320000), Emu(4130000), Emu(280000))
    row_box.fill.solid()
    row_box.fill.fore_color.rgb = COLOR_WHITE
    row_box.line.color.rgb = COLOR_CARD_BORDER
    row_box.line.width = Pt(1)
    
    tf = row_box.text_frame
    p1 = tf.paragraphs[0]
    p1.alignment = PP_ALIGN.LEFT
    r1 = p1.add_run()
    r1.text = f"{title}: "
    r1.font.bold = True
    r1.font.size = Pt(7.5)
    r1.font.color.rgb = COLOR_TEXT_DARK
    
    r2 = p1.add_run()
    r2.text = desc
    r2.font.bold = False
    r2.font.size = Pt(7.2)
    r2.font.color.rgb = COLOR_TEXT_MUTED

print("Slide 3 updated successfully.")

# ==========================================
# SLIDE 4: FEASIBILITY AND VIABILITY
# ==========================================
slide4 = prs.slides[3]
print("Processing Slide 4...")
update_header_badge(slide4, "TextBox 18")

# Add Deployment Roadmap Chevron in lower area (top=5150000, height=1200000)
card_road = slide4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Emu(457200), Emu(5150000), Emu(11277600), Emu(1200000))
card_road.fill.solid()
card_road.fill.fore_color.rgb = COLOR_LIGHT_BG
card_road.line.color.rgb = COLOR_CARD_BORDER
card_road.line.width = Pt(1)

tb_road = slide4.shapes.add_textbox(Emu(600000), Emu(5180000), Emu(11000000), Emu(240000))
p_rd = tb_road.text_frame.paragraphs[0]
r_rd1 = p_rd.add_run()
r_rd1.text = "CURRENT PROTOTYPE → FIELD DEPLOYMENT ROADMAP: "
r_rd1.font.bold = True
r_rd1.font.size = Pt(8.5)
r_rd1.font.color.rgb = COLOR_ORANGE
r_rd2 = p_rd.add_run()
r_rd2.text = "Phased, verifiable scale-up pathway from working prototype to nationwide agrarian coverage"
r_rd2.font.size = Pt(8)
r_rd2.font.color.rgb = COLOR_TEXT_MUTED

roadmap_steps = [
    ("Stage 1: Working Prototype", "60/60 tests, ML model, 7-lang UI, simulated gateway (COMPLETED)"),
    ("Stage 2: Pilot Catchment", "Field validation across Tenali & Warangal mandal farmer groups"),
    ("Stage 3: MoES/NCMRWF Feed", "Ingest operational high-resolution NEPS/ERPS ensemble sockets"),
    ("Stage 4: Cadastral GIS Layers", "Replace demonstration polygons with Survey of India administrative boundaries"),
    ("Stage 5: Production Telecom", "Enterprise DLT-approved SMS shortcode & WhatsApp Business Cloud API"),
    ("Stage 6: Multi-State Scale", "Expansion across Central & Peninsular rainfed agrarian belts")
]

step_w = Emu(1780000)
gap = Emu(80000)
for idx, (title, desc) in enumerate(roadmap_steps):
    x_pos = Emu(600000 + idx * (1780000 + 80000))
    sbox = slide4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x_pos, Emu(5450000), step_w, Emu(800000))
    sbox.fill.solid()
    if idx == 0:
        sbox.fill.fore_color.rgb = RGBColor(240, 253, 244) # light green
        sbox.line.color.rgb = COLOR_GREEN
        sbox.line.width = Pt(1.5)
    else:
        sbox.fill.fore_color.rgb = COLOR_WHITE
        sbox.line.color.rgb = COLOR_CARD_BORDER
        sbox.line.width = Pt(1)
        
    tf = sbox.text_frame
    tf.word_wrap = True
    p_t = tf.paragraphs[0]
    p_t.alignment = PP_ALIGN.LEFT
    r_t = p_t.add_run()
    r_t.text = title
    r_t.font.bold = True
    r_t.font.size = Pt(7.5)
    r_t.font.color.rgb = COLOR_GREEN if idx == 0 else COLOR_TEXT_DARK
    
    p_d = tf.add_paragraph()
    p_d.alignment = PP_ALIGN.LEFT
    r_d = p_d.add_run()
    r_d.text = desc
    r_d.font.size = Pt(6.8)
    r_d.font.color.rgb = COLOR_TEXT_MUTED

print("Slide 4 updated successfully.")

# ==========================================
# SLIDE 5: IMPACT AND BENEFITS
# ==========================================
slide5 = prs.slides[4]
print("Processing Slide 5...")
update_header_badge(slide5, "TextBox 39")

# In Slide 5 lower area (top=5050000, height=1300000):
# Left: Decision Value Chain
# Right: Scalability & Verification Evidence Strip
card_vc = slide5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Emu(457200), Emu(5050000), Emu(6300000), Emu(1300000))
card_vc.fill.solid()
card_vc.fill.fore_color.rgb = COLOR_LIGHT_BG
card_vc.line.color.rgb = COLOR_CARD_BORDER
card_vc.line.width = Pt(1)

tb_vc = slide5.shapes.add_textbox(Emu(550000), Emu(5080000), Emu(6100000), Emu(240000))
p_vc = tb_vc.text_frame.paragraphs[0]
r_vc = p_vc.add_run()
r_vc.text = "FARM-LEVEL DECISION VALUE CHAIN"
r_vc.font.bold = True
r_vc.font.size = Pt(8.5)
r_vc.font.color.rgb = COLOR_ACCENT_BLUE

chain_steps = [
    ("Hyperlocal S2S Intelligence", "5-10km rainfall anomaly & break-spell risk 7-28d ahead"),
    ("Scientific Sowing Timing", "Pre-empts dry spell seedling desiccation & fertilizer washout"),
    ("Contingent Resilience", "Automatic guidance to pivot to short-duration hardy cultivars"),
    ("Preserved Farmer Capital", "Protects seed investment & lowers weather-related debt cycle")
]

for idx, (head, sub) in enumerate(chain_steps):
    cbox = slide5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Emu(550000), Emu(5340000 + idx * 240000), Emu(6115000), Emu(210000))
    cbox.fill.solid()
    cbox.fill.fore_color.rgb = COLOR_WHITE
    cbox.line.color.rgb = COLOR_CARD_BORDER
    cbox.line.width = Pt(0.75)
    
    tf = cbox.text_frame
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.LEFT
    r1 = p.add_run()
    r1.text = f"• {head}: "
    r1.font.bold = True
    r1.font.size = Pt(7.2)
    r1.font.color.rgb = COLOR_TEXT_DARK
    r2 = p.add_run()
    r2.text = sub
    r2.font.size = Pt(7)
    r2.font.color.rgb = COLOR_TEXT_MUTED

# Right: Scalability Architecture Pillars
card_sc = slide5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Emu(6900000), Emu(5050000), Emu(4834800), Emu(1300000))
card_sc.fill.solid()
card_sc.fill.fore_color.rgb = COLOR_LIGHT_BG
card_sc.line.color.rgb = COLOR_CARD_BORDER
card_sc.line.width = Pt(1)

tb_sc = slide5.shapes.add_textbox(Emu(7020000), Emu(5080000), Emu(4600000), Emu(240000))
p_sc = tb_sc.text_frame.paragraphs[0]
r_sc = p_sc.add_run()
r_sc.text = "SYSTEM SCALABILITY & VERIFIED IMPLEMENTATION"
r_sc.font.bold = True
r_sc.font.size = Pt(8.5)
r_sc.font.color.rgb = COLOR_GREEN

scalability_pillars = [
    ("Modular Architecture", "Decoupled REST APIs enable seamless addition of new blocks/districts"),
    ("Dynamic Agronomy", "Pluggable ICAR-CRIDA crop profiles support any regional Kharif cultivar"),
    ("Centralized i18n", "7 languages with 231 keys per dictionary; rapid dialect onboarding"),
    ("Verified Codebase", "60/60 Pytest backend tests & 42/42 mobile viewport matrix passed")
]

for idx, (head, sub) in enumerate(scalability_pillars):
    sbox = slide5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Emu(7020000), Emu(5340000 + idx * 240000), Emu(4600000), Emu(210000))
    sbox.fill.solid()
    sbox.fill.fore_color.rgb = COLOR_WHITE
    sbox.line.color.rgb = COLOR_CARD_BORDER
    sbox.line.width = Pt(0.75)
    
    tf = sbox.text_frame
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.LEFT
    r1 = p.add_run()
    r1.text = f"• {head}: "
    r1.font.bold = True
    r1.font.size = Pt(7.2)
    r1.font.color.rgb = COLOR_TEXT_DARK
    r2 = p.add_run()
    r2.text = sub
    r2.font.size = Pt(7)
    r2.font.color.rgb = COLOR_TEXT_MUTED

print("Slide 5 updated successfully.")

# ==========================================
# SLIDE 6: RESEARCH AND REFERENCES
# ==========================================
slide6 = prs.slides[5]
print("Processing Slide 6...")
update_header_badge(slide6, "TextBox 16")

# In Slide 6 lower area (top=5150000, height=1200000):
# Explicit Scientific Limitations, Data Provenance & Governance Card
card_gov = slide6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Emu(457200), Emu(5150000), Emu(11277600), Emu(1200000))
card_gov.fill.solid()
card_gov.fill.fore_color.rgb = COLOR_LIGHT_BG
card_gov.line.color.rgb = COLOR_CARD_BORDER
card_gov.line.width = Pt(1)

tb_gov = slide6.shapes.add_textbox(Emu(600000), Emu(5180000), Emu(11000000), Emu(240000))
p_gv = tb_gov.text_frame.paragraphs[0]
r_gv = p_gv.add_run()
r_gv.text = "SCIENTIFIC INTEGRITY, PROTOTYPE BOUNDARIES & ETHICAL TRANSPARENCY"
r_gv.font.bold = True
r_gv.font.size = Pt(8.5)
r_gv.font.color.rgb = COLOR_ORANGE

gov_notes = [
    ("NCMRWF Connectivity", "NCMRWF upper-air variables are represented via climatological benchmark fallback in prototype; operational high-bandwidth NCMRWF data socket is a future deployment step."),
    ("IMD Onset Advisory", "IMD-referenced monsoon onset criteria adapted within the VarshaSetu hyperlocal forecasting framework; VarshaSetu does not issue an official statutory IMD onset declaration."),
    ("Rural Messaging Gateway", "SMS/WhatsApp delivery workflow demonstrated through a sandboxed simulation gateway without commercial telecom transmission or live carrier billing."),
    ("Cartographic Boundaries", "Demonstration boundaries are approximate visualization bounding-boxes, not official Survey of India cadastral administrative boundaries.")
]

for idx, (title, note) in enumerate(gov_notes):
    gbox = slide6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Emu(600000), Emu(5440000 + idx * 215000), Emu(11000000), Emu(190000))
    gbox.fill.solid()
    gbox.fill.fore_color.rgb = COLOR_WHITE
    gbox.line.color.rgb = COLOR_CARD_BORDER
    gbox.line.width = Pt(0.75)
    
    tf = gbox.text_frame
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.LEFT
    r1 = p.add_run()
    r1.text = f"• {title}: "
    r1.font.bold = True
    r1.font.size = Pt(7.2)
    r1.font.color.rgb = COLOR_ACCENT_BLUE if idx == 0 else COLOR_TEXT_DARK
    
    r2 = p.add_run()
    r2.text = note
    r2.font.bold = False
    r2.font.size = Pt(7)
    r2.font.color.rgb = COLOR_TEXT_MUTED

print("Slide 6 updated successfully.")

prs.save(OUT_PPTX)
print(f"Saved enhanced presentation to {OUT_PPTX}")
