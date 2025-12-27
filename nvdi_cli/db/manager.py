import aiosqlite
import json
from typing import List, Optional
from datetime import datetime
from nvdi_cli.api.models import CVEModel


class Database:
    def __init__(self, db_path: str = ".nvdi-data/nvdi.db"):
        self.db_path = db_path
        
    async def connect(self):
        """Create connection and ensure tables exist"""
        import os
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.conn = await aiosqlite.connect(self.db_path)
        await self._create_tables()
        
    async def _create_tables(self):
        """Create schema for CVEs, products, and monitoring"""
        await self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS cves (
                id TEXT PRIMARY KEY,
                description TEXT,
                published_date TEXT,
                modified_date TEXT,
                cvss_score REAL,
                cvss_vector TEXT,
                raw_data TEXT,
                fetched_at TEXT
            );
            
            CREATE TABLE IF NOT EXISTS monitored_products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_name TEXT UNIQUE,
                last_checked TEXT,
                created_at TEXT
            );
            
            CREATE TABLE IF NOT EXISTS product_cves (
                product_id INTEGER,
                cve_id TEXT,
                discovered_at TEXT,
                FOREIGN KEY (product_id) REFERENCES monitored_products(id),
                FOREIGN KEY (cve_id) REFERENCES cves(id),
                UNIQUE(product_id, cve_id)
            );
            
            CREATE INDEX IF NOT EXISTS idx_cve_published ON cves(published_date);
            CREATE INDEX IF NOT EXISTS idx_cve_score ON cves(cvss_score);
        """)
        await self.conn.commit()
    
    async def save_cve(self, cve: CVEModel) -> None:
        """Save or update a CVE in the database"""
        cvss_score = None
        cvss_vector = None
        if cve.cvssv3:
            if hasattr(cve.cvssv3, 'baseScore'):
                cvss_score = cve.cvssv3.baseScore
                cvss_vector = cve.cvssv3.vectorString
            else:
                cvss_score = cve.cvssv3.get('baseScore') if isinstance(cve.cvssv3, dict) else None
                cvss_vector = cve.cvssv3.get('vectorString') if isinstance(cve.cvssv3, dict) else None
        
        await self.conn.execute("""
            INSERT OR REPLACE INTO cves 
            (id, description, published_date, modified_date, cvss_score, cvss_vector, raw_data, fetched_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            cve.id,
            cve.description,
            cve.publishedDate,
            cve.lastModifiedDate,
            cvss_score,
            cvss_vector,
            json.dumps(cve.dict()),
            datetime.utcnow().isoformat()
        ))
        await self.conn.commit()
    
    async def get_cve(self, cve_id: str) -> Optional[CVEModel]:
        """Retrieve a CVE from local database"""
        async with self.conn.execute(
            "SELECT raw_data FROM cves WHERE id = ?", (cve_id,)
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                return CVEModel(**json.loads(row[0]))
            return None
    
    async def search_cves(self, keyword: Optional[str] = None, 
                         min_score: Optional[float] = None,
                         limit: int = 20) -> List[CVEModel]:
        """Search CVEs in local database"""
        query = "SELECT raw_data FROM cves WHERE 1=1"
        params = []
        
        if keyword:
            query += " AND (description LIKE ? OR id LIKE ?)"
            params.extend([f"%{keyword}%", f"%{keyword}%"])
        
        if min_score is not None:
            query += " AND cvss_score >= ?"
            params.append(min_score)
        
        query += " ORDER BY published_date DESC LIMIT ?"
        params.append(limit)
        
        async with self.conn.execute(query, params) as cursor:
            rows = await cursor.fetchall()
            return [CVEModel(**json.loads(row[0])) for row in rows]
    
    async def add_monitored_product(self, product_name: str) -> None:
        """Add a product to monitoring list"""
        await self.conn.execute("""
            INSERT OR IGNORE INTO monitored_products (product_name, created_at)
            VALUES (?, ?)
        """, (product_name, datetime.utcnow().isoformat()))
        await self.conn.commit()
    
    async def get_monitored_products(self) -> List[str]:
        """Get all monitored products"""
        async with self.conn.execute(
            "SELECT product_name FROM monitored_products"
        ) as cursor:
            rows = await cursor.fetchall()
            return [row[0] for row in rows]
    
    async def link_product_cve(self, product_name: str, cve_id: str) -> None:
        """Link a CVE to a monitored product"""
        await self.conn.execute("""
            INSERT OR IGNORE INTO product_cves (product_id, cve_id, discovered_at)
            SELECT id, ?, ? FROM monitored_products WHERE product_name = ?
        """, (cve_id, datetime.utcnow().isoformat(), product_name))
        await self.conn.commit()
    
    async def get_stats(self, year: Optional[int] = None) -> dict:
        """Get CVE statistics from local database"""
        query = "SELECT COUNT(*), AVG(cvss_score), MAX(cvss_score) FROM cves"
        params = []
        
        if year:
            query += " WHERE published_date LIKE ?"
            params.append(f"{year}%")
        
        async with self.conn.execute(query, params) as cursor:
            row = await cursor.fetchone()
            return {
                "total_cves": row[0],
                "avg_score": round(row[1], 2) if row[1] else 0,
                "max_score": row[2] if row[2] else 0
            }
    
    async def reset(self) -> None:
        """Reset/clear all data from database"""
        await self.conn.executescript("""
            DELETE FROM product_cves;
            DELETE FROM monitored_products;
            DELETE FROM cves;
        """)
        await self.conn.commit()
    
    async def close(self):
        """Close database connection"""
        await self.conn.close()


async def init_db(db_path: str = ".nvdi-data/nvdi.db") -> Database:
    """Initialize and return database instance"""
    db = Database(db_path)
    await db.connect()
    return db
