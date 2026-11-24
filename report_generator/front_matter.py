"""
Front Matter for TripSense DIU CSE FYDP Final Report
Includes Title, Board of Examiners, Declaration, Acknowledgements, Abstract,
Table of Contents, List of Figures, and List of Tables.
"""

PROJECT_TITLE = "TripSense: An Explainable, Group-Aware, and Context-Adaptive Travel Companion Application"

STUDENTS = [
    {"name": "Saniul Islam", "id": "211-15-4321", "dept": "Department of Computer Science and Engineering", "inst": "Daffodil International University"},
    {"name": "Tanvir Ahmed", "id": "211-15-4322", "dept": "Department of Computer Science and Engineering", "inst": "Daffodil International University"}
]

SUPERVISORS = {
    "supervisor": {
        "name": "Dr. Mohammad Jahangir Alam",
        "designation": "Associate Professor",
        "dept": "Department of Computer Science and Engineering",
        "inst": "Daffodil International University"
    },
    "co_supervisor": {
        "name": "Ms. Farzana Akter",
        "designation": "Lecturer",
        "dept": "Department of Computer Science and Engineering",
        "inst": "Daffodil International University"
    }
}

BOARD_OF_EXAMINERS = [
    {
        "name": "Professor Dr. Sheak Rashed Haider Noori",
        "role": "Chairman",
        "designation": "Professor and Head",
        "dept": "Department of Computer Science and Engineering",
        "inst": "Daffodil International University"
    },
    {
        "name": "Dr. S. M. Aminul Haque",
        "role": "Internal Examiner 1",
        "designation": "Associate Professor and Associate Head",
        "dept": "Department of Computer Science and Engineering",
        "inst": "Daffodil International University"
    },
    {
        "name": "Dr. Neil M. S. Rahman",
        "role": "Internal Examiner 2",
        "designation": "Assistant Professor",
        "dept": "Department of Computer Science and Engineering",
        "inst": "Daffodil International University"
    },
    {
        "name": "Dr. Md. Mostofa Akbar",
        "role": "External Examiner",
        "designation": "Professor",
        "dept": "Department of Computer Science and Engineering",
        "inst": "Bangladesh University of Engineering and Technology (BUET)"
    }
]

SUBMISSION_DATE = "October 2026"
DEFENSE_DATE = "October 24, 2026"

APPROVAL_TEXT = (
    "This Project titled \"TripSense: An Explainable, Group-Aware, and Context-Adaptive "
    "Travel Companion Application\", submitted by Saniul Islam, ID: 211-15-4321 and "
    "Tanvir Ahmed, ID: 211-15-4322 to the Department of Computer Science and Engineering, "
    "Daffodil International University, has been accepted as satisfactory for the partial "
    "fulfillment of the requirements for the degree of Bachelor of Science in Computer Science "
    "and Engineering and approved as to its style and contents. The presentation and comprehensive "
    "defense has been successfully held on October 24, 2026."
)

DECLARATION_TEXT = (
    "We hereby declare that this project has been carried out by us under the direct supervision "
    "of Dr. Mohammad Jahangir Alam, Associate Professor, and co-supervision of Ms. Farzana Akter, "
    "Lecturer, Department of Computer Science and Engineering, Daffodil International University. "
    "We further declare that neither this project report nor any part thereof has been submitted "
    "elsewhere for the award of any academic degree, diploma, or professional qualification. "
    "All primary algorithms, software artifacts, system architectural models, empirical evaluation "
    "benchmarks, and documentation presented in this report represent our original scholarly and "
    "engineering work, with all external literature and software dependencies appropriately cited."
)

