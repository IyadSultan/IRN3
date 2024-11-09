# Combined Python and HTML files
# Generated from directory: C:\Users\isult\Dropbox\AI\Projects\IRN3\users
# Total files found: 33



# Contents from: .\templates\users\base.html
<!DOCTYPE html>
<html lang="en">
<head>
    {% load static %}
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}iRN System{% endblock %}</title>

    <!-- CSS Dependencies -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/select2@4.1.0-rc.0/dist/css/select2.min.css" rel="stylesheet" />
    <link href="https://cdn.jsdelivr.net/npm/select2-bootstrap-5-theme@1.3.0/dist/select2-bootstrap-5-theme.min.css" rel="stylesheet" />
    <link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.10.24/css/dataTables.bootstrap4.min.css">
    <link rel="stylesheet" href="https://code.jquery.com/ui/1.12.1/themes/base/jquery-ui.css">

    <style>
        :root {
            --primary-color: #3498db;
            --secondary-color: #2c3e50;
            --background-color: #ecf0f1;
            --text-color: #34495e;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: var(--background-color);
            color: var(--text-color);
        }

        .navbar {
            background-color: var(--primary-color);
            box-shadow: 0 2px 4px rgba(0,0,0,.1);
        }

        .navbar-brand, .navbar-nav .nav-link {
            color: white !important;
        }

        .sidebar {
            background-color: white;
            box-shadow: 2px 0 5px rgba(0,0,0,.1);
            height: calc(100vh - 56px);
            position: fixed;
            top: 56px;
            left: 0;
            width: 250px;
            padding-top: 20px;
        }

        .sidebar .nav-link {
            color: var(--secondary-color);
            padding: 10px 20px;
            border-left: 3px solid transparent;
        }

        .sidebar .nav-link:hover, .sidebar .nav-link.active {
            background-color: rgba(52, 152, 219, 0.1);
            border-left-color: var(--primary-color);
        }

        .main-content {
            margin-left: 250px;
            padding: 20px;
        }

        .card {
            box-shadow: 0 4px 6px rgba(0,0,0,.1);
            border: none;
            border-radius: 8px;
        }

        /* Select2 Styles */
        .select2-container {
            width: 100% !important;
            margin-bottom: 10px;
        }
        
        .select2-selection--single {
            height: 38px !important;
            padding: 5px !important;
            border: 1px solid #ced4da !important;
            border-radius: 4px !important;
        }
        
        .select2-selection__rendered {
            line-height: 26px !important;
            padding-left: 8px !important;
        }
        
        .select2-selection__arrow {
            height: 36px !important;
        }
        
        .select2-selection--multiple {
            border: 1px solid #ced4da !important;
            min-height: 38px !important;
        }
        
        .select2-search__field {
            margin-top: 5px !important;
        }
        
        .select2-container .select2-selection--single .select2-selection__clear {
            margin-right: 25px;
            color: #999;
            font-size: 18px;
        }

        /* DataTables Custom Styles */
        .dataTables_wrapper .dataTables_length select {
            min-width: 60px;
            padding: 4px;
        }

        .dataTables_wrapper .dataTables_filter input {
            margin-left: 5px;
            padding: 4px;
        }

        .dataTables_wrapper .dataTables_paginate .paginate_button {
            padding: 0.3em 0.8em;
            margin: 0 2px;
        }

        .dataTables_wrapper .dataTables_info {
            padding-top: 10px;
        }

        /* Badge and Button Styles */
        .badge {
            padding: 0.4em 0.8em;
            font-size: 0.85em;
        }

        .badge-warning { background-color: #ffc107; color: #000; }
        .badge-info { background-color: #17a2b8; color: #fff; }
        .badge-success { background-color: #28a745; color: #fff; }
        .badge-primary { background-color: #007bff; color: #fff; }
        .badge-secondary { background-color: #6c757d; color: #fff; }

        .btn-sm {
            padding: 0.25rem 0.5rem;
            font-size: 0.875rem;
            line-height: 1.5;
            border-radius: 0.2rem;
        }

        /* Dropdown Styles */
        .dropdown-toggle::after {
            display: inline-block;
            margin-left: 0.255em;
            vertical-align: 0.255em;
            content: "";
            border-top: 0.3em solid;
            border-right: 0.3em solid transparent;
            border-bottom: 0;
            border-left: 0.3em solid transparent;
        }

        .dropdown-menu { margin-top: 0; }
        
        .dropdown-item:hover {
            background-color: rgba(52, 152, 219, 0.1);
        }
        
        .dropdown-item.text-danger:hover {
            background-color: rgba(220, 53, 69, 0.1);
        }

        /* Popup Styles */
        .custom-popup {
            display: none;
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            padding: 20px;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            z-index: 1000;
            min-width: 300px;
            max-width: 80%;
        }

        .popup-overlay {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.5);
            z-index: 999;
        }

        .popup-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
            padding-bottom: 10px;
            border-bottom: 1px solid #eee;
        }

        .popup-close {
            cursor: pointer;
            font-size: 20px;
            color: #666;
        }

        .popup-content {
            margin-bottom: 15px;
        }

        .popup-footer {
            text-align: right;
        }

        .popup-button {
            padding: 8px 16px;
            background: #007bff;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }

        .popup-button:hover {
            background: #0056b3;
        }

        /* Message Styles */
        .message-error {
            color: #721c24;
            background-color: #f8d7da;
            border: 1px solid #f5c6cb;
            padding: 10px;
            border-radius: 4px;
        }

        .message-success {
            color: #155724;
            background-color: #d4edda;
            border: 1px solid #c3e6cb;
            padding: 10px;
            border-radius: 4px;
        }

        .message-warning {
            color: #856404;
            background-color: #fff3cd;
            border: 1px solid #ffeeba;
            padding: 10px;
            border-radius: 4px;
        }

        .message-info {
            color: #004085;
            background-color: #cce5ff;
            border: 1px solid #b8daff;
            padding: 10px;
            border-radius: 4px;
        }
    </style>

    {% block page_specific_css %}{% endblock %}
</head>
<body>
    <!-- Navbar -->
    <nav class="navbar navbar-expand-lg navbar-dark">
        <div class="container-fluid">
            <a class="navbar-brand" href="#">iRN System</a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav" 
                    aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse justify-content-end" id="navbarNav">
                {% if user.is_authenticated %}
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item dropdown">
                        <button class="nav-link dropdown-toggle btn btn-link" 
                                id="navbarDropdown" 
                                data-bs-toggle="dropdown" 
                                aria-expanded="false"
                                style="text-decoration: none; border: none; background: none; color: white;">
                            <i class="fas fa-user me-1"></i>
                            {{ user.get_full_name|default:user.username }}
                        </button>
                        <ul class="dropdown-menu dropdown-menu-end shadow" aria-labelledby="navbarDropdown">
                            <li>
                                <a class="dropdown-item" href="{% url 'users:profile' %}">
                                    <i class="fas fa-tachometer-alt me-2"></i>Profile
                                </a>
                            </li>
                            <li><hr class="dropdown-divider"></li>
                            <li>
                                <form method="post" action="{% url 'users:logout' %}" class="d-inline w-100">
                                    {% csrf_token %}
                                    <button type="submit" class="dropdown-item text-danger">
                                        <i class="fas fa-sign-out-alt me-2"></i>Logout
                                    </button>
                                </form>
                            </li>
                        </ul>
                    </li>
                </ul>
                {% else %}
                <ul class="navbar-nav">
                    <li class="nav-item">
                        <a class="nav-link" href="{% url 'users:register' %}">
                            <i class="fas fa-user-plus me-1"></i> Register
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="{% url 'users:login' %}">
                            <i class="fas fa-sign-in-alt me-1"></i> Login
                        </a>
                    </li>
                </ul>
                {% endif %}
            </div>
        </div>
    </nav>

    <!-- Main Content -->
    <div class="container-fluid">
        <div class="row">
            <!-- Sidebar -->
            <nav class="col-md-3 col-lg-2 d-md-block sidebar collapse">
                <div class="position-sticky">
                    <ul class="nav flex-column">
                        <li class="nav-item">
                            <a class="nav-link active" href="{% url 'submission:dashboard' %}">
                                <i class="fas fa-tachometer-alt"></i> Dashboard
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="{% url 'submission:start_submission' %}">
                                <i class="fas fa-plus-circle"></i> Start New Submission
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="{% url 'review:review_dashboard' %}">
                                <i class="fas fa-clipboard-check"></i> Review Dashboard
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="{% url 'messaging:inbox' %}">
                                <i class="fas fa-inbox"></i> Inbox
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="{% url 'messaging:sent_messages' %}">
                                <i class="fas fa-paper-plane"></i> Sent Messages
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="{% url 'messaging:archived_messages' %}">
                                <i class="fas fa-archive"></i> Archived Messages
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="{% url 'messaging:compose_message' %}">
                                <i class="fas fa-pen"></i> Compose Message
                            </a>
                        </li>
                    </ul>
                </div>
            </nav>

            <!-- Content Area -->
            <main class="col-md-9 ms-sm-auto col-lg-10 px-md-4 main-content">
                {% block content %}{% endblock %}
            </main>
        </div>
    </div>

    <!-- Popup Overlay and Content -->
    <div id="popupOverlay" class="popup-overlay"></div>
    <div id="customPopup" class="custom-popup">
        <div class="popup-header">
            <h4>Notification</h4>
            <span class="popup-close" onclick="closePopup()">&times;</span>
        </div>
        <div class="popup-content" id="popupContent">
        </div>
        <div class="popup-footer">
            <button class="popup-button" onclick="closePopup()">OK</button>
        </div>
    </div>

    <!-- JavaScript Dependencies -->
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <script src="https://code.jquery.com/ui/1.12.1/jquery-ui.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/select2@4.1.0-rc.0/dist/js/select2.min.js"></script>
    <script src="https://cdn.datatables.net/1.10.24/js/jquery.dataTables.min.js"></script>
    <script src="https://cdn.datatables.net/1.10.24/js/dataTables.bootstrap4.min.js"></script>

    <!-- Base JavaScript -->
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            // Enable all dropdowns
            var dropdownElementList = [].slice.call(document.querySelectorAll('.dropdown-toggle'));
            var dropdownList = dropdownElementList.map(function (dropdownToggleEl) {
                return new bootstrap.Dropdown(dropdownToggleEl);
            });

            // Add hover effect for dropdown
            $('.nav-item.dropdown').hover(
                function() {
                    $(this).find('.dropdown-toggle').dropdown('show');
                },
                function() {
                    $(this).find('.dropdown-toggle').dropdown('hide');
                }
            );

            // Initialize popup for Django messages
            const messages = [
                {% for message in messages %}
                    {
                        text: "{{ message }}",
                        tags: "{{ message.tags }}"
                    },
                {% endfor %}
            ];
            
            if (messages.length > 0) {
                messages.forEach(function(message) {
                    showPopup(message.text, message.tags || 'info');
                });
            }
        });

        // Global popup functions
        function showPopup(message, type = 'info') {
            const popup = document.getElementById('customPopup');
            const overlay = document.getElementById('popupOverlay');
            const content = document.getElementById('popupContent');
            
            const messageElement = document.createElement('div');
            messageElement.className = `message-${type}`;
            messageElement.textContent = message;
            
            content.innerHTML = '';
            content.appendChild(messageElement);
            
            popup.style.display = 'block';
            overlay.style.display = 'block';
            
            document.addEventListener('keydown', handleEscapeKey);
        }
        
        function closePopup() {
            const popup = document.getElementById('customPopup');
            const overlay = document.getElementById('popupOverlay');
            popup.style.display = 'none';
            overlay.style.display = 'none';
            
            document.removeEventListener('keydown', handleEscapeKey);
        }
        
        function handleEscapeKey(e) {
            if (e.key === 'Escape') {
                closePopup();
            }
        }
        
        // Click outside to close popup
        document.getElementById('popupOverlay').addEventListener('click', closePopup);
    </script>

    {% block page_specific_js %}{% endblock %}
</body>
</html>

# Contents from: .\templates\users\login.html
{% extends 'users/base.html' %}
{% load crispy_forms_tags %}
{% block title %}Login{% endblock %}
{% block content %}
<div class="container mt-4">
    <div class="row">
        <div class="col-md-6 offset-md-3">
            <div class="card">
                <div class="card-header">
                    <h2>Login</h2>
                </div>
                <div class="card-body">
                    <form method="post">
                        {% csrf_token %}
                        {{ form|crispy }}
                        <div class="d-flex justify-content-between align-items-center mt-3">
                            <button type="submit" class="btn btn-primary">Login</button>
                            <a href="{% url 'users:password_reset' %}" class="btn btn-outline-secondary">Forgot Password?</a>
                        </div>
                        <div class="text-center mt-3">
                            <a href="{% url 'users:register' %}" class="btn btn-link">
                                Don't have an account? Register here
                            </a>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}


# Contents from: .\templates\users\password_reset.html
{# templates/users/password_reset.html #}
{% extends 'users/base.html' %}
{% load crispy_forms_tags %}

{% block title %}Reset Password{% endblock %}

{% block content %}
<div class="container mt-4">
    <div class="row">
        <div class="col-md-6 offset-md-3">
            <div class="card">
                <div class="card-header">
                    <h2>Reset Password</h2>
                </div>
                <div class="card-body">
                    <p>Enter your email address below, and we'll send you instructions for setting a new password.</p>
                    <form method="POST">
                        {% csrf_token %}
                        {{ form|crispy }}
                        <button type="submit" class="btn btn-primary">Reset Password</button>
                        <a href="{% url 'users:login' %}" class="btn btn-link">Back to Login</a>
                    </form>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}

# Contents from: .\templates\users\password_reset_complete.html
{# templates/users/password_reset_complete.html #}
{% extends 'users/base.html' %}

{% block title %}Password Reset Complete{% endblock %}

{% block content %}
<div class="container mt-4">
    <div class="row">
        <div class="col-md-6 offset-md-3">
            <div class="card">
                <div class="card-header">
                    <h2>Password Reset Complete</h2>
                </div>
                <div class="card-body">
                    <div class="alert alert-success">
                        <p>Your password has been successfully reset.</p>
                    </div>
                    <a href="{% url 'users:login' %}" class="btn btn-primary">Login with New Password</a>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}

# Contents from: .\templates\users\password_reset_confirm.html
{# templates/users/password_reset_confirm.html #}
{% extends 'users/base.html' %}
{% load crispy_forms_tags %}

{% block title %}Set New Password{% endblock %}

{% block content %}
<div class="container mt-4">
    <div class="row">
        <div class="col-md-6 offset-md-3">
            <div class="card">
                <div class="card-header">
                    <h2>Set New Password</h2>
                </div>
                <div class="card-body">
                    {% if validlink %}
                        <p>Please enter your new password twice to verify.</p>
                        <form method="POST">
                            {% csrf_token %}
                            {{ form|crispy }}
                            <button type="submit" class="btn btn-primary">Change Password</button>
                        </form>
                    {% else %}
                        <p>This password reset link is invalid or has expired. Please request a new password reset.</p>
                        <a href="{% url 'users:password_reset' %}" class="btn btn-primary">Request New Reset Link</a>
                    {% endif %}
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}

# Contents from: .\templates\users\password_reset_done.html
{# templates/users/password_reset_done.html #}
{% extends 'users/base.html' %}

{% block title %}Password Reset Sent{% endblock %}

{% block content %}
<div class="container mt-4">
    <div class="row">
        <div class="col-md-6 offset-md-3">
            <div class="card">
                <div class="card-header">
                    <h2>Password Reset Email Sent</h2>
                </div>
                <div class="card-body">
                    <p>We've sent you an email with instructions for setting your new password. You should receive it shortly.</p>
                    <p>If you don't receive an email, please verify that you entered the correct email address and check your spam folder.</p>
                    <a href="{% url 'users:login' %}" class="btn btn-primary">Return to Login</a>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}

# Contents from: .\templates\users\password_reset_email.html
{# templates/users/password_reset_email.html #}
{% autoescape off %}
Hello,

You are receiving this email because you requested a password reset for your account at iRN System.

Please click the following link to reset your password:

{{ protocol }}://{{ domain }}{% url 'users:password_reset_confirm' uidb64=uid token=token %}

If you did not request this reset, please ignore this email.

Best regards,
iRN System Team
{% endautoescape %}

# Contents from: .\templates\users\profile.html
{% extends 'users/base.html' %}
{% load crispy_forms_tags %}

{% block title %}Profile - {{ user.get_full_name|default:user.username }}{% endblock %}

{% block content %}
<div class="container mt-4">
    <div class="row">
        <div class="col-md-8 offset-md-2">
            <div class="card">
                <div class="card-header">
                    <h2>User Profile</h2>
                </div>
                <div class="card-body">
                    {% if messages %}
                    <div class="messages">
                        {% for message in messages %}
                        <div class="alert alert-{{ message.tags }}">
                            {{ message }}
                        </div>
                        {% endfor %}
                    </div>
                    {% endif %}

                    <form method="POST" enctype="multipart/form-data" novalidate>
                        {% csrf_token %}
                        
                        <div class="card mb-4">
                            <div class="card-header">
                                <h4 class="mb-0">Account Information</h4>
                            </div>
                            <div class="card-body">
                                {{ user_form|crispy }}
                                
                                <!-- Password Change Section -->
                                <div class="mb-3">
                                    <h5>Change Password</h5>
                                    {{ password_form|crispy }}
                                </div>
                            </div>
                        </div>

                        <div class="card mb-4">
                            <div class="card-header">
                                <h4 class="mb-0">Profile Information</h4>
                            </div>
                            <div class="card-body">
                                {{ profile_form|crispy }}
                            </div>
                        </div>
                        
                        <div class="mb-3 row">
                            <div class="col-sm-9 offset-sm-3">
                                <button type="submit" class="btn btn-primary">Save Changes</button>
                                <a href="{% url 'users:view_documents' %}" class="btn btn-info">View Document History</a>
                            </div>
                        </div>
                    </form>

                    <hr>

                    <h3 class="mt-4">Required Documents Status</h3>
                    
                    <div class="table-responsive">
                        <table class="table">
                            <thead>
                                <tr>
                                    <th>Document Type</th>
                                    <th>Status</th>
                                    <th>Action</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td>GCP Certificate</td>
                                    <td>
                                        {% if user.userprofile.has_valid_gcp %}
                                            <span class="badge bg-success">Valid</span>
                                        {% else %}
                                            <span class="badge bg-danger">Expired/Missing</span>
                                        {% endif %}
                                    </td>
                                    <td><a href="{% url 'users:upload_document' %}" class="btn btn-sm btn-primary">Upload</a></td>
                                </tr>
                                <tr>
                                    <td>QRC Certificate</td>
                                    <td>
                                        {% if user.userprofile.has_qrc %}
                                            <span class="badge bg-success">Valid</span>
                                        {% else %}
                                            <span class="badge bg-danger">Expired/Missing</span>
                                        {% endif %}
                                    </td>
                                    <td><a href="{% url 'users:upload_document' %}" class="btn btn-sm btn-primary">Upload</a></td>
                                </tr>
                                <tr>
                                    <td>CTC Certificate</td>
                                    <td>
                                        {% if user.userprofile.has_ctc %}
                                            <span class="badge bg-success">Valid</span>
                                        {% else %}
                                            <span class="badge bg-danger">Expired/Missing</span>
                                        {% endif %}
                                    </td>
                                    <td><a href="{% url 'users:upload_document' %}" class="btn btn-sm btn-primary">Upload</a></td>
                                </tr>
                                <tr>
                                    <td>CV</td>
                                    <td>
                                        {% if user.userprofile.has_cv %}
                                            <span class="badge bg-success">Valid</span>
                                        {% else %}
                                            <span class="badge bg-danger">Missing</span>
                                        {% endif %}
                                    </td>
                                    <td><a href="{% url 'users:upload_document' %}" class="btn btn-sm btn-primary">Upload</a></td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}

# Contents from: .\templates\users\register.html
{% extends 'users/base.html' %}
{% load crispy_forms_tags %}

{% block title %}Register{% endblock %}

{% block content %}
<div class="container mt-4">
    <div class="row">
        <div class="col-md-8 offset-md-2">
            <div class="card">
                <div class="card-header">
                    <h2>Register</h2>
                </div>
                <div class="card-body">
                    {% if messages %}
                    <div class="messages">
                        {% for message in messages %}
                        <div class="alert alert-{{ message.tags }}">
                            {{ message }}
                        </div>
                        {% endfor %}
                    </div>
                    {% endif %}
                    
                    <form method="post" enctype="multipart/form-data" novalidate>
                        {% csrf_token %}
                        {{ user_form|crispy }}
                        {{ profile_form|crispy }}
                        <div class="alert alert-info">
                            <small>{{ usage_agreement }}</small>
                        </div>
                        <div class="d-grid gap-2">
                            <button type="submit" class="btn btn-primary">
                                <i class="fas fa-user-plus me-2"></i>Register
                            </button>
                            <a href="{% url 'users:login' %}" class="btn btn-link text-center">
                                Already have an account? Login here
                            </a>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}


