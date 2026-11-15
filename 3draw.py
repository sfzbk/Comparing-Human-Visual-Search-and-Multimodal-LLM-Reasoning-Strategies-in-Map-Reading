
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

# Parameters manually transcribed from the report PDF
config = {
    'CodeLen':{
        'value_name': "Cohen's d",
        'value':{
            'human': [np.nan, 1.798, 1.939, 1.979, 1.85, 1.218],
            'gemini': [np.nan, np.nan, 0.509, 0.696, 0.221, 1.249],
            'glm': [np.nan, np.nan, np.nan, 0.061, 0.244, 1.541],
            'gpt': [np.nan, np.nan, np.nan, np.nan, 0.342, 1.717],
            'hunyuan': [np.nan, np.nan, np.nan, np.nan, np.nan, 1.322],
            'qwen': [np.nan, np.nan, np.nan, np.nan, np.nan, np.nan]
        },
        'annot':np.array(
            [['', '', '', '', '', ''],
             ['***', '', '', '', '', ''],
             ['***', '***', '', '', '', ''],
             ['***', '***', 'ns', '', '', ''],
             ['***', '***', '***', '***', '', ''],
             ['***', '***', '***', '***', '***', '']]
        )
    },
    'UniqueTypes':{
        'value_name': "Cohen's d",
        'value':{
            'human': [np.nan, 1.718, 1.947, 2.658, 1.657, 0.698],
            'gemini': [np.nan, np.nan,0.334, 1.018, 0.08, 0.944],
            'glm': [np.nan, np.nan, np.nan, 0.521, 0.218, 1.187],
            'gpt': [np.nan, np.nan, np.nan, np.nan, 0.733, 1.871],
            'hunyuan': [np.nan, np.nan, np.nan, np.nan, np.nan, 0.921],
            'qwen': [np.nan, np.nan, np.nan, np.nan, np.nan, np.nan]
        },
        'annot':np.array(
            [['', '', '', '', '', ''],
             ['***', '', '', '', '', ''],
             ['***', '***', '', '', '', ''],
             ['***', '***', '***', '', '', ''],
             ['***', '***', '***', '***', '', ''],
             ['***', '***', '***', '***', '***', '']]
        )
    },
    'IsCorrect':{
        'value_name': "Phi",
        'value':{
            'human': [np.nan, 0.322, 0.513, 0.495, 0.622, 0.616],
            'gemini': [np.nan, np.nan, 0.209, 0.189, 0.337, 0.33],
            'glm': [np.nan, np.nan, np.nan, 0.02, 0.133, 0.126],
            'gpt': [np.nan, np.nan, np.nan, np.nan, 0.153, 0.146],
            'hunyuan': [np.nan, np.nan, np.nan, np.nan, np.nan, 0.007],
            'qwen': [np.nan, np.nan, np.nan, np.nan, np.nan, np.nan]
        },
        'annot':np.array(
            [['', '', '', '', '', ''],
             ['***', '', '', '', '', ''],
             ['***', '***', '', '', '', ''],
             ['***', '***', 'ns', '', '', ''],
             ['***', '***', '***', '***', '', ''],
             ['***', '***', '***', '***', 'ns', '']]
        )
    }
}

respondent = ['human', 'gemini', 'glm', 'gpt',
              'hunyuan', 'qwen']
# --------------------------------------------------

def draw_violin():
    # Draw violin plots for the statistical metrics 'CodeLen' and 'UniqueTypes'

    data = pd.read_csv('output/report_spss.csv')
    # Rename models to shorter names
    rename_dict = {'human':'human','gemini-3-pro':'gemini','glm-4.6v':'glm','gpt-5':'gpt',
                         'hunyuan-t1-vision-20250916':'hunyuan','qwen3-vl-8b-thinking':'qwen'}
    data['Respondent'] = data['Respondent'].map(rename_dict)

    for x in ['CodeLen','UniqueTypes']:
        # Clear the canvas
        plt.cla()
        plt.clf()

        ax = sns.violinplot(
            x=x,
            y='Respondent',
            # hue='Respondent',
            # legend=False,
            order=respondent,
            palette="Set2",
            # inner='stick',
            cut=0,  # Trim portions extending beyond the data range
            data=data)
        # plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0)
        # Hide X-axis and Y-axis labels
        ax.set_xlabel("")
        ax.set_ylabel("")
        # Increase tick label font size
        ax.tick_params(axis='both', which='major', labelsize=20)

        plt.tight_layout()
        plt.savefig(f'output/pics/report_{x}.png', transparent=True, dpi=300)
        print(f'【INFO】output/pics/report_{x}.png saved.')

