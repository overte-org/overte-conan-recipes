# Overte Conan recipes
This repository contains Conan recipes used by Overte.
Some of these may be modified recipes from Conan Center, while others are not available upstream.

## Build a package
To build a package manually run a command like the following:
```bash
conan create libnode/all/conanfile.py --version 18.20.6
```

## Upload a package
To upload a package to our Artifactory, run a command like:
```bash
conan upload libnode/18.20.6@overte/experimental -r overte --only-recipe
```
Make sure that you only upload the recipe unless you know what you are doing!
Conan isn't aware of some things like the glibc version used.
