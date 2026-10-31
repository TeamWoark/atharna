#!/usr/bin/env bash
# نشر الموقع على GitHub + تشغيل GitHub Pages
# الاستخدام:  GITHUB_TOKEN=xxxx GITHUB_USER=username bash tools/publish.sh
set -euo pipefail
: "${GITHUB_TOKEN:?ضع الرمز في المتغير GITHUB_TOKEN}"
: "${GITHUB_USER:?ضع اسم المستخدم في GITHUB_USER}"
REPO="${REPO:-atharna}"

echo "→ إنشاء المستودع إن لم يكن موجودًا…"
curl -s -o /dev/null -w "" -X POST \
  -H "Authorization: Bearer $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github+json" \
  https://api.github.com/user/repos \
  -d "{\"name\":\"$REPO\",\"description\":\"أثرنا — تحدي وباء الوحدة الصامت | تمكّن بلس\",\"private\":false,\"has_issues\":true,\"has_wiki\":false}" || true

echo "→ ربط الريموت…"
git remote remove origin 2>/dev/null || true
git remote add origin "https://x-access-token:${GITHUB_TOKEN}@github.com/${GITHUB_USER}/${REPO}.git"

echo "→ الدفع…"
git push -u origin main

echo "→ تشغيل GitHub Pages…"
curl -s -X POST \
  -H "Authorization: Bearer $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github+json" \
  "https://api.github.com/repos/${GITHUB_USER}/${REPO}/pages" \
  -d '{"source":{"branch":"main","path":"/"}}' > /dev/null || true

echo
echo "تم ✔  المستودع: https://github.com/${GITHUB_USER}/${REPO}"
echo "الموقع:   https://${GITHUB_USER}.github.io/${REPO}/   (يحتاج دقيقة تقريبًا ليظهر أول مرة)"
