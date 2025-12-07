#!/bin/bash
# ================================================================================================
# Production Readiness Verification Script
# ================================================================================================
# Comprehensive check before deployment

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

ERRORS=0
WARNINGS=0
CHECKS=0

echo -e "${BLUE}================================================================================================${NC}"
echo -e "${BLUE}NOWHERE.AI Production Readiness Verification${NC}"
echo -e "${BLUE}================================================================================================${NC}"
echo ""

# Helper functions
check_pass() {
    CHECKS=$((CHECKS + 1))
    echo -e "${GREEN}✅ PASS${NC} - $1"
}

check_fail() {
    CHECKS=$((CHECKS + 1))
    ERRORS=$((ERRORS + 1))
    echo -e "${RED}❌ FAIL${NC} - $1"
}

check_warn() {
    CHECKS=$((CHECKS + 1))
    WARNINGS=$((WARNINGS + 1))
    echo -e "${YELLOW}⚠️  WARN${NC} - $1"
}

check_info() {
    echo -e "${BLUE}ℹ️  INFO${NC} - $1"
}

# ================================================================================================
# 1. Environment Variables
# ================================================================================================
echo -e "\n${BLUE}[1/10] Checking Environment Variables...${NC}"

if [ -f "backend/.env" ]; then
    check_pass "Backend .env file exists"
    
    # Check critical variables
    source backend/.env 2>/dev/null || true
    
    if [ -n "$JWT_SECRET" ] && [ "$JWT_SECRET" != "change-this-secret-key" ] && [ "$JWT_SECRET" != "default-secret-change-in-production" ]; then
        check_pass "JWT_SECRET is set and not default"
    else
        check_fail "JWT_SECRET is not set or using default value"
    fi
    
    if [ -n "$MONGO_URL" ]; then
        check_pass "MONGO_URL is configured"
    else
        check_fail "MONGO_URL is not set"
    fi
    
    if [ "$ENVIRONMENT" = "production" ]; then
        check_pass "ENVIRONMENT is set to production"
    else
        check_warn "ENVIRONMENT is not set to production (current: $ENVIRONMENT)"
    fi
    
else
    check_fail "Backend .env file not found"
fi

if [ -f "frontend/.env" ]; then
    check_pass "Frontend .env file exists"
else
    check_warn "Frontend .env file not found (may use defaults)"
fi

# ================================================================================================
# 2. Dependencies
# ================================================================================================
echo -e "\n${BLUE}[2/10] Checking Dependencies...${NC}"

if [ -f "backend/requirements.txt" ]; then
    check_pass "Backend requirements.txt exists"
else
    check_fail "Backend requirements.txt not found"
fi

if [ -f "frontend/package.json" ]; then
    check_pass "Frontend package.json exists"
else
    check_fail "Frontend package.json not found"
fi

# Check if dependencies are installed
if [ -d "backend/venv" ] || python3 -c "import fastapi" 2>/dev/null; then
    check_pass "Backend dependencies appear to be installed"
else
    check_warn "Backend dependencies may not be installed"
fi

if [ -d "frontend/node_modules" ]; then
    check_pass "Frontend dependencies are installed"
else
    check_warn "Frontend dependencies may not be installed"
fi

# ================================================================================================
# 3. Database
# ================================================================================================
echo -e "\n${BLUE}[3/10] Checking Database...${NC}"

if pgrep -x "mongod" > /dev/null; then
    check_pass "MongoDB is running"
    
    # Try to connect
    if mongo --eval "db.adminCommand('ping')" --quiet 2>/dev/null; then
        check_pass "MongoDB is accessible"
    else
        check_warn "Could not verify MongoDB connection"
    fi
else
    check_warn "MongoDB process not found (may be containerized)"
fi

# ================================================================================================
# 4. Services
# ================================================================================================
echo -e "\n${BLUE}[4/10] Checking Services...${NC}"

# Check if services are running
if command -v supervisorctl &> /dev/null; then
    if sudo supervisorctl status backend | grep -q "RUNNING"; then
        check_pass "Backend service is running (Supervisor)"
    else
        check_warn "Backend service not running via Supervisor"
    fi
    
    if sudo supervisorctl status frontend | grep -q "RUNNING"; then
        check_pass "Frontend service is running (Supervisor)"
    else
        check_warn "Frontend service not running via Supervisor"
    fi
elif command -v docker-compose &> /dev/null && [ -f "docker-compose.yml" ]; then
    if docker-compose ps | grep -q "Up"; then
        check_pass "Services are running (Docker Compose)"
    else
        check_warn "Docker Compose services may not be running"
    fi
else
    check_info "Using manual service management"
fi

