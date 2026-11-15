
import pandas as pd
import ast
import scipy.stats as stats

# ============= Utilities =============
def get_metrics(group):
    counts = group.value_counts()
    most_common_ratio = round(counts.max() / counts.sum(), 4)
    return pd.Series({
        'MostCommon1Ratio': most_common_ratio,
        'MostCommon3Aois': counts.index[0:3].tolist() # The most frequent AOIs
    })

def nomality_test(df_spss, col):
    # Normality test
    p = stats.shapiro(df_spss[col]).pvalue
    if p > 0.05:
        print(f'{col} column follows a normal distribution')
    else:
        print(f'{col} column does not follow a normal distribution')

# ============= Main operations =============
def compute_traj(input_data):
    # Combine individual codes into trajectories
    data = input_data.copy()
    data2 = data.groupby(['Respondent', 'Task', 'Run', 'IsCorrect'])['GridAoi'].apply(list).reset_index()
    data2.rename(columns={'GridAoi': 'Trajectory'}, inplace=True)
    data2['SemanticTraj'] = data.groupby(['Respondent', 'Task', 'Run', 'IsCorrect'])['SemanticCode'].apply(list).reset_index()['SemanticCode']
    return data2

def compute_stats(input_data):
    # Compute statistical features
    data = input_data.copy()
    # Code length for each run
    df_codelen = data.groupby(['Respondent', 'Task','Run'])['GridAoi'].agg(CodeLen='count').reset_index()
    data = data.merge(df_codelen, on=['Respondent','Task','Run'], how='left')

    #### Mean/median/quantiles/minimum and maximum/standard deviation of code length:
    stats = data[['Respondent','Task','CodeLen']].groupby(['Respondent','Task'])['CodeLen'].agg(
        Mean='mean',
        Median='median',
        Q25=lambda x: x.quantile(0.25),
        Q75=lambda x: x.quantile(0.75),
        Min='min',
        Max='max',
        Std='std'
    ).reset_index()

    #### Calculate the proportion of the most common AOI (Most Common AOI %)
    common_info = data.groupby(['Respondent', 'Task'])['GridAoi'].apply(get_metrics).unstack().reset_index()

    #### Calculate unique AOI metrics
    # Count unique AOIs for each task/model
    unique_info = data.groupby(['Respondent', 'Task'])['GridAoi'].agg(UniqueTypes='nunique').reset_index()
    # Count unique AOIs per task/model/run, then average over runs for each task/model
    u2 = data.groupby(['Respondent', 'Task', 'Run'])['GridAoi'].agg(UniqueTypes='nunique').reset_index()
    u2 = u2.groupby(['Respondent','Task'])['UniqueTypes'].agg(AvgUnique = 'mean').round(2).reset_index()
    unique_info = unique_info.merge(u2, on=['Respondent','Task'], how='left')

    #### Calculate accuracy
    correct_info = data[['Run','IsCorrect','Task','Respondent']].drop_duplicates().reset_index(drop=True)
    correct_info = correct_info.groupby(['Respondent', 'Task'])['IsCorrect'].mean().round(4).reset_index()

    final_report = pd.merge(stats, common_info, on=['Respondent','Task'], how='left')
    final_report = pd.merge(final_report, unique_info, on=['Respondent','Task'], how='left')
    final_report = pd.merge(final_report, correct_info, on=['Respondent','Task'], how='left')
    final_report['Mean'] = final_report['Mean'].round(2)
    final_report['Std'] = final_report['Std'].round(2)

    return final_report

def compute_spss(input_data):
    # Prepare data for SPSS statistical tests
    data = input_data.copy()
    # Code length and number of unique AOIs for each run
    df_spss = data.groupby(['Respondent', 'Task','Run'])['GridAoi'].agg(CodeLen='count',
                                                                         UniqueTypes='nunique').reset_index()
    # Correctness for each run
    df_correct = data[['Run','IsCorrect','Task','Respondent']].drop_duplicates().reset_index(drop=True)
    df_spss = df_spss.merge(df_correct, on=['Respondent', 'Task', 'Run'], how='left')
    df_spss['RespondentTask'] = df_spss['Respondent'] + '_' + df_spss['Task']
    return df_spss

if __name__ == '__main__':
    all_code = pd.read_csv('data/all_code.csv')

    # Combine trajectories for each respondent/task/run
    all_traj = compute_traj(all_code)
    all_traj.to_csv('output/all_traj.csv', index=False)
    print('【INFO】output/all_traj.csv saved.')

    # -------------------grid AOI section----------------------

    # Calculate basic statistical features (numeric version)
    all_report = compute_stats(all_code)
    all_report.to_csv('output/all_report.csv', index=False)
    print('【INFO】output/all_report.csv saved.')

    # Prepare data for SPSS statistical tests and plotting
    df_spss = compute_spss(all_code)
    df_spss.to_csv('output/report_spss.csv', index=False)
    print('【INFO】output/report_spss.csv saved.')

    df_spss = pd.read_csv('output/report_spss.csv')

    # Split the SPSS table into pairwise comparison tables
    res1 = df_spss['Respondent'].unique().tolist()
    res2 = res1.copy()
    l = len(df_spss['Respondent'].unique())
    for i in range(l):
        col1 = res1[i]
        res2.pop(0)
        for p in res2:
            col2 = p
            df = df_spss[df_spss['Respondent'].isin([col1, col2])]
            df.to_csv(f'output/report_spss/spss_{col1}_{col2}.csv', index=False)
            print(f'【INFO】output/report_spss/spss_{col1}_{col2}.csv saved.')
        i += 1

    # Normality test
    nomality_test(df_spss, col='CodeLen')
    nomality_test(df_spss, col='UniqueTypes')
    nomality_test(df_spss, col='IsCorrect')