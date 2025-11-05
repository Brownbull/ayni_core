#!/usr/bin/env python3
"""
Endpoint Registry Validation Script
Validates that all documented endpoints are accessible and respond as expected

Usage:
    python scripts/validate_endpoints.py
    python scripts/validate_endpoints.py --verbose
    python scripts/validate_endpoints.py --category auth

Task: 005-endpoints-registry
DevOps Orchestrator
"""
import argparse
import sys
from typing import Dict, List
import requests
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
TIMEOUT = 5  # seconds

# Endpoint definitions matching endpoints.md
ENDPOINTS = {
    "admin": [
        {"path": "/admin/", "method": "GET", "status": 200, "description": "Admin login page"},
        {"path": "/admin/login/", "method": "GET", "status": 200, "description": "Admin login form"},
    ],
    "auth": [
        {"path": "/api/auth/register/", "method": "POST", "status": 400, "description": "Register (no data = 400)"},
        {"path": "/api/auth/login/", "method": "POST", "status": 400, "description": "Login (no data = 400)"},
        {"path": "/api/auth/token/refresh/", "method": "POST", "status": 400, "description": "Token refresh (no data = 400)"},
    ],
    "companies": [
        {"path": "/api/companies/", "method": "GET", "status": 401, "description": "Company list (no auth = 401)"},
    ],
    "docs": [
        {"path": "/api/docs/", "method": "GET", "status": 200, "description": "Swagger UI"},
        {"path": "/api/schema/", "method": "GET", "status": 200, "description": "OpenAPI schema"},
    ],
}


def validate_endpoint(endpoint: Dict, verbose: bool = False) -> tuple[bool, str]:
    """
    Validate a single endpoint

    Returns:
        (success, message) tuple
    """
    url = f"{BASE_URL}{endpoint['path']}"
    method = endpoint['method']
    expected_status = endpoint['status']

    try:
        if method == 'GET':
            response = requests.get(url, timeout=TIMEOUT, allow_redirects=True)
        elif method == 'POST':
            response = requests.post(url, json={}, timeout=TIMEOUT)
        elif method == 'PUT':
            response = requests.put(url, json={}, timeout=TIMEOUT)
        elif method == 'DELETE':
            response = requests.delete(url, timeout=TIMEOUT)
        else:
            return False, f"Unsupported method: {method}"

        if response.status_code == expected_status:
            msg = f"✅ {method:6} {endpoint['path']:50} → {response.status_code}"
            if verbose:
                msg += f" | {endpoint['description']}"
            return True, msg
        else:
            return False, f"❌ {method:6} {endpoint['path']:50} → Expected {expected_status}, got {response.status_code}"

    except requests.exceptions.Timeout:
        return False, f"❌ {method:6} {endpoint['path']:50} → Timeout after {TIMEOUT}s"
    except requests.exceptions.ConnectionError as e:
        return False, f"❌ {method:6} {endpoint['path']:50} → Connection refused (is server running?)"
    except Exception as e:
        return False, f"❌ {method:6} {endpoint['path']:50} → {type(e).__name__}: {str(e)}"


def validate_category(category: str, endpoints: List[Dict], verbose: bool = False) -> tuple[int, int]:
    """
    Validate all endpoints in a category

    Returns:
        (passed, failed) counts
    """
    print(f"\n{'='*80}")
    print(f"🔍 Validating {category.upper()} endpoints")
    print(f"{'='*80}")

    passed = 0
    failed = 0

    for endpoint in endpoints:
        success, message = validate_endpoint(endpoint, verbose)
        print(message)

        if success:
            passed += 1
        else:
            failed += 1

    return passed, failed


def validate_all_endpoints(verbose: bool = False, category_filter: str = None) -> bool:
    """
    Validate all documented endpoints or a specific category

    Returns:
        True if all validations passed, False otherwise
    """
    print("\n" + "="*80)
    print("🚀 AYNI Endpoint Registry Validation")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 Base URL: {BASE_URL}")
    print("="*80)

    total_passed = 0
    total_failed = 0

    categories_to_validate = {category_filter: ENDPOINTS[category_filter]} if category_filter else ENDPOINTS

    for category, endpoints in categories_to_validate.items():
        passed, failed = validate_category(category, endpoints, verbose)
        total_passed += passed
        total_failed += failed

    # Summary
    print(f"\n{'='*80}")
    print("📊 SUMMARY")
    print(f"{'='*80}")
    print(f"✅ Passed: {total_passed}")
    print(f"❌ Failed: {total_failed}")
    print(f"📈 Total:  {total_passed + total_failed}")
    print(f"📊 Success Rate: {(total_passed / (total_passed + total_failed) * 100):.1f}%")

    if total_failed == 0:
        print("\n🎉 All endpoints validated successfully!")
        return True
    else:
        print(f"\n⚠️  {total_failed} endpoint(s) failed validation")
        print("\n💡 Troubleshooting:")
        print("   1. Ensure Django server is running: cd C:/Projects/play/ayni_be && python manage.py runserver")
        print("   2. Check database is running: docker-compose ps")
        print("   3. Review endpoint implementation in apps/*/urls.py")
        print("   4. Check ai-state/knowledge/endpoints.md for expected behavior")
        return False


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Validate AYNI API endpoints against documentation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/validate_endpoints.py                    # Validate all endpoints
  python scripts/validate_endpoints.py --verbose          # Verbose output
  python scripts/validate_endpoints.py --category auth    # Validate auth only
  python scripts/validate_endpoints.py -c companies       # Short form

Exit codes:
  0 - All validations passed
  1 - One or more validations failed
  2 - Invalid arguments or server not running
        """
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    parser.add_argument(
        '-c', '--category',
        choices=list(ENDPOINTS.keys()),
        help='Validate only specific category'
    )

    args = parser.parse_args()

    try:
        success = validate_all_endpoints(verbose=args.verbose, category_filter=args.category)
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Validation interrupted by user")
        sys.exit(2)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {type(e).__name__}: {str(e)}")
        sys.exit(2)


if __name__ == "__main__":
    main()
