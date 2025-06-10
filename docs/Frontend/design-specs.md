# Design Document: RisenOne Fire Risk AI Proof of Concept Front-End Interface

## Document Overview

[cite\_start]**Date Created:** June 10, 2025 [cite: 1]

[cite\_start]**Purpose:** This document serves as the official handoff from the UX/UI design team to the front-end development team for the RisenOne Fire Risk AI Proof of Concept (POC). [cite: 1] [cite\_start]It outlines the design specifications, features, and capabilities for the front-end interface, based on high-fidelity mockups and user journey mappings for three scenarios: [cite: 2]

  * [cite\_start]Current Fire Danger Assessment [cite: 2]
  * [cite\_start]Multi-Day Predictive Analysis [cite: 2]
  * [cite\_start]Complex Multi-Region Analysis. [cite: 2]

[cite\_start]**Target Audience:** Front-end developers using the React/AG/UI stack with Tailwind CSS, Leaflet with React-Leaflet, Redux Toolkit, Axios with WebSocket, and Vite for build. [cite: 3]

[cite\_start]**Design Files:** High-fidelity mockups available in Figma (link to be provided), referenced assets (color codes, fonts), and diagrams to be inserted as placeholders. [cite: 4]

[cite\_start]**Timeline:** Development to commence Week 1 (June 10-13, 2025), with stakeholder demo on June 20, 2025. [cite: 5]

## Design Vision and Objectives

  * [cite\_start]Transform the manual workflow of Forest Service Scientists into an intuitive, conversational AI experience using Map and Chat Interfaces. [cite: 6]
  * [cite\_start]Demonstrate technical feasibility, immediate ROI, and a path to production deployment. [cite: 6]
  * [cite\_start]Ensure responsiveness across desktop (1440px) and mobile (375px) views within a single Cloud Run container. [cite: 7]
  * [cite\_start]Leverage real-time data from the Vertex AI Multi-Agent System (Root Coordinator, Weather Analysis Agent, Fire Risk Agent). [cite: 8]

## User Stories and Journey Maps

### Scenario 1: Current Fire Danger Assessment

[cite\_start]**User Story:** As a Forest Service Scientist, I want to quickly assess the current fire danger in Zone 7 to make immediate crew positioning decisions. [cite: 9]

[cite\_start]**Acceptance Criteria:** Query via Chat Interface ("What’s the current fire danger in Zone 7?") returns a 15-second response with a Burning Index (e.g., 85 - EXTREME) and heatmap overlay on Map Interface, plus crew recommendations. [cite: 10]

**Journey Map:**

  * [cite\_start]**Trigger (0-2 sec):** User inputs query, Chat shows loading spinner. [cite: 11]
  * [cite\_start]**Processing (2-15 sec):** Agents fetch data, Map updates progress. [cite: 12]
  * [cite\_start]**Response (15 sec):** Map shows heatmap, Chat displays "Burning Index: 85 (EXTREME)" and recommendations. [cite: 13]
  * [cite\_start]**Follow-Up (15+ sec):** User clicks zone for details. [cite: 14]

### Scenario 2: Multi-Day Predictive Analysis

[cite\_start]**User Story:** As a Forest Service Scientist, I want to predict fire risk over 5 days (e.g., no rain) to plan proactive measures. [cite: 15]

[cite\_start]**Acceptance Criteria:** Query ("How will fire risk change over 5 days if no rain falls?") returns a 25-second response with a temporal heatmap and daily risk levels (e.g., Day 1: HIGH to Day 5: EXTREME) plus pre-positioning advice. [cite: 16]

**Journey Map:**

  * [cite\_start]**Trigger (0-2 sec):** User inputs query with "What-if" slider. [cite: 17]
  * [cite\_start]**Processing (2-25 sec):** Agents process forecast, Map animates progress. [cite: 18]
  * [cite\_start]**Response (25 sec):** Map shows day-by-day heatmap, Chat lists forecast and advice. [cite: 19]
  * [cite\_start]**Follow-Up (25+ sec):** User adjusts slider for new scenarios. [cite: 20]

