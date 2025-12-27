import asyncio
import time
from typing import List, Optional

import httpx
from pydantic import parse_obj_as

from nvdi_cli.api.models import CVEModel
from nvdi_cli.cache.manager import cache_get, cache_set
from nvdi_cli.config.settings import Settings
from nvdi_cli.db import init_db, Database


class NVDClient:
    def __init__(self, api_key: Optional[str] = None, rate_limit: int = 5, use_db: bool = True):
        self.base_url = "https://services.nvd.nist.gov/rest/json"
        self.api_key = api_key or Settings().nvd_api_key
        self._client = httpx.AsyncClient(timeout=30)
        self._semaphore = asyncio.Semaphore(rate_limit)
        self.use_db = use_db
        self.db: Optional[Database] = None

    async def _get(self, path: str, params: dict = None) -> dict:
        url = f"{self.base_url}{path}"
        cache_key = f"nvd:{url}:{params}"
        cached = await cache_get(cache_key)
        if cached is not None:
            return cached

        async with self._semaphore:
            headers = {"User-Agent": "nvdi/0.1"}
            if self.api_key:
                headers["apiKey"] = self.api_key
            for attempt in range(3):
                try:
                    resp = await self._client.get(url, params=params or {}, headers=headers)
                    resp.raise_for_status()
                    data = resp.json()
                    await cache_set(cache_key, data, ttl=Settings().cache_ttl)
                    return data
                except httpx.HTTPStatusError as e:
                    if resp.status_code in (429, 502, 503, 504) and attempt < 2:
                        await asyncio.sleep(2 ** attempt)
                        continue
                    raise

    async def get_cve(self, cve_id: str) -> Optional[CVEModel]:
        # Check DB first if enabled
        if self.use_db:
            if not self.db:
                self.db = await init_db()
            cached = await self.db.get_cve(cve_id)
            if cached:
                return cached
        
        # Fetch from API - NVD API 2.0
        path = f"/cves/2.0"
        params = {"cveId": cve_id}
        try:
            data = await self._get(path, params=params)
            vulns = data.get("vulnerabilities", [])
            if not vulns:
                return None
            
            cve_data = vulns[0].get("cve", {})
            cve_id = cve_data.get("id")
            source_id = cve_data.get("sourceIdentifier")
            vuln_status = cve_data.get("vulnStatus")
            
            # Extract description
            descs = cve_data.get("descriptions", [])
            desc = next((d["value"] for d in descs if d.get("lang") == "en"), None)
            
            published = cve_data.get("published")
            modified = cve_data.get("lastModified")
            
            # Extract CVSS v3
            cvssv3 = None
            cvssv2 = None
            metrics = cve_data.get("metrics", {})
            cvssv3_list = metrics.get("cvssMetricV31") or metrics.get("cvssMetricV30", [])
            if cvssv3_list:
                cvss_data = cvssv3_list[0].get("cvssData", {})
                cvssv3 = {
                    "baseScore": cvss_data.get("baseScore"),
                    "baseSeverity": cvss_data.get("baseSeverity"),
                    "vectorString": cvss_data.get("vectorString"),
                    "exploitabilityScore": cvssv3_list[0].get("exploitabilityScore"),
                    "impactScore": cvssv3_list[0].get("impactScore"),
                }
            
            # Extract CVSS v2
            cvssv2_list = metrics.get("cvssMetricV2", [])
            if cvssv2_list:
                cvss_data = cvssv2_list[0].get("cvssData", {})
                cvssv2 = {
                    "baseScore": cvss_data.get("baseScore"),
                    "vectorString": cvss_data.get("vectorString"),
                    "severity": cvssv2_list[0].get("baseSeverity"),
                }
            
            # Extract references
            refs = []
            for ref in cve_data.get("references", []):
                refs.append({
                    "url": ref.get("url"),
                    "source": ref.get("source"),
                    "tags": ref.get("tags", [])
                })
            
            # Extract weaknesses
            weaknesses = []
            for weak in cve_data.get("weaknesses", []):
                desc_list = [d.get("value") for d in weak.get("description", [])]
                weaknesses.append({
                    "source": weak.get("source"),
                    "type": weak.get("type"),
                    "description": desc_list
                })
            
            # Extract CPE configurations
            configs = []
            for config in cve_data.get("configurations", []):
                for node in config.get("nodes", []):
                    for cpe in node.get("cpeMatch", []):
                        configs.append({
                            "criteria": cpe.get("criteria"),
                            "matchCriteriaId": cpe.get("matchCriteriaId"),
                            "vulnerable": cpe.get("vulnerable")
                        })
            
            model = CVEModel(
                id=cve_id,
                sourceIdentifier=source_id,
                description=desc,
                publishedDate=published,
                lastModifiedDate=modified,
                vulnStatus=vuln_status,
                cvssv3=cvssv3,
                cvssv2=cvssv2,
                references=refs,
                weaknesses=weaknesses,
                configurations=configs,
                raw_data=cve_data
            )
            
            # Save to DB
            if self.use_db and self.db:
                await self.db.save_cve(model)
            
            return model
        except Exception as e:
            return None
    
    async def close(self):
        """Close client and database connections"""
        await self._client.aclose()
        if self.db:
            await self.db.close()

    async def search_cves(self, keyword: Optional[str] = None, resultsPerPage: int = 20, 
                         min_score: Optional[float] = None) -> List[CVEModel]:
        # Try DB first for offline search
        if self.use_db and keyword:
            if not self.db:
                self.db = await init_db()
            db_results = await self.db.search_cves(keyword=keyword, min_score=min_score, limit=resultsPerPage)
            if db_results:
                return db_results
        
        # Fetch from API - NVD API 2.0
        params = {"resultsPerPage": resultsPerPage}
        if keyword:
            params["keywordSearch"] = keyword
        if min_score:
            params["cvssV3Severity"] = "HIGH" if min_score >= 7.0 else "MEDIUM"
        
        try:
            data = await self._get("/cves/2.0", params=params)
            vulns = data.get("vulnerabilities", [])
            results = []
            
            for vuln in vulns:
                try:
                    cve_data = vuln.get("cve", {})
                    cve_id = cve_data.get("id")
                    source_id = cve_data.get("sourceIdentifier")
                    vuln_status = cve_data.get("vulnStatus")
                    
                    descs = cve_data.get("descriptions", [])
                    desc = next((d["value"] for d in descs if d.get("lang") == "en"), None)
                    
                    published = cve_data.get("published")
                    modified = cve_data.get("lastModified")
                    
                    cvssv3 = None
                    cvssv2 = None
                    metrics = cve_data.get("metrics", {})
                    cvssv3_list = metrics.get("cvssMetricV31") or metrics.get("cvssMetricV30", [])
                    if cvssv3_list:
                        cvss_data = cvssv3_list[0].get("cvssData", {})
                        cvssv3 = {
                            "baseScore": cvss_data.get("baseScore"),
                            "baseSeverity": cvss_data.get("baseSeverity"),
                            "vectorString": cvss_data.get("vectorString"),
                            "exploitabilityScore": cvssv3_list[0].get("exploitabilityScore"),
                            "impactScore": cvssv3_list[0].get("impactScore"),
                        }
                    
                    cvssv2_list = metrics.get("cvssMetricV2", [])
                    if cvssv2_list:
                        cvss_data = cvssv2_list[0].get("cvssData", {})
                        cvssv2 = {
                            "baseScore": cvss_data.get("baseScore"),
                            "vectorString": cvss_data.get("vectorString"),
                            "severity": cvssv2_list[0].get("baseSeverity"),
                        }
                    
                    model = CVEModel(
                        id=cve_id,
                        sourceIdentifier=source_id,
                        description=desc,
                        publishedDate=published,
                        lastModifiedDate=modified,
                        vulnStatus=vuln_status,
                        cvssv3=cvssv3,
                        cvssv2=cvssv2,
                        raw_data=cve_data
                    )
                    results.append(model)
                    
                    # Save to DB
                    if self.use_db and self.db:
                        await self.db.save_cve(model)
                        
                except Exception:
                    continue
            
            return results
        except Exception as e:
            return []
