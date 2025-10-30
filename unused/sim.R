#Load data
real_data <- read.csv("data_modules\\data\\gen_data_reales_w_h.csv", sep = ";",
                      colClasses = c("character", "character", "character", "character",
                                     "character", "numeric", "numeric", "numeric", "numeric"))

set.seed(123)

req_pkgs <- c("MASS","copula")
to_install <- req_pkgs[!req_pkgs %in% installed.packages()[, "Package"]]
if (length(to_install)) install.packages(to_install)
invisible(lapply(req_pkgs, library, character.only = TRUE))

# --------- CARGA (opcional si ya tienes real_data) ---------
# Ajusta dec="," o "." según tu archivo. Sep suele ser ";" si viene de Excel/;.
# real_data <- read.csv(
#   "data/gen_data_reales_w_h.csv",
#   sep = ";", dec = ".",
#   na.strings = c("", "NA"),
#   colClasses = c("character","character","character","character",
#                  "character","numeric","numeric","numeric","numeric")
# )

# --------- LIMPIEZA MÍNIMA ---------
# Requerimos positivos para lognormal y sin NA en Región/Tecnología
df <- subset(
  real_data,
  is.finite(Inversion_MMUS) & Inversion_MMUS > 0 &
  is.finite(Capacidad_MW)   & Capacidad_MW   > 0 &
  !is.na(Region) & !is.na(Tecnologia)
)

stopifnot(nrow(df) >= 100)  # sanity

# --------- HELPERS (versión "ajustada a real") ---------

# Cópula robusta (igual que antes)
fit_copula_safe <- function(x, y) {
  U <- pobs(cbind(x, y))                 # evita 0/1
  base <- normalCopula(param = 0, dim = 2, dispstr = "un")
  fit  <- tryCatch(fitCopula(base, U, method = "ml"), error = function(e) NULL)
  if (is.null(fit)) {
    tau <- suppressWarnings(cor(U[,1], U[,2], method = "kendall", use = "complete.obs"))
    if (!is.finite(tau)) tau <- 0
    rho <- sin(pi * tau / 2)
    base@parameters <- pmin(0.99, pmax(-0.99, rho))
    return(base)
  }
  fit@copula@parameters <- pmin(0.99, pmax(-0.99, fit@copula@parameters))
  fit@copula
}

# Modelo "empírico" por región (márgenes = cuantiles empíricos)
build_empirical_model <- function(x, y) {
  x <- x[is.finite(x) & x > 0]
  y <- y[is.finite(y) & y > 0]
  stopifnot(length(x) >= 5, length(y) >= 5)
  list(
    x = x,
    y = y,
    cop = fit_copula_safe(x, y)
  )
}

# Simular par (Inv, Cap) usando cópula + cuantiles empíricos
# JITTER_SD controla cuánta variabilidad extra agregamos (muy pequeña)
JITTER_SD <- 0.01  # 1% de ruido multiplicativo

sim_bivar_empirical <- function(n, model, jitter_sd = JITTER_SD) {
  U <- rCopula(n, model$cop)  # (n x 2)
  inv <- as.numeric(stats::quantile(model$x, probs = U[,1], type = 8, names = FALSE))
  cap <- as.numeric(stats::quantile(model$y, probs = U[,2], type = 8, names = FALSE))
  if (jitter_sd > 0) {
    inv <- inv * exp(rnorm(n, 0, jitter_sd))
    cap <- cap * exp(rnorm(n, 0, jitter_sd))
  }
  cbind(Inversion_MMUS = inv, Capacidad_MW = cap)
}

# --------- MODELOS: Global y por Región (empíricos) ---------
n_min_region <- 25

# Global empírico (fallback)
model_global <- build_empirical_model(df$Inversion_MMUS, df$Capacidad_MW)

regions <- sort(unique(df$Region))
models_by_region <- setNames(vector("list", length(regions)), regions)

for (r in regions) {
  dfr <- df[df$Region == r, ]
  if (nrow(dfr) >= n_min_region) {
    models_by_region[[r]] <- build_empirical_model(dfr$Inversion_MMUS, dfr$Capacidad_MW)
  } else {
    models_by_region[[r]] <- model_global
  }
}

# --------- CUÁNTOS SIMULAR POR REGIÓN Y TECNOLOGÍA ---------
additional_n <- 2800

