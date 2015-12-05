#############################################################
# intra sector and cross-setional and inter-contract ananlysis of summary
# panel??????
#############################################################
Sys.setenv(TZ="GMT")
require("xts")
require("RSQLite")
require("xts")
# require("data.table")
# op <- options(digits.secs = 3)
options(stringsAsFactors = FALSE)

dbfiledir_onemin = "D:\\bin\\pyproject\\ctpdata\\db\\jzt_onemin_oop_2.db"
m <- dbDriver("SQLite")
con <- dbConnect(m ,dbname = dbfiledir_onemin)
#############################################################
rs <- dbSendQuery(con, "select * from summary order by tradingday,instrumentid")
tmp <- fetch(rs, n=-1)
dbClearResult(rs)
# rex <- as.xts(tmp[,-1],order.by = strptime(tmp[,1],format="%Y%m%d"))
####################plot####################################
# load(file="20150929_tmp.RData")
# re<-tmp;rm(tmp)
tmp1<-re[re$instrumentid == "AG00",'jump']
tmp1<-re[re$instrumentid == "AG00",c(-1,-2)]
# pairs(tmp1[,1:5],main="AA",pch=21,bg=c("red","green3","blue")[unclass(iris[["Species"]])])
pairs(tmp1[,1:5],main="AA",pch=21)
t1 <- summary(with(tmp1,lm(hot~-1+vol)))

pairs(re[,3:7],main="AA",pch=21)
t11 <- summary(with(re,lm(hot~-1+vol)))

boxplot(tmp1[,1],tmp1[,2]*10000000,tmp1[,3]*100,tmp1[,4]*5,tmp1[,5]*10000,label=colnames(tmp1))
hist(tmp1[])
## xts attributes
# axTicksByTime(tmp1, ticks.on='months')
# plot(tmp1,major.ticks='months',minor.ticks=FALSE,main=NULL,col=3)
# attributes(tmp1)



###############################close#######################
dbDisconnect(con)

