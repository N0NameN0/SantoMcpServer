import logging
import subprocess
import re
import ipaddress
import socket
from typing import Optional


logger = logging.getLogger(__name__)

def register_tool(mcp):
    @mcp.tool()
    def nmap_scan(
        ip: str,
        full_name: str,
        port: Optional[str] = None,
        scan_type: Optional[str] = None,        # e.g. "-sS", "-sU"
        os_detection: Optional[bool] = False,   # True pour ajouter "-O"
        service_version: Optional[bool] = False, # True pour ajouter "-sV"
        extra_args: Optional[str] = None        # Autres arguments nmap libres
    ) -> str:
        """
        Effectue un scan nmap sur une IP ou un hostname avec des options avancées.

        Args:
            ip: IP ou hostname à scanner (ex: "192.168.1.1" ou "google.com")
            full_name: Nom complet pour le logging (obligatoire)
            port: Spécification optionnelle des ports ("80", "80,443", "1-1000")
            scan_type: Type de scan (ex: "-sS" pour SYN, "-sU" pour UDP)
            os_detection: Active la détection d'OS ("-O")
            service_version: Active la détection de version de service ("-sV")
            extra_args: Autres arguments nmap (string, split sur espaces)

        Returns:
            Résultat du scan nmap (stdout ou message d'erreur)
        """

        logger.info(
            f"🔧 Tool called: nmap_scan(ip='{ip}', port='{port}', scan_type='{scan_type}', "
            f"os_detection={os_detection}, service_version={service_version}, extra_args={extra_args}) by {full_name}"
        )

        try:
            cleaned_ip = ip.strip()

            # Refuser ranges, CIDR, wildcards, ou multiples IPs
            invalid_patterns = [
                r'\d+\.\d+\.\d+\.\d+/\d+',  # CIDR
                r'\d+\.\d+\.\d+\.\d+-\d+',  # Range
                r'\d+\.\d+\.\d+\.\*',       # Wildcard
                r',',                       # Virgule = multiple
                r'\s+',                     # Espace = multiple
            ]
            for pattern in invalid_patterns:
                if re.search(pattern, cleaned_ip):
                    return "Error: Only single IP addresses or hostnames are allowed. No ranges, CIDR, or multiple IPs."

            # Validation IP/hostname
            try:
                ipaddress.ip_address(cleaned_ip)
                target = cleaned_ip
            except ValueError:
                if re.search(r'\s', cleaned_ip):
                    return "Error: Invalid hostname (contains whitespace)."
                try:
                    socket.gethostbyname(cleaned_ip)
                except socket.gaierror:
                    return f"Error: Cannot resolve hostname '{cleaned_ip}'"
                target = cleaned_ip

            # Construction de la commande nmap
            nmap_cmd = ["nmap"]
            if scan_type:
                nmap_cmd.append(scan_type)
            if os_detection:
                nmap_cmd.append("-O")
            if service_version:
                nmap_cmd.append("-sV")
            if port:
                port = port.strip()
                if not re.match(r'^[\d,-]+$', port):
                    return "Error: Invalid port format. Use single port (80), multiple ports (80,443), or range (1-1000)."
                nmap_cmd.extend(["-p", port])
            if extra_args:
                try:
                    nmap_cmd.extend(extra_args.split())
                except Exception:
                    return "Error: Failed to parse extra_args."
            nmap_cmd.extend(["-T4", "--open", target])  # timing rapide, que ports ouverts

            logger.info(f"Executing nmap command: {' '.join(nmap_cmd)}")

            result = subprocess.run(
                nmap_cmd,
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.returncode == 0:
                output = result.stdout.strip()
                if not output:
                    return "Nmap completed but returned no output."
                logger.info(f"Nmap scan completed successfully for {target}")
                return f"Nmap scan results for {target}:\n\n{output}"
            else:
                error_msg = result.stderr.strip() or "Unknown error"
                logger.error(f"Nmap scan failed: {error_msg}")
                return f"Nmap scan failed: {error_msg}"

        except subprocess.TimeoutExpired:
            logger.error("Nmap scan timed out")
            return "Error: Nmap scan timed out after 60 seconds."
        except FileNotFoundError:
            logger.error("Nmap not found on system")
            return "Error: nmap is not installed or not found in PATH."
        except Exception as e:
            logger.error(f"Unexpected error in nmap_scan: {e}")
            return f"Error: {e}"


