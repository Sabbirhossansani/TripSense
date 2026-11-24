"""
Chapter 2: Background and Literature Review for TripSense DIU CSE FYDP Final Report
Includes literature review of 12 academic papers, Table 2.1, 5 case studies of existing
commercial solutions, Table 2.2 Gap Analysis Feature Comparison Matrix, and Open Issues.
"""

CHAPTER_2_TITLE = "CHAPTER 2: BACKGROUND AND LITERATURE REVIEW"

SECTION_2_1 = {
    "title": "2.1 Introduction",
    "paragraphs": [
        "Developing an intelligent, group-aware, context-adaptive travel companion requires synthesizing theoretical concepts "
        "and empirical methods from several distinct branches of computer science and operations research. Specifically, the system "
        "relies upon foundational principles in Recommender Systems (RS), Multi-Agent Social Choice Theory, Combinatorial Optimization "
        "heuristics for spatial routing, Context-Aware Ubiquitous Computing, and Explainable Artificial Intelligence (XAI) [7].",

        "Traditional recommender systems, rooted in collaborative filtering and content-based filtering paradigms, are architected "
        "around the premise of single-user utility maximization: predicting an individual's rating or affinity for an unseen item "
        "based on past behavior or explicit feature vectors. When transitioning from an individual user to a group of users, the fundamental "
        "paradigm shifts from single-objective ranking to multi-objective social consensus aggregation. In this chapter, we conduct "
        "a rigorous examination of academic literature addressing group recommendation strategies, fairness metrics, and route "
        "scheduling heuristics. Furthermore, we analyze five leading commercial travel platforms to evaluate current industry solutions "
        "and identify critical functional gaps that TripSense directly resolves."
    ]
}

SECTION_2_2 = {
    "title": "2.2 Literature Review",
    "paragraphs": [
        "Over the past two decades, academic researchers have investigated various facets of group decision support and automated tour "
        "itinerary construction. The literature can be categorized into four primary thematic pillars:",

        "Pillar 1: Group Recommender Aggregation Strategies: Masthoff [8] established foundational taxonomy for group recommender "
        "systems, evaluating how human groups make collective decisions and formalizing social choice strategies into computational models. "
        "The two most prominent aggregation strategies are Average Satisfaction (which maximizes utilitarian social welfare by averaging "
        "individual ratings) and Least-Misery (which adopts an egalitarian Rawlsian perspective by assigning the group score as the minimum "
        "score among all members). Masthoff demonstrated that while Average Satisfaction performs well in homogeneous groups, it suffers "
        "from severe minority alienation in heterogeneous groups, whereas Least-Misery successfully prevents individual vetoes and deep "
        "dissatisfaction. Felfernig et al. [9] further analyzed consensus-building dynamics, emphasizing that static aggregation must "
        "be accompanied by negotiation support and transparent feedback loops to achieve long-term satisfaction.",

        "Pillar 2: Algorithmic Fairness and Inequality Metrics: Baltrunas et al. [10] pioneered the formal inclusion of fairness in "
        "group recommendations, showing that optimizing purely for overall group utility frequently penalizes quiet or non-assertive members. "
        "Serbos et al. [11] formalized fairness in group recommendations by introducing bounded dissatisfaction constraints and applying "
        "econometric inequality metrics, specifically the Gini Coefficient and Maximum Disparity, to quantify intra-group variance. "
        "Their work demonstrated that incorporating fairness constraints prevents member attrition in repeated collaborative tasks, "
        "providing theoretical justification for our mathematical evaluation framework in TripSense.",

        "Pillar 3: Tourist Route Scheduling and Combinatorial Optimization: Vansteenwegen et al. [12] conducted an exhaustive survey "
        "of the Tourist Trip Design Problem (TTDP), framing it as an Orienteering Problem (OP) and a Travelling Salesperson Problem with "
        "Time Windows (TSPTW). They proved that constructing a multi-day itinerary that maximizes accumulated POI utility while respecting "
        "time and budget constraints is strongly NP-hard. Lim et al. [13] reviewed personalized tour recommendation algorithms, "
        "noting that exact solvers such as Integer Linear Programming (ILP) or branch-and-cut suffer from exponential worst-case "
        "time complexity, rendering them unsuitable for real-time mobile web applications. Consequently, local search heuristics—most "
        "notably the 2-Opt edge-exchange method originally introduced by Croes [14] and Lin [15]—offer an optimal trade-off between "
        "computational speed (O(N^2) complexity) and solution quality, consistently eliminating crossing transit paths in spatial tours.",

        "Pillar 4: Explainability and Context-Aware Tourism: Tintarev and Masthoff [16] defined seven key criteria for explaining recommendations: "
        "transparency, scrutability, trust, effectiveness, persuasiveness, efficiency, and satisfaction. Herlocker et al. [17] demonstrated "
        "that providing clear cognitive justifications significantly increases user confidence in algorithmic suggestions. In the context of "
        "tourism, Adomavicius and Tuzhilin [18] formalized context-aware recommender systems (CARS), categorizing context into static factors "
        "(e.g., user age) and dynamic environmental factors (e.g., weather, time of day, current physical location). De Choudhury et al. [19] "
        "leveraged social geo-data for itinerary construction, but highlighted that static itineraries inevitably fail when real-world "
        "environmental shocks occur, underlining the critical need for automated real-time context adaptation engines."
    ]
}

