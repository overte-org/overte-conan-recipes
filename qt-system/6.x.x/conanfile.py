from conan import ConanFile
from conan.tools.system import package_manager

# Note: Do NOT use conan create for this package!
# Export this package with:
# conan export . --user overte --channel system

class QtSystemConan(ConanFile):
    name = "qt"
    version = "6"
    author = "Julian Groß julian.gro@overte.org & Edgar Edgar@AnotherFoxGuy.com"
    settings = "os", "arch"
    options = {
        "modules": ["ANY"],
    }
    default_options = {
        "modules": "qtwebengine",
    }
    package_type = "shared-library"

    def layout(self):
        pass

    def package_id(self):
        self.info.clear()

    def system_requirements(self):
        apt = package_manager.Apt(self)
        apt.install(
            [
                "qt6-base-dev",
                "qt6-base-private-dev",
                "qt6-webengine-dev",
                "qt6-webengine-dev-tools",
                "qt6-multimedia-dev",
                # "libqt5multimedia5-plugins", # Probably obsolete
                "qt6-image-formats-plugins", # Support for WebP textures among others
                "fcitx5-frontend-qt6", # Support for Fcitx IME (Japanese and other input). Required is `libfcitxplatforminputcontextplugin.so`
                #"libqt5opengl5-dev", # No replacement package?
                "qt6-webchannel-dev",
                "qt6-websockets-dev",
                #"qtxmlpatterns5-dev-tools",
                "qt6-tools-dev",
                #"libqt5xmlpatterns5-dev",
                "qt6-svg-dev",
                "qt6-5compat-dev", # Required by Quazip, and probably us.
                "qml-module-qtwebchannel",
                "qml-module-qtquick-controls",
                "qml-module-qtquick-controls2",
                "qml-module-qt-labs-settings",
                "qml-module-qtquick-dialogs",
                "qml-module-qtwebengine",
            ], update=True, check=True
        )
        apt.install_substitutes(
            ["fcitx5-frontend-qt6"], ["fcitx-frontend-qt6"]  # On Debian Forky, both Fcitx5 and Fcitx4 are availalbe, while Ubuntu 22.04 only has Fcitx4
        )

    def package_info(self):
        self.cpp_info.filenames["cmake_find_package"] = "qt6_system"
        self.cpp_info.filenames["cmake_find_package_multi"] = "qt6_system"

        self.cpp_info.set_property("cmake_file_name", "qt6_system")

        self.cpp_info.bindirs = []
        self.cpp_info.includedirs = []
        self.cpp_info.libdirs = []
