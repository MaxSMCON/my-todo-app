# 1. Meat Pieces Check for 4 priority plan
## Function1.1(Main Function)
def meat_pieces_check(ProdMeat, req, meat):
    """
    To check if enough meat pieces are available to complete the plan.
    arguments:
    1. plan: the plan we can to check the feasibility
    2. pieces_in_box: how much pieces needed in a box for each sku
    3. meat_input: how many pieces of meat will arrive in each prority for each meat type
    4. ProdMeat: source meat of each sku

    Return:
    1. feasible or not feasible
    2. if not feasible it can also return infeasible meat type with priority.
    """
    import pandas as pd
    result = []
    meat_id_list = list(req.merge(ProdMeat,
                                  left_on='itemkey',
                                  right_on='FinishedGoodProductCode',
                                  how='left',
                                  validate='1:m'  # validates one to many connection
                                  ).MeatItem.drop_duplicates())
    # print(meat_id_list)
    for meat_id in meat_id_list:
        # if meat_id not in [412,803,901,902,413]:
        result = one_meat_checking(meat_id=meat_id, result=result, ProdMeat=ProdMeat, meat=meat, req=req)
        # print(result)
    if len(result) == 0:
        return "Feasible"
    elif len(result) > 0:
        print("Infeasible")
        print(len(result))
        return pd.DataFrame(result)


## Function1.2(One Meat Checking)
def one_meat_checking(meat_id, result, ProdMeat, meat, req):
    new_req = req.merge(ProdMeat,
                        left_on='itemkey',
                        right_on='FinishedGoodProductCode',
                        how='left',
                        validate="1:m"  # validates one to many connection
                        )

    new_req = new_req.loc[new_req['MeatItem'] == meat_id, :]
    pieces_need_df = new_req.copy()
    priority_cols = ['Priority1Qty', 'Priority2Qty', 'Priority3Qty', 'Priority4Qty']
    pieces_priority_cols = []
    for p in range(1, 4 + 1):
        pieces_need_df['pieces_p' + str(p)] = pieces_need_df['PiecesInBox'] * pieces_need_df[priority_cols[p - 1]]
        pieces_priority_cols.append('pieces_p' + str(p))
    pieces_need_df.drop(priority_cols, axis=1, inplace=True)
    pieces_need_df.drop(['FinishedGoodProductCode'], axis=1, inplace=True)

    # requirements
    p1_req = pieces_need_df.pieces_p1.sum()
    p2_req = pieces_need_df.pieces_p2.sum()
    p3_req = pieces_need_df.pieces_p3.sum()
    p4_req = pieces_need_df.pieces_p4.sum()

    avaliable = meat.loc[meat['Meat'] == meat_id, :]
    print(avaliable)
    p1_ava = avaliable.loc[:, 'Priority 1'].values[0]
    # print(p1_ava)
    p2_ava = avaliable.loc[:, 'Priority 2'].values[0]
    p3_ava = avaliable.loc[:, 'Priority 3'].values[0]
    p4_ava = avaliable.loc[:, 'Priority 4'].values[0]

    p1_remaining = p1_ava - p1_req
    p2_remaining = (p1_remaining + p2_ava) - p2_req
    p3_remaining = (p2_remaining + p3_ava) - p3_req
    p4_remaining = (p3_remaining + p4_ava) - p4_req
    if p1_remaining < 0:
        dic = {'meat': meat_id, 'priority': 'p1n'}
        dic['needed_pieces'] = p1_remaining * (-1)
        result.append(dic)
        print(len(result))
    if p2_remaining < 0:
        dic = {'meat': meat_id, 'priority': 'p2'}
        dic['needed_pieces'] = p2_remaining * (-1)
        result.append(dic)
        print(len(result))
    if p3_remaining < 0:
        dic = {'meat': meat_id, 'priority': 'p3'}
        dic['needed_pieces'] = p3_remaining * (-1)
        result.append(dic)
        print(len(result))
    if p4_remaining < 0:
        dic = {'meat': meat_id, 'priority': 'p4'}
        dic['needed_pieces'] = p4_remaining * (-1)
        result.append(dic)
        print(len(result))
    return result


# 2. Activity Time Checking-accumulated for 4 priority plan
def activity_time_check(req, hour_priority, cap, seq):
    """
    To check if enough time are available to complete the plan.
    arguments:
    1. req: 4 priority requirement
    2. hour_priority: relationship between hour and priority, used to calculate available time in each priority
    3. cap: maximum capacity table

    #output activty - priority - needed time - related skus in that prority using this activity

    """
    import pandas as pd

    # reshaping the requirements table
    req_transpose = req.loc[:, ["itemkey",
                                "Priority1Qty",
                                "Priority2Qty",
                                "Priority3Qty",
                                "Priority4Qty"]]
    req_transpose = req_transpose.set_index('itemkey')
    req_transpose = req_transpose.stack(0).rename_axis(
        ('itemkey', 'priority')).reset_index()

    # joining seq and req_transpose tables
    new_seq = seq.merge(req_transpose, left_on='BomKey', right_on='itemkey', how='right')
    new_seq.rename(columns={0: 'RequiredNumbers'}, inplace=True)
    new_seq["TotalTimebyActivity"] = new_seq["DurationSeconds"] * new_seq["RequiredNumbers"]
    # new_seq.head(24)

    # create an aggregated table
    new_seq22 = new_seq.loc[:, ["ActivityFunctionKey",
                                "priority",
                                "TotalTimebyActivity"]]
    new_seq22.head(24)
    new_seq2 = new_seq22.groupby(['ActivityFunctionKey', 'priority']).sum()
    new_seq2 = new_seq2.reset_index()

    # create a column for available time
    new_seq2.loc[new_seq2['priority'] == 'Priority1Qty', 'AvailableTime'] = len(
        [k for k, v in hour_priority.items() if v == 1]) * 3600
    new_seq2.loc[new_seq2['priority'] == 'Priority2Qty', 'AvailableTime'] = len(
        [k for k, v in hour_priority.items() if v == 2]) * 3600
    new_seq2.loc[new_seq2['priority'] == 'Priority3Qty', 'AvailableTime'] = len(
        [k for k, v in hour_priority.items() if v == 3]) * 3600
    new_seq2.loc[new_seq2['priority'] == 'Priority4Qty', 'AvailableTime'] = len(
        [k for k, v in hour_priority.items() if v == 4]) * 3600

    # keep the activities over 6700
    new_seq2 = new_seq2[new_seq2["ActivityFunctionKey"] > 6700]  # This is hardcord. If not suitable, need to be changed

    # join the capacity with the dataframe and mulitply with available time
    new_seq3 = new_seq2.merge(cap,
                              left_on='ActivityFunctionKey',
                              right_on='Activity_Num',
                              how='left')
    new_seq3["TotalAvailableTime"] = new_seq3["AvailableTime"] * new_seq3["Max"]
    new_seq3 = new_seq3.loc[:, ["ActivityFunctionKey",
                                "priority",
                                "TotalTimebyActivity",
                                "TotalAvailableTime"]]

    results2 = pd.DataFrame()
    # activity list
    act_list = list(dict.fromkeys(list(new_seq3["ActivityFunctionKey"])))
    result = []
    for act in act_list:
        new_seq4 = new_seq3[(new_seq3['ActivityFunctionKey'] == act)]

        p1_ava = new_seq4.loc[new_seq4['priority'] == "Priority1Qty", 'TotalAvailableTime'].values[0]
        p2_ava = new_seq4.loc[new_seq4['priority'] == "Priority2Qty", 'TotalAvailableTime'].values[0]
        p3_ava = new_seq4.loc[new_seq4['priority'] == "Priority3Qty", 'TotalAvailableTime'].values[0]
        p4_ava = new_seq4.loc[new_seq4['priority'] == "Priority4Qty", 'TotalAvailableTime'].values[0]

        p1_req = new_seq4.loc[new_seq4['priority'] == "Priority1Qty", 'TotalTimebyActivity'].values[0]
        p2_req = new_seq4.loc[new_seq4['priority'] == "Priority2Qty", 'TotalTimebyActivity'].values[0]
        p3_req = new_seq4.loc[new_seq4['priority'] == "Priority3Qty", 'TotalTimebyActivity'].values[0]
        p4_req = new_seq4.loc[new_seq4['priority'] == "Priority4Qty", 'TotalTimebyActivity'].values[0]

        p1_rem = p1_ava - p1_req
        p2_rem = (p1_rem + p2_ava) - p2_req
        p3_rem = (p2_rem + p3_ava) - p3_req
        p4_rem = (p3_rem + p4_ava) - p4_req
        if p1_rem < 0:
            dic = {'Activity': act, 'priority': 'p1'}
            dic['needed_time'] = p1_rem * (-1)
            result.append(dic)
        if p2_rem < 0:
            dic = {'Activity': act, 'priority': 'p2'}
            dic['needed_time'] = p2_rem * (-1)
            result.append(dic)
        if p3_rem < 0:
            dic = {'Activity': act, 'priority': 'p3'}
            dic['needed_time'] = p3_rem * (-1)
            result.append(dic)
        if p4_rem < 0:
            dic = {'Activity': act, 'priority': 'p4'}
            dic['needed_time'] = p4_rem * (-1)
            result.append(dic)

    if len(result) == 0:
        print("Feasible")
        return pd.DataFrame(result)
    elif len(result) > 0:
        print("Infeasible")

        return pd.DataFrame(result)


