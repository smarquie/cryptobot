# utils/wallet.py

import eth_account
from eth_account.signers.local import LocalAccount
from typing import Optional
import logging

logger = logging.getLogger(__name__)

def validate_private_key(private_key: str) -> Optional[LocalAccount]:
    """
    Validate Ethereum-style private key (64 hex chars without 0x prefix)
    
    Returns:
        LocalAccount if valid
        None if invalid or missing
    """
    if not private_key or len(private_key.strip()) == 0:
        logger.warning("⚠️ No private key provided – read-only mode")
        return None

    try:
        cleaned_key = private_key.strip().replace('0x', '')
        if len(cleaned_key) != 64:
            raise ValueError(f"Private key must be 64 hex characters (got {len(cleaned_key)})")

        wallet = eth_account.Account.from_key(cleaned_key)
        logger.info(f"✅ Valid private key loaded for {wallet.address}")
        return wallet
    except Exception as e:
        logger.error(f"❌ Invalid private key: {e}")
        return None
