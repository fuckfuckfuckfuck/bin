Sys.setenv(TZ="GMT")
require("xts")
require("quantmod")

dataday  <- function(file,dtime="day") {
  data <- data.frame(read.csv(file=file,header=TRUE))
  if (dtime == "day")
    format_dtime <- "%Y-%m-%d"
  else if (dtime == "min")
    format_dtime <- "%Y-%m-%d %H:%M"
  
  data <- as.xts(data[,-1],order.by=strptime(data[,1],format=format_dtime,tz="GMT"))    
}
datadir <- "E:\\data\\wind\\20140617\\"
mktcolname <- c("open","high",'low',"close","volume","openint")

rollingstd <- function(data,n) {
  f1 <- function(i) {
    if (i<n)
      re <- 0
    else {
      s0 <- i-n+1
      re <- var(data[s0:i,"close"])
    }
    sqrt(re[1])  
  }
  nrows <- nrow(data) # xts data
  re <- unlist(lapply(seq(1,nrows), f1))  
  re <- xts(re,order.by=index(data),tz="GMT")
}


pricevolume <- function(xdata) {   
  re <- diff(xdata[,"close"])/sqrt(xdata[,"volume"])
  re <- as.numeric(re[complete.cases(re)])
}
pricevolume_ratio <- function(min,day,dailystd) {
  tmp <- function(minx) {
#     as.date()
    dates <- strftime(index(minx[1]),format="%Y-%m-%d")
    re <- coredata(dailystd[dates])/coredata(sqrt(day[dates,"volume"]))
    pricevolume(minx)/as.numeric(re)      
  }
  ep <- endpoints(min,"days")
#   re <- period.apply(min,INDEX=ep,tmp)
  unlist(period.apply(min,INDEX=ep,tmp))
}

##########################################
if888min <- dataday(paste(datadir,"min\\if888.csv",sep=""),"min")
if888day <- dataday(paste(datadir,"day\\if888.csv",sep=""),"day")
colnames(if888min) <- mktcolname
colnames(if888day) <- mktcolname
if888min <- if888min["/2014-06-03"]
if888day <- if888day["/2014-06-03"]
save.image(file="IF.RData")
##########################################dailyviews
pq <- function(symbol,datestr) {
  tsday <- paste(symbol,"day",sep="")
  tsmin <- paste(symbol,"min",sep="")
  dailystd <- rollingstd(tsday,23)
  dateinterval <- paste(datestr,"/",sep="")
  pq_ratio <- pricevolume_ratio(tsmin[dateinterval],tsday,dailystd)
}


hist(as.numeric(pq_ratio))
quantile(as.numeric(pq_ratio),probs=seq(0,1,0.05))
plot(as.numeric(pq_ratio))

pqint <- as.integer(pq_ratio/0.02)
hist(pqint)
summary(pqint)
plot(order(pqint))
t = pqint[order(pqint)]
plot(t)
plot(diff(t))
quantile(t,probs=seq(0,1,0.05))
quantile(t,probs=seq(0.45,0.57,0.005))
save.image(file="IF2.RData")

t1 <- if888min["2014-05-27/"]
############################################06-07spread
load(file="IF.RData")
rm(if888min,if888day)
if1406min <- dataday(paste(datadir,"min\\if1406.csv",sep=""),"min")
if1407min <- dataday(paste(datadir,"min\\if1407.csv",sep=""),"min")
if1406day <- dataday(paste(datadir,"day\\if1406.csv",sep=""),"day")
if1407day <- dataday(paste(datadir,"day\\if1407.csv",sep=""),"day")
colnames(if1406min) <- mktcolname
colnames(if1407min) <- mktcolname
colnames(if1406day) <- mktcolname
colnames(if1407day) <- mktcolname
if1406day <- if1406day["2014-05-19/"]
save.image(file="IFspread.RData")

chartSeries(if1406min[,"close"]-if1407min[,"close"])
t <- if1406min[,"close"]-if1407min[,"close"]
index(t[t==max(t)])
chartSeries(t["2014-05-23 14:56:00/2014-05-26"])
##
load(file="IFspread.RData")
b <- if1407min["2014-05-27"]
a <- if1406min["2014-05-27"]
plot(a[,"volume"]/b[,"volume"])
datestr <- "2014-06-06"
chartSeries(if1407min[datestr,"volume"]/if1406min[datestr,"volume"])

jun <- pq("if1406","2014-06-03")
##############################2014-07-02
datadir <- "E:\\data\\wind\\20140617\\"
mktcolname <- c("open","high",'low',"close","volume","openint")
if1406 <- dataday(paste(datadir,"if1406.csv",sep=''), "min")
colnames(if1406) <- mktcolname
if1407 <- dataday(paste(datadir,"if1407.csv",sep=''), "min")
colnames(if1407) <- mktcolname

date_start <- '2014-05-19'
date_end <- '2014-06-20'
dateInterval <- paste(date_start, date_end, sep='/')
dateList <- extractDates(if1406[dateInterval])


## daily stats
a <- min2daily(if1406)
b <- min2daily(if1407)

c <- pricevolume_realized(if1406)
d <- pricevolume_realized(if1407)
for (i in seq(1,length(c)))
  print(length(c[[i]]))
for (i in seq(1,length(d)))
  print(length(d[[i]]))

for (str in dateList)
  print(c[str][1,'pq_ratio'])

xdata <- if1406[dateInterval]
save(xdata, file='xdata.RData')
load(file='xdata.RData')

####################2014-11-25
load(file='IF2.RData')
chartSeries(pq_ratio)

ep <- endpoints(if888min,"days")
#   re <- period.apply(min,INDEX=ep,tmp)
tmp1 = unlist(period.apply(if888min,INDEX=ep,tmp))

tmp <- function(xtss) {
  sqrt(sum((diff(xtss[,'Close']))^2)/nrow(xtss))
}