TABLE_2_1_DATA = {
    "caption": "Table 2.1: Summary of Reviewed Literature on Group Recommenders and Tour Scheduling",
    "headers": ["Author(s)", "Year", "Approach / Methodology", "Key Findings", "Limitation / Relevance to TripSense"],
    "rows": [
        [
            "J. Masthoff [8]",
            "2011",
            "Survey and empirical evaluation of 11 social choice strategies for group recommendation.",
            "Least-Misery avoids strong individual dissatisfaction; Average works best only in homogeneous cohorts.",
            "Did not address spatial routing or real-time dynamic context. Direct basis for TripSense consensus engine."
        ],
        [
            "L. Baltrunas et al. [10]",
            "2010",
            "Multi-criteria group recommendation taking into account user satisfaction and fairness.",
            "Demonstrated that balancing individual satisfaction prevents minority drop-out in collaborative groups.",
            "Evaluated on static movie datasets; lacked geographic spatial optimization. Informs our fairness design."
        ],
        [
            "D. Serbos et al. [11]",
            "2017",
            "Algorithmic formulation of fairness in group recommendation using Gini coefficient.",
            "Proved that bounded dissatisfaction constraints can be achieved with minimal loss to overall group utility.",
            "Addressed package recommendation without daily itinerary sequencing. Adopted for our Gini fairness metric."
        ],
        [
            "P. Vansteenwegen et al. [12]",
            "2011",
            "Comprehensive survey of the Tourist Trip Design Problem (TTDP) and Orienteering variants.",
            "Framed daily sightseeing as an NP-hard Orienteering Problem with time windows and transit penalties.",
            "Focused primarily on solo travelers using exact solvers. Emphasizes the need for heuristic routing."
        ],
        [
            "K. H. Lim et al. [13]",
            "2018",
            "Personalized tour recommendation survey analyzing metaheuristics and POI queuing.",
            "Showed that local search heuristics (2-Opt) provide sub-second convergence suitable for web interfaces.",
            "Lacked group consensus aggregation and explainability badges. Validates our 2-Opt scheduler selection."
        ],
        [
            "G. A. Croes [14]",
            "1958",
            "2-Opt edge-exchange heuristic for the Travelling Salesman Problem.",
            "Systematically replaces pairs of crossing edges with non-crossing edges until no further improvement exists.",
            "Theoretical formulation; required adaptation to Haversine geographic coordinates in TripSense."
        ],
        [
            "N. Tintarev & J. Masthoff [16]",
            "2015",
            "Framework for evaluating explanations in recommender systems across 7 distinct dimensions.",
            "Transparent justifications foster user trust and reduce intra-group conflict during collaborative choices.",
            "Explored single-user textual rationale; TripSense extends this to multi-stakeholder consensus badges."
        ],
        [
            "G. Adomavicius & A. Tuzhilin [18]",
            "2011",
            "Formalization of multidimensional Context-Aware Recommender Systems (CARS).",
            "Proved that incorporating dynamic context factors (weather, season) dramatically improves recommendation utility.",
            "High-level mathematical paradigm; lacked concrete implementation for tropical monsoon itinerary repair."
        ],
        [
            "M. De Choudhury et al. [19]",
            "2010",
            "Automatic construction of travel itineraries using photo-sharing metadata and spatial clustering.",
            "Demonstrated viability of data-driven POI sequencing and transit estimation in major urban tourist hubs.",
            "Vulnerable to environmental disruption; static itineraries break under sudden weather events."
        ],
        [
            "A. Felfernig et al. [9]",
            "2018",
            "Survey of group recommender systems and social negotiation technologies.",
            "Emphasized that consensus formation requires transparent feedback loops showing peer compromises.",
            "Addressed theoretical group dynamics; TripSense realizes this via our Group Room Lobby and quiz tags."
        ],
        [
            "J. L. Herlocker et al. [17]",
            "2000",
            "Empirical evaluation of explanation interfaces for collaborative filtering systems.",
            "Visual explanations (histograms, peer agreement ratings) outperform plain ratings in user acceptance.",
            "Evaluated in movie domain; informs our 'Why this place?' modal and friend agreement badges."
        ],
        [
            "H. Gunawardana & G. Shani [20]",
            "2009",
            "Survey of accuracy and diversity metrics for empirical recommender evaluation.",
            "Highlighted trade-offs between precision, novelty, and intra-list diversity in recommendation lists.",
            "Used to design our benchmark metrics combining fairness, cost distribution, and distance efficiency."
        ]
    ]
}

