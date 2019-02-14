
# import all packages
# import necessary libraries

import numpy as np
import pandas as pd
import pdb
import matplotlib as mpl


from pykalman import KalmanFilter
from datetime import datetime
from numpy import log, polyfit, sqrt, std, subtract
import statsmodels.tsa.stattools as ts
import statsmodels.api as sm
import matplotlib.pyplot as plt
import seaborn as sns
import ffn

all_data = pd.read_excel('Data.xlsx', index_col='date')
all_data = all_data.fillna("Zuhaib")

count = 0
i=2
while i < len(all_data.columns):
	one_col = all_data[all_data.columns[i]]
	for j in range(len(all_data)):
		if (one_col[j] == "Zuhaib"):
			count = count + 1
	if count >= (0.60*(len(all_data))):
		all_data = all_data.drop(all_data.columns[i], axis=1)
		count = 0
	i = i + 1

###############################################################################################################################

def find_cointegrated_pairs(dataframe, critial_level = 0.05):
	n = dataframe.shape[1] # the length of dateframe
	pvalue_matrix = np.ones((n, n)) # initialize the matrix of p
	keys = dataframe.keys() # get the column names
	pairs = [] # initilize the list for cointegration
	pairs1 = []
	for i in range(n):
		for j in range(i+1, n): # for j bigger than i
			#print dataframe[keys[i]]
			stock1 = dataframe[keys[i]] # obtain the price of two contract
			stock2 = dataframe[keys[j]]
			result = sm.tsa.stattools.coint(stock1, stock2) # get conintegration
			pvalue = result[1] # get the pvalue
			pvalue_matrix[i, j] = pvalue
			if pvalue < critial_level: # if p-value less than the critical level
				pairs.append((keys[i], keys[j], pvalue)) # record the contract with that p-value
			else:
				pairs1.append((keys[i], keys[j], pvalue))
	return pvalue_matrix, pairs

pvalue_matrix, pairs = find_cointegrated_pairs(all_data); 
p = pd.DataFrame(pairs)

p.to_csv('training_p_sorted.csv', index_label='id',header= ["S1","S2","p-value"])

############################################################################################################################

length_data = len(all_data)
length_train_data = int(0.80*length_data)	# training data is 80% of all data
						# test data is 20% of all data

train_data = all_data.loc[all_data.index[0:length_train_data]]
test_data = all_data.loc[all_data.index[length_train_data+1:]]


train_data.to_csv('training_data.csv')
test_data.to_csv('testing_data.csv')

# define functions
def load_data():
# set the working directory
    import os
    #os.getcwd() # this is to check the current working directory
    #os.chdir("D://EPAT//09 FP//")
    all_contracts = pd.read_csv('training_data.csv',index_col='date',parse_dates=True)
    p_sorted = pd.read_csv('training_p_sorted2.csv',index_col='id',parse_dates=False)

    return all_contracts,p_sorted


def hurst(ts):
    """Returns the Hurst Exponent of the time series vector ts"""
    # Create the range of lag values
    lags = range(2, 100)
 
    # Calculate the array of the variances of the lagged differences
    tau = [sqrt(std(subtract(ts[lag:], ts[:-lag]))) for lag in lags]
 
    # Use a linear fit to estimate the Hurst Exponent
    poly = polyfit(log(lags), log(tau), 1)
 
    # Return the Hurst exponent from the polyfit output
    return poly[0]*2.0


###############################################################################
##### ADF TEST
###############################################################################
def adf_test(x, y):
    df = pd.DataFrame({'y':y,'x':x})
    est = sm.OLS(df.y, df.x)
    est = est.fit()
    df['hr'] = -est.params[0]
    df['spread'] = df.y + (df.x * df.hr)
    
    cadf = ts.adfuller(df.spread)   
    return cadf[1] 

 
def half_life(spread):
    spread_lag = spread.shift(1)
    spread_lag.iloc[0] = spread_lag.iloc[1]
    
    spread_ret = spread - spread_lag
    spread_ret.iloc[0] = spread_ret.iloc[1]
    
    spread_lag2 = sm.add_constant(spread_lag)
     
    model = sm.OLS(spread_ret,spread_lag2)
    res = model.fit()
    halflife = int(round(-np.log(2) / res.params[1],0))
 
    if halflife <= 0:
        halflife = 1
    return halflife
    

def KalmanFilterAverage(x):
    # Construct a Kalman filter
    from pykalman import KalmanFilter
    kf = KalmanFilter(transition_matrices = [1],
                      observation_matrices = [1],
                      initial_state_mean = 0,
                      initial_state_covariance = 1,
                      observation_covariance=1,
                      transition_covariance=.01)

    # Use the observed values of the price to get a rolling mean
    state_means, _ = kf.filter(x.values)
    state_means = pd.Series(state_means.flatten(), index=x.index)
    return state_means

#  Kalman filter regression
def KalmanFilterRegression(x,y):

    delta = 1e-3
    trans_cov = delta / (1 - delta) * np.eye(2) # How much random walk wiggles
    obs_mat = np.expand_dims(np.vstack([[x], [np.ones(len(x))]]).T, axis=1)
    
    kf = KalmanFilter(n_dim_obs=1, n_dim_state=2, # y is 1-dimensional, (alpha, beta) is 2-dimensional
                      initial_state_mean=[0,0],
                      initial_state_covariance=np.ones((2, 2)),
                      transition_matrices=np.eye(2),
                      observation_matrices=obs_mat,
                      observation_covariance=2,
                      transition_covariance=trans_cov)
    
    # Use the observations y to get running estimates and errors for the state parameters
    state_means, state_covs = kf.filter(y.values)
    return state_means    

