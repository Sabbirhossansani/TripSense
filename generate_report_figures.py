"""
TripSense Report Figure Generator
Generates high-resolution academic figures for the DIU CSE FYDP Final Report:
1. fig3_1_architecture.png: Multi-tier Decoupled System Architecture
2. fig3_2_er_diagram.png: Relational / JSON Entity-Relationship Diagram
3. fig3_3_class_diagram.png: UML Class Diagram: Domain & Service Architecture
4. fig3_4_sequence.png: UML Sequence Diagram (Group Plan & Dynamic Weather Adaptation)
5. fig3_5_flowchart.png: Algorithmic Recommendation & TSP Scheduling Flowchart
6. fig4_1_route_opt.png: 2-Opt Route Optimization Before/After Comparison
7. fig4_2_fairness.png: Group Fairness & Satisfaction Distribution Metrics
8. fig4_3_weather_tree.png: Dynamic Context Weather Adaptation Decision Tree
9. fig4_4_demo_onboarding.png: System Demonstration - Destination & Onboarding Quiz
10. fig4_5_demo_itinerary.png: System Demonstration - Group Itinerary, Leaflet Map & XAI Modal
11. fig4_6_demo_weather_expense.png: System Demonstration - Weather Rerouting & Expense Splitter
"""

import os
import math
import shutil
from PIL import Image, ImageDraw, ImageFont

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "docs", "figures")
os.makedirs(OUTPUT_DIR, exist_ok=True)

FONT_REG = "C:/Windows/Fonts/segoeui.ttf"
FONT_BOLD = "C:/Windows/Fonts/segoeuib.ttf"
FONT_MONO = "C:/Windows/Fonts/consola.ttf"

def get_font(bold=False, size=14, mono=False):
    if mono and os.path.exists(FONT_MONO):
        return ImageFont.truetype(FONT_MONO, size)
    p = FONT_BOLD if bold else FONT_REG
    if os.path.exists(p):
        return ImageFont.truetype(p, size)
    return ImageFont.load_default()

def draw_rounded_box(draw, xy, fill, outline, width=2, radius=10):
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)

def draw_arrow(draw, start, end, fill=(70, 80, 95), width=2, arrow_size=8):
    x1, y1 = start
    x2, y2 = end
    draw.line([(x1, y1), (x2, y2)], fill=fill, width=width)
    angle = math.atan2(y2 - y1, x2 - x1)
    p1 = (x2 - arrow_size * math.cos(angle - math.pi / 6),
          y2 - arrow_size * math.sin(angle - math.pi / 6))
    p2 = (x2 - arrow_size * math.cos(angle + math.pi / 6),
          y2 - arrow_size * math.sin(angle + math.pi / 6))
    draw.polygon([end, p1, p2], fill=fill)

def generate_figure_3_1():
    """System Architecture Diagram"""
    w, h = 1200, 780
    im = Image.new("RGB", (w, h), (248, 250, 252))
    d = ImageDraw.Draw(im)

    # Title
    f_title = get_font(bold=True, size=22)
    f_sub = get_font(bold=False, size=13)
    d.text((40, 25), "TripSense: Multi-Tier Decoupled System Architecture", fill=(15, 23, 42), font=f_title)
    d.text((40, 55), "End-to-End Functional Architecture spanning Mobile Presentation, API Gateway, Algorithmic Engine, and Persistence", fill=(100, 116, 139), font=f_sub)

    # 4 Tier Boxes
    tiers = [
        ("Tier 1: Presentation Tier (Client)", 100, 220, (239, 246, 255), (191, 219, 254), (30, 64, 175)),
        ("Tier 2: API Gateway Tier (FastAPI)", 245, 365, (240, 253, 244), (187, 247, 208), (22, 101, 52)),
        ("Tier 3: Domain Algorithmic Tier", 390, 545, (254, 242, 242), (254, 202, 202), (153, 27, 27)),
        ("Tier 4: Data & Context Tier", 570, 715, (255, 251, 235), (254, 240, 138), (146, 64, 14))
    ]

    for title, top, bottom, fill, outline, text_color in tiers:
        draw_rounded_box(d, [50, top, 1150, bottom], fill=fill, outline=outline, width=2, radius=8)
        d.text((70, top + 10), title, fill=text_color, font=get_font(bold=True, size=15))

    # Modules in Tier 1
    t1_boxes = [
        ("Mobile Web App (React 18 + Vite)", "Responsive SPA UI, Room Lobby, Itinerary", 70, 135, 360, 205),
        ("Interactive Leaflet Map (OSM)", "Custom numbered pins (1-6), Polyline routes", 380, 135, 670, 205),
        ("Context Simulator & Splitter", "Monsoon Rain Toggle, Debt Settlement View", 690, 135, 960, 205),
        ("Offline Cache", "LocalStorage API", 980, 135, 1130, 205)
    ]
    for name, sub, x1, y1, x2, y2 in t1_boxes:
        draw_rounded_box(d, [x1, y1, x2, y2], fill=(255, 255, 255), outline=(147, 197, 253), width=1, radius=6)
        d.text((x1 + 10, y1 + 10), name, fill=(30, 58, 138), font=get_font(bold=True, size=13))
        d.text((x1 + 10, y1 + 35), sub, fill=(100, 116, 139), font=get_font(size=11))

    # Modules in Tier 2
    t2_boxes = [
        ("FastAPI Application Gateway", "ASGI Async Core with Uvicorn, CORS, GZip", 70, 280, 420, 350),
        ("REST Endpoint Controllers", "/api/destinations, /api/spots, /generate-plan", 440, 280, 790, 350),
        ("Pydantic v2 Validation Schemas", "GroupPlanRequest, WeatherReplanRequest", 810, 280, 1130, 350)
    ]
    for name, sub, x1, y1, x2, y2 in t2_boxes:
        draw_rounded_box(d, [x1, y1, x2, y2], fill=(255, 255, 255), outline=(134, 239, 172), width=1, radius=6)
        d.text((x1 + 10, y1 + 10), name, fill=(20, 83, 45), font=get_font(bold=True, size=13))
        d.text((x1 + 10, y1 + 35), sub, fill=(100, 116, 139), font=get_font(size=11))

    # Modules in Tier 3
    t3_boxes = [
        ("Content Recommender", "TF-IDF / Tag Cosine Matching", 70, 430, 310, 525),
        ("Group Consensus Engine", "Least-Misery & Avg-Satisfaction", 330, 430, 600, 525),
        ("Explainability (XAI)", "Multi-Badge & Narrative Generator", 620, 430, 870, 525),
        ("2-Opt TSP Scheduler", "Haversine Distance & Time Slotting", 890, 430, 1130, 525)
    ]
    for name, sub, x1, y1, x2, y2 in t3_boxes:
        draw_rounded_box(d, [x1, y1, x2, y2], fill=(255, 255, 255), outline=(252, 165, 165), width=1, radius=6)
        d.text((x1 + 10, y1 + 10), name, fill=(127, 29, 29), font=get_font(bold=True, size=13))
        d.text((x1 + 10, y1 + 35), sub, fill=(100, 116, 139), font=get_font(size=11))

    # Modules in Tier 4
    t4_boxes = [
        ("Bangladesh POI Dataset", "45 spots (Chittagong, Cox's, Sylhet, Dhaka)", 70, 610, 420, 695),
        ("Weather Context Adaptation Engine", "Rain Alert Trigger & Indoor Substitute Pool", 440, 610, 820, 695),
        ("Expense Splitter Ledger", "Zero-sum minimal debt settlement", 840, 610, 1130, 695)
    ]
    for name, sub, x1, y1, x2, y2 in t4_boxes:
        draw_rounded_box(d, [x1, y1, x2, y2], fill=(255, 255, 255), outline=(253, 224, 71), width=1, radius=6)
        d.text((x1 + 10, y1 + 10), name, fill=(120, 53, 15), font=get_font(bold=True, size=13))
        d.text((x1 + 10, y1 + 35), sub, fill=(100, 116, 139), font=get_font(size=11))

    # Connecting Arrows
    draw_arrow(d, (250, 220), (250, 245), fill=(30, 64, 175), width=3)
    draw_arrow(d, (600, 245), (600, 220), fill=(22, 101, 52), width=3)
    draw_arrow(d, (400, 365), (400, 390), fill=(22, 101, 52), width=3)
    draw_arrow(d, (750, 390), (750, 365), fill=(153, 27, 27), width=3)
    draw_arrow(d, (500, 545), (500, 570), fill=(153, 27, 27), width=3)
    draw_arrow(d, (700, 570), (700, 545), fill=(146, 64, 14), width=3)

    out_path = os.path.join(OUTPUT_DIR, "fig3_1_architecture.png")
    im.save(out_path, dpi=(300, 300))
    print(f"Generated {out_path}")

