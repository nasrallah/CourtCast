
d = read.table('~/Desktop/props.txt', sep='\t', header=TRUE)
plot(d$argYear, d$prop_uni, type='l',col='red', ylim=c(0,1), xlab='argument year', ylab='proportion', main='Supreme Court Recent Trends')
points(d$argYear, 1-d$prop_res, type='l', col='blue')
legend('topleft',legend=c('unanimous decisions','lower court reversed'),col=c('red','blue'),lty=1)


dev.copy2eps(file='~/Desktop/trends.eps')
