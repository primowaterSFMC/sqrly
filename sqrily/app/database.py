from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
import structlog
from typing import Generator

from .config import settings

logger = structlog.get_logger()

# Database engine
engine = create_engine(
    settings.database_url,
    echo=settings.database_echo,
    future=True,
    pool_pre_ping=True,
    pool_recycle=300,
    poolclass=StaticPool if "sqlite" in settings.database_url else None,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {}
)

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    future=True
)

# Base class for models
Base = declarative_base()
metadata = MetaData()

def get_db() -> Generator[Session, None, None]:
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error("Database session error", error=str(e))
        db.rollback()
        raise
    finally:
        db.close()

class DatabaseMixin:
    """Mixin class to add common database methods"""
    
    @classmethod
    def create(cls, db: Session, **kwargs):
        """Create a new instance"""
        instance = cls(**kwargs)
        db.add(instance)
        db.commit()
        db.refresh(instance)
        return instance
    
    def update(self, db: Session, **kwargs):
        """Update instance"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        db.commit()
        db.refresh(self)
        return self
    
    def delete(self, db: Session):
        """Delete instance"""
        db.delete(self)
        db.commit()
        return True
    
    def soft_delete(self, db: Session):
        """Soft delete instance if deleted_at field exists"""
        if hasattr(self, 'deleted_at'):
            from datetime import datetime
            self.deleted_at = datetime.utcnow()
            db.commit()
            db.refresh(self)
            return self
        else:
            return self.delete(db)