#!/bin/sh

cleanup() {
    kill "$OUTBOX_PID" 2>/dev/null
    kill "$INBOX_PID" 2>/dev/null
    kill "$INBOX_WRITER_PID" 2>/dev/null
    wait "$OUTBOX_PID" 2>/dev/null
    wait "$INBOX_WRITER_PID" 2>/dev/null
    wait "$INBOX_PID" 2>/dev/null
}
trap cleanup EXIT

make migrate
make truncate_db
make outbox & OUTBOX_PID=$!
make inboxw & INBOX_WRITER_PID=$!
make inbox & INBOX_PID=$!
make run