Sys.setenv(TZ="GMT")
## Sys.setenv(TZ="Etc/GMT+8")
require("xts")
require("RSQLite")
require("xts")
# require("data.table")
# op <- options(digits.secs = 3)
options(stringsAsFactors = FALSE)
# options(op)
report <- FALSE
summaryB <- FALSE
#######################params#######################
dbfiledir_onemin = "D:\\bin\\pyproject\\ctpdata\\db\\jzt_onemin_oop_2.db"
dbfiledir = "D:\\bin\\pyproject\\ctpdata\\db\\"
nullvalue <- -101
# dates <- c(20150817,20150818,20150819,20150820,20150821)
# dates <- c(20150824,20150825,20150827,20150828)
# dates <- c(20150831,20150901,20150902,20150907,20150908,20150909)
# dates <- c(20150910)
# dates <- c(20150907,20150908,20150909,20150910,20150911)
# dates <- c(20150831,20150901,20150902,20150907,20150908,20150909,20150910,20150911,20150914,20150915,20150916,20150917,20150918)
# dates <- c(20150525,20150526,20150527,20150528,20150529,20150602,20150603,20150604,20150605,20150609,20150610,20150611,20150612,20150615,20150616,20150617,20150618,20150619,20150623,20150624,20150625,20150626,20150629,20150630,20150701,20150702,20150703,20150706,20150707,20150708,20150709,20150710,20150713,20150714,20150715,20150716,20150717,20150720,20150721,20150722,20150723,20150724,20150727,20150728,20150729,20150730,20150731,20150831,20150901,20150902,20150907,20150908,20150909,20150910,20150911,20150914,20150915,20150916,20150917,20150918,20150921,20150922,20150923,20150924,20150925)
# dates <- c(20150803,20150804,20150805,20150806,20150807,20150810,20150811,20150812,20150813,20150814,20150817,20150818,20150819,20150820,20150821,20150824,20150825,20150827,20150828)
dates <- c(20150928,20150929)

weekNumber <- 240*length(dates)

dataDb <- paste0(dates[1],'.db')
datafiledir <- paste0(dbfiledir, dataDb)
####################function#######################
jump_bns <- function(tmp, t) {
  a1 <- diff(log(tmp$close))  
  a2 <- abs(a1)
  RV <- sum(a1*a1)
  BV <- sum(a2[-1]*a2[-length(a2)])
  miu1 <- sqrt(2/pi)
  len1 <- length(a1)
  delta_n <- 1/len1 
  QV <- sum(a2[-c(len1-2,len1-1,len1)]*a2[-c(1,len1-1,len1)]*a2[-c(1,2,len1)]*a2[-c(1,2,3)])/delta_n
  theta <- pi^2/4 + pi - 5
  S1 <- BV/RV/(miu1^2) - 1
  S2 <- sqrt(theta*max(1/t,QV/(BV^2)))
  S <- S1/S2/sqrt(delta_n)
  return(S)
}

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

efficiency <- function(tmp) {
  len <- dim(tmp)[1]
  if (1 > len ) {
    print("length is less than 1.return")
    return(-1) 
  }
  tmp_e <- abs(tmp$close[len] - tmp$open[1])
  if (0 == tmp_e) {
    return(0)
  } else {
    return(tmp_e/sum(abs(diff(tmp$close))))
  }
}

hott <- function(tmp) {
  len <- dim(tmp)[1]
  if (1 > len ) {
    print("length is less than 1.return")
    return(-1) 
  }
  tmp_h <- mean(tmp$openint)
  if (0 == tmp_h) {
    return(0)
  } else {
    return(sum(tmp$volume)/tmp_h)
  }
}

realizedvol <- function(tmp) {
  len <- dim(tmp)[1]
  if (1 > len ) {
    print("length is less than 1.return")
    return(-1) 
  } else {
    tmp_r1 <- sum((diff(log(tmp$close)))^2) 
    tmp_r2 <- log(tmp$close[len]/tmp$close[1])
    tmp_r3 <- sqrt(tmp_r1/len- (tmp_r2/len)^2)
    return(tmp_r3)
  }
} 