### Scenario 3: Complex Multi-Region Analysis

[cite\_start]**User Story:** As a Forest Service Scientist, I want to analyze fire risk across regions (e.g., Zone 7 and Southern California) to assess ignition risks. [cite: 21]

[cite\_start]**Acceptance Criteria:** Query ("With active fires in Southern California, what’s the risk in Zone 7?") returns a 30-second response with a multi-region heatmap and detailed assessment (e.g., "Ignition probability: 30%"). [cite: 22]

**Journey Map:**

  * [cite\_start]**Trigger (0-2 sec):** User inputs complex query. [cite: 23]
  * [cite\_start]**Processing (2-30 sec):** Agents correlate data, Map indicates multi-region analysis. [cite: 23]
  * [cite\_start]**Response (30 sec):** Map shows overlay, Chat provides analysis. [cite: 24]
  * [cite\_start]**Follow-Up (30+ sec):** User explores regions or requests strategies. [cite: 24]

## Interface Layout and Components

### Base Layout

  * [cite\_start]**Structure:** Split-screen design with 16:9 aspect ratio (1920x1080px), 50px padding, light https://www.google.com/search?q=gray background (\#F5F5F5). [cite: 25]

#### [cite\_start]Map Interface (Left, 60% width): [cite: 26]

  * [cite\_start]**Features:** High-resolution U.S. map with state boundaries, Zone 7 labeled, heatmap gradient (green \#32CD32 for LOW, yellow \#FFFF00 for HIGH, orange \#FFA500 for VERY HIGH, red \#FF4500 for EXTREME). [cite: 26]
  * [cite\_start]**Legend (50px x 100px, top-right, white text on blue \#1E90FF border).** [cite: 27]
  * [cite\_start]**Timestamp (top-left, 12px Roboto, white on blue \#1E90FF, e.g., "Updated: 12:05 AM PDT, June 10, 2025").** [cite: 28]
  * [cite\_start]**"What-if" slider (200px, blue \#1E90FF track, white thumb at 50% labeled "50% No Rain", endpoints "No Rain" and "Wind Increase" offset, 12px dark https://www.google.com/search?q=gray text) with toggle switch (40px x 20px, blue \#1E90FF, labeled "Adjust Conditions").** [cite: 29]
  * [cite\_start]**Interactions:** Clickable zones trigger tooltips (12px Roboto, white on blue \#1E90FF) with fade-in (e.g., "Dead Fuel Moisture: 10%, Wind: 15 mph"). [cite: 30] [cite\_start]Hover effects (5% scale-up). [cite: 31]

#### [cite\_start]Chat Interface (Right, 40% width): [cite: 31]

  * [cite\_start]**Features:** Green background (\#32CD32), input field (200px x 40px, placeholder "Ask about fire risk...", 14px Roboto) with send button (40px x 40px, white arrow on blue \#1E90FF). [cite: 32]
  * **Response area (300px, 16px Roboto with 8px spacing):** "Burning Index: 85 (EXTREME)" (red \#FF4500), "Current conditions indicate extreme fire danger.", "Position crews near high-risk areas." [cite\_start](https://www.google.com/search?q=gray). [cite: 33] [cite\_start]"What-if" button (100px x 40px, blue \#1E90FF, white text). [cite: 33]
  * [cite\_start]**Interactions:** Loading spinner (50px, blue \#1E90FF, 50% progress arc) on semi-transparent blue overlay (\#1E90FF, 70% opacity) during processing (15-30 seconds). [cite: 34]

#### [cite\_start]Responsive Behavior: [cite: 35]

  * [cite\_start]Stacks vertically on mobile (375px), 20px padding, proportional height adjustments. [cite: 35]

## Scenario-Specific Features

  * [cite\_start]**Scenario 1:** Static Zone 7 heatmap, 15-second response. [cite: 36]
  * [cite\_start]**Scenario 2:** Add timeline slider (200px, blue \#1E90FF, Day 1-5 notches) for animated heatmap, 25-second response. [cite: 37]
  * [cite\_start]**Scenario 3:** Add dropdown menu (100px, blue \#1E90FF) for regions (Zone 7, Southern California), multi-region overlay, 30-second response. [cite: 38]

## Styling and UX/UI Guidelines

  * [cite\_start]**Color Palette:** Blue (\#1E90FF) for interactive elements, green (\#32CD32) for chat background, red (\#FF4500) for extreme, orange (\#FFA500) for VERY HIGH, yellow (\#FFFF00) for HIGH, light https://www.google.com/search?q=gray (\#F5F5F5) for background. [cite: 39]
  * [cite\_start]**Typography:** Roboto, 16px body, 20px headers, 12px tooltips, 4.5:1 contrast ratio. [cite: 40]
  * [cite\_start]**Spacing:** 16px padding, 8px margins, subtle animations (fade-in tooltips, progress arc). [cite: 41]
  * [cite\_start]**Accessibility:** Alt text, keyboard navigation. [cite: 41]

## Diagrams and Visuals

  * [cite\_start][INSERT DIAGRAM HERE: Refined Base Layout Mockup] – High-fidelity mockup with Map and Chat Interfaces, slider, toggle, spinner, and tooltip. [cite: 42]
  * [cite\_start][INSERT DIAGRAM HERE: Scenario 2 Mockup] – Includes timeline slider and 5-day forecast response. [cite: 43]
  * [cite\_start][INSERT DIAGRAM HERE: Scenario 3 Mockup] – Features multi-region overlay and dropdown. [cite: 44]
  * [cite\_start][INSERT DIAGRAM HERE: Responsive Layout Sketch] – Shows stacked mobile view (375px). [cite: 45]
  * [cite\_start][INSERT DIAGRAM HERE: Color/Typography Style Guide] – Hex codes, font sizes, contrast examples. [cite: 46]

## Technical Notes

  * [cite\_start]**Tech Stack:** React with AG/UI, Tailwind CSS, Leaflet with React-Leaflet, Redux Toolkit, Axios with WebSocket, Vite. [cite: 47]
  * [cite\_start]**Browser Compatibility:** Chrome, Firefox, Safari (latest, June 2025). [cite: 48]
  * [cite\_start]**Performance:** Sub-30-second responses, Cloud Run optimization. [cite: 48]

## Acceptance Criteria

  * [cite\_start]Map and Chat Interfaces load and update within response times. [cite: 49]
  * [cite\_start]"What-if" slider and buttons trigger dynamic updates. [cite: 49]
  * [cite\_start]Responsive design passes testing at 1440px and 375px. [cite: 50]
  * [cite\_start]Accessibility standards met. [cite: 50]

## Next Steps

  * [cite\_start]Developers to review mockups in Figma and confirm asset integration by June 10, 2025, 5:00 PM PDT. [cite: 51]
  * [cite\_start]Kickoff meeting to align on build timeline. [cite: 52]
  * [cite\_start]Provide feedback on technical constraints. [cite: 52]

## Contact

  * **Product Owner:** [Your Name], [Your Email]
  * **UX/UI Designer:** [Designer Name], [Designer Email]
  * **Front-End Lead:** [Developer Name], [Developer Email]

## Notes for Implementation

  * [cite\_start]Insert the refined base mockup (from the latest designer prompt) and additional scenario mockups once delivered. [cite: 53]
  * [cite\_start]The document is ready for the developer to start Week 1 (June 10-13, 2025) work. [cite: 54]
  * [cite\_start]Update timestamps and visuals as needed based on designer output. [cite: 55]

[cite\_start]This synthesized document should serve as a robust handoff. [cite: 56]
[cite\_start]Let me know if you’d like to adjust any sections or add more placeholders\! [cite: 56]