#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${BASE_URL:-http://localhost:8000/api}"
RUN_ID="$(date +%s)"
EMAIL="cinefan_${RUN_ID}@example.com"
USERNAME="cinefan_${RUN_ID}"
PASSWORD="SuperSecretPassword123!"

if ! command -v jq >/dev/null 2>&1; then
  echo "Error: jq is required to run this script."
  exit 1
fi

extract_value() {
  local json="$1"
  local expression="$2"
  echo "$json" | jq -r "$expression // empty"
}

request_json() {
  local method="$1"
  local url="$2"
  local body="${3:-}"
  local expected_status="${4:-200}"
  local auth_header=()

  if [[ -n "${TOKEN:-}" ]]; then
    auth_header=(-H "Authorization: Bearer ${TOKEN}")
  fi

  local response_file
  response_file="$(mktemp)"

  local status
  if [[ -n "$body" ]]; then
    status="$(curl -sS -o "$response_file" -w "%{http_code}" -X "$method" \
      "${auth_header[@]}" \
      -H "Content-Type: application/json" \
      -d "$body" \
      "$url")"
  else
    status="$(curl -sS -o "$response_file" -w "%{http_code}" -X "$method" \
      "${auth_header[@]}" \
      "$url")"
  fi

  local response
  response="$(cat "$response_file")"
  rm -f "$response_file"

  if [[ "$status" != "$expected_status" ]]; then
    echo "Request failed: $method $url" >&2
    echo "Expected status: $expected_status | Actual status: $status" >&2
    echo "Response: $response" >&2
    exit 1
  fi

  echo "$response"
}

echo "Starting CineReserve API End-to-End Test..."

echo "1) Register User"
REGISTER_PAYLOAD="$(jq -n --arg email "$EMAIL" --arg username "$USERNAME" --arg password "$PASSWORD" '{email: $email, username: $username, password: $password}')"
request_json POST "${BASE_URL}/users/register/" "$REGISTER_PAYLOAD" "201" >/dev/null
echo "   OK ($EMAIL)"

echo "2) Login and get token"
LOGIN_PAYLOAD="$(jq -n --arg email "$EMAIL" --arg password "$PASSWORD" '{email: $email, password: $password}')"
LOGIN_RESPONSE="$(request_json POST "${BASE_URL}/users/login/" "$LOGIN_PAYLOAD" "200")"
TOKEN="$(extract_value "$LOGIN_RESPONSE" '.access')"
if [[ -z "$TOKEN" || "$TOKEN" == "null" ]]; then
  echo "Could not extract JWT token."
  exit 1
fi
echo "   OK"

echo "3) List Movies"
MOVIES_RESPONSE="$(request_json GET "${BASE_URL}/cinema/movies/" "" "200")"
MOVIE_ID="$(extract_value "$MOVIES_RESPONSE" '.results[0].id')"
if [[ -z "$MOVIE_ID" || "$MOVIE_ID" == "null" ]]; then
  echo "No movies found in the database! Please run the seed command first."
  exit 1
fi
echo "   OK (Found Movie ID: $MOVIE_ID)"

echo "4) List Sessions for Movie"
SESSIONS_RESPONSE="$(request_json GET "${BASE_URL}/cinema/sessions/?movie_id=${MOVIE_ID}" "" "200")"
SESSION_ID="$(extract_value "$SESSIONS_RESPONSE" '.results[0].id')"
if [[ -z "$SESSION_ID" || "$SESSION_ID" == "null" ]]; then
  echo "No sessions found for this movie!"
  exit 1
fi
echo "   OK (Found Session ID: $SESSION_ID)"

echo "5) Get Seat Map and pick available seat"
SEATS_RESPONSE="$(request_json GET "${BASE_URL}/cinema/sessions/${SESSION_ID}/seat_map/" "" "200")"
SEAT_ID="$(echo "$SEATS_RESPONSE" | jq -r 'map(select(.status == "Available")) | .[0].seat_id // empty')"
if [[ -z "$SEAT_ID" || "$SEAT_ID" == "null" ]]; then
  echo "No available seats found for this session!"
  exit 1
fi
echo "   OK (Found Available Seat ID: $SEAT_ID)"

echo "6) Reserve Seat (Redis Lock)"
RESERVE_PAYLOAD="$(jq -n --argjson session_id "$SESSION_ID" --argjson seat_id "$SEAT_ID" '{session_id: $session_id, seat_id: $seat_id}')"
request_json POST "${BASE_URL}/ticketing/reserve/" "$RESERVE_PAYLOAD" "200" >/dev/null
echo "   OK (Seat locked for 10 minutes)"

echo "7) Checkout (Create Ticket)"
CHECKOUT_PAYLOAD="$(jq -n --argjson session_id "$SESSION_ID" --argjson seat_id "$SEAT_ID" '{session_id: $session_id, seat_id: $seat_id}')"
request_json POST "${BASE_URL}/ticketing/checkout/" "$CHECKOUT_PAYLOAD" "201" >/dev/null
echo "   OK (Ticket purchased successfully)"

echo "8) View My Tickets Portal"
TICKETS_RESPONSE="$(request_json GET "${BASE_URL}/ticketing/my-tickets/" "" "200")"
TICKET_COUNT="$(extract_value "$TICKETS_RESPONSE" '.count')"
echo "   OK (Total tickets in wallet: $TICKET_COUNT)"

echo -e "\nAll core endpoint checks completed successfully."