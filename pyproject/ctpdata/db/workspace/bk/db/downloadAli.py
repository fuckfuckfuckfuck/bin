import os

# list_files = ["20150618.7z","20150617.7z","20150616.7z","20150615.7z"]
# list_files = ["20150612.7z","20150611.7z"]
# list_files = ["20150608.7z","20150609.7z","20150610.7z"]
# list_files = ["""{20150601.7z,20150602.7z,20150603.7z}"""] 
# list_files = []
# list_files = ["20150601.7z","20150602.7z","20150603.7z","20150604.7z","20150605.7z"]
# list_files = ["20150526.7z","20150527.7z",,"20150528.7z""20150529.7z"]
list_files = ["20150525.7z"]


cmd = """pscp -v dell@218.244.141.201:/alidata/ctp/test7/7d/20150619.7z E:\\data\\alidata\\ctp\\test7\\7d"""
cmd1 = """pscp -v dell@218.244.141.201:/alidata/ctp/test7/7d/"""
cmd2 = """ E:\\data\\alidata\\ctp\\test7\\7d"""

for file in list_files:
    cmd = cmd1 + file + cmd2
    # print cmd
    os.system(cmd)

