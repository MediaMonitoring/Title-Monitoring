import urllib

import diff_match_patch as dmp_module
import regex as re
from enums import Error

dmp = dmp_module.diff_match_patch()


def get_diff_log(left_side, right_side):
    '''
    Generate diff log between a pair of text strings.
    :param left_side: left hand side of comparison, original or predicted text
    :param right_side: right hand side of comparison, noisy text
    :return: a list of all differences between the two texts
    '''

    # Get diff list from diff_match_patch
    diff = dmp.diff_main(left_side, right_side)
    diff = [d for d in diff if d[1]]

    # Convert the diff list into a delta string, decode quoted chars with urlib
    delta_str = dmp.diff_toDelta(diff)
    delta_str = urllib.parse.unquote(delta_str)
    if delta_str:
        delta_str += '🔳'

    # Patterns for the errors
    no_change_pattern = r'=(\d+)🔳'
    insert_pattern = r'\+([^🔳]+)🔳'
    delete_pattern = r'\-(\d+)🔳'
    swap_pattern = r'\-1🔳=1🔳\+.🔳|\+.🔳=1🔳\-1🔳'
    swap_pattern_same_char = r'\-1🔳=2🔳\+.🔳|\+.🔳=2🔳\-1🔳'
    change_pattern = r'\-1🔳\+.🔳'

    diff_log = []
    # Indexes to keep track of left and right side of comparing..
    moving_index_l = 0
    moving_index_r = 0

    # Loop over delta_str, match it with the error patterns until exhaustion
    while delta_str:
        if delta_str[0] not in ['=', '+', '-']:
            # Break away in case of some unexpected delta string!
            break

        # 1. Match no change..
        no_change_match = re.match(no_change_pattern, delta_str, re.M | re.I)
        if no_change_match:
            moving_index_l += int(no_change_match.groups()[0])
            moving_index_r += int(no_change_match.groups()[0])
            delta_str = re.sub(no_change_pattern, "", delta_str, count=1)
            continue
        # 2. Match swap error..
        if re.match(swap_pattern, delta_str, re.M | re.I):
            diff_log.append(
                {'type': Error.swap.value, 'pos': moving_index_l,
                 # should be left first, keeping it that way to match original log
                 'chars': [right_side[moving_index_r], left_side[moving_index_l]]}
            )
            delta_str = re.sub(swap_pattern, "", delta_str, count=1)
            moving_index_l += 2
            moving_index_r += 2
            continue
        if re.match(swap_pattern_same_char, delta_str, re.M | re.I):
            # if left_side[moving_index_l] == right_side[moving_index_r]:
            chars = list(set(
                list(left_side[moving_index_l:moving_index_l + 3]) + list(
                    right_side[moving_index_r:moving_index_r + 3])
            ))
            if len(chars) == 2:
                diff_log.append(
                    {'type': Error.swap.value, 'pos': moving_index_l + 1,
                     # should be left first, keeping it that way to match original log
                     'chars': chars}
                )
                delta_str = re.sub(swap_pattern_same_char, "", delta_str, count=1)
                moving_index_l += 3
                moving_index_r += 3
                continue
        # 3. Match insertion error..
        insert_match = re.match(insert_pattern, delta_str, re.M | re.I)
        if insert_match:
            insertions = insert_match.groups()[0]
            for _ in insertions:
                diff_log.append(
                    {'type': Error.insertion.value, 'pos': moving_index_l, 'chars': [right_side[moving_index_r]]}
                )
                moving_index_r += 1
            delta_str = re.sub(insert_pattern, "", delta_str, count=1)
            continue
        # 4. Match change error..
        if re.match(change_pattern, delta_str, re.M | re.I):
            diff_log.append(
                {'type': Error.change.value, 'pos': moving_index_l,
                 'chars': [right_side[moving_index_r], left_side[moving_index_l], ]}
            )
            delta_str = re.sub(change_pattern, "", delta_str, count=1)
            moving_index_l += 1
            moving_index_r += 1
            continue
        # 5. Match delete error..
        delete_match = re.match(delete_pattern, delta_str, re.M | re.I)
        if delete_match:
            deletes = int(delete_match.groups()[0])
            for i in range(deletes):
                diff_log.append(
                    {'type': Error.delete.value, 'pos': moving_index_l, 'chars': [left_side[moving_index_l]]}
                )

                moving_index_l += 1
            delta_str = re.sub(delete_pattern, "", delta_str, count=1)
            continue
    return diff_log


def get_diff_distance(left_side, right_side):
    '''
    Generate Levenshtein distance between a pair of text strings.
    :param left_side: left hand side of comparison, original or predicted text
    :param right_side: right hand side of comparison, noisy text
    :return: a numeric value of the distance
    '''
    diff = dmp.diff_main(left_side, right_side)
    diff = [d for d in diff if d[1]]

    return dmp.diff_levenshtein(diff)


def get_eval_metrics(original_text, noisy_text, fixed_text):
    '''
    Get all evaluation metrics based on the difference between
    noise to original changes and noise to fixed ones.

    :param original_text:
    :param noisy_text:
    :param fixed_text:
    :return: Estimation of TP, DN, FP, FN
    '''

    # Get the diff logs from noise to original
    original_logs = get_diff_log(noisy_text, original_text)
    # Get the diff logs from noise to fixed
    fixed_logs = get_diff_log(noisy_text, fixed_text)

    # Compare keys of log dicts
    def obj_equal_on(obj0, obj1, keys):
        for key in keys:
            if obj0.get(key, False) != obj1.get(key, None):
                return False
        return True

    # Get evaluation metrics by comparing original_logs vs fixed_logs
    # TP is the same logs between the two list (intersection)
    # DN is the logs that match only on position
    # P all the positive found errors (TP + DN)
    # FN = original_logs - P
    # FP = fixed_logs - P
    TP = []
    DN = []
    for o_log in original_logs:
        for f_log in fixed_logs:
            if obj_equal_on(o_log, f_log, keys=['pos']):
                if obj_equal_on(o_log, f_log, keys=['type', 'chars']):
                    TP.append(o_log)
                else:
                    DN.append(o_log)
                break
    P = TP + DN
    FN = [log for log in original_logs if log not in P]
    FP = [log for log in fixed_logs if log not in P]

    return len(TP), len(FN), len(FP), len(DN)


def get_log_diff(original_logs, fixed_logs):
    ''''
    Same as get_eval_metrics, just for comparison between the ML model and the one generated here.
    Will delete after verification
    '''

    # Compare keys of log dicts
    def obj_equal_on(obj0, obj1, keys):
        for key in keys:
            if obj0.get(key, False) != obj1.get(key, None):
                return False
        return True

    # Get evaluation metrics by comparing original_logs vs fixed_logs
    # TP is the same logs between the two list (intersection)
    # DN is the logs that match only on position
    # P all the positive found errors (TP + DN)
    # FN = original_logs - P
    # FP = fixed_logs - P
    TP = []
    DN = []
    for o_log in original_logs:
        for f_log in fixed_logs:
            if obj_equal_on(o_log, f_log, keys=['pos']):
                if obj_equal_on(o_log, f_log, keys=['type', 'chars']):
                    TP.append(o_log)
                else:
                    DN.append(o_log)
                break
    P = TP + DN
    FN = [log for log in original_logs if log['pos'] not in [l['pos'] for l in P]]
    FP = [log for log in fixed_logs if log['pos'] not in [l['pos'] for l in P]]

    return TP, FN, FP, DN
    # return len(TP), len(FN), len(FP), len(DN)
