Este es tu código:

# === INPUT: interactivo, variable, o CLI ===
get_arg <- function(flag, default = NULL) {
  args <- commandArgs(trailingOnly = TRUE)
  hit <- grep(paste0("^", flag, "="), args, value = TRUE)
  if (length(hit)) return(sub(paste0("^", flag, "="), "", hit))
  default
}

# Ruta del archivo
input_path <- file.path(dirname(sys.frame(1)$ofile %||% "data_modules/sim.R"),
                        "data", "gen_data_reales_w_h.csv")
input_path <- normalizePath(input_path, winslash = "/", mustWork = TRUE)

# === AUTO-DETECCIÓN DE FORMATO ===
first_line <- readLines(input_path, n = 1)
if (grepl(";", first_line)) {
  sep_arg <- ";"
} else {
  sep_arg <- ","
}

# Si los números tienen punto decimal, usa dec="."
sample_lines <- readLines(input_path, n = 5)
if (any(grepl("[0-9]+\\.[0-9]+", sample_lines))) {
  dec_arg <- "."
} else {
  dec_arg <- ","
}

message("Leyendo CSV con separador '", sep_arg, "' y decimal '", dec_arg, "'")

# Lee el archivo
real_data <- read.csv(
  input_path,
  sep = sep_arg,
  dec = dec_arg,
  na.strings = c("", "NA"),
  colClasses = c("character","character","character","character",
                 "character","numeric","numeric","numeric","numeric")
)

# =========================
#  Simulación estratificada por REGIÓN
#  (márgenes lognormales + cópula gaussiana)
#  Mantiene Capacidad/Precio coherente por región
# =========================

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

# --------- HELPERS: ajustes robustos ---------
fit_lognorm_safe <- function(x) {
  x <- x[is.finite(x) & x > 0]
  if (length(x) < 5 || length(unique(x)) == 1L) {
    m <- mean(log(x))
    s <- sd(log(x))
    if (!is.finite(s) || s == 0) s <- 0.01
    return(list(meanlog = m, sdlog = s))
  }
  fx <- tryCatch(MASS::fitdistr(x, "lognormal"), error = function(e) NULL)
  if (is.null(fx)) {
    m <- mean(log(x)); s <- sd(log(x)); if (!is.finite(s) || s == 0) s <- 0.01
    return(list(meanlog = m, sdlog = s))
  }
  list(meanlog = unname(fx$estimate["meanlog"]), sdlog = unname(fx$estimate["sdlog"]))
}

fit_copula_safe <- function(x, y) {
  U <- pobs(cbind(x, y))                 # evita 0/1
  base <- normalCopula(param = 0, dim = 2, dispstr = "un")
  fit  <- tryCatch(fitCopula(base, U, method = "ml"), error = function(e) NULL)
  if (is.null(fit)) {
    # fallback por Kendall's tau en escala U
    tau <- suppressWarnings(cor(U[,1], U[,2], method = "kendall", use = "complete.obs"))
    if (!is.finite(tau)) tau <- 0
    rho <- sin(pi * tau / 2)             # tau = 2/pi * asin(rho)  => rho = sin(pi*tau/2)
    base@parameters <- pmin(0.99, pmax(-0.99, rho))
    return(base)
  }
  # recorta parámetros extremos por estabilidad numérica
  fit@copula@parameters <- pmin(0.99, pmax(-0.99, fit@copula@parameters))
  fit@copula
}

sim_bivar_lognorm <- function(n, model) {
  U <- rCopula(n, model$cop) # (n x 2)
  inv <- qlnorm(U[,1], meanlog = model$inv_meanlog, sdlog = model$inv_sdlog)
  cap <- qlnorm(U[,2], meanlog = model$cap_meanlog, sdlog = model$cap_sdlog)
  cbind(Inversion_MMUS = inv, Capacidad_MW = cap)
}

# --------- MODELOS: Global y por Región ---------
# Global
glob_inv <- fit_lognorm_safe(df$Inversion_MMUS)
glob_cap <- fit_lognorm_safe(df$Capacidad_MW)
glob_cop <- fit_copula_safe(df$Inversion_MMUS, df$Capacidad_MW)
model_global <- list(
  inv_meanlog = glob_inv$meanlog, inv_sdlog = glob_inv$sdlog,
  cap_meanlog = glob_cap$meanlog, cap_sdlog = glob_cap$sdlog,
  cop = glob_cop
)

# Por región (con fallback al global si n chico)
n_min_region <- 25
regions <- sort(unique(df$Region))
models_by_region <- setNames(vector("list", length(regions)), regions)

for (r in regions) {
  dfr <- df[df$Region == r, ]
  if (nrow(dfr) >= n_min_region) {
    inv <- fit_lognorm_safe(dfr$Inversion_MMUS)
    cap <- fit_lognorm_safe(dfr$Capacidad_MW)
    cop <- fit_copula_safe(dfr$Inversion_MMUS, dfr$Capacidad_MW)
    models_by_region[[r]] <- list(
      inv_meanlog = inv$meanlog, inv_sdlog = inv$sdlog,
      cap_meanlog = cap$meanlog, cap_sdlog = cap$sdlog,
      cop = cop
    )
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

# --------- SIMULACIÓN ---------
rows_list <- list()
row_id <- 1L

for (r in names(n_region)) {
  n_r <- n_region[[r]]
  if (n_r == 0) next

  # 1) Simular numéricos con el modelo de la región
  model_r <- models_by_region[[r]]
  sim_num <- sim_bivar_lognorm(n_r, model_r)
  sim_inv <- sim_num[, "Inversion_MMUS"]
  sim_cap <- sim_num[, "Capacidad_MW"]

  # 2) Asignar Tecnología según P(Tech|Region=r)
  p_tr <- tab_rt[r, , drop = TRUE]
  if (any(!is.finite(p_tr)) || sum(p_tr) <= 0) {
    # fallback: usar proporciones globales de Tech
    p_tr <- prop.table(table(df$Tecnologia))
    p_tr <- p_tr[match(tech_levels, names(p_tr))]
    p_tr[is.na(p_tr)] <- 0
    if (sum(p_tr) == 0) { # último fallback uniforme
      p_tr <- rep(1/length(tech_levels), length(tech_levels))
      names(p_tr) <- tech_levels
    }
  }
  tech_r <- sample(names(p_tr), size = n_r, replace = TRUE, prob = as.numeric(p_tr))

  # 3) Construir data.frame regional
  rows_list[[length(rows_list) + 1L]] <- data.frame(
    Id = paste0("sim_", r, "_", seq_len(n_r)),
    Region = r,
    Comuna = NA_character_,
    Titular = paste0("Titular", row_id + seq_len(n_r) - 1L),
    Nombre  = paste0("Nombre",  row_id + seq_len(n_r) - 1L),
    Tecnologia = tech_r,
    Inversion_MMUS = sim_inv,
    Capacidad_MW  = sim_cap,
    Latitud  = NA_real_,
    Longitud = NA_real_,
    is_simulated = TRUE
  )
  row_id <- row_id + n_r
}

simulated_data <- do.call(rbind, rows_list)

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