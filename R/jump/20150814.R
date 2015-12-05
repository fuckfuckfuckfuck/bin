######################connection####################
dbfiledir = "/home/dell/data/jzt/jzt_onemin_oop.db"
m <- dbDriver("SQLite")
con <- dbConnect(m ,dbname = dbfiledir)
#####################fetching########################
# sqls <- "select  from oneminute where instrumentid = \"AG00\";"
# rs <- dbSendQuery(con, sqls)
# a <- fetch(rs, n = -1)
# dbClearResult(rs)
datestr <- "20150813"
sqls <- "select instrumentid,count(*) as cnt from oneminute where tradingday = "
sqls <- paste0(sqls, datestr)
sqls <- paste0(sqls, " and instrumentid in (select instrumentid from main m join sectors s on substr(m.instrumentid,1,length(m.instrumentid)-2) = s.sector where s.exchange != 'ZJ') group by instrumentid having cnt >= 225 order by cnt desc;")
rs <- dbSendQuery(con, sqls)
a <- fetch(rs, n = -1)
dbClearResult(rs)
#########################################process#############
for (i in seq(1,dim(a)[1])) {
  print(a[i,1])
}

sqls <- "select updatetime,open,high,low,close,volume,amount,openint from oneminute where tradingday = "
sqls <- paste0(sqls,datestr," and instrumentid = '",a[i,1])
sqls <- paste0(sqls,"' order by updatetime ASC;")
rs <- dbSendQuery(con, sqls)
a1 <- fetch(rs, n = -1)
dbClearResult(rs)
#########################################close##############
# dbClearResult(rs)
dbDisconnect(con)

