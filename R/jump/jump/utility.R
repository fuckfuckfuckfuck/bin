######################connection####################
# dbfiledir_onemin = "D:\\bin\\pyproject\\ctpdata\\db\\jzt_onemin_oop_2.db"
# dbfiledir = "D:\\bin\\pyproject\\ctpdata\\db\\"
# nullvalue <- -101
# m <- dbDriver("SQLite")
# con <- dbConnect(m ,dbname = dbfiledir_onemin)
###################################close########################
# # dbClearResult(rs)
# dbDisconnect(con)
# dbDisconnect(con0)
# rm(con0, m0, m, con)
####################stattistics###############################
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
  # tmp_e <- abs(tmp$close[len] - tmp$open[1])
  tmp_e <- abs(tmp$close[len] - tmp$close[1]) ## close rather than open
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
  # tmp_h <- mean(tmp$openint)
  tmp_h <- (tmp$openint[1]+tmp$openint[len])/2 ## meausure intraday
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

####################functions@dadatabase#############################################
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
################functions@data##########################################
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

