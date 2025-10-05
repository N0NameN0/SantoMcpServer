import uvicorn

import sys
from importlib import metadata as importlib_metadata

from fastmcp import FastMCP
import importlib
import pkgutil
import tool_enabled

import logging

# ===== VARIABLES =================================
NAME="Santo MCP Server"
HOST="127.0.0.1"
PORT=8000
TRANSPORT="http"
PATH="/mcp"
#========================================================




# ===== Config du logger ================================
logging.basicConfig(
    level=logging.INFO,
    format='\033[32m%(levelname)s:     \033[0m%(asctime)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.propagate = False

logging.getLogger("uvicorn").setLevel(logging.WARNING)
logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
logging.getLogger("starlette").setLevel(logging.WARNING)




#========================================================




# ===== Startup banner =================================
ASCII_BANNER = r"""
      _____             _        __  __  _____ _____
     / ____|           | |      |  \/  |/ ____|  __ \
    | (___   __ _ _ __ | |_ ___ | \  / | |    | |__) |
     \___ \ / _` | '_ \| __/ _ \| |\/| | |    |  ___/
     ____) | (_| | | | | || (_) | |  | | |____| |
    |_____/ \__,_|_| |_|\__\___/|_|  |_|\_____|_|
                                           Server v1.0

"""

def _pkg_version(pkg: str) -> str:
    try:
        return importlib_metadata.version(pkg)
    except Exception:
        return "unknown"

def print_startup_banner():
    v_fastmcp = _pkg_version("fastmcp")
    v_uvicorn = _pkg_version("uvicorn")
    v_python = sys.version.split()[0]

    lines = [
	ASCII_BANNER,
        f"	🖥️  Server Name  : {NAME}",
        f"	📦 Transport    : {TRANSPORT}",
        f"	🔗 Server URL:  : http://{HOST}:{PORT}{PATH}",
	"",
        f"	🏎️  FastMCP      : {v_fastmcp}",
	f"	🦄 Uvicorn      : {v_uvicorn}",
        f"	🐍 Python       : {v_python}",
        "",
    ]

    # Ajouter la section des outils chargés
    if loaded_modules:
        lines.append("	🔧 Loaded Modules:")
        for module_name in sorted(loaded_modules):
            lines.append(f"		• {module_name}")
        lines.append("")
        lines.append(f"	📊 Total Modules : {len(loaded_modules)}")
        lines.append("")

    banner = "\n".join(lines)
    print(banner)

#========================================================


mcp = FastMCP(NAME)

loaded_modules = []

for _, module_name, _ in pkgutil.iter_modules(tool_enabled.__path__):
    try:
        module = importlib.import_module(f"tool_enabled.{module_name}")
        if hasattr(module, "register_tool"):
            module.register_tool(mcp)
            loaded_modules.append(module_name)
    except Exception as e:
        logger.error(f"❌ Failed to load module {module_name}: {e}")

app = mcp.http_app(transport=TRANSPORT, path=PATH)

if __name__ == "__main__":
    try:
        print_startup_banner()
        uvicorn.run(app, host=HOST, port=PORT)
    except KeyboardInterrupt:
        print("\nServer stopped by user. Exiting cleanly.")
