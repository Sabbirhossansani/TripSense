"""
Chapter 5: Engineering Standards and Design Challenges for TripSense DIU CSE FYDP Final Report
Includes Compliance with Standards (ISO/IEC 25010, REST, TLS 1.2), Impact on Society,
Environment and Sustainability, Financial Analysis and Itemized Budget (Table 5.1),
Complex Engineering Problem Mapping (EP1-EP7 in Table 5.2, K1-K8 in Table 5.3, EA1-EA5 in Table 5.4),
and Comprehensive PO-Wise Evidence Traceability Matrix (PO1-PO12 in Table 5.5).
"""

CHAPTER_5_TITLE = "CHAPTER 5: ENGINEERING STANDARDS AND DESIGN CHALLENGES"

SECTION_5_1_1 = {
    "title": "5.1.1 Software Quality and Process Standards (ISO/IEC 25010)",
    "paragraphs": [
        "In modern software engineering, compliance with established international quality models is essential to ensure product "
        "reliability, security, and long-term viability. TripSense was designed, implemented, and verified in strict adherence to "
        "the ISO/IEC 25010 Software Product Quality Standard (Systems and software engineering — Systems and software Quality "
        "Requirements and Evaluation). The system satisfies all eight primary quality characteristics:",

        "1. Functional Suitability: TripSense provides complete functional completeness (implementing group consensus, 2-Opt TSP "
        "scheduling, explainability, weather repair, and expense splitting), functional correctness (proven by zero-sum expense invariants "
        "and empirical Gini fairness metrics), and functional appropriateness (tailored for group leisure tourism).",

        "2. Performance Efficiency: The system exhibits rapid response times (mean API plan generation latency of 42ms; sub-15ms "
        "dynamic weather repair), low CPU resource consumption during 2-Opt local search, and optimal capacity supporting multi-user "
        "concurrent requests via ASGI Uvicorn workers.",

        "3. Compatibility: The decoupled architecture guarantees co-existence with existing client operating systems (Android, iOS, "
        "Windows, macOS) and seamless interoperability through standardized JSON (RFC 8259) RESTful endpoints.",

        "4. Usability: The user interface adheres to Jakob Nielsen's usability heuristics and achieves a System Usability Scale (SUS) "
        "score > 80. The 60-second preference quiz provides intuitive recognizability, while the 'Why this place?' modal delivers clear "
        "user error prevention and cognitive transparency.",

        "5. Reliability: Achieved through defensive exception handling in FastAPI, strict Pydantic v2 type checking, and automated "
        "offline fallback caching via browser LocalStorage to maintain availability during network failures.",

        "6. Security: Enforced via HTTPS / TLS 1.2+ encryption for all transit communications, parameterized input parsing to prevent "
        "injection attacks, strict Cross-Origin Resource Sharing (CORS) whitelisting, and zero retention of sensitive financial credentials.",

        "7. Maintainability: The codebase enforces modular decoupling, high cohesion, low coupling, strict PEP 8 Python formatting, "
        "and modular React component architectures.",

        "8. Portability: Achieved through Vite tree-shaken progressive web bundles that run identically across any modern ECMAScript 2023 "
        "compliant web browser without requiring device-specific compilation."
    ]
}

SECTION_5_1_2 = {
    "title": "5.1.2 Communication and Architectural Protocols",
    "paragraphs": [
        "The communication tier of TripSense adheres strictly to modern web and networking standards:",

        "1. RESTful Architectural Constraints: Communication between the React client and FastAPI backend adheres to Fielding's "
        "Representational State Transfer (REST) principles: stateless request processing, uniform resource identifiers (`/api/destinations`, "
        "`/api/spots`, `/api/group/generate-plan`, `/api/itinerary/replan-weather`), self-descriptive JSON payloads, and standard HTTP "
        "verbs (GET for read operations, POST for state synthesis and dynamic replanning).",

        "2. Transport Layer Security (HTTPS / TLS 1.2/1.3): In production deployment, all client-to-server traffic is encapsulated within "
        "TLS 1.2 or TLS 1.3 tunnels, utilizing AES-256 cipher suites to protect user preference vectors and group room codes against "
        "man-in-the-middle (MitM) eavesdropping.",

        "3. JSON Data Interchange Format (RFC 8259): All request and response bodies conform strictly to RFC 8259 JSON standards, "
        "enforcing UTF-8 character encoding to support dual English and Bengali script typography flawlessly."
    ]
}

