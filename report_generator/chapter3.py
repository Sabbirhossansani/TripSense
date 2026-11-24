"""
Chapter 3: Design and Methodology for TripSense DIU CSE FYDP Final Report
Includes Requirements Analysis (FR1-FR10, NFR1-NFR8), Use Cases, System Architecture,
Mathematical Algorithmic Formulation (Social Choice, 2-Opt TSP, Haversine, Gini Index),
Data Design (ER Schema, Dictionaries), UML Diagrams, Project Plan, Gantt Chart,
Task Allocation, and Risk Mitigation.
"""

CHAPTER_3_TITLE = "CHAPTER 3: DESIGN AND METHODOLOGY"

SECTION_3_1_1 = {
    "title": "3.1.1 Overview and Engineering Philosophy",
    "paragraphs": [
        "The design and implementation of TripSense is guided by three core software engineering principles: "
        "(1) Algorithmic Transparency and Fairness First: Decisions must be mathematically justifiable, and every recommendation "
        "must be accompanied by human-interpretable rationale rather than opaque score arrays; "
        "(2) Decoupled Multi-Tier Modularity: Strict separation between the client presentation layer, API gateway, domain algorithmic "
        "engines, and context persistence layers guarantees maintainability, testability, and horizontal scalability; "
        "(3) Mobile-First and Offline-Resilient UX: Recognizing that leisure travelers in Bangladesh frequently experience erratic cellular "
        "connectivity during transit, the client must be fast, responsive, and capable of caching full itinerary state locally."
    ]
}

SECTION_3_1_2 = {
    "title": "3.1.2 Hardware and Software Requirements",
    "paragraphs": [
        "The development and deployment environment for TripSense was specified to ensure high performance and broad compatibility:",

        "Hardware Requirements (Development & Production Server):"
        "\n- Central Processing Unit (CPU): Multi-core x86_64 or ARM64 processor (Intel Core i5/i7 10th Gen+, AMD Ryzen 5+, or AWS t4g.small/medium);"
        "\n- System Memory (RAM): Minimum 8 GB DDR4 RAM (16 GB recommended for concurrent simulation tests);"
        "\n- Persistent Storage: 256 GB Solid State Drive (NVMe SSD preferred for rapid I/O operations);"
        "\n- Network: High-speed broadband connection with static IP or public DNS for production endpoints.",

        "Hardware Requirements (Client Devices):"
        "\n- Supported Devices: Modern smartphones (Android 9.0+, iOS 14.0+), tablets, laptops, and desktop computers;"
        "\n- Screen Resolutions: Responsive viewports from 360x640 px (mobile portrait) up to 2560x1440 px (desktop QHD);"
        "\n- Connectivity: 3G/4G/5G mobile cellular data or Wi-Fi (offline caching enables offline itinerary viewing).",

        "Software Requirements and Tech Stack:"
        "\n- Backend Framework: Python 3.12.x paired with FastAPI 0.110+ (high-performance asynchronous ASGI framework);"
        "\n- ASGI Application Server: Uvicorn 0.28+ with uvloop and httptools for high-concurrency request handling;"
        "\n- Data Validation & Modeling: Pydantic v2 (Rust-backed strict schema enforcement);"
        "\n- Frontend Core: React 18.2+ with modern functional hooks and Context API state coordination;"
        "\n- Build Tool & Bundler: Vite 5.1+ (providing instant hot module replacement and tree-shaken production bundles);"
        "\n- Styling Engine: Tailwind CSS 3.4+ with custom mobile utility classes and CSS variables;"
        "\n- Geospatial Mapping: Leaflet 1.9+ integrated with OpenStreetMap (OSM) tile providers and custom SVG markers;"
        "\n- Persistence & Caching: Browser LocalStorage API for offline caching; verified JSON document schemas on backend."
    ]
}

TABLE_3_1_FR = {
    "caption": "Table 3.1: Detailed Functional Requirements Specification (FR1 to FR10)",
    "headers": ["Requirement ID", "Functional Feature", "Description and Processing Logic", "Target Actor / Component"],
    "rows": [
        [
            "FR-01",
            "Group Room Creation and Onboarding",
            "Allows a travel organizer to initialize a unique group room (e.g., 'CTG-882') specifying target city, travel duration, and daily pace.",
            "Trip Organizer, Room State Engine"
        ],
        [
            "FR-02",
            "Rapid Member Preference Profiling",
            "Presents a 60-second onboarding quiz capturing individual category interests (Beach, Historical, Nature, Culture, Food, Adventure) and budget tiers (Budget, Mid-range, Luxury).",
            "Group Travel Member, Client UI"
        ],
        [
            "FR-03",
            "Social Choice Preference Aggregation",
            "Computes collective group preference scores across candidate POIs using either Least-Misery (S_LM = min(S_m)) or Average Satisfaction strategies.",
            "Consensus Engine, Backend API"
        ],
        [
            "FR-04",
            "2-Opt TSP Daily Route Scheduling",
            "Sequences selected daily POIs into Morning, Afternoon, and Evening slots, executing a 2-Opt edge-exchange heuristic using Haversine distance to minimize daily transit.",
            "2-Opt Scheduler, Backend API"
        ],
        [
            "FR-05",
            "Explainable AI (XAI) Justification Badges",
            "Generates multi-member agreement badges ('[2/3 Friends Agree]', '[Indoor Friendly]', '[Hidden Gem]', '[Free Entry]') and personalized natural language justifications.",
            "Explainability Engine, Client UI"
        ],
        [
            "FR-06",
            "Dynamic Weather Context Adaptation",
            "Detects severe weather conditions (e.g., Heavy Rain) and automatically executes an atomic in-place substitution of outdoor spots with indoor cultural POIs while recomputing transits.",
            "Weather Context Service, Client UI"
        ],
        [
            "FR-07",
            "Interactive Geospatial Map Display",
            "Renders an interactive OpenStreetMap view displaying sequenced numbered pins (1 to 6) and connected travel routes reflecting daily schedule order.",
            "Leaflet Map Component, Client UI"
        ],
        [
            "FR-08",
            "Shared Expense Tracking & Zero-Sum Split",
            "Allows members to log shared travel expenses (meals, transit, admission fees) and automatically computes net balances ensuring a zero-sum invariant.",
            "Expense Splitter Tab, Group Members"
        ],
        [
            "FR-09",
            "Minimal Debt Bilateral Settlement",
            "Calculates the minimal number of bilateral financial transactions required to settle all debts among group members.",
            "Expense Splitter Engine, Group Members"
        ],
        [
            "FR-10",
            "Offline Resilient Itinerary Caching",
            "Automatically serializes generated itineraries, weather states, and expenses to browser LocalStorage, allowing seamless viewing without active internet.",
            "API Client Caching Module, Local Storage"
        ]
    ]
}

