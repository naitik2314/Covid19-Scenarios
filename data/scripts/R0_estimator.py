import numpy as np
from matplotlib import pyplot as plt
import sys
sys.path.append('..')
from datetime import datetime
from scipy.signal import savgol_filter
from scipy import optimize
from enum import IntEnum
import copy
from scripts.mapping import R0s_mapping, GR_mapping

compartments = ['S', 'E1', 'E2', 'E3', 'I', 'H', 'C', 'D', 'R', 'T', 'NUM']
Sub = IntEnum('Sub', compartments, start=0)

def empty_data_list():
    """
    Base data structure, a list containing vectors of data
    """
    return [np.array([]) if (i == Sub.D or i == Sub.T) else None for i in range(Sub.NUM)]

def smooth(data, as_int=False, nb_pts=9, order=3):
    """
    Smooth data using a savgol filter ignoring the nan values. The missing data points stay nans
    """
    smoothed = copy.deepcopy(data)
    for ii in [Sub.T, Sub.D, Sub.H, Sub.C]:
        if smoothed[ii] is not None:
            good_idx = ~np.isnan(smoothed[ii])
            np.put(smoothed[ii], np.where(good_idx)[0],
                    savgol_filter(smoothed[ii][good_idx], nb_pts, order,
                                  mode="interp" if np.sum(good_idx)>nb_pts else "mirror"))
            if as_int:
                smoothed[ii] = np.round(smoothed[ii]).astype(int)
    return smoothed

def get_log(data):
    '''
    return the logarithm of the data structure
    '''
    log_data = empty_data_list()
    for ii in [Sub.T, Sub.D, Sub.H, Sub.C]:
        if data[ii] is not None:
            log_data[ii] = np.ma.log(data[ii])
    return log_data


def log_smooth(data, nb_pts=7):
    '''
    smooth the logarithm in week windows and return the exponential
    '''
    log_smooth = empty_data_list()
    smoothed_log_diff = smooth(get_log(data), as_int=False, nb_pts=nb_pts, order=1)
    for ii in [Sub.T, Sub.D, Sub.H, Sub.C]:
        if smoothed_log_diff[ii] is not None:
            log_smooth[ii] = np.ma.exp(smoothed_log_diff[ii])
    return log_smooth


def growth_rate_to_R0(data, serial_interval=6):
    '''
    convert a growth rate estimate to R0 using a calibration table
    '''
    R0_by_day = empty_data_list()
    for ii in [Sub.T, Sub.D]:
        if data[ii] is not None:
            R0_by_day[ii] = np.ma.array(np.interp(data[ii], GR_mapping, R0s_mapping))
            R0_by_day[ii].mask = np.isnan(R0_by_day[ii])
        else:
            R0_by_day[ii] = None
    return R0_by_day


def get_daily_counts(data):
    '''
    convert cumulative counts into daily counts
    '''
    diff_data = empty_data_list()
    for ii in [Sub.T, Sub.D]:
        if data[ii] is not None:
            diff_data[ii] = np.ma.array(np.concatenate(([np.nan],np.diff(data[ii]))))
            diff_data[ii][diff_data[ii]==0] = np.nan
            diff_data[ii].mask = np.isnan(diff_data[ii])
        else:
            diff_data[ii] = None
    return diff_data


def get_growth_rate(data, step=7):
    '''
    take log derivative of the data over time intervals of step.
    pad overhang with nan
    '''
    log_diff = empty_data_list()
    for ii in [Sub.T, Sub.D]:
        if data[ii] is not None:
            log_diff[ii] = (np.ma.log(data[ii][step:]) - np.ma.log(data[ii][:-step]))/step
            nans = np.ma.repeat(np.nan, step)
            nans.mask = np.isnan(nans)
            log_diff[ii] = np.ma.concatenate((log_diff[ii], nans))
            log_diff[ii][log_diff[ii].mask] = np.nan
        else:
            log_diff[ii] = None
    return log_diff


def stair_func(time, val_o, val_e, x_drop):
    """
    Stair function used to fit R_0
    """
    return np.array([val_o if t <= x_drop else val_e for t in time])


def err_function(x_drop, time, vec, val_o, val_e):
    # vec need to be masked to avoid nan
    return np.sum(np.abs(vec - stair_func(time, val_o, val_e, x_drop)))

def stair_fits(time, data, n_start_value=3, n_end_values=3, dropshift=4):
    """
    Estimate the 3 parameters to best fit R_0 with a stair function. The origin and end values are estimated
    using an average over the first/list nb_value points. The drop position is choosen to minimize the error function.
    The shift of 4 days in the drop is here to compensate the shift caused by growth rate estimation (difference over 7 days)
    """
    stair_fits = empty_data_list()
    for ii in [Sub.T, Sub.D, Sub.H, Sub.C]:
        if data[ii] is not None:
            val_o = np.mean(data[ii][~data[ii].mask][:n_start_value])
            val_e = np.mean(data[ii][~data[ii].mask][-n_end_values:])
            if len(data[ii][~data[ii].mask][:n_start_value]) and len(data[ii][~data[ii].mask][-n_end_values:]):
                drop = time[np.argmin([err_function(x, time, data[ii], val_o, val_e) for x in time])]
                stair_fits[ii] = [val_o, val_e, drop+dropshift]
            else:
                stair_fits[ii] = None
        else:
            stair_fits[ii] = None
    return stair_fits

