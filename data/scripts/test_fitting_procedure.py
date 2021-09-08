import sys
sys.path.append("..")
import numpy as np
from scripts import model
from scripts.model import Sub
from R0_estimator import empty_data_list, get_Re_guess, stair_func
import matplotlib.pyplot as plt


def generate_data(params):
    """
    Generates fake data using the model.py with the given parameters and initial number of cases
    """
    data = {}
    pop = model.init_pop(params.ages, params.size, np.exp(params.logInitial), params.seroprevalence)
    model_out = model.solve_ode(params, pop)
    res = model.trace_ages(model_out)

    for ii, k in [(Sub.T, 'cases'), (Sub.D, 'deaths'), (Sub.H, 'hospitalized'), (Sub.I, 'infectious'), (Sub.S, 'susceptible'), (Sub.C, 'icu')]:
        data[k] = np.ma.array(res[:,ii])

    return data

def check_fit(data, data_fit, time_points):
    """
    Compare fake data curves to the fitted curves
    """
    plt.figure()
    for jj,(ii,lab) in enumerate(zip([Sub.T, Sub.D, Sub.H, Sub.C],["Cases", "Deaths", "Hospitalized", "ICU"])):
        if data[ii] is not None:
            plt.plot(time_points, data[ii], c=f"C{jj}", label=lab)
            plt.plot(time_points, data_fit[ii], '--', c=f"C{jj}", label=f"{lab} fit")
    plt.yscale("log")
    plt.legend()
    # plt.savefig("Test_fitting", format="png")
    plt.show()

if __name__ == "__main__":
    key = "Switzerland"
    containment_start = 20
    efficacy = 0.7
    time_points = range(1, 50)
    frac_reported = 0.2
    InitialCases = 8
    R0=3

    rates = model.DefaultRates
    params = model.Params(ages=model.AGES[model.POPDATA[key]["ageDistribution"]], size=model.POPDATA[key]["size"],
                    containment_start=containment_start, times=time_points, logR0=np.log(R0))
    params.efficacy = efficacy
    params.reported = frac_reported
    data = generate_data(params, InitialCases)

    data[Sub.H] = None
    data[Sub.C] = None
    Re_guess = get_Re_guess(time_points, data)
    res = model.fit_population_iterative(key, time_points, data)
    data_fit = generate_data(res["params"], np.exp(res["params"].logInitial))

    check_fit(data, data_fit, time_points)
    plt.plot(time_points, stair_func(time_points, *Re_guess["fit"]), label="Fit stair function")
    plt.plot(time_points, stair_func(time_points, 3, 3*0.3, containment_start), label="Input stair function")
    plt.plot(time_points, Re_guess["R0_by_day"][Sub.T], label="R_0 by day")
    plt.plot(time_points, Re_guess["gr"][Sub.T])
    plt.grid()
    plt.legend()
    # plt.savefig("R0_estimation", format="png")
    plt.show()
