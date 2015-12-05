#####################################################################
# 1) filter all contracts to find those 0~12 contracts having both volume over 5*cnt_min 
#   and #Klines/cnt_min over 50% on specific day.
# 2) several ratios from Mitra,diBartolomeo,Banerjee,Yu 2011
#   a)resilient: Market-efficient coefficient (MEC) (Hasbrouck and Schwartz, 1988)
#     rolling over, with daily span of 10?
#   b)immediacy: the daily ratio of absolute stock return to its dollar volume averaged over some period:
#     calculated at the beginning of next month
#####################################################################
rm(list=ls())
source("utility.R")
Sys.setenv(TZ="GMT")
require("xts")
require("RSQLite")
# require("data.table")
# op <- options(digits.secs = 3)
options(stringsAsFactors = FALSE)

# dbfiledir = "D:\\bin\\pyproject\\ctpdata\\db\\20151015.db"
dbfiledir_onemin = "D:\\bin\\pyproject\\ctpdata\\db\\jzt_onemin_oop_2.db"
NULLVALUE <- -101

m <- dbDriver("SQLite")
con <- dbConnect(m, dbname = dbfiledir_onemin)
dates <- c(20150930L,20151008L,20151009L,20151012L,20151013L,20151014L,20151015L,20151016L,20151019L)
########################################################experiment #########
# sql_sector <- "select * from sectors;"
# rs <- dbSendQuery(con, sql_sector)
# df_sectors <- fetch(rs)
# dbClearResult(rs)
# 
# sql1 <- "
# select
# d.instrumentid, round((count(*)+0.0000001)/(s.cnt_min+0.0000001), 3) as rt, d.volume 
# from oneminute o, contracts c, sectors s, day d
# where 
# o.instrumentid == c.instrumentid and o.instrumentid == c.instrumentid and c.sector == s.sector and o.instrumentid == d.instrumentid 
# and o.tradingday == d.tradingday 
# and substr(d.instrumentid,length(d.instrumentid)-1, 2) between \'0\' and \'12\'
# and o.tradingday == 20151015
# and s.sector == \'"
# 
# sql2 <- "\'
# and d.volume >= s.cnt_min*5 
# -- and rt >= 0.5 
# group by o.instrumentid 
# having rt >= 0.5 
# order by rt DESC;
# "
# re <- vector("list",length = dim(df_sectors)[1])
# for (i in seq(dim(df_sectors)[1])) {
#   sql <- paste0(sql1,df_sectors[i,]$sector, sql2)
#   rs <- dbSendQuery(con, sql)
#   tmp <- fetch(rs)
#   if (dbClearResult(rs)) {
#     re[[i]] <- tmp       
#   }
# }
  
##################################################better#########
sqls_filter <- "select
d.instrumentid, round((count(*)+0.0000001)/(s.cnt_min+0.0000001), 3) as rt, d.volume 
from oneminute o, contracts c, sectors s, day d
where 
o.instrumentid == c.instrumentid and o.instrumentid == c.instrumentid and c.sector == s.sector and o.instrumentid == d.instrumentid 
and o.tradingday == d.tradingday 
and substr(d.instrumentid,length(d.instrumentid)-1, 2) between \"0\" and \"12\"
and o.tradingday == @date@
-- and s.sector == \"CU\"
and d.volume >= s.cnt_min*5 
-- and rt >= 0.5 
group by o.instrumentid 
having rt >= 0.5 
order by rt DESC;"

sql_filter <- gsub('@date@',20151015,sqls_filter)
rs <- dbSendQuery(con, sqls)
df_filter1 <- fetch(rs)
dbClearResult(rs)

###########################emc#####################################

###############################################main################
datesLen <- length(dates)
for (i in seq(datesLen)) {
  sql_filter <- gsub('@date@', dates[i], sqls_filter)
  rs <- dbSendQuery(con, sql_filter)
  df_filter1 <- fetch(rs)
  dbClearResult(rs)
  
  tmp <- fetchdata(df_filter1[1], dates[i])
  
}