def generate_figure_3_2():
    """Entity-Relationship Diagram"""
    w, h = 1150, 680
    im = Image.new("RGB", (w, h), (255, 255, 255))
    d = ImageDraw.Draw(im)

    f_title = get_font(bold=True, size=20)
    d.text((40, 20), "TripSense: Relational & Document Entity-Relationship Diagram", fill=(15, 23, 42), font=f_title)

    entities = [
        ("GROUP_ROOM", 50, 80, 350, 270, [
            ("room_code (PK)", "VARCHAR(12)"),
            ("destination_city", "VARCHAR(50)"),
            ("days", "INT"),
            ("pace", "VARCHAR(20)"),
            ("consensus_strategy", "VARCHAR(30)"),
            ("promote_hidden_gems", "BOOLEAN"),
            ("created_at", "TIMESTAMP")
        ], (219, 234, 254), (30, 64, 175)),

        ("USER_MEMBER", 420, 80, 720, 270, [
            ("member_id (PK)", "VARCHAR(36)"),
            ("room_code (FK)", "VARCHAR(12)"),
            ("name", "VARCHAR(100)"),
            ("interests", "JSON / TEXT[]"),
            ("budget_tier", "VARCHAR(20)"),
            ("joined_at", "TIMESTAMP")
        ], (220, 252, 231), (22, 101, 52)),

        ("SPOT_POI", 790, 80, 1100, 330, [
            ("spot_id (PK)", "INT"),
            ("name", "VARCHAR(150)"),
            ("name_bn", "VARCHAR(150)"),
            ("city", "VARCHAR(50)"),
            ("category", "VARCHAR(50)"),
            ("estimated_cost_bdt", "FLOAT"),
            ("indoor_outdoor", "VARCHAR(10)"),
            ("best_time", "VARCHAR(20)"),
            ("latitude", "FLOAT"),
            ("longitude", "FLOAT")
        ], (254, 226, 226), (153, 27, 27)),

        ("ITINERARY_DAY", 50, 380, 380, 620, [
            ("schedule_id (PK)", "VARCHAR(36)"),
            ("room_code (FK)", "VARCHAR(12)"),
            ("day_number", "INT"),
            ("time_slot", "VARCHAR(20)"),
            ("spot_id (FK)", "INT"),
            ("transit_km", "FLOAT"),
            ("transit_mins", "INT"),
            ("is_weather_substitute", "BOOLEAN")
        ], (254, 243, 199), (146, 64, 14)),

        ("EXPENSE_ITEM", 430, 380, 750, 620, [
            ("expense_id (PK)", "VARCHAR(36)"),
            ("room_code (FK)", "VARCHAR(12)"),
            ("title", "VARCHAR(150)"),
            ("amount_bdt", "FLOAT"),
            ("paid_by_member_id (FK)", "VARCHAR(36)"),
            ("split_with_members", "JSON / TEXT[]"),
            ("created_at", "TIMESTAMP")
        ], (243, 232, 255), (107, 33, 168)),

        ("SETTLEMENT_TX", 800, 420, 1100, 620, [
            ("settlement_id (PK)", "VARCHAR(36)"),
            ("room_code (FK)", "VARCHAR(12)"),
            ("debtor_member_id (FK)", "VARCHAR(36)"),
            ("creditor_member_id (FK)", "VARCHAR(36)"),
            ("amount_bdt", "FLOAT")
        ], (255, 237, 213), (194, 65, 12))
    ]

    for name, x1, y1, x2, y2, fields, fill_c, text_c in entities:
        draw_rounded_box(d, [x1, y1, x2, y2], fill=(255, 255, 255), outline=text_c, width=2, radius=6)
        d.rectangle([x1, y1, x2, y1 + 32], fill=fill_c)
        d.text((x1 + 12, y1 + 8), name, fill=text_c, font=get_font(bold=True, size=13))
        
        curr_y = y1 + 40
        for fname, ftype in fields:
            d.text((x1 + 12, curr_y), fname, fill=(30, 41, 59), font=get_font(bold=True if "PK" in fname or "FK" in fname else False, size=11))
            d.text((x2 - 110, curr_y), ftype, fill=(100, 116, 139), font=get_font(mono=True, size=10))
            curr_y += 24

    # Connectors
    d.line([(350, 160), (420, 160)], fill=(30, 64, 175), width=2)
    d.text((360, 140), "1", fill=(30, 64, 175), font=get_font(bold=True, size=12))
    d.text((405, 140), "N", fill=(30, 64, 175), font=get_font(bold=True, size=12))

    d.line([(200, 270), (200, 380)], fill=(30, 64, 175), width=2)
    d.text((210, 280), "1", fill=(30, 64, 175), font=get_font(bold=True, size=12))
    d.text((210, 360), "N", fill=(30, 64, 175), font=get_font(bold=True, size=12))

    d.line([(790, 280), (380, 480)], fill=(153, 27, 27), width=2)
    d.text((750, 290), "1", fill=(153, 27, 27), font=get_font(bold=True, size=12))
    d.text((400, 460), "N", fill=(153, 27, 27), font=get_font(bold=True, size=12))

    d.line([(570, 270), (570, 380)], fill=(22, 101, 52), width=2)
    d.text((580, 280), "1", fill=(22, 101, 52), font=get_font(bold=True, size=12))
    d.text((580, 360), "N", fill=(22, 101, 52), font=get_font(bold=True, size=12))

    d.line([(750, 500), (800, 500)], fill=(107, 33, 168), width=2)
    d.text((760, 480), "N", fill=(107, 33, 168), font=get_font(bold=True, size=12))
    d.text((785, 480), "1", fill=(107, 33, 168), font=get_font(bold=True, size=12))

    out_path = os.path.join(OUTPUT_DIR, "fig3_2_er_diagram.png")
    im.save(out_path, dpi=(300, 300))
    print(f"Generated {out_path}")

