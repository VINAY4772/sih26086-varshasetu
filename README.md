# VarshaSetu

## Hyperlocal Monsoon Onset, Break & Agricultural Advisory System

**SIH Problem Statement:** SIH26086  
**Domain:** Agriculture, FoodTech & Rural Development  
**Ministry:** Ministry of Earth Sciences (MoES)  
**Reference Organization:** National Centre for Medium Range Weather Forecasting (NCMRWF)

> **VarshaSetu — Bridging Climate Intelligence with Every Farmer**

---

## 1. About the Project

VarshaSetu is a hyperlocal monsoon prediction and agricultural advisory system developed for SIH26086.

The main idea of this project is to connect large-scale climate information with local-level agricultural decisions.

Farmers generally need information that is useful for their own area. A general weather forecast may not be enough to decide whether to sow a crop, wait for rainfall, arrange irrigation, or consider another crop.

VarshaSetu tries to provide this information at a block, village-cluster, or demonstration-locality level.

The system combines climate indicators, weather information, historical data and machine-learning based prediction to generate probabilistic information about monsoon onset, active spells, break spells and heavy rainfall.

The forecast is then converted into crop-specific agricultural advisories.

The system also provides a mobile-friendly web interface and a prototype SMS/WhatsApp communication workflow for farmers and agricultural extension officers.

---

# 2. SIH Problem Statement

## Problem Statement ID: SIH26086

### Hyperlocal Monsoon Onset & Break Prediction System (Block/Village Scale)

### Ministry
Ministry of Earth Sciences (MoES)

### Organization
National Centre for Medium Range Weather Forecasting (NCMRWF)

### Category
Software

### Theme
Agriculture, FoodTech & Rural Development

---

## 3. SIH Problem Description

Indian agriculture is highly dependent on the southwest monsoon. However, rainfall does not behave uniformly across large regions.

Farmers and agricultural extension officers need information at a much smaller geographical scale so that agricultural decisions can be taken according to the expected local rainfall conditions.

The proposed system is intended to provide a hybrid predictive framework for 7–30 day probabilistic outlooks of monsoon behaviour at Block/Panchayat/Village-cluster scale.

The system should connect global climate teleconnections such as ENSO, IOD and MJO with regional atmospheric information and use advanced mathematical or machine-learning techniques to estimate localized rainfall behaviour.

The system should help identify monsoon onset, onset-related thresholds, active spells, break spells, continuous dry periods and heavy rainfall risks.

The output should be presented through dynamic and understandable risk maps and should be converted into practical crop-specific agricultural advisories.

The advisories may include decisions such as delaying sowing, considering irrigation alternatives or changing crop choices when prolonged dry conditions or delayed monsoon conditions are expected.

The system can provide this information through a mobile-optimized web application or through an automated SMS/WhatsApp communication gateway in regional Indian languages.

The intended users include farmers and local agricultural extension officers.

### References

- Ministry of Earth Sciences (MoES)
- National Centre for Medium Range Weather Forecasting (NCMRWF)

---

# 4. Problem We Are Trying to Solve

Monsoon information is often available at a larger regional scale, while agricultural decisions are taken locally.

A farmer needs answers to practical questions such as:

- When is useful rainfall likely to begin?
- Is the monsoon likely to become active?
- Is there a possible dry spell after rainfall?
- Is a break period likely?
- Is heavy rainfall possible?
- Should sowing be delayed?
- Is irrigation likely to be required?
- Should a shorter-duration crop or another crop be considered?
- What should the farmer do if the expected rainfall does not occur?

VarshaSetu tries to connect the forecast information with these practical decisions.

---

# 5. Our Proposed Solution

VarshaSetu follows this general flow:

**Climate and Weather Information**

↓

**Feature Processing**

↓

**Machine Learning / Statistical Forecasting**

↓

**7–30 Day Probabilistic Outlook**

↓

**Onset / Active / Break / Heavy Rainfall Assessment**

↓

**Hyperlocal Risk Map**

↓

**Crop-Specific Advisory**

↓

**Farmer / Agricultural Extension Officer**

↓

**Mobile Web / SMS / WhatsApp Prototype**

