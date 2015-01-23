i_labels <- c('Pet', 'Tie', 'Res')
a_labels <- c('Pet', 'None', 'Res')
m <- matrix(c(0.742, 0.5, 0.825,  0.569, 0.7, 0.760,  0.353, 0.714, 0.5), nrow=3, byrow=TRUE)
d <- data.frame(m)
colnames(d) <- i_labels
rownames(d) <- a_labels



cloud(probs~interrupted_side+amicus_curae, d, panel.3d.cloud=panel.3dbars, col.facet='grey', 
      xbase=0.4, ybase=0.4, scales=list(arrows=FALSE, col=1), 
      par.settings = list(axis.line = list(col = "transparent")))



probs <- c(0.742, 0.5, 0.825,  0.569, 0.7, 0.760,  0.353, 0.714, 0.5)

d <- data.frame(probs)
d$interrupted_side <- as.factor(rep(i_labels,times=3))
d$amicus_curae <- as.factor(rep(a_labels, each=3))
levelplot(d)