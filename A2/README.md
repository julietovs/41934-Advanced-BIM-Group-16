# A2 USE CASE - Ventilation Airflow Validation Tool
This repositpry documents the development of a BIM use case and proposed IfcOpenShell-based tool for validating ventilation airflow requirements in office and meeting rooms in Building #2601


## A2a: About the group

**Group number:** 16  
**Total Python coding confidence score:** 3  
**Focus area:** Indoor Climate  
**Role:** Analyst  

## A2b: Identify claim

Selected building: #2601

### Claim to check

In A1, we investigated the report’s claim that 24 of 29 evaluated rooms achieved 100% Category II thermal comfort compliance during occupied hours, while the remaining five achieved at least 99.7%. However, temperature-related properties in the IFC model were missing or contained zero values, preventing verification using the available model data.

We will therefore investigate a related ventilation claim. The report states that ventilation for offices and meeting rooms is designed using a Category II requirement of 7 L/s per person plus 0.7 L/s per m² of floor area.

We will check whether the design supply airflow assigned to each office and meeting room meets this stated requirement, using the room area and design occupancy.

Source: Part D – MEP report, Section 5.1, Table 5, p. 6.

### Justification

We selected this check because sufficient ventilation is important for indoor air quality. It builds on the data limitations identified in A1 and provides a measurable design requirement to investigate. The tool will compare design supply airflow with the required airflow based on floor area and design occupancy, while identifying missing information that prevents verification. This ventilation check does not independently verify the original thermal comfort claim.

## A2c: Use Case

#### How will the claim be checked?

Building on A1, the analyst will review whether sufficient thermal comfort results and occupied-hour information are available. If these data are insufficient, the original claim will be recorded as unverified, and a separate ventilation airflow check will be performed.

The tool will identify offices and meeting rooms through IfcSpace entities and retrieve floor area, design occupancy and design supply airflow. Supplementary project data will be used where required.

The required airflow will be calculated as:

q_required = 7 × N + 0.7 × A [L/s]

where N is the design number of occupants and A is the floor area in m².

After checking room mappings, completeness and units, the tool will compare design supply airflow with the requirement. Results will be classified as meeting the requirement, below the requirement, or having insufficient data. This check does not independently verify thermal comfort.

#### When and in which phase?

The check will be performed during the design phase, before the ventilation design is finalised, and repeated when room areas, occupancy or airflow rates change.

#### Information required
- Room identification and function.
- Floor area and design occupancy.
- Design supply airflow per room.
- The report’s stated ventilation criterion.
- Room mappings for supplementary data.

The initial thermal comfort review also requires relevant results, occupied-hour information and documented comfort criteria.

#### BIM purpose and related use case

The primary purpose is **Analyse – Validate**, as the tool evaluates whether ventilation airflow requirements are satisfied. Supporting purposes are:
- **Gather:** Extract room and ventilation data from the IFC model
- Calculate required airflow and compare against design airflow
- **Communicate:** produce a report highlighting compliant and non-compliant rooms.

The use case is adapted from Code Validation to check room-level ventilation airflow against the criterion stated in the report.


#### Process and information exchange

The analyst provides the IFC model and defines the check. The ventilation designer supplies missing occupancy or airflow data. The Python tool reads room data, links supplementary inputs, calculates required airflow and exports a results report. The analyst reviews the findings and communicates discrepancies or missing information to the ventilation designer.

## A2d: Scope the use case

The proposed Python/IfcOpenShell tool will automate the following tasks:
1. Read room data from IFC
2. Identify offices and meeting rooms
3. Extract floor area
4. Link supplementary occupancy data
5. Link supplementary airflow data
6. Calculate required airflow
7. Compare design and required airflow
8. Export a compliance report. Rooms with insufficient data will be flagged in the report.

These tasks are highlighted in blue in the scoped BPMN diagram: 
- Selecting the claim
- Providing supplementary data
- Reviewing the findings remain outside the tool’s scope

## A2e: Tool Idea

#### Proposed tool

