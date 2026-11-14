# =================================================
# This code is used for AI image reading and automatic code extraction

import os, sys, time, traceback
from openpyxl import load_workbook, Workbook
import pandas as pd

from tools.run_ai import run_chatgpt_code, run_openrouter_read, run_hunyuan_read


# -------------------------------------------------
# 1. Parameter configuration
# -------------------------------------------------
skipping = 0    # Improve output formatting with line breaks
from tools.cfg import cfg_read, cfg_read2, cfg_code


# -------------------------------------------------
# 2. General utility functions
# -------------------------------------------------
def load_key_dict(xlsx_path):
    wb = load_workbook(xlsx_path)
    ws = wb.active
    return {row[0]: (row[1] or '')
            for row in ws.iter_rows(min_row=2, values_only=True)
            if row[0]}


def init_result_workbook(xlsx_path):
    if os.path.exists(xlsx_path) and os.path.getsize(xlsx_path) > 0:
        return load_workbook(xlsx_path)
    wb = Workbook()
    ws = wb.active
    ws.append(['Image Path', 'Run', 'AI Answer'])
    wb.save(xlsx_path)
    return wb


def append_result(xlsx_path, image_path, run, ai_ans):
    wb = load_workbook(xlsx_path)
    ws = wb.active
    ws.append([image_path, run, ai_ans])
    # if ai_ans.lower() == xlsx_ans.lower():
    #     fill = PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid")
    #     ws.cell(row=ws.max_row, column=2).fill = fill
    wb.save(xlsx_path)


def load_processed_list(log_path):
    if not os.path.exists(log_path): return list()
    with open(log_path, 'r', encoding='utf-8') as f: return [line.strip() for line in f if line.strip()]


def mark_processed(log_path, image_path, run):
    with open(log_path, 'a', encoding='utf-8') as f:
        f.write(f'{image_path}, run={run} \n')
        f.flush()


def get_all_images(folder):
    ext = ('.png', '.jpg', '.jpeg')
    return [os.path.join(folder, f) for f in os.listdir(folder) if f.lower().endswith(ext)]


# -------------------------------------------------
# 3.1 Image reading
# -------------------------------------------------


def get_read(cfg, run_ai_read):
    print(f'\n========== {cfg["name"]} Started ==========')
    print(f'Model: {cfg['model']}')
    init_result_workbook(cfg['result_xlsx'])
    processed_list = load_processed_list(cfg['processed_log'])
    all_proto_images = get_all_images(cfg['image_folder1'])   # Use the original image folder as the reference
    todo_proto_images = [p for p in all_proto_images if f'{p}, run={cfg['repeat_runs']}' not in processed_list] # Add to todo if not logged yet or the number of runs has not reached the maximum

    if not todo_proto_images and len(processed_list) >= len(all_proto_images)*cfg['repeat_runs']:
        print(f'[INFO]{cfg["name"]} has completed all runs; skipping')
        return
    print(f'[INFO]{cfg["name"]} Pending: {len(todo_proto_images)} / {len(all_proto_images)} ; runs per image: {cfg["repeat_runs"]} times.')
    start_run = 1
    # If the next todo path matches the last path in the processed log, determine the completed runs and update start_run
    if len(processed_list)>0 and todo_proto_images[0] == (list(processed_list)[-1].split(','))[0]:
        start_run = int((list(processed_list)[-1].split('run='))[1]) + 1
        print(f'[INFO]Since {todo_proto_images[0]} has not completed all repeated runs, resuming from run {start_run}.')

    for idx, proto_img_path in enumerate(todo_proto_images, 1): # 1 means indices start at 1, 2, ..., while items still iterate over all images
        for run in range(start_run, cfg['repeat_runs']+1):       # Repeated runs for the same question
            try:
                proto_img_name = os.path.splitext(os.path.basename(proto_img_path))[0]
                grid_img_name = proto_img_name + '_Grid_8x8_Labeled'
                grid_img_path = cfg['image_folder2'] + '/' + grid_img_name + '.png'

                ai_ans = run_ai_read(cfg, proto_img_path, grid_img_path)
                if ai_ans.strip() == '':
                    raise ValueError('【WARN】Empty answer!')

                append_result(cfg['result_xlsx'], proto_img_path, run, ai_ans)
                mark_processed(cfg['processed_log'], proto_img_path, run)
                print(f'[INFO][{idx}/{len(todo_proto_images)}] {proto_img_name} run{run} completed.')  # {idx:>3} pads idx with leading spaces if it has fewer than three digits
            except Exception as e:
                print(f'[ERROR]Error while processing {proto_img_path}: {e}')
                traceback.print_exc()
                raise

        print(f'[INFO][{idx}/{len(todo_proto_images)}] {proto_img_path} all repeated runs completed.')
        start_run = 1    # Reset to 1

