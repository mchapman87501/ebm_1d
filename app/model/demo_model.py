#!/usr/bin/env python3

"""
Use the model to create a plot showing hysteresis -
the idea of climate tipping points.
"""
import typing as tp

import matplotlib.pyplot as plt

from .model import Model, ResultSeries, AvgTempResult


def plot_averages(*result_sets: ResultSeries) -> None:
    # Plot temperature ranges.
    plt.figure()
    for result_set in result_sets:
        results = result_set.results
        solar_mults = [rec.solar_mult for rec in results]
        avg_temps = [rec.solution.avg for rec in results]
        plt.plot(solar_mults, avg_temps, label=result_set.summary)

    plt.title("Average Temperature vs. Solar Multiplier")
    plt.xlabel("Solar Multiplier")
    plt.ylabel("Average Temperature")
    plt.legend(loc="best")
    plt.show()


def main() -> None:
    m = Model()
    rising: tp.List[AvgTempResult] = []
    falling: tp.List[AvgTempResult] = []
    for solution in m.gen_temps(0.5, 2.0, -60.0, 9):
        seq = rising if solution.delta > 0 else falling
        seq.append(solution)

    plot_averages(
        ResultSeries("Rising", rising), ResultSeries("Falling", falling)
    )


if __name__ == "__main__":
    main()