# Proporción por región
p_region <- prop.table(table(df$Region))
n_region <- round(as.numeric(p_region) * additional_n)
# Ajuste para que sume exactamente additional_n
while (sum(n_region) != additional_n) {
  diff <- additional_n - sum(n_region)
  idx <- sample(seq_along(n_region), 1)
  n_region[idx] <- n_region[idx] + sign(diff)
}
names(n_region) <- names(p_region)

# Matriz P(Tecnologia | Region)
tab_rt <- prop.table(table(df$Region, df$Tecnologia), 1)  # por fila (Región)
tech_levels <- colnames(tab_rt)

# --------- SIMULACIÓN (bootstrap empírico por Región y Tecnología) ---------
rows_list <- list()
row_id <- 1L

for (r in names(n_region)) {
  n_r <- n_region[[r]]
  if (n_r == 0) next

  dfr <- df[df$Region == r, , drop = FALSE]
  # Proporciones condicionales reales P(Tecnologia|Region=r)
  p_tr <- prop.table(table(dfr$Tecnologia))
  p_tr <- p_tr[order(names(p_tr))]

  # Tamaños por tecnología que suman n_r
  techs_r <- names(p_tr)
  n_tr <- round(as.numeric(p_tr) * n_r)
  while (sum(n_tr) != n_r) {  # ajuste de redondeo
    diff <- n_r - sum(n_tr)
    i <- sample(seq_along(n_tr), 1)
    n_tr[i] <- n_tr[i] + sign(diff)
  }

  # Para cada tecnología, re-muestrear filas REALES con reemplazo (pares Inv, Cap)
  sim_chunks <- list()
  for (i in seq_along(techs_r)) {
    tname <- techs_r[i]
    k <- n_tr[i]
    if (k == 0) next

    sub_rt <- dfr[dfr$Tecnologia == tname, , drop = FALSE]
    if (nrow(sub_rt) == 0) next

    idx <- sample.int(nrow(sub_rt), size = k, replace = TRUE)

    sim_chunks[[length(sim_chunks) + 1L]] <- data.frame(
      Id = paste0("sim_", r, "_", seq_len(k) + row_id - 1L),
      Region = r,
      Comuna = NA_character_,              # se completa más abajo
      Titular = paste0("Titular", row_id + seq_len(k) - 1L),
      Nombre  = paste0("Nombre",  row_id + seq_len(k) - 1L),
      Tecnologia = tname,
      Inversion_MMUS = sub_rt$Inversion_MMUS[idx],  # PAR EMPÍRICO REAL
      Capacidad_MW  = sub_rt$Capacidad_MW[idx],     # PAR EMPÍRICO REAL
      Latitud  = NA_real_,
      Longitud = NA_real_,
      is_simulated = TRUE
    )
    row_id <- row_id + k
  }

  if (length(sim_chunks)) {
    rows_list[[length(rows_list) + 1L]] <- do.call(rbind, sim_chunks)
  }
}

simulated_data <- do.call(rbind, rows_list)

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

# --- SOLO SIMULADOS: completar campos y exportar en formato original ---

# Orden y columnas EXACTAS del dataset original
col_order_out <- c(
  "Region","Comuna","Titular","Nombre","Tecnologia",
  "Inversion_MMUS","Capacidad_MW","Latitud","Longitud"
)

# Asegurar que existan todas las columnas y en el orden correcto
for (cc in setdiff(col_order_out, names(simulated_data))) {
  simulated_data[[cc]] <- NA
}
simulated_out <- simulated_data[, col_order_out]

# Diagnóstico breve (opcional)
cat("\n--- TOTALES (solo simulados) ---\n")
cat("n =", nrow(simulated_out), "\n")
cat("\n--- Ejemplo de filas ---\n")
print(utils::head(simulated_out, 3))

# Exportar: MISMO LUGAR que antes, con encabezado y ; como separador
write.table(
  simulated_out,
  file = "gen_data_simulados_2800.csv",  # puedes cambiar el nombre si prefieres
  sep = ";",
  dec = ".",
  row.names = FALSE,
  col.names = TRUE,
  quote = FALSE,
  fileEncoding = "UTF-8"
)

cat("\n✅ Archivo exportado (solo 2800 simulados, con encabezado): gen_data_simulados_2800.csv\n")