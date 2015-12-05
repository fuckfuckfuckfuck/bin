import re

# ctp
# line = "18246655 [139707331954432] DEBUG test <> - 20140627 au1408   263.25 264.05 263.8 212 262.45 263.25 262.45 16 4.2072e+06 220 1.79769e+308 1.79769e+308 277.25 250.8 02:00:15 0 262.75 2 263.3 1 262950 255957"
# mkt_pattern = "(\d+)\s\[(\d+)\]\s([A-Z]+)\stest\s<>\s-\s(\d+)\s(\w+)\s+(\d+\.?\d*[eE]?[+]?\d*)\s(\d+\.?\d*[eE]?[+]?\d*)\s(\d+\.?\d*[eE]?[+]?\d*)\s(\d+\.?\d*[eE]?[+]?\d*)\s(\d+\.?\d*[eE]?[+]?\d*)\s(\d+\.?\d*[eE]?[+]?\d*)\s(\d+\.?\d*[eE]?[+]?\d*)\s(\d+\.?\d*[eE]?[+]?\d*)\s(\d+\.?\d*[eE]?[+]?\d*)\s(\d+\.?\d*[eE]?[+]?\d*)\s(\d+\.?\d*[eE]?[+]?\d*)\s(\d+\.?\d*[eE]?[+]?\d*)\s(\d+\.?\d*[eE]?[+]?\d*)\s(\d+\.?\d*[eE]?[+]?\d*)\s(\d\d:\d\d:\d\d)\s(\d+)\s(\d+\.?\d*[eE]?[+]?\d*)\s(\d+\.?\d*[eE]?[+]?\d*)\s(\d+\.?\d*[eE]?[+]?\d*)\s(\d+\.?\d*[eE]?[+]?\d*)\s(\d+\.?\d*[eE]?[+]?\d*)\s(\d+)"
# line = "09:14:00|300|3499.8|3659|3841730000.0|118117|3503.0|741|778717000.0|67395"
# pattern = "(\d+:\d+:\d+)\|(\d+)\|(\d+\.?\d*)\|(\d+)\|(\d+\.?\d*[eE]?[+]?\d*)\|(\d+)\|(\d+\.?\d*)\|(\d+)\|(\d+\.?\d*[eE]?[+]?\d*)\|(\d+)"


# jzt
line = "2015/4/30 18:59:27 6040 35572 214561 116332 1"
# pattern = "(\d+/\d+/\d+)\s(\d+:\d+:\d+)\s(\d+\.?\d*)\s(\d+)\s(\d+\.?\d*)\s(\d+)\s([01])"
pattern_jzt = "(\d+)/(\d+)/(\d+)\s(\d+):(\d+):(\d+)\s(\d+\.?\d*)\s(\d+)\s(\d+\.?\d*)\s(\d+)\s([01])"
p_jzt = re.compile(pattern_jzt)

##ree = p_jzt.match(line)
##ree = ree.groups()
##np.datetime64(ree[0]+'-'+timeFill(ree[1])+'-'+timeFill(ree[2])+'T'+timeFill(ree[3])+':'+ree[4]+':'+ree[5])

# dictionary:
# m = re.match(r"(?P<date>\w+) (?P<last_name>\w+)", "Malcolm Reynolds")
# m = re.match(r"(?P<date>\d+/\d+/\d+)\s(?P<time>\d+:\d+:\d+)\s(?P<price>\d+\.?\d*)\s(?P<vol>\d+)\s(?P<amount>\d+\.?\d*)\s(?<openint>\d+)\s(?P<binited>[01])", line)
# m.groupdict()

# pattern_log = "(\w+)\s([(SQ)|(DQ)|(ZQ)|(ZJ)])\s(\d+)/(\d+)/(\d+)\s(\d+):(\d+):(\d+)\s(\d+)"
pattern_jztlog = "(\w+)\s([A-Z]+)\s(\d+)/(\d+)/(\d+)\s(\d+):(\d+):(\d+)\s(\d+)"
p_jztlog = re.compile(pattern_jztlog) 
line = "TF13 ZJ 2015/4/30 15:14:58 3507"
a = p_jztlog.match(line)

p_jzt_tmp1 = re.compile("[a-zA-Z]+") 
p_jzt_tmp2 = re.compile("([a-zA-Z]+\d+)\.txt")
p_jzt_tmp3 = re.compile("([a-zA-Z]+\d*)00")