The main purpose is not only to show a prediction, but to convert the prediction into information that can support agricultural decisions.

---

# 6. Main Objectives

The main objectives of VarshaSetu are:

1. Provide a 7–30 day probabilistic monsoon outlook.
2. Work at block/village-cluster level.
3. Use large-scale climate indicators such as ENSO, IOD and MJO.
4. Combine climate information with regional and historical weather information.
5. Use machine-learning/statistical methods for prediction.
6. Assess monsoon onset conditions.
7. Identify possible active and break spells.
8. Estimate heavy rainfall and dry-spell risks.
9. Display risks through an interactive map.
10. Convert forecast information into crop-specific advisories.
11. Provide sowing, irrigation, fertilizer and weather-risk recommendations.
12. Provide crop-choice alternatives when conditions require them.
13. Support farmers and agricultural extension officers.
14. Provide information through a mobile-friendly interface.
15. Support multiple Indian languages.
16. Demonstrate an SMS/WhatsApp advisory-dispatch workflow.

---

# 7. What VarshaSetu Provides

The main sections of the application include:

- Location selection
- Forecast summary
- 7/14/21/30 day outlooks
- Monsoon onset assessment
- Onset threshold status
- Active spell assessment
- Break spell assessment
- Heavy rainfall information
- Forecast charts
- Hyperlocal risk map
- Crop-specific advisories
- Crop-choice alternatives
- Farmer communication
- Agricultural extension officer communication
- SMS prototype
- WhatsApp prototype
- Notification delivery status
- Notification audit/history
- Data provenance
- Model validation
- Scientific methodology
- Multilingual interface
- Text-to-speech support where the device provides the required voice
- Mobile responsive interface

---

# 8. Forecasting Approach

VarshaSetu uses a machine-learning based forecasting framework.

The project currently uses a Random Forest based candidate model for the prediction component.

The forecasting system considers available climate, weather and derived features and produces probabilistic outputs instead of presenting a single deterministic statement.

The application supports forecast horizons of:

- 7 days
- 14 days
- 21 days
- 30 days

The system uses these outputs to assess different monsoon-related events.

These include:

- Onset probability
- Onset threshold assessment
- Active spell probability
- Active spell duration
- Break probability
- Break spell duration
- Heavy rainfall probability
- Dry-spell risk

---

# 9. Climate Information

VarshaSetu considers major climate teleconnections mentioned in the SIH problem description.

## ENSO

ENSO information is represented using the Niño 3.4 / ONI-related climate indicator.

The project includes a NOAA CPC based connection/handling for ENSO information, with benchmark/fallback handling where required by the prototype.

## IOD

The Indian Ocean Dipole is represented through the Dipole Mode Index related information/configuration used by the project.

IOD information is used as part of the broader climate context.

## MJO

The Madden-Julian Oscillation is represented through RMM phase/amplitude information.

MJO is considered as another large-scale climate signal in the forecasting framework.

---

# 10. Data Sources and Data Transparency

One important part of VarshaSetu is clearly separating different types of data.

The project does not treat every value as live real-time data.

The data used by the prototype can be grouped into the following categories.

### Real External Data / Telemetry

Where available, the project uses external data sources such as:

- NOAA CPC climate information
- NASA POWER weather/agro-climatology information

### Historical Observed Data

The project also uses historical observed agricultural/weather datasets available to the prototype.

### Benchmark / Fallback Data

When certain live upper-air or satellite feeds are not available locally, benchmark/climatological values may be used.

### Model-Derived Information

The following are generated by the forecasting framework:

- probabilities
- risk categories
- onset assessment
- active spell assessment
- break risk
- heavy rainfall probability
- advisory triggers

### Synthetic Demonstration Data

The project also contains synthetic/demo scenarios so that different conditions can be demonstrated during the prototype presentation.

Synthetic data is clearly identified instead of being presented as live observations.

---

# 11. NCMRWF / MoES Transparency

The SIH problem statement references the Ministry of Earth Sciences and NCMRWF.

VarshaSetu is designed around the problem context described by the SIH statement.

However, the current prototype should not be described as having a live operational NCMRWF feed unless such a connection is actually configured and verified.

