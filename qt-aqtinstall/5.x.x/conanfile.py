import platform

from conan import ConanFile
from conan.tools.files import download
import os
import shutil

# Note: Do NOT use conan create for this package!
# Export this package with:
# conan export . --user overte --channel aqt

class AqtConan(ConanFile):
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

    def source(self):
        if platform.system() == "Windows":
            download(self, "https://github.com/AnotherFoxGuy/aqtinstall-onefile/releases/latest/download/aqt-win.exe",
                     "aqt.exe")
        elif platform.system() == "Darwin":
            download(self, "https://github.com/AnotherFoxGuy/aqtinstall-onefile/releases/latest/download/aqt-macos",
                     "aqt")
        else:
            download(self, "https://github.com/AnotherFoxGuy/aqtinstall-onefile/releases/latest/download/aqt-linux",
                     "aqt")
            self.run("chmod a+x aqt")

    def package(self):
        glob_args = "-O {0} -m {1}".format(self.source_folder, self.options.modules)

        if self.settings.os == "Windows":
            self.run("aqt install-qt windows desktop {0} win64_msvc2019_64 {1}".format(self.version, glob_args))
            # copy(self, "*", os.path.join(self.source_folder, self.version, "msvc2019_64"), self.package_folder)
            src_dir = os.path.join(self.source_folder, self.version, "msvc2019_64")
            file_names = os.listdir(src_dir)
            for file_name in file_names:
                shutil.move(os.path.join(src_dir, file_name), self.package_folder)
        elif self.settings.os == "Macos":
            self.run("./aqt install-qt macos desktop {0} win64_msvc2019_64 {1}".format(self.version, glob_args))
        else:
            self.run("./aqt install-qt linux desktop {0} gcc_64 {1}".format(self.version, glob_args))
            src_dir = os.path.join(self.source_folder, self.version, "gcc_64")
            file_names = os.listdir(src_dir)
            for file_name in file_names:
                shutil.move(os.path.join(src_dir, file_name), self.package_folder)

    def package_info(self):
        self.buildenv_info.define_path("Qt5_ROOT", self.package_folder)
        self.runenv_info.define_path("Qt5_ROOT", self.package_folder)