fetchsymbols <- function(datee) {
  sqls1 <- "select instrumentid from oneminute where tradingday = "
  sqls2 <- " group by instrumentid having count(*) > 200;"
  sqls <- paste0(sqls1,datee,sqls2)
  rs <- dbSendQuery(con, sqls)
  tmp = fetch(rs, n= -1)
  dbClearResult(rs)
  return(tmp)
}

fetchdata <- function(symbol,datee) {
  sqls1 <- "select open,high,low,close,volume,amount,openint,sgnvol from oneminute where instrumentid = \""
  sqls2 <- "\" and tradingday = "
  sqls3 <- " order by updatetime;"
  sqls <- paste0(sqls1,symbol,sqls2,datee,sqls3)
  rs <- dbSendQuery(con, sqls)
  tmp <- fetch(rs, n = -1)
  dbClearResult(rs)
  return(tmp)
}

fetchitem <- function(symbol, item) {
  sqls1 <- "select " 
  sqls2 <- " from summary where instrumentid=\""
  sqls3 <- "\" order by tradingday;"
  sqls <- paste0(sqls1,item,sqls2,symbol,sqls3)
  rs = dbSendQuery(con, sqls)
  tmp <- fetch(rs, n=-1)
  dbClearResult(rs)
  return(tmp)
}

create.matrix <- function (sz1,sz2) {
  x <- matrix()
  length(x) <- sz1*sz2
  dim(x) <- c(sz1,sz2)
  x
}

create.array <- function (sz1,sz2,sz3,dimnames = NULL) {
  x <- array()
  length(x) <- sz1*sz2*sz3
  dim(x) <- c(sz1,sz2,sz3)
  dimnames <- dimnames
  x
}

######################connection####################
m <- dbDriver("SQLite")
con <- dbConnect(m ,dbname = dbfiledir_onemin)

# m <- dbDriver("SQLite")
# con <- dbConnect(m ,dbname = datafiledir)
#####################fetching########################
# # sqls <- "select * from mktvital where instrumentid = \"AG00\";"
# sqls1 <- "select instrumentid from oneminute where tradingday >= "
# sqls2 <- " and tradingday <= "
# sqls3 <- " group by instrumentid having count(*) > "
# sqls4 <- "  ;"
# sqls <- paste0(sqls1, dates[1], sqls2, dates[length(dates)], sqls3, weekNumber, sqls4)
# rs <- dbSendQuery(con, sqls)
# list_main_1 <- fetch(rs, n = -1)
# dbClearResult(rs)
# 
# sqls <- "select * from main;"
# rs <- dbSendQuery(con0, sqls) 
# list_main_0 <- fetch(rs, n = -1)
# dbClearResult(rs)
# 
# ## intersection
# list_main <- c()
# for (i in seq(nrow(list_main_0))) {
#   tmp_i <- list_main_0[i,]
#   for (j in seq(nrow(list_main_1))) {
#     if (tmp_i == list_main_1[j,]) {
#       list_main <- c(list_main, tmp_i)
#       break
#     }
#   }
# }
# rm(list_main_0, list_main_1)




##


# nrow_ <- dim(lst)[1] ## length(lst)    
# re <- matrix(0,nrow=nrow_,ncol=length(dates))

re <- data.frame()
for (i in seq(length(dates))) {
  lst <- fetchsymbols(dates[i])
  if (nrow(lst) > 0) {
    for (j in seq(nrow(lst))) {
      tmp <- fetchdata(lst[j,], dates[i])
      jump <- jump_bns(tmp, i)
      lbd <- lambda(tmp)
      eff <- efficiency(tmp)
      hot <- hott(tmp)
      vol <- realizedvol(tmp)
      tmp_re <- data.frame(date=dates[i],id=lst[j,],jump=jump,lbd=lbd,eff=eff,hot=hot,vol=vol)
      re <- rbind(re,tmp_re)      
    }
  }
}

if (!dbWriteTable(con,"summary",re,append=T,row.names=FALSE)) {
  print("failed to insert into db.")
}