For some upper-air variables such as 850 hPa zonal wind and satellite OLR, the current prototype can use climatological/benchmark fallback information when the required live operational feeds are unavailable locally.

This distinction is intentionally shown in the project so that real data, fallback data and demonstration data are not mixed together.

---

# 12. Monsoon Onset Assessment

VarshaSetu includes an onset threshold assessment based on IMD-referenced meteorological indicators adapted within the VarshaSetu hyperlocal forecasting framework.

The implemented assessment considers:

- Consecutive rainfall conditions
- 850 hPa zonal westerly wind
- OLR

The system can show:

- MET
- NOT MET
- INSUFFICIENT DATA

### Important scientific clarification

IMD's operational onset criteria are defined for declaration of southwest monsoon onset over Kerala and its advance.

VarshaSetu uses these meteorological indicators as reference features within its hyperlocal probabilistic assessment.

This dashboard does not represent an official IMD onset declaration.

---

# 13. Active and Break Spell Prediction

The system also provides information about possible active and break conditions.

For an active spell, the system can show:

- probability
- expected duration
- forecast window

For a break spell, the system can show:

- probability
- expected duration
- forecast window

The system also considers the possibility of prolonged dry spells.

If the required information is not sufficient, the application should indicate insufficient data rather than pretending that a reliable prediction is available.

---

# 14. Heavy Rainfall Risk

VarshaSetu provides a heavy rainfall risk component as part of the forecast.

The purpose is to help identify periods where excessive rainfall may affect agricultural activities.

This information can contribute to advisories related to:

- sowing
- fertilizer application
- irrigation
- crop protection
- field operations

The system does not present the risk as a guarantee of rainfall.

It is presented as a probabilistic outlook.

---

# 15. Hyperlocal Risk Map

VarshaSetu provides an interactive map for displaying localized risk information.

The map can display different risk categories and forecast information.

The map includes features such as:

- location selection
- risk categories
- probability information
- map legend
- demonstration polygons
- isochrones
- radar-related demonstration information
- interactive map controls

The purpose is to make the forecast easier to understand geographically.

### Boundary clarification

The project uses demonstration geometries for the prototype.

**Demonstration boundary — not an official administrative boundary. Polygons are approximate demonstration bounding-boxes; isochrones and radar points are illustrative simulations.**

---

# 16. Agricultural Advisory Engine

One of the main purposes of VarshaSetu is to convert weather and monsoon information into agricultural action.

The advisory engine uses forecast conditions and crop profiles to generate recommendations.

The project includes crop-specific advisory logic.

The advisory categories include:

- Sowing
- Irrigation
- Fertilizer
- Pest / Weather Risk
- Crop Choice / Variety

The basic decision flow is:

**Forecast**

↓

**Risk / Condition**

↓

**Crop Situation**

↓

**Agricultural Rule**

↓

**Localized Advisory**

---

# 17. Crop Advisories

The project contains advisory profiles for crops such as:

- Paddy
- Cotton
- Soybean
- Groundnut
- Maize
- Pulses

The actual advisory shown depends on the forecast and the crop profile.

Examples of advisory decisions include:

- delaying sowing when onset conditions are not suitable
- considering irrigation when a dry period is expected
- reducing or adjusting fertilizer application during unsuitable rainfall conditions
- taking precautions during heavy rainfall risk
- considering alternative crops or shorter-duration varieties when delayed onset or prolonged dry conditions are expected

The exact recommendation is generated by the implemented rules and should not be interpreted as a universal agricultural recommendation for every farm.

---

# 18. Crop Choice and Alternative Crops

VarshaSetu also considers crop-choice changes as part of the advisory system.

For example, under conditions such as delayed onset or prolonged dry conditions, the system can present alternative crop or variety options.

Examples implemented in the prototype may include:

- Paddy → short-duration Pulses / Greengram / Maize
- Cotton → Pigeonpea / Castor
- Soybean → Sunflower / Sesame

The exact recommendation depends on the rules and conditions implemented in the application.

These are prototype advisory examples and should be considered along with local agricultural expert guidance.

---

# 19. Farmers and Agricultural Extension Officers

VarshaSetu supports two intended communication recipients.

## Farmer

A farmer-oriented advisory focuses on practical actions such as:

