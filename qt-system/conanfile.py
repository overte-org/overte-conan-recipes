from conan import ConanFile
from conan.tools.system import package_manager

# Note: Do NOT use conan create for this package!
# Export this package with:
# conan export . --user overte --channel system

class QtSystemConan(ConanFile):
    name = "qt"
    version = "5.15.2"
    author = "Edgar Edgar@AnotherFoxGuy.com"
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
                "qtbase5-dev",
                "qtbase5-private-dev",
                "qtwebengine5-dev",
                "qtwebengine5-dev-tools",
                "qtmultimedia5-dev",
                "libqt5opengl5-dev",
                "libqt5webchannel5-dev",
                "libqt5websockets5-dev",
                "qtxmlpatterns5-dev-tools",
                "qttools5-dev",
                "libqt5xmlpatterns5-dev",
                "libqt5svg5-dev",
                "qml-module-qtwebchannel",
                "qml-module-qtquick-controls",
                "qml-module-qtquick-controls2",
                "qml-module-qt-labs-settings",
                "qml-module-qtquick-dialogs",
                "qml-module-qtwebengine",
            ]
        )

    def package_info(self):
        self.cpp_info.filenames["cmake_find_package"] = "qt5_system"
        self.cpp_info.filenames["cmake_find_package_multi"] = "qt5_system"

        self.cpp_info.set_property("cmake_file_name", "qt5_system")

        self.cpp_info.bindirs = []
        self.cpp_info.includedirs = []
        self.cpp_info.libdirs = []