# ================================================================================================
# 5. Ports
# ================================================================================================
echo -e "\n${BLUE}[5/10] Checking Ports...${NC}"

if netstat -tuln 2>/dev/null | grep -q ":8001"; then
    check_pass "Backend port 8001 is listening"
else
    check_warn "Backend port 8001 is not listening"
fi

if netstat -tuln 2>/dev/null | grep -q ":3000\|:80"; then
    check_pass "Frontend port is listening"
else
    check_warn "Frontend port is not listening"
fi

# ================================================================================================
# 6. API Health
# ================================================================================================
echo -e "\n${BLUE}[6/10] Checking API Health...${NC}"

if curl -f -s http://localhost:8001/api/health > /dev/null 2>&1; then
    check_pass "Backend API health check successful"
    
    # Check detailed health
    HEALTH_RESPONSE=$(curl -s http://localhost:8001/api/health?detailed=true)
    if echo "$HEALTH_RESPONSE" | grep -q "healthy"; then
        check_pass "Detailed health check shows healthy status"
    fi
else
    check_fail "Backend API health check failed"
fi

# ================================================================================================
# 7. Security
# ================================================================================================
echo -e "\n${BLUE}[7/10] Checking Security Configuration...${NC}"

# Check security headers
HEADERS=$(curl -I -s http://localhost:8001/api/health 2>/dev/null || echo "")

if echo "$HEADERS" | grep -qi "x-frame-options"; then
    check_pass "Security headers are configured (X-Frame-Options present)"
else
    check_warn "Security headers may not be fully configured"
fi

if echo "$HEADERS" | grep -qi "strict-transport-security"; then
    check_pass "HSTS header is configured"
else
    check_warn "HSTS header not found (consider enabling for HTTPS)"
fi

# Check for default secrets
if grep -q "change-this" backend/.env 2>/dev/null; then
    check_fail "Default secrets found in .env file"
else
    check_pass "No obvious default secrets in .env"
fi

# ================================================================================================
# 8. Files and Permissions
# ================================================================================================
echo -e "\n${BLUE}[8/10] Checking Files and Permissions...${NC}"

if [ -f "backend/server.py" ]; then
    check_pass "Backend server.py exists"
else
    check_fail "Backend server.py not found"
fi

if [ -f "frontend/build/index.html" ] || [ -f "frontend/public/index.html" ]; then
    check_pass "Frontend files exist"
else
    check_warn "Frontend may need to be built"
fi

if [ -d "logs" ]; then
    check_pass "Logs directory exists"
else
    check_info "Logs directory not found (will be created)"
fi

if [ -d "backups" ]; then
    check_pass "Backups directory exists"
else
    check_info "Backups directory not found (will be created)"
fi

# ================================================================================================
# 9. Docker (if using)
# ================================================================================================
echo -e "\n${BLUE}[9/10] Checking Docker Configuration...${NC}"

if [ -f "docker-compose.yml" ]; then
    check_pass "docker-compose.yml exists"
    
    if docker-compose config --quiet 2>/dev/null; then
        check_pass "docker-compose.yml is valid"
    else
        check_warn "docker-compose.yml may have syntax errors"
    fi
else
    check_info "Not using Docker Compose"
fi

if [ -f "backend/Dockerfile" ]; then
    check_pass "Backend Dockerfile exists"
else
    check_info "Backend Dockerfile not found"
fi

# ================================================================================================
# 10. Documentation
# ================================================================================================
echo -e "\n${BLUE}[10/10] Checking Documentation...${NC}"

if [ -f "README.md" ]; then
    check_pass "README.md exists"
else
    check_warn "README.md not found"
fi

if [ -f "PRODUCTION_DEPLOYMENT_GUIDE.md" ]; then
    check_pass "Production deployment guide exists"
else
    check_warn "Production deployment guide not found"
fi

# ================================================================================================
# Summary
# ================================================================================================
echo ""
echo -e "${BLUE}================================================================================================${NC}"
echo -e "${BLUE}Verification Summary${NC}"
echo -e "${BLUE}================================================================================================${NC}"
echo ""
echo "Total Checks: $CHECKS"
echo -e "${GREEN}Passed: $((CHECKS - ERRORS - WARNINGS))${NC}"
echo -e "${YELLOW}Warnings: $WARNINGS${NC}"
echo -e "${RED}Failed: $ERRORS${NC}"
echo ""

# Overall status
if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}🎉 System is PRODUCTION READY!${NC}"
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}⚠️  System is mostly ready with some warnings${NC}"
    echo -e "${YELLOW}Please review warnings before deployment${NC}"
    exit 0
else
    echo -e "${RED}❌ System is NOT ready for production${NC}"
    echo -e "${RED}Please fix errors before deployment${NC}"
    exit 1
fi