- sowing
- irrigation
- crop protection
- fertilizer timing
- crop-choice decisions

## Agricultural Extension Officer

An extension-officer advisory can provide:

- block/mandal-level risk information
- agricultural directives
- localized risk conditions
- advisory information that can be communicated to farmers

---

# 20. Mobile-Optimized Web Application

The SIH description specifically includes a mobile-optimized web application as one of the communication approaches.

VarshaSetu is designed to work on phone-sized screens.

The application was tested across different viewport sizes including:

- 320 × 800
- 360 × 800
- 375 × 812
- 390 × 844
- 412 × 915
- 1440 × 900

The mobile interface was checked for:

- no unwanted horizontal scrolling
- readable content
- responsive cards
- responsive charts
- map usability
- language selector
- advisory sections
- messaging controls
- notification history
- footer
- touch-friendly controls

The goal is that the important parts of the application remain usable from a phone instead of being designed only for a desktop screen.

---

# 21. Multilingual Support

VarshaSetu supports seven languages:

1. English
2. Telugu
3. Hindi
4. Tamil
5. Kannada
6. Urdu
7. Malayalam

The language system is centralized through locale files and an internationalization layer.

The selected language is stored so that it can persist across the application.

Dynamic content such as advisories, charts, notifications and interface text is localized where supported.

Urdu uses right-to-left layout handling.

---

# 22. Text-to-Speech

The project also includes browser-based text-to-speech support.

The system checks the available voices on the device/browser and attempts to use the selected language.

The project does not intentionally replace an unavailable regional-language voice with an unrelated English voice.

If the required voice is not available on the device, the application can show that voice functionality is unavailable.

This means TTS availability can depend on the browser and installed device voices.

---

# 23. SMS and WhatsApp Prototype

VarshaSetu includes an SMS/WhatsApp gateway demonstration.

The current implementation is a prototype/sandbox and does not perform real telecom delivery.

The workflow is:

**Select recipient**

↓

**Select channel**

↓

**Generate localized advisory**

↓

**Dispatch through prototype gateway**

↓

**Simulated delivery**

↓

**Store audit record**

The application can demonstrate:

- Farmer SMS
- Farmer WhatsApp
- Extension Officer SMS
- Extension Officer WhatsApp
- delivery status
- notification history

### Important

**WORKING PROTOTYPE — NO REAL TELECOM DELIVERY**

The simulated dispatches are recorded in the local SQLite audit system.

Real telecom delivery would require integration with an authorized SMS provider and/or WhatsApp Business/Cloud API or another authorized messaging provider.

---

# 24. Notification Audit

The notification workflow maintains an audit history.

The audit can record information related to:

- recipient type
- channel
- language
- message/advisory
- dispatch status
- timestamp
- simulated delivery status

This helps demonstrate how an actual communication system could maintain traceability.

---

# 25. Data Provenance

VarshaSetu contains a Data Provenance section to explain where information comes from.

The project distinguishes between:

- real external telemetry
- historical observed data
- benchmark/fallback data
- model-derived probabilities
- synthetic demonstration datasets

This is important because a prototype should not present simulated data as if it were live operational data.

---

# 26. Model Validation

The project includes model validation and evaluation components.

The model is evaluated against appropriate metrics and a climatological baseline where applicable.

The current project reports a Brier Skill Score of approximately +0.158 for the candidate forecasting model compared with the climatological baseline.

Other evaluation metrics available in the project should be taken directly from the evaluation output rather than manually estimated.

The purpose of validation is to measure how useful the probabilistic model is compared with a baseline.

---

# 27. Scientific Methodology

The general methodology used by VarshaSetu is:

1. Collect climate and weather information.
2. Process the available data.
3. Prepare model features.
4. Include climate teleconnection information.
5. Generate probabilistic predictions.
6. Assess monsoon events.
7. Convert results into risk information.
8. Generate crop-specific advisories.
9. Present information through the web application.
10. Demonstrate communication through the prototype gateway.
11. Maintain an audit trail.

---

# 28. System Architecture

The high-level architecture is:

