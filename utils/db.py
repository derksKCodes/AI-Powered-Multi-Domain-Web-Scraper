from sqlalchemy import create_engine, Column, String, Float, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import DB_CONFIG
import pandas as pd
from loguru import logger

Base = declarative_base()

class ScrapedData(Base):
    __tablename__ = 'scraped_data'
    
    id = Column(String, primary_key=True)
    domain = Column(String)
    data = Column(JSON)
    timestamp = Column(DateTime)
    source = Column(String)

class DatabaseManager:
    def __init__(self):
        self.engine = self._create_engine()
        self.Session = sessionmaker(bind=self.engine)
    
    def _create_engine(self):
        connection_string = (
            f"{DB_CONFIG['dialect']}+{DB_CONFIG['driver']}://"
            f"{DB_CONFIG['username']}:{DB_CONFIG['password']}@"
            f"{DB_CONFIG['host']}:{DB_CONFIG['port']}/"
            f"{DB_CONFIG['database']}"
        )
        return create_engine(connection_string)
    
    def save_data(self, domain: str, data: list, source: str):
        """Save scraped data to database"""
        try:
            session = self.Session()
            
            for item in data:
                record = ScrapedData(
                    id=f"{domain}_{hash(str(item))}",
                    domain=domain,
                    data=item,
                    timestamp=pd.Timestamp.now(),
                    source=source
                )
                session.merge(record)
            
            session.commit()
            logger.info(f"Saved {len(data)} records to database for domain: {domain}")
            
        except Exception as e:
            logger.error(f"Database save failed: {e}")
            session.rollback()
        finally:
            session.close()