def get_Re_guess(time, cases, step=7, extremal_points_start=10, extremal_points_end=21, only_deaths=False):
    """
    Compute R_effective from the data and estimate the stair function fit parameters for this R_effective
    """
    death_delay = 9
    diff_data = get_daily_counts(cases)
    data_log_smoothed = log_smooth(diff_data)
    growth_rate = get_growth_rate(data_log_smoothed, step)
    R0_by_day = growth_rate_to_R0(growth_rate)
    fits = stair_fits(time, R0_by_day, n_start_value=extremal_points_start, n_end_values=extremal_points_end)
    if only_deaths:
        fits[Sub.D][2] -= death_delay

    return {"fit" : fits[Sub.D] if only_deaths else combine_fits(fits),
            "diff_data": diff_data,
            "diff_data_smoothed": data_log_smoothed,
            "R0_by_day": R0_by_day,
            "gr":growth_rate}

def combine_fits(fits, drop_shift=9):
    """
    Combine fits coming from cases and deaths if they are coherent with one another and returns it. If they
    are not coherent, return the fit from the case data.
    """
    # combine fits from cases and deaths if they are coherent, otherwise return fit from cases
    if fits[Sub.T] != None:
        if fits[Sub.D] != None:
            test1 = np.abs(fits[Sub.T][0] - fits[Sub.D][0]) / (0.5*(fits[Sub.T][0] + fits[Sub.D][0])) < 0.4
            test2 = np.abs(fits[Sub.T][1] - fits[Sub.D][1]) / (0.5*(fits[Sub.T][1] + fits[Sub.D][1])) < 0.3
            test3 = np.abs((fits[Sub.D][2]-drop_shift) - fits[Sub.T][2]) < drop_shift//2 + 1
            if test1 and test2 and test3:
                val_o = 0.5*(fits[Sub.T][0] + fits[Sub.D][0])
                val_e = 0.5*(fits[Sub.T][1] + fits[Sub.D][1])
                drop = 0.5*(fits[Sub.T][2] + (fits[Sub.D][2] - drop_shift))
                return [val_o, val_e, drop]
            else:
                return fits[Sub.T]
        else:
            return fits[Sub.T]
    else:
        return None

def get_R0_comparison(country_list):
    """
    Get statistics on the fitting parameters over a list of countries.
    """
    lags = []
    rdiffs_o = []
    rdiffs_e = []
    for c in country_list:
        time, data = load_data(c, case_counts[c])
        res = get_Re_guess(time, data)
        fits = res["fits"]
        if (fits[Sub.D] != None) and (fits[Sub.T] != None):
            rdiff_o = (fits[Sub.D][0] - fits[Sub.T][0])/(0.5*(fits[Sub.D][0] + fits[Sub.T][0]))
            rdiff_e = (fits[Sub.D][1] - fits[Sub.T][1])/(0.5*(fits[Sub.D][1] + fits[Sub.T][1]))
            lag = fits[Sub.D][2] - fits[Sub.T][2]
        else:
            lag, rdiff_o, rdiff_e = np.nan, np.nan, np.nan

        lags = lags + [lag]
        rdiffs_o = rdiffs_o + [rdiff_o]
        rdiffs_e = rdiffs_e + [rdiff_e]

    for vec in [rdiffs_o, rdiffs_e, lags]:
          vec = np.ma.array(vec)
          vec.mask = np.isnan(vec)
          print(vec)
          print(np.ma.mean(vec))
          print(np.ma.std(vec))

if __name__ == "__main__":
    from scripts import tsv
    from scripts.model import load_data
    case_counts = tsv.parse()

    country_list = ["FRA-Auvergne-Rhône-Alpes"]
    # country_list = ["Germany", "Switzerland", "Italy"]
    # country_list = ["United States of America", "Spain", "Germany", "Italy", "Belgium",
    # "United Kingdom of Great Britain and Northern Ireland", "CHE-Zürich", "CHE-Basel-Stadt",
    # "CHE-Geneva", "CHE-Valais", "CHE-Ticino", "USA-California", "USA-New York", "USA-New Jersey"]

    for ci, c in enumerate(country_list):
        time, data = load_data(c, case_counts[c])
        res = get_Re_guess(time, data, extremal_points_start=10, extremal_points_end=20, only_deaths=True)
        fit = res["fit"]
        R0_by_day = res["R0_by_day"]
        dates = [datetime.fromordinal(x) for x in time]

        for ee, ii in enumerate([Sub.T, Sub.D]):
            if data[ii] is not None:
                plt.figure(1)
                plt.plot(dates, R0_by_day[ii], '--', c=f"C{2*ci+ee}", label=f"{c}")

                plt.figure(2)
                plt.plot(dates, res['diff_data'][ii], '--', label=f"{c} {ii}", c=f"C{2*ci+ee}")
                plt.plot(dates, res['diff_data_smoothed'][ii] , label=f"{c} {ii}", c=f"C{2*ci+ee}")

    plt.figure(1)
    plt.plot(dates, stair_func(time, *fit), label=f"fit")
    plt.ylabel("R0")
    plt.xlabel("Time [days]")
    plt.legend(loc="best")
    plt.savefig("Stair_fit", format="png")

    plt.figure(2)
    plt.title("New cases per day")
    plt.legend()
    plt.grid()

    plt.show()

    # get_R0_comparison(country_list)
