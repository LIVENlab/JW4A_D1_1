# turbines matching

```mermaid
graph TD
    HasHubHeight[Widpark has hub height?]
    HasHubHeight -- yes --> HasMan
    HasHubHeight -- no --> fit_curve[Hub height fitting curve]
    HasParPower[Windpark has park power?]
    HasParPower -- yes --> HasMan
    HasParPower -- no --> EXCLUDE[Exclude this wind farm]
    HasMan[Windpark has Manufacturer?]
    HasMan -- yes --> ManExists
    HasMan -- " no " --> MAN_FIT_CURVE[No turbine: Rotor diameter from fitting curves. Default generator gb_dfig]
    ManExists(Manufacturer exists?)
    ManExists -- yes --> WPHasTurbine?
    ManExists -- " no " --> MAN_FIT_CURVE
    WPHasTurbine?[Windpark has turbine?]
    WPHasTurbine? -- yes --> ManTurbinePairExists?[Manufacturer and turbine pair exists?]
    WPHasTurbine? -- no --> PowerMatch?[Manufacturer has turbines with same power?]
    PowerMatch? -- " yes " --> OneMostCommon?
    PowerMatch? -- no --> CLOSEST[Find manufacturers turbine with the most similar power]
    CLOSEST --> OneMostCommon?[For the turbine model candidates, is there one option deployed more often in Europe?]
    OneMostCommon? -- " yes " --> MATCH
    OneMostCommon? -- no --> RND[Random turbine model from candidates]
    ManTurbinePairExists? -- " yes " --> MATCH
    ManTurbinePairExists? -- no --> PowerMatch?
```
