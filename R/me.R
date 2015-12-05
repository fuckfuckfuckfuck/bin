# Sys.setenv(TZ="Etc/GMT+8")
# Sys.setenv(TZ="CST6CDT")
# Sys.setenv(TZ="GMT")
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

me1405day <- dataday("me1.csv")
me1409day <- dataday("me1.csv")
save("me1405day","me1409day",file="meday.RData")
a<-me1405day[,"volume"]/me1405day[,"openint"]
b<-me1409day[,"volume"]/me1409day[,"openint"]
par(mfrow=c(2,1))
plot(a["2013-12-02/"])
plot(b["2013-12-02/"])
chartSeries(me1409min[,"volume"]/me1409min[,"openint"])
meday <- new.env()

me1405min <- dataday("d:\\My Documents\\chongyang\\bin\\tbv441_portable\\User\\wangwatercup\\Desktop\\我的工作区\\data\\min\\me1405min.csv","min")
colnames(me1405min) <- colnames(me1405day)
me1409min <- dataday("d:\\My Documents\\chongyang\\bin\\tbv441_portable\\User\\wangwatercup\\Desktop\\我的工作区\\data\\min\\me1409min.csv","min")
colnames(me1409min) <- colnames(me1405day)
c<-(me1409min[,"volume"]/me1409min[,"openint"])
chartSeries(c["2014-04-17"])
hist(coredata(c["2014-04-01/"]))

f1 <- function(xdata) {  
  cumvol <- sum(xdata[,"volume"],na.rm=T)
  realsig <- sqrt(sum((diff(xdata[,"close"]))^2,na.rm=T))
  adj_ret <- diff(xdata[,"close"])/realsig
  adj_vol <- sqrt(xdata[,"volume"]/cumvol)
  re <- cbind(adj_ret,adj_vol,adj_ret/adj_vol)
  re[complete.cases(re),]
}
f2 <- function(xdata) {
  d <- xdata["2014-04-01/"]
  ep <- endpoints(d,"days")
  unlist(period.apply(d,INDEX=ep,FUN=f1))
}
a <- f2(me1409min)
a <- f1(me1409min["2014-04-17"])
a0 <- a[a[,"close"]!=0,"close"]
a1 <- a[a[,"close"]!=0,"volume"]
m <- lm(a0~1+a1)
summary(m)