ACKNOWLEDGEMENTS_TEXT = [
    "First and foremost, we express our profound gratitude to the Almighty for His divine blessings, "
    "endurance, and guidance throughout our academic journey, enabling us to bring this Final Year Design "
    "Project (FYDP) to successful fruition.",

    "We wish to express our heartfelt indebtedness and deepest respect to our respected supervisor, "
    "Dr. Mohammad Jahangir Alam, Associate Professor, Department of Computer Science and Engineering, "
    "Daffodil International University. His scholarly mentorship, incisive technical feedback, continuous "
    "intellectual encouragement, and meticulous guidance across all project phases—from theoretical "
    "algorithmic formulation to empirical evaluation—have been invaluable.",

    "We extend our sincere appreciation to our co-supervisor, Ms. Farzana Akter, Lecturer, Department "
    "of Computer Science and Engineering, for her invaluable advice on software architectural modeling, "
    "system verification, and presentation formatting throughout the research and development lifecycle.",

    "We express our profound thanks to Professor Dr. Sheak Rashed Haider Noori, Head of the Department "
    "of Computer Science and Engineering, and the distinguished faculty members of Daffodil International "
    "University for fostering an inspiring academic environment, providing access to computing facilities, "
    "and steering an Outcome-Based Education (OBE) curriculum aligned with international BAETE standards.",

    "We are also thankful to our classmates and academic peers whose constructive critiques during departmental "
    "colloquiums enriched the system design. Lastly, we express our deepest veneration and love to our parents "
    "and families, whose unwavering moral and financial support, patience, and sacrifices have been our "
    "greatest source of strength."
]

ABSTRACT_TEXT = (
    "Collaborative travel planning in multi-member groups represents a notoriously challenging decision-making problem, "
    "frequently derailed by conflicting individual preferences, disparate financial budgets, divergent travel paces, and "
    "the computational intractability of daily routing under unpredictable environmental dynamics. Existing commercial "
    "travel platforms cater predominantly to solo travelers or rely on opaque, black-box recommendation models that fail "
    "to explain collective trade-offs or recover dynamically from real-time disruptions such as tropical monsoon rainfall. "
    "In this Final Year Design Project, we present TripSense, an explainable, group-aware, and context-adaptive travel companion "
    "application engineered specifically for collaborative group tourism. TripSense integrates a Group Consensus Recommender "
    "employing Least-Misery and Average-Satisfaction social choice strategies to harmonize conflicting traveler preferences, "
    "guaranteeing mathematically bounded dissatisfaction verified by an empirical Gini inequality index of 0.0945, a satisfaction "
    "disparity of 16.99%, and a Group Fairness Score of 74.52/100. To eliminate group friction, an Explainable AI (XAI) transparent "
    "badging and natural language justification pipeline articulates multi-stakeholder consensus rationale for every candidate "
    "attraction. For efficient itinerary scheduling, a 2-Opt local search heuristic solves the daily Travelling Salesperson "
    "Problem (TSP), achieving a 39.4% reduction in transit distance over naive ordering across verified Bangladesh tourism hubs "
    "(Chittagong, Cox's Bazar, Sylhet, and Dhaka). Furthermore, a Dynamic Context Adaptation Engine executes sub-15ms real-time "
    "itinerary repair during heavy rain events by substituting outdoor spots with culturally relevant indoor landmarks while "
    "recomputing transit metrics. Delivered as a responsive progressive web application paired with an asynchronous FastAPI "
    "backend, peer expense ledger, and offline caching, TripSense demonstrates full compliance with ISO/IEC 25010 software quality "
    "standards and BAETE complex engineering problem attributes."
)

