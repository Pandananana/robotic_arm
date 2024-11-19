with import <nixpkgs> { };
let
  pythonPackages = python3Packages;
in pkgs.mkShell rec {
  name = "impurePythonEnv";
  venvDir = "./.venv";
  buildInputs = [
    # Python interpreter and venv
    pythonPackages.python
    pythonPackages.venvShellHook

    # Python packages from nixpkgs
    pythonPackages.numpy
    pythonPackages.requests
    pythonPackages.tkinter

    # OpenCV with GUI support
    (pythonPackages.opencv4.override { enableGtk2 = true; })

    # Other dependencies
    taglib
    openssl
    git
    libxml2
    libxslt
    libzip
    zlib

    # GUI dependencies
    gtk2
    pkg-config
    glib
    xorg.libX11
    xorg.libXext
    xorg.libXrender
    xorg.libICE
    xorg.libSM
  ];

  # Run this command, only after creating the virtual environment
  postVenvCreation = ''
    unset SOURCE_DATE_EPOCH
    pip install -r requirements.txt
  '';

  # Now we can execute any commands within the virtual environment.
  postShellHook = ''
    # allow pip to install wheels
    unset SOURCE_DATE_EPOCH
  '';

}