# 3. Plan Break Down (Method1: calculate ratio based on pieces needed)
## Function 3.1: Method1 Main Function
def plan_break_down(meat_and_req, meat_hourly, hour_priority):
    """
    To break plans into hourly plan according to partition calculated by packaging requirement.
    arguments:
    1. meat_and_req: origianl plan, a plan that passes feasibility check
    2. meat_hourly: hourly meat input
    3. hour_priority: map between hour and priority

    Return:
    1. a detailed hourly plan
    2. plans that cannot be arranged (due to limited meat source)
    """
    import pandas as pd
    # start hour and end hour
    t_start = min(meat_hourly.index)
    t_end = max(meat_hourly.index)

    packaging_plan = []
    requirements_not_complete = []
    for meat_id in sorted(list(set(meat_and_req.MeatItem))):
        one_meat_hourly = meat_hourly.loc[:, meat_id]
        one_meat_req = one_meat_req = meat_and_req.loc[meat_and_req['MeatItem'] == meat_id, :]
        # if there is only one prodct, no need to split
        if len(one_meat_req) == 1:
            pkg_dic, needs_by_priority = arrange_one_meat(one_meat_hourly, one_meat_req, t_start, t_end, hour_priority)
            packaging_plan.append(pkg_dic)
            if needs_by_priority[1] + needs_by_priority[2] + needs_by_priority[3] + needs_by_priority[4] != 0:
                requirements_not_complete.append(needs_by_priority)
        if len(one_meat_req) > 1:
            multiple_pkg_dic, multiple_needs_by_priority = arrange_multiple_meat(one_meat_hourly, one_meat_req, t_start,
                                                                                 t_end, hour_priority)
            # combine two lists
            packaging_plan += multiple_pkg_dic

            for needs_by_priority in multiple_needs_by_priority:
                if needs_by_priority[1] + needs_by_priority[2] + needs_by_priority[3] + needs_by_priority[4] != 0:
                    requirements_not_complete.append(needs_by_priority)
    return pd.DataFrame(packaging_plan), pd.DataFrame(requirements_not_complete)


## Function 3.2: arrange_one_meat,For meat that only has one sku related to it. Break into hourly plans
def arrange_one_meat(one_meat_hourly, one_meat_req, t_start, t_end, hour_priority):
    """
    For meat that only has one sku related to it. Break into hourly plans
    """
    import math
    pkg_dic = {}
    pkg_dic['meatkey'] = one_meat_hourly.name  # get meat id
    pkg_dic['itemkey'] = one_meat_req['itemkey'].values[0]
    pkg_dic['itemdesc'] = one_meat_req['itemdesc'].values[0]
    t = t_start
    # To track how many still need to be planed, once planed, the planed amount need to be subtracted from it
    needs_by_priority = {
        "meatkey": one_meat_hourly.name,
        "itemkey": one_meat_req['itemkey'].values[0],
        "itemdesc": one_meat_req['itemdesc'].values[0],
        1: one_meat_req['Priority1Qty'].values[0],
        2: one_meat_req['Priority2Qty'].values[0],
        3: one_meat_req['Priority3Qty'].values[0],
        4: one_meat_req['Priority4Qty'].values[0]
    }
    meat_available = 0  # to track have many meat pieces are avaliable
    while t <= t_end:
        meat_available = meat_available + one_meat_hourly[t]
        if meat_available == 0:  # if this hour does not produce meat and no meat remains from previous hour
            pkg_dic[t] = 0  # plan 0 boxes for packaing
            t += 1  # then goes to next hour
        else:  # plan packaging
            # check if still need meat (if have products not planed in current priority and latter priorities)
            current_priority = hour_priority[t]
            boxes_need = needs_by_priority[current_priority]
            p = current_priority
            while p != 4:  # if not in last priority,needs in latter priorities need to be added together
                p += 1  # move to next priority
                boxes_need += needs_by_priority[p]

            pieces_in_boxes = one_meat_req['PiecesInBox'].values[0]
            amount_can_pack = math.floor(
                meat_available / pieces_in_boxes)  # if can produce 1.6, we round it to 1(floor)
            pkg_dic[t] = min(boxes_need, amount_can_pack)
            meat_available = meat_available - amount_can_pack * pieces_in_boxes  # delect used meat pieces
            # the needs_by_priority needs to be updated as well. Need to be 0 at end, start from current priority
            to_update = pkg_dic[t]
            if needs_by_priority[current_priority] > 0:
                deduct_amount = min(to_update, needs_by_priority[current_priority])
                needs_by_priority[current_priority] -= deduct_amount
                to_update -= deduct_amount

            p = current_priority
            while p != 4 and to_update != 0:
                # reduce the demand in next priority
                p += 1
                if needs_by_priority[p] > 0:
                    deduct_amount = min(to_update, needs_by_priority[p])
                    needs_by_priority[p] -= deduct_amount
                    to_update -= deduct_amount
            # move to the next hour
            t += 1
    return pkg_dic, needs_by_priority