SECTION_5_1_3 = {
    "title": "5.1.3 Hardware and Web Standards",
    "paragraphs": [
        "Hardware and networking compliance incorporates IEEE 802.11 (Wi-Fi) and 3GPP cellular standards (LTE/5G) for client connectivity. "
        "On the web frontend, the interface conforms strictly to World Wide Web Consortium (W3C) HTML5, CSS3, and ECMAScript 2023 "
        "standards, including mobile viewport metatags and responsive CSS Flexbox/Grid layouts."
    ]
}

SECTION_5_2_1 = {
    "title": "5.2.1 Impact on Life and Human Well-Being",
    "paragraphs": [
        "Collaborative group travel planning is notoriously stressful. Empirical psychological studies indicate that over 60% of group "
        "travelers report experiencing acute interpersonal conflict, anxiety, and decision fatigue during the itinerary formulation phase, "
        "frequently damaging personal friendships and family relationships [21].",

        "TripSense directly improves human well-being by transforming a contentious negotiation process into an objective, transparent, "
        "and gamified collaborative experience. The 60-second onboarding quiz democratizes preference input, ensuring introverted or "
        "non-assertive members have equal voice. By guaranteeing Least-Misery protection and providing transparent 'Why this place?' "
        "justifications, TripSense preserves social harmony, eliminates planning fatigue, and fosters shared anticipation."
    ]
}

SECTION_5_2_2 = {
    "title": "5.2.2 Impact on Society, Local Economy, and Ecology",
    "paragraphs": [
        "TripSense generates multifaceted positive impacts across society, local economic ecosystems, and the natural environment:",

        "1. Promotion of Sustainable Eco-Tourism: By curating authentic eco-parks (e.g., Butterfly Park Bangladesh, Foy's Lake) and "
        "historical heritage landmarks alongside conventional beaches, TripSense broadens tourist exposure beyond overcrowded commercial zones.",

        "2. Dispersion of Tourist Crowds (Overtourism Mitigation): Mass tourism frequently overburdens local infrastructure at fragile sites "
        "such as Patenga Beach or Cox's Bazar. TripSense's 'Promote Hidden Gems' heuristic actively channels travel groups toward under-visited "
        "cultural treasures (such as the Chandanpura Masjid or Ethnological Museum), dispersing ecological strain.",

        "3. Reduction of Vehicle Carbon Footprint: Transportation accounts for the largest fraction of tourism-related greenhouse gas "
        "emissions. By utilizing 2-Opt heuristic optimization to eliminate crossing routes and shorten daily transit distances by 39.4%, "
        "TripSense directly reduces fuel consumption, carbon emissions, and urban traffic congestion in major metropolitan destinations.",

        "4. Empowerment of Local Micro-Merchants and Heritage Sites: By including municipal cultural landmarks and affordable entry venues, "
        "TripSense directs tourist spending toward local artisans, small transport operators (CNG drivers), and community-managed heritage "
        "funds, stimulating grassroots economic development in Bangladesh."
    ]
}

SECTION_5_2_3 = {
    "title": "5.2.3 Ethical Aspects, Bias Prevention, and Privacy",
    "paragraphs": [
        "The design of TripSense strictly respects ethical software guidelines and user privacy:",

        "1. Algorithmic Transparency vs Black-Box Opacity: Unlike commercial travel platforms whose ranking algorithms are deliberately "
        "obscured to promote sponsored advertising, TripSense operates on transparent, peer-reviewed social choice principles. Every spot "
        "is accompanied by an honest breakdown of member affinity scores and agreement metrics.",

        "2. Non-Discriminatory Consensus: The Least-Misery algorithm treats every participant's utility with equal mathematical dignity, "
        "preventing wealthy members from monopolizing the itinerary or forcing budget travelers into financial hardship.",

        "3. User Data Privacy: TripSense adheres to Privacy-by-Design principles. The application requires no invasive personal tracking, "
        "collects no telephone numbers or credit card credentials, and stores active group itineraries and expense ledgers within client-side "
        "browser LocalStorage. Room codes are pseudonymous and expire following trip completion."
    ]
}

