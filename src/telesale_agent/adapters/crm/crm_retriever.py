import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional

from telesale_agent.core.models import TurnContext
from telesale_agent.core.interfaces import CRMRetriever

logger = logging.getLogger(__name__)

class FileCRMRetriever(CRMRetriever):
    """
    CRM Retriever that fetches customer profile from a JSON file.
    Designed for the BTC seed dataset in the AI Challenge.
    """
    
    def __init__(self, crm_file_path: str | Path | None = None):
        """
        Initializes the retriever with priority path resolution:
        1. Explicitly provided crm_file_path argument.
        2. CRM_SEED_PATH environment variable (useful on Render/Cloud).
        3. Default path relative to project root.
        """
        import os
        
        default_path = "dataset/BTC-Data-Vong1-TEAMS/catalog/crm_seed.json"
        env_path = os.getenv("CRM_SEED_PATH")
        
        # Resolve raw path
        raw_path = crm_file_path or env_path or default_path
        self.crm_file_path = Path(raw_path)
        
        # Resolve absolute path relative to project root if it's relative
        if not self.crm_file_path.is_absolute():
            # Path calculation: file_crm.py -> crm -> adapters -> telesale_agent -> src -> project root
            project_root = Path(__file__).resolve().parents[4]
            self.crm_file_path = project_root / self.crm_file_path
            
        self._cache: Optional[Dict[str, Any]] = None

    def _load_data(self) -> Dict[str, Any]:
        """Loads and caches data from the CRM seed file robustly."""
        if self._cache is not None:
            return self._cache
            
        if not self.crm_file_path.exists():
            logger.warning(f"CRM file not found at {self.crm_file_path}. Defaulting to empty DB.")
            self._cache = {"customers": []}
            return self._cache
            
        try:
            with open(self.crm_file_path, 'r', encoding='utf-8') as f:
                self._cache = json.load(f)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse CRM file {self.crm_file_path}: {e}")
            self._cache = {"customers": []}
            
        return self._cache

    def _find_customer_by_phone(self, phone: str) -> Optional[Dict[str, Any]]:
        """Helper to find a customer record by phone number."""
        data = self._load_data()
        for customer in data.get("customers", []):
            if customer.get("phone") == phone:
                return customer
        return None

    async def retrieve_profile(self, ctx: TurnContext) -> Dict[str, Any]:
        """Fetch customer profile based on identity (phone number)."""
        if not ctx.identity or not ctx.identity.customer_id:
            logger.debug("No customer_id found in context. Returning empty profile.")
            return {}
            
        phone = ctx.identity.customer_id
        customer = self._find_customer_by_phone(phone)
        
        if customer:
            return customer
            
        # Return fallback profile for unknown customers
        return {"phone": phone, "is_new_customer": True}
        
    async def precompute_brief(self, ctx: TurnContext) -> Dict[str, Any]:
        """Fetch past conversation history and orders if available."""
        if not ctx.identity or not ctx.identity.customer_id:
            return {"past_orders": [], "sessions": []}
            
        phone = ctx.identity.customer_id
        customer = self._find_customer_by_phone(phone)
        
        if customer:
            return {
                "past_orders": customer.get("orders", []),
                "sessions": customer.get("sessions", [])
            }
                
        return {"past_orders": [], "sessions": []}