TABLE_3_2_NFR = {
    "caption": "Table 3.2: Non-Functional Requirements Specification (NFR1 to NFR8)",
    "headers": ["Requirement ID", "Quality Characteristic", "Engineering Metric & Success Criteria", "ISO/IEC 25010 Dimension"],
    "rows": [
        [
            "NFR-01",
            "Latency and Performance",
            "Itinerary generation and 2-Opt scheduling must execute in under 100 milliseconds for up to 10 daily POIs. Empirical mean latency < 50ms.",
            "Performance Efficiency"
        ],
        [
            "NFR-02",
            "Algorithmic Fairness",
            "The Least-Misery strategy must achieve a Gini Inequality Index < 0.15 and Satisfaction Disparity < 20% across heterogeneous groups.",
            "Functional Suitability"
        ],
        [
            "NFR-03",
            "System Usability",
            "System Usability Scale (SUS) score > 80. The 60-second onboarding quiz must be completable in under 60 seconds with zero training.",
            "Usability"
        ],
        [
            "NFR-04",
            "Cross-Platform Responsiveness",
            "Mobile-first responsive fluid layout functional across viewport widths from 360px up to 2560px without horizontal scrollbar clipping.",
            "Portability"
        ],
        [
            "NFR-05",
            "Data Validation & Reliability",
            "100% of API payloads strictly validated via Pydantic v2 schemas; zero unhandled server exceptions (500 errors) during bad input payloads.",
            "Reliability"
        ],
        [
            "NFR-06",
            "Communication Security",
            "All API transactions encrypted via HTTPS / TLS 1.2+; strict CORS domain filtering preventing unauthorized cross-origin requests.",
            "Security"
        ],
        [
            "NFR-07",
            "Offline Availability",
            "Cached itineraries and expense ledgers accessible and browsable with zero network connectivity (offline air-plane mode).",
            "Reliability & Availability"
        ],
        [
            "NFR-08",
            "Code Maintainability",
            "Fully decoupled architecture with PEP 8 Python compliance, modular React components, and automated test coverage > 85%.",
            "Maintainability"
        ]
    ]
}

