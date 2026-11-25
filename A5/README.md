# A5 Reflect – Group 16

**Focus area:** Indoor Climate  
**Role:** Analyst  
**Case study:** Building #2601

Our [A2 use case](../A2/README.md) defined a room-by-room ventilation check for Building #2601. The [A3 tutorial](../A3/README.md) shows how to import room-level indoor climate data into IFC and verify that the values were saved. The [A4 tool](../A4/README.md) uses room data to compare the design supply airflow with the airflow criterion selected in A2.

## Group reflection

### Feedback on our A3 tutorial

[Summarise one thing peers found useful and one point they wanted clarified or improved. Include a specific comment from the tutorial review or Show & Tell.]

[Explain how the group responded. Describe a change you made or a change you would make next time.]

### Did the A4 tool address our use case?

Our use case was to check whether the design supply airflow for offices and meeting rooms in Building #2601 meets the selected airflow criterion. The A4 tool calculates the required airflow from floor area and design occupancy, compares it with the design supply airflow and reports the result for each selected room. It also flags rooms with missing or invalid inputs.

We tested the calculation and reporting on a synthetic IFC model. [If you have since run the tool on the Building #2601 model, add one concrete result and mention any limitations in the available room data.]

### Advanced Building Design stage

We consider the tool most useful in **Stage C – Detailed Design**. By this stage, floor area, design occupancy and proposed supply airflow can be compared for each room. Designers can use the results to investigate shortfalls or missing inputs while the ventilation design can still be revised.

## Individual reflection – Julie Søfting Tovslid

**Group 16 · Indoor Climate · Analyst**

### My learning experience

**Starting level in the course framework:** [Insert the level from the course figure and briefly explain your choice.]

**Level at the end of the course:** [Insert the level from the course figure and give one example of what you can now do.]

At the start of the course, I was familiar with indoor climate criteria from an engineering perspective. I had less experience using Python to find and check the information behind those criteria in an IFC model. During the course, I learned how to link a row in a CSV file to the correct `IfcSpace`, store the values as room properties and verify that they were saved in the model.

A1 showed me why this matters. We could read the thermal comfort claim in the report, but the IFC did not contain the temperature information we needed to verify it. I would like to learn more about linking architectural and ventilation data across separate IFC models. Room area may come from the architectural model, while design airflow may be available in a ventilation model or a separate schedule.

### Developing the tutorial

Developing the tutorial made me pay closer attention to details I could easily skip when running the scripts myself. A user needs to know that the room number in the CSV must match `IfcSpace.Name`, which IFC file to save and how to check that the values landed on the intended room. [Add one sentence about what the peer feedback made you reconsider or explain differently.]

The course also helped me formulate a possible thesis question. *How can room-level IFC data support repeatable indoor climate checks when the required inputs come from different disciplines?*

I appreciated being able to choose a use case related to indoor climate. I would have benefited from more guidance on how to assess the available model data early on. For our project, Bonsai, IfcOpenShell and GitHub each served a clear purpose. I would keep those tools and make additional tools optional where the use case does not require them.

### My future use of OpenBIM

I would consider using OpenBIM in my thesis if the topic involves ventilation or building performance. For example, I could extract room areas and design occupancies from an IFC model to prepare inputs for a simulation or check how a design change affects the required airflow.

Over the next ten years, I can see myself using OpenBIM to review information exchanged between architects and building services engineers. A repeatable check could help me identify missing inputs or rooms that need closer review after a design update.

### Wrap-up – A1 to A5

A1 showed me what can happen when the information behind a design claim is missing from the model. In A2, we turned that problem into a narrower ventilation use case. A3 taught me how to explain the preparation and verification of room data, and A4 put those inputs to work in an automated check. Looking back in A5, the most important lesson for me is to make every input traceable to the correct room and source before drawing a conclusion from the result.

## Individual reflection – [Name]

**Group 16 · Indoor Climate**

### My learning experience

**Starting level in the course framework:** [Insert your level from the course figure and explain why it fits.]

**Level at the end of the course:** [Insert your level from the course figure and give an example of what you can now do.]

[Explain what you learned about working with room data in IFC. Use a specific example from your own work. What would you still like to learn, and how might it help you use OpenBIM?]

### Developing the tutorial

[Describe your contribution to the A3 tutorial. What did preparing it teach you? Include one comment you actually received and explain what it made you reconsider or what you would explain differently next time.]

[Did the course help you identify or refine a question you might investigate in a thesis? Describe the question or explain what remains unclear.]

[Would you have preferred fewer use-case choices? Was the number of tools appropriate? Explain which tools you would keep, add or leave out, and why.]

### My future use of OpenBIM

[Are you likely to use OpenBIM in your thesis? Explain how it could fit a topic you are considering.]

[Are you likely to use OpenBIM in professional practice over the next ten years? Give one example of a task where it could help.]

### Wrap-up – A1 to A5

[Describe how your understanding changed from investigating the claim in A1, defining the use case in A2, creating the tutorial in A3 and developing the tool in A4, to reflecting on the process in A5. End with one lesson you will take into your next project.]