def draw_bar():
    # Draw violin plots for the statistical metrics 'CodeLen' and 'UniqueTypes'

    data = pd.read_csv('output/report_spss.csv')
    # Rename models to shorter names
    rename_dict = {'human':'human','gemini-3-pro':'gemini','glm-4.6v':'glm','gpt-5':'gpt',
                         'hunyuan-t1-vision-20250916':'hunyuan','qwen3-vl-8b-thinking':'qwen'}
    data['Respondent'] = data['Respondent'].map(rename_dict)

    x = 'IsCorrect'

    # Clear the canvas
    plt.cla()
    plt.clf()

    ax = sns.barplot(
        x=x,
        y='Respondent',
        # hue='Respondent',
        # legend=False,
        order=respondent,
        palette="Set2",
        # inner='stick',
        data=data)
    # plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0)
    # Hide X-axis and Y-axis labels
    ax.set_xlabel("")
    ax.set_ylabel("")
    # Increase tick label font size
    ax.tick_params(axis='both', which='major', labelsize=20)

    plt.tight_layout()
    plt.savefig(f'output/pics/report_{x}.png', transparent=True, dpi=300)
    print(f'【INFO】output/pics/report_{x}.png saved.')

def draw_p_heatmap(input):
    # Draw a heatmap of p-values

    value = config[input]['value']
    annot = config[input]['annot']

    # 2. Draw the p-value heatmap
    df = pd.DataFrame(data=value, index=respondent)

    # Clear the canvas
    plt.cla()
    plt.clf()
    # Draw the heatmap
    ax = sns.heatmap(df,
                annot=annot,
                fmt='',
                # cbar=False,   # Hide the colorbar
                linewidths=1,   # Internal grid lines
                linecolor='white',  # Internal grid lines
                cmap='YlGnBu')
    # Add a colorbar and label it
    cbar = ax.collections[0].colorbar
    cbar.set_label(config[input]['value_name'])

    plt.yticks(rotation=0)
    # Show the outer borders on all four sides
    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_linewidth(1)  # Set border width
        spine.set_edgecolor('black')  # Set border color

    plt.title(input)
    plt.tight_layout()
    plt.savefig(f'output/pics/p_{input}.png', dpi=300)
    print(f'【INFO】output/pics/p_{input}.png saved.')