## Function 3.3: arrange_multiple_meat,For meat that only has multiple skus related to it. Need to calculate breakdown ratios.
def arrange_multiple_meat(one_meat_hourly, one_meat_req, t_start, t_end, hour_priority):
    """
    For meat that only has multiple skus related to it. Need to calculate breakdown ratios.
    """
    names = locals()
    # initialize result dictionary for each sku
    for itemkey in one_meat_req.itemkey:
        names[f"pkg_dic_{itemkey}"] = {}
        names[f"pkg_dic_{itemkey}"]['meatkey'] = one_meat_hourly.name
        names[f"pkg_dic_{itemkey}"]['itemkey'] = itemkey
        names[f"pkg_dic_{itemkey}"]['itemdesc'] = \
        one_meat_req.loc[one_meat_req['itemkey'] == itemkey, 'itemdesc'].values[0]

        # To track the  to-do list
        names[f"needs_by_priority_{itemkey}"] = {
            "meatkey": one_meat_hourly.name,
            "itemkey": itemkey,
            "itemdesc": one_meat_req.loc[one_meat_req['itemkey'] == itemkey, 'itemdesc'].values[0],
            1: one_meat_req.loc[one_meat_req['itemkey'] == itemkey, 'Priority1Qty'].values[0],
            2: one_meat_req.loc[one_meat_req['itemkey'] == itemkey, 'Priority2Qty'].values[0],
            3: one_meat_req.loc[one_meat_req['itemkey'] == itemkey, 'Priority3Qty'].values[0],
            4: one_meat_req.loc[one_meat_req['itemkey'] == itemkey, 'Priority4Qty'].values[0]
        }

    t = t_start

    meat_available = 0
    while t <= t_end:
        meat_available = meat_available + one_meat_hourly[t]
        if meat_available == 0:  # not plan
            for itemkey in one_meat_req.itemkey:
                names[f"pkg_dic_{itemkey}"][t] = 0  # plan 0
            t += 1
        else:  # plan

            current_priority = hour_priority[t]

            # debug
            needs_by_priority = {}
            for itemkey in one_meat_req.itemkey:
                needs_by_priority[itemkey] = names[f"needs_by_priority_{itemkey}"]

            split_p, ratio_calculation = ratio_calculator(current_priority, one_meat_req, needs_by_priority)
            # split meat based on calculated ratio
            # After current ratio, if there's remained pieces, need to check next ratio

            # initailze plans
            for itemkey in one_meat_req.itemkey:
                names[f"pkg_dic_{itemkey}"][t] = 0

            meat_used = 0
            for itemkey in one_meat_req.itemkey:
                names[f"pkg_dic_{itemkey}"], names[f"needs_by_priority_{itemkey}"], meat_used = ratio_make_plans(t,
                                                                                                                 split_p,
                                                                                                                 itemkey,
                                                                                                                 one_meat_req,
                                                                                                                 meat_available,
                                                                                                                 ratio_calculation,
                                                                                                                 meat_used,
                                                                                                                 names[
                                                                                                                     f"pkg_dic_{itemkey}"],
                                                                                                                 names[
                                                                                                                     f"needs_by_priority_{itemkey}"])
            # update meat_available
            meat_available -= meat_used

            # if there are still some meat left, can still plan next priotity. And the plan can be added
            # Need to check is greater than PiecesinBox or not
            min_piecesinbox = ratio_calculation['PiecesInBox'].min()

            # calculated min_piecesinbox_required: the min piecesinbox of what is still required
            piecesinbox_required = [
                100000]  # set a very big number to represent there's no requirement left, the statement cannot be satisfied
            for itemkey in one_meat_req.itemkey:
                boxes_still_need = names[f"needs_by_priority_{itemkey}"][1] + names[f"needs_by_priority_{itemkey}"][2] + \
                                   names[f"needs_by_priority_{itemkey}"][3] + names[f"needs_by_priority_{itemkey}"][4]
                piecesinbox = one_meat_req.loc[one_meat_req['itemkey'] == itemkey, "PiecesInBox"].values[0]
                if boxes_still_need > 0:
                    piecesinbox_required.append(piecesinbox)
            min_piecesinbox_required = min(piecesinbox_required)

            # 20220726,Need to add another if statement, this priority completed
            split_priority_still_need = 0
            for itemkey in one_meat_req.itemkey:
                split_priority_still_need += names[f"needs_by_priority_{itemkey}"][split_p]

            meat_available = round(meat_available, 0)
            # 20220726,if at the last priority and there's still some meat left
            if meat_available >= min_piecesinbox_required and split_p == 4 and split_priority_still_need > 0:

                # debug
                needs_by_priority = {}
                for itemkey in one_meat_req.itemkey:
                    needs_by_priority[itemkey] = names[f"needs_by_priority_{itemkey}"]

                split_p, ratio_calculation = ratio_calculator(split_p, one_meat_req, needs_by_priority)
                meat_used = 0
                for itemkey in one_meat_req.itemkey:
                    names[f"pkg_dic_{itemkey}"], names[f"needs_by_priority_{itemkey}"], meat_used = ratio_make_plans(t,
                                                                                                                     split_p,
                                                                                                                     itemkey,
                                                                                                                     one_meat_req,
                                                                                                                     meat_available,
                                                                                                                     ratio_calculation,
                                                                                                                     meat_used,
                                                                                                                     names[
                                                                                                                         f"pkg_dic_{itemkey}"],
                                                                                                                     names[
                                                                                                                         f"needs_by_priority_{itemkey}"])

                # update meat_available
                meat_available -= meat_used

                # update the min_piecesinbox_required
                piecesinbox_required = [100000]
                for itemkey in one_meat_req.itemkey:
                    boxes_still_need = names[f"needs_by_priority_{itemkey}"][1] + names[f"needs_by_priority_{itemkey}"][
                        2] + names[f"needs_by_priority_{itemkey}"][3] + names[f"needs_by_priority_{itemkey}"][4]
                    piecesinbox = one_meat_req.loc[one_meat_req['itemkey'] == itemkey, "PiecesInBox"].values[0]
                    if boxes_still_need > 0:
                        piecesinbox_required.append(piecesinbox)
                min_piecesinbox_required = min(piecesinbox_required)

            while meat_available >= min_piecesinbox_required and split_p < 4 and split_priority_still_need == 0:
                # while still have meat to pack what is required and not at the end of all priority
                # Continue calculating new split_p and ratio in split_p and add it to new plans

                # debug
                needs_by_priority = {}
                for itemkey in one_meat_req.itemkey:
                    needs_by_priority[itemkey] = names[f"needs_by_priority_{itemkey}"]

                split_p, ratio_calculation = ratio_calculator(split_p + 1, one_meat_req,
                                                              needs_by_priority)  # Start at next priority

                meat_used = 0
                for itemkey in one_meat_req.itemkey:
                    names[f"pkg_dic_{itemkey}"], names[f"needs_by_priority_{itemkey}"], meat_used = ratio_make_plans(t,
                                                                                                                     split_p,
                                                                                                                     itemkey,
                                                                                                                     one_meat_req,
                                                                                                                     meat_available,
                                                                                                                     ratio_calculation,
                                                                                                                     meat_used,
                                                                                                                     names[
                                                                                                                         f"pkg_dic_{itemkey}"],
                                                                                                                     names[
                                                                                                                         f"needs_by_priority_{itemkey}"])

                # update meat_available
                meat_available -= meat_used

                # update the min_piecesinbox_required
                piecesinbox_required = [100000]
                for itemkey in one_meat_req.itemkey:
                    boxes_still_need = names[f"needs_by_priority_{itemkey}"][1] + names[f"needs_by_priority_{itemkey}"][
                        2] + names[f"needs_by_priority_{itemkey}"][3] + names[f"needs_by_priority_{itemkey}"][4]
                    piecesinbox = one_meat_req.loc[one_meat_req['itemkey'] == itemkey, "PiecesInBox"].values[0]
                    if boxes_still_need > 0:
                        piecesinbox_required.append(piecesinbox)
                min_piecesinbox_required = min(piecesinbox_required)
            t += 1

    # need to return multiple dict result
    multiple_pkg_dic = []
    multiple_needs_by_priority = []
    for itemkey in one_meat_req.itemkey:
        multiple_pkg_dic.append(names[f"pkg_dic_{itemkey}"])
        multiple_needs_by_priority.append(names[f"needs_by_priority_{itemkey}"])

    return multiple_pkg_dic, multiple_needs_by_priority


## Function 3.4: ratio_calculator, calculate ratio
def ratio_calculator(current_priority, one_meat_req, needs_by_priority):
    """
    calculate the segragation ratio of all skus for that meat
    the ratio is calculated by pieces needed in one priority for skus
    """
    names = locals()
    # debug:

    for itemkey in needs_by_priority.keys():
        names[f"needs_by_priority_{itemkey}"] = needs_by_priority[itemkey]

    # calculate spliting ratio
    # Step1: decide the split priority (latest priority, the ratio will calculated based on all requirements in that priority)
    needs_in_current_priority = 0
    for itemkey in one_meat_req.itemkey:
        needs_in_current_priority += names[f"needs_by_priority_{itemkey}"][current_priority]
    split_p = current_priority
    while needs_in_current_priority == 0 and split_p < 4:  # split_p<=4:
        # if current priority does not have any plans and there're latter priorities, move to next priority
        split_p += 1
        for itemkey in one_meat_req.itemkey:
            needs_in_current_priority += names[f"needs_by_priority_{itemkey}"][split_p]
    # Step2: get pieces needed for each item
    ratio_calculation = one_meat_req[['itemkey', 'PiecesInBox']]
    # read number of boxes in split_p for each sku
    boxes_n = []
    for itemkey in one_meat_req.itemkey:
        boxes_n.append(names[f"needs_by_priority_{itemkey}"][split_p])
    ratio_calculation.insert(2, "boxes_n", boxes_n, True)
    # Step3: calcuclate number of pieces required
    pieces_n = ratio_calculation["boxes_n"] * ratio_calculation["PiecesInBox"]
    ratio_calculation.insert(2, "pieces_n", pieces_n, True)
    # calculate ratio
    if ratio_calculation['pieces_n'].sum() > 0:  # to solve problem: there's meat available, but no requirement
        ratio = ratio_calculation['pieces_n'] / ratio_calculation['pieces_n'].sum()
    else:
        ratio = [0 for i in range(len(ratio_calculation))]
    ratio_calculation.insert(2, "ratio", ratio, True)

    return split_p, ratio_calculation


