import os
import string
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, request, redirect, jsonify
import redis
import psycopg2

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

app = Flask(__name__)

# Define the 62 characters used for short codes (0-9, a-z, A-Z)
ALPHABET = string.digits + string.ascii_lowercase + string.ascii_uppercase
ALPHABET_INDEX = {char: i for i, char in enumerate(ALPHABET)}

# Connect to Redis for fast lookups
cache = redis.Redis(
    host=os.environ.get("REDIS_HOST", "redis"),
    port=int(os.environ.get("REDIS_PORT", 6379)),
    decode_responses=True,
)


def get_db():
    """Connect to PostgreSQL for permanent storage."""
    return psycopg2.connect(
        host=os.environ.get("POSTGRES_HOST", "db"),
        database=os.environ.get("POSTGRES_DB", "urlshortener"),
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
    )

def base62_encode(num):
    """Convert a database ID into a short alphanumeric string."""
    if num == 0:
        return ALPHABET[0]
    result = []
    while num > 0:
        num, remainder = divmod(num, 62)
        result.append(ALPHABET[remainder])
    return "".join(reversed(result))


def base62_decode(code):
    """Convert a short code back into the original database ID."""
    num = 0
    for char in code:
        if char not in ALPHABET_INDEX:
            raise ValueError("invalid short code")
        num = num * 62 + ALPHABET_INDEX[char]
    return num


def is_valid_short_code(code):
    return bool(code) and all(char in ALPHABET_INDEX for char in code)


@app.route("/shorten", methods=["POST"])
def shorten_url():
    # Grab the long URL from the request body
    data = request.get_json()
    if not data or "url" not in data:
        return jsonify({"error": "Missing url field"}), 400

    long_url = data["url"]

    # Save to PostgreSQL - the database assigns an auto-incrementing ID
    conn = get_db()
    cur = conn.cursor()
    cur.execute("INSERT INTO urls (long_url) VALUES (%s) RETURNING id", (long_url,))
    url_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()

    # Encode the database ID into a short code
    short_code = base62_encode(url_id)

    # Cache the mapping for fast redirects later
    cache.set(short_code, long_url)

    return jsonify({"short_url": f"{os.environ['BASE_URL']}/{short_code}", "short_code": short_code}), 201


@app.route("/")
def index():
    return jsonify({"service": "url-shortener", "health": "/health", "shorten": "POST /shorten"}), 200


@app.route("/favicon.ico")
def favicon():
    return "", 204


@app.route("/health")
def health():
    try:
        cache.ping()
        conn = get_db()
        conn.close()
    except Exception:
        return jsonify({"status": "unhealthy"}), 503
    return jsonify({"status": "healthy"}), 200


@app.route("/<short_code>")
def redirect_url(short_code):
    if not is_valid_short_code(short_code):
        return jsonify({"error": "Short URL not found"}), 404

    # Check the fast cache first
    long_url = cache.get(short_code)

    if long_url:
        print("CACHE HIT", flush=True)
        return redirect(long_url, code=302)

    # Cache miss - fall back to the database
    print("CACHE MISS - querying database", flush=True)
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT long_url FROM urls WHERE id = %s", (base62_decode(short_code),))
    result = cur.fetchone()
    cur.close()
    conn.close()

    if not result:
        return jsonify({"error": "Short URL not found"}), 404

    # Found it in the database - cache it for next time
    long_url = result[0]
    cache.set(short_code, long_url)

    return redirect(long_url, code=302)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