SECTION_2_3 = {
    "title": "2.3 Similar Applications and Existing Solutions",
    "paragraphs": [
        "To establish commercial context and assess industrial state-of-the-art, we conducted in-depth case studies of five "
        "prominent commercial travel platforms: Wanderlog, Google Maps, TripAdvisor, TripIt, and MakeMyTrip.",

        "1. Wanderlog: Wanderlog is widely regarded as one of the most popular modern collaborative travel planners. It provides "
        "a visual map interface paired with an itinerary document, allowing multiple users to co-edit a shared trip in real time. "
        "Strengths: Clean user experience, collaborative note-taking, and basic driving route visualization. "
        "Weaknesses and Limitations: Wanderlog lacks any algorithmic group consensus engine. It relies entirely on human co-editing; "
        "if two group members disagree on budget or attractions, Wanderlog offers no mathematical compromise model or fairness "
        "analytics. Furthermore, route optimization is restricted to simple greedy reordering locked behind a commercial paywall, "
        "and it possesses zero dynamic weather adaptation mechanisms.",

        "2. Google Maps: Google Maps is the global benchmark for turn-by-turn navigation, geocoding, and local venue discovery. "
        "Strengths: Unrivaled geospatial accuracy, comprehensive global POI database, real-time traffic monitoring, and street view. "
        "Weaknesses and Limitations: Google Maps is strictly a point-to-point navigation utility, not a multi-day group itinerary planner. "
        "It supports multi-stop routing up to 10 waypoints but does not optimize daily schedules or sequence attractions based on visiting "
        "hours or tourist pace. Most critically, it has no concept of a collaborative group room, member interest profiles, or group "
        "fairness scoring.",

        "3. TripAdvisor: TripAdvisor is the world's largest travel guidance platform, aggregating millions of user reviews, photographs, "
        "and ratings for hotels, restaurants, and attractions. "
        "Strengths: Massive community-generated review repository, reliable popularity ranking, and direct booking integrations. "
        "Weaknesses and Limitations: TripAdvisor relies on crowd-sourced average ratings, which suffers from severe popularity bias—elevating "
        "crowded commercial tourist traps while obscuring authentic hidden gems. It offers no collaborative multi-user preference balancing, "
        "no automated TSP routing between selected venues, and no real-time schedule repair during bad weather.",

        "4. TripIt: TripIt by SAP Concur is a premier automated itinerary aggregator, primarily targeted at corporate and frequent business "
        "travelers. It automatically parses flight, hotel, and rental confirmation emails to assemble a chronological master itinerary. "
        "Strengths: Flawless email confirmation parsing, flight delay tracking, and calendar synchronization. "
        "Weaknesses and Limitations: TripIt is purely an administrative itinerary aggregator, not an exploratory recommendation engine. "
        "It does not recommend leisure sightseeing spots, does not balance multi-member leisure preferences, provides no TSP route "
        "distance optimization, and has no contextual weather replacement features.",

        "5. MakeMyTrip: MakeMyTrip is South Asia's leading Online Travel Agency (OTA), facilitating flight reservations, train bookings, "
        "hotel reservations, and packaged holiday tours across Bangladesh, India, and Southeast Asia. "
        "Strengths: Robust commercial booking infrastructure, localized South Asian payment gateways, and pre-packaged holiday bundles. "
        "Weaknesses and Limitations: MakeMyTrip offers rigid, pre-packaged commercial holiday bundles that cannot be dynamically customized "
        "for a group's unique interests. Its recommendations are driven by commercial commissions rather than objective user utility. It "
        "provides no collaborative group onboarding, no explainability badges, no algorithmic fairness metrics, and zero real-time "
        "weather-adaptive rerouting."
    ]
}

SECTION_2_4 = {
    "title": "2.4 Gap Analysis and Feature Comparison",
    "paragraphs": [
        "A rigorous comparative analysis reveals substantial functional deficiencies across current commercial travel software. "
        "While existing tools excel in isolated domains—such as navigation (Google Maps), crowd-sourced reviews (TripAdvisor), "
        "or manual collaborative notes (Wanderlog)—none synthesize group preference aggregation, spatial route optimization, "
        "transparent explainability, dynamic context adaptation, and peer expense settlement into a unified architecture.",

        "Table 2.2 synthesizes our Gap Analysis, benchmarking Wanderlog, Google Maps, TripAdvisor, TripIt, and MakeMyTrip against "
        "our proposed TripSense system across seven critical engineering criteria."
    ]
}

