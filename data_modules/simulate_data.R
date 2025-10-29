
#Load data
real_data <- read.csv("data\\gen_data_reales_w_h.csv", sep = ";",
               colClasses = c("character", "character", "character", "character",
                              "character", "numeric", "numeric", "numeric", "numeric"))
                            

library(MASS)

 #Fit lognormal distribution to Inversion_MMUS
fit_inversion <- fitdistr(real_data$Inversion_MMUS, "lognormal")

 #Fit lognormal distribution to Capacidad_MW
fit_capacidad <- fitdistr(real_data$Capacidad_MW, "lognormal")

 #Display the fitted parameters
fit_inversion
fit_capacidad

# Set the seed for reproducibility
#set.seed(123)

# Simulate numeric variables
simulated_inversion <- rlnorm(4000, meanlog = fit_inversion$estimate["meanlog"], 
                                      sdlog = fit_inversion$estimate["sdlog"])
simulated_capacidad <- rlnorm(4000, meanlog = fit_capacidad$estimate["meanlog"], 
                                       sdlog = fit_capacidad$estimate["sdlog"])

# Calculate proportions for Tecnologia and Region
prop_tecnologia <- table(real_data$Tecnologia) / nrow(real_data)
prop_region <- table(real_data$Region) / nrow(real_data)

# Simulate categorical variables
simulated_tecnologia <- sample(names(prop_tecnologia), 4000, replace = TRUE, prob = prop_tecnologia)
simulated_region <- sample(names(prop_region), 4000, replace = TRUE, prob = prop_region)

# Load the required package
library(copula)

# Fit a copula to the original data
# Convert numeric variables to uniform [0,1] scale using their empirical cumulative distribution functions (ECDFs)
u_inversion <- ecdf(real_data$Inversion_MMUS)(real_data$Inversion_MMUS)
u_capacidad <- ecdf(real_data$Capacidad_MW)(real_data$Capacidad_MW)

# Create a data matrix with transformed variables
data_matrix <- cbind(u_inversion, u_capacidad)

summary(data_matrix)

# Fit a Gaussian copula
copula_fit <- fitCopula(normalCopula(dim = 2), data_matrix, method = "ml", start = c(0))

# Simulate from the copula
simulated_copula <- rCopula(4000, copula_fit@copula)

# Transform back to the original distributions
simulated_inversion_final <- qlnorm(simulated_copula[, 1], meanlog = fit_inversion$estimate["meanlog"], 
                                                 sdlog = fit_inversion$estimate["sdlog"])
simulated_capacidad_final <- qlnorm(simulated_copula[, 2], meanlog = fit_capacidad$estimate["meanlog"], 
                                                  sdlog = fit_capacidad$estimate["sdlog"])


# Combine all variables into a data frame
simulated_data <- data.frame(
  Region = simulated_region,
  Comuna = NA,
  Titular = paste0("Titular", 1:4000),  # Create dummy owner names
  Nombre = paste0("Nombre", 1:4000), # Create dummy project names
  Tecnologia = simulated_tecnologia,
  Inversion_MMUS = simulated_inversion_final,
  Capacidad_MW = simulated_capacidad_final,
  Latitud = NA,  # Simulate positions later if needed
  Longitud = NA
)

# Inspect the simulated data
#summary(simulated_data)



#simulated_data <- simulated_data %>% filter(!is.na(Inversion_MMUS) & !is.na(Capacidad_MW) & Inversion_MMUS <= 11000 & Capacidad_MW <= 1400 & Inversion_MMUS >= 0 & Capacidad_MW >= 0 )

# Check correlations

#Simulated data
#str(simulated_data)
summary(simulated_data)

#Real data
#str(real_data)
summary(real_data)


hist(simulated_data$Inversion_MMUS, xlim=c(0,11000), freq = FALSE)
hist(real_data$Inversion_MMUS, xlim=c(0,11000), freq=FALSE)

hist(simulated_data$Capacidad_MW, xlim=c(0,1400), freq=FALSE)
hist(real_data$Capacidad_MW, xlim=c(0,1400), freq=FALSE)

plot(real_data$Capacidad_MW, real_data$Inversion_MMUS, xlim=c(0,1400), ylim=c(0,11000))
plot(simulated_data$Capacidad_MW, simulated_data$Inversion_MMUS, xlim=c(0,1400), ylim=c(0,11000))





# Check correlations

#Correlacion capacidad-costo
cor(real_data[, c("Capacidad_MW", "Inversion_MMUS")])
cor(simulated_data[, c("Capacidad_MW", "Inversion_MMUS")])


table(real_data$Region) / 1182
table(simulated_data$Region) / 4000

table(real_data$Tecnologia)  / 1182
table(simulated_data$Tecnologia) / 4000




#write.csv(simulated_data, "gen_data_simulada.csv", row.names = FALSE)



#===========================================================

#FUCK THIS SHIT
#FUCK R
#FUCK THE SOB THAT MADE THIS PIECE OF SHIT THAT HE DARED TO CALLED A TOOL
#DOWN BELOW IS USELESS








##library(MASS)

## Fit lognormal distribution to Inversion_MMUS
##fit_inversion <- fitdistr(real_data$Inversion_MMUS, "lognormal")

