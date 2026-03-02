#!/bin/bash
# Cloud Run デプロイスクリプト（セキュリティ設定込み）
# 使用方法: bash scripts/deploy-cloudrun.sh

set -euo pipefail

PROJECT_ID="${GCP_PROJECT_ID:?GCP_PROJECT_ID を設定してください}"
REGION="${GCP_REGION:-asia-northeast1}"

BACKEND_SERVICE="marketing-interview-backend"
FRONTEND_SERVICE="marketing-interview-frontend"
BACKEND_IMAGE="${REGION}-docker.pkg.dev/${PROJECT_ID}/cloud-run-source-deploy/${BACKEND_SERVICE}"
FRONTEND_IMAGE="${REGION}-docker.pkg.dev/${PROJECT_ID}/cloud-run-source-deploy/${FRONTEND_SERVICE}"

echo "=== 1. Secret Manager にシークレットを登録 ==="
for SECRET_NAME in GOOGLE_API_KEY GOOGLE_CLIENT_ID GOOGLE_CLIENT_SECRET NEXTAUTH_SECRET DATABASE_URL; do
  if ! gcloud secrets describe "${SECRET_NAME}" --project="${PROJECT_ID}" &>/dev/null; then
    echo "  シークレット ${SECRET_NAME} を作成中..."
    echo -n "値を入力 (${SECRET_NAME}): "
    read -rs SECRET_VALUE
    echo
    printf '%s' "${SECRET_VALUE}" | gcloud secrets create "${SECRET_NAME}" \
      --project="${PROJECT_ID}" \
      --replication-policy="automatic" \
      --data-file=-
  else
    echo "  ${SECRET_NAME} は既に存在します（スキップ）"
  fi
done

echo ""
echo "=== 2. バックエンドをビルド & デプロイ ==="
BACKEND_URL=$(gcloud run deploy "${BACKEND_SERVICE}" \
  --project="${PROJECT_ID}" \
  --region="${REGION}" \
  --source=. \
  --dockerfile=Dockerfile \
  --set-secrets="GOOGLE_API_KEY=GOOGLE_API_KEY:latest,NEXTAUTH_SECRET=NEXTAUTH_SECRET:latest,DATABASE_URL=DATABASE_URL:latest" \
  --set-env-vars="PYTHONUNBUFFERED=1" \
  --no-allow-unauthenticated \
  --memory=1Gi \
  --timeout=300 \
  --max-instances=5 \
  --format='value(status.url)')

echo "  バックエンドURL: ${BACKEND_URL}"

echo ""
echo "=== 3. フロントエンドをビルド & デプロイ ==="
FRONTEND_URL=$(gcloud run deploy "${FRONTEND_SERVICE}" \
  --project="${PROJECT_ID}" \
  --region="${REGION}" \
  --source=frontend \
  --set-secrets="GOOGLE_CLIENT_ID=GOOGLE_CLIENT_ID:latest,GOOGLE_CLIENT_SECRET=GOOGLE_CLIENT_SECRET:latest,NEXTAUTH_SECRET=NEXTAUTH_SECRET:latest" \
  --set-env-vars="NEXT_PUBLIC_API_URL=${BACKEND_URL},NEXTAUTH_URL=${FRONTEND_URL:-}" \
  --build-arg="NEXT_PUBLIC_API_URL=${BACKEND_URL}" \
  --allow-unauthenticated \
  --memory=512Mi \
  --timeout=60 \
  --max-instances=5 \
  --format='value(status.url)')

echo "  フロントエンドURL: ${FRONTEND_URL}"

echo ""
echo "=== 4. バックエンドのCORS設定を更新 ==="
gcloud run services update "${BACKEND_SERVICE}" \
  --project="${PROJECT_ID}" \
  --region="${REGION}" \
  --update-env-vars="CORS_ALLOWED_ORIGINS=${FRONTEND_URL}"

echo ""
echo "=== 5. IAM設定: バックエンドへのアクセス制限 ==="
FRONTEND_SA=$(gcloud run services describe "${FRONTEND_SERVICE}" \
  --project="${PROJECT_ID}" \
  --region="${REGION}" \
  --format='value(spec.template.spec.serviceAccountName)')

if [ -z "${FRONTEND_SA}" ]; then
  FRONTEND_SA="${PROJECT_ID}@appspot.gserviceaccount.com"
fi

gcloud run services add-iam-policy-binding "${BACKEND_SERVICE}" \
  --project="${PROJECT_ID}" \
  --region="${REGION}" \
  --member="serviceAccount:${FRONTEND_SA}" \
  --role="roles/run.invoker"

echo ""
echo "=== 6. NextAuth URLを最終更新 ==="
gcloud run services update "${FRONTEND_SERVICE}" \
  --project="${PROJECT_ID}" \
  --region="${REGION}" \
  --update-env-vars="NEXTAUTH_URL=${FRONTEND_URL}"

echo ""
echo "=== デプロイ完了 ==="
echo "フロントエンド: ${FRONTEND_URL}"
echo "バックエンド:   ${BACKEND_URL} (認証必須)"
echo ""
echo "次のステップ:"
echo "  1. Google OAuth コンソールで承認済みリダイレクト URI を追加:"
echo "     ${FRONTEND_URL}/api/auth/callback/google"
echo "  2. ブラウザで ${FRONTEND_URL} にアクセスして動作確認"