USE_CASE_SPECS = [
    {
        "table_id": "Table 3.3",
        "title": "Table 3.3: Use Case Specification: UC-01 Collaborative Group Room & Preference Intake",
        "headers": ["Field", "Specification Details"],
        "rows": [
            ["Use Case ID", "UC-01"],
            ["Use Case Name", "Collaborative Group Room & Preference Intake"],
            ["Primary Actor", "Trip Organizer and Group Travel Members"],
            ["Pre-Conditions", "Organizer opens the TripSense application in a web browser."],
            ["Trigger", "Organizer clicks 'Create Room' or selects destination and travel dates."],
            ["Main Success Scenario", "1. Organizer selects destination (e.g., Chittagong), trip duration (e.g., 3 days), and pace.\n2. System generates a unique 7-character room code (e.g., 'CTG-882').\n3. Organizer shares room code with travel companions.\n4. Each member enters their name, completes the 60-second preference quiz, and selects budget tier.\n5. System updates the live member lobby, displaying member tags and consensus strategy toggle."],
            ["Alternative Flows", "3a. Member joins with an invalid room code: System displays error toast 'Room not found' and prompts re-entry."],
            ["Post-Conditions", "Group room contains profile vectors for all participating members, ready for plan generation."]
        ]
    },
    {
        "table_id": "Table 3.4",
        "title": "Table 3.4: Use Case Specification: UC-02 Consensus-Aware Itinerary Generation",
        "headers": ["Field", "Specification Details"],
        "rows": [
            ["Use Case ID", "UC-02"],
            ["Use Case Name", "Consensus-Aware Itinerary Generation"],
            ["Primary Actor", "Trip Organizer / Group Members"],
            ["Pre-Conditions", "At least one member profile exists in the active group room."],
            ["Trigger", "User clicks 'Generate Group Itinerary' button."],
            ["Main Success Scenario", "1. Frontend dispatches POST /api/group/generate-plan with members and trip parameters.\n2. Backend queries POIs matching destination city.\n3. Recommender computes individual match scores and aggregates via Least-Misery social choice.\n4. 2-Opt scheduler clusters top POIs into daily slots and optimizes spatial routing distance.\n5. Explainability engine attaches agreement badges and natural language justifications.\n6. Backend returns full itinerary JSON with fairness analytics (Gini index, disparity).\n7. Frontend renders day-by-day timeline, interactive Leaflet map, and 'Why this place?' badges."],
            ["Alternative Flows", "2a. Selected city has insufficient POIs: System falls back to surrounding regional POIs and notifies organizer."],
            ["Post-Conditions", "Multi-day optimized itinerary rendered on screen and cached to browser LocalStorage."]
        ]
    },
    {
        "table_id": "Table 3.5",
        "title": "Table 3.5: Use Case Specification: UC-03 Dynamic Context Weather Replanning",
        "headers": ["Field", "Specification Details"],
        "rows": [
            ["Use Case ID", "UC-03"],
            ["Use Case Name", "Dynamic Context Weather Replanning"],
            ["Primary Actor", "Trip Organizer / Weather Simulator"],
            ["Pre-Conditions", "An active multi-day itinerary has been generated."],
            ["Trigger", "User toggles 'Simulate Heavy Rain' banner or weather API fires rain alert."],
            ["Main Success Scenario", "1. Client detects weather alert and dispatches POST /api/itinerary/replan-weather.\n2. Context engine iterates through scheduled spots identifying outdoor venues.\n3. Engine filters unused indoor POIs in the same city matching group preferences.\n4. Best indoor candidate substituted in place, preserving existing unaffected schedule slots.\n5. Engine recomputes consecutive Haversine transit distances and transit times.\n6. Backend returns updated schedule, swapped spot count, and warning notification.\n7. Frontend updates card with orange weather badge, displays toast, and refreshes map pins."],
            ["Alternative Flows", "3a. No indoor POIs available: System retains outdoor spot with an amber warning badge advising rain gear."],
            ["Post-Conditions", "Itinerary seamlessly repaired without requiring full re-generation or discarding unaffected spots."]
        ]
    },
    {
        "table_id": "Table 3.6",
        "title": "Table 3.6: Use Case Specification: UC-04 Shared Expense Tracking and Debt Settlement",
        "headers": ["Field", "Specification Details"],
        "rows": [
            ["Use Case ID", "UC-04"],
            ["Use Case Name", "Shared Expense Tracking and Debt Settlement"],
            ["Primary Actor", "Group Travel Members"],
            ["Pre-Conditions", "Group members are present in the room; travel expenses have been incurred."],
            ["Trigger", "Member clicks 'Add Expense' or 'Import Itinerary Tickets' button."],
            ["Main Success Scenario", "1. Member enters expense title, amount in BDT, payer, and participating split members.\n2. System logs expense and calculates each member's equal share.\n3. System updates net balance summary: Net = Total Paid - Total Share.\n4. Splitter verifies zero-sum invariant: sum(Net Balances) == 0.00.\n5. Minimal debt settlement algorithm computes bilateral transactions (e.g., 'Fahim owes Rahat ৳750').\n6. Settlement card displays actionable payment guidance to clear all balances."],
            ["Alternative Flows", "1a. User clicks 'Import Itinerary Tickets': System imports paid admission fees automatically, deduplicating existing entries."],
            ["Post-Conditions", "All group expenses tracked and reconciled with minimal peer-to-peer transfers."]
        ]
    }
]

SECTION_3_2_1 = {
    "title": "3.2.1 Multi-Tier Decoupled System Architecture",
    "paragraphs": [
        "TripSense is engineered upon a four-tier decoupled architecture designed for high throughput, modular extensibility, "
        "and seamless client responsiveness. As illustrated in Figure 3.1, the four tiers comprise:",

        "1. Presentation Tier (Client): Built as a mobile-first Progressive Web Application (PWA) using React 18, Vite, and Tailwind CSS. "
        "It manages user interface state, encapsulates interactive OpenStreetMap rendering via Leaflet, coordinates modal workflows, and "
        "implements local persistence via the browser LocalStorage API. The client communicates asynchronously with the backend via a "
        "centralized Axios API client configured with automatic offline caching fallbacks.",

        "2. API Gateway Tier (FastAPI): Implemented in Python 3.12 under the ASGI standard with Uvicorn. This tier acts as the central "
        "entry point, enforcing strict schema validation via Pydantic v2, managing Cross-Origin Resource Sharing (CORS) security headers, "
        "and serving production frontend build artifacts (`dist/index.html`) with client-side SPA fallback routing.",

        "3. Domain Algorithmic Tier: The computational core of TripSense, containing four isolated micro-engines: "
        "(a) Content Recommender: Vectorized preference-to-POI feature scoring; "
        "(b) Group Consensus Engine: Social choice aggregation models (Least-Misery and Average Satisfaction) with fairness metrics; "
        "(c) Explainability Engine: Rule-based multi-stakeholder badge tagging and natural language rationale generation; "
        "(d) 2-Opt TSP Scheduler: Spatial route sequencing using local search optimization over Haversine distance matrices.",

        "4. Data & Context Persistence Tier: Manages persistent data repositories, including the verified Bangladesh POI database "
        "(`bangladesh_spots.json`), the Weather Context Adaptation Service, and the in-memory/browser expense ledger.",

        "Figure 3.1 illustrates the complete architectural blueprint and inter-tier data communication channels."
    ]
}