## Function 3.5: ratio_make_plans, get hourly plans with given ratio
def ratio_make_plans(t, split_p, itemkey, one_meat_req, meat_available, ratio_calculation, meat_used, pkg_dic_itemkey,
                     needs_by_priority_itemkey):
    """
    For each sku
    With ratio and meat_available, calculate plans for each sku.
    Add the planned_amount into plans dictionary
    """
    import math

    ratio = ratio_calculation.loc[ratio_calculation['itemkey'] == itemkey, 'ratio'].values[0]
    meat_can_get = meat_available * ratio
    piecesinbox = ratio_calculation.loc[ratio_calculation['itemkey'] == itemkey, 'PiecesInBox'].values[0]
    boxes_can_make = math.floor(meat_can_get / piecesinbox)
    boxes_need = ratio_calculation.loc[ratio_calculation['itemkey'] == itemkey, 'boxes_n'].values[0]
    boxed_really_make = min(boxes_can_make, boxes_need)
    pkg_dic_itemkey[t] += boxed_really_make

    # update the to-do list
    needs_by_priority_itemkey[split_p] -= boxed_really_make

    # update meat available
    meat_used += boxed_really_make * piecesinbox

    return pkg_dic_itemkey, needs_by_priority_itemkey, meat_used


# 4. Plan Break Down Method 2, given ratio between combo and packaging floor
## Function 4.1:meat_split_combo_pkg, get the splited meat source for combo and packaging floor
def meat_split_combo_pkg(hour_priority, one_meat_hourly, one_meat_req_combo, one_meat_req_pkg, combo_ratio):
    """
    To balance the meat between combo area and packaging floor with a given ratio.
    Return one_meat_hourly for combo and pkg seperately

    """
    import pandas as pd
    import math
    # calculate the meat required by combo and packaging floor (for each priority)
    piece_dist_byp = []  # piece distribution by priority
    for p in ['Priority1Qty', 'Priority2Qty', 'Priority3Qty', 'Priority4Qty']:
        dic = {}
        dic['priority'] = p
        dic['combo'] = sum(one_meat_req_combo['PiecesInBox'] * one_meat_req_combo[p])
        dic['pkg'] = sum(one_meat_req_pkg['PiecesInBox'] * one_meat_req_pkg[p])
        piece_dist_byp.append(dic)
    piece_dist_byp = pd.DataFrame(piece_dist_byp)
    piece_dist_byp_track = piece_dist_byp.loc[(piece_dist_byp['combo'] + piece_dist_byp['pkg']) != 0,]

    t_start = one_meat_hourly.index.min()
    t_end = one_meat_hourly.index.max()

    pkg_ratio = 1 - combo_ratio
    t = t_start
    meat_combo_result = []
    meat_pkg_result = []

    while t <= t_end:
        meat_combo_dic = {}
        meat_pkg_dic = {}
        meat_combo_dic['t'] = t
        meat_pkg_dic['t'] = t

        piece_available = one_meat_hourly[t]
        # initialize the plan
        meat_combo_dic['num'] = 0
        meat_pkg_dic['num'] = 0

        # earliest priority
        while ((len(piece_dist_byp_track) != 0) & (piece_available != 0)):
            one_p = piece_dist_byp_track.iloc[0]
            # print(one_p)
            if one_p.combo == 0:  # packaging only, no need to split
                meat_used = min(piece_available, one_p.pkg)
                new_num = meat_pkg_dic['num'] + meat_used
                meat_pkg_dic['num'] = new_num
                piece_available -= meat_used
                new_value = piece_dist_byp_track.loc[
                                piece_dist_byp_track['priority'] == one_p.priority, 'pkg'] - meat_used
                piece_dist_byp_track.loc[piece_dist_byp_track['priority'] == one_p.priority, 'pkg'] = new_value
            if one_p.pkg == 0:  # combo only, no need to split
                meat_used = min(piece_available, one_p.combo)
                new_num = meat_combo_dic['num'] + meat_used
                meat_combo_dic['num'] = new_num
                piece_available -= meat_used
                # print(meat_used)
                new_value = piece_dist_byp_track.loc[
                                piece_dist_byp_track['priority'] == one_p.priority, 'combo'] - meat_used
                piece_dist_byp_track.loc[piece_dist_byp_track['priority'] == one_p.priority, 'combo'] = new_value
            if ((one_p.combo != 0) & (one_p.pkg != 0)):
                meat_avail_combo = math.ceil(piece_available * combo_ratio)  # need to be integer
                meat_avail_pkg = math.floor(piece_available * pkg_ratio)  # need to be integer
                meat_used_combo = min(meat_avail_combo, one_p.combo)
                new_num = meat_combo_dic['num'] + meat_used_combo
                meat_combo_dic['num'] = new_num
                piece_available -= meat_used_combo
                new_value = piece_dist_byp_track.loc[
                                piece_dist_byp_track['priority'] == one_p.priority, 'combo'] - meat_used_combo
                piece_dist_byp_track.loc[piece_dist_byp_track['priority'] == one_p.priority, 'combo'] = new_value

                meat_used_pkg = min(meat_avail_pkg, one_p.pkg)
                new_num = meat_pkg_dic['num'] + meat_used_pkg
                meat_pkg_dic['num'] = new_num
                piece_available -= meat_used_pkg
                new_value = piece_dist_byp_track.loc[
                                piece_dist_byp_track['priority'] == one_p.priority, 'pkg'] - meat_used_pkg
                piece_dist_byp_track.loc[piece_dist_byp_track['priority'] == one_p.priority, 'pkg'] = new_value

            # update piece_dist_byp_track
            piece_dist_byp_track = piece_dist_byp_track.loc[
                                   (piece_dist_byp_track['combo'] + piece_dist_byp_track['pkg']) != 0, :]
            # print(piece_dist_byp_track)

        meat_combo_result.append(meat_combo_dic)
        meat_pkg_result.append(meat_pkg_dic)
        # move to next hour
        t += 1

    one_meat_hourly_combo = pd.DataFrame(meat_combo_result).set_index('t')['num'].rename(one_meat_hourly.name)
    one_meat_hourly_pkg = pd.DataFrame(meat_pkg_result).set_index('t')['num'].rename(one_meat_hourly.name)
    return one_meat_hourly_combo, one_meat_hourly_pkg


## Function 4.2: plan_break_down_combo_pkg_ratio, main function of Method 2,  get the hourly plan
def plan_break_down_combo_pkg_ratio(meat_and_req, meat_hourly, hour_priority, combo_ratio):
    import pandas as pd

    t_start = min(meat_hourly.index)
    t_end = max(meat_hourly.index)

    packaging_plan = []
    requirements_not_complete = []

    for meat_id in sorted(list(set(meat_and_req.MeatItem))):
        one_meat_hourly = meat_hourly.loc[:, meat_id]
        one_meat_req = meat_and_req.loc[meat_and_req['MeatItem'] == meat_id, :]
        one_meat_req_combo = one_meat_req.loc[one_meat_req['itemkey'] >= 30000, :]
        one_meat_req_pkg = one_meat_req.loc[one_meat_req['itemkey'] < 30000, :]
        # if there is only one prodct, no need to split
        if len(one_meat_req) == 1:
            pkg_dic, needs_by_priority = arrange_one_meat(one_meat_hourly, one_meat_req, t_start, t_end, hour_priority)
            packaging_plan.append(pkg_dic)
            if needs_by_priority[1] + needs_by_priority[2] + needs_by_priority[3] + needs_by_priority[4] != 0:
                requirements_not_complete.append(needs_by_priority)
        if (len(one_meat_req) > 1) & (len(one_meat_req_combo) == 0):  # all for packaging floor
            multiple_pkg_dic, multiple_needs_by_priority = arrange_multiple_meat(one_meat_hourly, one_meat_req, t_start,
                                                                                 t_end, hour_priority)
            # combine two lists
            packaging_plan += multiple_pkg_dic

            for needs_by_priority in multiple_needs_by_priority:
                if needs_by_priority[1] + needs_by_priority[2] + needs_by_priority[3] + needs_by_priority[4] != 0:
                    requirements_not_complete.append(needs_by_priority)
        if (len(one_meat_req) > 1) & (len(one_meat_req_combo) > 0):  # hybrid
            one_meat_hourly_combo, one_meat_hourly_pkg = meat_split_combo_pkg(hour_priority, one_meat_hourly,
                                                                              one_meat_req_combo, one_meat_req_pkg,
                                                                              combo_ratio)

            # plan for combo
            multiple_dic_combo, multiple_needs_by_priority_combo = arrange_multiple_meat(one_meat_hourly_combo,
                                                                                         one_meat_req_combo, t_start,
                                                                                         t_end, hour_priority)
            packaging_plan += multiple_dic_combo
            for needs_by_priority in multiple_needs_by_priority_combo:
                if needs_by_priority[1] + needs_by_priority[2] + needs_by_priority[3] + needs_by_priority[4] != 0:
                    requirements_not_complete.append(needs_by_priority)

            # plan for packaging floor
            multiple_dic_pkg, multiple_needs_by_priority_pkg = arrange_multiple_meat(one_meat_hourly_pkg,
                                                                                     one_meat_req_pkg, t_start, t_end,
                                                                                     hour_priority)
            packaging_plan += multiple_dic_pkg
            for needs_by_priority in multiple_needs_by_priority_pkg:
                if needs_by_priority[1] + needs_by_priority[2] + needs_by_priority[3] + needs_by_priority[4] != 0:
                    requirements_not_complete.append(needs_by_priority)
    return pd.DataFrame(packaging_plan), pd.DataFrame(requirements_not_complete)


