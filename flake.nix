{
  description = "Template for a direnv shell, with Python";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs = { self, nixpkgs }:
  let
    system = "x86_64-linux";
    pkgs = nixpkgs.legacyPackages.${system};

    mypython = let
      packageOverrides = prev: final: {
        selenium = final.selenium.overridePythonAttrs (old: {
          src = pkgs.fetchFromGitHub {
            owner = "SeleniumHQ";
            repo = "selenium";
            rev = "refs/tags/selenium-4.8.0";
            hash = "sha256-YTi6SNtTWuEPlQ3PTeis9osvtnWmZ7SRQbne9fefdco=";
          };
          postInstall = ''
            install -Dm 755 ../rb/lib/selenium/webdriver/atoms/getAttribute.js $out/${pkgs.python3Packages.python.sitePackages}/selenium/webdriver/remote/getAttribute.js
            install -Dm 755 ../rb/lib/selenium/webdriver/atoms/isDisplayed.js $out/${pkgs.python3Packages.python.sitePackages}/selenium/webdriver/remote/isDisplayed.js
          '';
        });
      }; in pkgs.python3.override { inherit packageOverrides; };

  in
  {
    devShells.${system}.default = pkgs.mkShell {
      buildInputs = with pkgs; [
        chromedriver
        chromium
        (let
          python-packages = ps: with ps; [
            requests
            lxml
            selenium
            (let
              pname = "openlocationcode";
              version = "1.0.1";
            in pkgs.python3Packages.buildPythonPackage {
              inherit pname version;
              src = pkgs.fetchPypi {
                inherit pname version;
                sha256 = "sha256-b8AQioIUtl10lkEFvWlkWop1KSN/Deaq3PqDzDNzs1k=";
              };
              doCheck = false;
            })
          ];
        in mypython.withPackages python-packages)
      ];
    };
  };
}