TABLE_OF_CONTENTS = [
    ("APPROVAL", "ii"),
    ("DECLARATION", "iii"),
    ("ACKNOWLEDGEMENTS", "iv"),
    ("ABSTRACT", "v"),
    ("LIST OF FIGURES", "viii"),
    ("LIST OF TABLES", "ix"),
    ("CHAPTER 1: INTRODUCTION", "1"),
    ("  1.1 Introduction and Background", "1"),
    ("  1.2 Problem Statement", "2"),
    ("  1.3 Computational Motivation", "3"),
    ("  1.4 Specific Objectives", "5"),
    ("  1.5 Methodology Summary", "6"),
    ("  1.6 Project Outcome", "7"),
    ("  1.7 Organization of the Report", "8"),
    ("CHAPTER 2: BACKGROUND AND LITERATURE REVIEW", "9"),
    ("  2.1 Introduction", "9"),
    ("  2.2 Literature Review", "10"),
    ("  2.3 Similar Applications and Existing Solutions", "15"),
    ("  2.4 Gap Analysis and Feature Comparison", "19"),
    ("  2.5 Chapter Summary", "22"),
    ("CHAPTER 3: DESIGN AND METHODOLOGY", "23"),
    ("  3.1 Requirements Analysis and Design Specification", "23"),
    ("    3.1.1 Overview and Engineering Philosophy", "23"),
    ("    3.1.2 Hardware and Software Requirements", "24"),
    ("    3.1.3 Functional Requirements (FR1 - FR10)", "25"),
    ("    3.1.4 Non-Functional Requirements (NFR1 - NFR8)", "27"),
    ("    3.1.5 Actors and Use Case Specifications", "29"),
    ("  3.2 Detailed Design", "33"),
    ("    3.2.1 Multi-Tier Decoupled System Architecture", "33"),
    ("    3.2.2 Algorithmic Formulation and Mathematical Models", "35"),
    ("    3.2.3 Data Design and Entity-Relationship Schema", "41"),
    ("    3.2.4 UML Class Diagram and Sequence Workflows", "45"),
    ("    3.2.5 User Interface Design and Information Flow", "48"),
    ("    3.2.6 Alternate Solutions and Trade-Off Rationale", "50"),
    ("  3.3 Project Plan and Timeline", "51"),
    ("  3.4 Task Allocation", "54"),
    ("  3.5 Risk Analysis, Challenges, and Mitigation", "55"),
    ("  3.6 Chapter Summary", "57"),
    ("CHAPTER 4: IMPLEMENTATION AND RESULTS", "58"),
    ("  4.1 Implementation Setup and Technical Stack", "58"),
    ("  4.2 Comprehensive Testing and Quality Assurance", "61"),
    ("    4.2.1 Unit Testing and Mathematical Invariant Checks", "61"),
    ("    4.2.2 API Gateway Integration Testing", "63"),
    ("    4.2.3 System Resilience and Edge Case Testing", "65"),
    ("    4.2.4 User Interface Black-Box Test Cases", "66"),
    ("  4.3 Algorithmic Performance Evaluation and Discussion", "70"),
    ("    4.3.1 Group Consensus and Social Welfare Evaluation", "70"),
    ("    4.3.2 2-Opt Heuristic TSP Route Optimization Benchmarks", "73"),
    ("    4.3.3 Dynamic Context Weather Adaptation Latency", "75"),
    ("    4.3.4 Execution Latency and Computational Profiling", "76"),
    ("  4.4 Final System Demonstration", "77"),
    ("  4.5 Chapter Summary", "82"),
    ("CHAPTER 5: ENGINEERING STANDARDS AND DESIGN CHALLENGES", "83"),
    ("  5.1 Compliance with Engineering Standards", "83"),
    ("    5.1.1 Software Quality and Process Standards (ISO/IEC 25010)", "83"),
    ("    5.1.2 Communication and Architectural Protocols", "86"),
    ("    5.1.3 Hardware and Web Standards", "87"),
    ("  5.2 Impact on Society, Environment, and Sustainability", "88"),
    ("    5.2.1 Impact on Life and Human Well-Being", "88"),
    ("    5.2.2 Impact on Society, Local Economy, and Ecology", "89"),
    ("    5.2.3 Ethical Aspects, Bias Prevention, and Privacy", "91"),
    ("    5.2.4 Long-Term Sustainability Plan", "92"),
    ("  5.3 Project Management and Financial Analysis", "93"),
    ("  5.4 Complex Engineering Problem (BAETE OBE Criteria)", "96"),
    ("    5.4.1 Complex Problem Solving Mapping (WP1 - WP7 / EP1 - EP7)", "96"),
    ("    5.4.2 Knowledge Profile Mapping (K1 - K8)", "98"),
    ("    5.4.3 Complex Engineering Activities (EA1 - EA5)", "100"),
    ("  5.5 PO-Wise Evidence Traceability Matrix (PO1 - PO12)", "102"),
    ("  5.6 Chapter Summary", "106"),
    ("CHAPTER 6: CONCLUSION", "107"),
    ("  6.1 Summary of Contributions", "107"),
    ("  6.2 Technical and Operational Limitations", "108"),
    ("  6.3 Future Work and Research Directions", "109"),
    ("REFERENCES", "111")
]

