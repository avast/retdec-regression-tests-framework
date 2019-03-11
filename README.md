## RetDec Regression Tests Framework

[![Documentation Status](https://readthedocs.org/projects/retdec-regression-tests-framework/badge/?version=latest)](https://retdec-regression-tests-framework.readthedocs.io/en/latest/?badge=latest)

A framework for writing and running regression tests for RetDec and related tools.

## Requirements

To run regression tests, you must have:
* Python >= 3.4
* Clang 3.9.1 (exactly this version; download a pre-built package [from here](http://releases.llvm.org/download.html#3.9.1) and extract it somewhere)
* Cloned our [retdec](https://github.com/avast-tl/retdec) repository, built and installed RetDec.
* Cloned our [retdec-regression-tests](https://github.com/avast-tl/retdec-regression-tests) repository that contains test cases.

Additionally, on Microsoft Windows, you need a 32-bit and a 64-bit GCC compiler from [MSYS2](http://www.msys2.org/):
* Download and run an MSYS2 installer:
    * 64-bit Windows: http://sourceforge.net/projects/msys2/files/Base/x86_64/msys2-x86_64-20150916.exe/download
* Open an MSYS2 shell.
* Install a 32-bit GCC compiler via `pacman -S mingw-w64-i686-gcc`.
* Install a 64-bit GCC compiler via `pacman -S mingw-w64-x86_64-gcc`.

Additionally, to run tests for our IDA plugin, you must have:
* IDA 7.x
* Cloned our [retdec-idaplugin](https://github.com/avast-tl/retdec-idaplugin) repository, built and installed our IDA plugin.

## Installation

* Clone the repository.
* Step inside it:

  ```
  $ cd retdec-regression-tests-framework
  ```

* Install all the needed third-party Python packages, either into a virtual environment:

  ```
  $ python -m venv virtualenv
  $ source virtualenv/bin/activate
  $ pip install -r requirements.txt
  ```

  or into your home directory:

  ```
  $ pip install --user -r requirements.txt
  ```

* Verify that all dependencies have been installed by running

  ```
  python check_dependencies.py
  ```

* Create a new file `config_local.ini` with the following content (you will need to adjust the paths; use Windows style paths on Windows,  e.g. `C:\path\to\clang`):

  ```
  [runner]
  ; Path to the extracted Clang package containing subdirectories such as bin, include, lib, share.
  clang_dir = /path/to/clang
  ; Path to the cloned repository containing regression tests.
  tests_root_dir = /path/to/retdec-regression-tests
  ; Path to the RetDec's build directory.
  retdec_build_dir = /path/to/retdec/build
  ; Path to the RetDec's installation directory.
  retdec_install_dir = /path/to/retdec/installed
  ; Path to the cloned RetDec repository.
  retdec_repo_dir = /path/to/retdec
  ```

* Additionally, if you plan to run tests for our IDA plugin, you have to also include the following settings into the `[runner]` section of the `config_local.ini` file:

  ```
  idaplugin_tests_enabled = 1
  ; Path to the IDA 7.x directory.
  idaplugin_ida_dir = /path/to/ida
  ; Path to our script run-ida-decompilation from the retdec-idaplugin repository.
  idaplugin_script = /path/to/retdec-idaplugin/scripts/run-ida-decompilation.py
  ```

## Use

Use MSYS2 shell on Microsoft Windows.

To run all tests, execute

```
$ python runner.py
```

To run only tests in the given directory, execute

```
$ python runner.py path/to/directory
```

For more information, execute

```
$ python runner.py --help
```

## Documentation

The documentation is available [online](https://retdec-regression-tests-framework.readthedocs.io/en/latest/). To generate it locally, execute

```
$ make docs
```

Then, open `docs/_build/html/index.html` in your favorite web browser.

## License

Copyright (c) 2017 Avast Software, licensed under the MIT license. See the [`LICENSE`](https://github.com/avast-tl/retdec-regression-tests-framework/blob/master/LICENSE) file for more details.

The framework includes several third-party libraries, whose code and licensing information is provided in the `deps` subdirectory.

## Contributing

See [RetDec contribution guidelines](https://github.com/avast-tl/retdec/wiki/Contribution-Guidelines).
