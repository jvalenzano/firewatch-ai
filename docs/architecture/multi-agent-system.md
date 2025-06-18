graph TD
    %% User Input Layer
    A[🔍 User Query Input] --> B{📝 Query Classification}
    
    %% Root Agent Decision Logic
    B -->|Fire Risk Analysis| C[🤖 Root Agent Initialization]
    B -->|Data Retrieval| D[📊 Direct Database Route]
    B -->|Weather Analysis| E[🌡️ Weather Specialist Route]
    B -->|Complex Analysis| F[🧠 Analytics Route]
    
    %% Root Agent Processing
    C --> G{🎯 Intent Analysis}
    G -->|Simple Data Query| H[📊 Transfer to Database Agent]
    G -->|Fire Calculations| I[🔥 Transfer to Fire Risk Agent]
    G -->|Multi-step Analysis| J[🧠 Transfer to Analytics Agent]
    G -->|Weather Focused| K[🌡️ Transfer to Weather Agent]
    
    %% Database Agent Workflow
    H --> L[📊 Database Agent]
    L --> M{🗄️ Data Source Selection}
    M -->|Fire Risk Data| N[🔥 BigQuery fire_risk_poc]
    M -->|Weather Stations| O[🌡️ BigQuery weather_data]
    M -->|Historical Fire| P[📈 BigQuery historical_fires]
    M -->|Station Metadata| Q[📍 BigQuery station_metadata]
    
    %% SQL Generation & Execution
    N --> R[⚙️ SQL Query Generation]
    O --> R
    P --> R
    Q --> R
    R --> S[🚀 BigQuery Execution]
    S --> T{✅ Query Success?}
    T -->|Success| U[📊 Format Response Data]
    T -->|Failure| V[⚠️ Error Handler]
    
    %% Fire Risk Agent Workflow
    I --> W[🔥 Fire Risk Agent]
    W --> X{🧮 Calculation Type}
    X -->|NFDRS Standard| Y[📏 Dead Fuel Moisture Calc]
    X -->|Burning Index| Z[🔥 Burning Index Calc]
    X -->|Spread Component| AA[📈 Spread Component Calc]
    X -->|Energy Release| BB[⚡ Energy Release Calc]
    
    %% NFDRS Calculation Pipeline
    Y --> CC[🌡️ Fetch Weather Data]
    Z --> CC
    AA --> CC
    BB --> CC
    CC --> DD[📊 Query Database Agent]
    DD --> L
    
    %% Analytics Agent Workflow
    J --> EE[🧠 Analytics Agent]
    EE --> FF{📊 Analysis Type}
    FF -->|Trend Analysis| GG[📈 Time Series Analysis]
    FF -->|Risk Prediction| HH[🎯 ML Model Execution]
    FF -->|Geographic Analysis| II[🗺️ Geospatial Processing]
    FF -->|Comparative Analysis| JJ[⚖️ Multi-Station Compare]
    
    %% External Data Integration
    GG --> KK[🌐 External API Calls]
    HH --> KK
    II --> KK
    JJ --> DD
    
    KK --> LL{🌍 External Source}
    LL -->|Weather.gov| MM[🌡️ NOAA Weather API]
    LL -->|Fire Detection| NN[🛰️ NASA FIRMS API]
    LL -->|Geographic| OO[🗺️ GACC Boundaries API]
    
    %% Weather Agent Workflow
    K --> PP[🌡️ Weather Agent]
    PP --> QQ{⛈️ Weather Analysis Type}
    QQ -->|Current Conditions| RR[🌤️ Real-time Data Fetch]
    QQ -->|Forecast Analysis| SS[🔮 Forecast Processing]
    QQ -->|Historical Patterns| TT[📊 Historical Weather Query]
    
    RR --> MM
    SS --> MM
    TT --> DD
    
    %% Response Consolidation
    U --> UU[📝 Response Formatter]
    V --> VV[❌ Error Response]
    
    %% Fire Calculations Results
    Y --> WW[🧮 NFDRS Results]
    Z --> WW
    AA --> WW
    BB --> WW
    WW --> UU
    
    %% Analytics Results
    GG --> XX[📊 Analytics Results]
    HH --> XX
    II --> XX
    JJ --> XX
    XX --> UU
    
    %% Weather Results  
    RR --> YY[🌡️ Weather Results]
    SS --> YY
    TT --> YY
    YY --> UU
    
    %% Final Response Assembly
    UU --> ZZ{🔄 Multi-Agent Coordination}
    ZZ -->|Single Agent Result| AAA[📤 Direct Response]
    ZZ -->|Multi-Agent Results| BBB[🔗 Response Aggregation]
    
    BBB --> CCC[📊 Cross-Agent Data Fusion]
    CCC --> DDD[🎯 Confidence Scoring]
    DDD --> EEE[📝 Natural Language Generation]
    
    %% Error Handling & Fallbacks
    V --> FFF{🔄 Retry Logic}
    FFF -->|Retry Available| L
    FFF -->|Max Retries| GGG[💬 Graceful Degradation]
    
    %% Session & Context Management
    A --> HHH[🗂️ Session Context]
    HHH --> III[💾 Conversation Memory]
    III --> JJJ[🔗 Context Propagation]
    JJJ --> C
    JJJ --> H
    JJJ --> I
    JJJ --> J
    JJJ --> K
    
    %% Final Output
    AAA --> KKK[🎯 Final User Response]
    EEE --> KKK
    GGG --> KKK
    VV --> KKK
    
    %% Monitoring & Logging
    KKK --> LLL[📊 Performance Metrics]
    LLL --> MMM[🔍 Monitoring Dashboard]
    
    %% Styling
    classDef rootAgent fill:#667eea,stroke:#4c63d2,color:#fff
    classDef dbAgent fill:#2ecc71,stroke:#27ae60,color:#fff
    classDef fireAgent fill:#e74c3c,stroke:#c0392b,color:#fff
    classDef analyticsAgent fill:#f39c12,stroke:#e67e22,color:#fff
    classDef weatherAgent fill:#3498db,stroke:#2980b9,color:#fff
    classDef dataSource fill:#95a5a6,stroke:#7f8c8d,color:#fff
    classDef externalAPI fill:#9b59b6,stroke:#8e44ad,color:#fff
    classDef decision fill:#f1c40f,stroke:#f39c12,color:#000
    classDef error fill:#e74c3c,stroke:#c0392b,color:#fff
    
    class C,G rootAgent
    class L,DD,N,O,P,Q dbAgent
    class W,Y,Z,AA,BB,CC,WW fireAgent
    class EE,GG,HH,II,JJ,XX analyticsAgent
    class PP,RR,SS,TT,YY weatherAgent
    class R,S,MM,NN,OO dataSource
    class KK,LL externalAPI
    class B,M,T,X,FF,QQ,ZZ,FFF decision
    class V,VV,GGG error