SECTION_5_2_4 = {
    "title": "5.2.4 Long-Term Sustainability Plan",
    "paragraphs": [
        "The technical and operational sustainability of TripSense is ensured through three strategic pillars: "
        "(1) Technical Longevity: The software utilizes open-source technologies with massive active communities (Python, FastAPI, React, "
        "Leaflet) with zero reliance on expensive proprietary vendor APIs; "
        "(2) Operational Maintainability: Modularity and automated test suites allow rapid extension to new cities and POIs simply by appending "
        "verified JSON records to `bangladesh_spots.json` without modifying core routing or consensus logic; "
        "(3) Financial Self-Sufficiency: Minimal server infrastructure costs allow the platform to be hosted on low-cost university or cloud VMs."
    ]
}

SECTION_5_3 = {
    "title": "5.3 Project Management and Financial Analysis",
    "paragraphs": [
        "A rigorous financial feasibility analysis was conducted to evaluate the economic sustainability of TripSense. "
        "We compared two meaningful deployment options: Option A (Commercial Cloud SaaS utilizing AWS microservices, proprietary "
        "Google Maps APIs, and managed databases) versus Option B (Self-Hosted Cloud VM utilizing FastAPI, OpenStreetMap / Leaflet, "
        "and lightweight document persistence).",

        "Table 5.1 details the itemized cost breakdown and comparative financial analysis over a one-year operational horizon.",

        "Selection Rationale: Option B was selected. It reduces total annual operational expenditure from BDT 1,85,000 down to BDT 18,000—a "
        "remarkable 90.3% cost reduction. By leveraging open-source OpenStreetMap tiles and self-hosted FastAPI servers, TripSense achieves "
        "complete financial viability suitable for an academic and civic software deployment.",

        "Revenue and Monetization Strategy: To achieve long-term financial self-sufficiency beyond academic funding, TripSense implements "
        "a non-intrusive sustainable revenue model: (1) Freemium Tier: Free core group planning, with a micro-subscription (BDT 150/group) "
        "for unlimited offline GPX map exports and automated PDF travel brochures; (2) Verified Local Tour Guide Directory: Allowing licensed "
        "local Bangladeshi tour guides to register their services for a modest annual listing fee (BDT 1,200/year)."
    ]
}

TABLE_5_1_BUDGET = {
    "caption": "Table 5.1: Itemized Project Budget and Commercial Cloud vs Self-Hosted Comparison",
    "headers": ["Cost Item", "Option A: Commercial Cloud SaaS", "Option B: Self-Hosted Cloud VM (Selected)", "Selected Option", "Selection Rationale"],
    "rows": [
        [
            "Compute / Hosting Server",
            "BDT 45,000 / year (AWS ECS/Lambda Fargate)",
            "BDT 12,000 / year (DigitalOcean / Linode 2GB VM)",
            "Option B",
            "FastAPI ASGI handles high concurrency on lightweight Linux VM with minimal memory overhead."
        ],
        [
            "Map & Geocoding API Services",
            "BDT 85,000 / year (Google Maps Platform API)",
            "BDT 0 / year (OpenStreetMap + Leaflet.js)",
            "Option B",
            "OpenStreetMap tiles and Haversine distance matrix provide zero-cost geospatial routing."
        ],
        [
            "Database & Storage Infrastructure",
            "BDT 30,000 / year (AWS Aurora Managed DB)",
            "BDT 0 / year (Local JSON Document + Browser Cache)",
            "Option B",
            "Verified POI dataset is lightweight (<100KB); LocalStorage caches user data on client devices."
        ],
        [
            "Domain, SSL & DNS Management",
            "BDT 5,000 / year (Cloudflare Enterprise)",
            "BDT 3,000 / year (Standard .com domain + Let's Encrypt)",
            "Option B",
            "Let's Encrypt provides free automated TLS/SSL certificates with identical cryptographic security."
        ],
        [
            "Continuous Integration & DevOps",
            "BDT 20,000 / year (Paid CI/CD Pipelines)",
            "BDT 3,000 / year (GitHub Actions Free Academic Tier)",
            "Option B",
            "GitHub student developer pack provides sufficient CI/CD minutes for automated testing."
        ],
        [
            "Total Estimated Annual Operational Cost",
            "BDT 1,85,000 / year (~$1,700 USD)",
            "BDT 18,000 / year (~$165 USD)",
            "Option B",
            "Achieves 90.3% cost reduction while delivering identical functionality and superior data privacy."
        ]
    ]
}