# Contents from: .\templates\users\upload_document.html
{% extends 'users/base.html' %}
{% load crispy_forms_tags %}
{% block title %}Upload Document{% endblock %}
{% block content %}
<h1>Upload Document</h1>
<form method="post" enctype="multipart/form-data">
    {% csrf_token %}
    {{ form|crispy }}
    <button type="submit">Upload</button>
</form>
<p>Or <a href="https://khcc.jo">Skip and go to khcc.jo</a></p>
{% endblock %}


# Contents from: .\templates\users\view_documents.html
{% extends 'users/base.html' %}
{% load crispy_forms_tags %}
{% block title %}My Documents{% endblock %}
{% block content %}
<h1>My Documents</h1>
{% if documents %}
    <table class="table table-striped">
        <thead>
            <tr>
                <th>Document Type</th>
                <th>Uploaded On</th>
                <th>Issued On</th>
                <th>Expires On</th>
                <th>Comments</th>
            </tr>
        </thead>
        <tbody>
        {% for doc_info in documents %}
            <tr {% if doc_info.days_until_expiry < 30 and doc_info.days_until_expiry >= 0 %}class="text-danger"{% endif %}>
                <td>
                    <a href="{% url 'users:display_document' doc_info.document.id %}" class="document-link" data-document-type="{{ doc_info.document.get_document_type_display }}" data-file-extension="{{ doc_info.file_extension }}" {% if doc_info.file_extension == '.pdf' %}target="_blank"{% endif %}>
                        {% if doc_info.document.document_type == 'Other' %}
                            {{ doc_info.document.other_document_name }}
                        {% else %}
                            {{ doc_info.document.get_document_type_display }}
                        {% endif %}
                    </a>
                </td>
                <td>{{ doc_info.document.uploaded_at|date:"F d, Y" }}</td>
                <td>{{ doc_info.document.issue_date|date:"F d, Y" }}</td>
                <td>{{ doc_info.document.expiry_date|date:"F d, Y" }}</td>
                <td>
                    {% if doc_info.days_until_expiry is not None %}
                        Days until expiry: {{ doc_info.days_until_expiry }}
                    {% endif %}
                </td>
            </tr>
        {% endfor %}
        </tbody>
    </table>

    <!-- Modal for image preview -->
    <div class="modal fade" id="imageModal" tabindex="-1" role="dialog" aria-labelledby="imageModalLabel" aria-hidden="true">
        <div class="modal-dialog modal-lg" role="document">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title" id="imageModalLabel"></h5>
                    <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                        <span aria-hidden="true">&times;</span>
                    </button>
                </div>
                <div class="modal-body">
                    <img id="imageFrame" style="width: 100%;" />
                </div>
            </div>
        </div>
    </div>

    <script>
        $(document).ready(function() {
            $('.document-link').click(function(e) {
                var fileExtension = $(this).data('file-extension');
                var documentType = $(this).data('document-type');
                
                if (fileExtension === '.pdf') {
                    // For PDF files, let the browser open it in a new tab
                    return true;
                } else if (['.jpg', '.jpeg', '.png', '.gif'].includes(fileExtension)) {
                    // For image files, show in modal
                    e.preventDefault();
                    var documentUrl = $(this).attr('href');
                    $('#imageModalLabel').text(documentType);
                    $('#imageFrame').attr('src', documentUrl);
                    $('#imageModal').modal('show');
                } else {
                    // For other file types, let the browser handle it
                    return true;
                }
            });
        });
    </script>
{% else %}
    <p>You haven't uploaded any documents yet.</p>
{% endif %}
<div class="mt-3">
    <a href="{% url 'users:upload_document' %}" class="btn btn-primary">Upload New Document</a>
    <a href="{% url 'users:profile' %}" class="btn btn-secondary">Back to Profile</a>
