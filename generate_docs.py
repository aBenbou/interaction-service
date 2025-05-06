from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.units import inch

def create_technical_documentation_pdf():
    # Create the PDF document
    doc = SimpleDocTemplate(
        "microservices_technical_documentation.pdf",
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )

    # Get styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30
    )
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=18,
        spaceAfter=20
    )
    subheading_style = ParagraphStyle(
        'CustomSubHeading',
        parent=styles['Heading3'],
        fontSize=14,
        spaceAfter=15
    )
    code_style = ParagraphStyle(
        'CodeStyle',
        parent=styles['Code'],
        fontSize=10,
        fontName='Courier',
        spaceAfter=12
    )

    content = []

    # Title
    content.append(Paragraph("Microservices Technical Documentation", title_style))
    content.append(Spacer(1, 20))

    # 1. API Versioning
    content.append(Paragraph("1. API Versioning", heading_style))
    content.append(Paragraph("Version Control Strategy", subheading_style))
    versioning_text = """
    • URL Path Versioning: /api/v1/*
    • Header Versioning: Accept: application/json; version=1.0
    • Current Version: v1
    • Deprecation Policy: 6 months notice before EOL
    """
    content.append(Paragraph(versioning_text, styles["Normal"]))
    content.append(Spacer(1, 12))

    # 2. API Endpoints Documentation
    content.append(Paragraph("2. API Endpoints Documentation", heading_style))
    
    # Auth Service Endpoints
    content.append(Paragraph("Auth Service Endpoints", subheading_style))
    auth_endpoints = [
        ["Endpoint", "Method", "Description", "Auth Required"],
        ["/api/v1/auth/register", "POST", "User registration", "No"],
        ["/api/v1/auth/login", "POST", "User login", "No"],
        ["/api/v1/auth/refresh", "POST", "Refresh token", "Yes"],
        ["/api/v1/auth/logout", "POST", "User logout", "Yes"]
    ]
    auth_table = Table(auth_endpoints, colWidths=[2*inch, inch, 2.5*inch, inch])
    auth_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    content.append(auth_table)
    content.append(Spacer(1, 20))

    # Example API Usage
    content.append(Paragraph("API Usage Example", subheading_style))
    api_example = """
    // User Registration Example
    POST /api/v1/auth/register
    Content-Type: application/json
    
    {
        "username": "user@example.com",
        "password": "securePassword123",
        "email": "user@example.com"
    }
    """
    content.append(Paragraph(api_example, code_style))
    content.append(Spacer(1, 20))

    # 3. Error Handling
    content.append(PageBreak())
    content.append(Paragraph("3. Error Handling Documentation", heading_style))
    error_codes = [
        ["Status Code", "Type", "Description"],
        ["400", "Bad Request", "Invalid input parameters"],
        ["401", "Unauthorized", "Authentication required"],
        ["403", "Forbidden", "Insufficient permissions"],
        ["404", "Not Found", "Resource not found"],
        ["500", "Server Error", "Internal server error"]
    ]
    error_table = Table(error_codes, colWidths=[1.5*inch, 1.5*inch, 3*inch])
    error_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    content.append(error_table)
    content.append(Spacer(1, 20))

    # 4. Database Requirements
    content.append(Paragraph("4. Database Requirements", heading_style))
    db_requirements = """
    • Primary Database: PostgreSQL 14+
    • Connection Pooling: PgBouncer
    • Backup Schedule: Daily full backup, hourly WAL archiving
    • Replication: Async streaming replication with 1 standby
    • Monitoring: pg_stat_statements, pgmetrics
    """
    content.append(Paragraph(db_requirements, styles["Normal"]))
    content.append(Spacer(1, 12))

    # 5. Security Implementation
    content.append(PageBreak())
    content.append(Paragraph("5. Security Implementation", heading_style))
    security_features = [
        ["Feature", "Implementation", "Status"],
        ["Rate Limiting", "Redis + Token Bucket", "Implemented"],
        ["API Keys", "JWT + Redis blacklist", "Implemented"],
        ["Input Validation", "Pydantic models", "Implemented"],
        ["Security Headers", "Helmet middleware", "Implemented"],
        ["Request Sanitization", "Custom middleware", "Implemented"]
    ]
    security_table = Table(security_features, colWidths=[2*inch, 2.5*inch, 1.5*inch])
    security_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    content.append(security_table)
    content.append(Spacer(1, 20))

    # 6. Monitoring and Logging
    content.append(Paragraph("6. Monitoring and Logging", heading_style))
    monitoring_config = """
    • System Metrics: Prometheus + Grafana
    • Error Tracking: Sentry
    • Log Aggregation: ELK Stack
    • Performance Monitoring: New Relic
    • Audit Logging: Custom solution with PostgreSQL
    """
    content.append(Paragraph(monitoring_config, styles["Normal"]))
    content.append(Spacer(1, 12))

    # 7. Integration Architecture
    content.append(PageBreak())
    content.append(Paragraph("7. Integration Architecture", heading_style))
    integration_details = """
    • Service Communication: gRPC + Protocol Buffers
    • Message Queue: RabbitMQ
    • Service Discovery: Consul
    • Load Balancing: NGINX
    • Circuit Breaker: Hystrix
    """
    content.append(Paragraph(integration_details, styles["Normal"]))
    content.append(Spacer(1, 12))

    # 8. Testing Requirements
    content.append(Paragraph("8. Testing Requirements", heading_style))
    test_requirements = [
        ["Test Type", "Tool", "Coverage Target"],
        ["Unit Tests", "pytest", "90%"],
        ["Integration Tests", "pytest-integration", "85%"],
        ["API Tests", "pytest + requests", "95%"],
        ["Security Tests", "OWASP ZAP", "100% critical"],
        ["Performance Tests", "k6 + Artillery", "P95 < 200ms"]
    ]
    test_table = Table(test_requirements, colWidths=[2*inch, 2*inch, 2*inch])
    test_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    content.append(test_table)

    # Build the PDF
    doc.build(content)

if __name__ == "__main__":
    create_technical_documentation_pdf() 