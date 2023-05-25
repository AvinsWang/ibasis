def f_dic(dic, only_key=False, only_value=False, joint_label=',', kv_joint_label=':'):
    # {'a':1, 'b':2} -> 'a:1,b:2'
    if only_key:
        return joint_label.join([k for k, v in dic.items()])
    elif only_value:
        return joint_label.join([v for k, v in dic.items()])
    else:
        return joint_label.join([f'{k}{kv_joint_label}{v}\n' for k, v in dic.items()])
