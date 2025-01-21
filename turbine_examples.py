import WindTrace_offshore

swt_6_150 = {'name': 'Siemens Gamesa SWT-6.0-154',
             'manufacturer': 'Siemens Gamesa',
             'power': 6,
             'hub height': 120,
             'rotor diameter': 154,
             'generator': 'gb_pmsg',
             'foundations': 'monopile',
             'sea depth': 35,
             'distance to shore': 16.5,
             'cf': 39,
             'park_name': 'Rampion Offshore Wind Farm',
             'coordinates': (50.750, -0.300),
             'location': 'GB',
             'commissioning': 2018
            }

v164_8 = {'name': 'Vestas V164-8.0',
          'manufacturer': 'Vestas',
          'power': 8,
          'hub height': 105,
          'rotor diameter': 164,
          'generator': 'gb_pmsg',
          'foundations': 'monopile',
          'sea depth': 10,
          'distance to shore': 8,
          'cf': 35,
          'park_name': 'Burbo Bank Offshore (extension)',
          'coordinates': (53.500, -3.200),
          'location': 'GB',
          'commissioning': 2017
          }

v164_10 = {'name': 'Vestas V164-10.0',
           'manufacturer': 'Vestas',
           'power': 10,
           'hub height': 122,
           'rotor diameter': 164,
           'generator': 'gb_pmsg',
           'foundations': 'monopile',
           'sea depth': 50,
           'distance to shore': 27,
           'cf': 40.58,
           'park_name': 'Seagreen Offshore',
           'coordinates': (56.633, -2.217),
           'location': 'GB',
           'commissioning': 2023
          }

v236_15 = {'name': 'Vestas V236-15.0',
           'manufacturer': 'Vestas',
           'power': 15,
           'hub height': 143,
           'rotor diameter': 236,
           'foundations': 'monopile',
           'generator': 'gb_pmsg',
           'sea depth': 50,
           'distance to shore': 27,
           'cf': 40.58,
           'park_name': 'hypothetical_Seagreen_Offshore',
           'coordinates': (56.633, -2.217),
           'location': 'GB',
           'commissioning': 2023
          }

for example in [swt_6_150, v164_8, v164_10, v236_15]:
    WindTrace_offshore.lci_offshore_turbine(
        park_name=f'{example["name"]}_{example["park_name"]}',
        park_power=example['power'], number_of_turbines=1, park_location=example['location'],
        park_coordinates=example['coordinates'], manufacturer=example['manufacturer'],
        rotor_diameter=example['rotor diameter'], turbine_power=example['power'], hub_height=example['hub height'],
        commissioning_year=example['commissioning'], offshore_type='monopile', sea_depth=example['sea depth'],
        distance_to_shore=example['distance to shore'], lifetime=25, generator_type=example['generator']
    )
    for foundation_type in ['gravity', 'tripod', 'floating']:
        if foundation_type == 'gravity':
            sea_depth = 5
            WindTrace_offshore.lci_offshore_turbine(
                park_name=f'{example["name"]}_{foundation_type}',
                park_power=example['power'], number_of_turbines=1, park_location=example['location'],
                park_coordinates=example['coordinates'], manufacturer=example['manufacturer'],
                rotor_diameter=example['rotor diameter'], turbine_power=example['power'],
                hub_height=example['hub height'],
                commissioning_year=example['commissioning'], offshore_type=foundation_type, sea_depth=sea_depth,
                distance_to_shore=example['distance to shore'], lifetime=25, generator_type=example['generator'])
        elif foundation_type == 'tripod':
            sea_depth = 50
            WindTrace_offshore.lci_offshore_turbine(
                park_name=f'{example["name"]}_{foundation_type}',
                park_power=example['power'], number_of_turbines=1, park_location=example['location'],
                park_coordinates=example['coordinates'], manufacturer=example['manufacturer'],
                rotor_diameter=example['rotor diameter'], turbine_power=example['power'],
                hub_height=example['hub height'],
                commissioning_year=example['commissioning'], offshore_type=foundation_type, sea_depth=sea_depth,
                distance_to_shore=example['distance to shore'], lifetime=25, generator_type=example['generator'])
        else:
            sea_depth = 70
            for floating_platform in ['semi_sub', 'spar_buoy_concrete', 'spar_buoy_iron',
                                      'spar_buoy_steel', 'tension_leg', 'barge']:
                WindTrace_offshore.lci_offshore_turbine(
                    park_name=f'{example["name"]}_{foundation_type}_{floating_platform}',
                    park_power=example['power'], number_of_turbines=1, park_location=example['location'],
                    park_coordinates=example['coordinates'], manufacturer=example['manufacturer'],
                    rotor_diameter=example['rotor diameter'], turbine_power=example['power'],
                    hub_height=example['hub height'],
                    commissioning_year=example['commissioning'], offshore_type=foundation_type, sea_depth=sea_depth,
                    floating_platform=floating_platform,
                    distance_to_shore=example['distance to shore'], lifetime=25, generator_type=example['generator'])