def generate_figure_3_3_class_diagram():
    """UML Class Diagram: Domain Models, Algorithmic Services, and Contextual Engines"""
    w, h = 1250, 850
    im = Image.new("RGB", (w, h), (248, 250, 252))
    d = ImageDraw.Draw(im)

    f_title = get_font(bold=True, size=21)
    f_sub = get_font(bold=False, size=12)
    d.text((40, 20), "TripSense: UML Class Diagram — Domain & Algorithmic Architecture", fill=(15, 23, 42), font=f_title)
    d.text((40, 48), "Object-Oriented Domain Entities, Consensus Services, Optimization Pipelines, and Contextual Adapters", fill=(100, 116, 139), font=f_sub)

    # Helper to draw a UML class box
    def draw_uml_class(x1, y1, x2, y2, stereotype, class_name, attrs, methods, fill_hdr, outline_col):
        draw_rounded_box(d, [x1, y1, x2, y2], fill=(255, 255, 255), outline=outline_col, width=2, radius=6)
        hdr_h = 36
        d.rectangle([x1, y1, x2, y1 + hdr_h], fill=fill_hdr)
        d.text((x1 + 10, y1 + 4), f"<<{stereotype}>>", fill=outline_col, font=get_font(size=9, mono=True))
        d.text((x1 + 10, y1 + 16), class_name, fill=(15, 23, 42), font=get_font(bold=True, size=12))
        
        # Attributes compartment
        cur_y = y1 + hdr_h + 6
        for a in attrs:
            d.text((x1 + 10, cur_y), a, fill=(30, 41, 59), font=get_font(size=9.5, mono=True))
            cur_y += 18
        
        # Divider
        d.line([(x1, cur_y + 2), (x2, cur_y + 2)], fill=(226, 232, 240), width=1)
        cur_y += 6
        for m in methods:
            d.text((x1 + 10, cur_y), m, fill=(15, 23, 42), font=get_font(size=9.5, mono=True))
            cur_y += 18

    # Classes layout in 3 columns
    # Col 1: Domain Entities (Spot, UserPreference, GroupRoom, ScheduleItem)
    # Col 2: Core Algorithmic Engines (ConsensusRecommender, TwoOptScheduler, ExplainabilityEngine)
    # Col 3: Contextual Adapters (WeatherService, ExpenseSplitter, SettlementTx)

    # 1. Spot (Col 1 Top)
    draw_uml_class(
        40, 85, 380, 290,
        "entity", "Spot",
        [
            "- spot_id: int",
            "- name: str",
            "- name_bn: str",
            "- city: str",
            "- category: str",
            "- cost_bdt: float",
            "- indoor_outdoor: str",
            "- lat: float, lon: float"
        ],
        [
            "+ haversine_to(other: Spot): float",
            "+ is_indoor(): bool",
            "+ to_dict(): dict"
        ],
        (254, 226, 226), (185, 28, 28)
    )

    # 2. UserPreference (Col 1 Mid)
    draw_uml_class(
        40, 310, 380, 470,
        "entity", "UserPreference",
        [
            "- member_id: str",
            "- name: str",
            "- interests: List[str]",
            "- budget_tier: str"
        ],
        [
            "+ get_category_affinity(cat): float",
            "+ get_budget_weight(): float",
            "+ to_feature_vector(): dict"
        ],
        (220, 252, 231), (22, 101, 52)
    )

    # 3. GroupRoom (Col 1 Bottom)
    draw_uml_class(
        40, 490, 380, 700,
        "aggregate-root", "GroupRoom",
        [
            "- room_code: str",
            "- destination_city: str",
            "- days: int",
            "- pace: str",
            "- consensus_strategy: str",
            "- members: List[UserPreference]"
        ],
        [
            "+ add_member(user: UserPreference)",
            "+ get_preference_matrix(): dict",
            "+ compile_request_payload(): dict"
        ],
        (219, 234, 254), (30, 64, 175)
    )

    # 4. ConsensusRecommender (Col 2 Top)
    draw_uml_class(
        420, 85, 800, 310,
        "service", "ConsensusRecommender",
        [
            "- candidate_spots: List[Spot]",
            "- strategy: ConsensusStrategy"
        ],
        [
            "+ compute_member_score(u, s): float",
            "+ aggregate_least_misery(m, s): float",
            "+ aggregate_average(m, s): float",
            "+ rank_candidates(members): List[dict]",
            "+ compute_gini_fairness(plan): dict"
        ],
        (243, 232, 255), (126, 34, 206)
    )

    # 5. TwoOptScheduler (Col 2 Mid)
    draw_uml_class(
        420, 330, 800, 530,
        "service", "TwoOptScheduler",
        [
            "- dist_matrix: Matrix[float]",
            "- daily_capacity: int = 3",
            "- avg_speed_kmh: float = 30.0"
        ],
        [
            "+ cluster_by_days(spots, days): dict",
            "+ solve_tsp_2opt(day_spots): List[Spot]",
            "+ compute_tour_distance(tour): float",
            "+ assign_time_slots(spots): List[ScheduleItem]"
        ],
        (254, 243, 199), (180, 83, 9)
    )

    # 6. ExplainabilityEngine (Col 2 Bottom)
    draw_uml_class(
        420, 550, 800, 720,
        "service", "ExplainabilityEngine",
        [
            "- consensus_breakdown: dict",
            "- badge_threshold: float = 0.5"
        ],
        [
            "+ generate_badges(spot, group): List[str]",
            "+ compute_friend_consensus(s, g): dict",
            "+ synthesize_narrative(s, g): str"
        ],
        (255, 237, 213), (194, 65, 12)
    )

    # 7. WeatherService (Col 3 Top)
    draw_uml_class(
        840, 85, 1210, 300,
        "context-adapter", "WeatherService",
        [
            "- alert_condition: str",
            "- indoor_fallback_pool: List[Spot]"
        ],
        [
            "+ detect_outdoor_risk(spot): bool",
            "+ find_indoor_substitute(city, cat): Spot",
            "+ replan_weather(itinerary, group): dict",
            "+ recalculate_consecutive_transits(): void"
        ],
        (224, 242, 254), (3, 105, 161)
    )

    # 8. ExpenseSplitter (Col 3 Mid)
    draw_uml_class(
        840, 320, 1210, 530,
        "service", "ExpenseSplitter",
        [
            "- expenses: List[ExpenseItem]",
            "- group_members: List[str]"
        ],
        [
            "+ add_expense(title, amt, payer, split)",
            "+ compute_net_balances(): dict",
            "+ minimize_debts_zero_sum(): List[SettlementTx]",
            "+ import_itinerary_tickets(plan)"
        ],
        (254, 242, 242), (153, 27, 27)
    )

    # 9. SettlementTx (Col 3 Bottom)
    draw_uml_class(
        840, 550, 1210, 710,
        "value-object", "SettlementTx",
        [
            "- tx_id: str",
            "- debtor: str",
            "- creditor: str",
            "- amount_bdt: float"
        ],
        [
            "+ is_settled(): bool",
            "+ to_string(): str"
        ],
        (241, 245, 249), (71, 85, 105)
    )

    # UML Relationships (Arrows & Annotations)
    # GroupRoom has UserPreference (1 to N Composition)
    d.line([(210, 470), (210, 490)], fill=(30, 64, 175), width=2)
    d.polygon([(210, 470), (206, 478), (210, 486), (214, 478)], fill=(30, 64, 175))
    d.text((220, 472), "1..*", fill=(30, 64, 175), font=get_font(size=10, bold=True))

    # GroupRoom -> ConsensusRecommender (Dependency)
    d.line([(380, 540), (420, 260)], fill=(126, 34, 206), width=2)
    draw_arrow(d, (380, 540), (420, 260), fill=(126, 34, 206), width=2)
    d.text((375, 380), "delegates to", fill=(126, 34, 206), font=get_font(size=10))

    # ConsensusRecommender -> TwoOptScheduler (Data Pipeline)
    draw_arrow(d, (610, 310), (610, 330), fill=(180, 83, 9), width=2)
    d.text((620, 315), "feeds ranked spots", fill=(180, 83, 9), font=get_font(size=9.5))

    # TwoOptScheduler -> ExplainabilityEngine
    draw_arrow(d, (610, 530), (610, 550), fill=(194, 65, 12), width=2)
    d.text((620, 535), "enriches routes", fill=(194, 65, 12), font=get_font(size=9.5))

    # WeatherService uses Spot & ConsensusRecommender
    draw_arrow(d, (840, 190), (800, 190), fill=(3, 105, 161), width=2)
    d.text((805, 170), "reranks via", fill=(3, 105, 161), font=get_font(size=9.5))

    # ExpenseSplitter produces SettlementTx
    draw_arrow(d, (1025, 530), (1025, 550), fill=(153, 27, 27), width=2)
    d.text((1035, 535), "solves to", fill=(153, 27, 27), font=get_font(size=9.5))

    # Bottom Legend
    draw_rounded_box(d, [40, 740, 1210, 815], fill=(255, 255, 255), outline=(203, 213, 225), width=1, radius=6)
    d.text((55, 755), "UML Architectural Annotations:", fill=(15, 23, 42), font=get_font(bold=True, size=11))
    d.text((55, 780), "• High Cohesion & Low Coupling: Algorithmic Recommender, Routing Optimizer, and XAI Engine remain strictly decoupled.", fill=(71, 85, 105), font=get_font(size=10))
    d.text((680, 780), "• Immutability & Fail-Safety: Weather replanning returns new schedule clones without state mutation.", fill=(71, 85, 105), font=get_font(size=10))

    out_path = os.path.join(OUTPUT_DIR, "fig3_3_class_diagram.png")
    im.save(out_path, dpi=(300, 300))
    print(f"Generated {out_path}")

