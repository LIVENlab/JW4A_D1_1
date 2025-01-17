from src.run import run
from const import result_file
import WindTrace_onshore
import pandas as pd

if __name__ == "__main__":
    # data gap filling
    run(
        run_main_loop=True,
        final_validation=False,
        # preparation
        redo_fix_encoding=False,
        redo_filter=False,
        test_all_filters=False,
        redo_power_fitting_params=False,
        redo_prepare_matching=False,
        redo_gearbox_generator=False,
        redo_continue_location_search=False,
        redo_prepare_hub_height_estimation=False,
    )
    # WindTrace application to European wind fleet
    WindTrace_onshore.bd.projects.set_current(WindTrace_onshore.consts_wt.PROJECT_NAME)
    new_db = WindTrace_onshore.bd.Database(WindTrace_onshore.consts_wt.NEW_DB_NAME)
    biosphere3 = WindTrace_onshore.bd.Database('biosphere3')
    df = pd.read_csv(result_file)
    for index, row in df.iterrows():
        # lifetime
        commissioning_date = str(row['Commissioning date']) if pd.notna(row['Commissioning date']) else None
        commissioning_year = int(commissioning_date[:4]) if commissioning_date else None
        decommissioning_date = str(row['Decommissioning date']) if pd.notna(row['Decommissioning date']) else None
        decommissioning_year = int(decommissioning_date[:4]) if decommissioning_date else None
        if commissioning_year is not None and decommissioning_year is not None:
            lifetime = decommissioning_year - commissioning_year
        else:
            lifetime = 20  # Default lifetime
            commissioning_year = 2011  # default commissioning year
        # Manufacturer
        if pd.isna(row['Manufacturer']):
            manufacturer = 'Vestas'
        else:
            manufacturer = row['Manufacturer']
        # generator type
        if row['Gearbox generator'] == 'gb_eesg':
            gearbox = 'dd_eesg'
        elif row['Gearbox generator'] == 'dd_dfig':
            gearbox = 'gb_dfig'
        else:
            gearbox = row['Gearbox generator']

        # create inventories and add mass to the dataframe
        mass_materials_park, trans, occ = WindTrace_onshore.lci_wind_turbine(
            park_name=row['Wind park name'], park_power=row['Wind park power']/1000,
            number_of_turbines=row['Number of turbines'], park_location=row['Park location'],
            park_coordinates=(row['Latitude'], row['Longitude']), manufacturer=manufacturer,
            rotor_diameter=row['Rotor diameter'], turbine_power=row['Turbine power']/1000, hub_height=row['Hub height'],
            commissioning_year=commissioning_year, lifetime=lifetime, generator_type=gearbox
        )
        for material, mass in mass_materials_park.items():
            if material not in df.columns:
                df[material] = None
            df.at[index, material] = mass
        if 'Transformation (m2)' not in df.columns:
            df['Transformation (m2)'] = None
        df.at[index, 'Transformation (m2)'] = trans
        if 'Occupation (m2a)' not in df.columns:
            df['Occupation (m2a)'] = None
        df.at[index, 'Occupation (m2a)'] = occ

        # calculate lcia and add to dataframe
        results, results_kwh = WindTrace_onshore.lca_wind_turbine(
            park_name=row['Wind park name'], park_power=row['Wind park power']/1000, turbine=False
        )
        for lcia_name, value in results.items():
            if lcia_name not in df.columns:
                df[lcia_name] = None
            df.at[index, lcia_name] = value
        for lcia_name, value in results_kwh.items():
            lcia_name = f'{lcia_name}_kwh'
            if lcia_name not in df.columns:
                df[lcia_name] = None
            df.at[index, lcia_name] = value
    df.to_csv('your_path')
    