</div>
{% endblock %}


# Contents from: .\__init__.py
# This file should be empty

default_app_config = 'users.apps.UsersConfig'


# Contents from: .\admin.py
# users/admin.py

from django.contrib import admin
from django.contrib.auth.models import Group
from .models import (
    UserProfile,
    Document,
    Role,
)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'institution', 'role', 'is_approved')
    list_filter = ('is_approved', 'role')
    actions = ['approve_users']
    filter_horizontal = ('groups',)

    def approve_users(self, request, queryset):
        queryset.update(is_approved=True)
    approve_users.short_description = "Approve selected users"

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('user', 'document_type', 'issue_date', 'expiry_date')
    list_filter = ('document_type',)
    search_fields = ('user__username', 'user__email')

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')
    search_fields = ('name', 'description')
    ordering = ('name',)





# Contents from: .\apps.py
from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = 'users'

    def ready(self):
        import users.signals


# Contents from: .\backends.py
# users/backends.py

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

class EmailOrUsernameModelBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        try:
            user = UserModel.objects.get(email=username)
        except UserModel.DoesNotExist:
            try:
                user = UserModel.objects.get(username=username)
            except UserModel.DoesNotExist:
                return None

        if user.check_password(password):
            return user
        return None


# Contents from: .\combine.py
import os

