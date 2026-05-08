import os
import platform
import shutil
import sys
import json

try:
    import psutil
except ImportError:
    psutil = None

def get_system_info():
    info = {
        "OS": f"{platform.system()} {platform.release()}",
        "CPU_Processor": platform.processor(),
        "Disk": {}
    }
    
    # Uso de Disco
    total, used, free = shutil.disk_usage("/")
    info["Disk"] = {
        "Total (GB)": round(total / (2**30), 2),
        "Used (GB)": round(used / (2**30), 2),
        "Free (GB)": round(free / (2**30), 2),
        "Percent": round((used / total) * 100, 2)
    }

    if psutil:
        info["CPU_Usage_Percent"] = psutil.cpu_percent(interval=1)
        info["RAM"] = {
            "Total (GB)": round(psutil.virtual_memory().total / (2**30), 2),
            "Available (GB)": round(psutil.virtual_memory().available / (2**30), 2),
            "Used (GB)": round(psutil.virtual_memory().used / (2**30), 2),
            "Percent": psutil.virtual_memory().percent
        }
    else:
        info["RAM"] = "Aviso: biblioteca 'psutil' não instalada. Detalhes de RAM indisponíveis."

    return info

if __name__ == "__main__":
    info = get_system_info()
    print(json.dumps(info, indent=4))