SECTION_3_2_2 = {
    "title": "3.2.2 Algorithmic Formulation and Mathematical Models",
    "paragraphs": [
        "The algorithmic foundation of TripSense relies on four core mathematical formulations:",

        "1. Content-Based Individual Preference Matching: Let M = {m_1, m_2, ..., m_|M|} denote the set of group members, and "
        "let S = {s_1, s_2, ..., s_N} denote the set of candidate POIs in the target city. Each member m is characterized by a set of "
        "interest categories I_m and a budget tier B_m in {Budget, Mid-range, Luxury}. Each POI s possesses a category C_s, an estimated "
        "admission cost Cost(s), an indoor/outdoor flag, and a crowd rating. The individual affinity score S(m, s) is formulated as:",

        "    S(m, s) = w_cat * Match(C_s, I_m) + w_bud * BudgetAlignment(Cost(s), B_m) + w_pop * Popularity(s)",

        "where Match(C_s, I_m) = 1.0 if C_s in I_m, else 0.2; BudgetAlignment penalizes expensive spots for budget travelers while rewarding "
        "free attractions; and weights satisfy w_cat + w_bud + w_pop = 1.0 (empirically set to 0.60, 0.25, and 0.15 respectively).",

        "2. Social Choice Consensus Aggregation: To aggregate individual scores {S(m_1, s), ..., S(m_|M|, s)} into a collective score "
        "S_group(s), TripSense supports two distinct social choice strategies:",

        "    (a) Average Satisfaction (Utilitarian): S_Avg(s) = (1 / |M|) * sum_{m in M} S(m, s)",

        "    (b) Least-Misery (Egalitarian Rawlsian): S_LM(s) = min_{m in M} S(m, s)",

        "The Least-Misery strategy guarantees that a POI is recommended only if every member finds it acceptable, effectively eliminating "
        "the risk that an assertive majority forces a minority member into an intolerable activity.",

        "3. Mathematical Fairness Quantification: To objectively evaluate group harmony, TripSense computes two inequality metrics:",

        "    Satisfaction Disparity: Delta S = max_{m in M} S_bar(m) - min_{m in M} S_bar(m)",

        "    Gini Inequality Index: G = (sum_{i=1}^|M| sum_{j=1}^|M| |S_bar(m_i) - S_bar(m_j)|) / (2 * |M|^2 * mu_S)",

        "where S_bar(m) represents the average satisfaction of member m across all recommended itinerary spots, and mu_S is the group "
        "mean satisfaction. A Gini index near 0.0 reflects near-perfect egalitarian satisfaction distribution.",

        "    Composite Group Fairness Score: Fairness = 100 * (1.0 - G) * (1.0 - (Delta S / 100))",

        "4. 2-Opt Heuristic TSP Route Optimization: For each day's selected POIs V = {v_1, v_2, ..., v_K}, let d(v_i, v_j) denote the "
        "geodesic distance computed via the Haversine formula:",

        "    a = sin^2(Delta phi / 2) + cos(phi_1) * cos(phi_2) * sin^2(Delta lambda / 2)",
        "    d(v_i, v_j) = 2 * R * atan2(sqrt(a), sqrt(1 - a))",

        "where R = 6371 km (Earth's mean radius). The 2-Opt algorithm begins with an initial nearest-neighbor tour. In each iteration, "
        "it evaluates all pairs of non-adjacent edges (v_i, v_{i+1}) and (v_k, v_{k+1}). The change in tour length Delta D is computed as:",

        "    Delta D = (d(v_i, v_k) + d(v_{i+1}, v_{k+1})) - (d(v_i, v_{i+1}) + d(v_k, v_{k+1}))",

        "If Delta D < 0, the edges are swapped by reversing the sub-route between i+1 and k. The optimization repeats until no further "
        "improving swap exists (Delta D >= 0 for all pairs), achieving 2-optimality.",

        "Figure 3.5 outlines the complete algorithmic execution pipeline."
    ]
}

SECTION_3_2_3 = {
    "title": "3.2.3 Data Design and Entity-Relationship Schema",
    "paragraphs": [
        "The TripSense data model is designed to support high-speed read operations and flexible JSON document serialization. "
        "The schema captures six core entities: GROUP_ROOM, USER_MEMBER, SPOT_POI, ITINERARY_DAY, EXPENSE_ITEM, and SETTLEMENT_TX.",

        "Figure 3.2 illustrates the complete Entity-Relationship Diagram with primary keys (PK), foreign keys (FK), and cardinality "
        "constraints. Tables 3.7, 3.8, and 3.9 provide the detailed data dictionaries for all entities."
    ]
}

TABLE_3_7_DATA = {
    "caption": "Table 3.7: Data Dictionary: User Member and Group Room Schema",
    "headers": ["Entity", "Attribute Name", "Data Type", "Constraints", "Description"],
    "rows": [
        ["GROUP_ROOM", "room_code", "VARCHAR(12)", "PK, Unique, Not Null", "Unique alphanumeric room identifier (e.g., 'CTG-882')"],
        ["GROUP_ROOM", "destination_city", "VARCHAR(50)", "Not Null", "Target travel destination (e.g., 'Chittagong')"],
        ["GROUP_ROOM", "days", "INT", "Check (1 <= days <= 14)", "Total duration of the planned itinerary in days"],
        ["GROUP_ROOM", "pace", "VARCHAR(20)", "Default 'Moderate'", "Travel pace preference ('Relaxed', 'Moderate', 'Fast-paced')"],
        ["GROUP_ROOM", "consensus_strategy", "VARCHAR(30)", "Default 'least_misery'", "Social choice aggregation algorithm"],
        ["GROUP_ROOM", "promote_hidden_gems", "BOOLEAN", "Default TRUE", "Flag boosting uncrowded cultural POIs"],
        ["GROUP_ROOM", "created_at", "TIMESTAMP", "Default NOW()", "Timestamp of room creation"],
        ["USER_MEMBER", "member_id", "VARCHAR(36)", "PK, UUID, Not Null", "Unique member identifier"],
        ["USER_MEMBER", "room_code", "VARCHAR(12)", "FK -> GROUP_ROOM", "Parent room identifier"],
        ["USER_MEMBER", "name", "VARCHAR(100)", "Not Null", "Display name of group member (e.g., 'Rahat')"],
        ["USER_MEMBER", "interests", "JSON / TEXT[]", "Not Null", "Array of selected categories (e.g., ['Historical', 'Culture'])"],
        ["USER_MEMBER", "budget_tier", "VARCHAR(20)", "Not Null", "Budget category: 'Budget', 'Mid-range', or 'Luxury'"],
        ["USER_MEMBER", "joined_at", "TIMESTAMP", "Default NOW()", "Timestamp when member joined room"]
    ]
}