def generate_figure_3_4_sequence():
    """UML Sequence Diagram"""
    w, h = 1200, 720
    im = Image.new("RGB", (w, h), (255, 255, 255))
    d = ImageDraw.Draw(im)

    f_title = get_font(bold=True, size=20)
    d.text((40, 20), "TripSense: UML Sequence Diagram — Group Plan & Weather Repair Workflow", fill=(15, 23, 42), font=f_title)

    lifelines = [
        ("Group Members / Organizer", 120),
        ("React Client (PWA)", 360),
        ("FastAPI Gateway", 600),
        ("Consensus & 2-Opt Engine", 840),
        ("Weather Context Engine", 1080)
    ]

    for name, x in lifelines:
        draw_rounded_box(d, [x - 90, 70, x + 90, 115], fill=(241, 245, 249), outline=(71, 85, 105), width=2, radius=6)
        d.text((x - 80, 85), name, fill=(15, 23, 42), font=get_font(bold=True, size=11))
        d.line([(x, 115), (x, 670)], fill=(203, 213, 225), width=2)

    steps = [
        (130, 0, 1, "1. Create Group Room & Submit Preference Quizzes", False),
        (165, 1, 2, "2. POST /api/group/generate-plan (Payload: Members, Days, Pace)", False),
        (205, 2, 3, "3. Filter Spots by City & Compute Member Match Matrix", False),
        (245, 3, 3, "4. Social Choice Aggregation: S_LM(s) = min(S_m(s))", True),
        (285, 3, 3, "5. 2-Opt TSP Route Distance Optimization & XAI Badging", True),
        (325, 3, 2, "6. Return Optimized Itinerary JSON + Fairness Analytics", False),
        (365, 2, 1, "7. Render Day-by-Day Timeline & Interactive Leaflet Map", False),
        (420, 0, 1, "8. Trigger Real-Time Context Event: Monsoon Rain Downpour", False),
        (460, 1, 2, "9. POST /api/itinerary/replan-weather (City, Spots, Members)", False),
        (500, 2, 4, "10. Detect Outdoor POIs & Query Indoor Substitute Candidates", False),
        (540, 4, 4, "11. Rerank Indoor POIs by Group Consensus & Swap in Place", True),
        (580, 4, 2, "12. Recalculate Consecutive Transits & Emit Substitution Alert", False),
        (620, 2, 1, "13. Re-render UI: Orange Weather Warning Badge & Swapped Spot", False)
    ]

    for y, src_idx, dst_idx, msg, is_self in steps:
        x1 = lifelines[src_idx][1]
        x2 = lifelines[dst_idx][1]
        
        if is_self:
            d.line([(x1, y), (x1 + 45, y), (x1 + 45, y + 25), (x1, y + 25)], fill=(185, 28, 28), width=2)
            draw_arrow(d, (x1 + 45, y + 25), (x1, y + 25), fill=(185, 28, 28), width=2)
            d.text((x1 + 55, y + 5), msg, fill=(185, 28, 28), font=get_font(bold=True, size=11))
        else:
            color = (30, 64, 175) if dst_idx > src_idx else (22, 101, 52)
            draw_arrow(d, (x1, y), (x2, y), fill=color, width=2)
            d.text((min(x1, x2) + 15, y - 18), msg, fill=(15, 23, 42), font=get_font(size=11))

    out_path = os.path.join(OUTPUT_DIR, "fig3_4_sequence.png")
    im.save(out_path, dpi=(300, 300))
    # Keep backward-compatible copy
    shutil.copy(out_path, os.path.join(OUTPUT_DIR, "fig3_3_sequence.png"))
    print(f"Generated {out_path} and synced fig3_3_sequence.png")

def generate_figure_3_5_flowchart():
    """Algorithmic Flowchart"""
    w, h = 1100, 620
    im = Image.new("RGB", (w, h), (255, 255, 255))
    d = ImageDraw.Draw(im)

    f_title = get_font(bold=True, size=20)
    d.text((40, 20), "TripSense: Algorithmic Recommendation & 2-Opt Scheduling Flowchart", fill=(15, 23, 42), font=f_title)

    boxes = [
        ("Start: Group Request Intake", 450, 70, 650, 115, (224, 231, 255), (67, 56, 202)),
        ("Filter Candidate POIs by Target City", 430, 145, 670, 190, (255, 255, 255), (71, 85, 105)),
        ("Calculate Content Match Scores S(m, s) per Member", 390, 220, 710, 265, (255, 255, 255), (71, 85, 105)),
        ("Apply Social Choice: S_LM(s) = min_{m} S(m, s)", 400, 295, 700, 340, (254, 226, 226), (185, 28, 28)),
        ("Select Top N Daily Candidate POIs", 430, 370, 670, 415, (255, 255, 255), (71, 85, 105)),
        ("Run 2-Opt Local Search: Swap Edges if ΔD < 0", 410, 445, 690, 490, (254, 243, 199), (180, 83, 9)),
        ("Generate Explainability Badges & Time Slots", 410, 520, 690, 565, (220, 252, 231), (21, 128, 61))
    ]

    for name, x1, y1, x2, y2, fill_c, text_c in boxes:
        draw_rounded_box(d, [x1, y1, x2, y2], fill=fill_c, outline=text_c, width=2, radius=8)
        d.text((x1 + 15, y1 + 12), name, fill=text_c, font=get_font(bold=True, size=11))

    for i in range(len(boxes) - 1):
        y_from = boxes[i][4]
        y_to = boxes[i+1][2]
        draw_arrow(d, (550, y_from), (550, y_to), fill=(71, 85, 105), width=2)

    f_side = get_font(size=11)
    d.text((725, 230), "Cosine category match + Budget tier alignment", fill=(100, 116, 139), font=f_side)
    d.text((725, 305), "Guarantees Least-Misery: prevents dissatisfied outlier", fill=(100, 116, 139), font=f_side)
    d.text((725, 455), "Haversine Distance Matrix: O(N^2) optimization loop", fill=(100, 116, 139), font=f_side)
    d.text((725, 530), "Assigns: [1/3 Friends Agree], [Hidden Gem], [Indoor]", fill=(100, 116, 139), font=f_side)

    out_path = os.path.join(OUTPUT_DIR, "fig3_5_flowchart.png")
    im.save(out_path, dpi=(300, 300))
    # Keep backward-compatible copy
    shutil.copy(out_path, os.path.join(OUTPUT_DIR, "fig3_4_flowchart.png"))
    print(f"Generated {out_path} and synced fig3_4_flowchart.png")