def get_files_recursively(directory, extensions):
    """
    Recursively get all files with specified extensions from directory and subdirectories
    """
    file_list = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                file_list.append(os.path.join(root, file))
    return file_list

def combine_files(output_file, file_list):
    """
    Combine contents of all files in file_list into output_file
    """
    with open(output_file, 'a', encoding='utf-8') as outfile:
        for fname in file_list:
            # Add a header comment to show which file's contents follow
            outfile.write(f"\n\n# Contents from: {fname}\n")
            try:
                with open(fname, 'r', encoding='utf-8') as infile:
                    for line in infile:
                        outfile.write(line)
            except Exception as e:
                outfile.write(f"# Error reading file {fname}: {str(e)}\n")

def main():
    # Define the base directory (current directory in this case)
    base_directory = "."
    output_file = 'combined.py'
    extensions = ('.py', '.html')

    # Remove output file if it exists
    if os.path.exists(output_file):
        try:
            os.remove(output_file)
        except Exception as e:
            print(f"Error removing existing {output_file}: {str(e)}")
            return

    # Get all files recursively
    all_files = get_files_recursively(base_directory, extensions)
    
    # Sort files by extension and then by name
    all_files.sort(key=lambda x: (os.path.splitext(x)[1], x))

    # Add a header to the output file
    with open(output_file, 'w', encoding='utf-8') as outfile:
        outfile.write("# Combined Python and HTML files\n")
        outfile.write(f"# Generated from directory: {os.path.abspath(base_directory)}\n")
        outfile.write(f"# Total files found: {len(all_files)}\n\n")

    # Combine all files
    combine_files(output_file, all_files)
    
    print(f"Successfully combined {len(all_files)} files into {output_file}")
    print("Files processed:")
    for file in all_files:
        print(f"  - {file}")

if __name__ == "__main__":
    main()

# Contents from: .\forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from .models import UserProfile, Document, validate_full_name
import logging

logger = logging.getLogger('IRN.users')

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        validators=[EmailValidator()],
        help_text='Required. Enter a valid email address.'
    )
    
    full_name = forms.CharField(
        max_length=255,
        required=True,
        help_text='Enter your full name (First and Last name)'
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'full_name', 'password1', 'password2')

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username__iexact=username).exists():
            raise ValidationError("This username is already taken.")
        return username.lower()

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("This email address is already registered.")
        return email.lower()

    def clean_full_name(self):
        full_name = self.cleaned_data.get('full_name')
        if full_name:
            try:
                validate_full_name(full_name)
            except ValidationError as e:
                logger.warning(f"Full name validation failed: {str(e)}")
                raise forms.ValidationError(str(e))
        return full_name.title()  # Capitalize first letter of each word

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        
        # Split and save full name
        full_name_parts = self.cleaned_data['full_name'].split()
        user.first_name = full_name_parts[0]
        user.last_name = ' '.join(full_name_parts[1:])
        
        if commit:
            user.save()
        return user

class UserProfileForm(forms.ModelForm):
    mobile = forms.CharField(
        required=False,
        max_length=20,
        initial='',
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Enter your mobile number (optional)'
            }
        )
    )

    class Meta:
        model = UserProfile
        fields = [
            'institution',
            'mobile',
            'khcc_employee_number',
            'title',
            'role',
            'photo',
        ]
        exclude = ['user', 'is_approved']
        
        widgets = {
            'institution': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter your institution name'
                }
            ),
            'khcc_employee_number': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter your KHCC employee number (if applicable)'
                }
            ),
            'title': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter your title'
                }
            ),
            'role': forms.Select(
                attrs={
                    'class': 'form-control'
                }
            ),
            'photo': forms.FileInput(
                attrs={
                    'class': 'form-control'
                }
            ),
        }

        help_texts = {
            'institution': 'Your affiliated institution',
            'mobile': 'Your mobile number in international format (e.g., +962xxxxxxxxx)',
            'khcc_employee_number': 'Required for KHCC employees only',
            'title': 'Your professional title',
            'role': 'Select your role in the system',
            'photo': 'Upload a professional photo (JPEG or PNG, max 5MB)',
        }

    def clean_mobile(self):
        mobile = self.cleaned_data.get('mobile')
        if not mobile:
            return ''
        # Remove any spaces or special characters
        mobile = ''.join(filter(str.isdigit, mobile))
        if len(mobile) < 10:
            raise ValidationError("Mobile number must be at least 10 digits.")
        # Format the number with international code if not present
        if not mobile.startswith('962'):
            mobile = f'962{mobile}'
        # Format the number with + sign
        mobile = f'+{mobile}'
        return mobile

    def clean_khcc_employee_number(self):
        emp_number = self.cleaned_data.get('khcc_employee_number')
        role = self.cleaned_data.get('role')
        
        if role == 'KHCC investigator' and not emp_number:
            raise ValidationError("Employee number is required for KHCC investigators.")
            
        if emp_number:
            # Remove any spaces or special characters
            emp_number = ''.join(filter(str.isalnum, emp_number))
            if len(emp_number) < 3:
                raise ValidationError("Employee number must be at least 3 characters.")
            # Convert to uppercase# Convert to uppercase
            emp_number = emp_number.upper()
        return emp_number

    def clean_photo(self):
        photo = self.cleaned_data.get('photo')
        if photo:
            # Check file size
            if photo.size > 5 * 1024 * 1024:  # 5MB limit
                raise ValidationError("Photo size cannot exceed 5MB.")
            
            # Check file type
            file_type = photo.content_type.split('/')[-1].lower()
            if file_type not in ['jpeg', 'jpg', 'png']:
                raise ValidationError("Only JPEG and PNG images are allowed.")
            
            # Check image dimensions
            from PIL import Image
            try:
                img = Image.open(photo)
                width, height = img.size
                if width > 2000 or height > 2000:
                    raise ValidationError("Image dimensions should not exceed 2000x2000 pixels.")
                if width < 100 or height < 100:
                    raise ValidationError("Image dimensions should be at least 100x100 pixels.")
            except Exception as e:
                raise ValidationError("Invalid image file. Please upload a valid JPEG or PNG file.")
        return photo

    def clean_institution(self):
        institution = self.cleaned_data.get('institution')
        if institution:
            # Remove extra spaces and capitalize properly
            institution = ' '.join(institution.split())
            institution = institution.title()
        return institution

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if title:
            # Remove extra spaces and capitalize properly
            title = ' '.join(title.split())
            title = title.title()
        return title

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        emp_number = cleaned_data.get('khcc_employee_number')
        institution = cleaned_data.get('institution')

        # Additional role-specific validation
        if role == 'KHCC investigator':
            if institution and institution.lower() != 'king hussein cancer center':
                raise ValidationError({
                    'institution': 'KHCC investigators must be from King Hussein Cancer Center'
                })
            if not emp_number:
                raise ValidationError({
                    'khcc_employee_number': 'Employee number is required for KHCC investigators'
                })

        return cleaned_data

    def save(self, user=None, commit=True):
        profile = super().save(commit=False)
        if user:
            # Try to get existing profile or create new one
            profile, created = UserProfile.objects.get_or_create(user=user)
            # Update the fields from the form
            profile.institution = self.cleaned_data.get('institution')
            profile.mobile = self.cleaned_data.get('mobile', '')
            profile.khcc_employee_number = self.cleaned_data.get('khcc_employee_number')
            profile.title = self.cleaned_data.get('title')
            profile.role = self.cleaned_data.get('role')
            if self.cleaned_data.get('photo'):
                profile.photo = self.cleaned_data.get('photo')
            
            if commit:
                try:
                    profile.save()
                except Exception as e:
                    logger.error(f"Error saving profile: {str(e)}")
                    raise
        return profile

