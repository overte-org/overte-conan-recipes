import os
from conan import ConanFile
from conan.tools.files import get, copy, collect_libs, rename, apply_conandata_patches, export_conandata_patches
from conan.tools.gnu import Autotools, AutotoolsToolchain, PkgConfigDeps
from conan.tools.env import Environment, VirtualBuildEnv
from conan.tools.microsoft import (
    VCVars,
    MSBuild,
    MSBuildToolchain,
    msvs_toolset,
)
from conan.tools.scm import Version
from conan.tools.build import check_min_cppstd

class libnodeConan(ConanFile):
    name = "libnode"
    license = "MIT"
    url = "https://nodejs.org"
    description = (
        "Node.js is an open-source, cross-platform JavaScript runtime environment"
    )
    settings = "os", "compiler", "build_type", "arch"
    package_type = "shared-library"

    @property
    def _min_cppstd(self):
        if Version(self.version) >= "22":
            return 20
        return 17

    def __add_shared(self, pkg_name, libname):
        libs = self.dependencies[pkg_name].cpp_info.libs
        libs += self.dependencies[pkg_name].cpp_info.system_libs
        for c in self.dependencies[pkg_name].cpp_info.components.values():
            libs += c.libs
            libs += c.system_libs
        includes = ",".join(self.dependencies[pkg_name].cpp_info.includedirs)
        libnames = ",".join(libs)
        libpath = ",".join(self.dependencies[pkg_name].cpp_info.libdirs)
        return [
            f"--shared-{libname}",
            f"--shared-{libname}-includes={includes}",
            f"--shared-{libname}-libname={libnames}",
            f"--shared-{libname}-libpath={libpath}",
        ]

    def build_requirements(self):
        self.tool_requires("nasm/2.15.05")

    def requirements(self):
        self.requires("brotli/[>1.0 <1.2]")
        self.requires("llhttp/[^9.3]")
        # self.requires("libnghttp2/[>1.50 <1.60]")
        # self.requires("libuv/[>1.40 <1.50]")
        self.requires("openssl/1.1.1w")
        self.requires("zlib/[>=1.3 <1.4]")

    def configure(self):
        # All "shared" dependencies need to be linked statically, otherwise bytecode_builtins_list_generator fails to find them.
        self.options["brotli"].shared = False
        self.options["llhttp"].shared = False
        self.options["openssl"].shared = False
        self.options["zlib"].shared = False

    def export_sources(self):
        # *Copy* patches into source.
        export_conandata_patches(self)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        # Apply previously copied patches.
        apply_conandata_patches(self)

    def generate(self):
        if self.settings.os == "Windows":
            toolset = msvs_toolset(self)
            # Match MSVC version to Visual Studio version.
            msvs_version = {"192": "2019", "193": "2022", "194": "2022"}.get(
                str(self.settings.compiler.version)
            )
            if msvs_version == None:
                raise KeyError(f"Unknown Visual Studio version for MSVC {str(self.settings.compiler.version)}! "
                               f"Please add it to the conanfile.")
            node_build_env = Environment()
            node_build_env.define("GYP_MSVS_VERSION", msvs_version)
            node_build_env.define("PLATFORM_TOOLSET", toolset)
            envvars = node_build_env.vars(self)
            envvars.save_script("node_build_env")
            vbe = VirtualBuildEnv(self)
            vbe.generate()
            tc = MSBuildToolchain(self)
            tc.configuration = str(self.settings.build_type)
            tc.generate()
            tc = VCVars(self)
            tc.generate()
        else:
            tc = AutotoolsToolchain(self)
            tc.generate()
            pc = PkgConfigDeps(self)
            pc.generate()
            node_build_env = Environment()
            node_build_env.define("PKG_CONFIG_PATH", self.build_folder)
            envvars = node_build_env.vars(self)
            envvars.save_script("node_build_env")
            rename(self, "libllhttp.pc", "http_parser.pc")

    def build(self):
        args = [
            # "--ninja",
            "--shared",
            "--without-npm",
            "--without-corepack",
            "--without-intl",
            "--v8-enable-object-print",
            "--prefix=%s" % self.package_folder,
        ]

        # TODO Fix building with these libs
        # args += self.__add_shared("", "cares")
        # args += self.__add_shared("", "nghttp3")
        # args += self.__add_shared("", "ngtcp2")
        # args += self.__add_shared("libnghttp2", "nghttp2")
        # args += self.__add_shared("libuv", "libuv")
        args += self.__add_shared("brotli", "brotli")
        args += self.__add_shared("llhttp", "http-parser")
        args += self.__add_shared("openssl", "openssl")
        args += self.__add_shared("zlib", "zlib")

        # Setting --debug on RelWithDebInfo causes missing includes in base64 and uvwasi.
        args.append("--debug" if self.settings.build_type == "Debug" else "")
        if self.settings.arch == "armv8":
            args.append("--dest-cpu=arm64")
        else:
            args.append("--dest-cpu=%s" % self.settings.arch)

        if self.settings.os == "Linux" and self.settings.arch != "armv8":
            # node doesn't build with the gdb argument on aarch64
            args.append("--gdb")

        if self.settings.os == "Windows":
            self.run(
                "python configure.py %s" % (" ".join(args)), env=["node_build_env"]
            )
            # self.run("ninja libnode", env=["node_build_env"])
            msbuild = MSBuild(self)
            msbuild.build("node.sln", targets=["libnode"])
        else:
            self.run(
                "python3 configure.py %s" % (" ".join(args)), env=["node_build_env"]
            )
            autotools = Autotools(self)
            autotools.make(args=["-C out", "BUILDTYPE=%s" % self.settings.build_type], target="libnode")

    def package(self):
        if self.settings.os == "Windows":
            self.run(
                "python ./tools/install.py --headers-only --is-win --dest-dir %s\\ --prefix \\ install"
                % self.package_folder
            )
            copy(
                self,
                "*.h",
                os.path.join(
                    self.source_folder, "deps", "v8", "include", "libplatform"
                ),
                os.path.join(self.package_folder, "include", "libplatform"),
                keep_path=False,
            )
            copy(
                self,
                "*.h",
                os.path.join(self.source_folder, "deps", "v8", "include", "cppgc"),
                os.path.join(self.package_folder, "include", "cppgc"),
                keep_path=False,
            )
            copy(
                self,
                "libnode.lib",
                os.path.join(self.source_folder, "out", str(self.settings.build_type)),
                os.path.join(self.package_folder, "lib"),
                keep_path=False,
            )
            copy(
                self,
                "v8_libplatform.lib",
                os.path.join(
                    self.source_folder, "out", str(self.settings.build_type), "lib"
                ),
                os.path.join(self.package_folder, "lib"),
                keep_path=False,
            )
            copy(
                self,
                "*.dll",
                os.path.join(self.source_folder, "out"),
                os.path.join(self.package_folder, "bin"),
                keep_path=False,
            )
        else:
            self.run(
                "python3 ./tools/install.py --headers-only --dest-dir %s/ --prefix / install"
                % self.package_folder
            )
            copy(
                self,
                "*.h",
                os.path.join(
                    self.source_folder, "deps", "v8", "include", "libplatform"
                ),
                os.path.join(self.package_folder, "include", "libplatform"),
                keep_path=False,
            )
            copy(
                self,
                "*.h",
                os.path.join(self.source_folder, "deps", "v8", "include", "cppgc"),
                os.path.join(self.package_folder, "include", "cppgc"),
                keep_path=False,
            )
            copy(
                self,
                "libnode.*",
                os.path.join(self.source_folder, "out", str(self.settings.build_type)),
                os.path.join(self.package_folder, "lib"),
                keep_path=False
            )

    def package_info(self):
        self.cpp_info.includedirs = ["include", "include/node"]
        if self.settings.os == "Linux":
            # Hack to work around collect_libs() not being able to deal with .so.x.y.z files.
            # See: https://github.com/conan-io/conan/pull/17816
            self.cpp_info.libs = ['libnode.so.127']
        else: # Windows and macOS
            self.cpp_info.libs = collect_libs(self)

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)