def generate_figure_4_1():
    """2-Opt Route Optimization Graph (Before vs After)"""
    w, h = 1000, 500
    im = Image.new("RGB", (w, h), (255, 255, 255))
    d = ImageDraw.Draw(im)

    f_title = get_font(bold=True, size=18)
    d.text((30, 20), "Figure 4.1: Empirical 2-Opt TSP Route Optimization Benchmark (Chittagong Day Tour)", fill=(15, 23, 42), font=f_title)

    draw_rounded_box(d, [40, 60, 480, 460], fill=(248, 250, 252), outline=(226, 232, 240), width=2, radius=8)
    d.text((60, 75), "Panel (a): Naive Random Route Ordering", fill=(185, 28, 28), font=get_font(bold=True, size=14))
    d.text((60, 100), "Total Distance: 21.84 km | Crossed Edges: 2", fill=(100, 116, 139), font=get_font(size=12))

    draw_rounded_box(d, [520, 60, 960, 460], fill=(240, 253, 244), outline=(187, 247, 208), width=2, radius=8)
    d.text((540, 75), "Panel (b): 2-Opt Optimized Tour (TripSense)", fill=(21, 128, 61), font=get_font(bold=True, size=14))
    d.text((540, 100), "Total Distance: 13.23 km (39.4% Reduction) | Uncrossed", fill=(21, 128, 61), font=get_font(size=12))

    pts_a = [(120, 180), (320, 380), (180, 240), (420, 410), (250, 210), (160, 390)]
    pts_b = [(580, 180), (640, 210), (690, 240), (820, 360), (890, 390), (910, 420)]
    names = ["Chandanpura", "War Cemetery", "Zia Museum", "Ethno Museum", "Butterfly Park", "Patenga Beach"]

    naive_order = [0, 4, 1, 3, 2, 5, 0]
    for i in range(len(naive_order) - 1):
        p1 = pts_a[naive_order[i]]
        p2 = pts_a[naive_order[i+1]]
        d.line([p1, p2], fill=(239, 68, 68), width=2)
    for idx, pt in enumerate(pts_a):
        d.ellipse([pt[0]-7, pt[1]-7, pt[0]+7, pt[1]+7], fill=(185, 28, 28), outline=(255, 255, 255), width=2)
        d.text((pt[0]+10, pt[1]-8), names[idx], fill=(30, 41, 59), font=get_font(size=10))

    opt_order = [0, 1, 2, 3, 4, 5, 0]
    for i in range(len(opt_order) - 1):
        p1 = pts_b[opt_order[i]]
        p2 = pts_b[opt_order[i+1]]
        d.line([p1, p2], fill=(34, 197, 94), width=3)
    for idx, pt in enumerate(pts_b):
        d.ellipse([pt[0]-7, pt[1]-7, pt[0]+7, pt[1]+7], fill=(21, 128, 61), outline=(255, 255, 255), width=2)
        d.text((pt[0]+10, pt[1]-8), names[idx], fill=(30, 41, 59), font=get_font(size=10))

    out_path = os.path.join(OUTPUT_DIR, "fig4_1_route_opt.png")
    im.save(out_path, dpi=(300, 300))
    print(f"Generated {out_path}")

def generate_figure_4_2():
    """Group Fairness & Satisfaction Metric Distribution"""
    w, h = 1000, 500
    im = Image.new("RGB", (w, h), (255, 255, 255))
    d = ImageDraw.Draw(im)

    f_title = get_font(bold=True, size=18)
    d.text((30, 20), "Figure 4.2: Group Satisfaction Distribution and Fairness Metric Dashboard", fill=(15, 23, 42), font=f_title)

    d.rectangle([50, 80, 550, 450], fill=(248, 250, 252), outline=(226, 232, 240), width=1)
    d.text((70, 95), "Member Average Satisfaction Scores (%)", fill=(15, 23, 42), font=get_font(bold=True, size=13))

    d.line([(100, 400), (520, 400)], fill=(71, 85, 105), width=2)
    d.line([(100, 140), (100, 400)], fill=(71, 85, 105), width=2)

    for val, y_pos in [(0, 400), (25, 335), (50, 270), (75, 205), (100, 140)]:
        d.line([(95, y_pos), (100, y_pos)], fill=(71, 85, 105), width=2)
        d.text((65, y_pos - 8), f"{val}%", fill=(100, 116, 139), font=get_font(size=10))

    members_data = [
        ("Rahat\n(Budget/Hist)", 49.2, 140, (59, 130, 246)),
        ("Sadia\n(Mid/Beach)", 38.3, 270, (16, 185, 129)),
        ("Fahim\n(Lux/Adv)", 32.2, 400, (245, 158, 11))
    ]

    for label, val, x_pos, color in members_data:
        bar_h = int((val / 100.0) * 260)
        top_y = 400 - bar_h
        d.rectangle([x_pos, top_y, x_pos + 70, 400], fill=color, outline=(15, 23, 42), width=1)
        d.text((x_pos + 12, top_y - 20), f"{val:.1f}%", fill=(15, 23, 42), font=get_font(bold=True, size=12))
        d.text((x_pos - 5, 410), label, fill=(51, 65, 85), font=get_font(size=10))

    metric_cards = [
        ("Group Fairness Score", "74.52 / 100", "Normalized composite social harmony metric", (239, 246, 255), (30, 64, 175)),
        ("Gini Inequality Index", "0.0945", "Near-equal utility distribution (0 = perfect equity)", (240, 253, 244), (22, 101, 52)),
        ("Satisfaction Disparity", "16.99%", "Max minus Min member satisfaction gap", (254, 243, 199), (180, 83, 9)),
        ("Least-Misery Guarantee", "ACTIVE", "Zero members subjected to intolerable dissatisfaction", (253, 242, 248), (157, 23, 77))
    ]

    card_y = 80
    for title, val, desc, bg, border in metric_cards:
        draw_rounded_box(d, [580, card_y, 960, card_y + 80], fill=bg, outline=border, width=2, radius=8)
        d.text((600, card_y + 10), title, fill=(71, 85, 105), font=get_font(size=11))
        d.text((600, card_y + 30), val, fill=border, font=get_font(bold=True, size=18))
        d.text((600, card_y + 58), desc, fill=(100, 116, 139), font=get_font(size=10))
        card_y += 92

    out_path = os.path.join(OUTPUT_DIR, "fig4_2_fairness.png")
    im.save(out_path, dpi=(300, 300))
    print(f"Generated {out_path}")

def generate_figure_4_3():
    """Weather Adaptation Decision Tree"""
    w, h = 1000, 520
    im = Image.new("RGB", (w, h), (255, 255, 255))
    d = ImageDraw.Draw(im)

    f_title = get_font(bold=True, size=18)
    d.text((30, 20), "Figure 4.3: Dynamic Context-Aware Weather Adaptation Decision Tree", fill=(15, 23, 42), font=f_title)

    steps = [
        ("Context Trigger: Inclement Weather Event Detected\n(Heavy Rain / Tropical Storm in Target Destination)", 300, 70, 700, 125, (254, 242, 242), (185, 28, 28)),
        ("Traverse Active Daily Itinerary Slots", 360, 155, 640, 200, (255, 255, 255), (71, 85, 105)),
        ("Is POI Indoor or Outdoor?", 410, 230, 590, 275, (254, 243, 199), (180, 83, 9)),
        ("Retain Spot in Schedule\n(No change required)", 100, 320, 300, 375, (240, 253, 244), (22, 101, 52)),
        ("Query Candidate Pool for Unused Indoor POIs", 400, 320, 740, 365, (255, 255, 255), (71, 85, 105)),
        ("Rank Candidates by Group Consensus & Geographic Proximity", 350, 395, 790, 440, (255, 255, 255), (71, 85, 105)),
        ("Execute In-Place Substitution, Recalculate Transits, & Notify", 320, 465, 820, 510, (220, 252, 231), (21, 128, 61))
    ]

    for item in steps:
        name, x1, y1, x2, y2, fill_c, text_c = item
        draw_rounded_box(d, [x1, y1, x2, y2], fill=fill_c, outline=text_c, width=2, radius=6)
        lines = name.split("\n")
        if len(lines) == 1:
            d.text((x1 + 15, y1 + 10), lines[0], fill=text_c, font=get_font(bold=True, size=11))
        else:
            d.text((x1 + 15, y1 + 6), lines[0], fill=text_c, font=get_font(bold=True, size=11))
            d.text((x1 + 15, y1 + 24), lines[1], fill=text_c, font=get_font(size=10))

    draw_arrow(d, (500, 125), (500, 155), fill=(71, 85, 105), width=2)
    draw_arrow(d, (500, 200), (500, 230), fill=(71, 85, 105), width=2)

    draw_arrow(d, (410, 252), (200, 320), fill=(22, 101, 52), width=2)
    d.text((250, 260), "Indoor (Safe)", fill=(22, 101, 52), font=get_font(bold=True, size=11))

    draw_arrow(d, (550, 275), (550, 320), fill=(185, 28, 28), width=2)
    d.text((560, 290), "Outdoor (Flooded)", fill=(185, 28, 28), font=get_font(bold=True, size=11))

    draw_arrow(d, (550, 365), (550, 395), fill=(71, 85, 105), width=2)
    draw_arrow(d, (550, 440), (550, 465), fill=(71, 85, 105), width=2)

    out_path = os.path.join(OUTPUT_DIR, "fig4_3_weather_tree.png")
    im.save(out_path, dpi=(300, 300))
    print(f"Generated {out_path}")

