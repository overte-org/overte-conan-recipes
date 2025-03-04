import re
from conan import ConanFile
from conan.tools.system import package_manager
from conan.errors import ConanInvalidConfiguration

# conan create . --user overte --channel stable

class SysConfiglibnodeConan(ConanFile):
    name = "libnode"
    version = "system"
    license = "MIT"
    url = "https://nodejs.org"
    description = (
        "Node.js is an open-source, cross-platform JavaScript runtime environment"
    )
    package_type = "shared-library"
    settings = "os", "arch", "compiler", "build_type"

    def layout(self):
        pass

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration("Only Linux is suported")
        valid = False
        regex = re.compile("NODE_MODULE_VERSION (\d+)")
        with open("/usr/include/node/node_version.h") as f:
            for line in f:
                result = regex.search(line)
                if result:
                    print(f"Nodejs module version found: {result.group(1)}")
                if result and result.group(1) == "108":
                    valid = True
        if not valid:
            raise ConanInvalidConfiguration("This version of nodejs can't be used")

    def system_requirements(self):
        apk = package_manager.Apk(self)
        apk.install(["nodejs-dev"], check=True)

        apt = package_manager.Apt(self)
        apt.install(["libnode-dev"], check=True)

        dnf = package_manager.Dnf(self)
        dnf.install(["nodejs18-devel"], check=True)

    def package_info(self):
        self.cpp_info.filenames["cmake_find_package"] = "libnode_system"
        self.cpp_info.filenames["cmake_find_package_multi"] = "libnode_system"

        self.cpp_info.set_property("cmake_file_name", "libnode_system")

        self.cpp_info.bindirs = []
        self.cpp_info.includedirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.system_libs = ["libnode"]