class LoginForm(forms.Form):
    username_or_email = forms.CharField(
        label="Username or Email",
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Enter your username or email'
            }
        )
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Enter your password'
            }
        )
    )

    def clean(self):
        cleaned_data = super().clean()
        username_or_email = cleaned_data.get('username_or_email')
        password = cleaned_data.get('password')

        if not username_or_email or not password:
            raise ValidationError("Both username/email and password are required.")

        return cleaned_data

class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['document_type', 'other_document_name', 'issue_date', 'expiry_date', 'file']
        widgets = {
            'document_type': forms.Select(
                attrs={
                    'class': 'form-control',
                    'onchange': 'toggleOtherDocumentName(this.value)'
                }
            ),
            'other_document_name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter the document name'
                }
            ),
            'issue_date': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'form-control'
                }
            ),
            'expiry_date': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'form-control'
                }
            ),
            'file': forms.FileInput(
                attrs={
                    'class': 'form-control'
                }
            ),
        }

        help_texts = {
            'document_type': 'Select the type of document you are uploading',
            'other_document_name': 'If "Other" is selected, specify the document name',
            'issue_date': 'Date when the document was issued',
            'expiry_date': 'Date when the document expires (if applicable)',
            'file': 'Upload your document (PDF, DOC, DOCX, JPG, JPEG, PNG)'
        }

    def clean(self):
        cleaned_data = super().clean()
        document_type = cleaned_data.get('document_type')
        other_document_name = cleaned_data.get('other_document_name')
        issue_date = cleaned_data.get('issue_date')
        expiry_date = cleaned_data.get('expiry_date')
        file = cleaned_data.get('file')

        if document_type == 'Other' and not other_document_name:
            self.add_error('other_document_name', 
                "Please specify the document name for 'Other' document type.")

        if issue_date and expiry_date and issue_date > expiry_date:
            self.add_error('expiry_date', 
                "Expiry date cannot be earlier than issue date.")

        if file:
            # Check file size (10MB limit)
            if file.size > 10 * 1024 * 1024:
                self.add_error('file', "File size cannot exceed 10MB.")
            
            # Check file extension
            allowed_extensions = ['.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png']
            file_ext = f".{file.name.split('.')[-1].lower()}"
            if file_ext not in allowed_extensions:
                self.add_error('file', 
                    f"Invalid file type. Allowed types are: {', '.join(allowed_extensions)}")

        return cleaned_data

    def save(self, commit=True):
        document = super().save(commit=False)
        if commit:
            try:
                document.save()
            except Exception as e:
                logger.error(f"Error saving document: {str(e)}")
                raise
        return document
    
from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User

class UserEditForm(forms.ModelForm):
    """Form for editing user account information"""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    
    username = forms.CharField(
        disabled=True,  # Username cannot be changed
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    first_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    last_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].help_text = 'Username cannot be changed'

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.exclude(pk=self.instance.pk).filter(email__iexact=email).exists():
            raise forms.ValidationError('A user with this email already exists.')
        return email.lower()

