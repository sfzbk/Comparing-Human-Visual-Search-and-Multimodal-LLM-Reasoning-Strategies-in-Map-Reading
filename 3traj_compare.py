import os                                               # Prevent forrtl: error (200) instead of KeyboardInterrupt,
os.environ['FOR_DISABLE_CONSOLE_CTRL_HANDLER'] = '1'    # These two lines must be set before importing the problematic packages
import pandas as pd
import tools.algorithms as alg
import sys

def compare_model_human():
    ## Compare each model run with all human participants for the same task
    # 1. Extract all model trajectories and human trajectories separately
    all_traj = pd.read_csv('output/all_traj.csv')
    all_traj['Trajectory'] = all_traj['Trajectory'].apply(eval)
    df_human = all_traj[all_traj['Respondent'] == 'human'].reset_index(drop=True)
    df_model = all_traj[all_traj['Respondent'] != 'human'].reset_index(drop=True)

    # 2. For each model run, compare its trajectory with those of all participants in the same task and obtain the results
    global temp_path
    temp_path = "output/traj_compare_temp.csv"
    global temp_df
    if os.path.exists(temp_path):
        # If the temp file exists, resume from the saved temp file
        temp_df = pd.read_csv(temp_path).drop_duplicates().reset_index(drop=True)
    else:
        # Create a new one from scratch
        temp_df = pd.DataFrame(columns=['Model', 'Task', 'Run', 'Participant', 'Levenshtein', 'Frdist',
                                       'MultiVecShape', 'MultiVecLen', 'MultiVecPosi', 'MultiVecDirec'])


    for model in df_model['Respondent'].unique():
        #If all records for the current model are complete, skip the entire model
        if len(temp_df[temp_df['Model'] == model]) == (15*30*49):
            print(f'【WARN】{model} already finished. Skipped.')
            continue

        for task in df_model['Task'].unique():
            # If all records for the current model and task are complete, skip the entire task
            if len(temp_df[(temp_df['Model'] == model) & (temp_df['Task'] == task)]) == (30*49):
                print(f'【WARN】{model} -> {task} already finished. Skipped.')
                continue

            for run in df_model['Run'].unique():
                # If all records for the current model, task, and run are complete, skip the entire run
                # The run values in the result are numbers, whereas those in the full DataFrame are strings!
                if len(temp_df[(temp_df['Model'] == model) & (temp_df['Task'] == task) & (temp_df['Run'] == int(run))]) == 49:
                    print(f'【WARN】{model} -> {task} -> {run} already finished. Skipped.')
                    continue

                for participant in df_human['Run'].unique():
                    traj1 =df_model[(df_model['Respondent']==model)&
                                    (df_model['Task']==task)&
                                    (df_model['Run']==run)]['Trajectory'].tolist()[0]
                    traj2 =df_human[(df_human['Task']==task)&
                                    (df_human['Run']==participant)]['Trajectory'].tolist()[0]

                    leven = alg.lv_dis(traj1, traj2)
                    frdist = alg.frdist_dis(traj1,traj2)
                    multi = alg.multi_match(traj1,traj2)
                    multi_vec_shape = multi[0]
                    multi_vec_len = multi[1]
                    multi_vec_posi = multi[2]
                    multi_vec_direc = multi[3]

                    temp_df.loc[len(temp_df)] = [model,task,run,participant,leven,frdist,
                                               multi_vec_shape,multi_vec_len,multi_vec_posi,multi_vec_direc]
                print(f'【INFO】model:{model} task:{task} run:{run} finished.')
                temp_df.to_csv(temp_path,index=False)
                print(f'【INFO】{temp_path} saved.')

    print('【INFO】All finished.')
    result = temp_df
    result.to_csv('output/traj_compare.csv', index=False)
    print('【INFO】output/traj_compare.csv saved.')

    # Delete the temp file
    os.remove(temp_path)
    print('【INFO】temp file deleted.')

def compare_human():
    ## Compare trajectory distances between all pairs of humans for the same task
    # 1. Extract all human trajectories
    all_traj = pd.read_csv('output/all_traj.csv')
    all_traj['Trajectory'] = all_traj['Trajectory'].apply(eval)
    df_human = all_traj[all_traj['Respondent'] == 'human'].reset_index(drop=True)

    result = pd.DataFrame(columns=['Task', 'Participant1', 'Participant2', 'Levenshtein', 'Frdist',
                                       'MultiVecShape', 'MultiVecLen', 'MultiVecPosi', 'MultiVecDirec'])
    #
    for task in df_human['Task'].unique():
        par1_list = df_human['Run'].unique().tolist()
        par2_list = df_human['Run'].unique().tolist()
        for participant1 in par1_list[:-1]:
            par2_list.remove(participant1) if participant1 in par2_list else None
            for participant2 in par2_list:
                traj1 = df_human[(df_human['Task']==task)&(df_human['Run']==participant1)]['Trajectory'].tolist()[0]
                traj2 = df_human[(df_human['Task']==task)&(df_human['Run']==participant2)]['Trajectory'].tolist()[0]

                leven = alg.lv_dis(traj1, traj2)
                frdist = alg.frdist_dis(traj1, traj2)
                multi = alg.multi_match(traj1, traj2)
                multi_vec_shape = multi[0]
                multi_vec_len = multi[1]
                multi_vec_posi = multi[2]
                multi_vec_direc = multi[3]

                result.loc[len(result)] = [task, participant1, participant2, leven, frdist,
                                           multi_vec_shape, multi_vec_len, multi_vec_posi, multi_vec_direc]
                print(f'【INFO】{task} {participant1} {participant2} finished.')
                result.to_csv('output/traj_compare_human_temp.csv', index=False)
                print(f'【INFO】output/traj_compare_human_temp.csv saved.')

    result.to_csv('output/traj_compare_human.csv', index=False)
    print('【INFO】output/traj_compare_human.csv saved.')