We propose a Python tool using IfcOpenShell to check design supply airflow in offices and meeting rooms against the ventilation criterion stated in the report.

The tool will read IfcSpace identifiers and available room properties and quantities. Supplementary occupancy and airflow data will be linked to the corresponding rooms where required. After checking data completeness and units, it will calculate the required airflow using q_required = 7 × N + 0.7 × A [L/s] and compare it with the design supply airflow.

The output will be a CSV report containing room identifiers, input values, required airflow, design supply airflow and the result of the check. Rooms with missing or invalid inputs will be marked as having insufficient data. The IFC model will remain unchanged.

#### Business and societal value

The tool can reduce repetitive manual calculations and help designers identify airflow shortfalls and missing information before the ventilation design is finalised. Linking each result to an IFC room makes the check traceable and easier to repeat after design changes.

By supporting appropriate ventilation sizing, the tool can contribute to better indoor air quality and occupants’ well-being. It checks a design requirement rather than demonstrating actual indoor climate performance.

See files for BPMN (ventilation_tool)

FIX MARKDOWN!!!!

#### IFC Classes Used
The tool primarily checks: 
- IfcSpace
- IfcPropertySet
- IfcElementQuantity
- Qto_SpaceBaseQuantities
Additional supplementary data may be linked using room identifiers

#### Tool BPMN diagram

<img width="1710" height="583" alt="image" src="https://github.com/user-attachments/assets/0b4a99d2-e4c9-4863-abde-6a5aeb7fe75c" />

The BPMN diagram above shows the final manual for the use case. The files can be found
- /A2/Ventilation_tool.bpmn
- /A2/Ventilation_tool.svg

## A2f: Information Requirements

The following information is required for the ventilation check. The IFC locations are possible sources; their availability in the selected model must be confirmed.

| Information required | Possible location or source | Available? | Planned extraction |
|---|---|---|---|
| Room identification | IfcSpace.GlobalId, Name and LongName | IfcSpace identified in A1; room identifiers to be checked. | model.by_type("IfcSpace") and direct attribute access. |
| Room function | Room names, classifications or properties associated with IfcSpace | To be checked. | Inspect attributes and property sets to identify offices and meeting rooms. |
| Floor area [m²] | Qto_SpaceBaseQuantities.NetFloorArea or an equivalent documented quantity | To be checked. | get_psets(space, qtos_only=True). |
| Design occupancy | Pset_SpaceOccupancyRequirements.OccupancyNumber, project properties or supplementary CSV data | To be checked. | get_psets(space), or link CSV data using room identifiers. |
| Design supply airflow [L/s] | Documented room properties or supplementary ventilation schedules | To be checked. | Inspect properties or import room-level CSV data. |
| Units | IFC unit definitions, property-specific units and external file documentation | To be checked. | Identify and convert units to m² and L/s. |
| Ventilation criterion | MEP report, Section 5.1, Table 5, p. 6 | Available in the report. | Apply q_required = 7 × N + 0.7 × A [L/s]. |

#### Learning needs

We need to learn how to extract property and quantity sets, identify the relevant design values, link supplementary data to IFC rooms, handle missing or invalid inputs, and convert units.

These learning needs will be added to the course Learning Bank. Rooms with insufficient information will be reported as unverifiable rather than assigned undocumented assumptions.


## A2g: Software Licence

We propose releasing the developed Python tool under the MIT License. 

The MIT License is a permissive open-source software licence that allows others to use, modify, distribute and reuse the code with minimal restrictions, provided that the original copyright notice and licence text are included ([Source](https://tlo.mit.edu/understand-ip/exploring-mit-open-source-license-comprehensive-guide)). MIT is an appropriate tool because: 
- It encourages collaboration and sharing of OpenBIM tools
- It allows other students and users to adapt and improve the tool
- It is compatible with the open-source work method
- It is simple and has many users

The tool will be developed using open-source software including Blender and IfcOpenShell, while the source code for the ventilation checking tool itself will be released under the MIT License. See the license in [MIT License](41934-Advanced-BIM-Group-16/A2/MITLicense)
