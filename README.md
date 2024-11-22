# VPN Tunnel Management System

A Django-based web application for managing VPN tunnel requests, approvals, and automated firewall configurations. The system includes features for annual tunnel validation, multi-level approval workflows, and automated Palo Alto Networks firewall integration.

## Features

### VPN Tunnel Management
- Create and track VPN tunnel requests
- Support for multiple local and remote networks per tunnel
- Configure Phase 1 and Phase 2 IPSec settings
- Specify network details and business requirements

### Approval Workflow
- Network team approval process
- Security team approval process
- Request status tracking
- Automated firewall configuration upon approval

### Annual Validation
- Automated annual tunnel review process
- Email notifications for pending validations
- Business justification requirement
- Automatic expiration for non-validated tunnels

### Security Features
- Role-based access control
- Rate limiting with django-axes
- Brute force protection
- Secure session handling

### API Integration
- RESTful API for automation
- Automated Palo Alto firewall configuration
- Comprehensive API documentation

## Prerequisites

- Python 3.8+
- Django 5.0+
- Palo Alto Networks Firewall (for automated deployment)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/jbhoorasingh/vpn-manager
cd vpn-tunnel-manager
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
# Create .env file with the following variables
DJANGO_SECRET_KEY=your-secret-key
FIREWALL_HOST=your-firewall-host
FIREWALL_USERNAME=your-firewall-username
FIREWALL_PASSWORD=your-firewall-password
VPN_PSK=your-vpn-preshared-key
```

5. Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

6. Create superuser:
```bash
python manage.py createsuperuser
```

7. Start the development server:
```bash
python manage.py runserver
```

## Configuration

### Security Groups
Create the following groups in Django admin:
- Network_Admin: For network team approvals
- Security_Admin: For security team approvals

### Validation Schedule
Set up a cron job to run the validation check:
```bash
python manage.py check_tunnel_validations
```

Recommended schedule: Daily at midnight
```cron
0 0 * * * cd /path/to/project && /path/to/venv/bin/python manage.py check_tunnel_validations
```

## Usage

### Creating a VPN Tunnel Request
1. Log in to the application
2. Click "New Request"
3. Fill in:
   - Business unit details
   - Local and remote networks (multiple CIDRs supported)
   - IPSec settings
   - Business justification
4. Submit the request

### Approval Process
1. Network team reviews and approves network settings
2. Security team performs security review
3. Upon both approvals, configuration is automatically pushed to firewall

### Annual Validation
1. Service owners receive email notification 30 days before expiration
2. Access validation form via email link or web interface
3. Provide updated business justification
4. Submit validation to maintain tunnel

## API Documentation

### Authentication
All API endpoints require authentication. Use token-based authentication:
```bash
curl -H "Authorization: Token your-token" https://your-domain/api/tunnels/
```

### Endpoints
- GET /api/tunnels/ - List all tunnels
- POST /api/tunnels/ - Create new tunnel request
- GET /api/tunnels/{id}/ - Get tunnel details
- PUT /api/tunnels/{id}/ - Update tunnel
- POST /api/tunnels/{id}/validate/ - Submit validation

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## Security Considerations

- Keep environment variables secure
- Regularly update dependencies
- Monitor access logs
- Follow security best practices for production deployment
- Implement proper firewall access controls

## Support

For support:
- Open an issue in the repository
- Contact the development team
- Check documentation in the `/docs` directory

## License

This project is licensed under the MIT License - see the LICENSE file for details.