class CustomPasswordChangeForm(PasswordChangeForm):
    """Custom password change form with bootstrap styles"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

# Contents from: .\management\commands\setup_system_user.py
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from users.models import UserProfile
from django.db import transaction

class Command(BaseCommand):
    help = 'Creates or updates the system user and its profile'

    def handle(self, *args, **options):
        try:
            with transaction.atomic():
                # Get or create system user
                system_user, user_created = User.objects.get_or_create(
                    username='system',
                    defaults={
                        'first_name': 'System',
                        'last_name': 'User',
                        'email': 'system@irn.com',
                        'is_active': False
                    }
                )

                # Get or create user profile
                profile, profile_created = UserProfile.objects.get_or_create(
                    user=system_user,
                    defaults={
                        'role': 'system'
                    }
                )

                if user_created:
                    self.stdout.write(self.style.SUCCESS('Successfully created system user'))
                else:
                    self.stdout.write(self.style.SUCCESS('System user already exists'))

                if profile_created:
                    self.stdout.write(self.style.SUCCESS('Successfully created system user profile'))
                else:
                    self.stdout.write(self.style.SUCCESS('System user profile already exists'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}')) 

# Contents from: .\migrations\0001_initial.py
# Generated by Django 5.1.2 on 2024-11-04 01:29

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Document",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "document_type",
                    models.CharField(
                        choices=[
                            ("GCP", "Good Clinical Practice Certificate"),
                            ("QRC", "Qualitative Record Certificate"),
                            ("CTC", "Consent Training Certificate"),
                            ("Other", "Other"),
                        ],
                        max_length=20,
                    ),
                ),
                (
                    "other_document_name",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                ("issue_date", models.DateField(blank=True, null=True)),
                ("expiry_date", models.DateField(blank=True, null=True)),
                ("file", models.FileField(upload_to="documents/")),
                ("uploaded_at", models.DateTimeField(auto_now_add=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="documents",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="SystemSettings",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "system_email",
                    models.EmailField(
                        default="aidi@khcc.jo",
                        help_text="System email address used for automated messages",
                        max_length=254,
                    ),
                ),
                (
                    "system_user",
                    models.ForeignKey(
                        blank=True,
                        help_text="User account to be used for system messages",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="system_settings",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "System Settings",
                "verbose_name_plural": "System Settings",
            },
        ),
        migrations.CreateModel(
            name="UserProfile",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "institution",
                    models.CharField(
                        default="King Hussein Cancer Center", max_length=255
                    ),
                ),
                ("mobile", models.CharField(max_length=20)),
                (
                    "khcc_employee_number",
                    models.CharField(blank=True, max_length=20, null=True),
                ),
                ("title", models.CharField(max_length=255)),
                (
                    "role",
                    models.CharField(
                        choices=[
                            ("KHCC investigator", "KHCC investigator"),
                            ("Non-KHCC investigator", "Non-KHCC investigator"),
                            (
                                "Research Assistant/Coordinator",
                                "Research Assistant/Coordinator",
                            ),
                            ("OSAR head", "OSAR head"),
                            ("OSAR", "OSAR"),
                            ("IRB chair", "IRB chair"),
                            ("RC coordinator", "RC coordinator"),
                            ("IRB member", "IRB member"),
                            ("RC chair", "RC chair"),
                            ("RC member", "RC member"),
                            ("RC coordinator", "RC coordinator"),
                            ("AHARPP Head", "AHARPP Head"),
                            ("System administrator", "System administrator"),
                            ("CEO", "CEO"),
                            ("CMO", "CMO"),
                            ("AIDI Head", "AIDI Head"),
                            ("Grant Management Officer", "Grant Management Officer"),
                        ],
                        max_length=50,
                    ),
                ),
                (
                    "photo",
                    models.ImageField(blank=True, null=True, upload_to="photos/"),
                ),
                ("is_approved", models.BooleanField(default=False)),
                (
                    "full_name",
                    models.CharField(
                        default="",
                        help_text="Full name (at least three names required)",
                        max_length=255,
                    ),
                ),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]


# Contents from: .\migrations\0002_role.py
# Generated by Django 5.1.2 on 2024-11-04 22:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Role",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255, unique=True)),
                ("description", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "ordering": ["name"],
            },
        ),
    ]


# Contents from: .\migrations\0003_group_alter_document_document_type_and_more.py
# Generated by Django 5.1.2 on 2024-11-05 06:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0002_role"),
    ]

    operations = [
        migrations.CreateModel(
            name="Group",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=50, unique=True)),
            ],
        ),
        migrations.AlterField(
            model_name="document",
            name="document_type",
            field=models.CharField(
                choices=[
                    ("GCP", "Good Clinical Practice Certificate"),
                    ("QRC", "Qualitative Record Certificate"),
                    ("CTC", "Consent Training Certificate"),
                    ("CV", "Curriculum Vitae"),
                    ("Other", "Other"),
                ],
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="userprofile",
            name="groups",
            field=models.ManyToManyField(
                blank=True, related_name="user_profiles", to="users.group"
            ),
        ),
    ]


# Contents from: .\migrations\0004_alter_userprofile_full_name.py
# Generated by Django 5.1.2 on 2024-11-05 18:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0003_group_alter_document_document_type_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="userprofile",
            name="full_name",
            field=models.CharField(
                default="",
                help_text="Full name (at least two names required)",
                max_length=255,
            ),
        ),
    ]


# Contents from: .\migrations\0005_alter_userprofile_full_name.py
# Generated by Django 5.1.2 on 2024-11-05 18:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0004_alter_userprofile_full_name"),
    ]

    operations = [
        migrations.AlterField(
            model_name="userprofile",
            name="full_name",
            field=models.CharField(
                default="",
                help_text="Full name (at least tw names required)",
                max_length=255,
            ),
        ),
    ]


# Contents from: .\migrations\0006_alter_document_options_alter_group_options_and_more.py
# Generated by Django 5.1.2 on 2024-11-08 22:53

import django.core.validators
import django.db.models.deletion
import django.utils.timezone
import users.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0005_alter_userprofile_full_name"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="document",
            options={"ordering": ["-uploaded_at"]},
        ),
        migrations.AlterModelOptions(
            name="group",
            options={"ordering": ["name"]},
        ),
        migrations.AlterModelOptions(
            name="role",
            options={
                "ordering": ["name"],
                "verbose_name": "Role",
                "verbose_name_plural": "Roles",
            },
        ),
        migrations.AlterModelOptions(
            name="userprofile",
            options={"ordering": ["user__username"]},
        ),
        migrations.AddField(
            model_name="group",
            name="created_at",
            field=models.DateTimeField(
                auto_now_add=True, default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="group",
            name="description",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="group",
            name="updated_at",
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name="systemsettings",
            name="system_email",
            field=models.EmailField(
                default="aidi@khcc.jo",
                help_text="System email address for automated messages",
                max_length=254,
            ),
        ),
        migrations.AlterField(
            model_name="systemsettings",
            name="system_user",
            field=models.ForeignKey(
                blank=True,
                help_text="System user account for automated actions",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="system_settings",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="userprofile",
            name="full_name",
            field=models.CharField(
                default="",
                help_text="Full name (at least two names required)",
                max_length=255,
                validators=[users.models.validate_full_name],
            ),
        ),
        migrations.AlterField(
            model_name="userprofile",
            name="khcc_employee_number",
            field=models.CharField(
                blank=True,
                max_length=20,
                null=True,
                unique=True,
                validators=[
                    django.core.validators.RegexValidator(
                        message="Employee number can only contain letters and numbers.",
                        regex="^[A-Za-z0-9]+$",
                    )
                ],
            ),
        ),
        migrations.AlterField(
            model_name="userprofile",
            name="mobile",
            field=models.CharField(
                max_length=20,
                validators=[
                    django.core.validators.RegexValidator(
                        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.",
                        regex="^\\+?1?\\d{9,15}$",
                    )
                ],
            ),
        ),
        migrations.AlterField(
            model_name="userprofile",
            name="role",
            field=models.CharField(
                choices=[
                    ("KHCC investigator", "KHCC investigator"),
                    ("Non-KHCC investigator", "Non-KHCC investigator"),
                    (
                        "Research Assistant/Coordinator",
                        "Research Assistant/Coordinator",
                    ),
                    ("OSAR head", "OSAR head"),
                    ("OSAR", "OSAR"),
                    ("IRB chair", "IRB chair"),
                    ("RC coordinator", "RC coordinator"),
                    ("IRB member", "IRB member"),
                    ("RC chair", "RC chair"),
                    ("RC member", "RC member"),
                    ("AHARPP Head", "AHARPP Head"),
                    ("System administrator", "System administrator"),
                    ("CEO", "CEO"),
                    ("CMO", "CMO"),
                    ("AIDI Head", "AIDI Head"),
                    ("Grant Management Officer", "Grant Management Officer"),
                ],
                db_index=True,
                max_length=50,
            ),
        ),
        migrations.AlterField(
            model_name="userprofile",
            name="user",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="userprofile",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddIndex(
            model_name="document",
            index=models.Index(
                fields=["document_type", "expiry_date"],
                name="users_docum_documen_150d1c_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="userprofile",
            index=models.Index(
                fields=["is_approved"], name="users_userp_is_appr_d8bf45_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="userprofile",
            index=models.Index(fields=["role"], name="users_userp_role_c31a7e_idx"),
        ),
    ]


# Contents from: .\migrations\0007_alter_userprofile_mobile_alter_userprofile_role_and_more.py
# Generated by Django 5.1.2 on 2024-11-08 23:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0006_alter_document_options_alter_group_options_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="userprofile",
            name="mobile",
            field=models.CharField(max_length=20),
        ),
        migrations.AlterField(
            model_name="userprofile",
            name="role",
            field=models.CharField(
                blank=True,
                choices=[
                    ("KHCC investigator", "KHCC investigator"),
                    ("Non-KHCC investigator", "Non-KHCC investigator"),
                    (
                        "Research Assistant/Coordinator",
                        "Research Assistant/Coordinator",
                    ),
                    ("OSAR head", "OSAR head"),
                    ("OSAR", "OSAR"),
                    ("IRB chair", "IRB chair"),
                    ("RC coordinator", "RC coordinator"),
                    ("IRB member", "IRB member"),
                    ("RC chair", "RC chair"),
                    ("RC member", "RC member"),
                    ("AHARPP Head", "AHARPP Head"),
                    ("System administrator", "System administrator"),
                    ("CEO", "CEO"),
                    ("CMO", "CMO"),
                    ("AIDI Head", "AIDI Head"),
                    ("Grant Management Officer", "Grant Management Officer"),
                ],
                max_length=50,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="userprofile",
            name="title",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]


# Contents from: .\migrations\0008_alter_userprofile_mobile.py
# Generated by Django 5.1.2 on 2024-11-08 23:16

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0007_alter_userprofile_mobile_alter_userprofile_role_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="userprofile",
            name="mobile",
            field=models.CharField(
                blank=True,
                default="",
                max_length=20,
                null=True,
                validators=[
                    django.core.validators.RegexValidator(
                        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.",
                        regex="^\\+?1?\\d{9,15}$",
                    )
                ],
            ),
        ),
    ]


# Contents from: .\migrations\__init__.py


# Contents from: .\models.py
# users/models.py

from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.utils import timezone
from django.core.cache import cache
from django.core.validators import EmailValidator, RegexValidator
from iRN.constants import USER_ROLE_CHOICES

class Role(models.Model):
    """Role model for managing user roles"""
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Role'
        verbose_name_plural = 'Roles'

    def __str__(self):
        return self.name

class Group(models.Model):
    """Group model for user permissions"""
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

def validate_full_name(value):
    """Validate full name format"""
    names = value.strip().split()
    if len(names) < 2:
        raise ValidationError('Full name must contain at least two names.')
    if not all(name.isalpha() for name in names):
        raise ValidationError('Names should only contain letters.')
    if any(len(name) < 2 for name in names):
        raise ValidationError('Each name should be at least 2 characters long.')

phone_regex = RegexValidator(
    regex=r'^\+?1?\d{9,15}$',
    message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
)

class UserProfile(models.Model):
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE,
        related_name='userprofile'
    )
    institution = models.CharField(
        max_length=255,
        default='King Hussein Cancer Center'
    )
    mobile = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        default='',
        validators=[phone_regex]
    )
    khcc_employee_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^[A-Za-z0-9]+$',
                message='Employee number can only contain letters and numbers.'
            )
        ]
    )
    title = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )
    role = models.CharField(
        max_length=50,
        choices=USER_ROLE_CHOICES,
        blank=True,
        null=True
    )
    groups = models.ManyToManyField(
        Group,
        related_name='user_profiles',
        blank=True
    )
    photo = models.ImageField(
        upload_to='photos/',
        blank=True,
        null=True
    )
    is_approved = models.BooleanField(default=False)
    full_name = models.CharField(
        max_length=255,
        default='',
        help_text='Full name (at least two names required)',
        validators=[validate_full_name]
    )

    class Meta:
        ordering = ['user__username']
        indexes = [
            models.Index(fields=['is_approved']),
            models.Index(fields=['role'])
        ]

    def __str__(self):
        return f"{self.full_name} ({self.user.username})"

    def clean(self):
        """Validate profile data"""
        super().clean()
        if self.full_name:
            validate_full_name(self.full_name)
        
        if self.role == 'KHCC investigator' and not self.khcc_employee_number:
            raise ValidationError({
                'khcc_employee_number': 'Employee number is required for KHCC investigators.'
            })

    def save(self, *args, **kwargs):
        """Custom save method with additional logic"""
        if not self.full_name and self.user:
            self.full_name = f"{self.user.first_name} {self.user.last_name}".strip()
        
        # Only run full_clean if it's a new object or specific fields have changed
        if not self.pk or self.has_changed:
            self.full_clean()
            
        super().save(*args, **kwargs)

    @property
    def has_changed(self):
        """Check if important fields have changed"""
        if not self.pk:
            return True
            
        original = UserProfile.objects.get(pk=self.pk)
        fields_to_check = ['full_name', 'role', 'institution', 'khcc_employee_number']
        
        return any(getattr(self, field) != getattr(original, field) for field in fields_to_check)

    def is_in_group(self, group_name):
        return self.groups.filter(name=group_name).exists()

    @property
    def is_irb_member(self):
        return self.is_in_group('IRB Member')

    @property
    def is_research_council_member(self):
        return self.is_in_group('Research Council Member')

    @property
    def is_head_of_irb(self):
        return self.is_in_group('Head of IRB')

    @property
    def is_osar_admin(self):
        return self.is_in_group('OSAR Admin')

    @property
    def has_valid_gcp(self):
        today = timezone.now().date()
        return self.user.documents.filter(
            document_type='GCP',
            expiry_date__gt=today
        ).exists()

    @property
    def has_qrc(self):
        return self.user.documents.filter(document_type='QRC').exists()

    @property
    def has_ctc(self):
        return self.user.documents.filter(document_type='CTC').exists()

    @property
    def has_cv(self):
        return self.user.documents.filter(document_type='CV').exists()

class Document(models.Model):
    """Document model for user certificates and files"""
    DOCUMENT_CHOICES = [
        ('GCP', 'Good Clinical Practice Certificate'),
        ('QRC', 'Qualitative Record Certificate'),
        ('CTC', 'Consent Training Certificate'),
        ('CV', 'Curriculum Vitae'),
        ('Other', 'Other'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=20, choices=DOCUMENT_CHOICES)
    other_document_name = models.CharField(max_length=255, blank=True, null=True)
    issue_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(blank=True, null=True)
    file = models.FileField(upload_to='documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']
        indexes = [
            models.Index(fields=['document_type', 'expiry_date'])
        ]

    def __str__(self):
        display_name = self.other_document_name if self.document_type == 'Other' else self.get_document_type_display()
        return f"{self.user.username} - {display_name}"

    @property
    def is_expired(self):
        if self.expiry_date:
            return self.expiry_date <= timezone.now().date()
        return False

    @property
    def days_until_expiry(self):
        if self.expiry_date:
            return (self.expiry_date - timezone.now().date()).days
        return None

    @property
    def get_name(self):
        """Return the document name for display"""
        if self.document_type == 'Other' and self.other_document_name:
            return self.other_document_name
        return self.get_document_type_display()

class SystemSettings(models.Model):
    """System-wide settings model"""
    system_email = models.EmailField(
        default='aidi@khcc.jo',
        help_text='System email address for automated messages'
    )
    system_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='system_settings',
        help_text='System user account for automated actions'
    )

    class Meta:
        verbose_name = 'System Settings'
        verbose_name_plural = 'System Settings'

    def save(self, *args, **kwargs):
        cache.delete('system_settings')
        super().save(*args, **kwargs)

    @classmethod
    def get_system_user(cls):
        settings = cls.objects.first()
        if settings and settings.system_user:
            return settings.system_user
        return User.objects.filter(is_superuser=True).first()

# Contents from: .\settings.py
from django.conf import settings

def get_system_email():
    """Get system email from settings with fallback"""
    return getattr(settings, 'SYSTEM_EMAIL', 'system@irn.org')

def get_system_name():
    """Get system name from settings with fallback"""
    return getattr(settings, 'SYSTEM_NAME', 'AIDI System')

def get_system_username():
    """Get system username from settings with fallback"""
    return getattr(settings, 'SYSTEM_USERNAME', 'system') 

# Contents from: .\signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create UserProfile for new users if it doesn't exist"""
    if instance.username == 'system':
        return
        
    # Only create if it doesn't exist
    UserProfile.objects.get_or_create(
        user=instance,
        defaults={
            'full_name': f"{instance.first_name} {instance.last_name}".strip() or instance.username
        }
    )

