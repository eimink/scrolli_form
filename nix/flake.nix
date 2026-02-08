{
  description = "Simple dev shell with C libs + Python (numpy, gradio)";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-25.11";
  };

  outputs = { self, nixpkgs }:
  let
    system = "x86_64-linux";
    pkgs = import nixpkgs { inherit system; };

    python = pkgs.python3.withPackages (ps: with ps; [
      numpy
      gradio
    ]);
  in
  {
    devShells.${system}.default = pkgs.mkShell {
      packages = with pkgs; [
        # C toolchain & common libs
        gcc
        cmake
        pkg-config
        glibc
        zlib

        # Python environment
        python
      ];

      shellHook = ''
        echo "🐍 Python: $(python --version)"
      '';
    };
  };
}
