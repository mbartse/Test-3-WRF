import numpy as np

def error_metrics(actual_inp, ideal_inp):
    actual = actual_inp[~np.isnan(actual_inp)]
    ideal = ideal_inp[~np.isnan(actual_inp)] 
    
    correlation_matrix = np.corrcoef(actual, ideal)
    correlation_xy = correlation_matrix[0,1]
    r_squared = correlation_xy**2
    
    MSE=np.mean((actual - ideal)**2)
    RMSE=np.sqrt(MSE)
    MAE=np.mean(np.absolute(actual - ideal))
    
    return r_squared,MSE,RMSE,MAE;

def heatindex(tin, rhin):

    original_shape = tin.shape

    # Convert to Farenheit
    # t = wv.K2F(tin.ravel())

    t = tin.ravel()
    rh = rhin.ravel()

    rh[rh > 100] = 100  # Truncate RH range to 100% (eqn is an approx.)

    # Initial guess for the Heat index

    hi_initial = 0.5 * (t + 61.0 + (t - 68.0) * 1.2 + rh * .094)

    # Our conditions for applying the different eqns and corrections for the
    # Heat Index

    cond0mask = (hi_initial + t) / 2 >= 80.
    cond1mask = (t[cond0mask] > 80) & (t[cond0mask] < 112) \
        & (rh[cond0mask] < 13)

    cond2mask = (rh[cond0mask] > 85) & (t[cond0mask] > 80) \
        & (t[cond0mask] < 87)

    # Initialize zero-arrays that we'll fill out depending on the
    # condition masks.

    hi = np.zeros(t.shape, dtype=np.float32)
    hi_baseline = np.zeros(t.shape, dtype=np.float32)
    adj = np.zeros(t.shape, dtype=np.float32)

    c1 = -42.379
    c2 = 2.04901523
    c3 = 10.14333127
    c4 = -.22475541
    c5 = -6.83783e-3
    c6 = -5.481717e-2
    c7 = 1.22873e-3
    c8 = 8.5282e-4
    c9 = -1.99e-6

    hi_baseline[cond0mask] = c1 + c2 * t[cond0mask] + c3 \
        * rh[cond0mask] + c4 * t[cond0mask] * rh[cond0mask] + c5 \
        * t[cond0mask] ** 2 + c6 * rh[cond0mask] ** 2 + c7 \
        * rh[cond0mask] * t[cond0mask] ** 2 + c8 * t[cond0mask] \
        * rh[cond0mask] ** 2 + c9 * t[cond0mask] ** 2 * rh[cond0mask] \
        ** 2

    adj[cond0mask][cond1mask] = -((13 - rh[cond0mask][cond1mask]) / 4) \
        * np.sqrt((17 - np.abs(t[cond0mask][cond1mask] - 95)) / 17.0)

    adj[cond0mask][cond2mask] = (rh[cond0mask][cond2mask] - 85) / 10 \
        * ((87 - t[cond0mask][cond2mask]) / 5.0)

    # The HI with condition 0 (cond0mask) is in the form baseline + adjustment

    hi[cond0mask] = hi_baseline[cond0mask] + adj[cond0mask]
    hi[~cond0mask] = hi_initial[~cond0mask]

    return hi.reshape(original_shape)
