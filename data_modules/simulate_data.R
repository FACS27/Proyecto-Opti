
#Load data
real_data <- read.csv("data\\gen_data_reales_w_h.csv", sep = ";",
               colClasses = c("character", "character", "character", "character",
                              "character", "numeric", "numeric", "numeric", "numeric"))

#Print data
str(real_data)
summary(real_data)

#Crear tablas
table(real_data$Region)
#table(real_data$Comuna) Unused
#table(real_data$Titular) No se repite ningun titular
#table(real_data$Nombre) No need
table(real_data$Tecnologia)
table(real_data$Inversion_MMUS)
table(real_data$Capacidad_MW)
#table(real_data$Latitud) Veremos
#table(real_data$Longitud) Veremos

#Proporción de proyectos por region
region_probs <- prop.table(table(real_data$region))
simulated_region <- sample(names(region_probs), size = 4000, replace = TRUE, prob = region_probs)

#Proporcion de proyectos por tecnologia
tech_probs <- prop.table(table(real_data$type_of_technology))
simulated_technology <- sample(names(tech_probs), size = 4000, replace = TRUE, prob = tech_probs)

library(MASS)

# Extract mean, standard deviation, and correlation matrix from original data
num_data <- real_data[, c("Capacidad_MW", "Inversion_MMUS")]
means <- colMeans(num_data)
cov_matrix <- cov(num_data)

# Simulate numerical data for 'cost' and 'capacity'
simulated_num_data <- mvrnorm(n = 4000, mu = means, Sigma = cov_matrix)

# Convert to a data frame
simulated_num_df <- as.data.frame(simulated_num_data)
names(simulated_num_df) <- c("Capacidad_MW", "Inversion_MMUS")

simulated_data <- data.frame(
  Region = simulated_region,
  Comuna = NA,
  Titular = paste0("Titular", 1:4000),  # Create dummy owner names
  Nombre = paste0("Nombre", 1:4000), # Create dummy project names
  Tecnologia = simulated_technology,
  Inversion_MMUS = simulated_num_df$"Inversion_MMUS",
  Capacidad_MW = simulated_num_df$"Capacidad_MW",
  Latitud = NA,  # Simulate positions later if needed
  Longitud = NA
)

# Check correlations

#Correlacion capacidad-costo
cor(real_data[, c("Capacidad_MW", "Inversion_MMUS")])
cor(simulated_data[, c("Capacidad_MW", "Inversion_MMUS")])

#Correlacion tecnologia-costo
cor(real_data[, c("Tecnologia", "Inversion_MMUS")])
cor(simulated_data[, c("Tecnologia", "Inversion_MMUS")])

#Correlacion capacidad-tecnologia
cor(real_data[, c("Capacidad_MW", "Tecnologia")])
cor(simulated_data[, c("Capacidad_MW", "Tecnologia")])

#Correlacion region-tecnologia
cor(real_data[, c("Region", "Tecnologia")])
cor(simulated_data[, c("Region", "Tecnologia")])

#Correlacion region-costo
cor(real_data[, c("Region", "Inversion_MMUS")])
cor(simulated_data[, c("Region", "Inversion_MMUS")])



write.csv(simulated_data, "gen_data_simulada.csv", row.names = FALSE)