#############################################################################################

def backtest(s1, s2, x, y ):      
    #############################################################    
    #run regression to find hedge ratio
    #and then create spread series
    df1 = pd.DataFrame({'y':y,'x':x})
    state_means = KalmanFilterRegression(KalmanFilterAverage(x),KalmanFilterAverage(y))
    
    df1['hr'] = - state_means[:,0]
    df1['spread'] = df1.y + (df1.x * df1.hr)

    ##############################################################
    halflife = half_life(df1['spread'])

    ##########################################################

    meanSpread = df1.spread.rolling(window=halflife).mean()
    stdSpread = df1.spread.rolling(window=halflife).std()
    
        
    df1['zScore'] = (df1.spread-meanSpread)/stdSpread

    ##############################################################

    entryZscore = 2 
    exitZscore = 0
    
    #set up num units long             
    df1['long entry'] = ((df1.zScore < - entryZscore) & ( df1.zScore.shift(1) > - entryZscore))
    df1['long exit'] = ((df1.zScore > - exitZscore) & (df1.zScore.shift(1) < - exitZscore)) 
    df1['num units long'] = np.nan 
    df1.loc[df1['long entry'],'num units long'] = 1 
    df1.loc[df1['long exit'],'num units long'] = 0
    df1['num units long'][0] = 0 
    df1['num units long'] = df1['num units long'].fillna(method='pad')
    
    #set up num units short 
    df1['short entry'] = ((df1.zScore >  entryZscore) & ( df1.zScore.shift(1) < entryZscore))
    df1['short exit'] = ((df1.zScore < exitZscore) & (df1.zScore.shift(1) > exitZscore))
    df1.loc[df1['short entry'],'num units short'] = -1
    df1.loc[df1['short exit'],'num units short'] = 0
    df1['num units short'][0] = 0
    df1['num units short'] = df1['num units short'].fillna(method='pad')
    
    df1['numUnits'] = df1['num units long'] + df1['num units short']
    df1['spread pct ch'] = (df1['spread'] - df1['spread'].shift(1)) / ((df1['x'] * abs(df1['hr'])) + df1['y'])
    df1['port rets'] = df1['spread pct ch'] * df1['numUnits'].shift(1)
    
    df1['cum rets'] = df1['port rets'].cumsum()
    df1['cum rets'] = df1['cum rets'] + 1
    
    try:
        sharpe = ((df1['port rets'].mean() / df1['port rets'].std()) * sqrt(252)) 
    except ZeroDivisionError:
        sharpe = 0.0

    #############################################################
    return df1['cum rets'], sharpe

#  load Training data
all_contracts, p_sorted = load_data()

all_contracts.tail(3)

p_sorted.tail(3)

# find the potential pairs for out-sample testing under the condition that sharp ratio > 0.5 and CAGR > 10.5%
list_sect = []
ret = pd.DataFrame() 
for i in np.arange(p_sorted.shape[0]):
   

    #print("The total # of testing is: ", p_sorted.shape[0], " Current: ", i)
    s1 = p_sorted.iloc[i][1]
    s2 = p_sorted.iloc[i][0]
    
    name = s1 + "-" + s2

    x = all_contracts[s1]
    y = all_contracts[s2]
    
    tmp, sharpe = backtest(s1, s2, x, y) 
    if sharpe > 0.5 and tmp.values[-1] > 1.105:
        ret[name] = tmp.values
        list_sect.append((s1,s2))


# list the potential pairs for out-sample testing
list_sect


# in-sample testing results
ret.tail(3)

# show the results of in sample testing
get_ipython().run_line_magic('matplotlib', 'tk')
ret.iloc[0] = 1
ret.index = all_contracts.index
ret.plot(figsize=(15,7),grid=True)

# calculate the performance
perf = ret.calc_stats() 
perf.display()
#perf.to_csv(sep=',',path="train_perfer.csv")

# plot the maxinum drawndown of each pair
ffn.to_drawdown_series(ret).plot(figsize=(15,7),grid=True)  

# In sample back testing of portfolio
port = ret.mean(axis=1)
port.plot(figsize=(15,7),grid=True)
perf = port.calc_stats() 
perf.stats


# In sample back testing of portfolio maxinum drawndown
ffn.to_drawdown_series(port).plot(figsize=(15,7),grid=True) 


## OUT　SAMPLE BACKＴＥＳＩＮＧ

testing_data = pd.read_csv('testing_data.csv',index_col='date', parse_dates=True)
test_ret = pd.DataFrame()
for i in np.arange(len(list_sect)):
    

    # print("The total # of testing is: ", p_sorted.shape[0], " Current: ", i)
    s1 = list_sect[i][1]
    s2 = list_sect[i][0]
    
    name = s1 + "-" + s2

    x = testing_data[s1]
    y = testing_data[s2]
    
    
    test_ret[name], sharpe = backtest(s1, s2, x, y) 
testing_data.tail(3)

test_ret.iloc[0] = 1
test_ret.tail(3)
test_ret.shape
test_ret.index

test_ret.plot()

# Out sample back testing of portfolio

port = test_ret.mean(axis=1)
port.plot(figsize=(15,7),grid=True)
perf = port.calc_stats() 
perf.stats

ffn.to_drawdown_series(port).plot(figsize=(15,7),grid=True) 

