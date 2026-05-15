idf_component_register(
    SRCS "main.c"
    INCLUDE_DIRS "."
    REQUIRES espressif__esp_codec_dev
             esp_driver_i2c
             esp_driver_i2s
             esp_driver_uart)
