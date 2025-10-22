"""
Database connection module for Neon PostgreSQL
Provides SQLAlchemy engine and session management
"""

import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool
import logging

logger = logging.getLogger(__name__)

# Get database URL from environment
DATABASE_URL = os.getenv('NEON_DATABASE_URL')

if not DATABASE_URL:
    logger.warning("NEON_DATABASE_URL not set. Database features will be disabled.")
    engine = None
    SessionLocal = None
else:
    # Create engine with connection pooling disabled for serverless
    engine = create_engine(
        DATABASE_URL,
        poolclass=NullPool,  # No connection pooling for serverless
        echo=False,  # Set to True for SQL query logging
    )

    # Create session factory
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    logger.info("✅ Database engine created successfully")


def get_db() -> Session:
    """
    Get a database session

    Usage:
        with get_db() as db:
            result = db.execute(text("SELECT * FROM installations"))
    """
    if SessionLocal is None:
        raise RuntimeError("Database not configured. Set NEON_DATABASE_URL environment variable.")

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_connection():
    """Test database connection"""
    if engine is None:
        return False, "Database not configured"

    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            result.fetchone()
        return True, "Database connection successful"
    except Exception as e:
        return False, f"Database connection failed: {str(e)}"


def save_installation(drop_number: str, contractor_name: str, project_name: str = "Velo Test"):
    """
    Save a new installation to the database

    Args:
        drop_number: Drop number (e.g., DR12345678)
        contractor_name: WhatsApp number or contractor identifier
        project_name: Project name (default: "Velo Test")

    Returns:
        dict: Result with success status and installation data
    """
    if engine is None:
        return {"success": False, "error": "Database not configured"}

    try:
        with engine.connect() as conn:
            # Check if installation already exists
            existing = conn.execute(
                text("SELECT id FROM installations WHERE drop_number = :drop_number"),
                {"drop_number": drop_number}
            ).fetchone()

            if existing:
                logger.info(f"Installation {drop_number} already exists")
                return {
                    "success": True,
                    "action": "exists",
                    "drop_number": drop_number,
                    "message": "Installation already exists"
                }

            # Insert new installation
            conn.execute(
                text("""
                    INSERT INTO installations (drop_number, contractor_name, project_name, status, date_submitted)
                    VALUES (:drop_number, :contractor_name, :project_name, 'submitted', NOW())
                """),
                {
                    "drop_number": drop_number,
                    "contractor_name": contractor_name,
                    "project_name": project_name
                }
            )
            conn.commit()

            logger.info(f"✅ Saved installation {drop_number} to database")

            # Create QA photo review record with all 12 steps = false
            conn.execute(
                text("""
                    INSERT INTO qa_photo_reviews (
                        drop_number, review_date, user_name, project,
                        step_01_house_photo, step_02_cable_from_pole, step_03_cable_entry_outside,
                        step_04_cable_entry_inside, step_05_wall_for_installation, step_06_ont_back_after_install,
                        step_07_power_meter_reading, step_08_ont_barcode, step_09_ups_serial,
                        step_10_final_installation, step_11_green_lights, step_12_customer_signature,
                        completed, incomplete
                    ) VALUES (
                        :drop_number, CURRENT_DATE, 'QA Team', :project_name,
                        false, false, false, false, false, false,
                        false, false, false, false, false, false,
                        false, false
                    )
                    ON CONFLICT (drop_number, review_date) DO NOTHING
                """),
                {
                    "drop_number": drop_number,
                    "project_name": project_name
                }
            )
            conn.commit()

            logger.info(f"✅ Created QA review record for {drop_number}")

            return {
                "success": True,
                "action": "created",
                "drop_number": drop_number,
                "message": "Installation saved and ready for QA review"
            }

    except Exception as e:
        logger.error(f"❌ Failed to save installation {drop_number}: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "drop_number": drop_number
        }


def mark_resubmitted(drop_number: str):
    """
    Mark a drop as resubmitted (agent sent "DONE" message)

    Args:
        drop_number: Drop number (e.g., DR12345678)

    Returns:
        dict: Result with success status
    """
    if engine is None:
        return {"success": False, "error": "Database not configured"}

    try:
        with engine.connect() as conn:
            # Update QA review to clear incomplete flag and feedback_sent
            result = conn.execute(
                text("""
                    UPDATE qa_photo_reviews
                    SET incomplete = false,
                        feedback_sent = NULL,
                        updated_at = NOW()
                    WHERE drop_number = :drop_number
                """),
                {"drop_number": drop_number}
            )
            conn.commit()

            if result.rowcount > 0:
                logger.info(f"✅ Marked {drop_number} as resubmitted")
                return {
                    "success": True,
                    "drop_number": drop_number,
                    "message": "Drop marked as resubmitted for re-review"
                }
            else:
                logger.warning(f"⚠️ Drop {drop_number} not found in database")
                return {
                    "success": False,
                    "error": "Drop not found",
                    "drop_number": drop_number
                }

    except Exception as e:
        logger.error(f"❌ Failed to mark {drop_number} as resubmitted: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "drop_number": drop_number
        }