def compare_ai():
    ## Compare trajectory distances between all pairs of AI trajectories for the same task
    # 1. Extract all AI trajectories
    all_traj = pd.read_csv('output/all_traj.csv')
    all_traj['Trajectory'] = all_traj['Trajectory'].apply(eval) # Convert the string representation of a list back into a list
    df_ai = all_traj[all_traj['Respondent'] != 'human'].reset_index(drop=True)
    df_ai['Model_Run'] = df_ai['Respondent'] + '_' + df_ai['Run']

    global temp_path    # Use a global variable so it can be saved during error handling
    temp_path = 'output/traj_compare_ai_temp.csv'
    global temp_df

    if os.path.exists(temp_path):
        # If the temp file exists, resume from the saved temp file
        temp_df = pd.read_csv(temp_path).drop_duplicates().reset_index(drop=True)
    else:
        # Create a new one from scratch
        temp_df = pd.DataFrame(columns=['Task', 'Model_Run1', 'Model_Run2', 'Levenshtein', 'Frdist',
                                       'MultiVecShape', 'MultiVecLen', 'MultiVecPosi', 'MultiVecDirec'])

    # Compare all pairs of models and runs within the same task
    for task in df_ai['Task'].unique():
        #If all records for the current task are complete, skip the entire task
        if len(temp_df[temp_df['Task'] == task]) == (150*74+75):  # The total number of records for one task should be 149+148+...+2+1 = 150*74+75 = 11175
            print(f'【WARN】{task} already finished. Skipped.')
            continue

        model_run_1_list = df_ai['Model_Run'].unique().tolist()
        model_run_2_list = df_ai['Model_Run'].unique().tolist()
        for model_run_1 in model_run_1_list[:-1]:
            # If the last element of model_run_2_list has already been recorded for the current task and model_run_1,
            # consider the current model_run_1 complete and skip it entirely
            if model_run_2_list[-1] in temp_df[(temp_df['Task']==task)&(temp_df['Model_Run1']==model_run_1)]['Model_Run2'].tolist():  #
                print(f'【WARN】{task} -> {model_run_1} already finished. Skipped.')
                model_run_2_list.remove(model_run_1) if model_run_1 in model_run_2_list else None
                continue

            model_run_2_list.remove(model_run_1) if model_run_1 in model_run_2_list else None
            for model_run_2 in model_run_2_list:
                # If the current model_run_2 is already recorded for this task and model_run_1, skip it
                if model_run_2 in temp_df[(temp_df['Task'] == task) & (temp_df['Model_Run1'] == model_run_1)]['Model_Run2'].tolist():
                    print(f'【WARN】{task} -> {model_run_1} -> {model_run_2} already finished. Skipped.')
                    continue

                traj1 = df_ai[(df_ai['Task'] == task) & (df_ai['Model_Run'] == model_run_1)]['Trajectory'].tolist()[
                    0]
                traj2 = df_ai[(df_ai['Task'] == task) & (df_ai['Model_Run'] == model_run_2)]['Trajectory'].tolist()[
                    0]

                leven = alg.lv_dis(traj1, traj2)
                frdist = alg.frdist_dis(traj1, traj2)
                multi = alg.multi_match(traj1, traj2)
                multi_vec_shape = multi[0]
                multi_vec_len = multi[1]
                multi_vec_posi = multi[2]
                multi_vec_direc = multi[3]

                temp_df.loc[len(temp_df)] = [task, model_run_1, model_run_2, leven, frdist,
                                           multi_vec_shape, multi_vec_len, multi_vec_posi, multi_vec_direc]
                print(f'【INFO】{task} {model_run_1} {model_run_2} finished.')

            temp_df.to_csv(temp_path, index=False)
            print(f'【INFO】{temp_path} saved.')

    print('【INFO】All finished.')
    result = temp_df
    result.to_csv('output/traj_compare_ai.csv', index=False)
    print('【INFO】output/traj_compare_ai.csv saved.')

    # Delete the temp file
    os.remove(temp_path)
    print('【INFO】temp file deleted.')



if '__main__' == __name__:
    temp_path = ''
    temp_df = pd.DataFrame()

    try:
        # compare_model_human()
        # compare_human()
        compare_ai()

    except KeyboardInterrupt:
        # Catch KeyboardInterrupt at the outermost level to prevent accidental program restarts
        print('【WARN】KeyboardInterrupt.')
        if not temp_df.empty:
            temp_df.to_csv(temp_path, index=False)
            print(f'【INFO】{temp_path} saved.')
        sys.exit(0)  # Raises SystemExit