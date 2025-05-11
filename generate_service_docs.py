from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.units import inch

def create_table(data, widths, style_overrides=None):
    table = Table(data, colWidths=widths)
    style = [
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
    ]
    if style_overrides:
        style.extend(style_overrides)
    table.setStyle(TableStyle(style))
    return table

def create_auth_service_doc():
    doc = SimpleDocTemplate(
        "auth_service_documentation.pdf",
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=24, spaceAfter=30)
    heading_style = ParagraphStyle('CustomHeading', parent=styles['Heading2'], fontSize=18, spaceAfter=20)
    subheading_style = ParagraphStyle('CustomSubHeading', parent=styles['Heading3'], fontSize=14, spaceAfter=15)
    normal_style = styles["Normal"]
    
    content = []
    
    # Title
    content.append(Paragraph("Auth Service Documentation", title_style))
    content.append(Spacer(1, 20))
    
    # API Endpoints
    content.append(Paragraph("1. API Endpoints", heading_style))
    endpoints = [
        ["Endpoint", "Method", "Description", "Auth Required"],
        ["/api/v1/auth/register", "POST", "User registration", "No"],
        ["/api/v1/auth/login", "POST", "User authentication", "No"],
        ["/api/v1/auth/refresh", "POST", "Refresh access token", "Yes"],
        ["/api/v1/auth/logout", "POST", "User logout", "Yes"],
        ["/api/v1/auth/reset-password", "POST", "Password reset request", "No"],
        ["/api/v1/auth/verify-email", "GET", "Email verification", "No"]
    ]
    content.append(create_table(endpoints, [2*inch, inch, 2.5*inch, inch]))
    content.append(Spacer(1, 20))
    
    # Caching System
    content.append(Paragraph("2. Caching System", heading_style))
    cache_config = [
        ["Cache Type", "Implementation", "TTL", "Purpose"],
        ["Token Cache", "Redis", "15 minutes", "Active JWT tokens"],
        ["Session Cache", "Redis", "24 hours", "User sessions"],
        ["Rate Limit Cache", "Redis", "1 hour", "API rate limiting"]
    ]
    content.append(create_table(cache_config, [1.5*inch, 1.5*inch, inch, 2*inch]))
    content.append(Spacer(1, 20))
    
    # Rate Limiting
    content.append(Paragraph("3. Rate Limiting", heading_style))
    rate_limits = [
        ["Endpoint", "Limit", "Window", "Scope"],
        ["Login", "5 requests", "5 minutes", "IP Address"],
        ["Register", "3 requests", "10 minutes", "IP Address"],
        ["Reset Password", "2 requests", "15 minutes", "Email"],
        ["Token Refresh", "30 requests", "1 hour", "User ID"]
    ]
    content.append(create_table(rate_limits, [1.5*inch, 1.5*inch, 1.5*inch, 1.5*inch]))
    content.append(Spacer(1, 20))
    
    # Message Queue System
    content.append(Paragraph("4. Message Queue System", heading_style))
    queues = [
        ["Queue Name", "Type", "Purpose", "Retry Policy"],
        ["user.registered", "Topic", "New user notifications", "3x with exponential backoff"],
        ["password.reset", "Queue", "Password reset emails", "5x with 1-min delays"],
        ["auth.events", "Topic", "Auth audit logging", "No retry"]
    ]
    content.append(create_table(queues, [1.5*inch, inch, 2.5*inch, 2*inch]))
    content.append(Spacer(1, 20))
    
    doc.build(content)