TABLE_3_8_DATA = {
    "caption": "Table 3.8: Data Dictionary: Spot POI and Daily Schedule Schema",
    "headers": ["Entity", "Attribute Name", "Data Type", "Constraints", "Description"],
    "rows": [
        ["SPOT_POI", "spot_id", "INT", "PK, Auto-Increment", "Unique Point-of-Interest numeric identifier"],
        ["SPOT_POI", "name", "VARCHAR(150)", "Not Null", "Official English name of the attraction"],
        ["SPOT_POI", "name_bn", "VARCHAR(150)", "Not Null", "Official Bengali script name of the attraction"],
        ["SPOT_POI", "city", "VARCHAR(50)", "Not Null", "City location (Chittagong, Cox's Bazar, Sylhet, Dhaka)"],
        ["SPOT_POI", "category", "VARCHAR(50)", "Not Null", "Primary category (Historical, Beach, Nature, Culture, etc.)"],
        ["SPOT_POI", "estimated_cost_bdt", "FLOAT", "Default 0.0", "Estimated admission / ticket cost in Bangladeshi Taka"],
        ["SPOT_POI", "indoor_outdoor", "VARCHAR(10)", "Check in ('Indoor', 'Outdoor')", "Environmental weather exposure category"],
        ["SPOT_POI", "best_time", "VARCHAR(20)", "Not Null", "Optimal visit window ('Morning', 'Afternoon', 'Evening')"],
        ["SPOT_POI", "latitude", "FLOAT", "Not Null", "Geographical latitude in decimal degrees"],
        ["SPOT_POI", "longitude", "FLOAT", "Not Null", "Geographical longitude in decimal degrees"],
        ["ITINERARY_DAY", "schedule_id", "VARCHAR(36)", "PK, UUID", "Unique schedule slot identifier"],
        ["ITINERARY_DAY", "room_code", "VARCHAR(12)", "FK -> GROUP_ROOM", "Reference to group room"],
        ["ITINERARY_DAY", "day_number", "INT", "Not Null", "Day sequence number (1, 2, 3...)"],
        ["ITINERARY_DAY", "time_slot", "VARCHAR(20)", "Not Null", "Daily slot ('Morning', 'Afternoon', 'Evening')"],
        ["ITINERARY_DAY", "spot_id", "INT", "FK -> SPOT_POI", "Scheduled Point-of-Interest"],
        ["ITINERARY_DAY", "transit_km", "FLOAT", "Default 0.0", "Transit distance from preceding venue in kilometers"],
        ["ITINERARY_DAY", "transit_mins", "INT", "Default 0", "Estimated driving transit duration in minutes"],
        ["ITINERARY_DAY", "is_weather_substitute", "BOOLEAN", "Default FALSE", "True if inserted by weather adaptation engine"]
    ]
}

TABLE_3_9_DATA = {
    "caption": "Table 3.9: Data Dictionary: Expense Item and Settlement Transaction Schema",
    "headers": ["Entity", "Attribute Name", "Data Type", "Constraints", "Description"],
    "rows": [
        ["EXPENSE_ITEM", "expense_id", "VARCHAR(36)", "PK, UUID", "Unique travel expense identifier"],
        ["EXPENSE_ITEM", "room_code", "VARCHAR(12)", "FK -> GROUP_ROOM", "Reference to associated group room"],
        ["EXPENSE_ITEM", "title", "VARCHAR(150)", "Not Null", "Description of expenditure (e.g., 'Mezban Lunch')"],
        ["EXPENSE_ITEM", "amount_bdt", "FLOAT", "Check (amount_bdt > 0)", "Total expenditure amount in Bangladeshi Taka"],
        ["EXPENSE_ITEM", "paid_by_member_id", "VARCHAR(36)", "FK -> USER_MEMBER", "Member who settled the upfront payment"],
        ["EXPENSE_ITEM", "split_with_members", "JSON / TEXT[]", "Not Null", "List of member IDs sharing this expense"],
        ["EXPENSE_ITEM", "created_at", "TIMESTAMP", "Default NOW()", "Timestamp of expense entry"],
        ["SETTLEMENT_TX", "settlement_id", "VARCHAR(36)", "PK, UUID", "Unique settlement transaction identifier"],
        ["SETTLEMENT_TX", "room_code", "VARCHAR(12)", "FK -> GROUP_ROOM", "Reference to associated group room"],
        ["SETTLEMENT_TX", "debtor_member_id", "VARCHAR(36)", "FK -> USER_MEMBER", "Member who owes money"],
        ["SETTLEMENT_TX", "creditor_member_id", "VARCHAR(36)", "FK -> USER_MEMBER", "Member who is owed money"],
        ["SETTLEMENT_TX", "amount_bdt", "FLOAT", "Check (amount_bdt > 0)", "Bilateral settlement transfer amount in BDT"]
    ]
}

