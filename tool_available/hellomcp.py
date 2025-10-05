import logging

logger = logging.getLogger(__name__)

def register_tool(mcp):
    @mcp.tool()
    def hellomcp(full_name: str) -> str:
        """return a little hello string

        Args:
            full_name: User name for testing purposes (required)
        """
        logger.info(f"🔧 Tool called: hellomcp() by {full_name}")
        return f"Hello {full_name} !!"


