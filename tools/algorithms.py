# Pass in two lists to obtain the result
import pandas as pd
import Levenshtein
import multimatch_gaze
import numpy as np
from itertools import groupby


# Remove consecutive duplicate values
def del_duplicates(l):
    return [x for x, _ in groupby(l)]


### Levenshtein
def lv_dis(l1, l2, delete_duplicates=False):
    ## This algorithm does not need to handle out-of-range AOI codes

    if delete_duplicates:
        l1 = del_duplicates(l1)
        l2 = del_duplicates(l2)
    return Levenshtein.distance(l1, l2)

### multimatch_gaze
# five dimensions 'vector shape', 'vector length' (saccadic amplitude), 'vector position', 'vector direction' and 'fixation duration'
def multi_match(l1,l2, delete_duplicates=False):
    if delete_duplicates:
        l1 = del_duplicates(l1)
        l2 = del_duplicates(l2)

    # Convert AOIs to their center points
    trans = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 6, 'G': 7, 'H': 8}

    def aoi_2_point(aoi_list):
        df = pd.DataFrame(columns=['start_x', 'start_y', 'duration'])
        for aoi in aoi_list:
            # If the AOI code is out of range, skip this AOI
            if aoi[0] not in trans.keys():
                continue

            x_num = trans[aoi[0]]
            # For an AOI such as GG6, aoi[1] is a letter, so use aoi[2]
            if aoi[1].isalpha():
                y_num = int(aoi[2])
            else:
                y_num = int(aoi[1])

            x = (x_num - 1) * (1920 / 8) + (1920 / 8 / 2)
            y = (y_num - 1) * (1080 / 8) + (1080 / 8 / 2)
            df.loc[len(df)] = [x, y, 0.3]
        return df

    l1_vector = aoi_2_point(l1)
    l2_vector = aoi_2_point(l2)

    result_list = multimatch_gaze.docomparison(l1_vector, l2_vector, screensize=[1920, 1080])
    return result_list

### frdist
def frdist_dis(l1, l2, delete_duplicates=False):
    if delete_duplicates:
        l1 = del_duplicates(l1)
        l2 = del_duplicates(l2)

    def frdist(p, q):
        p = np.array(p, np.float64)
        q = np.array(q, np.float64)
        len_p = len(p)
        len_q = len(q)
        if len_p == 0 or len_q == 0:
            raise ValueError('Input curves are empty.')
        ca = (np.ones((len_p, len_q), dtype=np.float64) * -1)
        for i in range(len_p):
            for j in range(len_q):
                if i == 0 and j == 0:
                    ca[i, j] = np.linalg.norm(p[i] - q[j])
                elif i > 0 and j == 0:
                    ca[i, j] = max(ca[i - 1, 0], np.linalg.norm(p[i] - q[j]))
                elif i == 0 and j > 0:
                    ca[i, j] = max(ca[0, j - 1], np.linalg.norm(p[i] - q[j]))
                elif i > 0 and j > 0:
                    ca[i, j] = max(
                        min(
                            ca[i - 1, j],
                            ca[i - 1, j - 1],
                            ca[i, j - 1]
                        ),
                        np.linalg.norm(p[i] - q[j])
                    )
                else:
                    ca[i, j] = float('inf')
        dist = ca[len_p - 1, len_q - 1]
        return dist


    # Convert codes to numeric values
    trans = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 6, 'G': 7, 'H': 8}

    def get_point_list(aoi_list):
        point_list = []
        for aoi in aoi_list:
            # If the AOI code is out of range, skip this AOI
            if aoi[0] not in trans.keys():
                continue

            # For an AOI such as GG6, aoi[1] is a letter, so use aoi[2]
            if aoi[1].isalpha():
                point_list.append([
                    trans[aoi[0]], int(aoi[2])
                ])
                continue
            # Normal case
            point_list.append([
                trans[aoi[0]], int(aoi[1])
            ])

        return point_list

    l1_point = get_point_list(l1)
    l2_point = get_point_list(l2)
    result = frdist(l1_point, l2_point)
    return result