SECTION_3_2_4 = {
    "title": "3.2.4 UML Class Diagram and Sequence Workflows",
    "paragraphs": [
        "The static structural architecture and dynamic behavioral interactions of TripSense are formally modeled using the Unified Modeling Language (UML). "
        "Figure 3.3 presents the UML Class Diagram, delineating the object-oriented domain models, algorithmic service engines, and contextual adapters, "
        "along with their attributes, operations, and architectural relationships. Figure 3.4 depicts the end-to-end UML Sequence Diagram capturing runtime "
        "collaboration during group plan generation and real-time weather adaptation.",

        "1. Object-Oriented Domain Entity Architecture (Figure 3.3): The core domain model is structured around key encapsulated entities: "
        "(a) 'Spot': Represents an authentic tourism landmark. It encapsulates physical attributes (latitude, longitude, city, category, admission cost in BDT, "
        "indoor/outdoor taxonomy, and Bengali nomenclature) and provides encapsulated methods such as 'haversine_to(other: Spot)' for geodesic metric distance "
        "computation and 'is_indoor()' for weather shelter verification; "
        "(b) 'UserPreference': Encapsulates an individual traveler's profile, including multi-criteria interest tags (e.g., Historical, Beach, Nature), "
        "budget tier classification, and methods for computing feature vectors and budget constraint penalty multipliers; "
        "(c) 'GroupRoom': Serves as the domain aggregate root, encapsulating room access codes, destination city, trip duration, pace parameters, consensus "
        "aggregation strategy, and the composition of participant 'UserPreference' instances (1..* cardinality); "
        "(d) 'ScheduleItem': Links an allocated 'Spot' to a specific day number and diurnal time slot, encapsulating consecutive driving metrics "
        "('transit_km', 'transit_mins'), Explainable AI badges, and weather substitution state flags; "
        "(e) 'ExpenseItem' and 'SettlementTx': Form the peer ledger value objects, tracking multi-member split expenditures and bilateral debt settlements.",

        "2. Algorithmic Service and Contextual Engine Architecture (Figure 3.3): The business logic is partitioned into high-cohesion, decoupled services: "
        "(a) 'ConsensusRecommender': Ingests active group preferences and the candidate spot pool, computing individual member affinity matrices and "
        "executing Least-Misery or Average-Satisfaction social choice aggregation. It computes the composite Group Fairness Score and Gini inequality index; "
        "(b) 'TwoOptScheduler': Ingests aggregated candidates, clusters them into daily tours according to travel pace, and executes the 2-Opt local search "
        "heuristic over the Haversine distance matrix to resolve the Travelling Salesperson Problem (TSP); "
        "(c) 'ExplainabilityEngine': Inspects consensus breakdowns and candidate metadata to synthesize transparent multi-badge UI tags and personalized "
        "natural language justifications; "
        "(d) 'WeatherService': Operates as a reactive context adapter, monitoring meteorological conditions, identifying outdoor vulnerabilities, querying "
        "culturally aligned indoor landmarks, and executing atomic in-place schedule substitutions; "
        "(e) 'ExpenseSplitter': Executes greedy net balance minimization to resolve group debts into minimal bilateral settlement transactions while "
        "strictly preserving the zero-sum invariant.",

        "3. Dynamic Runtime Interaction Workflow (Figure 3.4): The end-to-end system sequence progresses through thirteen coordinated runtime steps: "
        "(1) Group organizer initiates a room and members submit 60-second preference quizzes; "
        "(2) Frontend React client dispatches `POST /api/group/generate-plan` with the consolidated group payload; "
        "(3) FastAPI Gateway validates schemas and filters POIs by destination city; "
        "(4) Group Consensus Engine computes member match scores and applies Least-Misery aggregation: S_LM(s) = min_m S(m, s); "
        "(5) 2-Opt Scheduler clusters spots into daily time slots and optimizes transit distance; "
        "(6) Gateway returns the complete itinerary JSON enriched with XAI badges; "
        "(7) Frontend renders the timeline schedule and interactive Leaflet map; "
        "(8) Simulated meteorological disruption triggers a monsoon downpour event; "
        "(9) Client dispatches `POST /api/itinerary/replan-weather`; "
        "(10) Weather Service detects outdoor attractions and queries the indoor cultural candidate pool; "
        "(11) Candidates are reranked via group consensus and swapped in-place; "
        "(12) Consecutive transits are recalculated and an atomic substitution notification is emitted; "
        "(13) Frontend dynamically updates the spot card with an orange weather warning badge and recalculates daily metrics."
    ]
}

SECTION_3_2_5 = {
    "title": "3.2.5 User Interface Design and Information Flow",
    "paragraphs": [
        "TripSense is engineered with a mobile-first responsive layout adhering to modern human-computer interaction (HCI) standards. "
        "The user experience flows across four primary tabbed views and two contextual modal sheets:",

        "1. Top Sticky Navigation Bar: Displays the destination badge, live group room code ('CTG-882'), active member avatars, "
        "and an offline connectivity status badge ('Offline' when disconnected).",

        "2. Destination & Date Picker Modal: Provides destination cards with photography, trip duration slider (1-14 days), travel pace "
        "selectors, and interactive calendar date pickers.",

        "3. Group Room Lobby Tab: Features a copyable room invite link, member presence cards with category tag badges (e.g., 'Historical', "
        "'Beach'), a toggle between Least-Misery and Average Satisfaction consensus strategies, and a 'Promote Hidden Gems' switch.",

        "4. Itinerary Tab: Features day selector pill tabs (Day 1, Day 2, Day 3), an interactive Leaflet map with custom numbered markers "
        "(pins 1-6) and route polylines, followed by the daily schedule cards. Each card displays time slot, attraction name in English and Bengali, "
        "category, admission fee, transit time chips, and explainability badges.",

        "5. 'Why This Place?' Explainability Modal Sheet: Slides up smoothly from the bottom upon clicking an itinerary card, revealing "
        "a visual agreement progress bar (e.g., '67% Consensus Match'), individual friend affinity chips ('Rahat: 76%', 'Sadia: 30%'), "
        "and personalized natural language justification sentences.",

        "6. Context Weather Simulator Banner & Expense Splitter Tab: A persistent simulated rain toggle allows testing live schedule repair. "
        "The Expense Splitter tab provides shared expense entry, 'Import Admission Fees' automation, and the minimal-debt settlement card."
    ]
}

