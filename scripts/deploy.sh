#!/usr/bin/env bash
set -euo pipefail

REMOTE_HOST="test.k3rnel-pan1c.com"
REMOTE_PORT=2223
REMOTE_USER="marko"
IMAGE_NAME="openbench"
REMOTE="$REMOTE_USER@$REMOTE_HOST"
SSH_OPTS=(-p "$REMOTE_PORT" -o ConnectTimeout=10 -o ServerAliveInterval=5 -o ServerAliveCountMax=3)
: "${PUBLIC_URL:?PUBLIC_URL must be set}"
: "${PORT:?PORT must be set}"

print_remote_diagnostics() {
  ssh "${SSH_OPTS[@]}" "$REMOTE" '
    docker ps -a --filter "name='"${IMAGE_NAME}"'" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    echo
    docker logs --tail 80 '"${IMAGE_NAME}"' 2>/dev/null || true
  ' || true
}

printf "==> building image ($IMAGE_NAME, linux/amd64)..."
if [ "${SKIP_DOCKER_BUILD:-0}" != "1" ]; then
  ./scripts/build.sh linux/amd64 > /dev/null 2>&1
fi
echo "ok"

printf "==> saving image..."
docker save "$IMAGE_NAME" | gzip > /tmp/"${IMAGE_NAME}".tar.gz
echo "ok"

printf "==> uploading to $REMOTE_HOST..."
scp -P "$REMOTE_PORT" -o ConnectTimeout=10 -o ServerAliveInterval=5 -o ServerAliveCountMax=3 /tmp/"${IMAGE_NAME}".tar.gz "$REMOTE":/tmp/"${IMAGE_NAME}".tar.gz
rm /tmp/"${IMAGE_NAME}".tar.gz
echo "ok"

printf "==> loading image on remote..."
ssh "${SSH_OPTS[@]}" "$REMOTE" '
  docker load < /tmp/'"${IMAGE_NAME}"'.tar.gz
  rm /tmp/'"${IMAGE_NAME}"'.tar.gz
' > /dev/null 2>&1
echo "ok"

printf "==> starting container..."
printf -v image_name_q '%q' "$IMAGE_NAME"
printf -v port_q '%q' "$PORT"
printf -v public_url_q '%q' "$PUBLIC_URL"
if ! container_id=$(ssh "${SSH_OPTS[@]}" "$REMOTE" 'bash -se' <<EOF
set -euo pipefail
image_name=$image_name_q
port=$port_q
public_url=$public_url_q

docker stop "\$image_name" 2>/dev/null || true
docker rm "\$image_name" 2>/dev/null || true
docker run -d \
  -p "\$port:\$port" \
  -e PORT="\$port" \
  -e PUBLIC_URL="\$public_url" \
  -e DEPLOY_DATE="\$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  --name "\$image_name" \
  --restart unless-stopped \
  "\$image_name"
EOF
)
then
  echo "FAIL"
  echo "    remote container start failed"
  echo "    remote diagnostics:"
  print_remote_diagnostics
  exit 1
fi
echo "started (${container_id:0:12})"

printf "==> waiting for server..."
WAIT_TIMEOUT_SECONDS="${WAIT_TIMEOUT_SECONDS:-120}"
WAIT_INTERVAL_SECONDS="${WAIT_INTERVAL_SECONDS:-2}"
WAIT_DEADLINE=$(( $(date +%s) + WAIT_TIMEOUT_SECONDS ))
server_ready=false

while (( $(date +%s) < WAIT_DEADLINE )); do
  if ssh "${SSH_OPTS[@]}" "$REMOTE" 'curl -sf --max-time 3 http://localhost:'"$PORT"' > /dev/null' 2>/dev/null; then
    server_ready=true
    break
  fi
  sleep "$WAIT_INTERVAL_SECONDS"
done

if [[ "$server_ready" != true ]]; then
  echo "FAIL"
  echo "    server did not start within ${WAIT_TIMEOUT_SECONDS}s"
  echo "    remote diagnostics:"
  print_remote_diagnostics
  exit 1
fi
echo "server reachable"

printf "==> checking public endpoint ($PUBLIC_URL)..."
if ! body=$(curl -sf --max-time 10 "$PUBLIC_URL"); then
  echo "FAIL"
  echo "    could not reach $PUBLIC_URL"
  exit 1
fi

if ! echo "$body" | grep -q "LLM Benchmark Dashboard"; then
  echo "FAIL"
  echo "    $PUBLIC_URL does not contain 'LLM Benchmark Dashboard'"
  echo "    $body"
  exit 1
fi
echo "ok"

./scripts/get_logs.sh


echo "==> deployed $IMAGE_NAME to $PUBLIC_URL"
