try:
    from datetime import datetime
    from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey
    from sqlalchemy.orm import relationship
    from .database import Base

    class Commodity(Base):
        __tablename__ = "commodities"

        commodity_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
        name = Column(String(100), unique=True, nullable=False, index=True)
        name_hi = Column(String(100), nullable=True)

        price_records = relationship("PriceRecord", back_populates="commodity")
        forecast_records = relationship("ForecastRecord", back_populates="commodity")


    class Mandi(Base):
        __tablename__ = "mandis"

        mandi_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
        name = Column(String(150), unique=True, nullable=False, index=True)
        district = Column(String(100), nullable=False)
        state = Column(String(100), nullable=False)

        price_records = relationship("PriceRecord", back_populates="mandi")
        forecast_records = relationship("ForecastRecord", back_populates="mandi")


    class PriceRecord(Base):
        __tablename__ = "price_records"

        record_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
        commodity_id = Column(Integer, ForeignKey("commodities.commodity_id"), nullable=False)
        mandi_id = Column(Integer, ForeignKey("mandis.mandi_id"), nullable=False)
        price_date = Column(Date, nullable=False, index=True)
        min_price = Column(Float, nullable=True)
        max_price = Column(Float, nullable=True)
        modal_price = Column(Float, nullable=False)
        unit = Column(String(50), default="₹/Quintal")
        source = Column(String(100), default="Agmarknet")

        commodity = relationship("Commodity", back_populates="price_records")
        mandi = relationship("Mandi", back_populates="price_records")


    class QueryLog(Base):
        __tablename__ = "query_logs"

        query_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
        user_query = Column(String(500), nullable=False)
        detected_crop = Column(String(100), nullable=True)
        detected_mandi = Column(String(100), nullable=True)
        detected_intent = Column(String(50), nullable=True)
        status = Column(String(50), default="success")
        created_at = Column(DateTime, default=datetime.utcnow)


    class ForecastRecord(Base):
        __tablename__ = "forecast_records"

        forecast_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
        commodity_id = Column(Integer, ForeignKey("commodities.commodity_id"), nullable=False)
        mandi_id = Column(Integer, ForeignKey("mandis.mandi_id"), nullable=False)
        forecast_date = Column(Date, nullable=False)
        predicted_price = Column(Float, nullable=False)
        lower_bound = Column(Float, nullable=True)
        upper_bound = Column(Float, nullable=True)
        model_name = Column(String(100), default="ARIMA-Baseline")
        generated_at = Column(DateTime, default=datetime.utcnow)

        commodity = relationship("Commodity", back_populates="forecast_records")
        mandi = relationship("Mandi", back_populates="forecast_records")

except ImportError:
    Commodity = None
    Mandi = None
    PriceRecord = None
    QueryLog = None
    ForecastRecord = None
