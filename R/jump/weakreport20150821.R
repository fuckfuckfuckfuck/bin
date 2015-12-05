Sys.setenv(TZ="GMT")
## Sys.setenv(TZ="Etc/GMT+8")
require("xts")
require("RSQLite")
require("xts")
# require("data.table")
# op <- options(digits.secs = 3)
options(stringsAsFactors = FALSE)
options(op)
#######################params#######################
dbfiledir = "D:\\bin\\pyproject\\ctpdata\\db\\jzt_onemin_oop.db"
nullvalue <- -101

######################connection####################
m <- dbDriver("SQLite")
con <- dbConnect(m ,dbname = dbfiledir)
#####################fetching########################
# sqls <- "select * from mktvital where instrumentid = \"AG00\";"
sqls <- "select m.instrumentid,s.sector,s.exchange from main m join sectors s on substr(m.instrumentid,1,length(m.instrumentid)-2) = s.sector order by s.exchange,s.sector;"
rs <- dbSendQuery(con, sqls)
df_main <- fetch(rs, n = -1)
dbClearResult(rs)

sqls0 <- "select * from mktvital where instrumentid = \""
sqls1 <- "\" and date >= 20150521 and date < 20150824 order by date;"
symbol_cnt <- nrow(df_main)
list_vital <- vector("list", symbol_cnt)
format_dtime <- "%Y%m%d"

for (i in seq(1,symbol_cnt)) {
  sqls2 <- paste0(sqls0,df_main[i,1],sqls1)
  print(sqls2)
  rs <- dbSendQuery(con,sqls2)
  tmp <- fetch(rs, n=-1)
  tmp1 <- strptime(tmp$date,format=format_dtime,tz="GMT")
  tmp2 <- xts(tmp[,-c(1,2,6,7)],order.by = tmp1,dateFormat="POSIXct") 
  list_vital[[i]] <- tmp2
  dbClearResult(rs)
}
rm(sqls,sqls0,sqls1,sqls2,format_dtime,tmp,tmp1,tmp2)

##
sqls0 <- "select * from realizedcorr where instrumentid = \""
sqls1 <- "\" and date >= 20150521 and date < 20150824 order by date;"
symbol_cnt <- nrow(df_main)
list_realizedcorr <- vector("list", symbol_cnt)
format_dtime <- "%Y-%m-%d %H:%M:%S"

for (i in seq(1,symbol_cnt)) {
  sqls2 <- paste0(sqls0,df_main[i,1],sqls1)
  print(sqls2)
  rs <- dbSendQuery(con,sqls2)
  tmp <- fetch(rs, n=-1)
  tmp1 <- strptime(tmp$updatetime,format=format_dtime,tz="GMT")
  tmp2 <- xts(tmp[,-c(1,2,6,7)],order.by = tmp1,dateFormat="POSIXct") 
  list_vital[[i]] <- tmp2
  dbClearResult(rs)
}

# save(df_main,dbfiledir,list_vital,nullvalue,symbol_cnt,file="20150821.RData")
######################xts###########################
format_dtime <- "%Y-%m-%d %H:%M:%S"
# format_dtime <- "%Y%m%d %H:%M:%OS"
# # format_dtime <- "%H:%M:%OS3"
# # format_dtime <- "%H:%M:%OS"
# a <- paste(data$UpdateTime,data$UpdateMillisec,sep='.')
# a <- paste(data$TradingDay,a)
# a <- strptime(a,format=format_dtime,tz="GMT")

## time to sub-second accuracy (if supported by the OS)
# format(Sys.time(), "%H:%M:%OS3")

# aa <- as.xts(data[,-c(3,4,19,20)],order.by = a,dateFormat="POSIXct") 
####################################intervalStat################
ep <- endpoints(aaa,"mins")
lists <- period.apply(aaa, INDEX=ep, f1)

colnames(lists) <- c("open","high","low","close","vol","openint")

##################################insert back to db###########

###################################close########################
dbClearResult(rs)
dbDisconnect(con)



