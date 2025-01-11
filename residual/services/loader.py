import importlib
import pkgutil
import residual.services as services

def load_services():
    for _, module_name, _ in pkgutil.iter_modules(services.__path__):
        importlib.import_module(f"residual.services.{module_name}")
