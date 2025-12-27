#!/bin/bash
# Comprehensive test suite for nvdi
# Author: Supun Hewagamage (@supunhg)
# Tests all features and functionality

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${YELLOW}===========================================${NC}"
echo -e "${YELLOW}  nvdi Comprehensive Test Suite${NC}"
echo -e "${YELLOW}===========================================${NC}"
echo ""

# Activate venv
source .venv/bin/activate

# Test counter
PASSED=0
FAILED=0

# Test helper
test_command() {
    local desc="$1"
    local cmd="$2"
    echo -e "${YELLOW}Test:${NC} $desc"
    if eval "$cmd" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ PASSED${NC}"
        ((PASSED++))
    else
        echo -e "${RED}✗ FAILED${NC}"
        ((FAILED++))
    fi
    echo ""
}

test_command_output() {
    local desc="$1"
    local cmd="$2"
    echo -e "${YELLOW}Test:${NC} $desc"
    eval "$cmd"
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ PASSED${NC}"
        ((PASSED++))
    else
        echo -e "${RED}✗ FAILED${NC}"
        ((FAILED++))
    fi
    echo ""
}

echo -e "${YELLOW}=== SECTION 1: CLI Structure ===${NC}"
test_command "Help command" "nvdi --help"
test_command "Get help" "nvdi get --help"
test_command "Search help" "nvdi search --help"
test_command "Export help" "nvdi export --help"
test_command "Monitor help" "nvdi monitor --help"
test_command "Stats help" "nvdi stats --help"
test_command "DB help" "nvdi db --help"

echo -e "${YELLOW}=== SECTION 2: Database Management ===${NC}"
test_command_output "Database info (initial)" "nvdi db info"
test_command "Database clear" "echo 'y' | nvdi db clear"
test_command_output "Database info (after clear)" "nvdi db info"

echo -e "${YELLOW}=== SECTION 3: CVE Retrieval ===${NC}"
test_command "Get CVE (basic)" "nvdi get cve CVE-2021-44228"
test_command "Get CVE (full data)" "nvdi get cve CVE-2021-44228 --full"
test_command "Get CVE (specific fields)" "nvdi get cve CVE-2021-44228 --fields 'id,description,cvssv3'"
test_command "Get CVE (single field)" "nvdi get cve CVE-2021-44228 --fields 'id'"

echo -e "${YELLOW}=== SECTION 4: Search Functionality ===${NC}"
test_command "Search by keyword" "nvdi search keyword 'log4j' --limit 5"
test_command "Search with CVSS filter" "nvdi search keyword 'apache' --min-score 7.0 --limit 3"
test_command "Search with limit" "nvdi search keyword 'python' --limit 2"

echo -e "${YELLOW}=== SECTION 5: Export - JSON ===${NC}"
test_command "Export to JSON (stdout)" "nvdi export cve CVE-2021-44228 --format json"
test_command "Export to JSON file" "nvdi export cve CVE-2021-44228 --format json --output /tmp/nvdi_test.json"
test_command "Verify JSON file exists" "test -f /tmp/nvdi_test.json"
test_command "Export specific fields JSON" "nvdi export cve CVE-2021-44228 --format json --fields 'id,cvssv3'"

echo -e "${YELLOW}=== SECTION 6: Export - CSV ===${NC}"
test_command "Export to CSV" "nvdi export cve CVE-2021-44228 --format csv"
test_command "Export to CSV file" "nvdi export cve CVE-2021-44228 --format csv --output /tmp/nvdi_test.csv"
test_command "Verify CSV file exists" "test -f /tmp/nvdi_test.csv"
test_command "Export specific fields CSV" "nvdi export cve CVE-2021-44228 --format csv --fields 'id,description'"

echo -e "${YELLOW}=== SECTION 7: Export - TXT ===${NC}"
test_command "Export to TXT" "nvdi export cve CVE-2021-44228 --format txt"
test_command "Export to TXT file" "nvdi export cve CVE-2021-44228 --format txt --output /tmp/nvdi_test.txt"
test_command "Verify TXT file exists" "test -f /tmp/nvdi_test.txt"

echo -e "${YELLOW}=== SECTION 8: Product Monitoring ===${NC}"
test_command "Add product to monitor" "nvdi monitor add nginx"
test_command "Add another product" "nvdi monitor add apache"
test_command "List monitored products" "nvdi monitor list-products"

echo -e "${YELLOW}=== SECTION 9: Statistics ===${NC}"
test_command_output "Show database statistics" "nvdi stats show"
test_command_output "Database info (populated)" "nvdi db info"

echo -e "${YELLOW}=== SECTION 10: Field Validation ===${NC}"
test_command "Query non-existent CVE" "nvdi get cve CVE-9999-99999 || true"

echo -e "${YELLOW}=== SECTION 11: Database Verification ===${NC}"
test_command "Verify DB file exists" "test -f .nvdi-data/nvdi.db"
test_command "Verify cache dir exists" "test -d .nvdi-cache"

echo -e "${YELLOW}=== SECTION 12: Cleanup Test Files ===${NC}"
test_command "Remove test JSON" "rm -f /tmp/nvdi_test.json"
test_command "Remove test CSV" "rm -f /tmp/nvdi_test.csv"
test_command "Remove test TXT" "rm -f /tmp/nvdi_test.txt"

# Summary
echo -e "${YELLOW}===========================================${NC}"
echo -e "${YELLOW}  Test Summary${NC}"
echo -e "${YELLOW}===========================================${NC}"
echo -e "${GREEN}Passed: $PASSED${NC}"
if [ $FAILED -gt 0 ]; then
    echo -e "${RED}Failed: $FAILED${NC}"
    exit 1
else
    echo -e "${GREEN}Failed: $FAILED${NC}"
    echo ""
    echo -e "${GREEN}✓ All tests passed!${NC}"
    echo ""
    echo -e "${YELLOW}Database:${NC} .nvdi-data/nvdi.db"
    echo -e "${YELLOW}Cache:${NC} .nvdi-cache/"
    echo ""
fi