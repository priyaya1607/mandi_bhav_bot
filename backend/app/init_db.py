"""
Script to create PostgreSQL tables and seed initial commodities, mandis, and price records.
Usage:
    python -m backend.app.init_db
"""
import sys
import logging
from .database import engine, Base, SessionLocal
from .models import Commodity, Mandi, PriceRecord
from ..data.seed_records import COMMODITIES_SEED, MANDIS_SEED, generate_sample_price_records

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("init_db")

def init_postgresql():
    if engine is None:
        logger.error("PostgreSQL engine is not initialized. Please verify DATABASE_URL in .env")
        return False

    try:
        logger.info("Connecting to PostgreSQL and creating tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("Tables created successfully.")
    except Exception as e:
        logger.error(f"Failed to create tables in PostgreSQL: {e}")
        return False

    db = SessionLocal()
    try:
        # 1. Seed Commodities
        commodity_map = {}
        for c_data in COMMODITIES_SEED:
            existing = db.query(Commodity).filter(Commodity.name == c_data["name"]).first()
            if not existing:
                comm = Commodity(name=c_data["name"], name_hi=c_data["name_hi"])
                db.add(comm)
                db.flush()
                commodity_map[c_data["name"]] = comm.commodity_id
                logger.info(f"Added commodity: {c_data['name']}")
            else:
                commodity_map[c_data["name"]] = existing.commodity_id

        # 2. Seed Mandis
        mandi_map = {}
        for m_data in MANDIS_SEED:
            existing = db.query(Mandi).filter(Mandi.name == m_data["name"]).first()
            if not existing:
                mandi = Mandi(name=m_data["name"], district=m_data["district"], state=m_data["state"])
                db.add(mandi)
                db.flush()
                mandi_map[m_data["name"]] = mandi.mandi_id
                logger.info(f"Added mandi: {m_data['name']}")
            else:
                mandi_map[m_data["name"]] = existing.mandi_id

        # 3. Seed Price Records
        records = generate_sample_price_records()
        seeded_count = 0
        for r in records:
            c_id = commodity_map.get(r["commodity"])
            m_id = mandi_map.get(r["mandi"])
            if not c_id or not m_id:
                continue

            existing_record = (
                db.query(PriceRecord)
                .filter(
                    PriceRecord.commodity_id == c_id,
                    PriceRecord.mandi_id == m_id,
                    PriceRecord.price_date == r["price_date"]
                )
                .first()
            )
            if not existing_record:
                rec = PriceRecord(
                    commodity_id=c_id,
                    mandi_id=m_id,
                    price_date=r["price_date"],
                    min_price=r["min_price"],
                    max_price=r["max_price"],
                    modal_price=r["modal_price"],
                    unit=r["unit"],
                    source=r["source"]
                )
                db.add(rec)
                seeded_count += 1

        db.commit()
        logger.info(f"Seeding completed! Inserted {seeded_count} price records into PostgreSQL.")
        return True
    except Exception as e:
        db.rollback()
        logger.error(f"Error seeding PostgreSQL data: {e}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    success = init_postgresql()
    sys.exit(0 if success else 1)
