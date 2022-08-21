from typing import Dict, Any, Optional


def omit_empty_dict_attributes(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Remove empty dict attributes from a dict
    """
    return {key: value for key, value in data.items() if value is not None and value != {}}


def ensure_json_content_type_header(headers: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """
    Add the content type header for JSON requests, but only if not already present
    """
    if headers is not None and ("Content-Type" not in headers or "content-type" not in headers):
        headers["Content-Type"] = "application/json; charset=utf-8"
    return headers