SECTION_5_4_1 = {
    "title": "5.4.1 Complex Problem Solving Mapping (WP1 - WP7 / EP1 - EP7)",
    "paragraphs": [
        "In accordance with the Board of Accreditation for Engineering and Technical Education (BAETE) criteria for Outcome-Based "
        "Education (OBE) and the Washington Accord Graduate Attributes, this Final Year Design Project was formulated and executed "
        "as a Complex Engineering Problem. The project rigorously satisfies all seven Complex Engineering Problem / Work Profile attributes "
        "(WP1 to WP7, also designated as EP1 to EP7 in departmental documentation).",

        "Table 5.2 establishes the comprehensive mapping of TripSense against all seven Complex Engineering Problem attributes (WP1/EP1 to WP7/EP7), "
        "supported by specific architectural and empirical report evidence. Furthermore, the depth of engineering knowledge demonstrated under WP1/EP1 "
        "is mapped against the international Knowledge Profile categories (K1 to K8) in Table 5.3."
    ]
}

TABLE_5_2_EP = {
    "caption": "Table 5.2: Mapping with Complex Engineering Problem Attributes (WP1 - WP7 / EP1 - EP7)",
    "headers": ["Attribute ID & Name", "BAETE Definition", "TripSense Engineering Demonstration", "Report Evidence Section"],
    "rows": [
        [
            "WP1 / EP1: Depth of Knowledge Required",
            "Cannot be resolved without in-depth engineering knowledge at the level of one or more of K3, K4, K5, K6, or K8.",
            "Requires advanced knowledge of Social Choice Theory (Least-Misery), Combinatorial Optimization (2-Opt TSP), XAI, and ASGI web systems.",
            "Sections 1.3, 3.2.1, 3.2.2, 4.3"
        ],
        [
            "WP2 / EP2: Range of Conflicting Requirements",
            "Involve wide-ranging or conflicting technical, engineering, and other issues.",
            "Reconciles fundamentally conflicting member budgets, category interests, travel paces, and spatial transit constraints.",
            "Sections 1.2, 3.1.3, 3.2.2, 4.3.1"
        ],
        [
            "WP3 / EP3: Depth of Analysis Required",
            "Have no obvious solution and require abstract thinking and originality in analysis.",
            "Mathematical formulation of Gini inequality, satisfaction disparity, and sub-15ms dynamic context schedule repair.",
            "Sections 3.2.2, 4.2.1, 4.3.1-4.3.3"
        ],
        [
            "WP4 / EP4: Familiarity of Issues",
            "Involve infrequently encountered issues or non-standard engineering problems.",
            "Adapting group recommendation and routing heuristics to developing-world tourism contexts with sudden tropical weather downpours.",
            "Sections 1.2, 2.4, 3.2.2, 4.3.3"
        ],
        [
            "WP5 / EP5: Extent of Applicable Codes",
            "Are outside problems encompassed by standards and codes of practice for professional engineering.",
            "While web protocols exist, multi-agent leisure group fairness and dynamic rain substitution have no off-the-shelf standard codes.",
            "Sections 2.4, 3.2.2, 5.1"
        ],
        [
            "WP6 / EP6: Extent of Stakeholder Involvement",
            "Involve diverse groups of stakeholders with widely varying needs.",
            "Encompasses group organizers, diverse travel members (budget vs luxury), local cultural sites, transport operators, and tourists.",
            "Sections 1.1, 3.1.5, 5.2.2"
        ],
        [
            "WP7 / EP7: Interdependence",
            "Are high-level problems including many sub-problems with significant interdependence.",
            "POI selection directly impacts daily route feasibility, which impacts meal and budget allocations, which dictates weather vulnerability.",
            "Sections 3.2.1, 3.2.2, 3.2.4"
        ]
    ]
}

TABLE_5_3_KP = {
    "caption": "Table 5.3: Mapping with Knowledge Profile Attributes (K1 - K8)",
    "headers": ["Knowledge Profile", "Category Name", "Applicable (Y/N)", "Evidence-Based Engineering Justification in TripSense"],
    "rows": [
        ["K1", "Natural Sciences", "No", "Physical science principles not directly involved."],
        ["K2", "Mathematics", "Yes", "Formulation of Haversine spherical geometry, Gini inequality calculus, and combinatorial permutation spaces."],
        ["K3", "Engineering Fundamentals", "Yes", "Data structures (graphs, priority queues), algorithmic complexity analysis (O(N^2) 2-Opt), and state machines."],
        ["K4", "Specialist Knowledge", "Yes", "Advanced knowledge in Recommender Systems, Multi-Agent Social Choice, Combinatorial Optimization, and XAI."],
        ["K5", "Engineering Design", "Yes", "Decoupled multi-tier system architecture, Pydantic schemas, REST API contracts, and responsive UI design."],
        ["K6", "Engineering Practice", "Yes", "Modern web engineering practices using React 18, Vite, Tailwind CSS, FastAPI, Uvicorn, and automated testing."],
        ["K7", "Comprehension in Society", "Yes", "Understanding tourism impact on Bangladeshi society, crowd dispersal, cultural preservation, and digital privacy."],
        ["K8", "Research Literature", "Yes", "Critical review and operational synthesis of 12 peer-reviewed academic papers across group RS and routing."]
    ]
}