# 5. Activity Time Checking (Hourly) for hourly plan
## Function 5.1,hourly_activity_time_check
def hourly_activity_time_check(hourly_req, cap, hour_priority, seq):
    """
    This function is used to check the activity time for each hour.

    Arguments:
    1. hourly_req: a dataframe, the hourly requirements for each sku
    2. cap: capacity dataframe
    3. hour_priority: a dictionary map hour and priority
    4. seq: dataframe, activity sequence for each sku
    """

    import pandas as pd
    # Step1: DataCleaning
    # Only consider activity with max capacity
    cap_cleaned = cap.loc[cap['Max'] > 0, :]

    # Step2: calculate time available for each activity
    ##positions for each activity
    hourly_available_seconds = cap_cleaned["Max"] * 3600
    cap_cleaned.insert(3, "hourly_available_seconds", hourly_available_seconds, True)

    # Step3: calculate time required for each activity
    ##need hourly_req, activity_required for that sku
    # change wide to long table
    hourly_req_melt = pd.melt(hourly_req, id_vars='itemkey', value_vars=hour_priority.keys())
    hourly_req_melt.columns = ['itemkey', 'hour', 'sku_num']
    # add acticitykey and durationseconds
    req_and_activity = hourly_req_melt.merge(seq, how='left', left_on="itemkey", right_on="BomKey")
    # only keep acitivity with max capacity
    req_and_activity_clean = req_and_activity.merge(cap_cleaned, left_on="ActivityFunctionKey", right_on="Activity_Num")
    req_and_activity_clean = req_and_activity_clean[['hour', 'sku_num', 'Activity_Num', 'DurationSeconds']]
    # calculate time required
    time_required_df = req_and_activity_clean.assign(
        time_required=req_and_activity_clean.eval('sku_num*DurationSeconds')).groupby(['hour', 'Activity_Num']).sum()
    time_required_df.reset_index(inplace=True)

    # Step4: compare
    time_comparison = time_required_df.merge(cap_cleaned[["Activity_Num", "hourly_available_seconds"]], how='left',
                                             left_on='Activity_Num', right_on='Activity_Num')
    time_comparison = time_comparison.assign(
        time_still_need=time_comparison.eval("time_required-hourly_available_seconds"))
    time_comparison = time_comparison.loc[
        time_comparison['time_still_need'] > 0, ['hour', 'Activity_Num', 'time_required', 'hourly_available_seconds',
                                                 'time_still_need']]

    print("time_comparison", time_comparison)
    if len(time_comparison) == 0:
        return "Pass avtivity time checking!"
    if len(time_comparison) > 0:
        return time_comparison


# 6. Adjust Infeasible Plan
## Function 6.1: adjust_infeasible_plan
def adjust_infeasible_plan(original_plan, req, cap, seq, hour_priority, adjusting_rate):
    """
    Adjust houry plan

    Arguments:
    1. original_plan: original hourly plan
    2. req: 4 priority plan
    3. cap: capacity dataframe
    4. seq: sequence dataframe
    5. hour_priority: relationship between hour and priority
    6. adjusting_rate: the rate of moving current plans to next hour
    """
    import math
    end_hour = original_plan.columns[-1]

    new_plan = original_plan.copy()

    # calculate req_cum to make sure the adjustment can finish req in 4 priorities
    req_cum = req.copy()
    req_cum.insert(7, "p1_cum", req_cum['Priority1Qty'])
    req_cum.insert(9, "plNum", req_cum['p2_cum'] + req_cum['Priority3Qty'])
    req_cum.insert(8, "p2_cum", req_cum['p1_cum'] + req_cum['Priority2Qty'])
    req_cum.insert(10, "p4_cum", req_cum['p3_cum'] + req_cum['Priority4Qty'])
    ## to have the same order as new_plan
    req_cum = new_plan.loc[:, ['meatkey', 'itemkey']].merge(
        req_cum.loc[:, ['itemkey', 'p1_cum', 'p2_cum', 'p3_cum', 'p4_cum']], how='left', left_on='itemkey',
        right_on='itemkey')

    # dictionary, key:activity_id, value:list of skus need that priority
    acticity_skus = {}
    for activity_id in cap['Activity_Num'].values:
        acticity_skus[activity_id] = list(set(seq.loc[seq['ActivityFunctionKey'] == activity_id, 'BomKey']))

    infeasible_table = hourly_activity_time_check(new_plan, cap, hour_priority, seq)
    # current_hour = infeasible_table[:1].hour.values[0]
    current_hour = infeasible_table.hour.values[0]  # remove slicer
    current_ac = infeasible_table[:1].Activity_Num.values[0]

    while current_hour < end_hour:
        skus_use_activity_hour_plan = new_plan.loc[[i in acticity_skus[current_ac] for i in new_plan['itemkey']], :]
        target_plan = skus_use_activity_hour_plan.loc[skus_use_activity_hour_plan[current_hour] != 0, :]
        target_req = req.loc[[i in target_plan['itemkey'].values for i in req['itemkey']], :]
        # adjust latter priority plan first
        current_p = hour_priority[current_hour]
        req_not_need_current_p = target_req.loc[target_req['Priority' + str(current_p) + "Qty"] == 0, :]
        # get final target plan
        if len(req_not_need_current_p) == 0:  # if all plans are need in current priority
            current_p_hours = [k for k, v in hour_priority.items() if v == current_p]
            if current_hour < max(current_p_hours):
                final_target_plan = target_plan
            elif current_hour == max(current_p_hours):
                # if at end of current priority, it might leads to infeasible priority req(cannot finish req on-time)
                # final_target_plan should be plan_cum-req_until_current_p
                ##plan_cum is current plan, current priority cummulated
                plan_cum = target_plan.loc[:, min(hour_priority.keys())]  # First hour
                for h in range(min(hour_priority.keys()) + 1, max(current_p_hours) + 1):
                    plan_cum += target_plan.loc[:, h]

                target_req_cum = req_cum.loc[
                    [i in target_plan['itemkey'].values for i in req_cum['itemkey']], "p" + str(current_p) + "_cum"]
                planed_more = plan_cum.values - target_req_cum
                plans_can_adjust_list = [min(target_plan[current_hour].values[i], planed_more.values[i]) for i in
                                         range(len(target_plan))]
                target_plan.loc[:, current_hour] = plans_can_adjust_list
                final_target_plan = target_plan

        else:  # >0
            target_plan
            final_target_plan = target_plan.loc[
                                [i in req_not_need_current_p['itemkey'].values for i in target_plan['itemkey']], :]
        # shift plans in current hour to next hour by adjusting rate
        adjustment_list = [math.floor(i * adjusting_rate) for i in final_target_plan[current_hour]]
        if sum(adjustment_list) == 0:
            # the max one adjust by 1 unit
            adjustment_list = [(i == final_target_plan[current_hour].max()) * 1 for i in
                               final_target_plan[current_hour]]
        final_target_plan.loc[:, current_hour] -= adjustment_list
        final_target_plan.loc[:, current_hour + 1] += adjustment_list
        # get new plan
        row_adjust = [i in final_target_plan['itemkey'].values for i in new_plan['itemkey']]
        new_plan.loc[row_adjust, :] = final_target_plan

        ####Move before: To Do: need to check meat feasibility here
        ####Move afterwards: To Do: check can not meet priority requirements

        # check activty time
        infeasible_table2 = hourly_activity_time_check(new_plan, cap, hour_priority, seq)
        # check
        # infeasible_table2
        current_ac = infeasible_table2[:1].Activity_Num.values[0]
        current_hour = infeasible_table2[:1].hour.values[0]
        # current_hour = infeasible_table2.hour.values[0] # remove slicer

    return new_plan, infeasible_table2