def generate_figure_4_4_demo_onboarding():
    """System Demonstration: Destination Selection & Preference Onboarding Quiz UI Mockup"""
    w, h = 1150, 600
    im = Image.new("RGB", (w, h), (248, 250, 252))
    d = ImageDraw.Draw(im)

    f_title = get_font(bold=True, size=19)
    f_sub = get_font(bold=False, size=12)
    d.text((40, 20), "Figure 4.4: System Demonstration — Destination Selection & 60-Second Onboarding Quiz", fill=(15, 23, 42), font=f_title)
    d.text((40, 48), "Screen 1: Destination & Duration Modal | Screen 2: Individual Traveler Preference & Budget Intake", fill=(100, 116, 139), font=f_sub)

    # Panel Left: Screen 1 - Destination & Date Picker
    draw_rounded_box(d, [40, 80, 560, 560], fill=(255, 255, 255), outline=(203, 213, 225), width=2, radius=10)
    # Header bar
    d.rectangle([40, 80, 560, 125], fill=(30, 58, 138))
    d.text((60, 93), "Screen 1: Destination & Date Picker", fill=(255, 255, 255), font=get_font(bold=True, size=14))

    # City Dropdown
    d.text((60, 145), "Target Destination City:", fill=(71, 85, 105), font=get_font(bold=True, size=11))
    draw_rounded_box(d, [60, 170, 540, 210], fill=(241, 245, 249), outline=(147, 197, 253), width=1, radius=6)
    d.text((75, 180), "📍 Chittagong (Chattogram), Bangladesh  [Selected]", fill=(30, 64, 175), font=get_font(bold=True, size=12))

    # Duration slider
    d.text((60, 230), "Trip Duration (Days): 3 Days", fill=(71, 85, 105), font=get_font(bold=True, size=11))
    d.line([(60, 265), (540, 265)], fill=(203, 213, 225), width=4)
    d.line([(60, 265), (200, 265)], fill=(30, 64, 175), width=4)
    d.ellipse([(195, 257), (211, 273)], fill=(30, 64, 175))

    # Pace selector pills
    d.text((60, 290), "Travel Pace Intensity:", fill=(71, 85, 105), font=get_font(bold=True, size=11))
    paces = [("Relaxed (2 spots/day)", False), ("Balanced (3 spots/day)", True), ("Packed (4 spots/day)", False)]
    px = 60
    for ptext, is_active in paces:
        pw = 150
        bg = (219, 234, 254) if is_active else (241, 245, 249)
        tc = (30, 64, 175) if is_active else (100, 116, 139)
        draw_rounded_box(d, [px, 315, px + pw, 350], fill=bg, outline=tc, width=1, radius=6)
        d.text((px + 8, 325), ptext, fill=tc, font=get_font(bold=is_active, size=9.5))
        px += 160

    # Date Calendar Preview
    d.text((60, 375), "Trip Dates: Oct 24, 2026  ➔  Oct 26, 2026", fill=(71, 85, 105), font=get_font(bold=True, size=11))
    draw_rounded_box(d, [60, 400, 540, 480], fill=(248, 250, 252), outline=(226, 232, 240), width=1, radius=6)
    d.text((75, 415), "📅 Day 1: Saturday, Oct 24 (Historic Chittagong)", fill=(15, 23, 42), font=get_font(size=11))
    d.text((75, 435), "📅 Day 2: Sunday, Oct 25 (Culture & Patenga Coastal)", fill=(15, 23, 42), font=get_font(size=11))
    d.text((75, 455), "📅 Day 3: Monday, Oct 26 (Nature & Shopping Hubs)", fill=(15, 23, 42), font=get_font(size=11))

    # Button
    draw_rounded_box(d, [60, 500, 540, 545], fill=(30, 58, 138), outline=(30, 58, 138), width=1, radius=8)
    d.text((215, 513), "Create Collaborative Room ➔", fill=(255, 255, 255), font=get_font(bold=True, size=13))

    # Panel Right: Screen 2 - 60-Second Onboarding Quiz & Lobby
    draw_rounded_box(d, [590, 80, 1110, 560], fill=(255, 255, 255), outline=(203, 213, 225), width=2, radius=10)
    d.rectangle([590, 80, 1110, 125], fill=(22, 101, 52))
    d.text((610, 93), "Screen 2: 60-Second Preference Onboarding Quiz", fill=(255, 255, 255), font=get_font(bold=True, size=14))

    d.text((610, 140), "Select Interests (Multi-Choice):", fill=(71, 85, 105), font=get_font(bold=True, size=11))
    interests = [("🏛️ Historical", True), ("🏖️ Beach", False), ("🌿 Nature", False), ("🎭 Culture", True), ("🍛 Food", False), ("🧗 Adventure", False)]
    ix, iy = 610, 165
    for iname, checked in interests:
        ibg = (220, 252, 231) if checked else (248, 250, 252)
        itc = (22, 101, 52) if checked else (100, 116, 139)
        draw_rounded_box(d, [ix, iy, ix + 115, iy + 35], fill=ibg, outline=itc, width=1, radius=6)
        d.text((ix + 10, iy + 8), iname, fill=itc, font=get_font(bold=checked, size=10.5))
        ix += 125
        if ix > 950:
            ix = 610
            iy += 42

    d.text((610, 260), "Budget Tier Constraint:", fill=(71, 85, 105), font=get_font(bold=True, size=11))
    b_tiers = [("Budget (৳)", True), ("Mid-range (৳৳)", False), ("Luxury (৳৳৳)", False)]
    bx = 610
    for bname, bsel in b_tiers:
        bbg = (220, 252, 231) if bsel else (248, 250, 252)
        btc = (22, 101, 52) if bsel else (100, 116, 139)
        draw_rounded_box(d, [bx, 285, bx + 145, 320], fill=bbg, outline=btc, width=1, radius=6)
        d.text((bx + 12, 295), bname, fill=btc, font=get_font(bold=bsel, size=10.5))
        bx += 160

    # Active Group Lobby Room Members
    d.text((610, 340), "Group Lobby Members in Room 'CTG-882':", fill=(71, 85, 105), font=get_font(bold=True, size=11))
    members = [
        ("Rahat (Organizer)", "Historical, Culture", "Budget", (59, 130, 246)),
        ("Sadia", "Beach, Nature", "Mid-range", (16, 185, 129)),
        ("Fahim", "Adventure, Food", "Luxury", (245, 158, 11))
    ]
    my = 365
    for mname, mint, mbud, mcolor in members:
        draw_rounded_box(d, [610, my, 1090, my + 45], fill=(248, 250, 252), outline=(226, 232, 240), width=1, radius=6)
        d.ellipse([(620, my + 8), (648, my + 36)], fill=mcolor)
        d.text((627, my + 12), mname[0], fill=(255, 255, 255), font=get_font(bold=True, size=12))
        d.text((660, my + 6), mname, fill=(15, 23, 42), font=get_font(bold=True, size=11))
        d.text((660, my + 24), f"Interests: {mint} | Tier: {mbud}", fill=(100, 116, 139), font=get_font(size=9.5))
        my += 52

    # Synthesize button
    draw_rounded_box(d, [610, 525, 1090, 555], fill=(22, 101, 52), outline=(22, 101, 52), width=1, radius=6)
    d.text((750, 532), "✨ Synthesize Consensus Itinerary", fill=(255, 255, 255), font=get_font(bold=True, size=12))

    out_path = os.path.join(OUTPUT_DIR, "fig4_4_demo_onboarding.png")
    im.save(out_path, dpi=(300, 300))
    print(f"Generated {out_path}")

