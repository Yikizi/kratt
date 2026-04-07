file(GLOB_RECURSE ESP_MICRO_SPEECH_FEATURES_SRCS
     "${CMAKE_CURRENT_LIST_DIR}/src/*.c")

idf_component_register(
    SRCS "${ESP_MICRO_SPEECH_FEATURES_SRCS}"
    INCLUDE_DIRS "include" "src")
