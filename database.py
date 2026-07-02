import os
import json
import datetime
from contextlib import contextmanager
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, DateTime, Text
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from dotenv import load_dotenv  # type: ignore

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///vbcua.db")

Base = declarative_base()

class User(Base):
    __tablename__ = 'USER'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")
    audio_files = relationship("AudioFile", back_populates="user", cascade="all, delete-orphan")

class Session(Base):
    __tablename__ = 'SESSION'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('USER.id'), nullable=False)
    session_token = Column(String, unique=True, nullable=False)
    login_time = Column(DateTime, default=datetime.datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="sessions")

class AudioFile(Base):
    __tablename__ = 'AUDIO_FILE'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('USER.id'), nullable=False)
    filename = Column(String, nullable=False)
    filepath = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    duration_sec = Column(Float, nullable=False)
    upload_time = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="audio_files")
    transcripts = relationship("Transcript", back_populates="audio_file", cascade="all, delete-orphan")
    audio_features = relationship("AudioFeature", back_populates="audio_file", cascade="all, delete-orphan")
    evaluation_results = relationship("EvaluationResult", back_populates="audio_file", cascade="all, delete-orphan")

class ReferenceConcept(Base):
    __tablename__ = 'REFERENCE_CONCEPT'
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    concept_text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    semantic_similarities = relationship("SemanticSimilarity", back_populates="reference_concept", cascade="all, delete-orphan")
    evaluation_results = relationship("EvaluationResult", back_populates="reference_concept", cascade="all, delete-orphan")

class Transcript(Base):
    __tablename__ = 'TRANSCRIPT'
    id = Column(Integer, primary_key=True, autoincrement=True)
    audio_file_id = Column(Integer, ForeignKey('AUDIO_FILE.id'), nullable=False)
    transcript_text = Column(Text, nullable=False)
    word_count = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    audio_file = relationship("AudioFile", back_populates="transcripts")
    filler_word_stats = relationship("FillerWordStats", back_populates="transcript", uselist=False, cascade="all, delete-orphan")
    semantic_similarities = relationship("SemanticSimilarity", back_populates="transcript", cascade="all, delete-orphan")

class FillerWordStats(Base):
    __tablename__ = 'FILLER_WORD_STATS'
    id = Column(Integer, primary_key=True, autoincrement=True)
    transcript_id = Column(Integer, ForeignKey('TRANSCRIPT.id'), nullable=False)
    filler_word_count = Column(Integer, nullable=False)
    filler_ratio = Column(Float, nullable=False)
    filler_details = Column(Text, nullable=False)  # JSON-serialized string

    transcript = relationship("Transcript", back_populates="filler_word_stats")

class SemanticSimilarity(Base):
    __tablename__ = 'SEMANTIC_SIMILARITY'
    id = Column(Integer, primary_key=True, autoincrement=True)
    transcript_id = Column(Integer, ForeignKey('TRANSCRIPT.id'), nullable=False)
    reference_concept_id = Column(Integer, ForeignKey('REFERENCE_CONCEPT.id'), nullable=False)
    similarity_score = Column(Float, nullable=False)

    transcript = relationship("Transcript", back_populates="semantic_similarities")
    reference_concept = relationship("ReferenceConcept", back_populates="semantic_similarities")

class AudioFeature(Base):
    __tablename__ = 'AUDIO_FEATURE'
    id = Column(Integer, primary_key=True, autoincrement=True)
    audio_file_id = Column(Integer, ForeignKey('AUDIO_FILE.id'), nullable=False)
    pause_ratio = Column(Float, nullable=False)
    rms_energy = Column(Float, nullable=False)
    duration_sec = Column(Float, nullable=False)

    audio_file = relationship("AudioFile", back_populates="audio_features")

class EvaluationResult(Base):
    __tablename__ = 'EVALUATION_RESULT'
    id = Column(Integer, primary_key=True, autoincrement=True)
    audio_file_id = Column(Integer, ForeignKey('AUDIO_FILE.id'), nullable=False)
    reference_concept_id = Column(Integer, ForeignKey('REFERENCE_CONCEPT.id'), nullable=False)
    semantic_similarity_score = Column(Float, nullable=False)
    filler_word_penalty = Column(Float, nullable=False)
    audio_features_score = Column(Float, nullable=False)
    overall_score = Column(Float, nullable=False)
    category = Column(String, nullable=False)  # "Strong", "Moderate", "Poor"
    feedback_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    audio_file = relationship("AudioFile", back_populates="evaluation_results")
    reference_concept = relationship("ReferenceConcept", back_populates="evaluation_results")
    reports = relationship("Report", back_populates="evaluation_result", cascade="all, delete-orphan")

class Report(Base):
    __tablename__ = 'REPORT'
    id = Column(Integer, primary_key=True, autoincrement=True)
    evaluation_result_id = Column(Integer, ForeignKey('EVALUATION_RESULT.id'), nullable=False)
    pdf_filepath = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    evaluation_result = relationship("EvaluationResult", back_populates="reports")

# Automatically translate old postgres:// protocol schemas to postgresql:// required by SQLAlchemy 2.0
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

try:
    if "[YOUR-PASSWORD]" in DATABASE_URL:
        raise ValueError("Database password placeholder '[YOUR-PASSWORD]' has not been replaced in the .env configuration.")
    
    if DATABASE_URL.startswith("sqlite"):
        engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
    else:
        engine = create_engine(DATABASE_URL)
        # Test connection validity
        with engine.connect() as conn:
            pass
except Exception as e:
    print(f"DATABASE WARNING: Failed to connect to target '{DATABASE_URL}'. Falling back to local SQLite. Error: {e}")
    DATABASE_URL = "sqlite:///vbcua.db"
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@contextmanager
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    Base.metadata.create_all(bind=engine)
    
    # Seed default mock data
    with get_db() as db:
        # Check if default user exists, otherwise create it
        default_user = db.query(User).filter_by(username="default_user").first()
        if not default_user:
            default_user = User(username="default_user", email="student@example.com")
            db.add(default_user)
            db.commit()
            db.refresh(default_user)

        # Check if default reference concepts exist
        concepts = [
            {
                "title": "Photosynthesis",
                "concept_text": "Photosynthesis is the process used by plants, algae and certain bacteria to harness energy from sunlight and turn it into chemical energy. It requires carbon dioxide, water, and sunlight to produce glucose and oxygen, taking place in the chloroplasts using chlorophyll."
            },
            {
                "title": "Neural Networks",
                "concept_text": "A neural network is a method in artificial intelligence that teaches computers to process data in a way that is inspired by the human brain. It uses interconnected nodes or neurons in a layered structure resembling a human brain, containing input layers, hidden layers, and output layers to learn patterns and make predictions."
            },
            {
                "title": "Newton's First Law of Motion",
                "concept_text": "Newton's first law of motion, also known as the law of inertia, states that an object at rest remains at rest, and an object in motion remains in motion with a constant velocity and in a straight line, unless acted upon by a net external force."
            },
            {
                "title": "Water Cycle",
                "concept_text": "The water cycle, also known as the hydrologic cycle, describes the continuous movement of water on, above, and below the surface of the Earth. It involves processes such as evaporation, condensation, precipitation, transpiration, and runoff, driven by solar energy and gravity."
            }
        ]
        
        for c in concepts:
            existing = db.query(ReferenceConcept).filter_by(title=c["title"]).first()
            if not existing:
                ref_concept = ReferenceConcept(title=c["title"], concept_text=c["concept_text"])
                db.add(ref_concept)
        db.commit()

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")
