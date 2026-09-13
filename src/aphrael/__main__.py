import argparse
import sys

from .config import Settings


def main():
    parser = argparse.ArgumentParser(description="Run Aphrael's local development service")
    parser.add_argument("--port", type=int, help="Loopback HTTP port (default 8765)")
    args = parser.parse_args()
    try:
        settings = Settings.from_env()
        if args.port is not None:
            settings.port = args.port
            settings.__post_init__()
        import uvicorn
        from .app import create_app
        print(f"Aphrael: http://127.0.0.1:{settings.port} | runtime: {settings.data_dir}")
        uvicorn.run(create_app(settings), host="127.0.0.1", port=settings.port, access_log=False)
    except (ValueError, OSError, RuntimeError) as exc:
        print(f"Aphrael could not start: {exc}", file=sys.stderr)
        raise SystemExit(1) from None


if __name__ == "__main__":
    main()