##########report################
## after delete -1 lambda
report <- FALSE
if (report == TRUE) {
  datesLen <- length(dates)
  sqls0 <- "select instrumentid from summary where substr(instrumentid,length(instrumentid)-1,2)=\"00\" and tradingday >= "
  sqls1 <- " and tradingday <= "
  sqls3 <- " group by instrumentid having count(*) = "
  sqls <- paste0(sqls0,dates[1],sqls1,dates[datesLen],sqls3, datesLen, " ;")
  rs <- dbSendQuery(con, sqls)
  lst1 <- fetch(rs, n=-1)
  dbClearResult(rs)
  
  lenstat <- dim(re)[2] 
  # re2 <- create.array(nrow(lst1), datesLen, lenstat - 2)
  ## symbol,date,stat
  re_jump <- create.matrix(nrow(lst1), datesLen)
  re_lbd <- create.matrix(nrow(lst1), datesLen)
  re_eff <- create.matrix(nrow(lst1), datesLen)
  re_hot <- create.matrix(nrow(lst1), datesLen)
  re_vol <- create.matrix(nrow(lst1), datesLen)
  
  # statnames <- as.list(dimnames(re)[[2]])
  for (i in seq(nrow(lst1))) {
    tmp_r <- fetchitem(lst1[i,], "jump")
    for (j in seq(datesLen)) {
      re_jump[i,j] <- tmp_r[j,]  
    }
    
    tmp_r <- fetchitem(lst1[i,], "lbd")
    for (j in seq(datesLen)) {
      re_lbd[i,j] <- tmp_r[j,]  
    }
    
    tmp_r <- fetchitem(lst1[i,], "eff")
    for (j in seq(datesLen)) {
      re_eff[i,j] <- tmp_r[j,]  
    }
    
    tmp_r <- fetchitem(lst1[i,], "hot")
    for (j in seq(datesLen)) {
      re_hot[i,j] <- tmp_r[j,]  
    }
    
    tmp_r <- fetchitem(lst1[i,], "vol")
    for (j in seq(datesLen)) {
      re_vol[i,j] <- tmp_r[j,]  
    }
  }
  
  ##########summary################
  summaryB <- FALSE
  if (TRUE == summaryB) {
    write.csv(re_jump,file="jump.csv")
    write.csv(re_lbd,file="lbd.csv")
    write.csv(re_eff,file="eff.csv")
    write.csv(re_hot,file="hot.csv")
    write.csv(re_vol,file="vol.csv")
    
    summarycsv <- function (re_tmp,namee) {
      tmp <- summary.matrix(t(re_tmp))
      write.csv(tmp,file=namee)
    }
    # summarycsv(re_tmp,file="t_jump.csv")
    
    summarycsv(re_lbd, "t_lbd.csv")
    summarycsv(re_eff, "t_eff.csv")
    summarycsv(re_hot, "t_hot.csv")
    # summary.matrix(t(re_vol))
    summarycsv(re_vol, "t_vol.csv")
  }
}

######################xts###########################
format_dtime <- "%Y-%m-%d %H:%M:%S"
format_date <- "%Y/%m/%d"

###################################close########################
# # dbClearResult(rs)
# dbDisconnect(con)
# dbDisconnect(con0)
# rm(con0, m0, m, con)

# {list_main, re} are keys.
# save(list_main,re,file="20150817.RData")
# save(list_main,re,file="20150824.RData")
# save(list_main,re,file="20150831.RData")
# save(list_main,re,file="20150910.RData")
# save.image(file="tmp.RData")
# write(list_main,file="m1.csv",sep=',')

#####################chechkingSQL#############################
# select instrumentid 
# from v.oneminute where tradingday >= 20150831 and tradingday <= 20150910 and instrumentid in (select * from main) 
# group by instrumentid 
# having count(*) > 1440;

# sqls <- "create table if not exists summary (
#   tradingday int not null,
#   instrumentid text not null,
#   jump double,
#   lbd double,
#   eff double,
#   hot double,
#   vol double,
#   primary key (tradingday,instrumentid)
#   );"

# # > re1<-re
# # > re_eff1<-re_eff
# # > re_hot1<-re_hot
# # > re_jump1<-re_jump
# # > re_lbd1<-re_lbd
# # > re_vol1 <- re_vol
# # lst11 <-lst1
# re2 <- rbind(re,re1)
# re <- re2
# 
# rm(re1,re2,lst11,re_eff1,re_hot1,re_jump1,re_lbd1,re_vol1)

