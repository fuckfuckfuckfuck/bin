Sys.setenv(TZ="GMT")
require("xts")
require("RSQLite")
require("xts")
op <- options(digits.secs = 3)
options(stringsAsFactors = FALSE)
options(op)
###################################settings##############
instrumentidDate_print <- function(str, sql, sqlPrint = FALSE) {
  if (sqlPrint) {
    tmp_str <- paste0("id_str:",id_str,"|date:",date,"<<<---:",str,"|",sql)
  } else {
    tmp_str <- paste0("id_str:",id_str,"|date:",date,"<<<---:",str)
  }
  print(tmp_str)
}

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


insertOneminute_1 <- function(sql) {
  rs <- dbSendQuery(con, sql)
  data <- fetch(rs, n = -1)
  dbClearResult(rs)
  
  #   not enough rows
  tmp_n <- dim(data)[1]
  if (tmp_n <= 30) {
    instrumentidDate_print("less than 30 rows of data. Return.",sql,TRUE)
    return()
  }  
  
  format_dtime <- "%Y%m%d %H:%M:%OS"
  a <- paste(data$UpdateTime,data$UpdateMillisec,sep='.')
  a <- paste(data$TradingDay,a)
  a <- strptime(a,format=format_dtime,tz="GMT")
  aa <- as.xts(data[,-c(3,4,19,20)],order.by = a,dateFormat="POSIXct") 
  diff_vol <- diff(data$Volume)
  diff_seq <- diff(data$seq_num)
  
  tmp_BVol <- (diff_vol != 0)
  if (sum(tmp_BVol) < 1) {
    instrumentidDate_print("Not enough diff_vol!",sql,TRUE)
    return()
  }
  
  aaa <- aa[-1, ][tmp_BVol,]  
  aaa$DiffVol <- diff_vol[diff_vol != 0]
  
  ep <- endpoints(aaa,"minutes")
  if (length(ep) <= 2) {
    instrumentidDate_print("Less than 2 endpoints.",sql,TRUE)
    return()
  }
  
  lists <- period.apply(aaa, INDEX=ep, f1)
  colnames(lists) <- c("open","high","low","close","vol","openint")
  
  tmp_time <- strftime(index(lists), format="%H:%M:%S")
  df <- data.frame(date,tmp_time,id_str,lists[,c(1,2,3,4,5,6)])
  
  tmp_n <- dim(df)[1]
  tmp_str <- paste0(". df's rows:",tmp_n,", updatetime from:",df$tmp_time[1]," to:",df$tmp_time[tmp_n])
  instrumentidDate_print(tmp_str)
  instrumentidDate_print(". Start to write db.")
  
  if (!dbWriteTable(con,"oneminute",df, append=T, row.names=F)) {
    instrumentidDate_print("Failed instrumentidDate_print.")
    return()
  }
}

insertOneminute <- function(id_str, date) {
  sqls <- paste0(s1,date,s2,id_str,s3,s4_1,s5)
  insertOneminute_1(sqls)
  sqls <- paste0(s1,date,s2,id_str,s3,s4_2,s5)
  insertOneminute_1(sqls)
  sqls <- paste0(s1,date,s2,id_str,s3,s4_3,s5)
  insertOneminute_1(sqls)
}
######################connection####################
m <- dbDriver("SQLite")
con <- dbConnect(m ,dbname = "D:\\bin\\pyproject\\ctpdata\\ctp_20150422.db")
#####################fetching########################
## contract lists
sql1 <- "select * from contracts order by cnt DESC ;"
rs <- dbSendQuery(con, sql1)
contract_lists <- fetch(rs, n = -1)
if (!dbClearResult(rs)) {
  tmp_str <- paste("id_str:",id_str,". date:",date,". fail to fetch contract list.")
  print(tmp_str)
  return
}

cnt_row <- dim(contract_lists)[1] 
if (cnt_row > 0) {
  for (i in seq(1, cnt_row)) {
    id_str = contract_lists$instrumentid[i]
    for (date in seq(contract_lists[i,2],contract_lists[i,3])) {
      tryCatch(insertOneminute(id_str, date), finally=print("Hello"))
    }
  }  
}

dbClearResult(rs)
dbDisconnect(con)

