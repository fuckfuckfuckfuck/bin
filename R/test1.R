pricevolume <- function(xdata) {   
  re <- diff(xdata[,"close"])/sqrt(xdata[,"volume"])
  re <- re[complete.cases(re)]
}
pricevolume_ratio <- function(min,day,dailystd) {  
  tmp <- function(minx) {
    #     as.date()
    str(minx)
    dates <- strftime(index(minx[1]),format="%Y-%m-%d")
    re <- coredata(dailystd[dates])/coredata(sqrt(day[dates,"volume"]))
    pricevolume(minx)/as.numeric(re)  
  }
  ep <- endpoints(min,"days")
  re <- period.apply(min,INDEX=ep,tmp)
}

