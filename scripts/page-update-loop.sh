#!/usr/bin/env bash
set -u

INTERVAL_SECONDS="${NN_PAGE_UPDATE_INTERVAL_SECONDS:-900}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
running=true
sleep_pid=""

log() {
    printf '[%s] %s\n' "$(date -u '+%Y-%m-%d %H:%M:%S UTC')" "$*"
}

stop() {
    running=false
    if [[ -n "$sleep_pid" ]]; then
        kill "$sleep_pid" 2>/dev/null || true
    fi
}

trap stop INT TERM

case "$INTERVAL_SECONDS" in
    ''|*[!0-9]*)
        echo "NN_PAGE_UPDATE_INTERVAL_SECONDS must be a positive integer" >&2
        exit 1
        ;;
esac

if [[ "$INTERVAL_SECONDS" -eq 0 ]]; then
    echo "NN_PAGE_UPDATE_INTERVAL_SECONDS must be greater than zero" >&2
    exit 1
fi

if [[ -z "${NN_DB_URL:-}" ]]; then
    echo "Set NN_DB_URL to the production SQLite database URL before starting" >&2
    exit 1
fi

log "starting page-update loop; interval=${INTERVAL_SECONDS}s"

while "$running"; do
    log "running make page-update"
    if make -C "$REPO_ROOT" page-update; then
        log "make page-update completed"
    else
        status=$?
        log "make page-update failed with exit status $status"
    fi

    if ! "$running"; then
        break
    fi

    log "sleeping ${INTERVAL_SECONDS}s"
    sleep "$INTERVAL_SECONDS" &
    sleep_pid=$!
    wait "$sleep_pid" || true
    sleep_pid=""
done

log "stopped page-update loop"
