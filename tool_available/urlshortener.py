import logging
import requests
import json
import os
from dotenv import load_dotenv

#=== Infos ==================================================================
# This tool uses TinyURL service to shorten url by using  API call
# --->  you need a tinyURL API TOKEN <-----
# then add an entry in .env (in "tool_enabled/" directory) like this : 
# TINYURL_API_TOKEN=your_tinyurl_api_token_here
#============================================================================

load_dotenv()
logger = logging.getLogger(__name__)


def register_tool(mcp):
    @mcp.tool()
    def urlshortener(url: str, full_name: str) -> str:
        """return a shortened url via TinyURL service

        Args:
            url: the url to be shortened
            full_name: User name for logging purposes (required)
        """
        logger.info(f"🔧 Tool called: urlshortener() by {full_name}")

        try:
            # Récupération du token depuis les variables d'environnement
            api_token = os.getenv("TINYURL_API_TOKEN")
            if not api_token:
                logger.error("❌ TINYURL_API_TOKEN not found in environment variables")
                return "Error: API token not configured"

            # Configuration de l'API TinyURL
            api_url = "https://api.tinyurl.com/create"
            headers = {
                "Authorization": f"Bearer {api_token}",
                "Content-Type": "application/json"
            }

            # Données à envoyer
            payload = {
                "url": url
            }

            # Appel à l'API
            response = requests.post(api_url, headers=headers, json=payload)

            # Vérification du statut de la réponse
            if response.status_code == 200:
                data = response.json()
                shortened_url = data.get("data", {}).get("tiny_url")
                logger.info(f"✅ URL shortened successfully: {url} -> {shortened_url}")
                return shortened_url
            else:
                error_msg = f"Error {response.status_code}: {response.text}"
                logger.error(f"❌ TinyURL API error: {error_msg}")
                return f"Error shortening URL: {error_msg}"

        except requests.RequestException as e:
            logger.error(f"❌ Network error: {str(e)}")
            return f"Network error occurred: {str(e)}"
        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON parsing error: {str(e)}")
            return f"Error parsing API response: {str(e)}"
        except Exception as e:
            logger.error(f"❌ Unexpected error: {str(e)}")
            return f"Unexpected error occurred: {str(e)}"
