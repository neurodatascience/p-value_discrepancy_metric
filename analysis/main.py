import numpy as np
import pandas as pd
from scipy import stats
from pathlib import Path
from pvalue_metric import metric
from itertools import combinations


group_column = "dx_group" ##REMOVE IT FROM HERE there are copies in helper.py and main.py
# Hypothesis_test:callable=stats.ttest_ind,

def pvalue_test_for_all_volumes(path:Path,
                        regions:list,
                        groups:list,
                        Hypothesis_test_func,
                        n_bootstrap:int,
                        n_permutation:int,
                        **kwargs) -> pd.DataFrame:
    
    """
    This function is  calculate p disparity metric for all volumes in Sokolowski et al. 2023 paper

    Inputs:
        path: path to the csv file or pandas dataframe
        regions: list of brian regions that we are intrerested in
        groups: list of target groups that we are intrerested in 
        (there is three groups in the paper: PD-MCI, PD-non-MCI, HC)
        Hypothesis_test_func: Hypothesis testing function
        n_bootstrap: number of bootstrap iteration
        n_permutation: number of permutation iterations
        **kwargs: keyword arguments for the Hypothesis testing function

    Output:
        pandas dataframe of p disparity metric for all volumes
    """

    try:
        assert len(groups) == 2
    except AssertionError:
        print("Only two groups are allowed for now")
        raise

    data = pd.read_csv(path)
    results = np.zeros((len(regions),)) 
       
    for (i, region) in enumerate(regions):

        data_columns = []
        for group in groups:
            data_columns.append(data[region].loc[data[group_column] == group])
        data_columns = tuple(data_columns)
    
        tests_outputs, _ = metric.pvalue_test(data_columns, Hypothesis_test_func, n_bootstrap, n_permutation, **kwargs)
        results[i], _, _ = tests_outputs
        # pandas.Series(data=None, index=None, dtype=None, name=None, copy=None, fastpath=False)

    return pd.Series(results, index=regions, name= groups[0] + "_vs_" + groups[1])    #maybe change name  

def generate_pairs_indices(data):
    """
    This function generates all possible pairs of indices for a given list
    
    Inputs:
        data: list of data
    
    Output:
        pairs_elements: list of all possible pairs of indices
    """
    pairs_elements = []
    for i, j in combinations(data, 2):
        pairs_elements.append((i, j))

    return pairs_elements

if __name__ == "__main__":
 
    PARENT_DIR = Path(__file__).resolve().parents[1]
    Data_DIR = PARENT_DIR / "study_files/roi_data.csv"

    df = pd.read_csv(Data_DIR)
    target_groups = ["PD-non-MCI", "HC"]
    subject_group = "dx_group"
    ROIs = [
    "Thalamus", "Caudate", "Putamen", "Pallidum",
    "Hippocampus", "Amygdala","Accumbens-area"]
    target_columns = ["thickness_change"] + [region+"_change_pred" for region in ROIs]

    pairs = generate_pairs_indices(df[subject_group].unique())
    print(pairs)
    result = []
    for pair in pairs:

        result.append(pvalue_test_for_all_volumes(Data_DIR, target_columns, pair, stats.ttest_ind, 1000, 1000))

    all_result = pd.concat(result, axis=1)
    print(all_result)
    all_result.to_csv("pvalue_metric_1000bootstrap_1000permutation.csv",
                      header=True, index=True)
    