SECTION_5_4_2 = {
    "title": "5.4.2 Complex Engineering Activities (EA1 - EA5)",
    "paragraphs": [
        "In addition to complex problem solving, the execution of TripSense satisfied international Complex Engineering Activity "
        "attributes (EA1 to EA5), as documented in Table 5.4."
    ]
}

TABLE_5_4_EA = {
    "caption": "Table 5.4: Mapping with Complex Engineering Activities Attributes (EA1 - EA5)",
    "headers": ["Activity ID & Name", "BAETE Definition", "TripSense Engineering Activity Evidence", "Validation Method"],
    "rows": [
        [
            "EA1: Range of Resources",
            "Involve the use of diverse resources including people, money, equipment, materials, and technologies.",
            "Integrated multi-language datasets, geospatial mapping engines, ASGI web servers, reactive frontend frameworks, and automated test runners.",
            "Report Section 4.1, Repository Codebase"
        ],
        [
            "EA2: Level of Interaction",
            "Require resolution of significant problems arising from interactions between wide-ranging or conflicting technical issues.",
            "Resolved deep conflicts between multi-user budget ceilings, category interests, daily time constraints, and geographical distance.",
            "Report Section 3.2.2, Empirical Table 4.2"
        ],
        [
            "EA3: Innovation",
            "Involve creative use of engineering principles and research-based knowledge.",
            "Formulated a novel two-phase architecture uniting Least-Misery social choice with 2-Opt TSP and dynamic weather context repair.",
            "Report Sections 1.4, 3.2.2, 4.3"
        ],
        [
            "EA4: Consequences for Society and Environment",
            "Have significant consequences in a range of contexts, characterized by diverse societal and environmental impacts.",
            "Promotes crowd dispersion to under-visited cultural sites, reduces vehicular carbon emissions via route shortening, and prevents travel disputes.",
            "Report Section 5.2, Table 5.1"
        ],
        [
            "EA5: Familiarity",
            "Can extend beyond previous experiences by applying principles to non-standard or unfamiliar problems.",
            "Pioneered a tailored group travel companion specifically optimized for the dynamic infrastructural and weather realities of Bangladesh.",
            "Report Sections 1.2, 4.1, 4.3.3"
        ]
    ]
}

SECTION_5_5 = {
    "title": "5.5 PO-Wise Evidence Traceability Matrix (PO1 - PO12)",
    "paragraphs": [
        "To establish rigorous alignment with the 12 Program Outcomes (PO1 to PO12) mandated by BAETE and Daffodil International University, "
        "Table 5.5 presents the comprehensive PO-Wise Evidence Traceability Matrix. This matrix links Course Outcomes (COs), specific engineering "
        "claims, primary report evidence artifacts, and assessment methodologies."
    ]
}

