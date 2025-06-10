# Scenario Mapping

Walk through of how the different scenarios in the RisenOne Fire Risk AI Proof of Concept (POC) mapped with the components shown in the container diagram. This will help demystify the complex web of arrows and interactions by tying them to the specific demonstration flows.

### Scenario 1: "Current Fire Danger Assessment"

**User (Stakeholder):** "Show me the current fire danger assessment capabilities."

**System Response (via Chat Interface):** "Let’s assess the current fire danger in Zone 7. Give me a moment to process..."

The journey starts with the Chat Interface in the Streamlit Frontend layer, where the user’s query is entered. This query is passed to the Root Coordinator within the Vertex AI Multi-Agent System. The Root Coordinator acts like a traffic director, deciding which agents to call upon. It first engages the Weather Analysis Agent, which reaches out to the Weather.gov API (an external API) to fetch real-time weather data, such as temperature and humidity for the Missoula, MT area. This data flows back through the Root Coordinator.

Next, the Fire Risk Agent steps in, pulling the weather data and using the Fire Calculation Engine to compute the Dead Fuel Moisture (FM = f(RH, T, rain)). The engine then calculates the Spread Component (SC = 0.560 × ROS), incorporating wind conditions from the weather data, and the Energy Release Component (ERC = 2 × (1 - FM)), assessing cumulative dryness. Finally, it determines the Burning Index (BI = 10 × SC × ERC), resulting in a value of 85, indicating an EXTREME danger level.

The Map Simulation Interface then takes this data, integrates it with Geographic Data (zone boundaries from the external APIs), and generates an interactive heatmap overlay showing risk distribution. The results—numerical values, heatmap, and a natural language explanation with crew positioning recommendations—flow back through the Chat Interface to the user, all within 15 seconds. This replaces a 3-4 hour manual process, showcasing immediate value.

### Scenario 2: "Multi-Day Predictive Analysis"

**User (Stakeholder):** "Can this system predict future conditions?"

**System Response (via Chat Interface):** "Sure, let’s predict the fire risk in Zone 7 over the next 5 days with no rain. Processing now..."

Again, the query begins at the Chat Interface, routed to the Root Coordinator. This time, the Coordinator tasks the Weather Analysis Agent to retrieve a 5-day forecast from the Weather.gov API. The agent processes this data, and the Fire Risk Agent uses the Fire Calculation Engine to project fuel moisture evolution using drying models. The engine iterates through the Spread Component, Energy Release Component, and Burning Index calculations day by day.

The Map Simulation Interface then visualizes this temporal progression, showing risk levels: Day 1 (HIGH), Day 3 (VERY HIGH), and Day 5 (EXTREME), using Geographic Data for context. The Visualization Components in the frontend layer create a day-by-day breakdown, while the Chat Interface delivers a recommendation for proactive crew pre-positioning by Day 3. This 25-second response highlights predictive capabilities beyond manual methods.

### Scenario 3: "Complex Multi-Region Analysis"

**User (Stakeholder):** "With active fires in Southern California and current conditions in Northern Rockies, what’s the risk of new ignitions affecting Zone 7?"

**System Response (via Chat Interface):** "Let’s analyze the multi-region fire risk. This might take a moment..."

The query enters via the Chat Interface and is directed to the Root Coordinator. The Coordinator engages the Weather Analysis Agent to pull current conditions from the Weather.gov API for the Northern Rockies, and the Gemini 2.5 Pro Integration Agent to process synthetic active fire data from Southern California, simulating realistic fire patterns. The Fire Risk Agent then uses the Fire Calculation Engine to assess ignition risks, factoring in Dead Fuel Moisture, Spread Component, Energy Release Component, and Burning Index across regions.

The Map Simulation Interface integrates this with Geographic Data (zone boundaries) to map the risk, while the Visualization Components create a comprehensive overlay. The In-Memory Data Layer (holding real weather data and geographic data) supports rapid cross-referencing. The Chat Interface finally presents the 30-second response, offering a detailed risk assessment and strategic insights, demonstrating sophisticated analysis capabilities.

### Bringing It Together

The diagram’s arrows reflect this dynamic flow: the Cloud Run Container houses the Streamlit Frontend (Map and Chat Interfaces) and the Vertex AI Multi-Agent System (Root Coordinator, Weather Agent, Fire Risk Agent), all orchestrated to interact with External APIs and the In-Memory Data Layer. The Fire Calculation Engine drives the core computations, feeding results back through the frontend for user interaction. Each scenario leverages this structure differently, proving the system’s versatility and feasibility.

  * Real-time data for Scenario 1
  * Forecasts for Scenario 2
  * Synthetic multi-region data for Scenario 3