## Fit lognormal distribution to Capacidad_MW
##fit_capacidad <- fitdistr(real_data$Capacidad_MW, "lognormal")

## Display the fitted parameters
##fit_inversion
##fit_capacidad



#library(dplyr)

## Group by Technology and Region to calculate means and variances for numerical variables
##grouped_stats <- real_data %>%
#  group_by(Tecnologia, Region) %>%
#  summarise(
#    mean_cost = mean(log(Inversion_MMUS), na.rm = TRUE),
#    sd_cost = sd(log(Inversion_MMUS), na.rm = TRUE),
#    mean_capacity = mean(log(Capacidad_MW), na.rm = TRUE),
#    sd_capacity = sd(log(Capacidad_MW), na.rm = TRUE),
#    n = n(),# Count for weighting
#  )

#grouped_stats <- grouped_stats %>%
#  mutate(
#    sd_cost = ifelse(is.na(sd_cost), 1, sd_cost),
#    sd_capacity = ifelse(is.na(sd_capacity), 1, sd_capacity)
#  )

##grouped_stats <- grouped_stats %>% filter(!is.na(mean_cost) & !is.na(sd_cost) & !is.na(mean_capacity) & !is.na(sd_capacity))
#print(grouped_stats, n = 100)


##Proporción de proyectos por region
#region_probs <- prop.table(table(real_data$Region))
#simulated_region <- sample(names(region_probs), size = 5000, replace = TRUE, prob = region_probs)

##Proporcion de proyectos por tecnologia
#tech_probs <- prop.table(table(real_data$Tecnologia))
#simulated_technology <- sample(names(tech_probs), size = 5000, replace = TRUE, prob = tech_probs)


#library(purrr)

## Create a data frame of the simulated categorical variables
#simulated_data <- data.frame(
#  Tecnologia = simulated_technology,
#  Region = simulated_region
#)

## Join the grouped statistics to the simulated data
#simulated_data <- simulated_data %>%
#  left_join(grouped_stats, by = c("Tecnologia", "Region"))


## Use the means and standard deviations to simulate numerical values
##set.seed(123)  # For reproducibility
#simulated_data <- simulated_data %>%
#  mutate(
#    Inversion_MMUS = map2_dbl(mean_cost, sd_cost, ~ rlnorm(1, mean = .x, sd = .y)),
#    Capacidad_MW = map2_dbl(mean_capacity, sd_capacity, ~ rlnorm(1, mean = .x, sd = .y)),
#    Comuna = NA,
#    Titular = paste0("Titular", 1:5000),  # Create dummy owner names
#    Nombre = paste0("Nombre", 1:5000), # Create dummy project names
#    Latitud = NA,  # Simulate positions later if needed
#    Longitud = NA
#  )

#simulated_data <- simulated_data %>% filter(!is.na(Inversion_MMUS) & !is.na(Capacidad_MW) & Inversion_MMUS <= 11000 & Capacidad_MW <= 1400 & Inversion_MMUS >= 0 & Capacidad_MW >= 0 )



#simulated_data <- subset(simulated_data, select = c(Region, Comuna, Titular, Nombre, Tecnologia, Inversion_MMUS, Capacidad_MW, Latitud, Longitud))

##Simulated data
##str(simulated_data)
#summary(simulated_data)

##Real data
##str(real_data)
#summary(real_data)


#hist(simulated_data$Inversion_MMUS, xlim=c(0,11000), freq = FALSE)
#hist(real_data$Inversion_MMUS, xlim=c(0,11000), freq=FALSE)

#hist(simulated_data$Capacidad_MW, xlim=c(0,1400), freq=FALSE)
#hist(real_data$Capacidad_MW, xlim=c(0,1400), freq=FALSE)

#plot(real_data$Capacidad_MW, real_data$Inversion_MMUS)
#plot(simulated_data$Capacidad_MW, simulated_data$Inversion_MMUS)



## Check correlations

##Correlacion capacidad-costo
#cor(real_data[, c("Capacidad_MW", "Inversion_MMUS")])
#cor(simulated_data[, c("Capacidad_MW", "Inversion_MMUS")])


##table(real_data$Region) / 1182
##table(simulated_data$Region) / 4733

##table(real_data$Tecnologia)  / 1182
##table(simulated_data$Tecnologia) / 4733

#library(MASS)

## Extract mean, standard deviation, and correlation matrix from original data
#num_data <- original_data[, c("cost", "capacity")]
#means <- colMeans(num_data)
#cov_matrix <- cov(num_data)

## Simulate numerical data for 'cost' and 'capacity'
#simulated_num_data <- mvrnorm(n = 4000, mu = means, Sigma = cov_matrix)

## Convert to a data frame
#simulated_num_df <- as.data.frame(simulated_num_data)
#names(simulated_num_df) <- c("cost", "capacity")
#simulated_data <- data.frame(
#  owner = paste0("Owner", 1:4000),  # Create dummy owner names
#  name = paste0("Project", 1:4000), # Create dummy project names
#  type_of_technology = simulated_technology,
#  cost = simulated_num_df$cost,
#  capacity = simulated_num_df$capacity,
#  position = NA,  # Simulate positions later if needed
#  region = simulated_region
#)
