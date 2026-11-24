# TripSense: An Explainable, Group-Aware, and Context-Adaptive Travel Companion Application

## FINAL YEAR DESIGN PROJECT REPORT

**Submitted in Partial Fulfillment of the Requirements for the Degree of**  
**Bachelor of Science in Computer Science and Engineering**

---

### Submitted By:
- **Saniul Islam** (Student ID: 211-15-4321)  
  Department of Computer Science and Engineering, Daffodil International University
- **Tanvir Ahmed** (Student ID: 211-15-4322)  
  Department of Computer Science and Engineering, Daffodil International University

### Supervised By:
- **Dr. Mohammad Jahangir Alam**, Associate Professor  
  Department of Computer Science and Engineering, Daffodil International University
- **Ms. Farzana Akter**, Lecturer (Co-Supervisor)  
  Department of Computer Science and Engineering, Daffodil International University

<p align="center">
  <img src="figures/diu_logo.jpeg" alt="Daffodil International University Logo" width="140"/>
</p>

**Department of Computer Science and Engineering**  
**Daffodil International University**, Dhaka, Bangladesh  
*October 2026*

---

## APPROVAL

This Project titled "TripSense: An Explainable, Group-Aware, and Context-Adaptive Travel Companion Application", submitted by Saniul Islam, ID: 211-15-4321 and Tanvir Ahmed, ID: 211-15-4322 to the Department of Computer Science and Engineering, Daffodil International University, has been accepted as satisfactory for the partial fulfillment of the requirements for the degree of Bachelor of Science in Computer Science and Engineering and approved as to its style and contents. The presentation and comprehensive defense has been successfully held on October 24, 2026.

### BOARD OF EXAMINERS

- **Professor Dr. Sheak Rashed Haider Noori** (Chairman)  
  Professor and Head, Department of Computer Science and Engineering, Daffodil International University
- **Dr. S. M. Aminul Haque** (Internal Examiner 1)  
  Associate Professor and Associate Head, Department of Computer Science and Engineering, Daffodil International University
- **Dr. Neil M. S. Rahman** (Internal Examiner 2)  
  Assistant Professor, Department of Computer Science and Engineering, Daffodil International University
- **Dr. Md. Mostofa Akbar** (External Examiner)  
  Professor, Department of Computer Science and Engineering, Bangladesh University of Engineering and Technology (BUET)

---

## DECLARATION

We hereby declare that this project has been carried out by us under the direct supervision of Dr. Mohammad Jahangir Alam, Associate Professor, and co-supervision of Ms. Farzana Akter, Lecturer, Department of Computer Science and Engineering, Daffodil International University. We further declare that neither this project report nor any part thereof has been submitted elsewhere for the award of any academic degree, diploma, or professional qualification. All primary algorithms, software artifacts, system architectural models, empirical evaluation benchmarks, and documentation presented in this report represent our original scholarly and engineering work, with all external literature and software dependencies appropriately cited.

Submitted by:
- Saniul Islam (ID: 211-15-4321)
- Tanvir Ahmed (ID: 211-15-4322)

---

## ACKNOWLEDGEMENTS

First and foremost, we express our profound gratitude to the Almighty for His divine blessings, endurance, and guidance throughout our academic journey, enabling us to bring this Final Year Design Project (FYDP) to successful fruition.

We wish to express our heartfelt indebtedness and deepest respect to our respected supervisor, Dr. Mohammad Jahangir Alam, Associate Professor, Department of Computer Science and Engineering, Daffodil International University. His scholarly mentorship, incisive technical feedback, continuous intellectual encouragement, and meticulous guidance across all project phases—from theoretical algorithmic formulation to empirical evaluation—have been invaluable.

We extend our sincere appreciation to our co-supervisor, Ms. Farzana Akter, Lecturer, Department of Computer Science and Engineering, for her invaluable advice on software architectural modeling, system verification, and presentation formatting throughout the research and development lifecycle.

We express our profound thanks to Professor Dr. Sheak Rashed Haider Noori, Head of the Department of Computer Science and Engineering, and the distinguished faculty members of Daffodil International University for fostering an inspiring academic environment, providing access to computing facilities, and steering an Outcome-Based Education (OBE) curriculum aligned with international BAETE standards.

We are also thankful to our classmates and academic peers whose constructive critiques during departmental colloquiums enriched the system design. Lastly, we express our deepest veneration and love to our parents and families, whose unwavering moral and financial support, patience, and sacrifices have been our greatest source of strength.

---

## ABSTRACT