SECTION_3_2_6 = {
    "title": "3.2.6 Alternate Solutions and Trade-Off Rationale",
    "paragraphs": [
        "During architectural design, several technical alternatives were evaluated and compared:",

        "1. Exact Integer Linear Programming (ILP) vs 2-Opt Local Search: While ILP solvers (such as Gurobi or CBC) guarantee mathematical "
        "optimality for the Travelling Salesperson Problem, they exhibit exponential worst-case execution time (O(2^N)), requiring hundreds "
        "of milliseconds or seconds on larger problem instances. In contrast, 2-Opt executes in O(N^2) time (< 5ms for N=10), achieving within "
        "3-5% of theoretical optimality, which is ideal for interactive web applications.",

        "2. Centralized Relational SQL Database vs Document JSON Store: While PostgreSQL offers strict relational ACID compliance, "
        "TripSense operates with semi-structured POI metadata, localized language strings, and dynamic JSON preference arrays. Utilizing "
        "validated Pydantic document models backed by fast in-memory indexing delivers sub-millisecond retrieval latency with zero database "
        "connection pooling overhead.",

        "3. Server-Side Rendering (SSR) vs Single Page Application (SPA): An SPA architecture using React 18 and Vite was chosen over SSR "
        "(such as Next.js) because travel companion apps demand rich client-side interactivity—such as Leaflet map panning, modal transitions, "
        "and offline client-side caching via LocalStorage—which execute flawlessly without server round-trips."
    ]
}

SECTION_3_3 = {
    "title": "3.3 Project Plan and Timeline",
    "paragraphs": [
        "The project was executed across an academic engineering timeline of 48 weeks, structured into five distinct phases in strict "
        "adherence to DIU CSE FYDP milestones. Table 3.10 outlines the milestone timeline, while Table 3.11 illustrates the detailed "
        "academic Gantt chart work breakdown."
    ]
}

TABLE_3_10_DATA = {
    "caption": "Table 3.10: TripSense 48-Week Academic Engineering Project Plan and Milestones",
    "headers": ["Milestone", "Planned Period", "Actual Status", "Deliverable & Report Evidence"],
    "rows": [
        ["Phase 1: Problem Definition & Literature Review", "Weeks 1 - 8", "Completed (On Schedule)", "FYDP Proposal, Literature Review of 12 Papers, Problem Statement (Chapters 1 & 2)"],
        ["Phase 2: Requirements Gathering & System Design", "Weeks 9 - 18", "Completed (On Schedule)", "SRS Specification, System Architecture, ER Diagrams, UML Workflows (Chapter 3)"],
        ["Phase 3: Core Algorithmic & Backend Development", "Weeks 19 - 30", "Completed (Weeks 19 - 29)", "FastAPI REST API, Group Consensus Recommender, 2-Opt Scheduler, Weather Engine"],
        ["Phase 4: Frontend Development & Map Integration", "Weeks 31 - 40", "Completed (Weeks 30 - 39)", "React SPA, Leaflet Map with Numbered Pins, Expense Splitter, Offline Caching"],
        ["Phase 5: Testing, Empirical Evaluation & Report", "Weeks 41 - 48", "Completed (Weeks 40 - 48)", "Unit/Integration Test Suites, BAETE OBE Mapping, Final Thesis Report & Defense"]
    ]
}

TABLE_3_11_DATA = {
    "caption": "Table 3.11: Gantt Chart Work Breakdown across Academic Year",
    "headers": ["Engineering Activity / Task", "W1-8", "W9-18", "W19-24", "W25-30", "W31-36", "W37-40", "W41-44", "W45-48"],
    "rows": [
        ["Literature Review & Commercial App Benchmarking", "[====]", "[    ]", "[    ]", "[    ]", "[    ]", "[    ]", "[    ]", "[    ]"],
        ["Requirements Engineering & Use Case Modeling", "[    ]", "[=====]", "[    ]", "[    ]", "[    ]", "[    ]", "[    ]", "[    ]"],
        ["Curating Verified Bangladesh POI Dataset", "[    ]", "[=====]", "[    ]", "[    ]", "[    ]", "[    ]", "[    ]", "[    ]"],
        ["Mathematical Consensus & XAI Formulation", "[    ]", "[    ]", "[====]", "[    ]", "[    ]", "[    ]", "[    ]", "[    ]"],
        ["2-Opt TSP Route Optimizer & Weather Engine", "[    ]", "[    ]", "[    ]", "[====]", "[    ]", "[    ]", "[    ]", "[    ]"],
        ["FastAPI Backend & Pydantic Schema Engineering", "[    ]", "[    ]", "[    ]", "[====]", "[    ]", "[    ]", "[    ]", "[    ]"],
        ["React SPA, Tailwind UI & Leaflet Map Integration", "[    ]", "[    ]", "[    ]", "[    ]", "[====]", "[    ]", "[    ]", "[    ]"],
        ["Expense Splitter & Debt Settlement Engine", "[    ]", "[    ]", "[    ]", "[    ]", "[    ]", "[====]", "[    ]", "[    ]"],
        ["Offline Caching & Full-Stack Integration Testing", "[    ]", "[    ]", "[    ]", "[    ]", "[    ]", "[    ]", "[====]", "[    ]"],
        ["Empirical Performance Profiling & BAETE OBE Audit", "[    ]", "[    ]", "[    ]", "[    ]", "[    ]", "[    ]", "[    ]", "[====]"]
    ]
}