TABLE_5_5_PO = {
    "caption": "Table 5.5: PO-Wise Evidence Traceability Matrix (PO1 to PO12)",
    "headers": ["Program Outcome (PO)", "Course Outcome (CO)", "Engineering Activity & Claim", "Evidence Artifact in Report", "Relevant Section(s)", "Assessment Evidence Method"],
    "rows": [
        [
            "PO1: Engineering Knowledge",
            "CO1",
            "Formulated mathematical models for group consensus (Least-Misery) and spatial route optimization (2-Opt TSP).",
            "Equations for S_LM, Haversine distance, and 2-Opt edge-exchange formulation.",
            "Sections 1.3, 3.2.2",
            "Report + Implementation"
        ],
        [
            "PO2: Problem Analysis",
            "CO2",
            "Conducted comprehensive gap analysis of 5 commercial travel platforms and analyzed multi-member decision bottlenecks.",
            "Literature review of 12 academic papers and Table 2.2 Feature Comparison Matrix.",
            "Sections 1.2, 2.2 - 2.4",
            "Report + Presentation"
        ],
        [
            "PO3: Design/Development of Solutions",
            "CO5",
            "Architected decoupled multi-tier system with responsive client, FastAPI gateway, and dynamic weather context engine.",
            "System Architecture Diagram (Fig 3.1), ER Schema (Fig 3.2), and Sequence Diagram (Fig 3.3).",
            "Sections 3.1 - 3.2, 4.4",
            "Report + Presentation + Project"
        ],
        [
            "PO4: Investigation",
            "CO3",
            "Conducted empirical performance profiling of fairness metrics (Gini index 0.0945) and route shortening (39.4% reduction).",
            "Empirical benchmark tables (Tables 4.2 & 4.3) and performance graphs (Figs 4.1 & 4.2).",
            "Sections 4.2, 4.3",
            "Report + Implementation"
        ],
        [
            "PO5: Modern Tool Usage",
            "CO6",
            "Employed modern software engineering toolchain: Python 3.12, FastAPI, Pydantic v2, React 18, Vite, Tailwind CSS, Leaflet.",
            "Repository tech stack, package configs, and production bundle generation.",
            "Sections 3.1.2, 4.1",
            "Report + Project"
        ],
        [
            "PO6: The Engineer and Society",
            "CO7",
            "Evaluated societal impact on human well-being, interpersonal relationship preservation, and cultural tourism promotion.",
            "Socio-technical impact analysis, community economic upliftment discussion.",
            "Sections 5.2.1, 5.2.2",
            "Report"
        ],
        [
            "PO7: Environment and Sustainability",
            "CO8",
            "Demonstrated reduction in vehicle carbon emissions via route optimization and analyzed long-term economic sustainability.",
            "Carbon reduction analysis via 39.4% transit reduction; Table 5.1 budget comparison.",
            "Sections 5.2.2, 5.3",
            "Report + Project"
        ],
        [
            "PO8: Ethics",
            "CO9",
            "Applied ethical software principles: transparent explainable AI (XAI), non-discriminatory consensus, zero commercial bias, and privacy-first local caching.",
            "Ethical analysis, 'Why this place?' modal documentation, privacy design.",
            "Sections 5.2.3, 3.2.5",
            "Report"
        ],
        [
            "PO9: Individual and Team Work",
            "CO10",
            "Collaborative software execution across a 2-student engineering team with distinct ownership of backend, algorithms, frontend, and tests.",
            "Table 3.12 Task Allocation Matrix, modular Git commit tracking.",
            "Sections 3.3, 3.4",
            "Project + Presentation"
        ],
        [
            "PO10: Communication",
            "CO11",
            "Produced exhaustive, professional academic documentation, high-resolution architectural schematics, and defended project collquia.",
            "Complete Final FYDP Thesis Report, Figures 3.1-4.3, Oral Project Defense.",
            "All Chapters, Defense",
            "Report + Presentation + Defense"
        ],
        [
            "PO11: Project Management and Finance",
            "CO4",
            "Formulated 48-week academic project plan, Gantt chart, risk mitigation matrix, and comparative project budget.",
            "Tables 3.10, 3.11, 3.13, and Table 5.1 (itemized BDT budget comparison).",
            "Sections 3.3, 3.5, 5.3",
            "Report + Presentation"
        ],
        [
            "PO12: Life-Long Learning",
            "CO12",
            "Demonstrated self-directed mastery of emerging technologies (FastAPI ASGI, Pydantic v2, Vite, Leaflet, XAI heuristics) and chartered future research.",
            "Honest technical limitation analysis and future research roadmap.",
            "Sections 6.2, 6.3",
            "Report + Project"
        ]
    ]
}

SECTION_5_6 = {
    "title": "5.6 Chapter Summary",
    "paragraphs": [
        "In this chapter, we conducted a rigorous evaluation of TripSense against international engineering standards and BAETE OBE criteria. "
        "We demonstrated compliance with ISO/IEC 25010 and RESTful communication standards, detailed positive impacts on human well-being, "
        "local economies, and environmental sustainability, and established financial viability via a 90.3% cost reduction over commercial SaaS. "
        "Finally, we systematically mapped the project against Complex Engineering Problem attributes (EP1-EP7), Knowledge Profiles (K1-K8), "
        "Complex Activities (EA1-EA5), and all 12 Program Outcomes (PO1-PO12). Chapter 6 concludes the report with a synthesis of contributions, "
        "limitations, and future directions."
    ]
}
