This repository contains the code used to create the data included in the deliverable 1.1 of the project JustWindForAll (JW4A) https://justwind4all.eu/

The code is used to create a database that analyses the European wind fleet, with data of European farms up to 2021. The code makes use of the open-source parametric life-cycle inventory 
model WindTrace, also created within the project. For more information on WindTrace, visit its GitHub repo: https://github.com/LIVENlab/WindTrace_public

We use data from the Wind Power database (https://www.thewindpower.net/), which contains technical specifications of wind farms in Europe. WindTrace analyses these wind farms and provides the following:
- Estimation of the materials used to build the park and their masses.
- Estimation of the land transformed and occupied to build the wind park.
- Life-cycle impact assessment of all wind parks using ReCiPe 2016 midpoint (H) impact methods.

Data requirements before running the code:
- The Wind Power database (csv)
- The Wind Power technical database (csv)
- Ecoinvent license

Preparation to run the code:
1. In consts_wt.py change the following:
   - PROJECT_NAME (name of a new project that will be created in Brightway2)
   - SPOLD_FILES (local route to the cutoff Ecoinvent v3.9.1. Important: other versions are not supported)
   - NEW_DB_NAME (name of the database where the new turbine inventories will be created)
2. Save the following in the folder data -> 0_base:
   - The Wind Power database (csv). Change line 13 in const.py and use the same file name there.
   - The Wind Power technical database (csv). Change line 11 in const.py and use the same file name there.
3. In main.py:
   - In line 82, insert the path where you would like the dataframe to be saved.
Running the code:
1. run main.py
   a) first, run() will be runned, which will fill data gaps and prepare the necessary files to later run WindTrace.
   b) second, WindTrace will create an inventory for each European wind park and will calculate its material demands and environmental impacts.
   c) third, everything will be stored in a dataframe, which will be saved to a csv to the route that you have previously specified.

For any inquiries contact: Miquel Sierra-Montoya (miquel.sierra@uab.cat) or Cristina Madrid-López (cristina.madrid@uab.cat)