# -------------------------------------------------
# 3.2 Extracting codes from text
# -------------------------------------------------


def get_code(cfg, run_ai_code):
    print(f'\n========== {cfg["name"]} Started ==========')
    print(f'Model: {cfg['model']}')

    df = pd.read_excel(cfg['result_xlsx'], header=0)
    # Check whether the 'Code' column exists; add it if missing
    if not 'Code' in df.columns:
        df['Code'] = ''
        print(f'[INFO]{cfg['result_xlsx']} does not have a Code column; it has been created automatically.'
              f'Current columns in order: {df.columns}')
    # For nonempty AI Answer entries, check Code; if empty, extract a code from the corresponding AI Answer
    for i in range(len(df)):
        todo_text = df.loc[i, 'AI Answer']   # Get the text to convert into a code
        if todo_text:
            global skipping # Improve output formatting with line breaks

            if (not df.loc[i, 'Code']) or (pd.isnull(df.loc[i, 'Code'])):
                if skipping == 1:   # Improve output formatting with line breaks
                    print('')
                    skipping = 0

                code = run_ai_code(cfg, todo_text)
                if code.strip() == '':
                    raise ValueError('【WARN】Empty code!')
                df.loc[i, 'Code'] = code
                df.to_excel(cfg['result_xlsx'], index=False)
                print(f'[INFO]Row {i+1}: Code={code}')
            else:
                print(f'\r[INFO]Row {str(i+1).zfill(3)} already has a Code value; skipped.', end='', flush=True)
                skipping = 1    # Improve output formatting with line breaks

# -------------------------------------------------
# 4. Run all tasks
# -------------------------------------------------
def main():
    print(f"\n {time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())} Program started.")

    get_read(cfg_read2, run_ai_read=run_openrouter_read)
    # get_code(cfg_code, run_ai_code=run_chatgpt_code)

    print(f'\n {time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())} All tasks completed.')

# -------------------------------------------------
# 5. Exception handling and automatic restart wrapper
#    Automatically restart on errors; run in the console: python filename     # Run the file
# -------------------------------------------------
if __name__ == '__main__':
    try:
        while True:
            try:
                main()
                break  # Exit the loop after successful execution
            except ConnectionError as e:
                print(f'[WARN]Network connection error: {e}. Check your connection or whether the request succeeded.')
                print(f'[WARN]Automatically restarting in 60 seconds...')
                time.sleep(60)
                os.execv(sys.executable, [sys.executable] + sys.argv)  # Restart the program
            except Exception as e:
                print(f'[WARN]Script error: {e}. Automatically restarting in 5 seconds...')
                traceback.print_exc()
                time.sleep(5)
                os.execv(sys.executable, [sys.executable] + sys.argv)   # Restart the program

    except KeyboardInterrupt:
        # Catch KeyboardInterrupt at the outermost level to prevent accidental restarts
        print('[INFO]Interrupted by user.')
        sys.exit(0)     # Raises SystemExit

    except SystemExit:
        # Catch the SystemExit exception raised by sys.exit()
        # Ensure the program exits cleanly after the inner break logic completes
        pass