import jwt
import time
from typing import Dict, Optional
from loguru import logger


class JWTValidator:
    @staticmethod
    def verify_steam_jwt(refresh_token: str) -> int:
        """
        Verify Steam JWT token validity and expiration.
        Returns: -1 if invalid/expired, otherwise seconds until expiration
        """
        try:
            decoded_jwt = jwt.decode(refresh_token, options={"verify_signature": False})

            if decoded_jwt.get("iss") != "steam" or "client" not in decoded_jwt.get(
                "aud", []
            ):
                return -1

            expires_in = decoded_jwt.get("exp", 0) - time.time()
            if expires_in <= 0:
                logger.info("Token has expired")
                return -1

            logger.info(f"Token expires in {expires_in} seconds")
            return expires_in

        except Exception as e:
            logger.error(f"Error verifying token: {e}")
            return -1

    @staticmethod
    def parse_eya(eya: str) -> Optional[Dict]:
        """Parse and decode the EYA token payload"""
        try:
            token_parts = eya.split(".")
            if len(token_parts) != 3:
                return None

            # Add padding if needed
            payload = token_parts[1]
            padding = len(payload) % 4
            if padding:
                payload += "=" * (4 - padding)

            return jwt.decode(eya, options={"verify_signature": False})

        except Exception as e:
            logger.error(f"Error parsing EYA token: {e}")
            return None