def create_user_service_doc():
    doc = SimpleDocTemplate(
        "user_service_documentation.pdf",
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=24, spaceAfter=30)
    heading_style = ParagraphStyle('CustomHeading', parent=styles['Heading2'], fontSize=18, spaceAfter=20)
    subheading_style = ParagraphStyle('CustomSubHeading', parent=styles['Heading3'], fontSize=14, spaceAfter=15)
    
    content = []
    
    # Title
    content.append(Paragraph("User Service Documentation", title_style))
    content.append(Spacer(1, 20))
    
    # API Endpoints
    content.append(Paragraph("1. API Endpoints", heading_style))
    endpoints = [
        ["Endpoint", "Method", "Description", "Auth Required"],
        ["/api/v1/users", "GET", "List users", "Yes"],
        ["/api/v1/users/<id>", "GET", "Get user details", "Yes"],
        ["/api/v1/users/<id>", "PUT", "Update user", "Yes"],
        ["/api/v1/users/<id>", "DELETE", "Delete user", "Yes"],
        ["/api/v1/users/me", "GET", "Get own profile", "Yes"],
        ["/api/v1/users/me/preferences", "PUT", "Update preferences", "Yes"]
    ]
    content.append(create_table(endpoints, [2*inch, inch, 2.5*inch, inch]))
    content.append(Spacer(1, 20))
    
    # Caching System
    content.append(Paragraph("2. Caching System", heading_style))
    cache_config = [
        ["Cache Type", "Implementation", "TTL", "Purpose"],
        ["User Profile", "Redis", "15 minutes", "Frequently accessed profiles"],
        ["Preferences", "Redis", "30 minutes", "User preferences"],
        ["User List", "Redis", "5 minutes", "Paginated user lists"]
    ]
    content.append(create_table(cache_config, [1.5*inch, 1.5*inch, inch, 2*inch]))
    content.append(Spacer(1, 20))
    
    # Service Discovery
    content.append(Paragraph("3. Service Discovery", heading_style))
    discovery = [
        ["Service", "Health Check", "Load Balancing", "Instances"],
        ["User Service", "/health", "Round Robin", "3 min, 10 max"],
        ["Cache Service", "/health", "Least Connections", "2 min, 5 max"],
        ["DB Service", "/health", "Resource-based", "2 min, 3 max"]
    ]
    content.append(create_table(discovery, [1.5*inch, 1.5*inch, 1.5*inch, 1.5*inch]))
    content.append(Spacer(1, 20))
    
    doc.build(content)

def create_interaction_service_doc():
    doc = SimpleDocTemplate(
        "interaction_service_documentation.pdf",
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=24, spaceAfter=30)
    heading_style = ParagraphStyle('CustomHeading', parent=styles['Heading2'], fontSize=18, spaceAfter=20)
    subheading_style = ParagraphStyle('CustomSubHeading', parent=styles['Heading3'], fontSize=14, spaceAfter=15)
    
    content = []
    
    # Title
    content.append(Paragraph("Interaction Service Documentation", title_style))
    content.append(Spacer(1, 20))
    
    # API Endpoints
    content.append(Paragraph("1. API Endpoints", heading_style))
    endpoints = [
        ["Endpoint", "Method", "Description", "Auth Required"],
        ["/api/v1/interactions", "POST", "Create interaction", "Yes"],
        ["/api/v1/interactions/<id>", "GET", "Get interaction", "Yes"],
        ["/api/v1/interactions/<id>/prompts", "POST", "Add prompt", "Yes"],
        ["/api/v1/prompts/<id>/responses", "GET", "Get responses", "Yes"],
        ["/api/v1/interactions/history", "GET", "Get history", "Yes"]
    ]
    content.append(create_table(endpoints, [2*inch, inch, 2.5*inch, inch]))
    content.append(Spacer(1, 20))
    
    # Caching System
    content.append(Paragraph("2. Caching System", heading_style))
    cache_config = [
        ["Cache Type", "Implementation", "TTL", "Purpose"],
        ["Response Cache", "Redis", "1 hour", "AI responses"],
        ["History Cache", "Redis", "30 minutes", "User interaction history"],
        ["Prompt Cache", "Redis", "15 minutes", "Recent prompts"]
    ]
    content.append(create_table(cache_config, [1.5*inch, 1.5*inch, inch, 2*inch]))
    content.append(Spacer(1, 20))
    
    # Message Queue System
    content.append(Paragraph("3. Message Queue System", heading_style))
    queues = [
        ["Queue Name", "Type", "Purpose", "Retry Policy"],
        ["prompt.processing", "Queue", "Process new prompts", "3x with backoff"],
        ["response.generated", "Topic", "New AI responses", "No retry"],
        ["interaction.events", "Topic", "Interaction analytics", "2x with delay"]
    ]
    content.append(create_table(queues, [1.5*inch, inch, 2.5*inch, 2*inch]))
    content.append(Spacer(1, 20))
    
    # Rate Limiting
    content.append(Paragraph("4. Rate Limiting", heading_style))
    rate_limits = [
        ["Endpoint", "Limit", "Window", "Scope"],
        ["Create Interaction", "60 requests", "1 hour", "User ID"],
        ["Add Prompt", "10 requests", "1 minute", "User ID"],
        ["Get History", "30 requests", "5 minutes", "User ID"]
    ]
    content.append(create_table(rate_limits, [1.5*inch, 1.5*inch, 1.5*inch, 1.5*inch]))
    content.append(Spacer(1, 20))
    
    doc.build(content)

if __name__ == "__main__":
    create_auth_service_doc()
    create_user_service_doc()
    create_interaction_service_doc() 