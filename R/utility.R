# par(mfrow=c(3,1))
# plot(seq(1,1000),cumsum(seq(1,1000)))
# Sys.setenv(TZ="Etc/GMT+8")
# Sys.setenv(TZ="CST6CDT")
# Sys.setenv(TZ="GMT")
Sys.setenv(TZ="GMT")
require("xts")
op <- options(digits.secs = 3)
options(op)
require("quantmod")

###########################################
# rm(list=ls())

dataday  <- function(file,dtime="day") {
  data <- data.frame(read.csv(file=file,header=TRUE))
  if (dtime == "day")
    format_dtime <- "%Y-%m-%d"
  else if (dtime == "min")
    format_dtime <- "%Y-%m-%d %H:%M"
  else if (dtime == "sec")
    format_dtime <- "%Y-%m-%d %H:%M:%S"
  format_dtime
  data <- as.xts(data[,-1],order.by=strptime(data[,1],format=format_dtime,tz="GMT"))    
}

###########################################PQIF
# xdata should be xts
# mktcolname <- c("open","high",'low',"close","volume","openint")
# if1406 <- dataday("if1406A.csv","min")
# colnames(if1406) <- mktcolname
NotAvailable <- 1000

pricevolume_realized <- function(xdata) 
{  
  f1 <- function(datas) 
  {
    if (length(datas) <= 30) 
    {
      print("At least 30 records are needed to cal var.")
      xts(rep(NotAvailable, nrow(datas)), order.by = index(datas))
    } 
    else 
    {
      cumvol <- sum(datas[-1,"volume"],na.rm=T)
      realsig <- sqrt(sum((diff(datas[,"close"]))^2,na.rm=T))
      
      if (realsig == 0 || cumvol == 0) 
      {
        xts(rep(NotAvailable, nrow(datas)), order.by = index(datas))
      } 
      else 
      {
        adj_ret <- diff(datas[,"close"])[-1]/realsig 
        adj_vol <- sqrt(datas[-1, "volume"]/cumvol) 
        ##   should adj_* be filtered? 
        if (length(adj_vol[adj_vol == 0]) > 0) {
          re <- xts(rep(NotAvailable, nrow(adj_ret)), order.by = index(datas)[-1])
          re[adj_vol != 0] <- adj_ret[adj_vol != 0]/adj_vol[adj_vol != 0]
          re
        } 
        else 
        {
          xts(adj_ret/adj_vol, order.by = index(datas)[-1])                        
        }
        
      }
    }
    
  }
    
  xdata <- xdata[complete.cases(xdata)]     # only complete records.
  ep <- endpoints(xdata,"days")
  lists <- period.apply(xdata[,c('close','volume')], INDEX=ep, f1)
  re <- lists[[1]]
  for (i in seq(2,length(lists)))
    re <rbind(re,lists[[i]])
  colnames(re) <- 'pq_ratio'
  re
}


########################### following depleted, using daily data.
# pricevolume <- function(xdata) {   
#   re <- diff(xdata[,"close"])/sqrt(xdata[,"volume"])
#   re <- as.numeric(re[complete.cases(re)])
# }
# 
# pricevolume_ratio <- function(min,day,dailystd) {
#   tmp <- function(minx) {
#     #     as.date()
#     dates <- strftime(index(minx[1]),format="%Y-%m-%d")
#     re <- coredata(dailystd[dates])/coredata(sqrt(day[dates,"volume"]))
#     pricevolume(minx)/as.numeric(re)      
#   }
#   ep <- endpoints(min,"days")
#   #   re <- period.apply(min,INDEX=ep,tmp)
#   unlist(period.apply(min,INDEX=ep,tmp))
# }

###########################################PQIF
## min2daily
## does lqdt stable daily?
min2daily <- function(xdata) {    
  tmp <- function(xda) {
    xda <- xda[complete.cases(xda)] # na is discarded
    if (nrow(xda) <= 30) {
      print("At least 30 records are needed to cal var.")
      rep(NotAvailable, 7)
    } else {          
      cumvol <- sqrt(sum(xda[-1,"volume"], na.rm=T))
      realsig <- sqrt(sum((diff(xda[,"close"]))^2, na.rm=T))
      if (cumvol != 0) {
        pq_ratio <- realsig/cumvol
      } else {
        print("devided by zero!")
        pq_ratio <- NotAvailable
      }
          
      m_xdata <- coredata(xda)
      len <- nrow(m_xdata)
      o <- m_xdata[1,'open']
      h <- max(m_xdata[,'high'])
      l <- min(m_xdata[,'low'])
      c <- m_xdata[len, 'close']
      v <- sum(m_xdata[-1,'volume']) #1st volume is discarded.
      oint <- m_xdata[len,'openint']
  #     c('o'=o,'h'=h,'l'=l,'c'=c,'v'=v,'oint'=oint,'pq'=pq_ratio)
      c(o,h,l,c,v,oint,pq_ratio)
    }
  }

  ep <- endpoints(xdata, "days")
  pq_ratio_daily <- unlist(period.apply(xdata, INDEX=ep, tmp))  
}

##extract dates
extractDates <- function(xdata) {
  ep <- endpoints(xdata, on="days", k=1)  
  datestr <- strftime(index(xdata[ep[-1]]), format="%Y-%m-%d")    
  return(datestr)
}