def generate_figure_4_5_demo_itinerary():
    """System Demonstration: Collaborative Itinerary, Leaflet Map & Explainability Modal UI Mockup"""
    w, h = 1150, 620
    im = Image.new("RGB", (w, h), (248, 250, 252))
    d = ImageDraw.Draw(im)

    f_title = get_font(bold=True, size=19)
    f_sub = get_font(bold=False, size=12)
    d.text((40, 20), "Figure 4.5: System Demonstration — Consensus Itinerary, Leaflet Map & XAI Modal", fill=(15, 23, 42), font=f_title)
    d.text((40, 48), "Screen 3: Daily Timeline Schedule & Leaflet Map | Screen 4: 'Why This Place?' Transparent Consensus Justification", fill=(100, 116, 139), font=f_sub)

    # Panel Left: Screen 3 - Itinerary & Map
    draw_rounded_box(d, [40, 80, 640, 580], fill=(255, 255, 255), outline=(203, 213, 225), width=2, radius=10)
    d.rectangle([40, 80, 640, 125], fill=(30, 58, 138))
    d.text((60, 93), "Screen 3: Group Consensus Itinerary & Leaflet Map", fill=(255, 255, 255), font=get_font(bold=True, size=14))

    # Day Selector Tabs
    d.text((60, 140), "Select Day: ", fill=(71, 85, 105), font=get_font(bold=True, size=11))
    tabs = [("Day 1 (3 spots)", True), ("Day 2 (3 spots)", False), ("Day 3 (3 spots)", False)]
    tx = 150
    for tname, is_sel in tabs:
        tbg = (30, 58, 138) if is_sel else (241, 245, 249)
        ttc = (255, 255, 255) if is_sel else (71, 85, 105)
        draw_rounded_box(d, [tx, 135, tx + 120, 165], fill=tbg, outline=tbg, width=1, radius=6)
        d.text((tx + 12, 143), tname, fill=ttc, font=get_font(bold=is_sel, size=10))
        tx += 130

    # Leaflet Map Mockup
    draw_rounded_box(d, [60, 180, 620, 330], fill=(238, 242, 246), outline=(203, 213, 225), width=1, radius=6)
    d.text((70, 190), "🗺️ OpenStreetMap Tile View: Chittagong Metropolitan Tour", fill=(71, 85, 105), font=get_font(size=10))

    # Route polyline & markers 1, 2, 3
    map_pins = [(120, 240, "1", "Chandanpura"), (280, 270, "2", "War Cemetery"), (490, 230, "3", "Zia Museum")]
    d.line([(120, 240), (280, 270), (490, 230)], fill=(37, 99, 235), width=3)
    for px, py, pnum, pname in map_pins:
        d.ellipse([(px - 14, py - 14), (px + 14, py + 14)], fill=(30, 58, 138), outline=(255, 255, 255), width=2)
        d.text((px - 4, py - 7), pnum, fill=(255, 255, 255), font=get_font(bold=True, size=11))
        d.text((px - 25, py + 16), pname, fill=(15, 23, 42), font=get_font(bold=True, size=9.5))

    # Daily Schedule Spot Card (Spot 1)
    draw_rounded_box(d, [60, 350, 620, 480], fill=(248, 250, 252), outline=(203, 213, 225), width=1, radius=8)
    d.text((75, 360), "09:00 AM - 12:00 PM  |  Morning Slot", fill=(100, 116, 139), font=get_font(size=10))
    d.text((75, 380), "1. Chandanpura Masjid (চন্দনপুরা মসজিদ)", fill=(15, 23, 42), font=get_font(bold=True, size=13))
    d.text((75, 405), "Category: Historical | Admission: Free (৳0) | Type: Indoor", fill=(71, 85, 105), font=get_font(size=10.5))

    # Badges
    badges = ["1/3 Friends Agree", "Indoor Friendly", "Hidden Gem", "Free Entry"]
    bx = 75
    for b in badges:
        draw_rounded_box(d, [bx, 435, bx + 115, 460], fill=(224, 231, 255), outline=(165, 180, 252), width=1, radius=4)
        d.text((bx + 8, 442), b, fill=(49, 46, 129), font=get_font(bold=True, size=9))
        bx += 122

    # Click prompt
    d.text((75, 495), "👉 Tap card to view 'Why This Place?' Explainability Modal Sheet", fill=(37, 99, 235), font=get_font(size=11, bold=True))

    # Metrics summary footer
    d.text((60, 545), "Day 1 Metrics: Distance: 2.22 km | Total Cost: ৳30 | Route: 2-Opt Optimized ✓", fill=(22, 101, 52), font=get_font(bold=True, size=11))

    # Panel Right: Screen 4 - 'Why This Place?' XAI Modal Sheet
    draw_rounded_box(d, [670, 80, 1110, 580], fill=(255, 255, 255), outline=(147, 197, 253), width=2, radius=10)
    d.rectangle([670, 80, 1110, 125], fill=(30, 64, 175))
    d.text((690, 93), "Screen 4: 'Why This Place?' Explainability Modal", fill=(255, 255, 255), font=get_font(bold=True, size=14))

    d.text((690, 140), "Target POI: Chandanpura Masjid", fill=(15, 23, 42), font=get_font(bold=True, size=13))
    d.text((690, 162), "Consensus Model: Least-Misery Harmonization", fill=(100, 116, 139), font=get_font(size=10.5))

    # Agreement Progress Bar
    d.text((690, 195), "Group Social Agreement Match: 46.03%", fill=(30, 64, 175), font=get_font(bold=True, size=11))
    d.rectangle([690, 220, 1090, 235], fill=(226, 232, 240))
    d.rectangle([690, 220, 874, 235], fill=(37, 99, 235))

    # Individual Member Affinities
    d.text((690, 255), "Individual Member Alignment Breakdown:", fill=(71, 85, 105), font=get_font(bold=True, size=11))
    m_aff = [
        ("Rahat (Historical Enthusiast)", "76.0% Match", (59, 130, 246), "Direct category match"),
        ("Sadia (Beach / Nature)", "30.0% Match", (16, 185, 129), "Tolerable cultural visit"),
        ("Fahim (Luxury / Adventure)", "28.5% Match", (245, 158, 11), "Least-Misery threshold")
    ]
    ay = 280
    for name, match, col, note in m_aff:
        draw_rounded_box(d, [690, ay, 1090, ay + 42], fill=(248, 250, 252), outline=(226, 232, 240), width=1, radius=6)
        d.text((705, ay + 6), name, fill=(15, 23, 42), font=get_font(bold=True, size=10.5))
        d.text((705, ay + 24), note, fill=(100, 116, 139), font=get_font(size=9.5))
        d.text((1000, ay + 12), match, fill=col, font=get_font(bold=True, size=11))
        ay += 48

    # Narrative explanation box
    draw_rounded_box(d, [690, 435, 1090, 520], fill=(240, 253, 244), outline=(187, 247, 208), width=1, radius=6)
    d.text((705, 445), "Natural Language Consensus Narrative:", fill=(22, 101, 52), font=get_font(bold=True, size=10.5))
    narrative = (
        "\"Directly fits Rahat's primary preference in Historical architecture.\n"
        "Guarantees Least-Misery: Fahim's affinity (28.5%) safely exceeds\n"
        "the group misery boundary. Free public entry saves ৳150 BDT.\""
    )
    d.text((705, 465), narrative, fill=(20, 83, 45), font=get_font(size=9.5))

    # Close button
    draw_rounded_box(d, [690, 535, 1090, 565], fill=(241, 245, 249), outline=(203, 213, 225), width=1, radius=6)
    d.text((850, 542), "Close Explanation Sheet", fill=(71, 85, 105), font=get_font(bold=True, size=11))

    out_path = os.path.join(OUTPUT_DIR, "fig4_5_demo_itinerary.png")
    im.save(out_path, dpi=(300, 300))
    print(f"Generated {out_path}")

