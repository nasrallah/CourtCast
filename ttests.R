

N_x <- 73
H_x <- 62
T_x <- N_x - H_x

N_y <- 20
H_y <- 13
T_y <- N_y - H_y

x = c(rep(1,H_x),rep(0,T_x))
y = c(rep(1,H_y),rep(0,T_y))

t.test(x,y)


#### Test significance of which side spoke the most words, given everything else.
### Nothing was significant, due to lack of power, lack of true importance, or both.
cases <- c('law_P, inter_P', 'law_P, inter_R', 'law_T, inter_P', 'law_T, inter_R')

H_x <- c(19,62,43,65)
T_x <- c(7,11,29,18)

H_y <- c(2,13,21,37)
T_y <- c(3,7,19,17)

t <- NULL
for (i in 1:4){
	print(cases[i])
	x = c(rep(1,H_x[i]),rep(0,T_x[i]))
	y = c(rep(1,H_y[i]),rep(0,T_y[i]))
	t <- t.test(x,y)
	print(t$p.value)
}


##### Test significance of the most interrupted INDIVIDUAL for each amicus level.
### Significant for ties, but not otherwise.

cases <- c('law_P', 'law_T', 'law_R')

H_x <- c(21,64,30)
T_x <- c(10,48,34)

H_y <- c(75,102,10)
T_y <- c(18,35,13)

t <- NULL
for (i in 1:3){
	print(cases[i])
	x = c(rep(1,H_x[i]),rep(0,T_x[i]))
	y = c(rep(1,H_y[i]),rep(0,T_y[i]))
	t <- t.test(x,y)
	print(t$p.value)
}



##### Test significance of the most interrupted SIDE for each amicus level.

cases <- c('law_P', 'law_T', 'law_R')

H_x <- c(68,91,16)
T_x <- c(25,58,35)

H_y <- c(71,125,32)
T_y <- c(11,44,34)

t <- NULL
for (i in 1:3){
	print(cases[i])
	x = c(rep(1,H_x[i]),rep(0,T_x[i]))
	y = c(rep(1,H_y[i]),rep(0,T_y[i]))
	t <- t.test(x,y)
	print(t$p.value)
}