# Contents from: .\urls.py
# users/urls.py

from django.urls import path
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView
from . import views

app_name = 'users'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='users:login'), name='logout'),
    path('upload_document/', views.upload_document, name='upload_document'),
    path('view_documents/', views.view_documents, name='view_documents'),
    path('display_document/<int:document_id>/', views.display_document, name='display_document'),
    path('profile/', views.profile, name='profile'),
    path('role-autocomplete/', views.role_autocomplete, name='role-autocomplete'),
    path('password-reset/', 
        auth_views.PasswordResetView.as_view(
            template_name='users/password_reset.html',
            email_template_name='users/password_reset_email.html',
            subject_template_name='users/password_reset_subject.txt',
            success_url='/users/password-reset/done/'
        ),
        name='password_reset'),
        
    path('password-reset/done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='users/password_reset_done.html'
        ),
        name='password_reset_done'),
        
    path('password-reset-confirm/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='users/password_reset_confirm.html',
            success_url='/users/password-reset-complete/'
        ),
        name='password_reset_confirm'),
        
    path('password-reset-complete/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='users/password_reset_complete.html'
        ),
        name='password_reset_complete'),
]


# Contents from: .\utils.py
from django.contrib.auth import get_user_model
from django.db import transaction
from .settings import get_system_email, get_system_name, get_system_username

User = get_user_model()

def get_system_user():
    """Get or create the system user for automated messages"""
    with transaction.atomic():
        system_email = get_system_email()
        system_username = get_system_username()
        system_name = get_system_name()
        first_name, last_name = system_name.split(' ', 1) if ' ' in system_name else (system_name, '')
        
        # Try to get existing system user
        try:
            system_user = User.objects.select_related('userprofile').get(username=system_username)
            # Update email if it changed in settings
            if system_user.email != system_email:
                system_user.email = system_email
                system_user.first_name = first_name
                system_user.last_name = last_name
                system_user.save()
        except User.DoesNotExist:
            # Create new system user if it doesn't exist
            system_user = User.objects.create(
                username=system_username,
                email=system_email,
                is_active=False,
                first_name=first_name,
                last_name=last_name
            )

        return system_user

# Contents from: .\views.py
# users/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.http import FileResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.db import transaction, IntegrityError
from django.core.exceptions import ValidationError
from django.conf import settings
import os
import logging
from datetime import date, datetime
from pathlib import Path

from .forms import (
    UserRegistrationForm, 
    LoginForm, 
    DocumentForm, 
    UserProfileForm,
    UserEditForm,
    CustomPasswordChangeForm
)
from .models import UserProfile, Role, Document
# Set up loggers
users_logger = logging.getLogger('IRN.users')
security_logger = logging.getLogger('IRN.security')

# File security configuration
ALLOWED_EXTENSIONS = {
    '.pdf': 'application/pdf',
    '.doc': 'application/msword',
    '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.png': 'image/png'
}

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

