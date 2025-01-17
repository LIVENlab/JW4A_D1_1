import json
from typing import Any, Callable

import numpy as np
import pandas as pd
from pandas import DataFrame
from scipy.optimize import curve_fit

from const import base_data_path, hub_height_dir, global_hh_power_fitting_params_file, \
    filtered_market_file

hh_fitting_params: dict[str, Any] = {}


INITIAL_PARAMETERS = [220, 3000,1]


def lin_func(x, a, b):
    return a * x + b


def exp_modified_function(x, a, b, n):
    return a * x ** n / (x ** n + b)


USE_FUNC: Callable = exp_modified_function


def create_hh_fit_curve(power: np.ndarray, hub_height: np.ndarray, name: str = "GLOBAL"):
    global hh_fitting_params

    mask = ~np.isnan(power)
    power_filtered = power[mask]
    hub_height_filtered = hub_height[mask]
    # create a Dataframe from these two
    df = pd.DataFrame({"power": power_filtered, "hub_height": hub_height_filtered})
    # write that to a csv
    df.to_csv(hub_height_dir / f"{name}_data.csv", encoding="utf-8", index=False)

    params, params_covariance = curve_fit(USE_FUNC, power_filtered, hub_height_filtered, p0=INITIAL_PARAMETERS)

    hub_height_dir.mkdir(exist_ok=True)
    fp = global_hh_power_fitting_params_file
    with (fp).open("w", encoding="utf-8") as fout:
        json.dump(params.tolist(), fout)
    print(f"-> {fp.relative_to(base_data_path)}")
    hh_fitting_params[name] = params


def load_hh_fitting_params(name: str = "GLOBAL"):
    global hh_fitting_params
    if hh_fitting_params.get(name) is None:
        file_path = hub_height_dir / f"{name}.json"
        with file_path.open(encoding="utf-8") as fin:
            hh_fitting_params[name] = np.array(json.load(fin))


def fit_hh_value(power: float, name: str = "GLOBAL") -> float:
    global hh_fitting_params
    load_hh_fitting_params(name)
    return USE_FUNC(float(power), *hh_fitting_params[name])


def fit_hh_ndarray(power: np.ndarray, name: str = "GLOBAL"):
    global hh_fitting_params
    load_hh_fitting_params(name)
    print("use params", hh_fitting_params[name])
    return USE_FUNC(power, *hh_fitting_params[name])


def plot_hh(df: DataFrame):
    # type: ignore # plot the points, and the fitting curve
    import matplotlib.pyplot as plt

    # different colors for different manufacturers
    # create a figure
    fig = plt.figure(figsize=(10, 10))
    # create a subplot
    ax = fig.add_subplot(1, 1, 1)

    power = np.array([float(str(d).replace(",", ".")) for d in df["Turbine power"]])
    hub_height = np.array([float(str(d).replace(",", ".")) for d in df["Hub height"]])

    ax.scatter(power, hub_height, marker="x")
    x = np.linspace(0, 20000, 100)
    y = fit_hh_ndarray(x)
    # with orig parameters
    plt.plot(x, y, color="black")
    #y2 = USE_FUNC(x, *INITIAL_PARAMETERS)
    #plt.plot(x, y2, color="red")

    y_org = USE_FUNC(x, *INITIAL_PARAMETERS)
    plt.plot(x, y_org, color="red")

    plt.show()
    fig.savefig(hub_height_dir / "hh_power_fitting.png")


def create_hh_filtered_turbine_power_fitting() -> DataFrame:
    print("creating hub height filtered turbine power fitting")

    df = pd.read_csv(filtered_market_file, encoding="utf-8")
    # filter only those rows where we have a "Hub height"
    df = df[df["Hub height"].notna()]
    df2 = df[["ID", "Hub height", "Turbine power"]]
    df2.set_index("ID", inplace=True)
    power = np.array([float(d) for d in df2["Turbine power"]])
    hub_height = np.array([float(d) for d in df2["Hub height"]])
    create_hh_fit_curve(power, hub_height, "GLOBAL")
    return df2



if __name__ == "__main__":
    df = create_hh_filtered_turbine_power_fitting()
    plot_hh(df)