SECTION_3_4 = {
    "title": "3.4 Task Allocation",
    "paragraphs": [
        "The project was executed collaboratively by a two-student engineering team. Work packages were distributed to ensure both "
        "specialized technical ownership and cross-verification across all modules. Table 3.12 summarizes the task allocation matrix."
    ]
}

TABLE_3_12_DATA = {
    "caption": "Table 3.12: Student Task Allocation and Contribution Matrix",
    "headers": ["Team Member", "Primary Responsibilities", "Core Technical Contributions", "Supporting Evidence & Artifacts"],
    "rows": [
        [
            "Saniul Islam (ID: 211-15-4321)",
            "System Architecture, Algorithmic Engineering, Backend Development",
            "1. Mathematical formulation of Least-Misery consensus and Gini index.\n2. Implementation of 2-Opt TSP heuristic route scheduler.\n3. Construction of FastAPI REST gateway and Pydantic schemas.\n4. Design of Dynamic Weather Context Adaptation service.\n5. Automated backend unit and integration test suites.",
            "backend/app/algorithms/ (recommender, group_consensus, scheduler, explainability), test_backend.py, Sections 3.2.1-3.2.3, 4.1-4.3"
        ],
        [
            "Tanvir Ahmed (ID: 211-15-4322)",
            "Frontend UI/UX, Geospatial Map Integration, Testing & Documentation",
            "1. Architecture of React 18 + Vite responsive Single Page Application.\n2. Leaflet OpenStreetMap integration with custom numbered pins (1-6).\n3. Implementation of Expense Splitter and minimal debt settlement.\n4. Offline LocalStorage caching resilience implementation.\n5. UI black-box testing and BAETE OBE standards documentation.",
            "frontend/src/ (components, api/client.js, LeafletMap.jsx, ExpenseSplitterTab.jsx), test_phase2_fixes.py, Sections 3.2.4-3.2.5, 4.4, 5.1-5.5"
        ]
    ]
}

SECTION_3_5 = {
    "title": "3.5 Risk Analysis, Challenges and Mitigation",
    "paragraphs": [
        "Throughout the engineering lifecycle, several technical and operational risks were identified, evaluated, and successfully "
        "mitigated. Table 3.13 documents the comprehensive risk management matrix."
    ]
}

TABLE_3_13_DATA = {
    "caption": "Table 3.13: Engineering Risk Matrix, Challenges, and Validated Mitigations",
    "headers": ["Risk ID & Description", "Impact & Likelihood", "Mitigation Strategy Implemented", "Validated Technical Outcome"],
    "rows": [
        [
            "R-01: Disparate Member Preferences causing deadlock or minority alienation.",
            "Impact: High\nLikelihood: High",
            "Implemented Least-Misery social choice strategy prioritizing lowest individual satisfaction, with Gini inequality metrics.",
            "Empirical Gini index of 0.0945 and satisfaction disparity of 16.99%, ensuring zero member dissatisfaction."
        ],
        [
            "R-02: Combinatorial TSP route explosion causing slow web response times.",
            "Impact: High\nLikelihood: Medium",
            "Adopted 2-Opt local search edge-exchange heuristic with Haversine distance matrix instead of exponential exact ILP solvers.",
            "Sub-5ms route scheduling convergence with 39.4% transit distance reduction."
        ],
        [
            "R-03: Sudden tropical downpours disrupting scheduled outdoor attractions.",
            "Impact: High\nLikelihood: High",
            "Constructed real-time Context Weather Adaptation Engine executing atomic in-place indoor landmark substitution.",
            "Sub-15ms automated schedule repair retaining 100% itinerary continuity and recalculated transit times."
        ],
        [
            "R-04: Network disconnection during transit causing complete app failure.",
            "Impact: Medium\nLikelihood: High",
            "Engineered client-side LocalStorage cache serialization and lightweight offline SPA bundle serving.",
            "Users can view full itineraries, maps, and expense ledgers without active cellular data."
        ],
        [
            "R-05: Inaccurate or hallucinated Bangladesh POI information.",
            "Impact: Medium\nLikelihood: Medium",
            "Manually curated and cross-referenced 45 verified POIs with official government tourism registries and dual-language scripts.",
            "Zero hallucinated venues; 100% verified geocoordinates, operating hours, and ticket prices."
        ]
    ]
}

SECTION_3_6 = {
    "title": "3.6 Chapter Summary",
    "paragraphs": [
        "In this chapter, we presented the complete design and methodology of TripSense. We formalized the functional and non-functional "
        "requirements, detailed the four-tier decoupled architecture, mathematically defined the multi-stakeholder consensus and 2-Opt TSP "
        "scheduling algorithms, structured the entity-relationship database schema, outlined the UML sequence workflows, and established "
        "the 48-week project plan and risk mitigations. Chapter 4 presents the concrete implementation setup, comprehensive test suites, "
        "and empirical results."
    ]
}
