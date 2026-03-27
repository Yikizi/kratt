set(srcs
    "main.c"
    "esp_hid_gap.c")

idf_component_register(
    SRCS "${srcs}"
    INCLUDE_DIRS "."
    REQUIRES esp_hid
    PRIV_REQUIRES bt nvs_flash esp_adc)