# 7. Get Best plan
def get_best_plan(meat_and_req, meat_hourly, hour_priority, cap, seq, req, method1_adjusting_rate_list,
                  method2_combo_ratio_list, method2_adjusting_rate_list, requirements_not_complete_method1=None):
    """
    Get the best plan (minimum total labor deviation)

    """
    import pandas as pd
    # After passing meat and time feasibility check
    # try different breakdowns and choose the best one
    ## There're two ways of break down
    result = []

    # Method1
    if len(method1_adjusting_rate_list) > 0:
        for adjusting_rate in method1_adjusting_rate_list:
            dic = {}
            dic['method'] = 'method1'
            dic['combo_ratio'] = '-'
            dic['adjusting_rate'] = adjusting_rate
            print(dic['method'], dic['combo_ratio'], dic['adjusting_rate'])

            ### Method 1: evenly distributed(according to meat required)
            hourly_req, _ = plan_break_down(meat_and_req=meat_and_req,
                                            meat_hourly=meat_hourly,
                                            hour_priority=hour_priority)
            #### Activity hourly check
            infeasible_hourly_plans = hourly_activity_time_check(hourly_req,
                                                                 cap,
                                                                 hour_priority,
                                                                 seq)
            # shows the list on jobs not matching feasibilty
            print(infeasible_hourly_plans)
            #### If current plan is not feasible, adjust the plan
            if len(infeasible_hourly_plans) > 0:
                print('current plan is infeasible')
                new_plan, new_infeasible_table = adjust_infeasible_plan(hourly_req,
                                                                        req,
                                                                        cap,
                                                                        seq,
                                                                        hour_priority,
                                                                        adjusting_rate=adjusting_rate)
            elif len(infeasible_hourly_plans) == 0:
                new_plan, new_infeasible_table = hourly_req, _
            #### index calculation: total labor deviation
            dic['new_plan'] = new_plan
            dic['stdev'] = hourly_total_position_stdev(new_plan,
                                                       cap,
                                                       hour_priority,
                                                       seq, plot=False)
            result.append(dic)

    # Method2
    if len(method2_combo_ratio_list) > 0:
        for combo_ratio in method2_combo_ratio_list:
            for adjusting_rate in method2_adjusting_rate_list:
                dic = {}
                dic['method'] = 'method2'
                dic['combo_ratio'] = combo_ratio
                dic['adjusting_rate'] = adjusting_rate
                print(dic['method'], dic['combo_ratio'], dic['adjusting_rate'])

                ### Method 2: set a ratio first
                hourly_req, _ = plan_break_down_combo_pkg_ratio(meat_and_req,
                                                                meat_hourly,
                                                                hour_priority,
                                                                combo_ratio=combo_ratio)

                #### Activity hourly check
                infeasible_hourly_plans = hourly_activity_time_check(hourly_req,
                                                                     cap,
                                                                     hour_priority,
                                                                     seq)

                #### If current plan is not feasible, adjust the plan
                if len(infeasible_hourly_plans) > 0:
                    new_plan, new_infeasible_table = adjust_infeasible_plan(hourly_req,
                                                                            req,
                                                                            cap,
                                                                            seq,
                                                                            hour_priority,
                                                                            adjusting_rate=0.01)
                elif len(infeasible_hourly_plans) == 0:
                    new_plan, new_infeasible_table = hourly_req, requirements_not_complete_method1
                #### index calculation: total labor deviation
                dic['new_plan'] = new_plan
                dic['stdev'] = hourly_total_position_stdev(new_plan, cap, hour_priority, seq, plot=False)
                result.append(dic)

    # get the best plan
    result = pd.DataFrame(result)
    best_plan = result.loc[result.stdev == result.stdev.min(), 'new_plan'][0]

    return result, best_plan


# 8. Ratio calculation
## Function 8.1 EEO
# EEO calculation-Max Overall Equipment Effectiveness
##For Each equipment: (Good Count × Ideal Cycle Time) / Planned Production Time
def EEO_caculation(hourly_req, cap, hour_priority, seq):
    """
    calculate EEO for an hourly plan

    #Note: Step1 to Step3 are exactily the same as logic in hourly_activity_time_check function
    Arguments same to hourly_activity_time_check() :
    1. hourly_req: a dataframe, the hourly requirements for each sku
    2. cap: capacity dataframe
    3. hour_priority: a dictionary map hour and priority
    4. seq: dataframe, activity sequence for each sku

    It will return 2 result:
    1. OEE: overall OEE
    2. result_table: OEE for each activity
    """
    import pandas as pd

    # Step1: DataCleaning
    # Only consider activity with max capacity
    cap_cleaned = cap.loc[cap['Max'] > 0, :]

    # Step2: calculate time available for each activity
    ##positions for each activity
    hourly_available_seconds = cap_cleaned["Max"] * 3600
    cap_cleaned.insert(3, "hourly_available_seconds", hourly_available_seconds, True)

    # Step3: calculate time required for each activity
    ##need hourly_req, activity_required for that sku
    # change wide to long table
    hourly_req_melt = pd.melt(hourly_req, id_vars='itemkey', value_vars=hour_priority.keys())
    hourly_req_melt.columns = ['itemkey', 'hour', 'sku_num']
    # add acticitykey and durationseconds
    req_and_activity = hourly_req_melt.merge(seq, how='left', left_on="itemkey", right_on="BomKey")
    # only keep acitivity with max capacity
    req_and_activity_clean = req_and_activity.merge(cap_cleaned, left_on="ActivityFunctionKey", right_on="Activity_Num")
    req_and_activity_clean = req_and_activity_clean[['hour', 'sku_num', 'Activity_Num', 'DurationSeconds']]
    # calculate time required
    time_required_df = req_and_activity_clean.assign(
        time_required=req_and_activity_clean.eval('sku_num*DurationSeconds')).groupby(['hour', 'Activity_Num']).sum()
    time_required_df.reset_index(inplace=True)

    # Step4: get all activity time table
    all_activity_time = time_required_df.merge(
        cap_cleaned[["Activity_Num", "Activity_Desc", "hourly_available_seconds", "Max"]], how='left',
        left_on="Activity_Num", right_on="Activity_Num")
    all_activity_time = all_activity_time.assign(
        time_still_need=all_activity_time.eval("time_required-hourly_available_seconds"))
    all_activity_time = all_activity_time.loc[:,
                        ['hour', 'Activity_Num', 'Activity_Desc', 'Max', 'time_required', 'hourly_available_seconds',
                         'time_still_need']]

    print(all_activity_time.columns)

    # drop 0 time_required. In these hours the machine does not need to open
    activity_check_nonzero = all_activity_time.loc[all_activity_time['time_required'] != 0]

    # Step5: Calculate EEO
    # calculate planned production time
    result_table = activity_check_nonzero.groupby('Activity_Num').agg(
        {'hour': ['count'], 'time_required': ['sum'], 'Max': ['mean']}).reset_index()
    hours_num = result_table.hour.loc[:, 'count']
    time_required = result_table.time_required.loc[:, 'sum']
    capacity = result_table.Max.loc[:, 'mean']
    result_table = result_table.loc[:, ["Activity_Num"]]
    result_table.insert(1, "hours_num", hours_num)
    result_table.insert(2, "time_required", time_required)
    result_table.insert(3, "capacity", capacity)

    time_required = result_table.time_required
    total_time_required = time_required.sum()

    time_available = result_table.hours_num * result_table.capacity * 3600
    total_time_available = time_available.sum()
    OEE = total_time_required / total_time_available

    result_table.insert(1, "OEE", time_required / time_available)
    return OEE, result_table


