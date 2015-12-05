# sqlite coodinate.

readtablename <- function(fdir) {
  require("stringr") 
  
  con <- file(fdir, open="r")
  # c(isOpen(con, "r"), isOpen(con, "w"))
  line <- readLines(con=con, n=1L)
  list <- c()
  while(length(line) != 0) {
    tmp <- str_trim(unlist(strsplit(line,spli="  ")))
    for(i in seq(1,length(tmp)))
      list <- c(list,tmp[i])
    line <- readLines(con, n=1L)
  }
  
  close(con)
  list
}

extractname <- function(name,min="Min") {
  re <-""
  if (nchar(name) == 9) {
    if (substr(name,7,9) == min) 
      re <- substr(name,1,5)
  } else if (nchar(name) == 10) {
    if (substr(name,8,10) == min)
      re <- substr(name,1,6)
  }
  re    
}

############################################
list <- readtablename("d:\\My Documents\\data\\t0.txt")
# writeChar(list, con1, eos = "\r\n")
# for (i in seq(1,length(list))) {
#   write(list[i], con=con1)
# }
write.table(list,file="d:\\My Documents\\data\\t1.txt",
            row.names=F,col.names=F, quote=FALSE)


close(con)
unlink(con)
# flush(con)
##################################combineAllDatabases
# require("RSQLite", lib.loc="C:/Program Files/R/R-3.1.0/library")
# m <- dbDriver("SQLite",max.con=5)
# con <- dbConnect(m,dbname="d:\\My Documents\\data\\data_2_0.db")
list <- readtablename("d:\\My Documents\\data\\t1.txt")

//min
for (i in seq(1,length(list))) {
  name <- list[i]                   
#       sqls <- paste("insert into trade_min select \"",name1,"\", ticktime,high,low,open,close,vol,oi,avg from \"",name,"\";", sep="")                      
#       sqls <- paste("create index idx on \"",name,"\" (ticktime ASC);", sep="")                      
#       rs <- dbSendQuery(con, sqls) 
#       list0 <- c(list0,name1)         
                  
}
# sqls <- "select count(*) from v1005_day;"
# rs <- dbSendQuery(con, sqls)
# data <- fetch(rs, n=-1)

dbClearResult(rs)
dbDisconnect(con)
######################################divideandconquer
require("RSQLite", lib.loc="C:/Program Files/R/R-3.1.0/library")
require("xts")
require("data.table", lib.loc="C:/Program Files/R/R-3.1.0/library")
m <- dbDriver("SQLite",max.con=5)
con <- dbConnect(m,dbname="d:\\My Documents\\data\\data_2_0.db")
# list <- readtablename("d:\\My Documents\\data\\t1.txt")
options(stringsAsFactors = FALSE)
# Sys.setenv(TZ="Etc/GMT+8")
Sys.setenv(TZ="GMT")

sqls <- "select distinct 
case when length(name)==9 then substr(name,1,5) 
when length(name)==10 then substr(name,1,6) 
end as subname from tname order by subname ASC;";             
rs <- dbSendQuery(con,sqls)
names <- fetch(rs, n=-1)

//min
for (i in seq(1,length(names))) {
  name <- names[i]  
  divideandconquer(name)                 
}

dbClearResult(rs)
dbDisconnect(con)

divideandconquer <- function(name) {
  regression_interval <- 23 # interval len to calc. std. A trading month 
  
#   sqls <- paste("create unique index idx on \"",name,"\" (ticktime ASC);",sep="")
  sqls <- paste("select count(*) from \"",name,"_Day\" ;",sep="")
  tryCatch(rs <- dbSendQuery(con, sqls), error = function(e) print(e))
  length_day <- fetch(rs, n=-1)
  
  if (length_day > regression_interval) {
    sqls <- paste("select * from \"",name,"_Day\" order by TickTime ASC;",sep="")
    tryCatch(rs <- dbSendQuery(con, sqls), error = function(e) print(e))
    ts_day <- fetch(rs, n=-1)
    idx <- strptime(ts_day[,"TickTime"], format="%Y-%m-%d")
    ts_day <- xts(ts_day[,-1], order.by=idx)
    
    sqls <- paste("select * from \"",name,"_Min\" order by TickTime ASC;",sep="")
    tryCatch(rs <- dbSendQuery(con, sqls), error = function(e) print(e))
    ts_min <- fetch(rs, n=-1)    
    idx <- paste(substr(ts_min[,"TickTime"],1,10),substr(ts_min[,"TickTime"],12,19))
    idx <- strptime(idx, format="%Y-%m-%d %H:%M:%S")
    ts_min <- xts(ts_min[,-1], order.by=idx)
    
    data.day <- daily.std(ts_day, regression_interval)#day[date,std,vol]
    data.min.adj_ret <- min.adj_min() 
  }

  
  sqls <- paste("select count(*) from \"",name,"\" where (open>high) or (open<low) or (close>high) or (close<low);", sep="")                      
  rs <- dbSendQuery(con, sqls) 
  data <- fetch(rs, n=-1)  
  if (data != 0)
    print(paste("wrong OHLC at ",name," : ",data,sep=""))
}


daily.std <- function(ts_day, interval) {
  ## daily stats
  day.ret <- c(0,diff(ts_day[,'Close'])/ts_day[-1,'Close'])
  nrows <- nrow(ts_day)
  std <- rep(0, nrows)
  for (i in seq(interval, nrows)) {
    std[i] <- sqrt(var(day.ret[seq(i-interval+1,i)]))
  }
  
  day.std_vol <- xts(cbind(std, ts_day[,'Vol']), order.by=index(ts_day))
  colnames(day.std_vol) <- c("std","vol")
  day.std_vol
}

min.adj_min <- function(ts_min, day) {
  ret <- c(0,diff(ts_min[,"Close"])/ts_min[-1,"Close"])
#   min <- xts(matrix(0,nrow=nrow(ts_min),ncol=2), order.by=index(ts_min))
#   colnames(min) <- c("std","vol")
  std <- data.table(substr(index(ts_min),1,10))
  setkeyv(std, colnames(std)[1])
  dayday <- data.frame(time=index(day),std=coredata(day[,1]),vol=coredata(day[,2]))
  std[dayday[,1],,]
  
  lapply(seq(1,length(ret)), function(x) ret[x]/ts_day[substr(index(ts_min[x]),1,10), "std"])
}


