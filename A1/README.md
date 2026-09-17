# A1 Forensic BIM

# Group number 16

## Focus Area
Indoor Climate

## Identified issues

During the investigation of the indoor climate data in the IFC model, 
temperature-related values were found to be set to 0.

This creates an issue because the IFC model does not contain meaningful 
temperature values that can be used to verify the indoor climate results 
reported in the project documentation.

## Project Claim

The MEP report states that the indoor climate was evaluated according to 
DS/EN 16798-1 Category II.

The report states that 29 rooms were evaluated, of which 24 achieved 
100% compliance, while the remaining five rooms had a minimum compliance 
of 99.7%.

**Source:** Renovation of Building 308 – Part D MEP Report, Indoor Climate 
Performance, page 18.

## Investigation

The IFC model was investigated using Python and IfcOpenShell to determine 
whether temperature information is available in the model and can be used 
to verify the reported indoor climate performance.

..............

## Possible Solutions

[INSERT POSSIBLE SOLUTIONS HERE]

## Conclusion

[INSERT CONCLUSION AFTER THE IFC ANALYSIS IS COMPLETED]
