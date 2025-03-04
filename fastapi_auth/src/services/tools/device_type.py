from core.logger import log
from user_agents import parse


def get_device_type(user_agent_header: str) -> str:
    """Parse user agent for user's device type."""

    user_agent = parse(user_agent_header)
    log.info(f"\n{__file__}: user_agent: \n{user_agent}\n")

    device_type = "other"
    if user_agent.is_mobile:
        device_type = "mobile"
    elif user_agent.is_pc:
        device_type = "desktop"
    return device_type
