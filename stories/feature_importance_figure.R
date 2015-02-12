
par(mar=c(12,3,3,1))
j_col <- c('light blue', 'blue', 'pink', 'red', 'brown')
colors = c('gray')
barplot(d$importances, names.arg=d$features, las=3, ylim=c(0,0.2), main="Feature Importances" )

dev.copy2eps(file="~/Desktop/feature_importance_figure.eps")
