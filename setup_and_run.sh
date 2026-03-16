#!/usr/bin/env bash
set -euo pipefail

# Bootstrap script to download (optional), install and run the OSINT tool.
# Examples:
#   ./setup_and_run.sh --gui
#   ./setup_and_run.sh --cli --nombre "Ana" --apellido "Pérez" --caso "KYC interno" --autorizado --modo auto
#   ./setup_and_run.sh --download https://github.com/usuario/repo.git --dir osint-panama --gui

MODE=""
DOWNLOAD_URL=""
TARGET_DIR=""
PYTHON_BIN="python3"
CLI_ARGS=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --gui)
      MODE="gui"
      shift
      ;;
    --cli)
      MODE="cli"
      shift
      # remaining args are passed to osint_tool.py
      while [[ $# -gt 0 ]]; do
        CLI_ARGS+=("$1")
        shift
      done
      ;;
    --download)
      DOWNLOAD_URL="${2:-}"
      shift 2
      ;;
    --dir)
      TARGET_DIR="${2:-}"
      shift 2
      ;;
    --python)
      PYTHON_BIN="${2:-python3}"
      shift 2
      ;;
    -h|--help)
      cat <<'USAGE'
Uso:
  ./setup_and_run.sh --gui
  ./setup_and_run.sh --cli --nombre "Ana" --apellido "Pérez" --caso "KYC interno" --autorizado --modo auto
  ./setup_and_run.sh --download <repo_git_url> --dir <carpeta> --gui

Opciones:
  --download <url>  Clona el repositorio si no existe localmente.
  --dir <carpeta>   Carpeta de trabajo (si se usa --download).
  --python <bin>    Binario Python (default: python3).
  --gui             Ejecuta interfaz gráfica.
  --cli             Ejecuta CLI y pasa el resto de parámetros a osint_tool.py.
USAGE
      exit 0
      ;;
    *)
      echo "Parámetro no reconocido: $1" >&2
      exit 1
      ;;
  esac
done

if [[ -n "$DOWNLOAD_URL" ]]; then
  if [[ -z "$TARGET_DIR" ]]; then
    echo "Si usas --download debes indicar --dir <carpeta>." >&2
    exit 1
  fi
  if [[ ! -d "$TARGET_DIR/.git" ]]; then
    git clone "$DOWNLOAD_URL" "$TARGET_DIR"
  fi
  cd "$TARGET_DIR"
fi

if [[ ! -f "osint_tool.py" || ! -f "osint_gui.py" ]]; then
  echo "No se encontraron osint_tool.py y osint_gui.py en el directorio actual." >&2
  echo "Ubícate en la raíz del proyecto o usa --download/--dir." >&2
  exit 1
fi

"$PYTHON_BIN" -m venv .venv
# shellcheck disable=SC1091
source .venv/bin/activate
python -m pip install --upgrade pip --disable-pip-version-check || echo "Aviso: no se pudo actualizar pip (sin red/proxy)."

if [[ "$MODE" == "gui" ]]; then
  python osint_gui.py
elif [[ "$MODE" == "cli" ]]; then
  python osint_tool.py "${CLI_ARGS[@]}"
else
  echo "Debes elegir --gui o --cli." >&2
  exit 1
fi
