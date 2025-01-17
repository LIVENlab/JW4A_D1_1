import json
from typing import Any, Callable

import numpy as np
import pandas as pd
from pandas import DataFrame
from scipy.optimize import curve_fit

from const import base_data_path, power_fitting_params_dir, filtered_turbine_file

fitting_params: dict[str, Any] = {}


INITIAL_PARAMETERS = [250, 1000, 1]



def lin_func(x, a, b):
    return a * x + b


def exp_modified_function(x, a, b, n):
    return a * x ** n / (x ** n + b)


USE_FUNC: Callable = exp_modified_function


def create_fit_curve(power: np.ndarray, diameter: np.ndarray, name: str = "GLOBAL"):
    global fitting_params

    mask = ~np.isnan(power)
    power_filtered = power[mask]
    diameter_filtered = diameter[mask]
    # create a Dataframe from these two
    df = pd.DataFrame({"power": power_filtered, "diameter": diameter_filtered})
    # write that to a csv
    df.to_csv(power_fitting_params_dir / f"{name}_data.csv", encoding="utf-8", index=False)

    params, params_covariance = curve_fit(USE_FUNC, power_filtered, diameter_filtered, p0=INITIAL_PARAMETERS)

    power_fitting_params_dir.mkdir(exist_ok=True)
    fp = power_fitting_params_dir / f"{name}.json"
    with (fp).open("w", encoding="utf-8") as fout:
        json.dump(params.tolist(), fout)
    print(f"-> {fp.relative_to(base_data_path)}")
    fitting_params[name] = params


def load_fitting_params(name: str = "GLOBAL"):
    global fitting_params
    if fitting_params.get(name) is None:
        file_path = power_fitting_params_dir / f"{name}.json"
        with file_path.open(encoding="utf-8") as fin:
            fitting_params[name] = np.array(json.load(fin))


def fit_value(power: float, name: str = "GLOBAL") -> float:
    global fitting_params
    load_fitting_params(name)
    return USE_FUNC(float(power), *fitting_params[name])


def fit_ndarray(power: np.ndarray, name: str = "GLOBAL"):
    global fitting_params
    load_fitting_params(name)
    print("use params", fitting_params[name])
    return USE_FUNC(power, *fitting_params[name])


def plot(df: DataFrame):
    # type: ignore # plot the points, and the fitting curve
    import matplotlib.pyplot as plt

    # different colors for different manufacturers
    # get all unique manufacturers
    manufacturers = df["Manufucturer"].unique()
    # create a color map
    color_map = plt.get_cmap("tab20")
    # create a figure
    fig = plt.figure(figsize=(10, 10))
    # create a subplot
    ax = fig.add_subplot(1, 1, 1)

    power = np.array([float(str(d).replace(",", ".")) for d in df["Rated power"]])
    diameter = np.array([float(str(d).replace(",", ".")) for d in df["Rotor diameter"]])

    ax.scatter(power, diameter, marker="x")
    x = np.linspace(0, 20000, 100)
    y = fit_ndarray(x)
    # with orig parameters
    plt.plot(x, y, color="black")
    #y2 = USE_FUNC(x, *INITIAL_PARAMETERS)
    #plt.plot(x, y2, color="red")

    y_org = USE_FUNC(x, *INITIAL_PARAMETERS)
    plt.plot(x, y_org, color="red")

    mask = ~np.isnan(power)
    power_filtered = power[mask]
    diameter_filtered = diameter[mask]

    a_values = [100]  # [max(diameter_filtered) - 10, max(diameter_filtered), max(diameter_filtered) + 10]
    b_values = [0.001]  # [0.0001, 0.0005, 0.001, 0.005]


    # for a in a_values:
    #     for b in b_values:
    #         print(a,b)
    #         print(list(zip(power_filtered, USE_FUNC(power_filtered, a, b))))
    #         plt.plot(power_filtered, USE_FUNC(power_filtered, a, b), label=f'Exp Sat a={a:.1f}, b={b:.4f}')

    plt.show()
    fig.savefig(power_fitting_params_dir / "power_fitting.png")


def create_filtered_turbine_power_fitting() -> DataFrame:
    print("creating filtered turbine power fitting")
    # open wind_extract_file with pandas
    df = pd.read_csv(filtered_turbine_file, encoding="utf-8")
    df2 = df[["ID", "Manufucturer", "Rated power", "Rotor diameter"]]
    # make ID the index
    df2.set_index("ID", inplace=True)
    # save that to a 2nd csv
    # get rated power and rotor diameter as 2 ndarrays
    power = np.array([float(str(d).replace(",", ".")) for d in df2["Rated power"]])
    diameter = np.array([float(str(d).replace(",", ".")) for d in df2["Rotor diameter"]])
    # create the fitting curve
    create_fit_curve(power, diameter, "GLOBAL")

    return df2


if __name__ == "__main__":
    df = create_filtered_turbine_power_fitting()
    plot(df)
