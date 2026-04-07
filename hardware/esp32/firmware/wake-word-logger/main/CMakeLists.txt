idf_component_register(
    SRCS "main.cpp"
    INCLUDE_DIRS "."
    REQUIRES esp_micro_speech_features
             espressif__esp_codec_dev
             espressif__esp-tflite-micro
             esp_driver_i2c
             esp_driver_i2s
             esp_driver_sdmmc
             esp_adc
             esp_app_format
             esp_timer
             fatfs
             sdmmc
    EMBED_FILES "kratt.tflite")