## Function 8.2: Total Labor deviation
def hourly_total_position_stdev(hourly_req, cap, hour_priority, seq, plot):
    """
    calculate the hourly total labor deviation.
    Calculation Logic:
        use required time/3600, get the position_num in each hour for each activity.
        Sum up position_num for each hour
        Calculate the standard deviation of hourly total position num

    #Note: Step1 to Step4 are exactily the same as logic in EEO_calculation
    Arguments same to hourly_activity_time_check() :
    1. hourly_req: a dataframe, the hourly requirements for each sku
    2. cap: capacity dataframe
    3. hour_priority: a dictionary map hour and priority
    4. seq: dataframe, activity sequence for each sku
    5. plot: boolen, true means plot the graph

    It will return:
    1. standard deviation of hourly total position num
    """
    import pandas as pd
    import math
    import statistics
    import matplotlib.pyplot as plt
    from matplotlib.ticker import MaxNLocator
    # Step1: DataCleaning
    # Only consider activity with max capacity
    cap_cleaned = cap.copy()

    # Step2: calculate time available for each activity
    ##positions for each activity
    hourly_available_seconds = cap_cleaned["Max"] * 3600
    cap_cleaned.insert(3, "hourly_available_seconds", hourly_available_seconds, True)

    # Step3: calculate time required for each activity
    ##need hourly_req, activity_required for that sku
    # change wide to long table
    hourly_req_melt = pd.melt(hourly_req, id_vars='itemkey', value_vars=hour_priority.keys())
    hourly_req_melt.columns = ['itemkey', 'hour', 'sku_num']
    # add acticitykey and durationseconds
    req_and_activity = hourly_req_melt.merge(seq, how='left', left_on="itemkey", right_on="BomKey")

    # only keep acitivity with max capacity
    req_and_activity_clean = req_and_activity.merge(cap_cleaned, left_on="ActivityFunctionKey", right_on="Activity_Num")
    req_and_activity_clean = req_and_activity_clean[['hour', 'sku_num', 'Activity_Num', 'DurationSeconds']]

    # calculate time required
    time_required_df = req_and_activity_clean.assign(
        time_required=req_and_activity_clean.eval('sku_num*DurationSeconds')).groupby(
        ['hour', 'Activity_Num']).sum().reset_index()

    # Step4: get all activity time table
    all_activity_time = time_required_df.merge(
        cap_cleaned[["Activity_Num", "Activity_Desc", "hourly_available_seconds", "Max"]], how='left',
        left_on="Activity_Num", right_on="Activity_Num")
    all_activity_time = all_activity_time.assign(
        time_still_need=all_activity_time.eval("time_required-hourly_available_seconds"))
    all_activity_time = all_activity_time.loc[:,
                        ['hour', 'Activity_Num', 'Activity_Desc', 'Max', 'time_required', 'hourly_available_seconds',
                         'time_still_need']]

    # Step5: calculate position_num
    all_activity_time.insert(7, "position_num",
                             list(map(lambda x: math.ceil(x), all_activity_time['time_required'] / 3600)))

    # Step6: Calculation hourly position_num standard distribution
    stdev = statistics.stdev(all_activity_time.groupby('hour').sum('position_num')['position_num'])

    # Step7:if plot = True, plot the distribution of total position num
    if plot == True:
        total_position_num = all_activity_time.groupby('hour').sum('position_num')['position_num']
        position_num = total_position_num.values
        hour = total_position_num.index.values

        fig = plt.figure()
        ax = fig.add_axes([0, 0, 1.5, 1])
        ax.bar(hour, position_num)
        plt.xticks(hour)
        plt.xlabel('hour')
        plt.ylabel('position_num')

        plt.gca().yaxis.set_major_locator(MaxNLocator(integer=True))

        plt.title("Hourly Total Position Num Distribution")
        plt.show()

    return stdev


# 9.Visualize the Result
def visualize_estimated_position_num(hourly_req, cap, hour_priority, seq):
    """
    Estimate position_num in each hour

    #Compared with hourly_activity_time_check function
    1. cap_cleaned include all activities, since also need to estimate activity without max capacity
    2. add Activity_Desc in all_activity_time

    Arguments same to hourly_activity_time_check() :
    1. hourly_req: a dataframe, the hourly requirements for each sku
    2. cap: capacity dataframe
    3. hour_priority: a dictionary map hour and priority
    4. seq: dataframe, activity sequence for each sku
    """
    import pandas as pd
    import math
    import matplotlib.pyplot as plt
    from matplotlib.ticker import MaxNLocator

    # Step1: DataCleaning
    # Only consider activity with max capacity
    cap_cleaned = cap.copy()

    # Step2: calculate time available for each activity
    ##positions for each activity
    hourly_available_seconds = cap_cleaned["Max"] * 3600
    cap_cleaned.insert(3, "hourly_available_seconds", hourly_available_seconds, True)

    # Step3: calculate time required for each activity
    ##need hourly_req, activity_required for that sku
    # change wide to long table
    hourly_req_melt = pd.melt(hourly_req, id_vars='itemkey', value_vars=hour_priority.keys())
    hourly_req_melt.columns = ['itemkey', 'hour', 'sku_num']
    # add acticitykey and durationseconds
    req_and_activity = hourly_req_melt.merge(seq, how='left', left_on="itemkey", right_on="BomKey")

    # only keep acitivity with max capacity
    req_and_activity_clean = req_and_activity.merge(cap_cleaned, left_on="ActivityFunctionKey", right_on="Activity_Num")
    req_and_activity_clean = req_and_activity_clean[['hour', 'sku_num', 'Activity_Num', 'DurationSeconds']]

    # calculate time required
    time_required_df = req_and_activity_clean.assign(
        time_required=req_and_activity_clean.eval('sku_num*DurationSeconds')).groupby(
        ['hour', 'Activity_Num']).sum().reset_index()

    # Step4: get all activity time table
    all_activity_time = time_required_df.merge(
        cap_cleaned[["Activity_Num", "Activity_Desc", "hourly_available_seconds", "Max"]], how='left',
        left_on="Activity_Num", right_on="Activity_Num")
    all_activity_time = all_activity_time.assign(
        time_still_need=all_activity_time.eval("time_required-hourly_available_seconds"))
    all_activity_time = all_activity_time.loc[:,
                        ['hour', 'Activity_Num', 'Activity_Desc', 'Max', 'time_required', 'hourly_available_seconds',
                         'time_still_need']]

    # Step5: Plot the results
    i = 1
    for activity_num in set(all_activity_time.Activity_Num):
        one_activity_df = all_activity_time.loc[all_activity_time.Activity_Num == activity_num, :]

        activity_desc = one_activity_df.Activity_Desc.values[0]
        position_num = [math.ceil(i) for i in one_activity_df.time_required / 3600]
        hour = list(one_activity_df.hour.values)
        max_cap = one_activity_df.Max.values[0]

        fig = plt.figure()
        ax = fig.add_axes([0, 0, 1.5, 1])
        ax.bar(hour, position_num)
        plt.xticks(hour)
        plt.xlabel('hour')
        plt.ylabel('position_num')

        plt.plot([6, 22], [max_cap, max_cap], 'k-', lw=2, dashes=[2, 2])
        plt.gca().yaxis.set_major_locator(MaxNLocator(integer=True))

        plt.title(f"{activity_num}:{activity_desc}")
        plt.show()
        i += 1


