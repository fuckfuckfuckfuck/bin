sid <- c("CU","ZN","I","RB","AX","C","CS","M","RM","P","Y","SRX","CF","RU","TA")
datee <- 20151012L

##########################################################
sqls <- "SELECT 
tradingday,instrumentid,open,high,low,close,volume,openint,amount 
FROM day where tradingday = 20151012 and instrumentid in 
(select instrumentid from contracts where sector = \'CU\') 
and round(substr(instrumentid,length(instrumentid)-1,2), 0) between 1 and 12  
order by volume DESC;"
sqls1 <- "select * from summary where tradingday = 20151012 and instrumentid in 
(select instrumentid from contracts where sector = \'CU\');"

rs <- dbSendQuery(con,sqls)
tmp <- fetch(rs)
dbClearResult(rs)

##
tmp1 <- fetchdata(tmp[1,2],datee)
tmp2 <- fetchdata(tmp[2,2],datee)

ret <- diff(log(tmp1$close)) 
a <- lm(ret~tmp1$sgnvol[-1])
lbd <- a1$coefficients[2]
asum <- summary(a)
pr <- a1$coefficients[8]

ret1 <- diff(log(tmp2$close)) 
a1 <- lm(ret1~tmp2$sgnvol[-1])
lbd1 <- a1$coefficients[2]
asum1 <- summary(a1)
pr1 <- a1$coefficients[8]



##
tmp <- fetchdata(sid[1], datee)
