#############################################################
# 20150921
# event: zn drags down cu
# fetch intraday dataframe
#############################################################
# cu <- fetchdata('CU00',20150921)
# zn <- fetchdata('ZN00',20150921)
# if (nrow(cu) == nrow(zn)) {
#   sum(abs(diff(log(cu)) - diff(log(zn))))
# }

sqls1 <- "select updatetime,open,high,low,close,volume,amount,openint,sgnvol from oneminute where instrumentid = \""
sqls2 <- "\" and tradingday ="
sqls23 <- " and updatetime in (select distinct updatetime from oneminute where tradingday="
sqls3 <- " and instrumentid = \""
sqls4 <- "\" intersect select distinct updatetime from oneminute where tradingday = " 
sqls5 <- " and instrumentid = \"" 
sqls6 <- "\" ) ;"

fetchdata28 <- function(sym1,sym2,datee) {
  sqls <- paste0(sqls1,sym1,sqls2,datee,sqls23,datee,sqls3,sym1,sqls4,datee,sqls5,sym2,sqls6)
  rs <-dbSendQuery(con, sqls)
  tmp <- fetch(rs, n=-1)
  dbClearResult(rs)  
  tmp
}

cu <- fetchdata28('CU00','ZN00',20150921)
zn <- fetchdata28('ZN00','CU00',20150921)
cu <- xts(cu[,-1],order.by = strptime(cu$updatetime,format="%H:%M"))
zn <- xts(zn[,-1],order.by = strptime(zn$updatetime,format="%H:%M"))
tmp <- diff(log(cu$close)) - diff(log(zn$close))
tmp <- cbind(diff(cu$close)["2015-09-28 04:55/2015-09-28 14:00"]/10,
             diff(zn$close)["2015-09-28 04:55/2015-09-28 14:00"]/5)
colnames(tmp) <- c('cu','zn')

rex <- as.xts(re[,-1],order.by=strptime(re[,1],format="%Y%m%d"))