LIST_OF_FIGURES = [
    ("Figure 3.1", "TripSense Multi-Tier Decoupled System Architecture", "34"),
    ("Figure 3.2", "TripSense Relational and Document Entity-Relationship (ER) Schema", "42"),
    ("Figure 3.3", "UML Class Diagram: Domain Entities, Algorithmic Services, and Structural Relations", "46"),
    ("Figure 3.4", "UML Sequence Diagram: Group Plan Synthesis and Dynamic Weather Adaptation Workflow", "48"),
    ("Figure 3.5", "Algorithmic Recommendation and 2-Opt TSP Scheduling Flowchart", "38"),
    ("Figure 4.1", "Empirical 2-Opt TSP Route Optimization Benchmark (Chittagong Day Tour)", "74"),
    ("Figure 4.2", "Group Satisfaction Distribution and Fairness Metric Dashboard", "72"),
    ("Figure 4.3", "Dynamic Context-Aware Weather Adaptation Decision Tree", "76"),
    ("Figure 4.4", "System Demonstration: Destination Selection and 60-Second Preference Onboarding Quiz", "78"),
    ("Figure 4.5", "System Demonstration: Consensus Itinerary, Leaflet Map, and Explainability Modal", "80"),
    ("Figure 4.6", "System Demonstration: Dynamic Monsoon Weather Alert and Peer Expense Splitter", "81")
]

LIST_OF_TABLES = [
    ("Table 2.1", "Summary of Reviewed Literature on Group Recommenders and Tour Scheduling", "14"),
    ("Table 2.2", "Feature Comparison and Gap Analysis Matrix across Commercial Travel Platforms", "20"),
    ("Table 3.1", "Detailed Functional Requirements Specification (FR1 to FR10)", "26"),
    ("Table 3.2", "Non-Functional Requirements Specification (NFR1 to NFR8)", "28"),
    ("Table 3.3", "Use Case Specification: UC-01 Collaborative Group Room & Preference Intake", "30"),
    ("Table 3.4", "Use Case Specification: UC-02 Consensus-Aware Itinerary Generation", "31"),
    ("Table 3.5", "Use Case Specification: UC-03 Dynamic Context Weather Replanning", "32"),
    ("Table 3.6", "Use Case Specification: UC-04 Shared Expense Tracking and Debt Settlement", "33"),
    ("Table 3.7", "Data Dictionary: User Member and Group Room Schema", "43"),
    ("Table 3.8", "Data Dictionary: Spot POI and Daily Schedule Schema", "44"),
    ("Table 3.9", "Data Dictionary: Expense Item and Settlement Transaction Schema", "45"),
    ("Table 3.10", "TripSense 48-Week Academic Engineering Project Plan and Milestones", "52"),
    ("Table 3.11", "Gantt Chart Work Breakdown across Academic Year", "53"),
    ("Table 3.12", "Student Task Allocation and Contribution Matrix", "54"),
    ("Table 3.13", "Engineering Risk Matrix, Challenges, and Validated Mitigations", "56"),
    ("Table 4.1", "Comprehensive Unit Test Cases and Mathematical Invariant Validation", "62"),
    ("Table 4.2", "Comprehensive API Gateway Integration Test Cases", "64"),
    ("Table 4.3", "Comprehensive System Resilience and Edge-Case Test Cases", "66"),
    ("Table 4.4", "Comprehensive System and UI Black-Box Test Cases with Validation Results", "68"),
    ("Table 4.5", "Empirical Social Choice Aggregation Comparison (Least-Misery vs Average Satisfaction)", "71"),
    ("Table 4.6", "Chittagong 2-Day Daily Schedule Transit and Optimization Benchmark", "74"),
    ("Table 5.1", "Itemized Project Budget and Commercial Cloud vs Self-Hosted Comparison", "95"),
    ("Table 5.2", "Mapping with Complex Engineering Problem Attributes (WP1 - WP7 / EP1 - EP7)", "97"),
    ("Table 5.3", "Mapping with Knowledge Profile Attributes (K1 - K8)", "99"),
    ("Table 5.4", "Mapping with Complex Engineering Activities Attributes (EA1 - EA5)", "101"),
    ("Table 5.5", "PO-Wise Evidence Traceability Matrix (PO1 to PO12)", "103")
]
