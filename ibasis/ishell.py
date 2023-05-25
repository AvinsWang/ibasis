import os
import os
import subprocess
import os.path as osp


def exec_shell(cmd, decode_type='utf-8', is_verbose=False, is_res=False):
    if is_verbose:
        print(f"{'-'*(len(cmd)+1)}\n{cmd}\n{'-'*(len(cmd)+1)}")
    if is_res:
        res = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        result = res.stdout.read()
        res.wait()
        res.stdout.close()
        if decode_type is not None:
            result = result.decode(decode_type)
        return result
    else:
        os.system(cmd)

