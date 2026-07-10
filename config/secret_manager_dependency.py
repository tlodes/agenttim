"""SecretManager dependency - separated to avoid circular imports."""
from shared.secrets.secret_manager import SecretManager
from shared.secrets.secret_service import get_secret_manager_instance
from agenttim.config.settings import get_settings
def get_secret_manager() -> SecretManager:

    """Get the singleton instance of SecretManager for this service."""

    settings = get_settings()

    return get_secret_manager_instance(

        app_name=settings.SERVICE_NAME,

        debug=settings.DEBUG_MODE

    )

