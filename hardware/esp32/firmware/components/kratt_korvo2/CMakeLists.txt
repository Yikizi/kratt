idf_component_register(SRCS "kratt_korvo2_board.c"
                            "kratt_korvo2_buttons.c"
                       INCLUDE_DIRS "include"
                       REQUIRES button esp_adc esp_driver_gpio)
