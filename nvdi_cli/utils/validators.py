def is_cve_id(v: str) -> bool:
    return v.upper().startswith("CVE-")
