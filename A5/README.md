A5 Reflect – Group 16
Focus area: Indoor Climate
Role: Analyst
Case study: Building #2601

Our [A2 use case](../A2/README.md) defined a room-by-room ventilation check for Building #2601. The [A3 tutorial](../A3/README.md) shows how to import room-level indoor climate data into IFC and verify that the values were saved. The [A4 tool](../A4/README.md) uses room data to compare the design supply airflow with the airflow criterion selected in A2.
Group reflection
Feedback on our A3 tutorial
[Summarise one thing peers found useful and one point they wanted clarified or improved. Include a specific comment from the tutorial review or Show & Tell.]

[Explain how the group responded. Describe a change you made or a change you would make next time.]
Did the A4 tool address our use case?
Our use case was to check whether the design supply airflow for offices and meeting rooms in Building #2601 meets the selected airflow criterion. The A4 tool calculates the required airflow from floor area and design occupancy, compares it with the design supply airflow and reports the result for each selected room. It also flags rooms with missing or invalid inputs.

We tested the calculation and reporting on a synthetic IFC model. [If you have since run the tool on the Building #2601 model, add one concrete result and mention any limitations in the available room data.]
Advanced Building Design stage
We consider the tool most useful in Stage C – Detailed Design. By this stage, floor area, design occupancy and proposed supply airflow can be compared for each room. Designers can use the results to investigate shortfalls or missing inputs while the ventilation design can still be revised.