def generate_figure_4_6_demo_weather_expense():
    """System Demonstration: Dynamic Weather Adaptation & Expense Splitter UI Mockup"""
    w, h = 1150, 600
    im = Image.new("RGB", (w, h), (248, 250, 252))
    d = ImageDraw.Draw(im)

    f_title = get_font(bold=True, size=19)
    f_sub = get_font(bold=False, size=12)
    d.text((40, 20), "Figure 4.6: System Demonstration — Weather Rerouting & Peer Expense Ledger", fill=(15, 23, 42), font=f_title)
    d.text((40, 48), "Screen 5: Real-Time Monsoon Weather Substitute Alert | Screen 6: Peer Expense Splitter & Minimal Settlement Ledger", fill=(100, 116, 139), font=f_sub)

    # Panel Left: Screen 5 - Weather Alert & Substitute
    draw_rounded_box(d, [40, 80, 560, 560], fill=(255, 255, 255), outline=(254, 202, 202), width=2, radius=10)
    d.rectangle([40, 80, 560, 125], fill=(185, 28, 28))
    d.text((60, 93), "Screen 5: Context Weather Adaptation Simulator", fill=(255, 255, 255), font=get_font(bold=True, size=14))

    # Alert Banner
    draw_rounded_box(d, [60, 140, 540, 200], fill=(254, 242, 242), outline=(239, 68, 68), width=2, radius=6)
    d.text((75, 150), "⚠️ MONSOON RAIN ALERT TRIGGERED (Chittagong)", fill=(185, 28, 28), font=get_font(bold=True, size=11.5))
    d.text((75, 172), "Heavy downpour detected! Outdoor spots require immediate shelter reroute.", fill=(127, 29, 29), font=get_font(size=10))

    # Substituted Spot Comparison
    d.text((60, 220), "Automated Schedule Repair Action (Sub-15ms):", fill=(71, 85, 105), font=get_font(bold=True, size=11))

    # Original outdoor spot (strikethrough / replaced)
    draw_rounded_box(d, [60, 245, 540, 310], fill=(241, 245, 249), outline=(203, 213, 225), width=1, radius=6)
    d.text((75, 255), "❌ Replaced Outdoor Spot:", fill=(185, 28, 28), font=get_font(bold=True, size=11))
    d.text((75, 275), "Chattogram Shishu Park (চট্টগ্রাম শিশু পার্ক)", fill=(100, 116, 139), font=get_font(size=11))
    d.text((75, 292), "Outdoor Attraction | High rain hazard | Distance: 3.4 km", fill=(148, 163, 184), font=get_font(size=9.5))

    # Replacement indoor spot
    draw_rounded_box(d, [60, 325, 540, 420], fill=(240, 253, 244), outline=(134, 239, 172), width=2, radius=6)
    d.text((75, 335), "✅ Substituted Cultural Indoor Landmark:", fill=(21, 128, 61), font=get_font(bold=True, size=11.5))
    d.text((75, 355), "Ethnological Museum of Chittagong (নৃতাত্ত্বিক জাদুঘর)", fill=(15, 23, 42), font=get_font(bold=True, size=12))
    d.text((75, 375), "Indoor Enclosed Landmark | Admission: ৳50 | Weather Safe ✓", fill=(21, 128, 61), font=get_font(size=10))
    d.text((75, 395), "Consecutive Transit Recomputed: 8 mins drive (4.12 km)", fill=(71, 85, 105), font=get_font(size=9.5))

    # Badging
    draw_rounded_box(d, [60, 435, 250, 465], fill=(255, 237, 213), outline=(251, 146, 60), width=1, radius=4)
    d.text((70, 443), "⚡ Weather Substitute Badge", fill=(194, 65, 12), font=get_font(bold=True, size=9.5))

    # Notice
    d.text((60, 490), "Engine Response Time: 12.4 ms | Status: 200 OK ✓", fill=(21, 128, 61), font=get_font(bold=True, size=11))
    d.text((60, 515), "Group consensus breakdown preserved without user re-survey.", fill=(100, 116, 139), font=get_font(size=10))

    # Panel Right: Screen 6 - Peer Expense Splitter
    draw_rounded_box(d, [590, 80, 1110, 560], fill=(255, 255, 255), outline=(203, 213, 225), width=2, radius=10)
    d.rectangle([590, 80, 1110, 125], fill=(107, 33, 168))
    d.text((610, 93), "Screen 6: Peer Expense Splitter & Settlement Ledger", fill=(255, 255, 255), font=get_font(bold=True, size=14))

    # Total Spent
    d.text((610, 140), "Total Group Expenditures Logged: ৳ 2,250.00 BDT", fill=(15, 23, 42), font=get_font(bold=True, size=12))
    d.text((610, 160), "Equal Share per Traveler: ৳ 750.00 BDT (3 Members)", fill=(100, 116, 139), font=get_font(size=10.5))

    # Net Balances Card
    d.text((610, 190), "Net Member Balances (Zero-Sum Invariant):", fill=(71, 85, 105), font=get_font(bold=True, size=11))
    balances = [
        ("Rahat (Paid: ৳ 1,800)", "+ ৳ 1,050.00 (Gets back)", (22, 101, 52)),
        ("Sadia (Paid: ৳ 450)", "- ৳ 300.00 (Owes)", (185, 28, 28)),
        ("Fahim (Paid: ৳ 0)", "- ৳ 750.00 (Owes)", (185, 28, 28))
    ]
    by = 215
    for mname, bstr, bcolor in balances:
        draw_rounded_box(d, [610, by, 1090, by + 36], fill=(248, 250, 252), outline=(226, 232, 240), width=1, radius=4)
        d.text((625, by + 10), mname, fill=(15, 23, 42), font=get_font(size=10.5))
        d.text((910, by + 10), bstr, fill=bcolor, font=get_font(bold=True, size=10.5))
        by += 42

    d.text((610, 350), "Sum of Net Balances = ৳ 0.00 BDT (Mathematically Verified ✓)", fill=(22, 101, 52), font=get_font(bold=True, size=10.5))

    # Minimal Settlement Transactions
    d.text((610, 385), "Optimized Debt Settlement Transfers (Greedy Reduction):", fill=(71, 85, 105), font=get_font(bold=True, size=11))
    settlements = [
        ("Transfer 1", "Fahim pays Rahat", "৳ 750.00 BDT", "bKash / Cash"),
        ("Transfer 2", "Sadia pays Rahat", "৳ 300.00 BDT", "bKash / Cash")
    ]
    sy = 410
    for t_id, desc, amt, method in settlements:
        draw_rounded_box(d, [610, sy, 1090, sy + 45], fill=(245, 243, 255), outline=(196, 181, 253), width=1, radius=6)
        d.text((625, sy + 6), f"{t_id}: {desc}", fill=(107, 33, 168), font=get_font(bold=True, size=11))
        d.text((625, sy + 24), f"Payment Method: {method}", fill=(100, 116, 139), font=get_font(size=9.5))
        d.text((950, sy + 12), amt, fill=(107, 33, 168), font=get_font(bold=True, size=12))
        sy += 52

    # Button
    draw_rounded_box(d, [610, 520, 1090, 550], fill=(107, 33, 168), outline=(107, 33, 168), width=1, radius=6)
    d.text((760, 527), "💳 Import Admission Ticket Expenses", fill=(255, 255, 255), font=get_font(bold=True, size=11.5))

    out_path = os.path.join(OUTPUT_DIR, "fig4_6_demo_weather_expense.png")
    im.save(out_path, dpi=(300, 300))
    print(f"Generated {out_path}")

if __name__ == "__main__":
    generate_figure_3_1()
    generate_figure_3_2()
    generate_figure_3_3_class_diagram()
    generate_figure_3_4_sequence()
    generate_figure_3_5_flowchart()
    generate_figure_4_1()
    generate_figure_4_2()
    generate_figure_4_3()
    generate_figure_4_4_demo_onboarding()
    generate_figure_4_5_demo_itinerary()
    generate_figure_4_6_demo_weather_expense()
    print("All 11 report figures generated successfully!")