def validate_file(uploaded_file):
    """Validate file size and type"""
    if uploaded_file.size > MAX_FILE_SIZE:
        raise ValidationError(f'File size cannot exceed {MAX_FILE_SIZE/1024/1024}MB')

    file_ext = os.path.splitext(uploaded_file.name)[1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise ValidationError(f'Unsupported file type. Allowed types: {", ".join(ALLOWED_EXTENSIONS.keys())}')

    content_type = uploaded_file.content_type
    if content_type not in ALLOWED_EXTENSIONS.values():
        raise ValidationError('File type does not match its extension')

    return True

# views.py (update the profile view)
@login_required
def profile(request):
    """Handle user profile view and updates"""
    try:
        today = date.today()
        if request.method == 'POST':
            user_form = UserEditForm(request.POST, instance=request.user)
            profile_form = UserProfileForm(
                request.POST, 
                request.FILES, 
                instance=request.user.userprofile
            )
            password_form = CustomPasswordChangeForm(request.user, request.POST)
            
            # Flag to track if password form was filled
            password_changed = any(request.POST.get(key) for key in password_form.fields.keys())
            
            # Validate forms
            forms_valid = user_form.is_valid() and profile_form.is_valid()
            if password_changed:
                forms_valid = forms_valid and password_form.is_valid()

            if forms_valid:
                try:
                    with transaction.atomic():
                        user_form.save()
                        profile_form.save()
                        
                        if password_changed and password_form.is_valid():
                            password_form.save()
                            # Re-authenticate the user
                            update_session_auth_hash(request, request.user)
                            messages.success(request, 'Password updated successfully.')
                            
                        users_logger.info(f"Profile updated: {request.user.username}")
                        messages.success(request, 'Profile updated successfully.')
                        return redirect('users:profile')
                except Exception as e:
                    users_logger.error(f"Profile update error: {str(e)}", exc_info=True)
                    messages.error(request, 'An error occurred while updating your profile.')
            else:
                messages.error(request, 'Please correct the errors below.')
        else:
            user_form = UserEditForm(instance=request.user)
            profile_form = UserProfileForm(instance=request.user.userprofile)
            password_form = CustomPasswordChangeForm(request.user)

        documents = [{
            'document': doc,
            'days_until_expiry': (doc.expiry_date - today).days if doc.expiry_date else None,
            'is_expiring_soon': doc.expiry_date and (doc.expiry_date - today).days < 30 if doc.expiry_date else False
        } for doc in request.user.documents.all()]

        context = {
            'user_form': user_form,
            'profile_form': profile_form,
            'password_form': password_form,
            'today': today,
            'documents': documents,
        }
        return render(request, 'users/profile.html', context)
        
    except Exception as e:
        users_logger.error(f"Profile view error: {request.user.username} - {str(e)}", exc_info=True)
        messages.error(request, 'An error occurred. Please try again later.')
        return redirect('users:profile')

@require_http_methods(["GET", "POST"])
def register(request):
    """Handle new user registration"""
    if request.user.is_authenticated:
        return redirect('messaging:inbox')
        
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        profile_form = UserProfileForm(request.POST, request.FILES)
        
        if user_form.is_valid() and profile_form.is_valid():
            try:
                with transaction.atomic():
                    # Create user
                    user = user_form.save(commit=False)
                    full_name_parts = user_form.cleaned_data['full_name'].split()
                    user.first_name = full_name_parts[0]
                    user.last_name = ' '.join(full_name_parts[1:]) if len(full_name_parts) > 1 else ''
                    user.save()

                    # Update profile
                    profile = UserProfile.objects.get(user=user)
                    for field in profile_form.cleaned_data:
                        setattr(profile, field, profile_form.cleaned_data[field])
                    profile.save()

                    users_logger.info(f"New user registered: {user.username}")
                    messages.success(request, 'Registration successful. Awaiting approval from administrator.')
                    return redirect('users:login')

            except Exception as e:
                users_logger.error(f"Registration error: {str(e)}", exc_info=True)
                messages.error(request, 'An error occurred during registration. Please try again.')
                if isinstance(e, IntegrityError):
                    messages.error(request, 'A user with this username or email already exists.')
        else:
            if user_form.errors:
                users_logger.warning(f"User form validation errors: {user_form.errors}")
            if profile_form.errors:
                users_logger.warning(f"Profile form validation errors: {profile_form.errors}")
    else:
        user_form = UserRegistrationForm()
        profile_form = UserProfileForm()
    
    return render(request, 'users/register.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'usage_agreement': 'By registering, you agree to the terms and conditions of use.',
    })

@require_http_methods(["GET", "POST"])
def user_login(request):
    """Handle user login"""
    if request.user.is_authenticated:
        return redirect('messaging:inbox')
        
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if username and password:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    security_logger.info(f"Login successful: {username}")
                    return redirect('messaging:inbox')
                else:
                    security_logger.warning(f"Login attempt to inactive account: {username}")
                    messages.error(request, 'Your account is not active.')
            else:
                security_logger.warning(f"Failed login attempt: {username}")
                messages.error(request, 'Invalid username or password')
        else:
            messages.error(request, 'Please provide both username and password')
    
    return render(request, 'users/login.html')

@login_required
def user_logout(request):
    """Handle user logout"""
    username = request.user.username
    logout(request)
    security_logger.info(f"User logged out: {username}")
    messages.success(request, 'You have been successfully logged out.')
    return redirect('users:login')

@login_required
@require_http_methods(["GET", "POST"])
def upload_document(request):
    """Handle document uploads"""
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                document = form.save(commit=False)
                document.user = request.user
                
                # Validate file
                validate_file(request.FILES['file'])
                document.save()
                
                security_logger.info(
                    f"Document uploaded: {document.get_document_type_display()} by {request.user.username}"
                )
                
                messages.success(request, 'Document uploaded successfully.')
                return redirect('users:view_documents')
                
            except ValidationError as e:
                messages.error(request, str(e))
            except Exception as e:
                security_logger.error(f"Document upload error: {str(e)}", exc_info=True)
                messages.error(request, 'Error uploading document. Please try again.')
    else:
        form = DocumentForm()
    
    return render(request, 'users/upload_document.html', {
        'form': form,
        'allowed_types': list(ALLOWED_EXTENSIONS.keys()),
        'max_size_mb': MAX_FILE_SIZE / (1024 * 1024)
    })

@login_required
def view_documents(request):
    """Display user's documents"""
    try:
        documents = request.user.documents.all()
        documents_with_expiry = [{
            'document': document,
            'days_until_expiry': (document.expiry_date - date.today()).days if document.expiry_date else None,
            'file_extension': os.path.splitext(document.file.name)[1].lower()
        } for document in documents]
        
        return render(request, 'users/view_documents.html', {'documents': documents_with_expiry})
        
    except Exception as e:
        users_logger.error(f"Error viewing documents: {str(e)}", exc_info=True)
        messages.error(request, 'Error loading documents. Please try again.')
        return redirect('users:profile')

@login_required
def display_document(request, document_id):
    """Display a specific document"""
    try:
        # Get document and verify ownership
        document = get_object_or_404(Document, id=document_id)
        
        # Check if the user has permission to view this document
        if document.user != request.user and not request.user.is_staff:
            raise PermissionDenied("You don't have permission to view this document.")

        # Get the file path and verify it exists
        if not document.file:
            raise FileNotFoundError("Document file not found in database")
            
        file_path = document.file.path
        
        if not os.path.exists(file_path):
            users_logger.error(f"Physical file missing for document {document_id}: {file_path}")
            raise FileNotFoundError(f"Document file not found on disk: {file_path}")

        # Determine content type
        file_ext = os.path.splitext(document.file.name)[1].lower()
        content_type = ALLOWED_EXTENSIONS.get(
            file_ext, 
            mimetypes.guess_type(document.file.name)[0] or 'application/octet-stream'
        )

        try:
            response = FileResponse(
                open(file_path, 'rb'),
                content_type=content_type
            )
            response['Content-Disposition'] = f'inline; filename="{os.path.basename(document.file.name)}"'
            
            users_logger.info(
                f"Document successfully served: {document.get_document_type_display()} "
                f"(ID: {document_id}) to user {request.user.username}"
            )
            return response

        except IOError as e:
            users_logger.error(f"IOError reading document {document_id}: {str(e)}")
            return HttpResponseServerError("Error reading document file")

    except Document.DoesNotExist:
        users_logger.warning(f"Attempt to access non-existent document {document_id}")
        return HttpResponseNotFound("Document not found")
        
    except PermissionDenied as e:
        security_logger.warning(
            f"Unauthorized document access attempt: User {request.user.username} "
            f"tried to access document {document_id}"
        )
        messages.error(request, str(e))
        return redirect('users:view_documents')
        
    except FileNotFoundError as e:
        users_logger.error(f"File not found for document {document_id}: {str(e)}")
        messages.error(request, "Document file not found")
        return redirect('users:view_documents')
        
    except Exception as e:
        users_logger.error(
            f"Unexpected error displaying document {document_id}: {str(e)}", 
            exc_info=True
        )
        messages.error(request, "An error occurred while displaying the document")
        return redirect('users:view_documents')

@login_required
def role_autocomplete(request):
    """Handle role autocomplete functionality"""
    try:
        term = request.GET.get('term', '').strip()
        
        if len(term) < 2:
            return JsonResponse([], safe=False)

        roles = Role.objects.filter(name__icontains=term)[:10]
        results = [{'id': role.id, 'label': role.name} for role in roles]
        
        return JsonResponse(results, safe=False)
        
    except Exception as e:
        users_logger.error(f"Role autocomplete error: {str(e)}", exc_info=True)
        return JsonResponse([], safe=False)