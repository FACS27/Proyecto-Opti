#Este lo puse solo para ver si calzaban todo lo que pedíamos

# Comprobador.R
suppressPackageStartupMessages({
  library(readr)
  library(dplyr)
  library(stringr)
})

# --- helper: números con coma o punto decimal ---
parse_num_any <- function(x) {
  y1 <- suppressWarnings(readr::parse_number(as.character(x),
                                             locale = readr::locale(decimal_mark = ",", grouping_mark = ".")))
  y2 <- suppressWarnings(readr::parse_number(as.character(x),
                                             locale = readr::locale(decimal_mark = ".", grouping_mark = ",")))
  out <- ifelse(is.na(y1) & !is.na(y2), y2, y1)
  as.numeric(out)
}

# --- función principal ---
resumen_por_region <- function(file_path) {
  df <- readr::read_delim(
    file = file_path,
    delim = ";",
    trim_ws = TRUE,
    show_col_types = FALSE,
    locale = locale(encoding = "UTF-8")
  )

  cols_req <- c("Region","Comuna","Titular","Nombre","Tecnologia",
                "Inversion_MMUS","Capacidad_MW","Latitud","Longitud")
  faltan <- setdiff(cols_req, names(df))
  if (length(faltan) > 0) stop("Faltan columnas: ", paste(faltan, collapse = ", "))

  df <- df %>%
    mutate(
      Inversion_MMUS = parse_num_any(Inversion_MMUS),
      Capacidad_MW   = parse_num_any(Capacidad_MW),
      Latitud        = parse_num_any(Latitud),
      Longitud       = parse_num_any(Longitud),
      ratio_inv_cap  = ifelse(is.na(Capacidad_MW) | Capacidad_MW == 0,
                              NA_real_, Inversion_MMUS / Capacidad_MW)
    )

  total_n <- nrow(df)

  df %>%
    group_by(Region) %>%
    summarise(
      n_registros       = n(),
      media             = mean(ratio_inv_cap, na.rm = TRUE),
      mediana           = median(ratio_inv_cap, na.rm = TRUE),
      q1                = quantile(ratio_inv_cap, 0.25, na.rm = TRUE, names = FALSE),
      q3                = quantile(ratio_inv_cap, 0.75, na.rm = TRUE, names = FALSE),
      promedio          = mean(ratio_inv_cap, na.rm = TRUE),
      desv_estandar     = sd(ratio_inv_cap, na.rm = TRUE),
      cant_solar        = sum(str_detect(Tecnologia, regex("^\\s*solar\\s*$", ignore_case = TRUE)), na.rm = TRUE),
      cant_eolica       = sum(str_detect(Tecnologia, regex("^\\s*e[oó]lica\\s*$", ignore_case = TRUE)), na.rm = TRUE),
      proporcion_region = n_registros / total_n,
      porcentaje_region = 100 * proporcion_region,
      .groups = "drop"
    ) %>%
    mutate(across(c(media, mediana, q1, q3, promedio, desv_estandar),
                  ~ ifelse(is.nan(.x), NA_real_, .x))) %>%
    arrange(desc(n_registros))
}

# --- ruta por defecto a tu archivo en data_modules/data ---
input_path <- normalizePath(file.path("gen_data_simulados_2800.csv"),
                            winslash = "/", mustWork = TRUE)

# --- correr y guardar ---
resultado <- resumen_por_region(input_path)
print(resultado, n = nrow(resultado))

# guarda al lado del CSV de entrada
out_path <- file.path(dirname(input_path), "resumen_por_region.csv")
readr::write_csv(resultado, out_path)
message("Resumen guardado en: ", out_path)