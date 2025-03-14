########## MACROS ###########################################################################
#############################################################################################

# Requires CMake > 3.15
if(${CMAKE_VERSION} VERSION_LESS "3.15")
    message(FATAL_ERROR "The 'CMakeDeps' generator only works with CMake >= 3.15")
endif()

if(xkeyboard-config_FIND_QUIETLY)
    set(xkeyboard-config_MESSAGE_MODE VERBOSE)
else()
    set(xkeyboard-config_MESSAGE_MODE STATUS)
endif()

include(${CMAKE_CURRENT_LIST_DIR}/cmakedeps_macros.cmake)
include(${CMAKE_CURRENT_LIST_DIR}/xkeyboard-configTargets.cmake)
include(CMakeFindDependencyMacro)

check_build_type_defined()

foreach(_DEPENDENCY ${xkeyboard-config_FIND_DEPENDENCY_NAMES} )
    # Check that we have not already called a find_package with the transitive dependency
    if(NOT ${_DEPENDENCY}_FOUND)
        find_dependency(${_DEPENDENCY} REQUIRED ${${_DEPENDENCY}_FIND_MODE})
    endif()
endforeach()

set(xkeyboard-config_VERSION_STRING "system")
set(xkeyboard-config_INCLUDE_DIRS ${xkeyboard-config_INCLUDE_DIRS_RELEASE} )
set(xkeyboard-config_INCLUDE_DIR ${xkeyboard-config_INCLUDE_DIRS_RELEASE} )
set(xkeyboard-config_LIBRARIES ${xkeyboard-config_LIBRARIES_RELEASE} )
set(xkeyboard-config_DEFINITIONS ${xkeyboard-config_DEFINITIONS_RELEASE} )


# Only the last installed configuration BUILD_MODULES are included to avoid the collision
foreach(_BUILD_MODULE ${xkeyboard-config_BUILD_MODULES_PATHS_RELEASE} )
    message(${xkeyboard-config_MESSAGE_MODE} "Conan: Including build module from '${_BUILD_MODULE}'")
    include(${_BUILD_MODULE})
endforeach()


