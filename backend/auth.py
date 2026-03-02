# -*- coding: utf-8 -*-
"""
認証とユーザー管理 - JWT検証対応版
"""

from fastapi import Depends, HTTPException, Header
from sqlalchemy.orm import Session
from database import get_db, User
from typing import Optional
import logging
import os

logger = logging.getLogger(__name__)

NEXTAUTH_SECRET = os.getenv("NEXTAUTH_SECRET", "")


def _verify_jwt_token(token: str) -> dict:
    """NextAuthが発行したJWTトークンを検証し、ペイロードを返す"""
    from jose import jwt, JWTError

    if not NEXTAUTH_SECRET:
        logger.warning("NEXTAUTH_SECRET が未設定のため、JWT検証をスキップします")
        return {"sub": token}

    try:
        payload = jwt.decode(
            token,
            NEXTAUTH_SECRET,
            algorithms=["HS256"],
            options={"verify_aud": False},
        )
        return payload
    except JWTError as e:
        logger.warning(f"JWT検証失敗: {e}")
        raise HTTPException(status_code=401, detail="無効なトークンです。再ログインしてください。")


def get_current_user(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
) -> User:
    """
    リクエストヘッダーからユーザーを取得。
    Bearer トークンをJWTとして検証し、sub クレームからユーザーIDを取得する。
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="認証が必要です。ログインしてください。")

    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="無効な認証形式です。")

    raw_token = parts[1]

    payload = _verify_jwt_token(raw_token)
    user_id = payload.get("sub", raw_token)

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="ユーザーが見つかりません。")

    return user


def get_optional_user(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
) -> Optional[User]:
    """オプションでユーザーを取得（認証が必須ではないエンドポイント用）"""
    if not authorization:
        return None
    try:
        return get_current_user(authorization, db)
    except HTTPException:
        return None


def create_or_update_user(
    user_id: str,
    email: str,
    name: Optional[str],
    picture: Optional[str],
    db: Session,
) -> User:
    """ユーザーを作成または更新"""
    user = db.query(User).filter(User.id == user_id).first()

    if user:
        user.email = email
        user.name = name
        user.picture = picture
        logger.info(f"ユーザー更新: {email}")
    else:
        user = User(id=user_id, email=email, name=name, picture=picture)
        db.add(user)
        logger.info(f"新規ユーザー作成: {email}")

    db.commit()
    db.refresh(user)
    return user
