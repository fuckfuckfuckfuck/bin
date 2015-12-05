Sys.setenv(TZ="GMT")
## Sys.setenv(TZ="Etc/GMT+8")
require("xts")
require("RSQLite")
require("xts")
# require("data.table")
op <- options(digits.secs = 3)
options(stringsAsFactors = FALSE)
options(op)
###################################settings##############
s1 <- "select * from mktinfo where tradingday = "
s2 <- " and instrumentid = \""
s3 <- "\" and LastPrice <= upperlimitprice and LastPrice >= lowerlimitprice and "
s4 <- "(substr(updatetime,1,5) < \"02:30\" or (substr(updatetime,1,5) >= \"09:00\" and substr(updatetime,1,5) < \"15:15\") or substr(updatetime,1,5) >= \"21:00\")"
s4_1 <- "(substr(updatetime,1,5) < \"02:30\") "
s4_2 <- "(substr(updatetime,1,5) >= \"09:00\" and substr(updatetime,1,5) < \"15:15\") "
s4_3 <- "(substr(updatetime,1,5) >= \"21:00\") "
s5 <- " order by updatetime,updatemillisec ;"

nullvalue <- -1
f1 <- function(xdata) {
  #   str(xdata)
  len <- dim(xdata)[1]
  if (len > 0) {    
    num <- as.numeric(xdata$LastPrice)
    o <- num[1]
    h <- max(num)
    l <- min(num)
    c <- num[len]
    
    openint <- (xdata$OpenInterest)[len]
    vol <- sum(xdata$DiffVol)
    #     return(c('o'=o,'h'=h,'l'=l,'c'=c))
    return(c(o,h,l,c,vol,openint))
  } 
  return(c(nullvalue,nullvalue,nullvalue,nullvalue,nullvalue,nullvalue)) 
}
######################connection####################
m <- dbDriver("SQLite")
con <- dbConnect(m ,dbname = "D:\\bin\\pyproject\\ctpdata\\ctp_20150413.db")
# con <- dbConnect(RSQLite::SQLite(), ":memory:")

#####################fetching########################
## contract lists
sql1 <- "select * from contracts order by cnt DESC ;"
rs <- dbSendQuery(con, sql1)
contract_lists <- fetch(rs, n = -1)
dbClearResult(rs)

## date
date = contract_lists$min_date[1]
id_str = contract_lists$instrumentid[1]

sql <- paste0(s1,date,s2,id_str,s3,s4_1,s5)
rs <- dbSendQuery(con, sql)
data <- fetch(rs, n = -1)
dbClearResult(rs)
######################xts###########################
format_dtime <- "%Y%m%d %H:%M:%OS"
# format_dtime <- "%H:%M:%OS3"
# format_dtime <- "%H:%M:%OS"
a <- paste(data$UpdateTime,data$UpdateMillisec,sep='.')
a <- paste(data$TradingDay,a)
a <- strptime(a,format=format_dtime,tz="GMT")

## time to sub-second accuracy (if supported by the OS)
format(Sys.time(), "%H:%M:%OS3")

# aaa <- as.xts(data[,-c(3,4,19,20)],order.by=aa,dateFormat="POSIXct", .RECLASS=TRUE)    
aa <- as.xts(data[,-c(3,4,19,20)],order.by = a,dateFormat="POSIXct")    
# if exists char field, all fields will be changed into char
# so all non-numeric fields excluded

# sizeof(diff(xts)) = n, sizeof(diff(dataframe)) = n - 1 
diff_vol <- diff(data$Volume)
diff_seq <- diff(data$seq_num)
if (min(diff_vol) < 0) {
  print("Non increasing volume found!")
}
if (min(diff_seq) < 1) {
  print("Non increasing seq found!")
}

aaa <- aa[-1, ][diff_vol != 0,]
# MAYBE the ONLY way to add a colume to xts/df
aaa$DiffVol <- diff_vol[diff_vol != 0]

rm(a)
rm(aa)
rm(diff_seq)
rm(diff_vol)

# format_time <- "%Y%m%d %H:%M:%OS"
# a <- paste(data$UpdateTime,data$UpdateMillisec,sep='.')
# a <- paste(data$TradingDay, a, sep = " ")
# aa <- strptime(a,format=format_time,tz="GMT")
# diff_time <-diff(aa)

####################################intervalStat################
ep <- endpoints(aaa,"mins")
lists <- period.apply(aaa, INDEX=ep, f1)
# # null
# # keeping null may reveal more info
# has_null <- rowSums(lists)
# lists <- lists[has_null != 0]
colnames(lists) <- c("open","high","low","close","vol","openint")
# diff_vol  date  id_str
##################################insert back to db###########
# sql_create_onemin <- "CREATE TABLE if not exists `oneminute` (
#   `tradingday` INT NOT NULL,
#   `updatetime` text NOT NULL,
# `instrumentid` text NOT NULL,
# `open` double NOT NULL,
# `high` double NOT NULL,
# `low` double NOT NULL,
# `close` double NOT NULL,
# `volume` int NOT NULL,
# `openint` int NOT NULL,
# PRIMARY KEY (`instrumentid`,`tradingday`,`updatetime`)
# )"
# 
# # creat
# rs <- dbSendQuery(con, sql)
# dbClearResult(rs)
# # loop inserting

# ANOTHER WAY AROUND, directly write.
tmp_time <- strftime(index(lists),format="%H:%M:%S")
df <- data.frame(date,tmp_time,id_str,lists[,c(1,2,3,4,5,6)])
# dbWriteTable(connection, name=tableName, value=rows , append=TRUE, row.names=FALSE, overwrite=FALSE);
if (!dbWriteTable(con,"oneminute",df, append=T, row.names=F)) {
  tmp_p <- paste(date,id_str)
  print(tmp_p)
  next
}
tmp(tmp_time)

###################################close########################
dbClearResult(rs)
dbDisconnect(con)

save.image(file="20150423.RData")
rm(list=ls())
