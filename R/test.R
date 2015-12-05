require("Quandl", lib.loc="C:/Program Files/R/R-3.1.0/library")
Quandl.auth("4cUiozK8Xyxd41yoZJub")
## function
getdaydata <- function(symbol) {
  Quandl(paste("SHFE/",symbol,sep=""), type="xts",
         start_date="2014-01-01",sort="asc")
}
#############################################
symbols <- unlist(lapply(c("M","N","Q","U","V"),
                         function(c) paste("AL",c,"2014",sep="")))

datadaily <- getdaydata(symbols)

