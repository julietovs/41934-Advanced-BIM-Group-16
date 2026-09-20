# A1 Forensic BIM

**Group number:** 16

## Focus Area

Indoor Climate


## Project Claim

The MEP report claims that the indoor temperatures in the evaluated rooms comply with the temperature limits defined for DS/EN 16798-1 Category II.

Source: Renovation of Building 308 – Part D MEP Report, Indoor Climate Performance, page 18.

## Identified issues

To verify the project claim, the room temperatures in the IFC model should be compared with the temperature requirements for DS/EN 16798-1 Category II.

However, no temperature values were found in the investigated IfcSpace properties. The IFC model therefore does not contain the temperature data needed to perform this comparison and verify the claim.

### Cause of the Issue

The issue is primarily considered a modelling issue.

The indoor climate performance is documented in the MEP report, but the corresponding temperature data is not available in the investigated IfcSpace properties in the IFC model.

This creates a gap between the indoor climate analysis presented in the report and the information available in the BIM model.


## Investigation

The IFC model was investigated using Python and IfcOpenShell.

The script:

- extracts all IfcSpace objects from the model,
- identifies the room name and room number,
- searches the associated property sets for temperature-related properties,
- exports the results to a CSV file.

The rooms and room numbers were successfully identified. However, no temperature values were found, leaving the temperature column in the CSV file empty.

Because the temperature values are not available, they cannot be compared with the requirements in DS/EN 16798-1 Category II.

## Potential Solutions
### Design Perspective

The indoor climate analysis could provide a clearer connection between the reported temperature performance and the corresponding rooms in the BIM model.

This would improve the traceability between the design analysis and the model.

### Modelling Perspective

Temperature-related data could be added to the relevant IfcSpace objects through appropriate property sets.

This would make it possible to extract the room temperatures directly from the IFC model and compare them with the temperature limits defined in DS/EN 16798-1 Category II.

## Conclusion

The investigation shows that the IFC model contains information about the building spaces, but no temperature values were found in the investigated IfcSpace properties.

As a result, the reported compliance with DS/EN 16798-1 Category II cannot be directly verified using the temperature information available in the IFC model. The project claim is therefore documented in the MEP report, but the necessary temperature data for independently checking the claim is not available through the investigated IFC properties.
