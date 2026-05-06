idf_component_register(SRCS "main.c" "ble_wiz_bridge.c" "wiz_udp_bridge.c"
                       INCLUDE_DIRS "."
                       PRIV_REQUIRES
                         bt
                         dns_server
                         esp_adc
                         esp_common
                         esp_driver_i2c
                         esp_driver_i2s
                         esp_driver_sdmmc
                         esp_event
                         esp_http_server
                         esp_netif
                         esp_timer
                         esp_wifi
                         espressif__esp_codec_dev
                         fatfs
                         lwip
                         nvs_flash
                         sdmmc
                       EMBED_FILES "index.html")
