# -*- coding: utf-8 -*-
"""
データベース設定とモデル定義
"""

from sqlalchemy import create_engine, Column, String, DateTime, Text, Integer, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

# データベースファイルのパス
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    # SQLAlchemyの仕様で postgres:// を postgresql:// に置換
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

if not DATABASE_URL:
    # ローカル実行用のフォールバック
    DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "marketing_interview.db")
    DATABASE_URL = f"sqlite:///{DB_PATH}"

# connect_args は SQLite 専用の設定なので、PostgreSQL時は除外する
if "sqlite" in DATABASE_URL:
    engine = create_engine(DATABASE_URL, echo=False, connect_args={"check_same_thread": False})
else:
    # PostgreSQLの場合は connect_args は不要
    engine = create_engine(DATABASE_URL, echo=False)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# データベースセッションを取得するヘルパー関数
def get_db():
    """データベースセッションを取得"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- データベースモデル ---

class User(Base):
    """ユーザーテーブル"""
    __tablename__ = "users"
    
    id = Column(String, primary_key=True)  # Google User ID
    email = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=True)
    picture = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # リレーション
    projects = relationship("Project", back_populates="user", cascade="all, delete-orphan")
    sessions = relationship("InterviewSessionDB", back_populates="user", cascade="all, delete-orphan")


class Project(Base):
    """プロジェクトテーブル（商品情報など）"""
    __tablename__ = "projects"
    
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    topic = Column(String, nullable=False)
    products_services = Column(JSON, nullable=False)  # List[ProductService]
    competitors = Column(JSON, nullable=True)  # List[Competitor]
    analysis_types = Column(JSON, nullable=True)  # List[str]
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # リレーション
    user = relationship("User", back_populates="projects")
    personas = relationship("Persona", back_populates="project", cascade="all, delete-orphan")
    interviews = relationship("Interview", back_populates="project", cascade="all, delete-orphan")


class Persona(Base):
    """ペルソナテーブル"""
    __tablename__ = "personas"
    
    id = Column(String, primary_key=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False, index=True)
    name = Column(String, nullable=False)
    details = Column(JSON, nullable=False)  # Dict[str, str]
    raw_text = Column(Text, nullable=False)
    index_order = Column(Integer, nullable=False)  # 表示順序
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # リレーション
    project = relationship("Project", back_populates="personas")
    interviews = relationship("Interview", back_populates="persona", cascade="all, delete-orphan")


class Interview(Base):
    """インタビューテーブル"""
    __tablename__ = "interviews"
    
    id = Column(String, primary_key=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False, index=True)
    persona_id = Column(String, ForeignKey("personas.id"), nullable=False, index=True)
    questions = Column(JSON, nullable=False)  # List[str]
    results = Column(JSON, nullable=False)  # List[InterviewResult]
    is_hypothesis_phase = Column(Integer, default=0)  # 0: 初回, 1: 仮説検証
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # リレーション
    project = relationship("Project", back_populates="interviews")
    persona = relationship("Persona", back_populates="interviews")


class Analysis(Base):
    """分析結果テーブル"""
    __tablename__ = "analyses"
    
    id = Column(String, primary_key=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False, index=True)
    analysis_type = Column(String, nullable=False)  # "initial", "hypothesis", "final"
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # インデックス
    # project_idとanalysis_typeで検索することが多い


class InterviewSessionDB(Base):
    """セッションテーブル（現在のインタビュー状態）"""
    __tablename__ = "interview_sessions"
    
    id = Column(String, primary_key=True)  # session_id
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=True, index=True)
    state = Column(JSON, nullable=False)  # セッションの状態を保存
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # リレーション
    user = relationship("User", back_populates="sessions")


# データベーステーブルを作成
def init_db():
    """データベースを初期化"""
    Base.metadata.create_all(bind=engine)
    print("✅ データベーステーブルを作成しました")


if __name__ == "__main__":
    # データベース初期化スクリプトとして実行
    init_db()
    # DB_PATHが存在する場合のみ表示（SQLite用）
    if 'DB_PATH' in locals() or 'DB_PATH' in globals():
        print(f"データベースファイル: {DB_PATH}")
    else:
        print("Cloud SQL (PostgreSQL) に接続しました")

