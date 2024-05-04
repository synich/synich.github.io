#!/usr/bin/env python3.9

def _urlstr_filldict(s, d):
    """split str, urldecodde and fill in dict"""
    from urllib.parse import unquote
    if s == "":
        return
    arr = s.split("&")
    for i in range(len(arr)):
        kv = arr[i].split("=")
        d[kv[0]] = unquote(kv[1])

def cgi_entry():
    import sys
    import os
    print("Content-Type: text/html; charset=UTF-8\n")

    try:
        method = os.environ["REQUEST_METHOD"]
        if method == "GET":
            params = os.environ["QUERY_STRING"]
        else:
            params = sys.stdin.read()
        path_info = os.environ["PATH_INFO"]
        pth_arr: list = path_info.strip("/").split("/")
        m = __import__(pth_arr[0])
        mth = getattr(m, pth_arr[1])
        prm_dict = {}
        _urlstr_filldict(params, prm_dict)
        mth(prm_dict)
    except Exception as e:
        print(f'<div style="background:#ff0;">oops: {method} {path_info} {params}</div>')
        if 0 == 1:
            print(e)
            import traceback, sys
            t, v, b = sys.exc_info()
            traceback.print_tb(b, file=sys.stdout)

cgi_entry()

