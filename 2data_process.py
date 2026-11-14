
import pandas as pd
import ast
import scipy.stats as stats

# ============= Utilities =============
def concat_process(EXCEL, model):
    excel = EXCEL.copy()
    excel['Task'] = excel['Image Path'].str.split('\\').str.get(1).str.split('_1').str.get(0)
    excel['Task'] = excel['Task'] + '_1'
    excel = excel.drop(columns=['Image Path','AI Answer'])
    excel['Model'] = model
    # Convert list strings into lists
    excel['Code'] = excel['Code'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)
    # Explode the lists
    result_df = excel.explode('Code')
    return result_df

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

def compute_human_code():
    # Get participant codes
    filtered_metrics = pd.read_csv('data/filtered_metrics.csv')

    df = filtered_metrics[filtered_metrics['Event_type'] == 'Fixation'].reset_index(drop=True)
    df.loc[df['FixationPointX'] < 0, 'FixationPointX'] = 0
    df.loc[df['FixationPointX'] > 1, 'FixationPointX'] = 1
    df.loc[df['FixationPointY'] < 0, 'FixationPointY'] = 0
    df.loc[df['FixationPointY'] > 1, 'FixationPointY'] = 1

    row_list = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
    col_list = [1, 2, 3, 4, 5, 6, 7, 8]

    for i in range(len(df)):
        fixation_x = df.loc[i, 'FixationPointX']
        fixation_y = df.loc[i, 'FixationPointY']

        if fixation_y == 1:
            grid_row = 'H'
        else:
            grid_row = row_list[int(fixation_y // (1 / 8))]
        if fixation_x == 1:
            grid_col = 8
        else:
            grid_col = col_list[int(fixation_x // (1 / 8))]

        df.loc[i, 'Code'] = grid_row + str(grid_col)

    # Add correctness data
    ans = pd.read_excel('data/答题情况.xlsx')
    ans = ans[ans['任务模式'] == '自然交互']
    ans.columns = ['Participant', 'Task', 'IsCorrect', '_']
    ans.drop(columns='_', inplace=True)
    d2 = df.merge(ans, on=['Participant', 'Task'], how='left')

    d2.to_csv('output/human_code.csv', index=False)
    print('【INFO】output/human_code.csv saved.')

def concat_ai_data():
    # Merge data
    EXCEL_GPT = pd.read_excel('test_result/test_result_gpt5.xlsx')
    EXCEL_GEMINI = pd.read_excel('test_result/test_result_gemini3pro.xlsx')
    EXCEL_GLM = pd.read_excel('test_result/test_result_glm.xlsx')
    EXCEL_HUNYUAN = pd.read_excel('test_result/test_result_hunyuan.xlsx')
    EXCEL_QWEN = pd.read_excel('test_result/test_result_qwen.xlsx')
    df_gpt = concat_process(EXCEL_GPT, 'gpt-5')
    df_gemini = concat_process(EXCEL_GEMINI, 'gemini-3-pro')
    df_glm = concat_process(EXCEL_GLM, 'glm-4.6v')
    df_hunyuan = concat_process(EXCEL_HUNYUAN, 'hunyuan-t1-vision-20250916')
    df_qwen = concat_process(EXCEL_QWEN, 'qwen3-vl-8b-thinking')

    data = pd.concat([df_gpt, df_gemini, df_glm, df_hunyuan, df_qwen], axis=0)
    data = data[data['Run']<=30]    # Keep the first 30 runs
    data['Index'] = data.groupby(['Model', 'Task', 'Run']).cumcount() + 1
    data.rename(columns={'Is Correct': 'IsCorrect'}, inplace=True)
    data.to_csv('output/ai_code.csv', index=False)
    print('【INFO】output/ai_code.csv saved.')

def concat_all():
    # Merge AI and human tables
    ai_code = pd.read_csv('output/ai_code.csv')
    human_code = pd.read_csv('output/human_code.csv')

    ai_code.rename(columns={'Model': 'Participant'}, inplace=True)
    human_code = human_code[['Participant', 'Code', 'IsCorrect', 'Task', 'EventIndex']].drop_duplicates().reset_index(drop=True)
    human_code.rename(columns={'Participant': 'Run', 'EventIndex': 'Index'}, inplace=True)
    human_code['Participant'] = 'human'
    all_code = pd.concat([ai_code, human_code])
    all_code.rename(columns={'Participant': 'Respondent'}, inplace=True)

    # Get the corresponding semantic AOI codes
    grid2semantic = pd.read_csv('data/grid2semantic.csv')
    grid2semantic = grid2semantic.drop(columns='FID')

    grid2semantic = grid2semantic.rename(columns={'rank_attri': 'rank_attribute_1', 'iden_attri': 'identify_attribute_1',
                          'deli_attri': 'delineate_attribute_1',
                          'comp_attri': 'compare_attribute_1', 'asso_attri': 'associate_attribute_1',
                          'rank_space': 'rank_space_1', 'iden_space': 'identify_space_1',
                          'deli_space': 'delineate_space_1', 'comp_space': 'compare_space_1',
                          'asso_space': 'associate_space_1', 'rank_time': 'rank_time_1', 'iden_time': 'identify_time_1',
                          'deli_time': 'delineate_time_1', 'comp_time': 'compare_time_1',
                          'asso_time': 'associate_time_1',
                          'GridAoi': 'Code'
                          })
    grid2semantic = pd.melt(grid2semantic, id_vars=['Code'], var_name='Task', value_name='SemanticCode')
    map_val = {'Legend': 'L', 'Map': 'M', 'Key_legend': 'K', 'Answer': 'A', 'Target_area': 'T', 'Question': 'Q'}
    grid2semantic['SemanticCode'] = grid2semantic['SemanticCode'].map(map_val)
    all_code = all_code.merge(grid2semantic, on=['Code', 'Task'], how='left')

    all_code.to_csv('output/all_code.csv', index=False)
    print('【INFO】output/all_code.csv saved.')

def compute_traj(input_data):
    # Combine individual codes into trajectories
    data = input_data.copy()
    data2 = data.groupby(['Respondent', 'Task', 'Run', 'IsCorrect'])['Code'].apply(list).reset_index()
    data2.rename(columns={'Code': 'Trajectory'}, inplace=True)
    data2['SemanticTraj'] = data.groupby(['Respondent', 'Task', 'Run', 'IsCorrect'])['SemanticCode'].apply(list).reset_index()['SemanticCode']
    return data2

def compute_stats(input_data):
    # Compute statistical features
    data = input_data.copy()
    # Code length for each run
    df_codelen = data.groupby(['Respondent', 'Task','Run'])['Code'].agg(CodeLen='count').reset_index()
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
    common_info = data.groupby(['Respondent', 'Task'])['Code'].apply(get_metrics).unstack().reset_index()

    #### Calculate unique AOI metrics
    # Count unique AOIs for each task/model
    unique_info = data.groupby(['Respondent', 'Task'])['Code'].agg(UniqueTypes='nunique').reset_index()
    # Count unique AOIs per task/model/run, then average over runs for each task/model
    u2 = data.groupby(['Respondent', 'Task', 'Run'])['Code'].agg(UniqueTypes='nunique').reset_index()
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
    df_spss = data.groupby(['Respondent', 'Task','Run'])['Code'].agg(CodeLen='count',
                                                                         UniqueTypes='nunique').reset_index()
    # Correctness for each run
    df_correct = data[['Run','IsCorrect','Task','Respondent']].drop_duplicates().reset_index(drop=True)
    df_spss = df_spss.merge(df_correct, on=['Respondent', 'Task', 'Run'], how='left')
    df_spss['RespondentTask'] = df_spss['Respondent'] + '_' + df_spss['Task']
    return df_spss

if __name__ == '__main__':
    # # Generate and save all_code
    # concat_ai_data()        # Combine AI results into one table
    # compute_human_code()    # Combine participant results into one table
    # concat_all()            # Merge AI and human tables, and add semantic codes

    all_code = pd.read_csv('output/all_code.csv')

    # Combine trajectories for each respondent/task/run
    all_traj = compute_traj(all_code)
    all_traj.to_csv('output/all_traj.csv', index=False)
    print('【INFO】output/all_traj.csv saved.')

    # -------------------grid AOI (semantic code) section----------------------

    # # Calculate basic statistical features (numeric version)
    # all_report = compute_stats(all_code)
    # all_report.to_csv('output/all_report.csv', index=False)
    # print('【INFO】output/all_report.csv saved.')

    # # Prepare data for SPSS statistical tests and plotting
    # df_spss = compute_spss(all_code)
    # df_spss.to_csv('output/report_spss.csv', index=False)
    # print('【INFO】output/report_spss.csv saved.')
    #
    # df_spss = pd.read_csv('output/report_spss.csv')

    # # Split the SPSS table into pairwise comparison tables
    # res1 = df_spss['Respondent'].unique().tolist()
    # res2 = res1.copy()
    # l = len(df_spss['Respondent'].unique())
    # for i in range(l):
    #     col1 = res1[i]
    #     res2.pop(0)
    #     for p in res2:
    #         col2 = p
    #         df = df_spss[df_spss['Respondent'].isin([col1, col2])]
    #         df.to_csv(f'output/report_spss/spss_{col1}_{col2}.csv', index=False)
    #         print(f'【INFO】output/report_spss/spss_{col1}_{col2}.csv saved.')
    #     i += 1

    # # Normality test
    # nomality_test(df_spss, col='CodeLen')
    # nomality_test(df_spss, col='UniqueTypes')
    # nomality_test(df_spss, col='IsCorrect')