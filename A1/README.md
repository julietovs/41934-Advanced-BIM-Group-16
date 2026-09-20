# A1 Forensic BIM

**Group number:** 16

## Focus Area

Indoor Climate

## Identified issues

During the investigation of the indoor climate data in the IFC model, no temperature values were found in the investigated properties associated with the IfcSpace objects.

This creates an issue because the IFC model does not contain directly accessible temperature data that can be used to verify the indoor climate performance reported in the project documentation.

## Project Claim

The MEP report states that the indoor climate was evaluated according to 
DS/EN 16798-1 Category II.

The report states that 29 rooms were evaluated, of which 24 achieved 
100% compliance, while the remaining five rooms had a minimum compliance 
of 99.7%.

**Source:** Renovation of Building 308 – Part D MEP Report, Indoor Climate 
Performance, page 18.

## Investigation

The IFC model was investigated using Python and IfcOpenShell to determine whether temperature information is available in the model and can be used to verify the reported indoor climate performance.

The script extracts all IfcSpace objects from the IFC model and searches their associated property sets for temperature-related properties. For each space, the room name, room number, and available temperature value are extracted and exported to a CSV file.

The analysis successfully identified the spaces and their corresponding room numbers. However, no temperature values were found for the investigated IfcSpace objects, leaving the temperature column in the CSV file empty.

Therefore, the temperature data required to directly verify the indoor climate performance stated in the MEP report could not be retrieved from the IFC model.

## Possible Solutions

Temperature-related indoor climate data could be added to the relevant IfcSpace objects through appropriate property sets. This would allow the indoor climate information in the BIM model to be compared with the results reported in the MEP documentation.

Alternatively, the indoor climate simulation results could be linked to the corresponding spaces in the IFC model, improving traceability between the BIM model and the indoor climate analysis.

## Conclusion

The investigation shows that the IFC model contains information about the building spaces, but no temperature values were found in the investigated IfcSpace properties.

As a result, the reported compliance with DS/EN 16798-1 Category II cannot be directly verified using the temperature information available in the IFC model. The project claim is therefore documented in the MEP report, but the necessary temperature data for independently checking the claim is not available through the investigated IFC properties.