def draw_heatmap(by='respondent'):

    def get_heatmap_data(df):
        heatmap_data = df[['GridAoi', 'X', 'Y']].pivot_table(index='Y', columns='X', aggfunc='count', fill_value=0)
        heatmap_data.columns = heatmap_data.columns.droplevel(0)
        ## Align to an 8x8 grid
        target_rows = list("ABCDEFGH")  # ['A', 'B', ..., 'H']
        target_cols = [str(i) for i in range(1, 9)]  # ['1', '2', ..., '8']
        # Enforce alignment (Reindex)
        # fill_value=0 ensures missing rows and columns are filled with 0 instead of NaN
        heatmap_data = heatmap_data.reindex(index=target_rows, columns=target_cols, fill_value=0)
        # Normalize data to the range 0-1 (divide by the maximum value in this plot)
        heatmap_data = heatmap_data / heatmap_data.values.max()
        return heatmap_data

    def draw_save(by, heatmap_data, note, respondent, vmax, vmin):
        # Clear the canvas
        plt.cla()
        plt.clf()
        ax = sns.heatmap(heatmap_data,
                         square=True,
                         annot=True,
                         fmt='.2f',
                         # cbar=False,  # Hide the colorbar
                         vmax=vmax, vmin=vmin,  # Colorbar minimum and maximum values
                         linewidths=1,  # Internal grid lines
                         linecolor='white',  # Internal grid lines
                         cmap='YlGnBu')
        # Hide X-axis and Y-axis labels
        ax.set_xlabel("")
        ax.set_ylabel("")
        plt.yticks(rotation=0)
        plt.title(f'{note}_{respondent}')
        plt.tight_layout()
        plt.savefig(f'output/pics/heatmap/by_{by}/{note}_{respondent}.png', dpi=300)
        print(f'【INFO】output/pics/heatmap/by_{by}/{note}_{respondent}.png saved.')


    data = pd.read_csv('data/all_code.csv')
    # Rename models to shorter names
    rename_dict = {'human':'human','gemini-3-pro':'gemini','glm-4.6v':'glm','gpt-5':'gpt',
                         'hunyuan-t1-vision-20250916':'hunyuan','qwen3-vl-8b-thinking':'qwen'}
    data['Respondent'] = data['Respondent'].map(rename_dict)

    data['Y'] = data['GridAoi'].str[0]
    data['X'] = data['GridAoi'].str[1]

    # Draw heatmaps for each model and task, and for all humans for each task
    if by == 'respondent_task':
        # Collect all heatmap_data to determine the minimum and maximum color values
        # Plot models separately using the overall range across all models
        heatmap_data_list = []
        for task in data['Task'].unique():
            # Draw a heatmap for each model under this task
            models = data['Respondent'].unique().tolist()
            models.remove('human')
            for respondent in models:
                df = data[(data['Respondent'] == respondent) & (data['Task'] == task)]
                heatmap_data = get_heatmap_data(df)
                heatmap_data_list.append([heatmap_data,task,respondent])
        global_max = max([i[0].values.max() for i in heatmap_data_list])
        global_min = min([i[0].values.min() for i in heatmap_data_list])
        # Draw all plots after determining the shared colorbar limits
        for heatmap_data, task, respondent in heatmap_data_list:
            draw_save(by, heatmap_data, task, respondent, global_max, global_min)

        # Plot humans separately using the overall range across all human data
        heatmap_data_list = []
        for task in data['Task'].unique():
            df = data[(data['Respondent'] == 'human') & (data['Task'] == task)]
            heatmap_data = get_heatmap_data(df)
            heatmap_data_list.append([heatmap_data,task])
        global_max = max([i[0].values.max() for i in heatmap_data_list])
        global_min = min([i[0].values.min() for i in heatmap_data_list])
        # Draw all plots after determining the shared colorbar limits
        for heatmap_data, task in heatmap_data_list:
            draw_save(by, heatmap_data, task, 'human', global_max, global_min)

    # Draw six plots, one for each respondent
    elif by == 'respondent':
        # Collect heatmap_data for all models to determine the minimum and maximum color values
        models = data['Respondent'].unique().tolist()
        for respondent in models:
            df = data[(data['Respondent'] == respondent)]
            heatmap_data = get_heatmap_data(df)
            draw_save(by, heatmap_data, '', respondent, vmax=1, vmin=0)

    # Draw 6 x 2 plots grouped by correctness
    elif by == 'respondent_correctness':
        # Collect heatmap_data for all models to determine the minimum and maximum color values
        heatmap_data_list = []
        models = data['Respondent'].unique().tolist()
        models.remove('human')
        for respondent in models:
            # Draw the heatmap for correct answers
            df = data[(data['Respondent'] == respondent)&(data['IsCorrect'] == 1)]
            heatmap_data = get_heatmap_data(df)
            heatmap_data_list.append([heatmap_data,respondent, 1])
            # Draw the heatmap for incorrect answers
            df = data[(data['Respondent'] == respondent) & (data['IsCorrect'] == 0)]
            heatmap_data = get_heatmap_data(df)
            heatmap_data_list.append([heatmap_data, respondent, 0])

        global_max = max([i[0].values.max() for i in heatmap_data_list])
        global_min = min([i[0].values.min() for i in heatmap_data_list])
        for heatmap_data, respondent, IsCorrect in heatmap_data_list:
            draw_save(by, heatmap_data, IsCorrect, respondent, global_max, global_min)

        # Plot humans separately
        # Draw the heatmap for correct answers
        df = data[(data['Respondent'] == 'human')&(data['IsCorrect'] == 1)]
        heatmap_data = get_heatmap_data(df)
        draw_save(by, heatmap_data, 1, 'human', None, None)
        # Draw the heatmap for incorrect answers
        df = data[(data['Respondent'] == 'human')&(data['IsCorrect'] == 0)]
        heatmap_data = get_heatmap_data(df)
        draw_save(by, heatmap_data, 0, 'human', None, None)

    # Draw heatmaps by respondent and task type 1 (five types)
    elif by == 'respondent_tasktype1':
        data['TaskType1'] = data['Task'].str.split('_').str[0]
        # Collect all heatmap_data to determine the minimum and maximum color values
        # Plot models separately using the overall range across all models
        heatmap_data_list = []
        for tasktype in data['TaskType1'].unique():
            # Draw a heatmap for each model under this task
            models = data['Respondent'].unique().tolist()
            models.remove('human')
            for respondent in models:
                df = data[(data['Respondent'] == respondent) & (data['TaskType1'] == tasktype)]
                heatmap_data = get_heatmap_data(df)
                heatmap_data_list.append([heatmap_data,tasktype,respondent])
        global_max = max([i[0].values.max() for i in heatmap_data_list])
        global_min = min([i[0].values.min() for i in heatmap_data_list])
        # Draw all plots after determining the shared colorbar limits
        for heatmap_data, tasktype, respondent in heatmap_data_list:
            draw_save(by, heatmap_data, tasktype, respondent, global_max, global_min)

        # Plot humans separately using the overall range across all human data
        heatmap_data_list = []
        for tasktype in data['TaskType1'].unique():
            df = data[(data['Respondent'] == 'human') & (data['TaskType1'] == tasktype)]
            heatmap_data = get_heatmap_data(df)
            heatmap_data_list.append([heatmap_data,tasktype])
        global_max = max([i[0].values.max() for i in heatmap_data_list])
        global_min = min([i[0].values.min() for i in heatmap_data_list])
        # Draw all plots after determining the shared colorbar limits
        for heatmap_data, tasktype in heatmap_data_list:
            draw_save(by, heatmap_data, tasktype, 'human', global_max, global_min)

    # Group by tasktype1
    elif by == 'tasktype1':
        data['TaskType1'] = data['Task'].str.split('_').str[0]
        # Collect all heatmap_data to determine the minimum and maximum color values
        # Plot separately using the overall range across all models and tasktype1 groups
        heatmap_data_list = []
        for tasktype in data['TaskType1'].unique():
            df = data[(data['Respondent'] != 'human')&(data['TaskType1'] == tasktype)]
            heatmap_data = get_heatmap_data(df)
            heatmap_data_list.append([heatmap_data,tasktype])
        global_max = max([i[0].values.max() for i in heatmap_data_list])
        global_min = min([i[0].values.min() for i in heatmap_data_list])
        # Draw all plots after determining the shared colorbar limits
        for heatmap_data, tasktype in heatmap_data_list:
            draw_save(by, heatmap_data, tasktype, 'all_model', global_max, global_min)

        # Plot humans separately using the overall range across all human data
        heatmap_data_list = []
        for tasktype in data['TaskType1'].unique():
            df = data[(data['Respondent'] == 'human') & (data['TaskType1'] == tasktype)]
            heatmap_data = get_heatmap_data(df)
            heatmap_data_list.append([heatmap_data,tasktype])
        global_max = max([i[0].values.max() for i in heatmap_data_list])
        global_min = min([i[0].values.min() for i in heatmap_data_list])
        # Draw all plots after determining the shared colorbar limits
        for heatmap_data, tasktype in heatmap_data_list:
            draw_save(by, heatmap_data, tasktype, 'human', global_max, global_min)
    else:
        print('【WARN】Input value "by" error.')

if __name__ == '__main__':
    draw_violin()
    draw_bar()

    draw_p_heatmap('CodeLen')
    draw_p_heatmap('UniqueTypes')
    draw_p_heatmap('IsCorrect')

    # draw_heatmap()
    draw_heatmap(by='respondent_task')
    draw_heatmap(by='respondent_correctness')
    draw_heatmap(by='respondent_tasktype1')
    draw_heatmap(by='tasktype1')