if __name__ == "__main__":
    # Input Files
    import pandas as pd
    import math

    names = locals()
    import matplotlib.pyplot as plt
    from matplotlib.ticker import MaxNLocator
    import statistics

    # Sequence table
    seq = pd.read_excel("Q:\Operations\Industrial Engineering\Maxim\Packaging tool\Files/Activities.xlsx", sheet_name='Product Seqeunce')

    # Maximum Capacity
    # cap=pd.read_excel("Files/Activities.xlsx", sheet_name='Activity Cap')
    cap = pd.read_excel("Q:\Operations\Industrial Engineering\Maxim\Packaging tool\Files/Activities_adjust.xlsx", sheet_name='Activity Cap')

    # Products and Meat Relationship Table
    ProdMeat = pd.read_excel("Q:\Operations\Industrial Engineering\Maxim\Packaging tool\Files/Activities.xlsx", sheet_name='Products and Meat')

    # Four Priority Requirement
    req = pd.read_excel("Q:\Operations\Industrial Engineering\Maxim\Packaging tool\Files/req wihtout byproducts.xlsx", sheet_name="Sheet1")

    # Priority Meat Input
    # meat=pd.read_excel("Files/Meats.xlsx",  sheet_name ='Priority Meat Input') #delected the byproduct,
    meat = pd.read_excel("Q:\Operations\Industrial Engineering\Maxim\Packaging tool\Files/Meats_adjust_v3.xlsx", sheet_name='Priority Meat Input')  # delected the byproduct,

    # Hourly Meat Input
    # meat_hourly = pd.read_excel("Files/hourly_meat_input.xlsx",index_col = 0)

    meat_hourly = pd.read_excel("Q:\Operations\Industrial Engineering\Maxim\Packaging tool\Files/hourly_meat_input_adjustment_v3.xlsx", index_col=0)

    # relationship between hour and priority
    ## key represents hour, value represents priority
    hour_priority = {
        6: 1,
        7: 1,
        8: 1,
        9: 1,
        10: 1,
        11: 1,
        12: 1,
        13: 1,
        14: 1,
        15: 2,
        16: 2,
        17: 3,
        18: 3,
        19: 4,
        20: 4,
        21: 4,
        22: 4
        }

    # # the code
    new_req = req.merge(ProdMeat, left_on='itemkey', right_on='FinishedGoodProductCode', how='left')

    req = req.loc[req["PiecesInBox"] != 0, :]

    # exclude byproduct(just include meat_id in Meat table)
    meat_hourly = meat_hourly.loc[:, list(meat.Meat.values)]

    # combine meat inputs and requirements
    meat_and_req = req.merge(ProdMeat, left_on='itemkey', right_on='FinishedGoodProductCode', how='left')

    meat_pieces_check(ProdMeat, req, meat)
    activity_time_check(req, hour_priority, cap, seq)

    # %%time
    method1_adjusting_rate_list = [0.01, 0.03]
    method2_combo_ratio_list = [0.3, 0.7]
    method2_adjusting_rate_list = [0.01]
    result, best_plan = get_best_plan(meat_and_req,
                                      meat_hourly,
                                      hour_priority,
                                      cap,
                                      seq,
                                      req,
                                      method1_adjusting_rate_list,
                                      method2_combo_ratio_list,
                                      method2_adjusting_rate_list)
    # %%

    print(result)


    hourly_total_position_stdev(best_plan,cap,hour_priority,seq,plot=True)

    OEE, OEE_table=EEO_caculation(best_plan,cap,hour_priority,seq)
    print(OEE_table)


    # visualize_estimated_position_num(best_plan,cap,hour_priority,seq)


    hourly_packaging_plan_method1, requirements_not_complete_method1 = plan_break_down(meat_and_req, meat_hourly, hour_priority)
    print(hourly_packaging_plan_method1)

    # Imort
    import pandas as pd
    import math
    import numpy as np
    names = locals()
    import matplotlib.pyplot as plt
    from matplotlib.ticker import MaxNLocator
    import statistics
    # from GenerateHourlyPlan import *
    import pyodbc as odbc

    # Import Data
    # Sequence table
    # seq=pd.read_excel("Q:\Operations\Industrial Engineering\Maxim\Packaging tool\Files/Activities.xlsx", sheet_name='Product Seqeunce')
    server = 'cmpcsb01'
    database = 'conestoga'
    username = 'remotequery'
    password = "excel"
    cnxn = odbc.connect(
        'DRIVER={SQL Server}; SERVER=' + server + ';DATABASE=' + database + ';UID=' + username + ';PWD=' + password,
        trusted_connection='no'
        )
    cursor = cnxn.cursor()

    query = '''select
            convert(INT, bomkey) as BomKey,
            CONVERT(INT, sequenceno) as SequenceNo,
             CONVERT(INT, ActivityFunctionKey) as ActivityFunctionKey,
             CONVERT(INT, DurationMinutes) as DurationSeconds
    
    FROM [conestoga].[dbo].[DimBOMActivitiesFunctions]
     where BomKey>10000
     '''

    seq = pd.read_sql(query, cnxn)



    # Maximum Capacity
    # cap=pd.read_excel("ActiviActivity Cap Modties.xlsx", sheet_name='Activity Cap')
    # cap=pd.read_excel("Files/Activities_adjust.xlsx", sheet_name='Activity Cap')
    cap=pd.read_excel("Q:\Operations\Industrial Engineering\Maxim\Packaging tool\Activities_adjust.xlsx", sheet_name='Activity Cap Mod')



    # Products and Meat Relationship Table
    # ProdMeat=pd.read_excel("Files/Activities.xlsx",
    #                     #    sheet_name='Products and Meat'
    #                     sheet_name='dataProdMeat'
    #                        )
    # print(ProdMeat.shape)

    server = 'cmpcsb01'
    database = 'conestoga'
    username = 'remotequery'
    password = "excel"
    cnxn = odbc.connect('DRIVER={SQL Server}; SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password,
                        # trusted_connection='yes'
                        )
    cursor = cnxn.cursor()
    # print(cursor)
    query = '''SELECT
               CAST(Itemkey as int) as FinishedGoodProductCode,
               --Pieces,
               Cast(ItemSort4Key as INT) as MeatItem
                FROM dimitem
                WHERE Itemkey >  ? and Itemkey < ?
                --and ItemSort4Key > 0
                '''
    ProdMeat = pd.read_sql(query, cnxn,
                       params=['10000', '39999']
                    )

    # ProdMeat.head()
    # print("ss", ProdMeat.shape)


    # Four Priority Requirement
    # req = pd.read_excel("Files/req wihtout byproducts.xlsx")
    req = pd.read_excel("Q:\Operations\Industrial Engineering\Maxim\Packaging tool\Files/req wihtout byproducts.xlsx", sheet_name='data (2)')
    # req = pd.read_excel("Files/Cut Sheet 20221024", sheet_name='Sheet2' )

    # Priority Meat Input
    # meat=pd.read_excel("Files/Meats.xlsx",  sheet_name ='Priority Meat Input') #delected the byproduct,
    # meat=pd.read_excel("Files/Meats_adjust_v3.xlsx",  sheet_name ='Priority Meat Input') #delected the byproduct,
    # meat=pd.read_excel("Files/Meats_adjust_v3.xlsx",  sheet_name ='meat prior') #delected the byproduct,


    server = 'cmpcsb01'
    database = 'packagingplanner'
    username = 'remotequery'
    password = "excel"
    cnxn = odbc.connect('DRIVER={SQL Server}; SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password,
                        trusted_connection='no'
                        )
    cursor = cnxn.cursor()
    print(cursor)

    query = '''SELECT
    
    cast(MeatItem as INT) as Meat,
    SUM(P1) AS 'Priority 1',
    SUM(P2) AS 'Priority 2',
    SUM(P3) AS 'Priority 3',
    SUM(P4) AS 'Priority 4'
    FROM     vwPrepForCutInputPriorities
    where productiondate= ? and MeatItem < ?
    GROUP BY MeatItem'''
    meat = pd.read_sql(query, cnxn,
                       params=['20221021', 800]
                    )





    # Hourly Meat Input
    # meat_hourly = pd.read_excel("Files/hourly_meat_input.xlsx",index_col = 0)

    meat_hourly = pd.read_excel(
    # "Files/hourly_meat_input_adjustment_v3.xlsx",index_col = 0, sheet_name='Sheet1'
    "Q:\Operations\Industrial Engineering\Maxim\Packaging tool\Files/PackagingSimulationInputs v4.xlsx", index_col = 0, sheet_name='Summ'
     )


    # relationship between hour and priority
    ## key represents hour, value represents priority
    hour_priority={
        6:1,
        7:1,
        8:1,
        9:1,
        10:1,
        11:1,
        12:1,
        13:1,
        14:1,
        15:2,
        16:2,
        17:3,
        18:3,
        19:4,
        20:4,
        21:4,
        22:4
        }


    # the code
    meat_hourly.columns = np.dtype('int64').type(meat_hourly.columns)
    #Some products have 0 PiecesInBox, these skus are also excluded
    req = req.loc[req["PiecesInBox"]!=0,:]
    print(req)
    meat_hourly
    print(meat_hourly)
    # # exclude byproduct(just include meat_id in Meat table)
    meat_hourly = meat_hourly.loc[:,list(meat.Meat.values)]
    meat_hourly = meat_hourly.loc[:, list(meat.Meat.values)]

    # print(meat_hourly)
    # #combine meat inputs and requirements
    meat_and_req = req.merge(ProdMeat, left_on='itemkey',  right_on='FinishedGoodProductCode', how='left')
    #
    # print(meat_and_req.head())

    meat_pieces_check(ProdMeat,req, meat)
    activity_time_check(req,hour_priority,cap,seq)
    #
    # # Function 7
    method1_adjusting_rate_list=[0.01,0.03]
    method2_combo_ratio_list=[0.3,0.7]
    method2_adjusting_rate_list=[0.01]
    result, best_plan=get_best_plan(meat_and_req,
                                    meat_hourly,
                                    hour_priority,
                                    cap,
                                    seq,
                                    req,
                                    method1_adjusting_rate_list,
                                    method2_combo_ratio_list,
                                    method2_adjusting_rate_list)


    print(result)


    hourly_total_position_stdev(best_plan,cap,hour_priority,seq,plot=True)

    OEE, OEE_table=EEO_caculation(best_plan,cap,hour_priority,seq)
    print(OEE_table)


    # visualize_estimated_position_num(best_plan,cap,hour_priority,seq)


    hourly_packaging_plan_method1, requirements_not_complete_method1 = plan_break_down(meat_and_req, meat_hourly, hour_priority)
    print(hourly_packaging_plan_method1)
