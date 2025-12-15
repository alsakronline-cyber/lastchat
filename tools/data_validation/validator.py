import logging
from typing import Dict, List, Optional
import re

logger = logging.getLogger("DataValidator")

class DataValidator:
    """
    Validates product data before ingestion.
    Checks for required fields, data types, and logical consistency.
    """
    
    REQUIRED_FIELDS = ["sku_id", "product_name", "source"]
    
    def __init__(self):
        pass

    def validate_product(self, product: Dict) -> Dict:
        """
        Validate a single product record.
        Returns a dictionary with 'is_valid', 'errors', and 'score'.
        """
        errors = []
        score = 1.0
        
        # 1. Check Required Fields
        for field in self.REQUIRED_FIELDS:
            if not product.get(field) or str(product.get(field)).strip() == "":
                errors.append(f"Missing required field: {field}")
                score -= 0.3

        # 2. SKU Validation
        sku = product.get("sku_id", "")
        if len(sku) < 3:
            errors.append("SKU too short")
            score -= 0.1
        
        # 3. Image Validation
        images = product.get("images", [])
        if not images:
            logger.warning(f"Product {sku} has no images")
            score -= 0.1
        
        # 4. Specifications Check
        specs = product.get("specifications", {})
        if not specs or len(specs) < 2:
            logger.warning(f"Product {sku} has sparse specifications")
            score -= 0.1

        # 5. Datasheet Check
        if not product.get("datasheet_url"):
            logger.warning(f"Product {sku} missing datasheet")
            score -= 0.1

        # Calculate final confidence score
        score = max(0.0, score)
        
        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "confidence_score": round(score, 2)
        }

    def validate_batch(self, products: List[Dict]) -> List[Dict]:
        """Validate a list of products and append validation metadata"""
        validated_products = []
        for p in products:
            res = self.validate_product(p)
            p['validation_errors'] = res['errors']
            p['confidence_score'] = p.get('confidence_score', res['confidence_score']) # Keep existing score if present
            
            if res['is_valid']:
                validated_products.append(p)
            else:
                logger.error(f"Dropping invalid product {p.get('sku_id')}: {res['errors']}")
        
        return validated_products
