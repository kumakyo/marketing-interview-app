# -*- coding: utf-8 -*-
"""
データベース管理ヘルパー関数
"""

from sqlalchemy.orm import Session
from database import User, Project, Persona, Interview, Analysis, InterviewSessionDB
from typing import List, Dict, Optional
import uuid
import json
import logging

logger = logging.getLogger(__name__)

# --- プロジェクト管理 ---

def save_project(
    user: User,
    topic: str,
    products_services: List[dict],
    competitors: List[dict],
    analysis_types: List[str],
    db: Session
) -> Project:
    """プロジェクトを保存"""
    project = Project(
        id=str(uuid.uuid4()),
        user_id=user.id,
        topic=topic,
        products_services=products_services,
        competitors=competitors,
        analysis_types=analysis_types
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    logger.info(f"プロジェクト保存: {project.id} - {topic}")
    return project


def get_user_projects(user: User, db: Session, limit: int = 10) -> List[Project]:
    """ユーザーのプロジェクト一覧を取得"""
    return db.query(Project).filter(
        Project.user_id == user.id
    ).order_by(Project.created_at.desc()).limit(limit).all()


# --- ペルソナ管理 ---

def save_personas(
    project: Project,
    personas: List[dict],
    db: Session
) -> List[Persona]:
    """ペルソナを保存"""
    saved_personas = []
    for i, persona_data in enumerate(personas):
        persona = Persona(
            id=str(uuid.uuid4()),
            project_id=project.id,
            name=persona_data['name'],
            details=persona_data['details'],
            raw_text=persona_data.get('raw_text', ''),
            index_order=i
        )
        db.add(persona)
        saved_personas.append(persona)
    
    db.commit()
    logger.info(f"ペルソナ保存: {len(saved_personas)}件")
    return saved_personas


def get_project_personas(project_id: str, db: Session) -> List[Persona]:
    """プロジェクトのペルソナを取得"""
    return db.query(Persona).filter(
        Persona.project_id == project_id
    ).order_by(Persona.index_order).all()


# --- インタビュー管理 ---

def save_interview(
    project: Project,
    persona: Persona,
    questions: List[str],
    results: List[dict],
    is_hypothesis_phase: bool,
    db: Session
) -> Interview:
    """インタビュー結果を保存"""
    interview = Interview(
        id=str(uuid.uuid4()),
        project_id=project.id,
        persona_id=persona.id,
        questions=questions,
        results=results,
        is_hypothesis_phase=1 if is_hypothesis_phase else 0
    )
    db.add(interview)
    db.commit()
    db.refresh(interview)
    logger.info(f"インタビュー保存: {interview.id}")
    return interview


def get_project_interviews(project_id: str, db: Session) -> List[Interview]:
    """プロジェクトのインタビュー結果を取得"""
    return db.query(Interview).filter(
        Interview.project_id == project_id
    ).order_by(Interview.created_at).all()


# --- 分析管理 ---

def save_analysis(
    project_id: str,
    analysis_type: str,
    content: str,
    db: Session
) -> Analysis:
    """分析結果を保存"""
    analysis = Analysis(
        id=str(uuid.uuid4()),
        project_id=project_id,
        analysis_type=analysis_type,
        content=content
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    logger.info(f"分析保存: {analysis.id} - {analysis_type}")
    return analysis


def get_project_analyses(project_id: str, db: Session) -> List[Analysis]:
    """プロジェクトの分析結果を取得"""
    return db.query(Analysis).filter(
        Analysis.project_id == project_id
    ).order_by(Analysis.created_at).all()


# --- セッション状態管理 ---

def save_session_state(
    user: User,
    session_id: str,
    project_id: Optional[str],
    state: dict,
    db: Session
) -> InterviewSessionDB:
    """セッション状態を保存"""
    session = db.query(InterviewSessionDB).filter(
        InterviewSessionDB.id == session_id
    ).first()
    
    if session:
        # 既存セッションを更新
        session.project_id = project_id
        session.state = state
    else:
        # 新規セッション作成
        session = InterviewSessionDB(
            id=session_id,
            user_id=user.id,
            project_id=project_id,
            state=state
        )
        db.add(session)
    
    db.commit()
    db.refresh(session)
    logger.info(f"セッション状態保存: {session_id}")
    return session


def get_session_state(session_id: str, db: Session) -> Optional[InterviewSessionDB]:
    """セッション状態を取得"""
    return db.query(InterviewSessionDB).filter(
        InterviewSessionDB.id == session_id
    ).first()


# --- ユーティリティ ---

def get_user_statistics(user: User, db: Session) -> dict:
    """ユーザーの統計情報を取得"""
    projects_count = db.query(Project).filter(Project.user_id == user.id).count()
    
    # 最新のプロジェクトを取得
    latest_project = db.query(Project).filter(
        Project.user_id == user.id
    ).order_by(Project.created_at.desc()).first()
    
    interviews_count = 0
    if latest_project:
        interviews_count = db.query(Interview).filter(
            Interview.project_id == latest_project.id
        ).count()
    
    return {
        "projects_count": projects_count,
        "interviews_count": interviews_count,
        "latest_project": {
            "id": latest_project.id,
            "topic": latest_project.topic,
            "created_at": latest_project.created_at.isoformat()
        } if latest_project else None
    }

