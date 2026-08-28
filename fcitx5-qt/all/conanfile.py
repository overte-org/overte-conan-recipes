import os
from conan import ConanFile
from conan.tools.files import collect_libs, copy, get, apply_conandata_patches, export_conandata_patches
from conan.tools.scm import Version
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps

class WAPConan(ConanFile):
    name = "fcitx5-qt"
    package_type = "shared-library"
    license = "Mixed LGPL2.1+ and BSD"
    url = "https://github.com/fcitx/fcitx5-qt"
    description = "fcitx5-qt is the Qt im-module for fcitx5 and it's needed to use fcitx5 with Qt-based applications."
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "ENABLE_QT5": [True, False],
        "ENABLE_QT6": [True, False],
        "ENABLE_X11": [True, False],
        "BUILD_ONLY_PLUGIN": [True, False],
        "BUILD_STATIC_PLUGIN": [True, False],
        "WITH_FCITX_PLUGIN_NAME": [True, False],
        "ENABLE_QT6_WAYLAND_WORKAROUND": [True, False]
    }
    default_options = {
        "ENABLE_QT5": True,
        "ENABLE_QT6": False,
        "ENABLE_X11": True,
        "BUILD_ONLY_PLUGIN": True,
        "BUILD_STATIC_PLUGIN": False,
        "WITH_FCITX_PLUGIN_NAME": True,
        "ENABLE_QT6_WAYLAND_WORKAROUND": True
    }

    def layout(self):
        cmake_layout(self)

    def export_sources(self):
        # *Copy* patches into source.
        export_conandata_patches(self)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        # Apply previously copied patches.
        apply_conandata_patches(self)

    def generate(self):
        tc = CMakeToolchain(self)
        #tc.cache_variables["BUILD_SHARED"] = self.options.shared
        tc.cache_variables["ENABLE_QT5"] = self.options.ENABLE_QT5
        tc.cache_variables["ENABLE_QT6"] = self.options.ENABLE_QT6
        tc.cache_variables["ENABLE_X11"] = self.options.ENABLE_X11
        tc.cache_variables["BUILD_ONLY_PLUGIN"] = self.options.BUILD_ONLY_PLUGIN
        tc.cache_variables["BUILD_STATIC_PLUGIN"] = self.options.BUILD_STATIC_PLUGIN
        tc.cache_variables["WITH_FCITX_PLUGIN_NAME"] = self.options.WITH_FCITX_PLUGIN_NAME
        tc.cache_variables["ENABLE_QT6_WAYLAND_WORKAROUND"] = self.options.ENABLE_QT6_WAYLAND_WORKAROUND
        tc.cache_variables["CMAKE_INSTALL_QT5PLUGINDIR"] = os.path.join(self.package_folder, "lib")
        tc.cache_variables["CMAKE_INSTALL_QT6PLUGINDIR"] = os.path.join(self.package_folder, "lib")
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def requirements(self):
        if self.options.ENABLE_QT5:
            #self.requires("qt/5.15.18")  # We override this in Overte's conanfile.py
            self.requires("qt/5.15.2@overte/system")
            #self.requires("qt/5.15.18@overte/experimental#3a9079f3023351a7319be352cc6f4665")
        if self.options.ENABLE_QT6:
            self.requires("qt/6.11.1")  # We override this in Overte's conanfile.py
        if self.options.ENABLE_X11:
            self.requires("xorg/system")
        if not self.options.BUILD_ONLY_PLUGIN:  # TODO: Looks like this adds translations for the plugin?
            self.requires("Fcitx5Utils")

    def build_requirements(self):
        self.tool_requires("extra-cmake-modules/6.8.0")

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "*", src=os.path.join(self.source_folder + "LICENSES"), dst=os.path.join(self.package_folder, "licenses")) # FIXME: This doesn't work and I have no idea why.
        copy(self, "README.md", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = collect_libs(self)