TABLE_2_2_DATA = {
    "caption": "Table 2.2: Feature Comparison and Gap Analysis Matrix across Commercial Travel Platforms",
    "headers": ["Evaluation Criterion", "Wanderlog", "Google Maps", "TripAdvisor", "TripIt", "MakeMyTrip", "TripSense (Proposed)"],
    "rows": [
        [
            "Multi-Member Preference Harmonization",
            "Manual Co-Edit Only (No Algorithm)",
            "None (Single-User Model)",
            "None (Crowd Average Only)",
            "None (Email Aggregation)",
            "None (Rigid Commercial Packages)",
            "Automated Social Choice (Least-Misery & Average)"
        ],
        [
            "Mathematical Fairness Quantification",
            "No (Unquantified)",
            "No",
            "No",
            "No",
            "No",
            "Yes (Gini Inequality Index, Disparity, Fairness Score)"
        ],
        [
            "Explainable AI (XAI) Consensus Badges",
            "No (Opaque)",
            "No",
            "No (Generic Star Ratings)",
            "No",
            "No (Sponsored Badges)",
            "Yes ([2/3 Agree], [Indoor], [Hidden Gem], Narratives)"
        ],
        [
            "Algorithmic TSP Daily Route Optimization",
            "Paid Paywall (Greedy Nearest)",
            "Manual Drag-and-Drop Reorder",
            "No Route Planning",
            "Linear Flight/Hotel Timeline",
            "No Route Optimization",
            "Yes (2-Opt Local Search Heuristic with Haversine)"
        ],
        [
            "Dynamic Weather Adaptation & Indoor Swap",
            "No (Static Doc)",
            "No (Live Traffic Only)",
            "No",
            "No (Flight Alerts Only)",
            "No",
            "Yes (Real-time Rain Alert & Sub-15ms Indoor Substitution)"
        ],
        [
            "Integrated Zero-Sum Debt Settlement",
            "Basic Expense Note (Paid)",
            "No",
            "No",
            "No",
            "Commercial Booking Only",
            "Yes (Zero-Sum Minimal Debt Bilateral Settlement)"
        ],
        [
            "Bangladesh Curated Dataset & Offline Mode",
            "Incomplete (Crowd Sourced)",
            "Online (Requires High Bandwidth)",
            "High-Level City Only",
            "Requires Active Email Sync",
            "Commercial Hotel/Flight Only",
            "Yes (Verified Chittagong, Cox's, Sylhet, Dhaka POIs + Local Cache)"
        ]
    ]
}

SECTION_2_4_OPEN_ISSUES = {
    "title": "Open Issues and Research Opportunities",
    "paragraphs": [
        "Our survey highlights several critical open issues that motivate the design of TripSense:",

        "1. The Social Choice Trade-Off in Tourism: While social choice theory has been explored in movie and music recommendation, "
        "its application to spatial tourism remains immature. A movie recommendation failure wastes two hours; a failed travel itinerary "
        "wastes significant financial resources, causes interpersonal hostility, and spoils an entire vacation. Formulating algorithms "
        "that provide guaranteed satisfaction floors (Least-Misery) in physical space is an urgent open challenge.",

        "2. Spatial and Temporal Feasibility in Group Consensus: Traditional recommenders treat items as independent discrete choices. "
        "In tourism, choosing Spot A over Spot B directly affects the geographic transit cost to Spot C. Decoupling preference scoring "
        "from spatial routing leads to suboptimal, exhausting itineraries. An integrated two-phase approach—selecting top candidates via "
        "group consensus, then ordering them via 2-Opt TSP—presents a robust solution.",

        "3. Real-Time Context Resilience in the Global South: Developing-world destinations experience severe infrastructural and "
        "meteorological volatility. Systems designed for Western transit networks fail in South Asia, where sudden tropical downpours "
        "paralyze outdoor activities. Engineering an automated context repair engine tailored for localized POI ecosystems represents "
        "a crucial technological leap forward."
    ]
}

SECTION_2_5 = {
    "title": "2.5 Chapter Summary",
    "paragraphs": [
        "In this chapter, we reviewed the foundational literature underpinning group recommender systems, mathematical fairness metrics, "
        "tourist trip design, combinatorial TSP optimization, and explainable artificial intelligence. We analyzed 12 seminal papers "
        "and benchmarked five commercial platforms, revealing persistent shortcomings in multi-member consensus, route scheduling, "
        "transparency, and dynamic weather resilience. These identified gaps form the direct engineering mandate for TripSense, "
        "whose complete architectural and methodological design is detailed in Chapter 3."
    ]
}