sqls <- "select instrumentid, round((sum(sgnvol)+0.001)/(sum(volume)+0.001), 2) from oneminute where tradingday == 20151009 group by instrumentid order by instrumentid "
rs <- dbSendQuery(con,sqls)
tmp1 <- fetch(rs)
dbClearResult(rs)
lambda <- function(tmp) {
  ret <- diff(log(tmp$close)) 
  a<-lm(ret~tmp$sgnvol[-1])
  lbd <- a$coefficients[2]
  a1 <- summary(a)
  pr <- a1$coefficients[8]
  # adj.r.squared <- a1$adj.r.squared
  if (pr >= 0.05) {
    return(-1L)
  }
  return(lbd)
}
  
##################30151020#######################
sqls <- "select * from summary where tradingday>=20150930 and instrumentid=\'TF00\' order by tradingday; "
rs <- dbSendQuery(con, sqls)  
tmp1 <- dbFetch(rs)
dbClearResult(rs)

normalized_0 <- function(tmp) {
  mn <- mean(tmp) 
  sigma_square <- var(tmp)
  if (0 == sigma_square) {
    print("zero variance. return.")
    return 
  } else {
    return((tmp-mn)/sqrt(sigma_square))
  }
}

normalized <- function(tmp) {
  tmp_df <- tmp
  for (i in seq(dim(tmp)[2])) {
    tmp_df[,i] <- normalized_0(tmp[,i])
  }
  return(tmp_df)
}

tmp1_normalized <- normalized(tmp1[,3:7])
require(ggplot2)
cntcolumn <- 5
cntrow <- nrow(tmp1)
xrange <- seq(cntrow)
for (i in seq(2,cntcolumn)) {
  xrange <- c(xrange, seq(cntrow))
}
colorrange <- rep(c("red","blue","green","yellow","black"),each=cntrow)
shaperange <- colorrange
qplot(xrange,c(jump,lbd,eff,hot,vol),color=colorrange,data=tmp1_normalized)
# with(tmp1_normalized,plot(jump,lbd,eff,vol,col=rep(c("red","blue","green","yellow"),each=dim(tmp1)[1]),pch=rep(22:25,each=dim(tmp1)[1])))
# with(tmp1_normalized,plot(jump,col=rep("red",each=dim(tmp1)[1]),pch=rep(22,each=dim(tmp1)[1])))
# par(new=T)
# with(tmp1_normalized,plot(lbd,col=rep("blue",each=dim(tmp1)[1]),pch=rep(23,each=dim(tmp1)[1])))
# par(new=T)
# with(tmp1_normalized,plot(eff,col=rep("green",each=dim(tmp1)[1]),pch=rep(24,each=dim(tmp1)[1])))
# par(new=T)
# with(tmp1_normalized,plot(hot,col=rep("yellow",each=dim(tmp1)[1]),pch=rep(25,each=dim(tmp1)[1])))
# par(new=T)
# with(tmp1_normalized,plot(vol,col=rep("black",each=dim(tmp1)[1]),pch=rep(26,each=dim(tmp1)[1])))

plot(tmp1_normalized)
pairs(tmp1_normalized)
andrews_curve(tmp1_normalized[,1:3],col=rep(2:4,each=cntrow))

plot(tmp1_normalized$lbd,tmp1_normalized$vol)
tmp1_0 <- tmp1_normalized[tmp1_normalized$lbd <2.9,c(2,5)]
tmp1_0 <- tmp1_0[tmp1_0$vol <2.9,]
tmp_a <-summary(with(tmp1_0,lm(vol~-1+lbd)))
plot(lm(tmp1_0$vol~tmp1_0$lbd))

###############
sqls <- "select * from day where instrumentid=\"TF00\" and tradingday>=20150930 order by tradingday;"
rs <- dbSendQuery(con, sqls)
tmp2 <- dbFetch(rs)
dbClearResult(rs)