```text
                CLIMATE INFORMATION
        ┌─────────────────────────────┐
        │ ENSO / IOD / MJO            │
        │ Weather / Historical Data   │
        │ External Data Sources       │
        └──────────────┬──────────────┘
                       │
                       ▼
              DATA PROCESSING
                       │
                       ▼
             FEATURE ENGINEERING
                       │
                       ▼
          ML / STATISTICAL FORECASTING
                       │
                       ▼
            PROBABILISTIC OUTLOOK
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
      ONSET         ACTIVE/BREAK     HEAVY RAIN
        │              │              │
        └──────────────┼──────────────┘
                       ▼
                  RISK MAP
                       │
                       ▼
              CROP ADVISORY ENGINE
                       │
          ┌────────────┴────────────┐
          ▼                         ▼
       FARMERS              EXTENSION OFFICERS
          │                         │
          └────────────┬────────────┘
                       ▼
              MOBILE WEB APPLICATION
                       │
                       ▼
             SMS / WHATSAPP PROTOTYPE
                       │
                       ▼
                 AUDIT HISTORY


---

29. Technology Stack

The project uses technologies appropriate to its current implementation.

The main technologies include:

Layer	Technology	Purpose

Frontend	HTML	Web structure
Frontend	CSS	Responsive UI
Frontend	JavaScript	Application interaction
Backend	Python	Application and forecasting logic
Backend	Flask	API/server layer
ML	Random Forest	Probabilistic forecasting
Database	SQLite	Audit/persistence
Maps	Leaflet	Interactive map
Charts	Chart.js	Forecast visualization
Localization	JSON + i18n JavaScript	Multilingual interface
TTS	Web Speech API	Browser-based speech
API	REST-style endpoints	Frontend/backend communication


The final technology list should be compared with the actual project dependencies before making claims about any additional technology.


---

30. Important API Areas

The backend provides APIs for the main application functions.

Important API areas include:

Health

Forecast

Locations

Risk Map

Advisories

Notification simulation

Notification history


The exact API paths, request formats and response structures are documented in the project's backend source files.


---

31. Database

The project uses SQLite for local persistence/audit purposes.

The notification audit system is particularly useful for the SMS/WhatsApp prototype.

The database stores information required to demonstrate notification dispatch and history.

The database is intended for prototype-level traceability and is not presented as a production-scale telecom infrastructure.


---

32. Error Handling

The application includes error handling for important operations.

Examples include:

forecast API failure

advisory API failure

location loading failure

notification dispatch failure

retry actions

unavailable voice handling


The application should not show a fake successful forecast or fake successful notification when the underlying operation has failed.


---

33. Testing

The project contains automated tests for important components.

The test suite covers areas such as:

API

forecasting

event definitions

advisories

database

model evaluation

data ingestion

locale validation

provenance/transparency

SIH-specific requirement gaps


The current verified project state reported:

60/60 automated tests passed.

Frontend JavaScript syntax checks were also performed.

The multilingual lifecycle was tested for selected languages including:

English

Telugu

Urdu

Malayalam


The mobile/language audit reported:

42/42 combinations passed

with no unwanted horizontal overflow detected across the tested viewport/language combinations.

These values should be rechecked against the latest test run before a final submission if the code changes afterward.


---

34. End-to-End Workflow

The complete application workflow is:

LOCATION
   ↓
FORECAST
   ↓
PROBABILITY
   ↓
RISK
   ↓
CROP
   ↓
ADVISORY
   ↓
FARMER / EXTENSION OFFICER
   ↓
LANGUAGE
   ↓
SMS / WHATSAPP PROTOTYPE
   ↓
SIMULATED DELIVERY
   ↓
AUDIT HISTORY

This demonstrates how the system connects climate information to an agricultural action.


---

35. Real Data vs Prototype Data

Component	Current Type

NOAA CPC information	External data/connector where available
NASA POWER	External data
Historical observed datasets	Historical real data
ENSO	Climate indicator
IOD	Climate indicator/configuration
MJO	Climate indicator/representation
Random Forest	Implemented ML model
Forecast probabilities	Model-derived
Risk categories	Model/application-derived
850 hPa wind	Benchmark/climatological fallback when live feed unavailable
OLR	Benchmark/climatological fallback when live feed unavailable
Demonstration scenarios	Synthetic/demo data
Map polygons	Demonstration geometry
Radar points	Illustrative simulation where applicable
SMS	Simulated prototype
WhatsApp	Simulated prototype
Notification audit	Local SQLite prototype


The purpose of this separation is to keep the demonstration scientifically transparent.


---

36. Current Limitations

VarshaSetu is a working prototype and has limitations.

1. NCMRWF operational data

The current project should not be treated as a live operational NCMRWF forecasting system unless an actual NCMRWF operational data connection is established and verified.

2. Upper-air and satellite information

Some variables can use climatological/benchmark fallback values when live feeds are unavailable locally.

3. Demonstration boundaries

The map polygons are demonstration geometries and are not official administrative boundaries.

4. SMS/WhatsApp

The current messaging system is a simulated prototype and does not transmit messages through a real telecom carrier.

5. Synthetic scenarios

Synthetic scenarios are used to demonstrate different system conditions.

6. Prototype scope

The project is intended as a demonstration of the proposed system architecture and workflow. A production deployment would require additional operational data infrastructure, provider integrations, monitoring, security, validation and field testing.


---

37. Why This System Can Be Useful

The main value of VarshaSetu is the connection between prediction and action.

Instead of stopping at:

“Rainfall probability is high.”

the system tries to move toward:

“Based on the expected rainfall conditions and the selected crop, this is the agricultural action that can be considered.”

This creates a chain from:

Climate Intelligence → Local Risk → Agricultural Decision


---

38. SIH26086 Requirement Mapping

SIH Requirement	VarshaSetu Implementation

7–30 day outlook	7/14/21/30 day forecast horizons
Block/Village scale	Demonstration localities and hyperlocal map
ENSO	ENSO/ONI climate information
IOD	IOD/DMI representation
MJO	MJO RMM representation
Regional atmospheric information	Weather and derived atmospheric information
ML/statistical framework	Random Forest forecasting framework
Localized rainfall information	Probabilistic local outputs
Monsoon onset	Onset assessment
Onset threshold	Threshold status
Active spells	Active probability/duration
Break spells	Break probability/duration
Dry spells	Dry-spell assessment
Heavy rainfall	Heavy rainfall risk
1–4 week risk	Forecast horizons
Dynamic risk map	Leaflet-based map
Crop advisories	Crop-specific advisory engine
Delay sowing	Sowing advisory
Irrigation alternatives	Irrigation advisory
Crop-choice alteration	Alternative crop/variety advisory
Farmers	Farmer recipient workflow
Extension officers	Officer workflow
Regional languages	Seven-language interface
Mobile application	Responsive mobile web application
SMS/WhatsApp	Prototype communication gateway
Actionable information	Crop-specific recommendations



---

39. Demonstration Flow

A simple demonstration can be done in this order:

1. Open VarshaSetu.


2. Select the demonstration location.


3. Show the forecast summary.


4. Explain the 7–30 day outlook.


5. Show the onset assessment.


6. Explain the onset threshold status.


7. Show active spell information.


8. Show break spell information.


9. Show heavy rainfall risk.


10. Open the risk map.


11. Select a crop.


12. Show the crop-specific advisory.


13. Show crop-choice alternatives.


14. Change the language.


15. Demonstrate the localized advisory.


16. Select Farmer or Agricultural Extension Officer.


17. Select SMS or WhatsApp.


18. Send the simulated message.


19. Show the simulated delivery status.


20. Show notification history.


21. Explain data provenance.


22. Explain model validation.


23. Explain the scientific limitations.




---

40. PPT Preparation

The project can be presented through the following slide structure:

Slide 1 — Title

VarshaSetu

Hyperlocal Monsoon Onset, Break & Agricultural Advisory System

SIH26086

Slide 2 — Problem

Explain the gap between regional monsoon information and local agricultural decisions.

Slide 3 — Need

Explain why farmers need local rainfall/onset/break information.

Slide 4 — Proposed Solution

Introduce VarshaSetu.

Slide 5 — Objectives

Show the major objectives.

Slide 6 — System Architecture

Show the complete data-to-advisory flow.

Slide 7 — Data and Climate Signals

Explain ENSO, IOD, MJO and weather information.

Slide 8 — AI/ML

Explain the Random Forest based probabilistic forecasting framework.

Slide 9 — Forecast Outputs

Show onset, active, break and heavy-rain information.

Slide 10 — Risk Map

Show the hyperlocal map and risk visualization.

Slide 11 — Agricultural Advisory

Show how forecast information becomes crop-specific action.

Slide 12 — Farmer and Extension Officer

Explain both communication workflows.

Slide 13 — Mobile and Multilingual

Show the phone interface and supported languages.

Slide 14 — SMS/WhatsApp Prototype

Explain the simulated gateway honestly.

Slide 15 — Validation

Show actual model evaluation and testing results.

Slide 16 — Data Transparency

Explain real data, fallback data and synthetic demonstration data.

Slide 17 — SIH Requirement Mapping

Show how VarshaSetu addresses the problem statement.

Slide 18 — Limitations

Clearly explain prototype limitations.

Slide 19 — Future Scope

Possible future work can include:

operational NCMRWF data integration

real authorized SMS/WhatsApp provider integration

official administrative boundaries

more locations

more historical observations

field validation

improved model training

production deployment


Slide 20 — Conclusion

Summarize:

Climate Intelligence → Hyperlocal Risk → Agricultural Advisory → Farmer Action


---

41. Future Scope

If VarshaSetu is developed beyond the prototype stage, possible future improvements include:

1. Direct operational NCMRWF data integration.


2. More real-time atmospheric observations.


3. More official administrative boundaries.


4. More historical datasets.


5. Larger geographical coverage.


6. Field validation with agricultural experts and farmers.


7. Production-grade model monitoring.


8. Authorized SMS provider integration.


9. Authorized WhatsApp Business integration.


10. Additional Indian languages.


11. Improved regional-language TTS coverage.


12. Integration with additional agricultural data sources.



These are future possibilities and are not presented as already completed features.


---

42. Conclusion

VarshaSetu is designed to connect climate information with local agricultural decisions.

The system combines climate indicators, weather information, machine learning, probabilistic forecasting, risk visualization and crop-specific advisory rules.

The main idea is simple:

Predict the possible monsoon condition → understand the local risk → convert it into an agricultural advisory → communicate it clearly to the intended user.

The project is developed as a working prototype for SIH26086 and maintains transparency about real data, fallback data, synthetic demonstration data and simulated communication.


---

43. Project Structure

The exact structure can change during development, but the project contains major areas for:

VarshaSetu/
│
├── backend/
│   └── API and server logic
│
├── forecasting/
│   └── Forecasting and monsoon event logic
│
├── advisories/
│   └── Crop profiles and advisory rules
│
├── database/
│   └── Database schema and persistence
│
├── frontend/
│   ├── index.html
│   ├── css/
│   ├── js/
│   └── locales/
│
├── models/
│   └── Machine-learning model files
│
├── data/
│   └── Data and demonstration datasets
│
└── tests/
    └── Automated tests

The actual repository should be considered the source of truth for the exact current file structure.


---

44. Important Project Statement

VarshaSetu is a prototype created to demonstrate a practical approach to the SIH26086 problem.

The system is designed to be transparent about what is currently implemented, what uses fallback or demonstration data, and what would require further operational integration.

The project does not claim to be an official MoES, NCMRWF or IMD operational system.

It is a student-developed prototype based on the problem described in SIH26086.


---

45. Project Status

Current status: Working Prototype

Major implemented areas include:

Hyperlocal forecast interface

7–30 day forecast horizons

ENSO/IOD/MJO context

ML-based forecasting

Onset assessment

Active/break assessment

Heavy rainfall risk

Interactive risk map

Crop advisories

Crop-choice alternatives

Farmer workflow

Extension officer workflow

Seven-language interface

Urdu RTL support

Mobile responsive interface

SMS/WhatsApp simulated gateway

Notification audit

Data provenance

Model validation

Scientific methodology

Automated testing

---

48. Final Note

For the latest and most accurate implementation details, the source code, tests and configuration files in this repository should be treated as the final source of truth.

This README explains the purpose, architecture, functionality and current status of VarshaSetu for people who want to understand the project without first reading the complete source code.