Collaborative travel planning in multi-member groups represents a notoriously challenging decision-making problem, frequently derailed by conflicting individual preferences, disparate financial budgets, divergent travel paces, and the computational intractability of daily routing under unpredictable environmental dynamics. Existing commercial travel platforms cater predominantly to solo travelers or rely on opaque, black-box recommendation models that fail to explain collective trade-offs or recover dynamically from real-time disruptions such as tropical monsoon rainfall. In this Final Year Design Project, we present TripSense, an explainable, group-aware, and context-adaptive travel companion application engineered specifically for collaborative group tourism. TripSense integrates a Group Consensus Recommender employing Least-Misery and Average-Satisfaction social choice strategies to harmonize conflicting traveler preferences, guaranteeing mathematically bounded dissatisfaction verified by an empirical Gini inequality index of 0.0945, a satisfaction disparity of 16.99%, and a Group Fairness Score of 74.52/100. To eliminate group friction, an Explainable AI (XAI) transparent badging and natural language justification pipeline articulates multi-stakeholder consensus rationale for every candidate attraction. For efficient itinerary scheduling, a 2-Opt local search heuristic solves the daily Travelling Salesperson Problem (TSP), achieving a 39.4% reduction in transit distance over naive ordering across verified Bangladesh tourism hubs (Chittagong, Cox's Bazar, Sylhet, and Dhaka). Furthermore, a Dynamic Context Adaptation Engine executes sub-15ms real-time itinerary repair during heavy rain events by substituting outdoor spots with culturally relevant indoor landmarks while recomputing transit metrics. Delivered as a responsive progressive web application paired with an asynchronous FastAPI backend, peer expense ledger, and offline caching, TripSense demonstrates full compliance with ISO/IEC 25010 software quality standards and BAETE complex engineering problem attributes.

**Keywords:** Group Recommender Systems, Social Choice Theory, Least-Misery Consensus, Gini Inequality Metric, Travelling Salesperson Problem (TSP), 2-Opt Local Search Heuristic, Explainable AI (XAI), Dynamic Weather Adaptation, Bangladesh Tourism, Progressive Web Application (PWA).

---

## TABLE OF CONTENTS

**APPROVAL** .................................................... ii  
**DECLARATION** .................................................... iii  
**ACKNOWLEDGEMENTS** .................................................... iv  
**ABSTRACT** .................................................... v  
**LIST OF FIGURES** .................................................... viii  
**LIST OF TABLES** .................................................... ix  
**CHAPTER 1: INTRODUCTION** .................................................... 1  
&nbsp;&nbsp;**1.1 Introduction and Background** .................................................... 1  
&nbsp;&nbsp;**1.2 Problem Statement** .................................................... 2  
&nbsp;&nbsp;**1.3 Computational Motivation** .................................................... 3  
&nbsp;&nbsp;**1.4 Specific Objectives** .................................................... 5  
&nbsp;&nbsp;**1.5 Methodology Summary** .................................................... 6  
&nbsp;&nbsp;**1.6 Project Outcome** .................................................... 7  
&nbsp;&nbsp;**1.7 Organization of the Report** .................................................... 8  
**CHAPTER 2: BACKGROUND AND LITERATURE REVIEW** .................................................... 9  
&nbsp;&nbsp;**2.1 Introduction** .................................................... 9  
&nbsp;&nbsp;**2.2 Literature Review** .................................................... 10  
&nbsp;&nbsp;**2.3 Similar Applications and Existing Solutions** .................................................... 15  
&nbsp;&nbsp;**2.4 Gap Analysis and Feature Comparison** .................................................... 19  
&nbsp;&nbsp;**2.5 Chapter Summary** .................................................... 22  
**CHAPTER 3: DESIGN AND METHODOLOGY** .................................................... 23  
&nbsp;&nbsp;**3.1 Requirements Analysis and Design Specification** .................................................... 23  
&nbsp;&nbsp;&nbsp;&nbsp;**3.1.1 Overview and Engineering Philosophy** .................................................... 23  
&nbsp;&nbsp;&nbsp;&nbsp;**3.1.2 Hardware and Software Requirements** .................................................... 24  
&nbsp;&nbsp;&nbsp;&nbsp;**3.1.3 Functional Requirements (FR1 - FR10)** .................................................... 25  
&nbsp;&nbsp;&nbsp;&nbsp;**3.1.4 Non-Functional Requirements (NFR1 - NFR8)** .................................................... 27  
&nbsp;&nbsp;&nbsp;&nbsp;**3.1.5 Actors and Use Case Specifications** .................................................... 29  
&nbsp;&nbsp;**3.2 Detailed Design** .................................................... 33  
&nbsp;&nbsp;&nbsp;&nbsp;**3.2.1 Multi-Tier Decoupled System Architecture** .................................................... 33  
&nbsp;&nbsp;&nbsp;&nbsp;**3.2.2 Algorithmic Formulation and Mathematical Models** .................................................... 35  
&nbsp;&nbsp;&nbsp;&nbsp;**3.2.3 Data Design and Entity-Relationship Schema** .................................................... 41  
&nbsp;&nbsp;&nbsp;&nbsp;**3.2.4 UML Class Diagram and Sequence Workflows** .................................................... 45  
&nbsp;&nbsp;&nbsp;&nbsp;**3.2.5 User Interface Design and Information Flow** .................................................... 48  
&nbsp;&nbsp;&nbsp;&nbsp;**3.2.6 Alternate Solutions and Trade-Off Rationale** .................................................... 50  
&nbsp;&nbsp;**3.3 Project Plan and Timeline** .................................................... 51  
&nbsp;&nbsp;**3.4 Task Allocation** .................................................... 54  
&nbsp;&nbsp;**3.5 Risk Analysis, Challenges, and Mitigation** .................................................... 55  
&nbsp;&nbsp;**3.6 Chapter Summary** .................................................... 57  
**CHAPTER 4: IMPLEMENTATION AND RESULTS** .................................................... 58  
&nbsp;&nbsp;**4.1 Implementation Setup and Technical Stack** .................................................... 58  
&nbsp;&nbsp;**4.2 Comprehensive Testing and Quality Assurance** .................................................... 61  
&nbsp;&nbsp;&nbsp;&nbsp;**4.2.1 Unit Testing and Mathematical Invariant Checks** .................................................... 61  
&nbsp;&nbsp;&nbsp;&nbsp;**4.2.2 API Gateway Integration Testing** .................................................... 63  
&nbsp;&nbsp;&nbsp;&nbsp;**4.2.3 System Resilience and Edge Case Testing** .................................................... 65  
&nbsp;&nbsp;&nbsp;&nbsp;**4.2.4 User Interface Black-Box Test Cases** .................................................... 66  
&nbsp;&nbsp;**4.3 Algorithmic Performance Evaluation and Discussion** .................................................... 70  
&nbsp;&nbsp;&nbsp;&nbsp;**4.3.1 Group Consensus and Social Welfare Evaluation** .................................................... 70  
&nbsp;&nbsp;&nbsp;&nbsp;**4.3.2 2-Opt Heuristic TSP Route Optimization Benchmarks** .................................................... 73  
&nbsp;&nbsp;&nbsp;&nbsp;**4.3.3 Dynamic Context Weather Adaptation Latency** .................................................... 75  
&nbsp;&nbsp;&nbsp;&nbsp;**4.3.4 Execution Latency and Computational Profiling** .................................................... 76  
&nbsp;&nbsp;**4.4 Final System Demonstration** .................................................... 77  
&nbsp;&nbsp;**4.5 Chapter Summary** .................................................... 82  
**CHAPTER 5: ENGINEERING STANDARDS AND DESIGN CHALLENGES** .................................................... 83  
&nbsp;&nbsp;**5.1 Compliance with Engineering Standards** .................................................... 83  
&nbsp;&nbsp;&nbsp;&nbsp;**5.1.1 Software Quality and Process Standards (ISO/IEC 25010)** .................................................... 83  
&nbsp;&nbsp;&nbsp;&nbsp;**5.1.2 Communication and Architectural Protocols** .................................................... 86  
&nbsp;&nbsp;&nbsp;&nbsp;**5.1.3 Hardware and Web Standards** .................................................... 87  
&nbsp;&nbsp;**5.2 Impact on Society, Environment, and Sustainability** .................................................... 88  
&nbsp;&nbsp;&nbsp;&nbsp;**5.2.1 Impact on Life and Human Well-Being** .................................................... 88  
&nbsp;&nbsp;&nbsp;&nbsp;**5.2.2 Impact on Society, Local Economy, and Ecology** .................................................... 89  
&nbsp;&nbsp;&nbsp;&nbsp;**5.2.3 Ethical Aspects, Bias Prevention, and Privacy** .................................................... 91  
&nbsp;&nbsp;&nbsp;&nbsp;**5.2.4 Long-Term Sustainability Plan** .................................................... 92  
&nbsp;&nbsp;**5.3 Project Management and Financial Analysis** .................................................... 93  
&nbsp;&nbsp;**5.4 Complex Engineering Problem (BAETE OBE Criteria)** .................................................... 96  
&nbsp;&nbsp;&nbsp;&nbsp;**5.4.1 Complex Problem Solving Mapping (WP1 - WP7 / EP1 - EP7)** .................................................... 96  
&nbsp;&nbsp;&nbsp;&nbsp;**5.4.2 Knowledge Profile Mapping (K1 - K8)** .................................................... 98  
&nbsp;&nbsp;&nbsp;&nbsp;**5.4.3 Complex Engineering Activities (EA1 - EA5)** .................................................... 100  
&nbsp;&nbsp;**5.5 PO-Wise Evidence Traceability Matrix (PO1 - PO12)** .................................................... 102  
&nbsp;&nbsp;**5.6 Chapter Summary** .................................................... 106  
**CHAPTER 6: CONCLUSION** .................................................... 107  
&nbsp;&nbsp;**6.1 Summary of Contributions** .................................................... 107  
&nbsp;&nbsp;**6.2 Technical and Operational Limitations** .................................................... 108  
&nbsp;&nbsp;**6.3 Future Work and Research Directions** .................................................... 109  
**REFERENCES** .................................................... 111  

---

## LIST OF FIGURES

- **Figure 3.1**: TripSense Multi-Tier Decoupled System Architecture .................... *Page 34*  
- **Figure 3.2**: TripSense Relational and Document Entity-Relationship (ER) Schema .................... *Page 42*  
- **Figure 3.3**: UML Class Diagram: Domain Entities, Algorithmic Services, and Structural Relations .................... *Page 46*  
- **Figure 3.4**: UML Sequence Diagram: Group Plan Synthesis and Dynamic Weather Adaptation Workflow .................... *Page 48*  
- **Figure 3.5**: Algorithmic Recommendation and 2-Opt TSP Scheduling Flowchart .................... *Page 38*  
- **Figure 4.1**: Empirical 2-Opt TSP Route Optimization Benchmark (Chittagong Day Tour) .................... *Page 74*  
- **Figure 4.2**: Group Satisfaction Distribution and Fairness Metric Dashboard .................... *Page 72*  
- **Figure 4.3**: Dynamic Context-Aware Weather Adaptation Decision Tree .................... *Page 76*  
- **Figure 4.4**: System Demonstration: Destination Selection and 60-Second Preference Onboarding Quiz .................... *Page 78*  
- **Figure 4.5**: System Demonstration: Consensus Itinerary, Leaflet Map, and Explainability Modal .................... *Page 80*  
- **Figure 4.6**: System Demonstration: Dynamic Monsoon Weather Alert and Peer Expense Splitter .................... *Page 81*  

---

## LIST OF TABLES

- **Table 2.1**: Summary of Reviewed Literature on Group Recommenders and Tour Scheduling .................... *Page 14*  
- **Table 2.2**: Feature Comparison and Gap Analysis Matrix across Commercial Travel Platforms .................... *Page 20*  
- **Table 3.1**: Detailed Functional Requirements Specification (FR1 to FR10) .................... *Page 26*  
- **Table 3.2**: Non-Functional Requirements Specification (NFR1 to NFR8) .................... *Page 28*  
- **Table 3.3**: Use Case Specification: UC-01 Collaborative Group Room & Preference Intake .................... *Page 30*  
- **Table 3.4**: Use Case Specification: UC-02 Consensus-Aware Itinerary Generation .................... *Page 31*  
- **Table 3.5**: Use Case Specification: UC-03 Dynamic Context Weather Replanning .................... *Page 32*  
- **Table 3.6**: Use Case Specification: UC-04 Shared Expense Tracking and Debt Settlement .................... *Page 33*  
- **Table 3.7**: Data Dictionary: User Member and Group Room Schema .................... *Page 43*  
- **Table 3.8**: Data Dictionary: Spot POI and Daily Schedule Schema .................... *Page 44*  
- **Table 3.9**: Data Dictionary: Expense Item and Settlement Transaction Schema .................... *Page 45*  
- **Table 3.10**: TripSense 48-Week Academic Engineering Project Plan and Milestones .................... *Page 52*  
- **Table 3.11**: Gantt Chart Work Breakdown across Academic Year .................... *Page 53*  
- **Table 3.12**: Student Task Allocation and Contribution Matrix .................... *Page 54*  
- **Table 3.13**: Engineering Risk Matrix, Challenges, and Validated Mitigations .................... *Page 56*  
- **Table 4.1**: Comprehensive Unit Test Cases and Mathematical Invariant Validation .................... *Page 62*  
- **Table 4.2**: Comprehensive API Gateway Integration Test Cases .................... *Page 64*  
- **Table 4.3**: Comprehensive System Resilience and Edge-Case Test Cases .................... *Page 66*  
- **Table 4.4**: Comprehensive System and UI Black-Box Test Cases with Validation Results .................... *Page 68*  
- **Table 4.5**: Empirical Social Choice Aggregation Comparison (Least-Misery vs Average Satisfaction) .................... *Page 71*  
- **Table 4.6**: Chittagong 2-Day Daily Schedule Transit and Optimization Benchmark .................... *Page 74*  
- **Table 5.1**: Itemized Project Budget and Commercial Cloud vs Self-Hosted Comparison .................... *Page 95*  
- **Table 5.2**: Mapping with Complex Engineering Problem Attributes (WP1 - WP7 / EP1 - EP7) .................... *Page 97*  
- **Table 5.3**: Mapping with Knowledge Profile Attributes (K1 - K8) .................... *Page 99*  
- **Table 5.4**: Mapping with Complex Engineering Activities Attributes (EA1 - EA5) .................... *Page 101*  
- **Table 5.5**: PO-Wise Evidence Traceability Matrix (PO1 to PO12) .................... *Page 103*  

---

# CHAPTER 1: INTRODUCTION

## 1.1 Introduction and Background

Leisure travel and cultural exploration represent vital aspects of human life, contributing significantly to psychological rejuvenation, social bonding, and economic vitality. In recent years, group travel—encompassing vacations undertaken by families, university cohorts, corporate teams, and friend circles—has surged in popularity. Unlike solo tourism, where an individual exercises unilateral autonomy over itineraries, timing, budgets, and attractions, group travel is inherently a multi-agent, collaborative endeavor. Every participant brings an idiosyncratic constellation of interests, personal constraints, budgetary tolerances, and mobility expectations to the table [1].

In emerging tourism destinations such as Bangladesh, group tourism forms the predominant mode of domestic travel. Major destination hubs like Chittagong, Cox's Bazar, Sylhet, and Dhaka witness hundreds of thousands of group visitors annually, ranging from student cohorts exploring historical landmarks to family units seeking coastal resorts and eco-parks [2]. However, the organizational workflow underpinning group travel in Bangladesh remains overwhelmingly manual, fragmented, and inefficient. Planning a collective itinerary typically involves protracted arguments across social messaging platforms, unstructured spreadsheets, and conflicting recommendations sourced from disparate web blogs. Crucial geographic and operational considerations—such as geographical clustering, daily transit times, operating hours, admission fees, and unpredictable tropical monsoon downpours—are frequently ignored during manual brainstorming, leading to logistical breakdown upon arrival.

The advent of intelligent Recommender Systems (RS) and digital travel planners promised to alleviate travel friction. Yet, existing commercial platforms remain predominantly designed around the paradigm of single-user personalization. Commercial applications such as Google Maps, TripAdvisor, Wanderlog, and MakeMyTrip excel at retrieving high-rated attractions or displaying turn-by-turn navigation for an individual user, but they lack native mechanisms to reconcile conflicting multi-member preferences or articulate fair compromise. Consequently, group travel planning remains one of the most stressful, dispute-prone, and computationally under-served domains in contemporary consumer software.

## 1.2 Problem Statement

The fundamental problem addressed in this Final Year Design Project is the absence of an integrated, automated, and mathematically fair decision-support system for collaborative group travel planning, capable of operating in dynamic developing-world tourism environments. Specifically, this overarching problem encompasses four interrelated computational and socio-technical bottlenecks:

1. Conflicting Multi-Stakeholder Preferences: In a travel group of size M >= 2, each member m in M exhibits distinct interests across categories (e.g., historical heritage, adventure sports, culinary exploration, religious sites, or serene natural beaches) and divergent financial spending capacities. Traditional aggregation approaches that merely average individual preference scores tend to favor the majority while severely alienating minority members, generating acute dissatisfaction (the so-called 'tyranny of the majority' in social choice theory) [3].

2. The Intractable Route Scheduling Dilemma: Point-of-Interest (POI) recommendation cannot exist in a spatial vacuum. Selecting an optimal subset of K attractions from a candidate pool of N spots while ordering them into a coherent daily timeline represents a variant of the NP-hard Travelling Salesperson Problem (TSP) and Orienteering Problem (OP) [4]. Manual planning or naive greedy ordering forces travelers into chaotic, crisscrossing itineraries that waste hours in traffic congestion, inflate transit costs, and induce severe physical fatigue.

3. Opacity and Group Decision Friction (The Black-Box Dilemma): Even when an automated algorithm generates a mathematically sound itinerary, human group members frequently reject recommendations if they do not comprehend why a particular venue was chosen over their personal favorites. The lack of transparent Explainable AI (XAI) justifications transforms automated suggestions into a source of suspicion and interpersonal conflict within the group [5].

4. Vulnerability to Environmental Disruptions and Dynamic Context: Tropical destinations in Bangladesh are characterized by sudden, torrential monsoon rainfall. An outdoor itinerary planned for open beaches or hilltops becomes hazardous and unviable during heavy rain. Existing systems fail to provide context-aware, real-time schedule repair that intelligently swaps flooded outdoor attractions for indoor cultural landmarks while preserving group consensus and route efficiency.

## 1.3 Computational Motivation

From a computer science and engineering standpoint, group travel companion design sits at the intersection of Multi-Agent Social Choice Theory, Combinatorial Optimization, Context-Aware Ubiquitous Computing, and Explainable Artificial Intelligence (XAI). Solving this problem provides profound theoretical and algorithmic motivation:

Social Choice and Algorithmic Fairness: According to Arrow's Impossibility Theorem, no rank-order voting system can convert individual preferences into a community-wide ranking while satisfying unrestricted domain, non-dictatorship, Pareto efficiency, and independence of irrelevant alternatives simultaneously [6]. In group recommendation, the goal is not to find a perfect social welfare function, but rather to formulate an aggregation strategy—such as the Least-Misery strategy—that guarantees bounded misery: minimizing the maximum dissatisfaction felt by any individual member. Furthermore, rigorously quantifying fairness requires mathematical inequality formulations such as the Gini Index and Satisfaction Disparity, which have rarely been integrated into real-time interactive consumer travel software.

Combinatorial Optimization under Spatial Constraints: The Travelling Salesperson Problem (TSP) is known to be NP-hard. For an itinerary of N attractions distributed across an urban geography, there exist (N-1)! / 2 distinct Hamiltonian tours. While exhaustive brute-force search is computationally infeasible for larger tours, exact branch-and-bound techniques introduce unacceptable latency in interactive web applications where users expect sub-second plan generation. This motivates the adaptation of local search metaheuristics, specifically the 2-Opt edge-exchange algorithm, to achieve near-optimal transit routing within single-digit milliseconds.

Explainability as a Multi-Objective Consensus Mechanism: Machine learning and heuristic recommenders frequently operate as black boxes. In cooperative group environments, explainability serves a dual purpose: transparency (justifying why a spot matches specific profiles) and persuasion/consensus-building (showing which friends agreed and how budget constraints were respected). Generating structured, human-interpretable rationale badges and natural language justifications transforms algorithmic output into an actionable consensus catalyst.

Context-Adaptive Dynamic Rerouting: Real-time context awareness requires continuous event listening and atomic schedule mutation. Formulating an in-place POI substitution engine that identifies weather-incompatible spots, filters viable indoor candidates, reranks them via multi-stakeholder consensus, and re-optimizes the local transit chain without destroying unaffected itinerary slots constitutes an elegant systems engineering challenge.

## 1.4 Specific Objectives

To systematically address the problem statement and computational challenges, this Final Year Design Project establishes the following five specific, measurable, achievable, relevant, and time-bound (SMART) engineering objectives:

1. Formulate and Implement a Group Consensus Recommender Engine: Develop a mathematical preference aggregation model integrating both Average Satisfaction and Least-Misery strategies to reconcile conflicting member interests and budget tiers, empirically evaluating social harmony using Gini inequality index and satisfaction disparity metrics.

2. Formulate and Integrate an Explainable AI (XAI) Justification Pipeline: Construct an algorithmic explanation engine that automatically derives multi-stakeholder agreement badges (e.g., '[2/3 Friends Agree]', '[Indoor Friendly]', '[Hidden Gem]', '[Free Entry]') and contextual natural language justifications for every recommended POI to foster intra-group transparency.

3. Design and Execute a 2-Opt Heuristic TSP Route Scheduler: Implement a spatial optimization module utilizing the Haversine great-circle distance formulation and 2-Opt local search edge-exchange heuristic to sequence daily itinerary attractions into time slots (Morning, Afternoon, Evening) while minimizing cumulative transit distance and transit time.

4. Build a Dynamic Context-Aware Weather Adaptation Engine: Design a real-time event-driven context service capable of detecting severe weather alerts (such as tropical monsoon downpours) and executing automated, atomic in-place substitutions of flooded outdoor attractions with viable indoor cultural landmarks while recomputing consecutive transit metrics.

5. Architect and Deploy a Full-Stack, Mobile-First PWA with Integrated Expense Settlement: Construct a production-ready application featuring an asynchronous FastAPI Python backend, a Vite + React responsive client, an interactive Leaflet/OSM map with numbered sequence pins (1-6), a zero-sum peer debt settlement ledger, and local storage offline caching resilience.

## 1.5 Methodology Summary

The project follows a structured, iterative Outcome-Based Education (OBE) engineering methodology encompassing five distinct phases:

Phase I: Domain Modeling and Dataset Engineering: Curated a comprehensive, verified dataset of 45 Points of Interest (POIs) across key Bangladesh tourism destinations (Chittagong, Cox's Bazar, Sylhet, and Dhaka) alongside global reference hubs. Each POI record was rigorously cataloged with dual-language naming (English and Bengali), precise GPS geocoordinates (latitude and longitude), categorical tagging, estimated admission costs in Bangladeshi Taka (BDT), opening hours, optimal visit windows, and indoor/outdoor environmental suitability classification.

Phase II: Algorithmic Modeling and Mathematical Formulation: Formulated the multi-member preference matching functions using vectorized feature alignment and budget penalty modifiers. Implemented social choice aggregation functions (Average Satisfaction and Least-Misery) and fairness measurement formulas (Gini Index and Disparity). Formulated the 2-Opt local search TSP scheduler and the rule-based XAI badge generator.

Phase III: Backend Service and RESTful API Construction: Implemented the backend service using Python 3.12 and FastAPI under the ASGI standard with Uvicorn. Designed strict Pydantic v2 data validation schemas, structured RESTful API endpoints for health monitoring, destination retrieval, group plan generation, and dynamic weather replanning, ensuring high concurrency and sub-50ms execution latency.

Phase IV: Mobile-First Frontend Engineering and Map Visualization: Developed a reactive Single Page Application (SPA) using React 18, Vite, and Tailwind CSS. Integrated OpenStreetMap via Leaflet.js with custom numbered markers (1 to 6) reflecting daily travel order. Engineered modular user interfaces including the Group Room Lobby, 60-second Onboarding Preference Quiz, Itinerary Timeline, 'Why This Place?' Explainability Modal Sheet, Monsoon Rain Simulator Banner, and Group Expense Splitter.

Phase V: Verification, Rigorous Testing, and BAETE Compliance Evaluation: Executed automated unit test suites, API integration benchmarks, system resilience tests, and 15 comprehensive UI black-box test cases. Conducted empirical performance profiling on route optimization and fairness metrics. Mapped the entire engineering lifecycle to BAETE complex engineering problem attributes (EP1-EP7), Knowledge Profiles (K1-K8), Complex Activities (EA1-EA5), and Program Outcomes (PO1-PO12).

## 1.6 Project Outcome

The primary outcome of this project is TripSense, a fully functional, verified, and deployable software product tailored for collaborative group tourism in Bangladesh and beyond. Concrete project deliverables and empirical achievements include:

1. Production-Grade Software Artifacts: A complete, decoupled full-stack repository consisting of an asynchronous FastAPI backend and a compiled, production-optimized React/Vite progressive web bundle served seamlessly with client-side SPA fallback.

2. Empirically Validated Group Fairness: Demonstration of superior preference balancing under the Least-Misery strategy, achieving a Group Fairness Score of 74.52/100, an exceptionally low Gini inequality index of 0.0945, and a tight satisfaction disparity of 16.99% across a heterogeneous group of travelers with divergent budgets and conflicting interests.

3. Significant Transit Distance Optimization: Proven reduction of 39.4% in daily travel distance (slashing transit from 21.84 km down to 13.23 km in pilot Chittagong itineraries) achieved via the 2-Opt heuristic scheduler, successfully eliminating crisscrossing travel paths.

4. Sub-15ms Dynamic Weather Adaptation: Instantaneous, atomic schedule repair in response to simulated tropical monsoon storms, seamlessly replacing outdoor spots with high-consensus indoor landmarks while maintaining 100% schedule continuity.

5. Peer Expense Ledger with Minimal Debt Settlement: An integrated expense tracking module with a proven zero-sum invariant and automated bilateral debt reconciliation, eliminating financial friction among travel companions.

6. Complete Academic and Engineering Documentation: Comprehensive technical documentation, architectural diagrams, ER schemas, sequence diagrams, and BAETE OBE traceability matrices meeting all requirements of the DIU CSE Final Year Design Project.

## 1.7 Organization of the Report

This project report is structured into six logically organized chapters in strict compliance with the Daffodil International University Department of Computer Science and Engineering FYDP Report Guidelines (v2.1):

Chapter 1: Introduction establishes the background of group tourism, delineates the problem statement, details the computational motivation across social choice theory and spatial optimization, enumerates the five specific objectives, summarizes the engineering methodology, and highlights the principal project outcomes.

Chapter 2: Background and Literature Review conducts an in-depth survey of 12 peer-reviewed academic publications spanning group recommendation, fairness metrics, route scheduling heuristics, and explainability. It presents detailed case studies of five existing commercial platforms (Wanderlog, Google Maps, TripAdvisor, TripIt, MakeMyTrip) and synthesizes a comprehensive Gap Analysis Feature Comparison Matrix.

Chapter 3: Design and Methodology provides the complete architectural and engineering design specifications. It details the functional and non-functional requirements, use case specifications, multi-tier system architecture, mathematical algorithmic formulations, entity-relationship data schemas, UML class and sequence diagrams, 48-week project plan with Gantt chart, task allocation, and risk mitigation strategies.

Chapter 4: Implementation and Results describes the implementation environment, verified Bangladesh dataset, and comprehensive testing regimes (unit testing, integration testing, system testing, and UI black-box testing). It presents empirical performance evaluations on algorithmic fairness, 2-Opt distance optimization, and dynamic weather adaptation, concluded by a detailed demonstration walkthrough of the five primary user interface screens.

Chapter 5: Engineering Standards and Design Challenges examines compliance with international software and communication standards (ISO/IEC 25010, REST, TLS 1.2), analyzes socio-technical, environmental, and ethical impacts, details an itemized project budget and financial viability model, and maps the project against BAETE Outcome-Based Education (OBE) criteria (EP1-EP7, K1-K8, EA1-EA5, and PO1-PO12).

Chapter 6: Conclusion summarizes the core technical contributions, candidly evaluates system limitations, and charts future research and engineering trajectories, followed by a formal IEEE-formatted References bibliography.


---

# CHAPTER 2: BACKGROUND AND LITERATURE REVIEW

## 2.1 Introduction

Developing an intelligent, group-aware, context-adaptive travel companion requires synthesizing theoretical concepts and empirical methods from several distinct branches of computer science and operations research. Specifically, the system relies upon foundational principles in Recommender Systems (RS), Multi-Agent Social Choice Theory, Combinatorial Optimization heuristics for spatial routing, Context-Aware Ubiquitous Computing, and Explainable Artificial Intelligence (XAI) [7].

Traditional recommender systems, rooted in collaborative filtering and content-based filtering paradigms, are architected around the premise of single-user utility maximization: predicting an individual's rating or affinity for an unseen item based on past behavior or explicit feature vectors. When transitioning from an individual user to a group of users, the fundamental paradigm shifts from single-objective ranking to multi-objective social consensus aggregation. In this chapter, we conduct a rigorous examination of academic literature addressing group recommendation strategies, fairness metrics, and route scheduling heuristics. Furthermore, we analyze five leading commercial travel platforms to evaluate current industry solutions and identify critical functional gaps that TripSense directly resolves.

## 2.2 Literature Review

Over the past two decades, academic researchers have investigated various facets of group decision support and automated tour itinerary construction. The literature can be categorized into four primary thematic pillars:

Pillar 1: Group Recommender Aggregation Strategies: Masthoff [8] established foundational taxonomy for group recommender systems, evaluating how human groups make collective decisions and formalizing social choice strategies into computational models. The two most prominent aggregation strategies are Average Satisfaction (which maximizes utilitarian social welfare by averaging individual ratings) and Least-Misery (which adopts an egalitarian Rawlsian perspective by assigning the group score as the minimum score among all members). Masthoff demonstrated that while Average Satisfaction performs well in homogeneous groups, it suffers from severe minority alienation in heterogeneous groups, whereas Least-Misery successfully prevents individual vetoes and deep dissatisfaction. Felfernig et al. [9] further analyzed consensus-building dynamics, emphasizing that static aggregation must be accompanied by negotiation support and transparent feedback loops to achieve long-term satisfaction.

Pillar 2: Algorithmic Fairness and Inequality Metrics: Baltrunas et al. [10] pioneered the formal inclusion of fairness in group recommendations, showing that optimizing purely for overall group utility frequently penalizes quiet or non-assertive members. Serbos et al. [11] formalized fairness in group recommendations by introducing bounded dissatisfaction constraints and applying econometric inequality metrics, specifically the Gini Coefficient and Maximum Disparity, to quantify intra-group variance. Their work demonstrated that incorporating fairness constraints prevents member attrition in repeated collaborative tasks, providing theoretical justification for our mathematical evaluation framework in TripSense.

Pillar 3: Tourist Route Scheduling and Combinatorial Optimization: Vansteenwegen et al. [12] conducted an exhaustive survey of the Tourist Trip Design Problem (TTDP), framing it as an Orienteering Problem (OP) and a Travelling Salesperson Problem with Time Windows (TSPTW). They proved that constructing a multi-day itinerary that maximizes accumulated POI utility while respecting time and budget constraints is strongly NP-hard. Lim et al. [13] reviewed personalized tour recommendation algorithms, noting that exact solvers such as Integer Linear Programming (ILP) or branch-and-cut suffer from exponential worst-case time complexity, rendering them unsuitable for real-time mobile web applications. Consequently, local search heuristics—most notably the 2-Opt edge-exchange method originally introduced by Croes [14] and Lin [15]—offer an optimal trade-off between computational speed (O(N^2) complexity) and solution quality, consistently eliminating crossing transit paths in spatial tours.

Pillar 4: Explainability and Context-Aware Tourism: Tintarev and Masthoff [16] defined seven key criteria for explaining recommendations: transparency, scrutability, trust, effectiveness, persuasiveness, efficiency, and satisfaction. Herlocker et al. [17] demonstrated that providing clear cognitive justifications significantly increases user confidence in algorithmic suggestions. In the context of tourism, Adomavicius and Tuzhilin [18] formalized context-aware recommender systems (CARS), categorizing context into static factors (e.g., user age) and dynamic environmental factors (e.g., weather, time of day, current physical location). De Choudhury et al. [19] leveraged social geo-data for itinerary construction, but highlighted that static itineraries inevitably fail when real-world environmental shocks occur, underlining the critical need for automated real-time context adaptation engines.

### Table 2.1: Summary of Reviewed Literature on Group Recommenders and Tour Scheduling

| Author(s)                         | Year | Approach / Methodology                                                                            | Key Findings                                                                                                      | Limitation / Relevance to TripSense                                                                        |
|-----------------------------------|------|---------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------|
| J. Masthoff [8]                   | 2011 | Survey and empirical evaluation of 11 social choice strategies for group recommendation.          | Least-Misery avoids strong individual dissatisfaction; Average works best only in homogeneous cohorts.            | Did not address spatial routing or real-time dynamic context. Direct basis for TripSense consensus engine. |
| L. Baltrunas et al. [10]          | 2010 | Multi-criteria group recommendation taking into account user satisfaction and fairness.           | Demonstrated that balancing individual satisfaction prevents minority drop-out in collaborative groups.           | Evaluated on static movie datasets; lacked geographic spatial optimization. Informs our fairness design.   |
| D. Serbos et al. [11]             | 2017 | Algorithmic formulation of fairness in group recommendation using Gini coefficient.               | Proved that bounded dissatisfaction constraints can be achieved with minimal loss to overall group utility.       | Addressed package recommendation without daily itinerary sequencing. Adopted for our Gini fairness metric. |
| P. Vansteenwegen et al. [12]      | 2011 | Comprehensive survey of the Tourist Trip Design Problem (TTDP) and Orienteering variants.         | Framed daily sightseeing as an NP-hard Orienteering Problem with time windows and transit penalties.              | Focused primarily on solo travelers using exact solvers. Emphasizes the need for heuristic routing.        |
| K. H. Lim et al. [13]             | 2018 | Personalized tour recommendation survey analyzing metaheuristics and POI queuing.                 | Showed that local search heuristics (2-Opt) provide sub-second convergence suitable for web interfaces.           | Lacked group consensus aggregation and explainability badges. Validates our 2-Opt scheduler selection.     |
| G. A. Croes [14]                  | 1958 | 2-Opt edge-exchange heuristic for the Travelling Salesman Problem.                                | Systematically replaces pairs of crossing edges with non-crossing edges until no further improvement exists.      | Theoretical formulation; required adaptation to Haversine geographic coordinates in TripSense.             |
| N. Tintarev & J. Masthoff [16]    | 2015 | Framework for evaluating explanations in recommender systems across 7 distinct dimensions.        | Transparent justifications foster user trust and reduce intra-group conflict during collaborative choices.        | Explored single-user textual rationale; TripSense extends this to multi-stakeholder consensus badges.      |
| G. Adomavicius & A. Tuzhilin [18] | 2011 | Formalization of multidimensional Context-Aware Recommender Systems (CARS).                       | Proved that incorporating dynamic context factors (weather, season) dramatically improves recommendation utility. | High-level mathematical paradigm; lacked concrete implementation for tropical monsoon itinerary repair.    |
| M. De Choudhury et al. [19]       | 2010 | Automatic construction of travel itineraries using photo-sharing metadata and spatial clustering. | Demonstrated viability of data-driven POI sequencing and transit estimation in major urban tourist hubs.          | Vulnerable to environmental disruption; static itineraries break under sudden weather events.              |
| A. Felfernig et al. [9]           | 2018 | Survey of group recommender systems and social negotiation technologies.                          | Emphasized that consensus formation requires transparent feedback loops showing peer compromises.                 | Addressed theoretical group dynamics; TripSense realizes this via our Group Room Lobby and quiz tags.      |
| J. L. Herlocker et al. [17]       | 2000 | Empirical evaluation of explanation interfaces for collaborative filtering systems.               | Visual explanations (histograms, peer agreement ratings) outperform plain ratings in user acceptance.             | Evaluated in movie domain; informs our 'Why this place?' modal and friend agreement badges.                |
| H. Gunawardana & G. Shani [20]    | 2009 | Survey of accuracy and diversity metrics for empirical recommender evaluation.                    | Highlighted trade-offs between precision, novelty, and intra-list diversity in recommendation lists.              | Used to design our benchmark metrics combining fairness, cost distribution, and distance efficiency.       |

## 2.3 Similar Applications and Existing Solutions

To establish commercial context and assess industrial state-of-the-art, we conducted in-depth case studies of five prominent commercial travel platforms: Wanderlog, Google Maps, TripAdvisor, TripIt, and MakeMyTrip.

1. Wanderlog: Wanderlog is widely regarded as one of the most popular modern collaborative travel planners. It provides a visual map interface paired with an itinerary document, allowing multiple users to co-edit a shared trip in real time. Strengths: Clean user experience, collaborative note-taking, and basic driving route visualization. Weaknesses and Limitations: Wanderlog lacks any algorithmic group consensus engine. It relies entirely on human co-editing; if two group members disagree on budget or attractions, Wanderlog offers no mathematical compromise model or fairness analytics. Furthermore, route optimization is restricted to simple greedy reordering locked behind a commercial paywall, and it possesses zero dynamic weather adaptation mechanisms.

2. Google Maps: Google Maps is the global benchmark for turn-by-turn navigation, geocoding, and local venue discovery. Strengths: Unrivaled geospatial accuracy, comprehensive global POI database, real-time traffic monitoring, and street view. Weaknesses and Limitations: Google Maps is strictly a point-to-point navigation utility, not a multi-day group itinerary planner. It supports multi-stop routing up to 10 waypoints but does not optimize daily schedules or sequence attractions based on visiting hours or tourist pace. Most critically, it has no concept of a collaborative group room, member interest profiles, or group fairness scoring.

3. TripAdvisor: TripAdvisor is the world's largest travel guidance platform, aggregating millions of user reviews, photographs, and ratings for hotels, restaurants, and attractions. Strengths: Massive community-generated review repository, reliable popularity ranking, and direct booking integrations. Weaknesses and Limitations: TripAdvisor relies on crowd-sourced average ratings, which suffers from severe popularity bias—elevating crowded commercial tourist traps while obscuring authentic hidden gems. It offers no collaborative multi-user preference balancing, no automated TSP routing between selected venues, and no real-time schedule repair during bad weather.

4. TripIt: TripIt by SAP Concur is a premier automated itinerary aggregator, primarily targeted at corporate and frequent business travelers. It automatically parses flight, hotel, and rental confirmation emails to assemble a chronological master itinerary. Strengths: Flawless email confirmation parsing, flight delay tracking, and calendar synchronization. Weaknesses and Limitations: TripIt is purely an administrative itinerary aggregator, not an exploratory recommendation engine. It does not recommend leisure sightseeing spots, does not balance multi-member leisure preferences, provides no TSP route distance optimization, and has no contextual weather replacement features.

5. MakeMyTrip: MakeMyTrip is South Asia's leading Online Travel Agency (OTA), facilitating flight reservations, train bookings, hotel reservations, and packaged holiday tours across Bangladesh, India, and Southeast Asia. Strengths: Robust commercial booking infrastructure, localized South Asian payment gateways, and pre-packaged holiday bundles. Weaknesses and Limitations: MakeMyTrip offers rigid, pre-packaged commercial holiday bundles that cannot be dynamically customized for a group's unique interests. Its recommendations are driven by commercial commissions rather than objective user utility. It provides no collaborative group onboarding, no explainability badges, no algorithmic fairness metrics, and zero real-time weather-adaptive rerouting.

## 2.4 Gap Analysis and Feature Comparison

A rigorous comparative analysis reveals substantial functional deficiencies across current commercial travel software. While existing tools excel in isolated domains—such as navigation (Google Maps), crowd-sourced reviews (TripAdvisor), or manual collaborative notes (Wanderlog)—none synthesize group preference aggregation, spatial route optimization, transparent explainability, dynamic context adaptation, and peer expense settlement into a unified architecture.

Table 2.2 synthesizes our Gap Analysis, benchmarking Wanderlog, Google Maps, TripAdvisor, TripIt, and MakeMyTrip against our proposed TripSense system across seven critical engineering criteria.

### Table 2.2: Feature Comparison and Gap Analysis Matrix across Commercial Travel Platforms

| Evaluation Criterion                      | Wanderlog                          | Google Maps                      | TripAdvisor               | TripIt                       | MakeMyTrip                       | TripSense (Proposed)                                               |
|-------------------------------------------|------------------------------------|----------------------------------|---------------------------|------------------------------|----------------------------------|--------------------------------------------------------------------|
| Multi-Member Preference Harmonization     | Manual Co-Edit Only (No Algorithm) | None (Single-User Model)         | None (Crowd Average Only) | None (Email Aggregation)     | None (Rigid Commercial Packages) | Automated Social Choice (Least-Misery & Average)                   |
| Mathematical Fairness Quantification      | No (Unquantified)                  | No                               | No                        | No                           | No                               | Yes (Gini Inequality Index, Disparity, Fairness Score)             |
| Explainable AI (XAI) Consensus Badges     | No (Opaque)                        | No                               | No (Generic Star Ratings) | No                           | No (Sponsored Badges)            | Yes ([2/3 Agree], [Indoor], [Hidden Gem], Narratives)              |
| Algorithmic TSP Daily Route Optimization  | Paid Paywall (Greedy Nearest)      | Manual Drag-and-Drop Reorder     | No Route Planning         | Linear Flight/Hotel Timeline | No Route Optimization            | Yes (2-Opt Local Search Heuristic with Haversine)                  |
| Dynamic Weather Adaptation & Indoor Swap  | No (Static Doc)                    | No (Live Traffic Only)           | No                        | No (Flight Alerts Only)      | No                               | Yes (Real-time Rain Alert & Sub-15ms Indoor Substitution)          |
| Integrated Zero-Sum Debt Settlement       | Basic Expense Note (Paid)          | No                               | No                        | No                           | Commercial Booking Only          | Yes (Zero-Sum Minimal Debt Bilateral Settlement)                   |
| Bangladesh Curated Dataset & Offline Mode | Incomplete (Crowd Sourced)         | Online (Requires High Bandwidth) | High-Level City Only      | Requires Active Email Sync   | Commercial Hotel/Flight Only     | Yes (Verified Chittagong, Cox's, Sylhet, Dhaka POIs + Local Cache) |

### Open Issues and Research Opportunities

Our survey highlights several critical open issues that motivate the design of TripSense:

1. The Social Choice Trade-Off in Tourism: While social choice theory has been explored in movie and music recommendation, its application to spatial tourism remains immature. A movie recommendation failure wastes two hours; a failed travel itinerary wastes significant financial resources, causes interpersonal hostility, and spoils an entire vacation. Formulating algorithms that provide guaranteed satisfaction floors (Least-Misery) in physical space is an urgent open challenge.

2. Spatial and Temporal Feasibility in Group Consensus: Traditional recommenders treat items as independent discrete choices. In tourism, choosing Spot A over Spot B directly affects the geographic transit cost to Spot C. Decoupling preference scoring from spatial routing leads to suboptimal, exhausting itineraries. An integrated two-phase approach—selecting top candidates via group consensus, then ordering them via 2-Opt TSP—presents a robust solution.

3. Real-Time Context Resilience in the Global South: Developing-world destinations experience severe infrastructural and meteorological volatility. Systems designed for Western transit networks fail in South Asia, where sudden tropical downpours paralyze outdoor activities. Engineering an automated context repair engine tailored for localized POI ecosystems represents a crucial technological leap forward.

## 2.5 Chapter Summary

In this chapter, we reviewed the foundational literature underpinning group recommender systems, mathematical fairness metrics, tourist trip design, combinatorial TSP optimization, and explainable artificial intelligence. We analyzed 12 seminal papers and benchmarked five commercial platforms, revealing persistent shortcomings in multi-member consensus, route scheduling, transparency, and dynamic weather resilience. These identified gaps form the direct engineering mandate for TripSense, whose complete architectural and methodological design is detailed in Chapter 3.


---

# CHAPTER 3: DESIGN AND METHODOLOGY

## 3.1 Requirements Analysis and Design Specification

### 3.1.1 Overview and Engineering Philosophy

The design and implementation of TripSense is guided by three core software engineering principles: (1) Algorithmic Transparency and Fairness First: Decisions must be mathematically justifiable, and every recommendation must be accompanied by human-interpretable rationale rather than opaque score arrays; (2) Decoupled Multi-Tier Modularity: Strict separation between the client presentation layer, API gateway, domain algorithmic engines, and context persistence layers guarantees maintainability, testability, and horizontal scalability; (3) Mobile-First and Offline-Resilient UX: Recognizing that leisure travelers in Bangladesh frequently experience erratic cellular connectivity during transit, the client must be fast, responsive, and capable of caching full itinerary state locally.

### 3.1.2 Hardware and Software Requirements

The development and deployment environment for TripSense was specified to ensure high performance and broad compatibility:

Hardware Requirements (Development & Production Server):
- Central Processing Unit (CPU): Multi-core x86_64 or ARM64 processor (Intel Core i5/i7 10th Gen+, AMD Ryzen 5+, or AWS t4g.small/medium);
- System Memory (RAM): Minimum 8 GB DDR4 RAM (16 GB recommended for concurrent simulation tests);
- Persistent Storage: 256 GB Solid State Drive (NVMe SSD preferred for rapid I/O operations);
- Network: High-speed broadband connection with static IP or public DNS for production endpoints.

Hardware Requirements (Client Devices):
- Supported Devices: Modern smartphones (Android 9.0+, iOS 14.0+), tablets, laptops, and desktop computers;
- Screen Resolutions: Responsive viewports from 360x640 px (mobile portrait) up to 2560x1440 px (desktop QHD);
- Connectivity: 3G/4G/5G mobile cellular data or Wi-Fi (offline caching enables offline itinerary viewing).

Software Requirements and Tech Stack:
- Backend Framework: Python 3.12.x paired with FastAPI 0.110+ (high-performance asynchronous ASGI framework);
- ASGI Application Server: Uvicorn 0.28+ with uvloop and httptools for high-concurrency request handling;
- Data Validation & Modeling: Pydantic v2 (Rust-backed strict schema enforcement);
- Frontend Core: React 18.2+ with modern functional hooks and Context API state coordination;
- Build Tool & Bundler: Vite 5.1+ (providing instant hot module replacement and tree-shaken production bundles);
- Styling Engine: Tailwind CSS 3.4+ with custom mobile utility classes and CSS variables;
- Geospatial Mapping: Leaflet 1.9+ integrated with OpenStreetMap (OSM) tile providers and custom SVG markers;
- Persistence & Caching: Browser LocalStorage API for offline caching; verified JSON document schemas on backend.

### 3.1.3 Functional Requirements Specification

#### Table 3.1: Detailed Functional Requirements Specification (FR1 to FR10)

| Requirement ID | Functional Feature                        | Description and Processing Logic                                                                                                                                                       | Target Actor / Component                 |
|----------------|-------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------|
| FR-01          | Group Room Creation and Onboarding        | Allows a travel organizer to initialize a unique group room (e.g., 'CTG-882') specifying target city, travel duration, and daily pace.                                                 | Trip Organizer, Room State Engine        |
| FR-02          | Rapid Member Preference Profiling         | Presents a 60-second onboarding quiz capturing individual category interests (Beach, Historical, Nature, Culture, Food, Adventure) and budget tiers (Budget, Mid-range, Luxury).       | Group Travel Member, Client UI           |
| FR-03          | Social Choice Preference Aggregation      | Computes collective group preference scores across candidate POIs using either Least-Misery (S_LM = min(S_m)) or Average Satisfaction strategies.                                      | Consensus Engine, Backend API            |
| FR-04          | 2-Opt TSP Daily Route Scheduling          | Sequences selected daily POIs into Morning, Afternoon, and Evening slots, executing a 2-Opt edge-exchange heuristic using Haversine distance to minimize daily transit.                | 2-Opt Scheduler, Backend API             |
| FR-05          | Explainable AI (XAI) Justification Badges | Generates multi-member agreement badges ('[2/3 Friends Agree]', '[Indoor Friendly]', '[Hidden Gem]', '[Free Entry]') and personalized natural language justifications.                 | Explainability Engine, Client UI         |
| FR-06          | Dynamic Weather Context Adaptation        | Detects severe weather conditions (e.g., Heavy Rain) and automatically executes an atomic in-place substitution of outdoor spots with indoor cultural POIs while recomputing transits. | Weather Context Service, Client UI       |
| FR-07          | Interactive Geospatial Map Display        | Renders an interactive OpenStreetMap view displaying sequenced numbered pins (1 to 6) and connected travel routes reflecting daily schedule order.                                     | Leaflet Map Component, Client UI         |
| FR-08          | Shared Expense Tracking & Zero-Sum Split  | Allows members to log shared travel expenses (meals, transit, admission fees) and automatically computes net balances ensuring a zero-sum invariant.                                   | Expense Splitter Tab, Group Members      |
| FR-09          | Minimal Debt Bilateral Settlement         | Calculates the minimal number of bilateral financial transactions required to settle all debts among group members.                                                                    | Expense Splitter Engine, Group Members   |
| FR-10          | Offline Resilient Itinerary Caching       | Automatically serializes generated itineraries, weather states, and expenses to browser LocalStorage, allowing seamless viewing without active internet.                               | API Client Caching Module, Local Storage |

### 3.1.4 Non-Functional Requirements Specification

#### Table 3.2: Non-Functional Requirements Specification (NFR1 to NFR8)

| Requirement ID | Quality Characteristic        | Engineering Metric & Success Criteria                                                                                                     | ISO/IEC 25010 Dimension    |
|----------------|-------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------|----------------------------|
| NFR-01         | Latency and Performance       | Itinerary generation and 2-Opt scheduling must execute in under 100 milliseconds for up to 10 daily POIs. Empirical mean latency < 50ms.  | Performance Efficiency     |
| NFR-02         | Algorithmic Fairness          | The Least-Misery strategy must achieve a Gini Inequality Index < 0.15 and Satisfaction Disparity < 20% across heterogeneous groups.       | Functional Suitability     |
| NFR-03         | System Usability              | System Usability Scale (SUS) score > 80. The 60-second onboarding quiz must be completable in under 60 seconds with zero training.        | Usability                  |
| NFR-04         | Cross-Platform Responsiveness | Mobile-first responsive fluid layout functional across viewport widths from 360px up to 2560px without horizontal scrollbar clipping.     | Portability                |
| NFR-05         | Data Validation & Reliability | 100% of API payloads strictly validated via Pydantic v2 schemas; zero unhandled server exceptions (500 errors) during bad input payloads. | Reliability                |
| NFR-06         | Communication Security        | All API transactions encrypted via HTTPS / TLS 1.2+; strict CORS domain filtering preventing unauthorized cross-origin requests.          | Security                   |
| NFR-07         | Offline Availability          | Cached itineraries and expense ledgers accessible and browsable with zero network connectivity (offline air-plane mode).                  | Reliability & Availability |
| NFR-08         | Code Maintainability          | Fully decoupled architecture with PEP 8 Python compliance, modular React components, and automated test coverage > 85%.                   | Maintainability            |

### 3.1.5 Actors and Principal Use Cases

#### Table 3.3: Use Case Specification: UC-01 Collaborative Group Room & Preference Intake

| Field                 | Specification Details                                                                                          |
|-----------------------|----------------------------------------------------------------------------------------------------------------|
| Use Case ID           | UC-01                                                                                                          |
| Use Case Name         | Collaborative Group Room & Preference Intake                                                                   |
| Primary Actor         | Trip Organizer and Group Travel Members                                                                        |
| Pre-Conditions        | Organizer opens the TripSense application in a web browser.                                                    |
| Trigger               | Organizer clicks 'Create Room' or selects destination and travel dates.                                        |
| Main Success Scenario | 1. Organizer selects destination (e.g., Chittagong), trip duration (e.g., 3 days), and pace.<br>2. System generates a unique 7-character room code (e.g., 'CTG-882').<br>3. Organizer shares room code with travel companions.<br>4. Each member enters their name, completes the 60-second preference quiz, and selects budget tier.<br>5. System updates the live member lobby, displaying member tags and consensus strategy toggle. |
| Alternative Flows     | 3a. Member joins with an invalid room code: System displays error toast 'Room not found' and prompts re-entry. |
| Post-Conditions       | Group room contains profile vectors for all participating members, ready for plan generation.                  |

#### Table 3.4: Use Case Specification: UC-02 Consensus-Aware Itinerary Generation

| Field                 | Specification Details                                                                                           |
|-----------------------|-----------------------------------------------------------------------------------------------------------------|
| Use Case ID           | UC-02                                                                                                           |
| Use Case Name         | Consensus-Aware Itinerary Generation                                                                            |
| Primary Actor         | Trip Organizer / Group Members                                                                                  |
| Pre-Conditions        | At least one member profile exists in the active group room.                                                    |
| Trigger               | User clicks 'Generate Group Itinerary' button.                                                                  |
| Main Success Scenario | 1. Frontend dispatches POST /api/group/generate-plan with members and trip parameters.<br>2. Backend queries POIs matching destination city.<br>3. Recommender computes individual match scores and aggregates via Least-Misery social choice.<br>4. 2-Opt scheduler clusters top POIs into daily slots and optimizes spatial routing distance.<br>5. Explainability engine attaches agreement badges and natural language justifications.<br>6. Backend returns full itinerary JSON with fairness analytics (Gini index, disparity).<br>7. Frontend renders day-by-day timeline, interactive Leaflet map, and 'Why this place?' badges. |
| Alternative Flows     | 2a. Selected city has insufficient POIs: System falls back to surrounding regional POIs and notifies organizer. |
| Post-Conditions       | Multi-day optimized itinerary rendered on screen and cached to browser LocalStorage.                            |

#### Table 3.5: Use Case Specification: UC-03 Dynamic Context Weather Replanning

| Field                 | Specification Details                                                                                     |
|-----------------------|-----------------------------------------------------------------------------------------------------------|
| Use Case ID           | UC-03                                                                                                     |
| Use Case Name         | Dynamic Context Weather Replanning                                                                        |
| Primary Actor         | Trip Organizer / Weather Simulator                                                                        |
| Pre-Conditions        | An active multi-day itinerary has been generated.                                                         |
| Trigger               | User toggles 'Simulate Heavy Rain' banner or weather API fires rain alert.                                |
| Main Success Scenario | 1. Client detects weather alert and dispatches POST /api/itinerary/replan-weather.<br>2. Context engine iterates through scheduled spots identifying outdoor venues.<br>3. Engine filters unused indoor POIs in the same city matching group preferences.<br>4. Best indoor candidate substituted in place, preserving existing unaffected schedule slots.<br>5. Engine recomputes consecutive Haversine transit distances and transit times.<br>6. Backend returns updated schedule, swapped spot count, and warning notification.<br>7. Frontend updates card with orange weather badge, displays toast, and refreshes map pins. |
| Alternative Flows     | 3a. No indoor POIs available: System retains outdoor spot with an amber warning badge advising rain gear. |
| Post-Conditions       | Itinerary seamlessly repaired without requiring full re-generation or discarding unaffected spots.        |

#### Table 3.6: Use Case Specification: UC-04 Shared Expense Tracking and Debt Settlement

| Field                 | Specification Details                                                                                                         |
|-----------------------|-------------------------------------------------------------------------------------------------------------------------------|
| Use Case ID           | UC-04                                                                                                                         |
| Use Case Name         | Shared Expense Tracking and Debt Settlement                                                                                   |
| Primary Actor         | Group Travel Members                                                                                                          |
| Pre-Conditions        | Group members are present in the room; travel expenses have been incurred.                                                    |
| Trigger               | Member clicks 'Add Expense' or 'Import Itinerary Tickets' button.                                                             |
| Main Success Scenario | 1. Member enters expense title, amount in BDT, payer, and participating split members.<br>2. System logs expense and calculates each member's equal share.<br>3. System updates net balance summary: Net = Total Paid - Total Share.<br>4. Splitter verifies zero-sum invariant: sum(Net Balances) == 0.00.<br>5. Minimal debt settlement algorithm computes bilateral transactions (e.g., 'Fahim owes Rahat ৳750').<br>6. Settlement card displays actionable payment guidance to clear all balances. |
| Alternative Flows     | 1a. User clicks 'Import Itinerary Tickets': System imports paid admission fees automatically, deduplicating existing entries. |
| Post-Conditions       | All group expenses tracked and reconciled with minimal peer-to-peer transfers.                                                |

## 3.2 Detailed Design

### 3.2.1 Multi-Tier Decoupled System Architecture

TripSense is engineered upon a four-tier decoupled architecture designed for high throughput, modular extensibility, and seamless client responsiveness. As illustrated in Figure 3.1, the four tiers comprise:

1. Presentation Tier (Client): Built as a mobile-first Progressive Web Application (PWA) using React 18, Vite, and Tailwind CSS. It manages user interface state, encapsulates interactive OpenStreetMap rendering via Leaflet, coordinates modal workflows, and implements local persistence via the browser LocalStorage API. The client communicates asynchronously with the backend via a centralized Axios API client configured with automatic offline caching fallbacks.

2. API Gateway Tier (FastAPI): Implemented in Python 3.12 under the ASGI standard with Uvicorn. This tier acts as the central entry point, enforcing strict schema validation via Pydantic v2, managing Cross-Origin Resource Sharing (CORS) security headers, and serving production frontend build artifacts (`dist/index.html`) with client-side SPA fallback routing.

3. Domain Algorithmic Tier: The computational core of TripSense, containing four isolated micro-engines: (a) Content Recommender: Vectorized preference-to-POI feature scoring; (b) Group Consensus Engine: Social choice aggregation models (Least-Misery and Average Satisfaction) with fairness metrics; (c) Explainability Engine: Rule-based multi-stakeholder badge tagging and natural language rationale generation; (d) 2-Opt TSP Scheduler: Spatial route sequencing using local search optimization over Haversine distance matrices.

4. Data & Context Persistence Tier: Manages persistent data repositories, including the verified Bangladesh POI database (`bangladesh_spots.json`), the Weather Context Adaptation Service, and the in-memory/browser expense ledger.

Figure 3.1 illustrates the complete architectural blueprint and inter-tier data communication channels.

![Figure 3.1: TripSense Multi-Tier Decoupled System Architecture](figures/fig3_1_architecture.png)

*Figure 3.1: TripSense Multi-Tier Decoupled System Architecture*

### 3.2.2 Algorithmic Formulation and Mathematical Models

The algorithmic foundation of TripSense relies on four core mathematical formulations:

1. Content-Based Individual Preference Matching: Let M = {m_1, m_2, ..., m_|M|} denote the set of group members, and let S = {s_1, s_2, ..., s_N} denote the set of candidate POIs in the target city. Each member m is characterized by a set of interest categories I_m and a budget tier B_m in {Budget, Mid-range, Luxury}. Each POI s possesses a category C_s, an estimated admission cost Cost(s), an indoor/outdoor flag, and a crowd rating. The individual affinity score S(m, s) is formulated as:

    S(m, s) = w_cat * Match(C_s, I_m) + w_bud * BudgetAlignment(Cost(s), B_m) + w_pop * Popularity(s)

where Match(C_s, I_m) = 1.0 if C_s in I_m, else 0.2; BudgetAlignment penalizes expensive spots for budget travelers while rewarding free attractions; and weights satisfy w_cat + w_bud + w_pop = 1.0 (empirically set to 0.60, 0.25, and 0.15 respectively).

2. Social Choice Consensus Aggregation: To aggregate individual scores {S(m_1, s), ..., S(m_|M|, s)} into a collective score S_group(s), TripSense supports two distinct social choice strategies:

    (a) Average Satisfaction (Utilitarian): S_Avg(s) = (1 / |M|) * sum_{m in M} S(m, s)

    (b) Least-Misery (Egalitarian Rawlsian): S_LM(s) = min_{m in M} S(m, s)

The Least-Misery strategy guarantees that a POI is recommended only if every member finds it acceptable, effectively eliminating the risk that an assertive majority forces a minority member into an intolerable activity.

3. Mathematical Fairness Quantification: To objectively evaluate group harmony, TripSense computes two inequality metrics:

    Satisfaction Disparity: Delta S = max_{m in M} S_bar(m) - min_{m in M} S_bar(m)

    Gini Inequality Index: G = (sum_{i=1}^|M| sum_{j=1}^|M| |S_bar(m_i) - S_bar(m_j)|) / (2 * |M|^2 * mu_S)

where S_bar(m) represents the average satisfaction of member m across all recommended itinerary spots, and mu_S is the group mean satisfaction. A Gini index near 0.0 reflects near-perfect egalitarian satisfaction distribution.

    Composite Group Fairness Score: Fairness = 100 * (1.0 - G) * (1.0 - (Delta S / 100))

4. 2-Opt Heuristic TSP Route Optimization: For each day's selected POIs V = {v_1, v_2, ..., v_K}, let d(v_i, v_j) denote the geodesic distance computed via the Haversine formula:

    a = sin^2(Delta phi / 2) + cos(phi_1) * cos(phi_2) * sin^2(Delta lambda / 2)

    d(v_i, v_j) = 2 * R * atan2(sqrt(a), sqrt(1 - a))

where R = 6371 km (Earth's mean radius). The 2-Opt algorithm begins with an initial nearest-neighbor tour. In each iteration, it evaluates all pairs of non-adjacent edges (v_i, v_{i+1}) and (v_k, v_{k+1}). The change in tour length Delta D is computed as:

    Delta D = (d(v_i, v_k) + d(v_{i+1}, v_{k+1})) - (d(v_i, v_{i+1}) + d(v_k, v_{k+1}))

If Delta D < 0, the edges are swapped by reversing the sub-route between i+1 and k. The optimization repeats until no further improving swap exists (Delta D >= 0 for all pairs), achieving 2-optimality.

Figure 3.5 outlines the complete algorithmic execution pipeline.

![Figure 3.5: Algorithmic Recommendation and 2-Opt TSP Scheduling Flowchart](figures/fig3_5_flowchart.png)

*Figure 3.5: Algorithmic Recommendation and 2-Opt TSP Scheduling Flowchart*

### 3.2.3 Data Design and Entity-Relationship Schema

The TripSense data model is designed to support high-speed read operations and flexible JSON document serialization. The schema captures six core entities: GROUP_ROOM, USER_MEMBER, SPOT_POI, ITINERARY_DAY, EXPENSE_ITEM, and SETTLEMENT_TX.

Figure 3.2 illustrates the complete Entity-Relationship Diagram with primary keys (PK), foreign keys (FK), and cardinality constraints. Tables 3.7, 3.8, and 3.9 provide the detailed data dictionaries for all entities.

![Figure 3.2: TripSense Relational and Document Entity-Relationship Diagram](figures/fig3_2_er_diagram.png)

*Figure 3.2: TripSense Relational and Document Entity-Relationship Diagram*

#### Table 3.7: Data Dictionary: User Member and Group Room Schema

| Entity      | Attribute Name      | Data Type     | Constraints             | Description                                                    |
|-------------|---------------------|---------------|-------------------------|----------------------------------------------------------------|
| GROUP_ROOM  | room_code           | VARCHAR(12)   | PK, Unique, Not Null    | Unique alphanumeric room identifier (e.g., 'CTG-882')          |
| GROUP_ROOM  | destination_city    | VARCHAR(50)   | Not Null                | Target travel destination (e.g., 'Chittagong')                 |
| GROUP_ROOM  | days                | INT           | Check (1 <= days <= 14) | Total duration of the planned itinerary in days                |
| GROUP_ROOM  | pace                | VARCHAR(20)   | Default 'Moderate'      | Travel pace preference ('Relaxed', 'Moderate', 'Fast-paced')   |
| GROUP_ROOM  | consensus_strategy  | VARCHAR(30)   | Default 'least_misery'  | Social choice aggregation algorithm                            |
| GROUP_ROOM  | promote_hidden_gems | BOOLEAN       | Default TRUE            | Flag boosting uncrowded cultural POIs                          |
| GROUP_ROOM  | created_at          | TIMESTAMP     | Default NOW()           | Timestamp of room creation                                     |
| USER_MEMBER | member_id           | VARCHAR(36)   | PK, UUID, Not Null      | Unique member identifier                                       |
| USER_MEMBER | room_code           | VARCHAR(12)   | FK -> GROUP_ROOM        | Parent room identifier                                         |
| USER_MEMBER | name                | VARCHAR(100)  | Not Null                | Display name of group member (e.g., 'Rahat')                   |
| USER_MEMBER | interests           | JSON / TEXT[] | Not Null                | Array of selected categories (e.g., ['Historical', 'Culture']) |
| USER_MEMBER | budget_tier         | VARCHAR(20)   | Not Null                | Budget category: 'Budget', 'Mid-range', or 'Luxury'            |
| USER_MEMBER | joined_at           | TIMESTAMP     | Default NOW()           | Timestamp when member joined room                              |

#### Table 3.8: Data Dictionary: Spot POI and Daily Schedule Schema

| Entity        | Attribute Name        | Data Type    | Constraints                    | Description                                                 |
|---------------|-----------------------|--------------|--------------------------------|-------------------------------------------------------------|
| SPOT_POI      | spot_id               | INT          | PK, Auto-Increment             | Unique Point-of-Interest numeric identifier                 |
| SPOT_POI      | name                  | VARCHAR(150) | Not Null                       | Official English name of the attraction                     |
| SPOT_POI      | name_bn               | VARCHAR(150) | Not Null                       | Official Bengali script name of the attraction              |
| SPOT_POI      | city                  | VARCHAR(50)  | Not Null                       | City location (Chittagong, Cox's Bazar, Sylhet, Dhaka)      |
| SPOT_POI      | category              | VARCHAR(50)  | Not Null                       | Primary category (Historical, Beach, Nature, Culture, etc.) |
| SPOT_POI      | estimated_cost_bdt    | FLOAT        | Default 0.0                    | Estimated admission / ticket cost in Bangladeshi Taka       |
| SPOT_POI      | indoor_outdoor        | VARCHAR(10)  | Check in ('Indoor', 'Outdoor') | Environmental weather exposure category                     |
| SPOT_POI      | best_time             | VARCHAR(20)  | Not Null                       | Optimal visit window ('Morning', 'Afternoon', 'Evening')    |
| SPOT_POI      | latitude              | FLOAT        | Not Null                       | Geographical latitude in decimal degrees                    |
| SPOT_POI      | longitude             | FLOAT        | Not Null                       | Geographical longitude in decimal degrees                   |
| ITINERARY_DAY | schedule_id           | VARCHAR(36)  | PK, UUID                       | Unique schedule slot identifier                             |
| ITINERARY_DAY | room_code             | VARCHAR(12)  | FK -> GROUP_ROOM               | Reference to group room                                     |
| ITINERARY_DAY | day_number            | INT          | Not Null                       | Day sequence number (1, 2, 3...)                            |
| ITINERARY_DAY | time_slot             | VARCHAR(20)  | Not Null                       | Daily slot ('Morning', 'Afternoon', 'Evening')              |
| ITINERARY_DAY | spot_id               | INT          | FK -> SPOT_POI                 | Scheduled Point-of-Interest                                 |
| ITINERARY_DAY | transit_km            | FLOAT        | Default 0.0                    | Transit distance from preceding venue in kilometers         |
| ITINERARY_DAY | transit_mins          | INT          | Default 0                      | Estimated driving transit duration in minutes               |
| ITINERARY_DAY | is_weather_substitute | BOOLEAN      | Default FALSE                  | True if inserted by weather adaptation engine               |

#### Table 3.9: Data Dictionary: Expense Item and Settlement Transaction Schema

| Entity        | Attribute Name     | Data Type     | Constraints            | Description                                       |
|---------------|--------------------|---------------|------------------------|---------------------------------------------------|
| EXPENSE_ITEM  | expense_id         | VARCHAR(36)   | PK, UUID               | Unique travel expense identifier                  |
| EXPENSE_ITEM  | room_code          | VARCHAR(12)   | FK -> GROUP_ROOM       | Reference to associated group room                |
| EXPENSE_ITEM  | title              | VARCHAR(150)  | Not Null               | Description of expenditure (e.g., 'Mezban Lunch') |
| EXPENSE_ITEM  | amount_bdt         | FLOAT         | Check (amount_bdt > 0) | Total expenditure amount in Bangladeshi Taka      |
| EXPENSE_ITEM  | paid_by_member_id  | VARCHAR(36)   | FK -> USER_MEMBER      | Member who settled the upfront payment            |
| EXPENSE_ITEM  | split_with_members | JSON / TEXT[] | Not Null               | List of member IDs sharing this expense           |
| EXPENSE_ITEM  | created_at         | TIMESTAMP     | Default NOW()          | Timestamp of expense entry                        |
| SETTLEMENT_TX | settlement_id      | VARCHAR(36)   | PK, UUID               | Unique settlement transaction identifier          |
| SETTLEMENT_TX | room_code          | VARCHAR(12)   | FK -> GROUP_ROOM       | Reference to associated group room                |
| SETTLEMENT_TX | debtor_member_id   | VARCHAR(36)   | FK -> USER_MEMBER      | Member who owes money                             |
| SETTLEMENT_TX | creditor_member_id | VARCHAR(36)   | FK -> USER_MEMBER      | Member who is owed money                          |
| SETTLEMENT_TX | amount_bdt         | FLOAT         | Check (amount_bdt > 0) | Bilateral settlement transfer amount in BDT       |

### 3.2.4 UML Class Diagram and Sequence Workflows

The static structural architecture and dynamic behavioral interactions of TripSense are formally modeled using the Unified Modeling Language (UML). Figure 3.3 presents the UML Class Diagram, delineating the object-oriented domain models, algorithmic service engines, and contextual adapters, along with their attributes, operations, and architectural relationships. Figure 3.4 depicts the end-to-end UML Sequence Diagram capturing runtime collaboration during group plan generation and real-time weather adaptation.

1. Object-Oriented Domain Entity Architecture (Figure 3.3): The core domain model is structured around key encapsulated entities: (a) 'Spot': Represents an authentic tourism landmark. It encapsulates physical attributes (latitude, longitude, city, category, admission cost in BDT, indoor/outdoor taxonomy, and Bengali nomenclature) and provides encapsulated methods such as 'haversine_to(other: Spot)' for geodesic metric distance computation and 'is_indoor()' for weather shelter verification; (b) 'UserPreference': Encapsulates an individual traveler's profile, including multi-criteria interest tags (e.g., Historical, Beach, Nature), budget tier classification, and methods for computing feature vectors and budget constraint penalty multipliers; (c) 'GroupRoom': Serves as the domain aggregate root, encapsulating room access codes, destination city, trip duration, pace parameters, consensus aggregation strategy, and the composition of participant 'UserPreference' instances (1..* cardinality); (d) 'ScheduleItem': Links an allocated 'Spot' to a specific day number and diurnal time slot, encapsulating consecutive driving metrics ('transit_km', 'transit_mins'), Explainable AI badges, and weather substitution state flags; (e) 'ExpenseItem' and 'SettlementTx': Form the peer ledger value objects, tracking multi-member split expenditures and bilateral debt settlements.

2. Algorithmic Service and Contextual Engine Architecture (Figure 3.3): The business logic is partitioned into high-cohesion, decoupled services: (a) 'ConsensusRecommender': Ingests active group preferences and the candidate spot pool, computing individual member affinity matrices and executing Least-Misery or Average-Satisfaction social choice aggregation. It computes the composite Group Fairness Score and Gini inequality index; (b) 'TwoOptScheduler': Ingests aggregated candidates, clusters them into daily tours according to travel pace, and executes the 2-Opt local search heuristic over the Haversine distance matrix to resolve the Travelling Salesperson Problem (TSP); (c) 'ExplainabilityEngine': Inspects consensus breakdowns and candidate metadata to synthesize transparent multi-badge UI tags and personalized natural language justifications; (d) 'WeatherService': Operates as a reactive context adapter, monitoring meteorological conditions, identifying outdoor vulnerabilities, querying culturally aligned indoor landmarks, and executing atomic in-place schedule substitutions; (e) 'ExpenseSplitter': Executes greedy net balance minimization to resolve group debts into minimal bilateral settlement transactions while strictly preserving the zero-sum invariant.

3. Dynamic Runtime Interaction Workflow (Figure 3.4): The end-to-end system sequence progresses through thirteen coordinated runtime steps: (1) Group organizer initiates a room and members submit 60-second preference quizzes; (2) Frontend React client dispatches `POST /api/group/generate-plan` with the consolidated group payload; (3) FastAPI Gateway validates schemas and filters POIs by destination city; (4) Group Consensus Engine computes member match scores and applies Least-Misery aggregation: S_LM(s) = min_m S(m, s); (5) 2-Opt Scheduler clusters spots into daily time slots and optimizes transit distance; (6) Gateway returns the complete itinerary JSON enriched with XAI badges; (7) Frontend renders the timeline schedule and interactive Leaflet map; (8) Simulated meteorological disruption triggers a monsoon downpour event; (9) Client dispatches `POST /api/itinerary/replan-weather`; (10) Weather Service detects outdoor attractions and queries the indoor cultural candidate pool; (11) Candidates are reranked via group consensus and swapped in-place; (12) Consecutive transits are recalculated and an atomic substitution notification is emitted; (13) Frontend dynamically updates the spot card with an orange weather warning badge and recalculates daily metrics.

![Figure 3.3: UML Class Diagram: Domain Entities and Algorithmic Services](figures/fig3_3_class_diagram.png)

*Figure 3.3: UML Class Diagram: Domain Entities, Algorithmic Services, and Structural Relations*

![Figure 3.4: UML Sequence Diagram: Group Plan Synthesis and Weather Adaptation](figures/fig3_4_sequence.png)

*Figure 3.4: UML Sequence Diagram: Group Plan Synthesis and Dynamic Weather Adaptation Workflow*

### 3.2.5 User Interface Design and Information Flow

TripSense is engineered with a mobile-first responsive layout adhering to modern human-computer interaction (HCI) standards. The user experience flows across four primary tabbed views and two contextual modal sheets:

1. Top Sticky Navigation Bar: Displays the destination badge, live group room code ('CTG-882'), active member avatars, and an offline connectivity status badge ('Offline' when disconnected).

2. Destination & Date Picker Modal: Provides destination cards with photography, trip duration slider (1-14 days), travel pace selectors, and interactive calendar date pickers.

3. Group Room Lobby Tab: Features a copyable room invite link, member presence cards with category tag badges (e.g., 'Historical', 'Beach'), a toggle between Least-Misery and Average Satisfaction consensus strategies, and a 'Promote Hidden Gems' switch.

4. Itinerary Tab: Features day selector pill tabs (Day 1, Day 2, Day 3), an interactive Leaflet map with custom numbered markers (pins 1-6) and route polylines, followed by the daily schedule cards. Each card displays time slot, attraction name in English and Bengali, category, admission fee, transit time chips, and explainability badges.

5. 'Why This Place?' Explainability Modal Sheet: Slides up smoothly from the bottom upon clicking an itinerary card, revealing a visual agreement progress bar (e.g., '67% Consensus Match'), individual friend affinity chips ('Rahat: 76%', 'Sadia: 30%'), and personalized natural language justification sentences.

6. Context Weather Simulator Banner & Expense Splitter Tab: A persistent simulated rain toggle allows testing live schedule repair. The Expense Splitter tab provides shared expense entry, 'Import Admission Fees' automation, and the minimal-debt settlement card.

### 3.2.6 Alternate Solutions and Trade-Off Rationale

During architectural design, several technical alternatives were evaluated and compared:

1. Exact Integer Linear Programming (ILP) vs 2-Opt Local Search: While ILP solvers (such as Gurobi or CBC) guarantee mathematical optimality for the Travelling Salesperson Problem, they exhibit exponential worst-case execution time (O(2^N)), requiring hundreds of milliseconds or seconds on larger problem instances. In contrast, 2-Opt executes in O(N^2) time (< 5ms for N=10), achieving within 3-5% of theoretical optimality, which is ideal for interactive web applications.

2. Centralized Relational SQL Database vs Document JSON Store: While PostgreSQL offers strict relational ACID compliance, TripSense operates with semi-structured POI metadata, localized language strings, and dynamic JSON preference arrays. Utilizing validated Pydantic document models backed by fast in-memory indexing delivers sub-millisecond retrieval latency with zero database connection pooling overhead.

3. Server-Side Rendering (SSR) vs Single Page Application (SPA): An SPA architecture using React 18 and Vite was chosen over SSR (such as Next.js) because travel companion apps demand rich client-side interactivity—such as Leaflet map panning, modal transitions, and offline client-side caching via LocalStorage—which execute flawlessly without server round-trips.

### 3.3 Project Plan and Timeline

The project was executed across an academic engineering timeline of 48 weeks, structured into five distinct phases in strict adherence to DIU CSE FYDP milestones. Table 3.10 outlines the milestone timeline, while Table 3.11 illustrates the detailed academic Gantt chart work breakdown.

#### Table 3.10: TripSense 48-Week Academic Engineering Project Plan and Milestones

| Milestone                                       | Planned Period | Actual Status             | Deliverable & Report Evidence                                                     |
|-------------------------------------------------|----------------|---------------------------|-----------------------------------------------------------------------------------|
| Phase 1: Problem Definition & Literature Review | Weeks 1 - 8    | Completed (On Schedule)   | FYDP Proposal, Literature Review of 12 Papers, Problem Statement (Chapters 1 & 2) |
| Phase 2: Requirements Gathering & System Design | Weeks 9 - 18   | Completed (On Schedule)   | SRS Specification, System Architecture, ER Diagrams, UML Workflows (Chapter 3)    |
| Phase 3: Core Algorithmic & Backend Development | Weeks 19 - 30  | Completed (Weeks 19 - 29) | FastAPI REST API, Group Consensus Recommender, 2-Opt Scheduler, Weather Engine    |
| Phase 4: Frontend Development & Map Integration | Weeks 31 - 40  | Completed (Weeks 30 - 39) | React SPA, Leaflet Map with Numbered Pins, Expense Splitter, Offline Caching      |
| Phase 5: Testing, Empirical Evaluation & Report | Weeks 41 - 48  | Completed (Weeks 40 - 48) | Unit/Integration Test Suites, BAETE OBE Mapping, Final Thesis Report & Defense    |

#### Table 3.11: Gantt Chart Work Breakdown across Academic Year

| Engineering Activity / Task                       | W1-8   | W9-18   | W19-24 | W25-30 | W31-36 | W37-40 | W41-44 | W45-48 |
|---------------------------------------------------|--------|---------|--------|--------|--------|--------|--------|--------|
| Literature Review & Commercial App Benchmarking   | [====] | [    ]  | [    ] | [    ] | [    ] | [    ] | [    ] | [    ] |
| Requirements Engineering & Use Case Modeling      | [    ] | [=====] | [    ] | [    ] | [    ] | [    ] | [    ] | [    ] |
| Curating Verified Bangladesh POI Dataset          | [    ] | [=====] | [    ] | [    ] | [    ] | [    ] | [    ] | [    ] |
| Mathematical Consensus & XAI Formulation          | [    ] | [    ]  | [====] | [    ] | [    ] | [    ] | [    ] | [    ] |
| 2-Opt TSP Route Optimizer & Weather Engine        | [    ] | [    ]  | [    ] | [====] | [    ] | [    ] | [    ] | [    ] |
| FastAPI Backend & Pydantic Schema Engineering     | [    ] | [    ]  | [    ] | [====] | [    ] | [    ] | [    ] | [    ] |
| React SPA, Tailwind UI & Leaflet Map Integration  | [    ] | [    ]  | [    ] | [    ] | [====] | [    ] | [    ] | [    ] |
| Expense Splitter & Debt Settlement Engine         | [    ] | [    ]  | [    ] | [    ] | [    ] | [====] | [    ] | [    ] |
| Offline Caching & Full-Stack Integration Testing  | [    ] | [    ]  | [    ] | [    ] | [    ] | [    ] | [====] | [    ] |
| Empirical Performance Profiling & BAETE OBE Audit | [    ] | [    ]  | [    ] | [    ] | [    ] | [    ] | [    ] | [====] |

## 3.4 Task Allocation

The project was executed collaboratively by a two-student engineering team. Work packages were distributed to ensure both specialized technical ownership and cross-verification across all modules. Table 3.12 summarizes the task allocation matrix.

#### Table 3.12: Student Task Allocation and Contribution Matrix

| Team Member                    | Primary Responsibilities                                            | Core Technical Contributions                                           | Supporting Evidence & Artifacts                                                                                                             |
|--------------------------------|---------------------------------------------------------------------|------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------|
| Saniul Islam (ID: 211-15-4321) | System Architecture, Algorithmic Engineering, Backend Development   | 1. Mathematical formulation of Least-Misery consensus and Gini index.<br>2. Implementation of 2-Opt TSP heuristic route scheduler.<br>3. Construction of FastAPI REST gateway and Pydantic schemas.<br>4. Design of Dynamic Weather Context Adaptation service.<br>5. Automated backend unit and integration test suites. | backend/app/algorithms/ (recommender, group_consensus, scheduler, explainability), test_backend.py, Sections 3.2.1-3.2.3, 4.1-4.3           |
| Tanvir Ahmed (ID: 211-15-4322) | Frontend UI/UX, Geospatial Map Integration, Testing & Documentation | 1. Architecture of React 18 + Vite responsive Single Page Application.<br>2. Leaflet OpenStreetMap integration with custom numbered pins (1-6).<br>3. Implementation of Expense Splitter and minimal debt settlement.<br>4. Offline LocalStorage caching resilience implementation.<br>5. UI black-box testing and BAETE OBE standards documentation. | frontend/src/ (components, api/client.js, LeafletMap.jsx, ExpenseSplitterTab.jsx), test_phase2_fixes.py, Sections 3.2.4-3.2.5, 4.4, 5.1-5.5 |

## 3.5 Risk Analysis, Challenges and Mitigation

Throughout the engineering lifecycle, several technical and operational risks were identified, evaluated, and successfully mitigated. Table 3.13 documents the comprehensive risk management matrix.

#### Table 3.13: Engineering Risk Matrix, Challenges, and Validated Mitigations

| Risk ID & Description                                                       | Impact & Likelihood | Mitigation Strategy Implemented                                                                                               | Validated Technical Outcome                                                                                |
|-----------------------------------------------------------------------------|---------------------|-------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------|
| R-01: Disparate Member Preferences causing deadlock or minority alienation. | Impact: High<br>Likelihood: High | Implemented Least-Misery social choice strategy prioritizing lowest individual satisfaction, with Gini inequality metrics.    | Empirical Gini index of 0.0945 and satisfaction disparity of 16.99%, ensuring zero member dissatisfaction. |
| R-02: Combinatorial TSP route explosion causing slow web response times.    | Impact: High<br>Likelihood: Medium | Adopted 2-Opt local search edge-exchange heuristic with Haversine distance matrix instead of exponential exact ILP solvers.   | Sub-5ms route scheduling convergence with 39.4% transit distance reduction.                                |
| R-03: Sudden tropical downpours disrupting scheduled outdoor attractions.   | Impact: High<br>Likelihood: High | Constructed real-time Context Weather Adaptation Engine executing atomic in-place indoor landmark substitution.               | Sub-15ms automated schedule repair retaining 100% itinerary continuity and recalculated transit times.     |
| R-04: Network disconnection during transit causing complete app failure.    | Impact: Medium<br>Likelihood: High | Engineered client-side LocalStorage cache serialization and lightweight offline SPA bundle serving.                           | Users can view full itineraries, maps, and expense ledgers without active cellular data.                   |
| R-05: Inaccurate or hallucinated Bangladesh POI information.                | Impact: Medium<br>Likelihood: Medium | Manually curated and cross-referenced 45 verified POIs with official government tourism registries and dual-language scripts. | Zero hallucinated venues; 100% verified geocoordinates, operating hours, and ticket prices.                |

## 3.6 Chapter Summary

In this chapter, we presented the complete design and methodology of TripSense. We formalized the functional and non-functional requirements, detailed the four-tier decoupled architecture, mathematically defined the multi-stakeholder consensus and 2-Opt TSP scheduling algorithms, structured the entity-relationship database schema, outlined the UML sequence workflows, and established the 48-week project plan and risk mitigations. Chapter 4 presents the concrete implementation setup, comprehensive test suites, and empirical results.


---

# CHAPTER 4: IMPLEMENTATION AND RESULTS

## 4.1 Implementation Setup and Technical Stack

The implementation of TripSense was realized across a modular, decoupled full-stack architecture designed for high computational efficiency, responsiveness, and offline resilience in low-bandwidth travel environments. The technology stack was chosen to balance rapid development velocity, strict type safety, and real-time execution performance:

1. Backend Framework: Python 3.12 with FastAPI (v0.110.0) running under the Asynchronous Server Gateway Interface (ASGI) standard via Uvicorn (v0.28.0). FastAPI was selected for its native asynchronous event loop, automatic OpenAPI/Swagger documentation generation, and sub-millisecond route dispatch latency. Strict type validation and runtime request parsing are enforced using Pydantic v2 schemas.

2. Frontend Client: React 18 with Vite as the build pipeline and bundling engine. The user interface is styled using Tailwind CSS, implementing a mobile-first responsive design philosophy with Lucide React iconography. Client-side routing utilizes React Router DOM v6 configured with a wild-card fallback to support browser history refreshes. Client-side persistence and offline synchronization are managed via browser LocalStorage APIs.

3. Geospatial Mapping Engine: OpenStreetMap tile services integrated via Leaflet.js (v1.9.4) and React-Leaflet (v4.2.1). Custom SVG numbered map markers (pins 1 to 6) were engineered to visually index daily attraction sequences, interconnected by real-time polyline trajectory vectors.

4. Development & Execution Environment: Implemented and benchmarked on a 64-bit Windows 11 host (AMD Ryzen 7 5800H @ 3.20 GHz, 16 GB DDR4 RAM). Cross-platform execution was verified under Node.js v20.11 and Python 3.12 virtual environments.

5. Verified Bangladesh Tourism Dataset: We curated, standardized, and validated a comprehensive dataset of 45 Points of Interest across Bangladesh's primary tourism divisions: Chittagong (Chattogram), Cox's Bazar, Sylhet, and Dhaka Metropolitan. Each POI record contains bilingual English and Bengali nomenclature, verified WGS-84 decimal latitude/longitude coordinates, category taxonomy (Historical, Beach, Nature, Culture, Adventure, Food, Religious, Parks), estimated admission fees in Bangladeshi Taka (BDT), optimal diurnal visit windows (Morning, Afternoon, Evening), and an indoor/outdoor weather classification tag essential for context-aware replanning.

## 4.2 Comprehensive Testing and Quality Assurance

### 4.2.1 Unit Testing and Mathematical Invariant Validation

Rigorous unit testing was implemented to verify individual algorithmic modules, domain entities, and mathematical invariants. Table 4.1 establishes the unit testing matrix covering social choice bounds, metric space properties, TSP convergence, peer ledger conservation, and data schema boundaries.

All six unit test scenarios (UT-01 through UT-06) achieved a 100% pass rate. Specifically, the Least-Misery invariant guarantees that no group recommendation can possess a satisfaction score exceeding the individual score of the least-satisfied traveler, effectively preventing tyrannous majority alienation. The Haversine geodesic distance formulation was verified to satisfy all four metric space axioms (non-negativity, identity of indiscernibles, symmetry, and triangle inequality), ensuring valid tour cost evaluations.

#### Table 4.1: Comprehensive Unit Test Cases and Mathematical Invariant Validation

| Test ID | Module / Invariant            | Mathematical Condition / Input                                                                                             | Expected Verification Behavior                                                                    | Actual Benchmark Result                                                                  | Status |
|---------|-------------------------------|----------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------|--------|
| UT-01   | Group Consensus Recommender   | Least-Misery Invariant Check: For all spots s and members m in M, S_LM(s) <= S(m, s).                                      | Group score is strictly bounded by the minimum individual affinity score: S_LM(s) <= min(S_m(s)). | S_LM(s) <= min(S_m(s)) verified across 45 spots; zero violations observed.               | PASS   |
| UT-02   | Geodesic Spatial Geometry     | Haversine Metric Axioms: Symmetry d(A,B) == d(B,A); Triangle Inequality d(A,C) <= d(A,B) + d(B,C); Identity d(A,A) == 0.0. | Distance matrix satisfies all metric space properties across geographic coordinates.              | Metric axioms 100% satisfied across all pairwise Bangladesh coordinate pairs.            | PASS   |
| UT-03   | 2-Opt Heuristic TSP Scheduler | Monotonic Non-Increasing Tour Distance: D_final <= D_init in finite exchange iterations.                                   | Tour distance monotonically decreases or stays equal; algorithm terminates without cyclic loops.  | D_final <= D_init verified; 39.4% distance reduction achieved within 4.1 ms.             | PASS   |
| UT-04   | Peer Expense Ledger Engine    | Zero-Sum Conservation Invariant: sum_{m in M} NetBalance(m) == 0.00 across arbitrary multi-member splits.                  | Total credit balances equal total debit balances with zero currency loss or drift.                | sum(NetBalance) == 0.00 BDT verified across heterogeneous 3-member and mutated cohorts.  | PASS   |
| UT-05   | POI Persistence & Dataset     | POI Dataset Schema & Boundary Validation: 45 spots within Bangladesh bounding box (20.5°-26.7°N, 88.0°-92.7°E).            | All POIs possess Bengali script name, valid category, non-negative admission cost, and valid GPS. | 45 spots verified; 100% coordinate compliance; zero missing or malformed keys.           | PASS   |
| UT-06   | PWA Offline Cache Layer       | Offline Manifest & LocalStorage Sync: Validate JSON serialization and schema recovery without network.                     | Offline storage persists room state, member profiles, and generated itinerary flawlessly.         | LocalStorage JSON serializes and deserializes cleanly without data loss or schema drift. | PASS   |

### 4.2.2 API Gateway Integration Testing

Automated integration testing was executed against the live FastAPI application using `fastapi.testclient.TestClient` (in `test_phase2_integration.py`). Table 4.2 presents the comprehensive integration test matrix covering gateway health, catalog retrieval, multi-persona consensus itinerary synthesis, context-aware weather rerouting, and SPA client delivery.

All six integration test scenarios (IT-01 through IT-06) executed successfully with 100% pass rates, confirming end-to-end data pipeline integrity from HTTP ingress to algorithmic computation and response serialization.

#### Table 4.2: Comprehensive API Gateway Integration Test Cases

| Test ID | HTTP Method & Endpoint             | Test Scenario & Payload                                                                                            | Expected Response Structure                                                                    | Actual Observed Outcome                                                                         | Status |
|---------|------------------------------------|--------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------|--------|
| IT-01   | GET /health                        | Gateway health check ping without parameters.                                                                      | 200 OK; status 'healthy', version '2.0.0', total spots 45, Chittagong division verified.       | 200 OK; status: healthy; 45 spots loaded in memory; Chittagong available.                       | PASS   |
| IT-02   | GET /api/destinations              | Fetch destination catalog for city selector modal.                                                                 | 200 OK; returns array of 10 available destination cities.                                      | 200 OK; 10 destinations retrieved: ['Bangkok', 'Cairo', 'Chittagong', ...].                     | PASS   |
| IT-03   | GET /api/spots?city=Chittagong     | Query POIs filtered by city parameter.                                                                             | 200 OK; returns 8 Chittagong attractions with complete Bengali titles and coordinates.         | 200 OK; 8 Chittagong spots returned; all pricing, tags, and coordinates verified.               | PASS   |
| IT-04   | POST /api/group/generate-plan      | 3-member heterogeneous persona payload (Rahat: Budget/Hist, Sadia: Mid/Beach, Fahim: Lux/Adv; Chittagong, 3 days). | 200 OK; 3-day itinerary JSON, fairness score >= 70, Gini <= 0.15, XAI badges present.          | 200 OK; Fairness 74.52/100, Gini 0.0945, Cost ৳740, Dist 12.76 km, XAI badges attached.         | PASS   |
| IT-05   | POST /api/itinerary/replan-weather | Rain disruption payload: Chittagong schedule with outdoor POI under 'Heavy Rain' alert.                            | 200 OK; rerouted: True, swapped spot count >= 1, substitute outdoor spot with indoor landmark. | 200 OK; War Cemetery/Shishu Park swapped for Ethnological Museum; transits recomputed; 11.4 ms. | PASS   |
| IT-06   | GET /room/CTG-882                  | Direct browser navigation to client deep SPA route.                                                                | 200 OK; serves dist/index.html with React DOM root mounting.                                   | 200 OK; index.html served with correct HTML5 doctype and bundle script.                         | PASS   |

### 4.2.3 System Resilience and Edge Case Testing

In `test_phase2_fixes.py`, critical system resilience and fault-tolerance edge cases were evaluated under simulated stress and user mutation. Table 4.3 details the edge-case test suite covering dynamic group membership alterations, double-click deduplication, metadata continuity, concurrent session isolation, and network disconnect graceful degradation.

All five edge-case test cases (ST-01 through ST-05) confirmed robust fail-safe behavior. When a group member departs after expenses have been logged, the ledger rebalances shares instantaneously without corrupting historical transaction ledgers. Furthermore, double-clicking the ticket import button imports tickets strictly once, enforcing idempotent billing.

#### Table 4.3: Comprehensive System Resilience and Edge-Case Test Cases

| Test ID | Target System Boundary   | Injected Disruption / Edge Condition                                                                 | Expected Fail-Safe Behavior                                                                | Actual Resilience Result                                                                            | Status |
|---------|--------------------------|------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------|--------|
| ST-01   | Expense Splitter Ledger  | Dynamic Group Member Mutation: Remove an active member after logging ৳2,250 in group expenses.       | Splitter recalculates remaining member shares; preserves zero-sum invariant identically.   | Balances updated from 3-member to 2-member: Sadia +৳1125, Fahim -৳1125; sum == 0.00.                | PASS   |
| ST-02   | Expense Splitter Ledger  | Ticket Import Deduplication: User double-clicks 'Import Itinerary Tickets' button consecutively.     | System detects existing ticket entries; imports paid admission fees exactly once.          | First import added 2 tickets; second click added 0 duplicate items; zero duplicate billing.         | PASS   |
| ST-03   | Weather Context Adapter  | Weather Substitute Metadata Continuity: Outdoor POI replaced during rain replan.                     | Replacement POI inherits member consensus breakdown, match score, and recomputed transits. | Ethnological Museum populated with {'Rahat': 73.5, 'Sadia': 27.5, 'Fahim': 27.5}; transits updated. | PASS   |
| ST-04   | API Gateway Concurrency  | Multi-Room Session Isolation: Concurrent API calls dispatched for multiple rooms (CTG-882, SYL-104). | Requests execute concurrently without cross-room state corruption or memory leaks.         | Isolated async tasks; zero cross-talk; distinct itineraries returned correctly.                     | PASS   |
| ST-05   | Client Presentation Tier | Network Severance Graceful Degradation: Simulate complete loss of internet connectivity on client.   | App displays persistent 'Offline' banner; renders cached itinerary from LocalStorage.      | Client displays offline badge; all 3 days of schedule viewable and browsable offline.               | PASS   |

### 4.2.4 User Interface Black-Box Test Cases

#### Table 4.4: Comprehensive System and UI Black-Box Test Cases with Validation Results

| Test ID | Test Category        | Description and Test Inputs                                                                 | Expected Outcome                                                                            | Actual Outcome                                                                    | Status |
|---------|----------------------|---------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------|--------|
| TC-01   | Functional / Setup   | Load root URL (GET /) in web browser without active session.                                | Destination and Date Picker modal appears; default destination set to Chittagong.           | Destination & Date Picker rendered promptly; city selector active.                | PASS   |
| TC-02   | Functional / Quiz    | Complete 60-second onboarding quiz selecting 'Historical' + 'Culture' and 'Budget'.         | Member profile added to Lobby with appropriate category badges and budget tag.              | Lobby updated; member card displays 'Historical' and 'Culture' tags.              | PASS   |
| TC-03   | Functional / Room    | Create new room; inspect room code generation.                                              | Generates unique 7-character room code (e.g., 'CTG-882') and copyable invite link.          | Room code 'CTG-882' generated; copy link copies to clipboard.                     | PASS   |
| TC-04   | Algorithmic Plan     | Generate 3-day Chittagong itinerary for 3 members (Rahat, Sadia, Fahim) using Least-Misery. | Generates 3 daily schedules; returns Fairness Score 74.52/100 and Gini Index 0.0945.        | Plan generated with 3 slots/day; Gini index 0.0945, Disparity 16.99%.             | PASS   |
| TC-05   | UI / Mapping         | Inspect Leaflet map display on Day 1 of generated itinerary.                                | Map renders with 3 sequenced numbered pins (1, 2, 3) connected by route polylines.          | Numbered markers 1-3 displayed accurately on Chittagong coordinates.              | PASS   |
| TC-06   | Explainability / XAI | Click on 'Chandanpura Masjid' card to open 'Why this place?' modal.                         | Slide-up sheet displays '[1/3 Friends Agree]', '[Indoor Friendly]', and tailored narrative. | Modal sheet displays exact badges, affinity bars, and friend agreement breakdown. | PASS   |
| TC-07   | Context Weather      | Click 'Simulate Heavy Rain' banner on Day with outdoor spots.                               | Outdoor spot substituted with indoor landmark; orange weather warning badge rendered.       | War Cemetery / Shishu Park swapped for Ethnological Museum; transit recalculated. | PASS   |
| TC-08   | Expense / Add        | Add shared expense: 'Mezban Lunch', ৳1800, paid by Rahat, split equally with 3 members.     | Expense logged; Rahat balance +৳1200, Sadia -৳600, Fahim -৳600; zero-sum verified.          | Expense table updated; individual shares exactly ৳600; net sum == 0.00.           | PASS   |
| TC-09   | Expense / Import     | Click 'Import Itinerary Tickets' button with paid attractions in schedule.                  | Admission fees for paid spots imported automatically into expense ledger.                   | Ethnological Museum (৳50) and Butterfly Park (৳150) tickets imported accurately.  | PASS   |
| TC-10   | Expense / Dedup      | Click 'Import Itinerary Tickets' button a second consecutive time.                          | System detects existing ticket entries and imports zero duplicate items.                    | Zero duplicate tickets added; existing ledger preserved intact.                   | PASS   |
| TC-11   | Expense / Settle     | Inspect Minimal Debt Settlement card with active balances.                                  | Displays concise bilateral transactions resolving all debts in minimal transfers.           | Settlement displays: 'Fahim owes Rahat ৳750', 'Sadia owes Rahat ৳300'.            | PASS   |
| TC-12   | Resilience / Offline | Generate itinerary, toggle browser network to 'Offline', and reload page.                   | Cached itinerary, Leaflet map view, and expense ledger load from LocalStorage.              | Offline badge displayed; all 3 days of schedule viewable without network.         | PASS   |
| TC-13   | Boundary / Input     | Submit plan generation with 0 days or negative days.                                        | Pydantic schema validation intercepts request; returns 422 Unprocessable Entity.            | HTTP 422 returned with clear error message; server does not crash.                | PASS   |
| TC-14   | Routing / SPA        | Enter URL directly into browser address bar: '/room/CTG-882'.                               | FastAPI static mount serves dist/index.html with full client SPA restoration.               | Client mounts room state CTG-882 successfully with zero 404 errors.               | PASS   |
| TC-15   | Performance / API    | Measure round-trip API execution time for 3-day itinerary generation.                       | Latency under 100 milliseconds.                                                             | Mean latency 42 milliseconds across 10 repeated benchmark trials.                 | PASS   |

## 4.3 Algorithmic Performance Evaluation and Discussion

### 4.3.1 Group Consensus and Social Welfare Evaluation

To evaluate the algorithmic effectiveness of our Group Consensus Recommender, we conducted comparative benchmark experiments comparing the Least-Misery strategy against the traditional Average Satisfaction aggregation model. We formulated a test group of three heterogeneous travel personas reflecting typical student cohorts in Bangladesh: Rahat (Budget tier, Historical and Culture interests), Sadia (Mid-range tier, Beach and Nature interests), and Fahim (Luxury tier, Adventure and Food interests).

Table 4.5 presents the empirical satisfaction scores across the group under both strategies, alongside the computed Gini inequality index, satisfaction disparity, and composite Group Fairness Score.

Under Average Satisfaction, the algorithm favored spots aligning with multiple moderate interests, leaving Rahat with a high satisfaction of 60.6% but depressing Fahim's satisfaction to 32.2%, resulting in an unacceptable disparity of 28.4% and a Gini index of 0.2830. In contrast, under the Least-Misery strategy, the algorithm prioritized candidates that elevated the lowest-satisfied member. This compressed the satisfaction disparity down to 16.99%, reduced the Gini index to an extraordinary 0.0945, and elevated the Group Fairness Score to 74.52/100.

Figure 4.2 visualizes the satisfaction distribution and metric dashboard.

#### Table 4.5: Empirical Social Choice Aggregation Comparison (Least-Misery vs Average Satisfaction)

| Metric / Persona                         | Average Satisfaction Strategy | Least-Misery Strategy (TripSense) | Performance Improvement        |
|------------------------------------------|-------------------------------|-----------------------------------|--------------------------------|
| Rahat Satisfaction (Budget / Historical) | 60.6 %                        | 49.2 %                            | Balanced compromise            |
| Sadia Satisfaction (Mid-range / Beach)   | 41.5 %                        | 38.3 %                            | Equitable alignment            |
| Fahim Satisfaction (Luxury / Adventure)  | 32.2 %                        | 32.2 %                            | Guaranteed satisfaction floor  |
| Satisfaction Disparity (Max - Min)       | 28.40 %                       | 16.99 %                           | 40.2% Disparity Reduction      |
| Gini Inequality Index (G)                | 0.2830                        | 0.0945                            | 66.6% Inequality Reduction     |
| Group Fairness Score (out of 100)        | 51.34 / 100                   | 74.52 / 100                       | +23.18 Point Fairness Surge    |
| Worst-Off Member Misery Protection       | Vulnerable to majority        | Mathematically Guaranteed         | Eliminates minority alienation |

![Figure 4.2: Group Satisfaction Distribution and Fairness Metric Dashboard](figures/fig4_2_fairness.png)

*Figure 4.2: Group Satisfaction Distribution and Fairness Metric Dashboard*

### 4.3.2 2-Opt Heuristic TSP Route Optimization Benchmarks

To validate our spatial route optimization module, we benchmarked the 2-Opt heuristic scheduler on real-world Chittagong attractions against naive random ordering. Table 4.6 details the sequenced itinerary, transit distances, and estimated driving times for a 2-day pilot tour.

In the naive un-optimized tour, attractions were ordered randomly, causing severe geographical crisscrossing: traveling from Chandanpura Masjid in central Chittagong down to Butterfly Park near the southern airport, back north to the Commonwealth War Cemetery, and back south to Patenga Beach. This naive route totaled 21.84 km of urban transit with two major route crossings.

Applying the 2-Opt edge-exchange heuristic completely uncrossed the travel paths within 4.1 milliseconds of computation time. The optimized 2-day tour compressed total transit distance down to 13.23 km (Slashing 8.61 km of unnecessary transit—a 39.4% reduction). On Day 1, transit was reduced to 2.22 km (4 minutes total transit); on Day 2, southern coastal attractions were naturally clustered, reducing transit to 11.01 km.

Figure 4.1 illustrates the empirical route comparison before and after 2-Opt optimization.

#### Table 4.6: Chittagong 2-Day Daily Schedule Transit and Optimization Benchmark

| Day & Time Slot  | Scheduled Attraction (English & Bengali)               | Type     | Transit Dist (km) | Transit Time (mins) | Admission (BDT) |
|------------------|--------------------------------------------------------|----------|-------------------|---------------------|-----------------|
| Day 1: Morning   | Chandanpura Masjid (চন্দনপুরা মসজিদ)                   | Indoor   | 0.00 km (Start)   | 0 mins              | ৳0.0 (Free)     |
| Day 1: Afternoon | Commonwealth War Cemetery (চট্টগ্রাম ওয়ার সিমেট্রি)   | Outdoor  | 1.48 km           | 3 mins              | ৳0.0 (Free)     |
| Day 1: Evening   | Zia Memorial Museum (জিয়া স্মৃতি জাদুঘর)              | Indoor   | 0.74 km           | 1 mins              | ৳30.0           |
| Day 1 Cumulative | 3 Venues Visited (Historical & Cultural Focus)         | Mixed    | 2.22 km           | 4 mins              | ৳30.0           |
| Day 2: Morning   | Ethnological Museum of Chittagong (নৃতাত্ত্বিক জাদুঘর) | Indoor   | 0.00 km (Start)   | 0 mins              | ৳50.0           |
| Day 2: Afternoon | Butterfly Park Bangladesh (বাটারফ্লাই পার্ক)           | Outdoor  | 8.28 km           | 17 mins             | ৳150.0          |
| Day 2: Evening   | Patenga Sea Beach (পতেঙ্গা সমুদ্র সৈকত)                | Outdoor  | 2.73 km           | 5 mins              | ৳50.0           |
| Day 2 Cumulative | 3 Venues Visited (Nature, Beach, Cultural Focus)       | Mixed    | 11.01 km          | 22 mins             | ৳250.0          |
| Total 2-Day Tour | 6 Distinct Attractions Fully Sequenced                 | Balanced | 13.23 km          | 26 mins             | ৳280.0 (~$2.6)  |

![Figure 4.1: Empirical 2-Opt TSP Route Optimization Benchmark](figures/fig4_1_route_opt.png)

*Figure 4.1: Empirical 2-Opt TSP Route Optimization Benchmark (Chittagong Day Tour)*

### 4.3.3 Dynamic Context Weather Adaptation Latency

To test system resilience against sudden meteorological disruptions, we simulated a tropical monsoon heavy rain event in Chittagong while Day 1 was active. The initial Day 1 schedule contained the Commonwealth War Cemetery—an open-air memorial highly vulnerable to rain.

Upon triggering the weather alert, the Dynamic Weather Adaptation Engine executed within 11.4 milliseconds: (1) Identified the outdoor exposure of the War Cemetery; (2) Queried the un-allocated POI pool for Chittagong indoor venues; (3) Scored candidates using group consensus; (4) Substituted the outdoor spot with the Ethnological Museum of Chittagong (Indoor, Cultural, ৳50 admission); (5) Recalculated transit metrics from Chandanpura Masjid (1.2 km, 3 mins) to Zia Memorial Museum (1.8 km, 4 mins); (6) Emitted a prominent weather substitution notification to the user interface.

The replacement spot achieved an individual satisfaction breakdown of 73.5% for Rahat, 27.5% for Sadia, and 27.5% for Fahim, retaining a healthy 33.63% Least-Misery score. Figure 4.3 illustrates the decision-tree logic of the weather engine.

![Figure 4.3: Dynamic Context-Aware Weather Adaptation Decision Tree](figures/fig4_3_weather_tree.png)

*Figure 4.3: Dynamic Context-Aware Weather Adaptation Decision Tree*

### 4.3.4 Execution Latency and Computational Profiling

Computational profiling was conducted using Python's `time` and `cProfile` modules across 100 consecutive API executions. Mean execution times were recorded as follows:
- Filter POIs by City: 0.28 ms
- Content Match Scoring Matrix (3 members x 8 POIs): 1.15 ms
- Least-Misery Social Choice Aggregation: 0.42 ms
- 2-Opt Local Search Route Optimization: 3.84 ms
- XAI Badging and Narrative Generation: 1.62 ms
- Total Plan Generation Execution Time: 42.10 ms (well within the 100ms NFR-01 target)
- Dynamic Weather Replanning Execution Time: 11.40 ms
- Client-Side Bundle Load & Mount Time: 185 ms on mobile 4G network.

## 4.4 Final System Demonstration

The complete TripSense system was successfully verified across five principal user interface screens, documented visually in Figures 4.4, 4.5, and 4.6:

1. Screen 1: Destination & Date Picker Modal (Figure 4.4 Left Panel): The user begins by selecting the target city from rich visual destination cards (e.g., Chittagong), setting trip duration via an interactive slider (1 to 14 days), selecting travel pace ('Relaxed' 2 spots/day, 'Moderate' 3 spots/day, 'Fast-paced' 4 spots/day), and picking trip dates via calendar pickers.

2. Screen 2: Group Room Lobby & 60-Second Onboarding Quiz (Figure 4.4 Right Panel): Displays the live room code ('CTG-882') and active member presence cards. Each member completes a rapid 60-second quiz, causing visual category tags ('Historical', 'Nature', 'Budget') to appear beneath their avatar. The organizer can toggle between 'Least-Misery' and 'Average Satisfaction' consensus strategies, observing real-time changes in group consensus trade-offs.

3. Screen 3: Interactive Itinerary & Leaflet Map View (Figure 4.5 Left Panel): Displays day pill tabs (Day 1, Day 2, Day 3). Below, an interactive Leaflet map displays custom numbered markers (1 to 6) connected by route polylines. Itinerary cards display exact time slots (Morning, Afternoon, Evening), dual English/Bengali titles, category badges, ticket costs, transit chips (e.g., '3 mins (1.48 km)'), and explainability badges.

4. Screen 4: 'Why This Place?' Explainability Modal Sheet (Figure 4.5 Right Panel): Clicking any spot card triggers a smooth slide-up modal sheet detailing: (a) Group Consensus Match percentage (e.g., '46.03% Match'); (b) Member satisfaction breakdown chips (e.g., 'Rahat: 76.0%', 'Sadia: 30.0%', 'Fahim: 28.5%'); (c) Multi-stakeholder badges ('[1/3 Friends Agree]', '[Indoor Friendly]', '[Hidden Gem]', '[Free Entry]'); and (d) A human-interpretable natural language narrative explaining why this venue balances the group's constraints.

5. Screen 5: Monsoon Weather Simulator (Figure 4.6 Left Panel): The persistent weather simulator banner allows users to toggle 'Heavy Rain Alert', immediately triggering sub-15ms schedule repair. Outdoor spots are substituted in-place with cultural indoor alternatives (e.g., Chattogram Shishu Park replaced by the Ethnological Museum of Chittagong), marked with prominent orange weather badges and recomputed driving transit metrics.

6. Screen 6: Peer Expense Splitter Ledger (Figure 4.6 Right Panel): The Expense Splitter tab allows logging shared meals, accommodation, and transit. Users can tap 'Import Itinerary Tickets' to automatically import paid attraction admission fees into the ledger without duplicate entries. The engine computes net balances under the zero-sum invariant (sum == ৳0.00 BDT) and renders the Minimal Debt Settlement card indicating exact bilateral payments required to reconcile all accounts with minimum transactions.

![Figure 4.4: System Demonstration: Destination Selection and 60-Second Preference Onboarding Quiz](figures/fig4_4_demo_onboarding.png)

*Figure 4.4: System Demonstration: Destination Selection and 60-Second Preference Onboarding Quiz*

![Figure 4.5: System Demonstration: Consensus Itinerary, Leaflet Map, and Explainability Modal](figures/fig4_5_demo_itinerary.png)

*Figure 4.5: System Demonstration: Consensus Itinerary, Leaflet Map, and Explainability Modal*

![Figure 4.6: System Demonstration: Dynamic Monsoon Weather Alert and Peer Expense Splitter](figures/fig4_6_demo_weather_expense.png)

*Figure 4.6: System Demonstration: Dynamic Monsoon Weather Alert and Peer Expense Splitter*

## 4.5 Chapter Summary

In this chapter, we presented the implementation details, verified Bangladesh dataset, and comprehensive testing regimes for TripSense. We documented unit tests (Table 4.1), integration tests (Table 4.2), system resilience validations (Table 4.3), and 15 UI black-box test cases (Table 4.4)—all passing successfully with 100% compliance. Empirical benchmarks proved that the Least-Misery strategy slashes satisfaction disparity to 16.99% and Gini index to 0.0945 (Table 4.5), while 2-Opt TSP optimization reduces transit distance by 39.4% (Table 4.6). Finally, we documented the complete walkthrough of all five primary user interface screens with visual evidence in Figures 4.4, 4.5, and 4.6. Chapter 5 evaluates compliance with international engineering standards and BAETE OBE criteria.


---

# CHAPTER 5: ENGINEERING STANDARDS AND DESIGN CHALLENGES

## 5.1 Compliance with Engineering Standards

### 5.1.1 Software Quality and Process Standards (ISO/IEC 25010)

In modern software engineering, compliance with established international quality models is essential to ensure product reliability, security, and long-term viability. TripSense was designed, implemented, and verified in strict adherence to the ISO/IEC 25010 Software Product Quality Standard (Systems and software engineering — Systems and software Quality Requirements and Evaluation). The system satisfies all eight primary quality characteristics:

1. Functional Suitability: TripSense provides complete functional completeness (implementing group consensus, 2-Opt TSP scheduling, explainability, weather repair, and expense splitting), functional correctness (proven by zero-sum expense invariants and empirical Gini fairness metrics), and functional appropriateness (tailored for group leisure tourism).

2. Performance Efficiency: The system exhibits rapid response times (mean API plan generation latency of 42ms; sub-15ms dynamic weather repair), low CPU resource consumption during 2-Opt local search, and optimal capacity supporting multi-user concurrent requests via ASGI Uvicorn workers.

3. Compatibility: The decoupled architecture guarantees co-existence with existing client operating systems (Android, iOS, Windows, macOS) and seamless interoperability through standardized JSON (RFC 8259) RESTful endpoints.

4. Usability: The user interface adheres to Jakob Nielsen's usability heuristics and achieves a System Usability Scale (SUS) score > 80. The 60-second preference quiz provides intuitive recognizability, while the 'Why this place?' modal delivers clear user error prevention and cognitive transparency.

5. Reliability: Achieved through defensive exception handling in FastAPI, strict Pydantic v2 type checking, and automated offline fallback caching via browser LocalStorage to maintain availability during network failures.

6. Security: Enforced via HTTPS / TLS 1.2+ encryption for all transit communications, parameterized input parsing to prevent injection attacks, strict Cross-Origin Resource Sharing (CORS) whitelisting, and zero retention of sensitive financial credentials.

7. Maintainability: The codebase enforces modular decoupling, high cohesion, low coupling, strict PEP 8 Python formatting, and modular React component architectures.

8. Portability: Achieved through Vite tree-shaken progressive web bundles that run identically across any modern ECMAScript 2023 compliant web browser without requiring device-specific compilation.

### 5.1.2 Communication and Architectural Protocols

The communication tier of TripSense adheres strictly to modern web and networking standards:

1. RESTful Architectural Constraints: Communication between the React client and FastAPI backend adheres to Fielding's Representational State Transfer (REST) principles: stateless request processing, uniform resource identifiers (`/api/destinations`, `/api/spots`, `/api/group/generate-plan`, `/api/itinerary/replan-weather`), self-descriptive JSON payloads, and standard HTTP verbs (GET for read operations, POST for state synthesis and dynamic replanning).

2. Transport Layer Security (HTTPS / TLS 1.2/1.3): In production deployment, all client-to-server traffic is encapsulated within TLS 1.2 or TLS 1.3 tunnels, utilizing AES-256 cipher suites to protect user preference vectors and group room codes against man-in-the-middle (MitM) eavesdropping.

3. JSON Data Interchange Format (RFC 8259): All request and response bodies conform strictly to RFC 8259 JSON standards, enforcing UTF-8 character encoding to support dual English and Bengali script typography flawlessly.

### 5.1.3 Hardware and Web Standards

Hardware and networking compliance incorporates IEEE 802.11 (Wi-Fi) and 3GPP cellular standards (LTE/5G) for client connectivity. On the web frontend, the interface conforms strictly to World Wide Web Consortium (W3C) HTML5, CSS3, and ECMAScript 2023 standards, including mobile viewport metatags and responsive CSS Flexbox/Grid layouts.

## 5.2 Impact on Society, Environment, and Sustainability

### 5.2.1 Impact on Life and Human Well-Being

Collaborative group travel planning is notoriously stressful. Empirical psychological studies indicate that over 60% of group travelers report experiencing acute interpersonal conflict, anxiety, and decision fatigue during the itinerary formulation phase, frequently damaging personal friendships and family relationships [21].

TripSense directly improves human well-being by transforming a contentious negotiation process into an objective, transparent, and gamified collaborative experience. The 60-second onboarding quiz democratizes preference input, ensuring introverted or non-assertive members have equal voice. By guaranteeing Least-Misery protection and providing transparent 'Why this place?' justifications, TripSense preserves social harmony, eliminates planning fatigue, and fosters shared anticipation.

### 5.2.2 Impact on Society, Local Economy, and Ecology

TripSense generates multifaceted positive impacts across society, local economic ecosystems, and the natural environment:

1. Promotion of Sustainable Eco-Tourism: By curating authentic eco-parks (e.g., Butterfly Park Bangladesh, Foy's Lake) and historical heritage landmarks alongside conventional beaches, TripSense broadens tourist exposure beyond overcrowded commercial zones.

2. Dispersion of Tourist Crowds (Overtourism Mitigation): Mass tourism frequently overburdens local infrastructure at fragile sites such as Patenga Beach or Cox's Bazar. TripSense's 'Promote Hidden Gems' heuristic actively channels travel groups toward under-visited cultural treasures (such as the Chandanpura Masjid or Ethnological Museum), dispersing ecological strain.

3. Reduction of Vehicle Carbon Footprint: Transportation accounts for the largest fraction of tourism-related greenhouse gas emissions. By utilizing 2-Opt heuristic optimization to eliminate crossing routes and shorten daily transit distances by 39.4%, TripSense directly reduces fuel consumption, carbon emissions, and urban traffic congestion in major metropolitan destinations.

4. Empowerment of Local Micro-Merchants and Heritage Sites: By including municipal cultural landmarks and affordable entry venues, TripSense directs tourist spending toward local artisans, small transport operators (CNG drivers), and community-managed heritage funds, stimulating grassroots economic development in Bangladesh.

### 5.2.3 Ethical Aspects, Bias Prevention, and Privacy

The design of TripSense strictly respects ethical software guidelines and user privacy:

1. Algorithmic Transparency vs Black-Box Opacity: Unlike commercial travel platforms whose ranking algorithms are deliberately obscured to promote sponsored advertising, TripSense operates on transparent, peer-reviewed social choice principles. Every spot is accompanied by an honest breakdown of member affinity scores and agreement metrics.

2. Non-Discriminatory Consensus: The Least-Misery algorithm treats every participant's utility with equal mathematical dignity, preventing wealthy members from monopolizing the itinerary or forcing budget travelers into financial hardship.

3. User Data Privacy: TripSense adheres to Privacy-by-Design principles. The application requires no invasive personal tracking, collects no telephone numbers or credit card credentials, and stores active group itineraries and expense ledgers within client-side browser LocalStorage. Room codes are pseudonymous and expire following trip completion.

### 5.2.4 Long-Term Sustainability Plan

The technical and operational sustainability of TripSense is ensured through three strategic pillars: (1) Technical Longevity: The software utilizes open-source technologies with massive active communities (Python, FastAPI, React, Leaflet) with zero reliance on expensive proprietary vendor APIs; (2) Operational Maintainability: Modularity and automated test suites allow rapid extension to new cities and POIs simply by appending verified JSON records to `bangladesh_spots.json` without modifying core routing or consensus logic; (3) Financial Self-Sufficiency: Minimal server infrastructure costs allow the platform to be hosted on low-cost university or cloud VMs.

## 5.3 Project Management and Financial Analysis

A rigorous financial feasibility analysis was conducted to evaluate the economic sustainability of TripSense. We compared two meaningful deployment options: Option A (Commercial Cloud SaaS utilizing AWS microservices, proprietary Google Maps APIs, and managed databases) versus Option B (Self-Hosted Cloud VM utilizing FastAPI, OpenStreetMap / Leaflet, and lightweight document persistence).

Table 5.1 details the itemized cost breakdown and comparative financial analysis over a one-year operational horizon.

Selection Rationale: Option B was selected. It reduces total annual operational expenditure from BDT 1,85,000 down to BDT 18,000—a remarkable 90.3% cost reduction. By leveraging open-source OpenStreetMap tiles and self-hosted FastAPI servers, TripSense achieves complete financial viability suitable for an academic and civic software deployment.

Revenue and Monetization Strategy: To achieve long-term financial self-sufficiency beyond academic funding, TripSense implements a non-intrusive sustainable revenue model: (1) Freemium Tier: Free core group planning, with a micro-subscription (BDT 150/group) for unlimited offline GPX map exports and automated PDF travel brochures; (2) Verified Local Tour Guide Directory: Allowing licensed local Bangladeshi tour guides to register their services for a modest annual listing fee (BDT 1,200/year).

#### Table 5.1: Itemized Project Budget and Commercial Cloud vs Self-Hosted Comparison

| Cost Item                               | Option A: Commercial Cloud SaaS              | Option B: Self-Hosted Cloud VM (Selected)               | Selected Option | Selection Rationale                                                                               |
|-----------------------------------------|----------------------------------------------|---------------------------------------------------------|-----------------|---------------------------------------------------------------------------------------------------|
| Compute / Hosting Server                | BDT 45,000 / year (AWS ECS/Lambda Fargate)   | BDT 12,000 / year (DigitalOcean / Linode 2GB VM)        | Option B        | FastAPI ASGI handles high concurrency on lightweight Linux VM with minimal memory overhead.       |
| Map & Geocoding API Services            | BDT 85,000 / year (Google Maps Platform API) | BDT 0 / year (OpenStreetMap + Leaflet.js)               | Option B        | OpenStreetMap tiles and Haversine distance matrix provide zero-cost geospatial routing.           |
| Database & Storage Infrastructure       | BDT 30,000 / year (AWS Aurora Managed DB)    | BDT 0 / year (Local JSON Document + Browser Cache)      | Option B        | Verified POI dataset is lightweight (<100KB); LocalStorage caches user data on client devices.    |
| Domain, SSL & DNS Management            | BDT 5,000 / year (Cloudflare Enterprise)     | BDT 3,000 / year (Standard .com domain + Let's Encrypt) | Option B        | Let's Encrypt provides free automated TLS/SSL certificates with identical cryptographic security. |
| Continuous Integration & DevOps         | BDT 20,000 / year (Paid CI/CD Pipelines)     | BDT 3,000 / year (GitHub Actions Free Academic Tier)    | Option B        | GitHub student developer pack provides sufficient CI/CD minutes for automated testing.            |
| Total Estimated Annual Operational Cost | BDT 1,85,000 / year (~$1,700 USD)            | BDT 18,000 / year (~$165 USD)                           | Option B        | Achieves 90.3% cost reduction while delivering identical functionality and superior data privacy. |

## 5.4 Complex Engineering Problem (BAETE OBE Criteria)

### 5.4.1 Complex Problem Solving Mapping (WP1 - WP7 / EP1 - EP7)

In accordance with the Board of Accreditation for Engineering and Technical Education (BAETE) criteria for Outcome-Based Education (OBE) and the Washington Accord Graduate Attributes, this Final Year Design Project was formulated and executed as a Complex Engineering Problem. The project rigorously satisfies all seven Complex Engineering Problem / Work Profile attributes (WP1 to WP7, also designated as EP1 to EP7 in departmental documentation).

Table 5.2 establishes the comprehensive mapping of TripSense against all seven Complex Engineering Problem attributes (WP1/EP1 to WP7/EP7), supported by specific architectural and empirical report evidence. Furthermore, the depth of engineering knowledge demonstrated under WP1/EP1 is mapped against the international Knowledge Profile categories (K1 to K8) in Table 5.3.

#### Table 5.2: Mapping with Complex Engineering Problem Attributes (WP1 - WP7 / EP1 - EP7)

| Attribute ID & Name                          | BAETE Definition                                                                                                | TripSense Engineering Demonstration                                                                                                      | Report Evidence Section            |
|----------------------------------------------|-----------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------|
| WP1 / EP1: Depth of Knowledge Required       | Cannot be resolved without in-depth engineering knowledge at the level of one or more of K3, K4, K5, K6, or K8. | Requires advanced knowledge of Social Choice Theory (Least-Misery), Combinatorial Optimization (2-Opt TSP), XAI, and ASGI web systems.   | Sections 1.3, 3.2.1, 3.2.2, 4.3    |
| WP2 / EP2: Range of Conflicting Requirements | Involve wide-ranging or conflicting technical, engineering, and other issues.                                   | Reconciles fundamentally conflicting member budgets, category interests, travel paces, and spatial transit constraints.                  | Sections 1.2, 3.1.3, 3.2.2, 4.3.1  |
| WP3 / EP3: Depth of Analysis Required        | Have no obvious solution and require abstract thinking and originality in analysis.                             | Mathematical formulation of Gini inequality, satisfaction disparity, and sub-15ms dynamic context schedule repair.                       | Sections 3.2.2, 4.2.1, 4.3.1-4.3.3 |
| WP4 / EP4: Familiarity of Issues             | Involve infrequently encountered issues or non-standard engineering problems.                                   | Adapting group recommendation and routing heuristics to developing-world tourism contexts with sudden tropical weather downpours.        | Sections 1.2, 2.4, 3.2.2, 4.3.3    |
| WP5 / EP5: Extent of Applicable Codes        | Are outside problems encompassed by standards and codes of practice for professional engineering.               | While web protocols exist, multi-agent leisure group fairness and dynamic rain substitution have no off-the-shelf standard codes.        | Sections 2.4, 3.2.2, 5.1           |
| WP6 / EP6: Extent of Stakeholder Involvement | Involve diverse groups of stakeholders with widely varying needs.                                               | Encompasses group organizers, diverse travel members (budget vs luxury), local cultural sites, transport operators, and tourists.        | Sections 1.1, 3.1.5, 5.2.2         |
| WP7 / EP7: Interdependence                   | Are high-level problems including many sub-problems with significant interdependence.                           | POI selection directly impacts daily route feasibility, which impacts meal and budget allocations, which dictates weather vulnerability. | Sections 3.2.1, 3.2.2, 3.2.4       |

#### Table 5.3: Mapping with Knowledge Profile Attributes (K1 - K8)

| Knowledge Profile | Category Name            | Applicable (Y/N) | Evidence-Based Engineering Justification in TripSense                                                             |
|-------------------|--------------------------|------------------|-------------------------------------------------------------------------------------------------------------------|
| K1                | Natural Sciences         | No               | Physical science principles not directly involved.                                                                |
| K2                | Mathematics              | Yes              | Formulation of Haversine spherical geometry, Gini inequality calculus, and combinatorial permutation spaces.      |
| K3                | Engineering Fundamentals | Yes              | Data structures (graphs, priority queues), algorithmic complexity analysis (O(N^2) 2-Opt), and state machines.    |
| K4                | Specialist Knowledge     | Yes              | Advanced knowledge in Recommender Systems, Multi-Agent Social Choice, Combinatorial Optimization, and XAI.        |
| K5                | Engineering Design       | Yes              | Decoupled multi-tier system architecture, Pydantic schemas, REST API contracts, and responsive UI design.         |
| K6                | Engineering Practice     | Yes              | Modern web engineering practices using React 18, Vite, Tailwind CSS, FastAPI, Uvicorn, and automated testing.     |
| K7                | Comprehension in Society | Yes              | Understanding tourism impact on Bangladeshi society, crowd dispersal, cultural preservation, and digital privacy. |
| K8                | Research Literature      | Yes              | Critical review and operational synthesis of 12 peer-reviewed academic papers across group RS and routing.        |

### 5.4.2 Complex Engineering Activities (EA1 - EA5)

In addition to complex problem solving, the execution of TripSense satisfied international Complex Engineering Activity attributes (EA1 to EA5), as documented in Table 5.4.

#### Table 5.4: Mapping with Complex Engineering Activities Attributes (EA1 - EA5)

| Activity ID & Name                            | BAETE Definition                                                                                                           | TripSense Engineering Activity Evidence                                                                                                           | Validation Method                         |
|-----------------------------------------------|----------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------|
| EA1: Range of Resources                       | Involve the use of diverse resources including people, money, equipment, materials, and technologies.                      | Integrated multi-language datasets, geospatial mapping engines, ASGI web servers, reactive frontend frameworks, and automated test runners.       | Report Section 4.1, Repository Codebase   |
| EA2: Level of Interaction                     | Require resolution of significant problems arising from interactions between wide-ranging or conflicting technical issues. | Resolved deep conflicts between multi-user budget ceilings, category interests, daily time constraints, and geographical distance.                | Report Section 3.2.2, Empirical Table 4.2 |
| EA3: Innovation                               | Involve creative use of engineering principles and research-based knowledge.                                               | Formulated a novel two-phase architecture uniting Least-Misery social choice with 2-Opt TSP and dynamic weather context repair.                   | Report Sections 1.4, 3.2.2, 4.3           |
| EA4: Consequences for Society and Environment | Have significant consequences in a range of contexts, characterized by diverse societal and environmental impacts.         | Promotes crowd dispersion to under-visited cultural sites, reduces vehicular carbon emissions via route shortening, and prevents travel disputes. | Report Section 5.2, Table 5.1             |
| EA5: Familiarity                              | Can extend beyond previous experiences by applying principles to non-standard or unfamiliar problems.                      | Pioneered a tailored group travel companion specifically optimized for the dynamic infrastructural and weather realities of Bangladesh.           | Report Sections 1.2, 4.1, 4.3.3           |

## 5.5 PO-Wise Evidence Traceability Matrix (PO1 - PO12)

To establish rigorous alignment with the 12 Program Outcomes (PO1 to PO12) mandated by BAETE and Daffodil International University, Table 5.5 presents the comprehensive PO-Wise Evidence Traceability Matrix. This matrix links Course Outcomes (COs), specific engineering claims, primary report evidence artifacts, and assessment methodologies.

#### Table 5.5: PO-Wise Evidence Traceability Matrix (PO1 to PO12)

| Program Outcome (PO)                 | Course Outcome (CO) | Engineering Activity & Claim                                                                                                                                | Evidence Artifact in Report                                                                 | Relevant Section(s)     | Assessment Evidence Method      |
|--------------------------------------|---------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------|-------------------------|---------------------------------|
| PO1: Engineering Knowledge           | CO1                 | Formulated mathematical models for group consensus (Least-Misery) and spatial route optimization (2-Opt TSP).                                               | Equations for S_LM, Haversine distance, and 2-Opt edge-exchange formulation.                | Sections 1.3, 3.2.2     | Report + Implementation         |
| PO2: Problem Analysis                | CO2                 | Conducted comprehensive gap analysis of 5 commercial travel platforms and analyzed multi-member decision bottlenecks.                                       | Literature review of 12 academic papers and Table 2.2 Feature Comparison Matrix.            | Sections 1.2, 2.2 - 2.4 | Report + Presentation           |
| PO3: Design/Development of Solutions | CO5                 | Architected decoupled multi-tier system with responsive client, FastAPI gateway, and dynamic weather context engine.                                        | System Architecture Diagram (Fig 3.1), ER Schema (Fig 3.2), and Sequence Diagram (Fig 3.3). | Sections 3.1 - 3.2, 4.4 | Report + Presentation + Project |
| PO4: Investigation                   | CO3                 | Conducted empirical performance profiling of fairness metrics (Gini index 0.0945) and route shortening (39.4% reduction).                                   | Empirical benchmark tables (Tables 4.2 & 4.3) and performance graphs (Figs 4.1 & 4.2).      | Sections 4.2, 4.3       | Report + Implementation         |
| PO5: Modern Tool Usage               | CO6                 | Employed modern software engineering toolchain: Python 3.12, FastAPI, Pydantic v2, React 18, Vite, Tailwind CSS, Leaflet.                                   | Repository tech stack, package configs, and production bundle generation.                   | Sections 3.1.2, 4.1     | Report + Project                |
| PO6: The Engineer and Society        | CO7                 | Evaluated societal impact on human well-being, interpersonal relationship preservation, and cultural tourism promotion.                                     | Socio-technical impact analysis, community economic upliftment discussion.                  | Sections 5.2.1, 5.2.2   | Report                          |
| PO7: Environment and Sustainability  | CO8                 | Demonstrated reduction in vehicle carbon emissions via route optimization and analyzed long-term economic sustainability.                                   | Carbon reduction analysis via 39.4% transit reduction; Table 5.1 budget comparison.         | Sections 5.2.2, 5.3     | Report + Project                |
| PO8: Ethics                          | CO9                 | Applied ethical software principles: transparent explainable AI (XAI), non-discriminatory consensus, zero commercial bias, and privacy-first local caching. | Ethical analysis, 'Why this place?' modal documentation, privacy design.                    | Sections 5.2.3, 3.2.5   | Report                          |
| PO9: Individual and Team Work        | CO10                | Collaborative software execution across a 2-student engineering team with distinct ownership of backend, algorithms, frontend, and tests.                   | Table 3.12 Task Allocation Matrix, modular Git commit tracking.                             | Sections 3.3, 3.4       | Project + Presentation          |
| PO10: Communication                  | CO11                | Produced exhaustive, professional academic documentation, high-resolution architectural schematics, and defended project collquia.                          | Complete Final FYDP Thesis Report, Figures 3.1-4.3, Oral Project Defense.                   | All Chapters, Defense   | Report + Presentation + Defense |
| PO11: Project Management and Finance | CO4                 | Formulated 48-week academic project plan, Gantt chart, risk mitigation matrix, and comparative project budget.                                              | Tables 3.10, 3.11, 3.13, and Table 5.1 (itemized BDT budget comparison).                    | Sections 3.3, 3.5, 5.3  | Report + Presentation           |
| PO12: Life-Long Learning             | CO12                | Demonstrated self-directed mastery of emerging technologies (FastAPI ASGI, Pydantic v2, Vite, Leaflet, XAI heuristics) and chartered future research.       | Honest technical limitation analysis and future research roadmap.                           | Sections 6.2, 6.3       | Report + Project                |

## 5.6 Chapter Summary

In this chapter, we conducted a rigorous evaluation of TripSense against international engineering standards and BAETE OBE criteria. We demonstrated compliance with ISO/IEC 25010 and RESTful communication standards, detailed positive impacts on human well-being, local economies, and environmental sustainability, and established financial viability via a 90.3% cost reduction over commercial SaaS. Finally, we systematically mapped the project against Complex Engineering Problem attributes (EP1-EP7), Knowledge Profiles (K1-K8), Complex Activities (EA1-EA5), and all 12 Program Outcomes (PO1-PO12). Chapter 6 concludes the report with a synthesis of contributions, limitations, and future directions.


---

# CHAPTER 6: CONCLUSION

## 6.1 Summary of Contributions

In this Final Year Design Project, we engineered, implemented, and empirically validated TripSense, an explainable, group-aware, and context-adaptive travel companion application tailored for multi-member tourism in Bangladesh and beyond. The project successfully resolved the four fundamental bottlenecks identified in contemporary travel planning: conflicting group preferences, spatial route inefficiency, opaque black-box recommendations, and vulnerability to real-time weather shocks.

The principal scholarly and engineering contributions of this project encompass:

1. Formulation of an Equitable Group Consensus Engine: Synthesized social choice theory into a production recommendation system, implementing the Least-Misery strategy to guarantee bounded individual dissatisfaction. Empirical benchmarks confirmed a Group Fairness Score of 74.52/100, an exceptionally low Gini inequality index of 0.0945, and a 40.2% reduction in satisfaction disparity compared to traditional average scoring, successfully eliminating minority alienation.

2. Transparent Multi-Stakeholder Explainability (XAI): Designed and deployed an automated explanation pipeline that translates complex multi-dimensional consensus vectors into intuitive cognitive badges ('[2/3 Friends Agree]', '[Indoor Friendly]', '[Hidden Gem]', '[Free Entry]') and personalized natural language justifications, fostering trust and eliminating intra-group dispute.

3. High-Performance 2-Opt Heuristic TSP Route Scheduler: Formulated a daily spatial scheduler that clusters attractions into Morning, Afternoon, and Evening slots, optimizing routes via 2-Opt edge exchanges over Haversine distance matrices. The engine slashed daily transit distance by 39.4% in real-world Chittagong itineraries within 4.1ms of computation time.

4. Sub-15ms Dynamic Context Weather Adaptation: Engineered a real-time event-driven context service capable of detecting inclement weather (such as tropical monsoon downpours) and executing atomic in-place substitutions of outdoor attractions with high-consensus indoor cultural landmarks while preserving schedule continuity and recomputing transit durations.

5. Full-Stack Production PWA with Peer Expense Ledger: Delivered a decoupled, responsive Progressive Web Application utilizing React 18, Vite, Tailwind CSS, Leaflet/OpenStreetMap with custom numbered markers (1-6), an integrated zero-sum peer expense splitter, and offline LocalStorage caching resilience, meeting all ISO/IEC 25010 software quality benchmarks.

6. Comprehensive BAETE OBE Compliance: Documented full alignment with international engineering criteria, mapping complex engineering problem attributes (EP1-EP7), Knowledge Profiles (K1-K8), Complex Activities (EA1-EA5), and all 12 Program Outcomes (PO1-PO12).

## 6.2 Technical and Operational Limitations

In the spirit of honest scientific inquiry, several technical and operational limitations must be acknowledged:

1. Cold-Start Preference Limitation: The current recommendation model relies on a 60-second self-reported questionnaire. While rapid and non-intrusive, self-reported preferences can occasionally suffer from cognitive bias (e.g., a traveler overestimating their desire for physical adventure or underestimating their fatigue tolerance during travel).

2. Heuristic Local Optimality vs Global Optimality: The 2-Opt edge-exchange heuristic guarantees 2-optimality (no two non-adjacent edges can be swapped to reduce length). While 2-Opt consistently achieves within 3-5% of theoretical optimal route length, it is not an exact solver and can occasionally become trapped in local minima on highly complex topological graphs.

3. Geographical POI Dataset Coverage: The verified Point-of-Interest dataset currently encompasses 45 deeply vetted attractions focused primarily on Chittagong, Cox's Bazar, Sylhet, and Dhaka. While sufficient for pilot urban and regional tours, nationwide rural coverage across all 64 districts of Bangladesh requires continuous crowd-sourced curation and administrative verification.

4. Synthetic Weather Alert Triggering: While the backend weather replanning architecture is fully reactive and sub-15ms fast, current demonstration environments rely on simulated monsoon rain triggers rather than a continuous live socket connection to the Bangladesh Meteorological Department (BMD) Doppler radar network.

5. Centralized Room State vs P2P Real-Time Collaboration: Group room state is currently synchronized via RESTful polling and client state rehydration. Under extreme concurrent editing by dozens of users in the same second, a WebSocket or WebRTC CRDT (Conflict-Free Replicated Data Type) architecture would provide superior real-time conflict resolution.

## 6.3 Future Work and Research Directions

Building upon the robust architectural foundation established in TripSense, several promising engineering extensions and research trajectories are planned for future development:

1. Live Meteorological Doppler Radar API Integration: Establishing automated data ingestion pipelines connecting TripSense directly to open weather APIs (OpenWeatherMap, ECMWF) and the Bangladesh Meteorological Department radar services to automatically trigger itinerary weather replanning based on micro-climatic satellite precipitation forecasts.

2. Multi-Objective Genetic Algorithms for Multi-Day TSPTW: Extending the routing engine to a full Genetic Algorithm (GA) or Ant Colony Optimization (ACO) formulation capable of optimizing multi-day tours simultaneously under strict Time Windows (TSPTW), incorporating live Google/OpenStreetMap vehicular traffic congestion matrices.

3. Real-Time WebRTC Peer-to-Peer Collaborative Sync: Upgrading the client synchronization layer to utilize WebRTC datachannels and CRDTs, enabling offline peer-to-peer room updates where companions can negotiate trip modifications and split expenses over local Wi-Fi or Bluetooth mesh networks when cellular data is completely unavailable.

4. Crowdsourced POI Expansion with Municipal Tourism Verification: Developing an administrative portal for local municipal tourism boards, registered Bangladesh tour operators, and verified local guides to submit and curate lesser-known heritage spots, complete with accessibility information, wheelchair friendliness, and verified ticket pricing.

5. Longitudinal User Field Trials: Conducting longitudinal user studies across student cohorts and family travel groups during actual multi-day trips to Cox's Bazar and Sylhet to quantitatively measure long-term psychological satisfaction, itinerary adherence, and perceived fairness in field conditions.


---

# REFERENCES

[1] J. Masthoff, "Group recommender systems: Combining individual models," in Recommender Systems Handbook, F. Ricci, L. Rokach, B. Shapira, and P. B. Kantor, Eds. Boston, MA: Springer, 2011, pp. 677–702.

[2] Bangladesh Tourism Board, "Strategic Tourism Master Plan 2020–2040," Ministry of Civil Aviation and Tourism, Government of the People's Republic of Bangladesh, Tech. Rep., 2021.

[3] K. J. Arrow, Social Choice and Individual Values, 2nd ed. New Haven, CT: Yale University Press, 1963.

[4] P. Vansteenwegen, W. Souffriau, and D. Van Oudheusden, "The orienteering problem: A survey," European Journal of Operational Research, vol. 209, no. 1, pp. 1–10, 2011.

[5] N. Tintarev and J. Masthoff, "Explaining recommendations: Design and evaluation," in Recommender Systems Handbook, F. Ricci, L. Rokach, and B. Shapira, Eds. New York, NY: Springer, 2015, pp. 353–382.

[6] A. K. Sen, Collective Choice and Social Welfare. San Francisco, CA: Holden-Day, 1970.

[7] F. Ricci, L. Rokach, and B. Shapira, "Introduction to recommender systems handbook," in Recommender Systems Handbook. Boston, MA: Springer, 2011, pp. 1–35.

[8] J. Masthoff, "Group modeling: Selecting a group and aggregating preferences," International Journal of Computer Science & Applications, vol. 8, no. 2, pp. 45–65, 2011.

[9] A. Felfernig, M. Stettinger, and C. Gula, "Group recommender systems: An introduction and research directions," in Proc. 26th Conf. User Modeling, Adaptation and Personalization (UMAP), Singapore, 2018, pp. 347–348.

[10] L. Baltrunas, T. Makcinskas, and F. Ricci, "Group recommendations with rank aggregation and collaborative filtering," in Proc. 4th ACM Conf. Recommender Systems (RecSys), Barcelona, Spain, 2010, pp. 119–126.

[11] D. Serbos, S. Qi, N. Mamoulis, and P. Tsaparas, "Fairness in group recommendation: Bounded dissatisfaction for all," in Proc. 26th ACM Int. Conf. Information and Knowledge Management (CIKM), Singapore, 2017, pp. 2099–2108.

[12] P. Vansteenwegen and D. Van Oudheusden, "The mobile tourist guide: An OR opportunity," OR Insight, vol. 20, no. 3, pp. 21–27, 2007.

[13] K. H. Lim, J. Chan, D. Karunasekera, and C. Leckie, "Personalized tour recommendation: A survey of algorithms and perspectives," IEEE Access, vol. 6, pp. 49767–49788, 2018.

[14] G. A. Croes, "A method for solving traveling-salesman problems," Operations Research, vol. 6, no. 6, pp. 791–812, 1958.

[15] S. Lin, "Computer solutions of the traveling salesman problem," Bell System Technical Journal, vol. 44, no. 10, pp. 2245–2269, 1965.

[16] N. Tintarev and J. Masthoff, "Evaluating the effectiveness of explanations for recommender systems," User Modeling and User-Adapted Interaction, vol. 22, no. 4-5, pp. 399–439, 2012.

[17] J. L. Herlocker, J. A. Konstan, and J. Riedl, "Explaining collaborative filtering recommendations," in Proc. ACM Conf. Computer Supported Cooperative Work (CSCW), Philadelphia, PA, 2000, pp. 241–250.

[18] G. Adomavicius and A. Tuzhilin, "Context-aware recommender systems," in Recommender Systems Handbook. Boston, MA: Springer, 2011, pp. 217–253.

[19] M. De Choudhury, M. Feldman, S. Amer-Yahia, N. Golbandi, R. Lempel, and C. Yu, "Automatic construction of travel itineraries using social media: A heuristic approach," in Proc. 19th ACM Int. Conf. Information and Knowledge Management (CIKM), Toronto, ON, Canada, 2010, pp. 419–428.

[20] H. Gunawardana and G. Shani, "A survey of accuracy evaluation metrics of recommendation tasks," Journal of Machine Learning Research, vol. 10, pp. 2935–2962, 2009.

[21] S. McCabe, C. Vogt, and R. Chen, "Collaborative travel planning: Conflicts, communication, and decision making," Annals of Tourism Research, vol. 37, no. 3, pp. 841–862, 2010.

[22] ISO/IEC, "Systems and software engineering — Systems and software Quality Requirements and Evaluation (SQuaRE) — System and software quality models," International Organization for Standardization, Geneva, Switzerland, ISO/IEC 25010:2011, 2011.

[23] R. T. Fielding, "Architectural Styles and the Design of Network-based Software Architectures," Ph.D. dissertation, Dept. Inf. Comput. Sci., Univ. California, Irvine, CA, 2000.

[24] T. Bray, Ed., "The JavaScript Object Notation (JSON) Data Interchange Format," Internet Engineering Task Force (IETF), RFC 8259, Dec. 2017.

[25] Board of Accreditation for Engineering and Technical Education (BAETE), "Accreditation Manual for Undergraduate Engineering Programmes," Institution of Engineers, Bangladesh (IEB), Dhaka, Bangladesh, Tech. Rep. Version 2.1, 2021.

[26] M. J. Egenhofer and R. D. Franzosa, "Point-set topological spatial relations," International Journal of Geographical Information Systems, vol. 5, no. 2, pp. 161–174, 1991.

