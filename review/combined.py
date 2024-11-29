# Combined Python and HTML files
# Generated from directory: C:\Users\isult\Dropbox\AI\Projects\IRN3\review
# Total files found: 41



# Contents from: .\pdf\dashboard_export.html
{# review/templates/review/pdf/dashboard_export.html #}
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; }
        .header { text-align: center; margin-bottom: 20px; }
        table { width: 100%; border-collapse: collapse; margin-bottom: 20px; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left;
        font-size: 12px; }
        th { background-color: #f5f5f5; }
        .status-badge {
            padding: 3px 8px;
            border-radius: 3px;
            font-size: 11px;
            color: white;
        }
        .status-pending { background-color: #ffc107; }
        .status-accepted { background-color: #17a2b8; }
        .status-completed { background-color: #28a745; }
        .status-overdue { background-color: #dc3545; }
        .section-header { 
            font-size: 16px;
            font-weight: bold;
            margin: 20px 0 10px 0;
            padding-bottom: 5px;
            border-bottom: 2px solid #333;
        }
        .footer {
            position: fixed;
            bottom: 0;
            width: 100%;
            text-align: center;
            font-size: 10px;
            padding: 10px 0;
            border-top: 1px solid #ddd;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>Review Dashboard Export</h1>
        <p>Generated on: {{ date|date:"F d, Y H:i" }}</p>
        <p>Reviewer: {{ user.userprofile.full_name }}</p>
    </div>

    <div class="section-header">Pending Reviews</div>
    <table>
        <thead>
            <tr>
                <th>Title</th>
                <th>Primary Investigator</th>
                <th>Study Type</th>
                <th>Deadline</th>
                <th>Status</th>
                <th>Days Remaining</th>
            </tr>
        </thead>
        <tbody>
            {% for review in pending_reviews %}
            <tr>
                <td>{{ review.submission.title }}</td>
                <td>{{ review.submission.primary_investigator.userprofile.full_name }}</td>
                <td>{{ review.submission.study_type.name }}</td>
                <td>{{ review.deadline|date:"M d, Y" }}</td>
                <td>
                    <span class="status-badge status-{{ review.status|lower }}">
                        {{ review.get_status_display }}
                    </span>
                </td>
                <td>{{ review.days_until_deadline }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>

    <div class="section-header">Completed Reviews</div>
    <table>
        <thead>
            <tr>
                <th>Title</th>
                <th>Primary Investigator</th>
                <th>Study Type</th>
                <th>Submitted On</th>
            </tr>
        </thead>
        <tbody>
            {% for review in completed_reviews %}
            <tr>
                <td>{{ review.submission.title }}</td>
                <td>{{ review.submission.primary_investigator.userprofile.full_name }}</td>
                <td>{{ review.submission.study_type.name }}</td>
                <td>{{ review.date_submitted|date:"M d, Y" }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>

    <div class="footer">
        <p>Generated from iRN System - Page {page_number} of {total_pages}</p>
    </div>
</body>
</html>

{# review/templates/review/includes/review_actions.html #}
<div class="btn-group" role="group">
    {% if review.status == 'pending' %}
    <a href="{% url 'review:submit_review' review.id %}" class="btn btn-sm btn-primary">
        <i class="fas fa-edit"></i> Review
    </a>
    {% elif review.status == 'accepted' %}
    <a href="{% url 'review:submit_review' review.id %}" class="btn btn-sm btn-info">
        <i class="fas fa-check"></i> Complete
    </a>
    {% endif %}
    
    <button type="button" class="btn btn-sm btn-secondary dropdown-toggle" data-bs-toggle="dropdown">
        <i class="fas fa-ellipsis-v"></i>
    </button>
    <ul class="dropdown-menu">
        <li>
            <a class="dropdown-item" href="{% url 'review:view_review' review.id %}">
                <i class="fas fa-eye"></i> View Details
            </a>
        </li>
        {% if review.status == 'pending' %}
        <li>
            <a class="dropdown-item text-warning" href="{% url 'review:request_extension' review.id %}">
                <i class="fas fa-clock"></i> Request Extension
            </a>
        </li>
        <li>
            <a class="dropdown-item text-danger" href="{% url 'review:decline_review' review.id %}">
                <i class="fas fa-times"></i> Decline Review
            </a>
        </li>
        {% endif %}
        <li>
            <a class="dropdown-item" href="{% url 'messaging:compose_message' %}?related_review={{ review.id }}">
                <i class="fas fa-envelope"></i> Send Message
            </a>
        </li>
    </ul>
</div>

# Contents from: .\templates\review\assign_irb_number.html
{% extends "base.html" %}

{% block content %}
<div class="container mt-4">
    <h2>Assign IRB Number</h2>
    <div class="card">
        <div class="card-body">
            <h5 class="card-title">{{ submission.title }}</h5>
            <p class="card-text">Primary Investigator: {{ submission.primary_investigator.get_full_name }}</p>
            
            <form method="post">
                {% csrf_token %}
                <div class="mb-3">
                    <label for="irb_number" class="form-label">IRB Number</label>
                    <input type="text" 
                           class="form-control" 
                           id="irb_number" 
                           name="irb_number" 
                           value="{{ suggested_irb }}"
                           required>
                    <div class="form-text">Suggested format: YYYY-XXX</div>
                </div>
                
                <div class="mt-3">
                    <button type="submit" class="btn btn-primary">Assign IRB Number</button>
                    <a href="{% url 'review:review_summary' submission.temporary_id %}" 
                       class="btn btn-secondary">Cancel</a>
                </div>
            </form>
        </div>
    </div>
</div>
{% endblock %} 

# Contents from: .\templates\review\create_review_request.html
<!-- review/templates/review/create_review_request.html -->
{% extends 'base.html' %}
{% block content %}
<h2>Create Review Request for "{{ submission.title }}" (Version {{ submission.version }})</h2>
<form method="post">
    {% csrf_token %}
    {{ form.non_field_errors }}

    <div class="form-group">
        {{ form.requested_to.label_tag }}
        <select name="requested_to" id="id_requested_to" class="form-control select2"></select>
        {{ form.requested_to.errors }}
        <small class="form-text text-muted">{{ form.requested_to.help_text }}</small>
    </div>

    <div class="form-group">
        {{ form.deadline.label_tag }}
        {{ form.deadline }}
        {{ form.deadline.errors }}
        <small class="form-text text-muted">{{ form.deadline.help_text }}</small>
    </div>

    <div class="form-group">
        {{ form.message.label_tag }}
        {{ form.message }}
        {{ form.message.errors }}
        <small class="form-text text-muted">{{ form.message.help_text }}</small>
    </div>

    <div class="form-group">
        {{ form.selected_forms.label_tag }}
        {{ form.selected_forms }}
        {{ form.selected_forms.errors }}
        <small class="form-text text-muted">
            Available forms for {{ submission.study_type.name }}. 
            Select all applicable review forms.
        </small>
    </div>

    <div class="form-check mb-3">
        {{ form.can_forward }}
        <label class="form-check-label" for="{{ form.can_forward.id_for_label }}">
            Allow reviewer to forward this request to others
        </label>
    </div>

    <button type="submit" class="btn btn-primary">Send Review Request</button>
</form>
{% endblock %}

{% block page_specific_js %}
<script>
    $(document).ready(function() {
        $('#id_requested_to').select2({
            theme: 'bootstrap4',
            ajax: {
                url: '{% url "submission:user-autocomplete" %}',
                dataType: 'json',
                delay: 250,
                data: function (params) {
                    return {
                        term: params.term,
                        submission_id: '{{ submission.id }}',
                        user_type: 'reviewer'
                    };
                },
                processResults: function (data) {
                    return {
                        results: data.map(function(item) {
                            return {
                                id: item.id,
                                text: item.label
                            };
                        })
                    };
                },
                cache: true
            },
            minimumInputLength: 2,
            placeholder: 'Search for reviewer...',
            allowClear: true,
            width: '100%'
        });

        // Handle initial value if it exists
        {% if form.requested_to.initial %}
            var initialUser = {
                id: '{{ form.requested_to.initial.id }}',
                text: '{{ form.requested_to.initial.get_full_name|escapejs }}'
            };
            var initialOption = new Option(initialUser.text, initialUser.id, true, true);
            $('#id_requested_to').append(initialOption).trigger('change');
        {% endif %}
    });
</script>
{% endblock %}


# Contents from: .\templates\review\dashboard.html
{% extends 'base.html' %}
{% load static %}
{% load review_tags %}

{% block extra_css %}
<link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.10.24/css/dataTables.bootstrap4.min.css">
<link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/buttons/2.2.3/css/buttons.bootstrap4.min.css">
<style>
    .btn-green {
        background-color: #28a745;
        border-color: #28a745;
        color: #fff;
    }
    .btn-green:hover {
        background-color: #218838;
        border-color: #1e7e34;
        color: #fff;
    }
</style>
{% endblock %}

{% block content %}
<div class="container">
    <h2 class="mb-4">Review Dashboard</h2>
    <div class="container">
        {% if is_irb_member %}
        <!-- IRB Dashboard -->
        <div class="card mb-4">
            <div class="card-header">
                <h3 class="card-title mb-0">IRB Review Queue</h3>
            </div>
            <div class="card-body">
                {% if irb_submissions %}
                    <div class="table-responsive">
                        <table id="irbSubmissionsTable" class="table table-hover">
                            <thead>
                                <tr>
                                    <th>Title</th>
                                    <th>Submission Date</th>
                                    <th>Primary Investigator</th>
                                    <th>Study Type</th>
                                    <th>Status</th>
                                    <th>Visibility</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for submission in irb_submissions %}
                                <tr>
                                    <td>{{ submission.title }}</td>
                                    <td>{{ submission.date_submitted|date:"Y-m-d" }}</td>
                                    <td>{{ submission.primary_investigator.userprofile.full_name }}</td>
                                    <td>{{ submission.study_type }}</td>
                                    <td>{{ submission.get_status_display }}</td>
                                    <td>
                                        <button class="toggle-visibility-btn btn {% if submission.show_in_irb %}btn-success{% else %}btn-secondary{% endif %}"
                                                data-submission-id="{{ submission.id }}"
                                                data-toggle-type="irb">
                                            Toggle IRB
                                        </button>
                                        <button class="toggle-visibility-btn btn {% if submission.show_in_rc %}btn-success{% else %}btn-secondary{% endif %}"
                                                data-submission-id="{{ submission.id }}"
                                                data-toggle-type="rc">
                                            Toggle RC
                                        </button>
                                    </td>
                                    <td>
                                        <a href="{% url 'review:review_summary' submission.pk %}" 
                                           class="btn btn-success btn-sm">View Details</a>
                                        {% if submission.status == 'under_review' %}
                                            <a href="{% url 'review:process_decision' submission.pk %}" 
                                               class="btn btn-primary btn-sm">Make Decision</a>
                                        {% endif %}
                                    </td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                {% else %}
                    <p class="mb-0">No submissions requiring IRB review.</p>
                {% endif %}
            </div>
        </div>
    
        <!-- IRB Review Requests -->
        <div class="card mb-4">
            <div class="card-header">
                <h3 class="card-title mb-0">My IRB Reviews</h3>
            </div>
            <div class="card-body">
                {% if irb_reviews %}
                    <div class="table-responsive">
                        <table id="irbReviewsTable" class="table table-hover">
                            <thead>
                                <tr>
                                    <th>Title</th>
                                    <th>Primary Investigator</th>
                                    <th>Requested By</th>
                                    <th>Status</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for review in irb_reviews %}
                                <tr>
                                    <td>{{ review.submission.title }}</td>
                                    <td>{{ review.submission.primary_investigator.userprofile.full_name }}</td>
                                    <td>{{ review.requested_by.userprofile.full_name }}</td>
                                    <td>{{ review.get_status_display }}</td>
                                    <td>
                                        {% if review.requested_to == user or review.requested_by == user %}
                                            <a href="{% url 'review:view_review' review.id %}" 
                                               class="btn btn-info btn-sm">View Review</a>
                                        {% endif %}
                                        {% if review.requested_to == user and review.status == 'pending' %}
                                            <a href="{% url 'review:submit_review' review.id %}" 
                                               class="btn btn-primary btn-sm">Submit Review</a>
                                        {% endif %}
                                    </td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                {% else %}
                    <p class="mb-0">No IRB reviews assigned.</p>
                {% endif %}
            </div>
        </div>
        {% endif %}
    
        {% if is_rc_member %}
        <!-- RC Dashboard -->
        <div class="card mb-4">
            <div class="card-header">
                <h3 class="card-title mb-0">RC Review Queue</h3>
            </div>
            <div class="card-body">
                {% if rc_submissions %}
                    <div class="table-responsive">
                        <table id="rcSubmissionsTable" class="table table-hover">
                            <thead>
                                <tr>
                                    <th>Title</th>
                                    <th>Submission Date</th>
                                    <th>Primary Investigator</th>
                                    <th>Study Type</th>
                                    <th>Status</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for submission in rc_submissions %}
                                <tr>
                                    <td>{{ submission.title }}</td>
                                    <td>{{ submission.date_submitted|date:"Y-m-d" }}</td>
                                    <td>{{ submission.primary_investigator.userprofile.full_name }}</td>
                                    <td>{{ submission.study_type }}</td>
                                    <td>{{ submission.get_status_display }}</td>
                                    <td>
                                        <a href="{% url 'review:review_summary' submission.pk %}" 
                                           class="btn btn-success btn-sm">View Details</a>
                                    </td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                {% else %}
                    <p class="mb-0">No submissions requiring RC review.</p>
                {% endif %}
            </div>
        </div>
    
        <!-- RC Review Requests -->
        <div class="card mb-4">
            <div class="card-header">
                <h3 class="card-title mb-0">My RC Reviews</h3>
            </div>
            <div class="card-body">
                {% if rc_reviews %}
                    <div class="table-responsive">
                        <table id="rcReviewsTable" class="table table-hover">
                            <thead>
                                <tr>
                                    <th>Title</th>
                                    <th>Primary Investigator</th>
                                    <th>Requested By</th>
                                    <th>Status</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for review in rc_reviews %}
                                <tr>
                                    <td>{{ review.submission.title }}</td>
                                    <td>{{ review.submission.primary_investigator.userprofile.full_name }}</td>
                                    <td>{{ review.requested_by.userprofile.full_name }}</td>
                                    <td>{{ review.get_status_display }}</td>
                                    <td>
                                        {% if review.requested_to == user or review.requested_by == user %}
                                            <a href="{% url 'review:view_review' review.id %}" 
                                               class="btn btn-info btn-sm">View Review</a>
                                        {% endif %}
                                        {% if review.requested_to == user and review.status == 'pending' %}
                                            <a href="{% url 'review:submit_review' review.id %}" 
                                               class="btn btn-primary btn-sm">Submit Review</a>
                                        {% endif %}
                                    </td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                {% else %}
                    <p class="mb-0">No RC reviews assigned.</p>
                {% endif %}
            </div>
        </div>
        {% endif %}
    </div>

    {# OSAR Member Dashboard #}
    {% if is_osar_member %}
    <div class="card mb-4">
        <div class="card-header">
            <h3 class="card-title mb-0">Submissions Needing Review</h3>
        </div>
        <div class="card-body">
            {% if submissions_needing_review %}
                <div class="table-responsive">
                    <table id="submissionsNeedingReviewTable" class="table table-hover">
                        <thead>
                            <tr>
                                <th>Title</th>
                                <th>Submission Date</th>
                                <th>Primary Investigator</th>
                                <th>Study Type</th>
                                <th>Requests</th>
                                <th>Days</th>
                                <th>✅</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for submission in submissions_needing_review %}
                            <tr>
                                <td>{{ submission.title }}</td>
                                <td>{{ submission.date_submitted|date:"Y-m-d" }}</td>
                                <td>{{ submission.primary_investigator.userprofile.full_name }}</td>
                                <td>{{ submission.study_type }}</td>
                                <td>
                                    {% if submission.review_requests.exists %}
                                        <ul class="list-unstyled mb-0">
                                        {% for request in submission.review_requests.all %}
                                            <li>
                                                <strong>
                                                    <a href="{% url 'messaging:compose' %}?recipient={{ request.requested_to.id }}&submission={{ submission.id }}" 
                                                       class="text-primary text-decoration-none">
                                                        {{ request.requested_to.get_full_name }}
                                                    </a>
                                                </strong>
                                            </li>
                                        {% endfor %}
                                        </ul>
                                    {% else %}
                                        No requests yet
                                    {% endif %}
                                </td>
                                <td>
                                    {% if submission.review_requests.exists %}
                                        <ul class="list-unstyled mb-0">
                                        {% for request in submission.review_requests.all %}
                                            <li>
                                                {% with days=request.created_at|timesince_in_days %}
                                                    {{ days }}
                                                {% endwith %}
                                            </li>
                                        {% endfor %}
                                        </ul>
                                    {% else %}
                                        -
                                    {% endif %}
                                </td>
                                <td>
                                    {% if submission.review_requests.exists %}
                                        <ul class="list-unstyled mb-0">
                                        {% for request in submission.review_requests.all %}
                                            <li>
                                                {% if request.status == 'completed' %}
                                                    <span class="text-success">✅</span>
                                                {% elif request.status == 'declined' %}
                                                    <span class="text-danger">❌</span>
                                                {% elif request.status == 'pending' %}
                                                    <span class="text-warning">⏳</span>
                                                {% else %}
                                                    <span class="text-secondary">-</span>
                                                {% endif %}
                                            </li>
                                        {% endfor %}
                                        </ul>
                                    {% else %}
                                        -
                                    {% endif %}
                                </td>
                                <td>
                                    <a href="{% url 'review:create_review_request' submission.pk %}" class="btn btn-primary btn-sm">Create Review Request</a>
                                    <a href="{% url 'review:review_summary' submission.pk %}" class="btn btn-success btn-sm">Details</a>
                                    {% if is_irb_member and not submission.irb_number %}
                                        <a href="{% url 'review:assign_irb' submission.pk %}" class="btn btn-info btn-sm">Assign IRB</a>
                                    {% endif %}
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            {% else %}
                <p class="mb-0">No submissions currently need review.</p>
            {% endif %}
        </div>
    </div>
    {% endif %}

    {# Forwarded Reviews Dashboard #}
    {% if forwarded_reviews %}
    <div class="card mb-4">
        <div class="card-header">
            <h3 class="card-title mb-0">Forwarded Reviews</h3>
        </div>
        <div class="card-body">
            {% if forwarded_reviews %}
                <div class="table-responsive">
                    <table id="forwardedReviewsTable" class="table table-hover">
                        <thead>
                            <tr>
                                <th>Title</th>
                                <th>Submission Date</th>
                                <th>Primary Investigator</th>
                                <th>Study Type</th>
                                <th>Requested by</th>
                                <th>Days</th>
                                <th>✅</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for review in forwarded_reviews %}
                            <tr>
                                <td>{{ review.submission.title }}</td>
                                <td>{{ review.submission.date_submitted|date:"Y-m-d" }}</td>
                                <td>{{ review.submission.primary_investigator.userprofile.full_name }}</td>
                                <td>{{ review.submission.study_type }}</td>
                                <td>
                                    <strong>
                                        <a href="{% url 'messaging:compose' %}?recipient={{ review.requested_by.id }}&submission={{ review.submission.id }}" 
                                           class="text-primary text-decoration-none">
                                            {{ review.requested_by.get_full_name }}
                                        </a>
                                    </strong>
                                </td>
                                <td>
                                    {% with days=review.created_at|timesince_in_days %}
                                        {{ days }}
                                    {% endwith %}
                                </td>
                                <td>
                                    {% if review.status == 'completed' %}
                                        <span class="text-success">✅</span>
                                    {% elif review.status == 'declined' %}
                                        <span class="text-danger">❌</span>
                                    {% elif review.status == 'pending' %}
                                        <span class="text-warning">⏳</span>
                                    {% else %}
                                        <span class="text-secondary">-</span>
                                    {% endif %}
                                </td>
                                <td>
                                    <a href="{% url 'review:create_review_request' review.submission.pk %}" class="btn btn-primary btn-sm">Create Review Request</a>
                                    <a href="{% url 'review:review_summary' review.submission.pk %}" class="btn btn-success btn-sm">Details</a>
                                    {% if is_irb_member and not review.submission.irb_number %}
                                        <a href="{% url 'review:assign_irb' review.submission.pk %}" class="btn btn-info btn-sm">Assign IRB</a>
                                    {% endif %}
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            {% else %}
                <p class="mb-0">No forwarded reviews.</p>
            {% endif %}
        </div>
    </div>
    {% endif %}

    {# IRB Member Dashboard #}
    {% if is_irb_member %}
    <div class="card mb-4">
        <div class="card-header">
            <h3 class="card-title mb-0">Pending IRB Decisions</h3>
        </div>
        <div class="card-body">
            {% if pending_irb_decisions %}
                <div class="table-responsive">
                    <table id="pendingIRBDecisionsTable" class="table table-hover">
                        <thead>
                            <tr>
                                <th>Title</th>
                                <th>Submission Date</th>
                                <th>Primary Investigator</th>
                                <th>Study Type</th>
                                <th>Requests</th>
                                <th>Days</th>
                                <th>✅</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for submission in pending_irb_decisions %}
                            <tr>
                                <td>{{ submission.title }}</td>
                                <td>{{ submission.date_submitted|date:"Y-m-d" }}</td>
                                <td>{{ submission.primary_investigator.userprofile.full_name }}</td>
                                <td>{{ submission.study_type }}</td>
                                <td>
                                    {% if submission.review_requests.exists %}
                                        <ul class="list-unstyled mb-0">
                                        {% for request in submission.review_requests.all %}
                                            <li>
                                                <strong>
                                                    <a href="{% url 'messaging:compose' %}?recipient={{ request.requested_to.id }}&submission={{ submission.id }}" 
                                                       class="text-primary text-decoration-none">
                                                        {{ request.requested_to.get_full_name }}
                                                    </a>
                                                </strong>
                                            </li>
                                        {% endfor %}
                                        </ul>
                                    {% else %}
                                        No requests yet
                                    {% endif %}
                                </td>
                                <td>
                                    {% if submission.review_requests.exists %}
                                        <ul class="list-unstyled mb-0">
                                        {% for request in submission.review_requests.all %}
                                            <li>
                                                {% with days=request.created_at|timesince_in_days %}
                                                    {{ days }}
                                                {% endwith %}
                                            </li>
                                        {% endfor %}
                                        </ul>
                                    {% else %}
                                        -
                                    {% endif %}
                                </td>
                                <td>
                                    {% if submission.review_requests.exists %}
                                        <ul class="list-unstyled mb-0">
                                        {% for request in submission.review_requests.all %}
                                            <li>
                                                {% if request.status == 'completed' %}
                                                    <span class="text-success">✅</span>
                                                {% elif request.status == 'declined' %}
                                                    <span class="text-danger">❌</span>
                                                {% elif request.status == 'pending' %}
                                                    <span class="text-warning">⏳</span>
                                                {% else %}
                                                    <span class="text-secondary">-</span>
                                                {% endif %}
                                            </li>
                                        {% endfor %}
                                        </ul>
                                    {% else %}
                                        -
                                    {% endif %}
                                </td>
                                <td>
                                    <a href="{% url 'review:review_summary' submission.pk %}" class="btn btn-success btn-sm">Details</a>
                                    <a href="{% url 'review:process_decision' submission.pk %}" class="btn btn-primary btn-sm">Make Decision</a>
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            {% else %}
                <p class="mb-0">No submissions pending IRB decision.</p>
            {% endif %}
        </div>
    </div>
    {% endif %}

    {# RC Member Dashboard #}
    {% if is_rc_member %}
    <div class="card mb-4">
        <div class="card-header">
            <h3 class="card-title mb-0">My Department's Submissions</h3>
        </div>
        <div class="card-body">
            {% if department_submissions %}
                <div class="table-responsive">
                    <table id="departmentSubmissionsTable" class="table table-hover">
                        <thead>
                            <tr>
                                <th>Title</th>
                                <th>Submission Date</th>
                                <th>Primary Investigator</th>
                                <th>Study Type</th>
                                <th>Requests</th>
                                <th>Days</th>
                                <th>✅</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for submission in department_submissions %}
                            <tr>
                                <td>{{ submission.title }}</td>
                                <td>{{ submission.date_submitted|date:"Y-m-d" }}</td>
                                <td>{{ submission.primary_investigator.userprofile.full_name }}</td>
                                <td>{{ submission.study_type }}</td>
                                <td>
                                    {% if submission.review_requests.exists %}
                                        <ul class="list-unstyled mb-0">
                                        {% for request in submission.review_requests.all %}
                                            <li>
                                                <strong>
                                                    <a href="{% url 'messaging:compose' %}?recipient={{ request.requested_to.id }}&submission={{ submission.id }}" 
                                                       class="text-primary text-decoration-none">
                                                        {{ request.requested_to.get_full_name }}
                                                    </a>
                                                </strong>
                                            </li>
                                        {% endfor %}
                                        </ul>
                                    {% else %}
                                        No requests yet
                                    {% endif %}
                                </td>
                                <td>
                                    {% if submission.review_requests.exists %}
                                        <ul class="list-unstyled mb-0">
                                        {% for request in submission.review_requests.all %}
                                            <li>
                                                {% with days=request.created_at|timesince_in_days %}
                                                    {{ days }}
                                                {% endwith %}
                                            </li>
                                        {% endfor %}
                                        </ul>
                                    {% else %}
                                        -
                                    {% endif %}
                                </td>
                                <td>
                                    {% if submission.review_requests.exists %}
                                        <ul class="list-unstyled mb-0">
                                        {% for request in submission.review_requests.all %}
                                            <li>
                                                {% if request.status == 'completed' %}
                                                    <span class="text-success">✅</span>
                                                {% elif request.status == 'declined' %}
                                                    <span class="text-danger">❌</span>
                                                {% elif request.status == 'pending' %}
                                                    <span class="text-warning">⏳</span>
                                                {% else %}
                                                    <span class="text-secondary">-</span>
                                                {% endif %}
                                            </li>
                                        {% endfor %}
                                        </ul>
                                    {% else %}
                                        -
                                    {% endif %}
                                </td>
                                <td>
                                    <a href="{% url 'review:review_summary' submission.pk %}" class="btn btn-success btn-sm">Details</a>
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            {% else %}
                <p class="mb-0">No submissions in your department.</p>
            {% endif %}
        </div>
    </div>
    {% endif %}

    {# AAHRPP Member Dashboard #}
    {% if is_aahrpp_member %}
    <div class="card mb-4">
        <div class="card-header">
            <h3 class="card-title mb-0">AAHRPP Review Queue</h3>
        </div>
        <div class="card-body">
            {% if aahrpp_submissions %}
                <div class="table-responsive">
                    <table id="aahrppSubmissionsTable" class="table table-hover">
                        <thead>
                            <tr>
                                <th>Title</th>
                                <th>Submission Date</th>
                                <th>Primary Investigator</th>
                                <th>Study Type</th>
                                <th>Requests</th>
                                <th>Days</th>
                                <th>✅</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for submission in aahrpp_submissions %}
                            <tr>
                                <td>{{ submission.title }}</td>
                                <td>{{ submission.date_submitted|date:"Y-m-d" }}</td>
                                <td>{{ submission.primary_investigator.userprofile.full_name }}</td>
                                <td>{{ submission.study_type }}</td>
                                <td>
                                    {% if submission.review_requests.exists %}
                                        <ul class="list-unstyled mb-0">
                                        {% for request in submission.review_requests.all %}
                                            <li>
                                                <strong>
                                                    <a href="{% url 'messaging:compose' %}?recipient={{ request.requested_to.id }}&submission={{ submission.id }}" 
                                                       class="text-primary text-decoration-none">
                                                        {{ request.requested_to.get_full_name }}
                                                    </a>
                                                </strong>
                                            </li>
                                        {% endfor %}
                                        </ul>
                                    {% else %}
                                        No requests yet
                                    {% endif %}
                                </td>
                                <td>
                                    {% if submission.review_requests.exists %}
                                        <ul class="list-unstyled mb-0">
                                        {% for request in submission.review_requests.all %}
                                            <li>
                                                {% with days=request.created_at|timesince_in_days %}
                                                    {{ days }}
                                                {% endwith %}
                                            </li>
                                        {% endfor %}
                                        </ul>
                                    {% else %}
                                        -
                                    {% endif %}
                                </td>
                                <td>
                                    {% if submission.review_requests.exists %}
                                        <ul class="list-unstyled mb-0">
                                        {% for request in submission.review_requests.all %}
                                            <li>
                                                {% if request.status == 'completed' %}
                                                    <span class="text-success">✅</span>
                                                {% elif request.status == 'declined' %}
                                                    <span class="text-danger">❌</span>
                                                {% elif request.status == 'pending' %}
                                                    <span class="text-warning">⏳</span>
                                                {% else %}
                                                    <span class="text-secondary">-</span>
                                                {% endif %}
                                            </li>
                                        {% endfor %}
                                        </ul>
                                    {% else %}
                                        -
                                    {% endif %}
                                </td>
                                <td>
                                    <a href="{% url 'review:review_summary' submission.pk %}" class="btn btn-success btn-sm">Details</a>
                                    <a href="{% url 'review:review' submission.pk %}" class="btn btn-primary btn-sm">Review</a>
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            {% else %}
                <p class="mb-0">No submissions requiring AAHRPP review.</p>
            {% endif %}
        </div>
    </div>
    {% endif %}

    {# Common Section for All Users - Pending Reviews #}
    <div class="card mb-4">
        <div class="card-header">
            <h3 class="card-title mb-0">My Pending Reviews</h3>
        </div>
        <div class="card-body">
            {% if pending_reviews %}
                <div class="table-responsive">
                    <table id="pendingReviewsTable" class="table table-hover">
                        <thead>
                            <tr>
                                <th>Title</th>
                                <th>Primary Investigator</th>
                                <th>Requested By</th>
                                <th>Deadline</th>
                                <th>Status</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for review in pending_reviews %}
                            <tr>
                                <td>{{ review.submission.title }}</td>
                                <td>{{ review.submission.primary_investigator.userprofile.full_name }}</td>
                                <td>{{ review.requested_by.userprofile.full_name }}</td>
                                <td>{{ review.deadline }}</td>
                                <td>{{ review.status }}</td>
                                <td>
                                    <div class="btn-group">
                                        <a href="{% url 'review:submit_review' review.id %}" class="btn btn-primary btn-sm">Submit Review</a>
                                        <a href="{% url 'review:decline_review' review.id %}" class="btn btn-danger btn-sm">Decline</a>
                                        <a href="{% url 'review:request_extension' review.id %}" class="btn btn-warning btn-sm">Request Extension</a>
                                        <a href="{% url 'review:review_summary' review.submission.pk %}" class="btn btn-success btn-sm">Details</a>
                                    </div>
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            {% else %}
                <p class="mb-0">No pending reviews.</p>
            {% endif %}
        </div>
    </div>

    {# Common Section for All Users - Completed Reviews #}
    <div class="card">
        <div class="card-header">
            <h3 class="card-title mb-0">My Completed Reviews</h3>
        </div>
        <div class="card-body">
            {% if completed_reviews %}
                <div class="table-responsive">
                    <table id="completedReviewsTable" class="table table-hover">
                        <thead>
                            <tr>
                                <th>Title</th>
                                <th>Primary Investigator</th>
                                <th>Requested By</th>
                                <th>Completion Date</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for review in completed_reviews %}
                            <tr>
                                <td>{{ review.submission.title }}</td>
                                <td>{{ review.submission.primary_investigator.userprofile.full_name }}</td>
                                <td>{{ review.requested_by.userprofile.full_name }}</td>
                                <td>{{ review.updated_at }}</td>
                                <td>
                                    <div class="btn-group">
                                        <a href="{% url 'review:view_review' review.id %}" class="btn btn-info btn-sm">View Review</a>
                                        <a href="{% url 'review:download_review_pdf' review.id %}" class="btn btn-primary btn-sm">PDF</a>
                                        <a href="{% url 'review:review_summary' review.submission.pk %}" class="btn btn-success btn-sm">Details</a>
                                    </div>
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            {% else %}
                <p class="mb-0">No completed reviews.</p>
            {% endif %}
        </div>
    </div>
</div>

{% endblock %}

{% block page_specific_js %}
<script src="https://cdn.datatables.net/1.10.24/js/jquery.dataTables.min.js"></script>
<script src="https://cdn.datatables.net/1.10.24/js/dataTables.bootstrap4.min.js"></script>
<script src="https://cdn.datatables.net/buttons/2.2.3/js/dataTables.buttons.min.js"></script>
<script src="https://cdn.datatables.net/buttons/2.2.3/js/buttons.bootstrap4.min.js"></script>
<script>
$(document).ready(function() {
    // Initialize DataTables for all tables
    const tableConfigs = {
        irbSubmissionsTable: {
            order: [[1, 'desc']]
        },
        irbReviewsTable: {
            dom: 'Bfrtip',
            buttons: ['copy', 'excel', 'csv'],
            order: [[1, 'desc']]
        },
        rcSubmissionsTable: {
            order: [[1, 'desc']]
        },
        rcReviewsTable: {
            dom: 'Bfrtip',
            buttons: ['copy', 'excel', 'csv'],
            order: [[1, 'desc']]
        }
    };

    // Initialize all tables with their specific configurations
    Object.keys(tableConfigs).forEach(tableId => {
        const table = $(`#${tableId}`);
        if (table.length) {
            table.DataTable({
                processing: true,
                serverSide: false,
                pageLength: 10,
                ...tableConfigs[tableId]
            });
        }
    });

    // Handle toggle visibility buttons
    $('.toggle-visibility-btn').on('click', function(e) {
        e.preventDefault();
        
        const btn = $(this);
        const submissionId = btn.data('submission-id');
        const toggleType = btn.data('toggle-type');
        
        $.ajax({
            url: `/review/submission/${submissionId}/toggle-visibility/`,
            method: 'POST',
            data: {
                toggle_type: toggleType,
                csrfmiddlewaretoken: $('[name=csrfmiddlewaretoken]').val()
            },
            success: function(response) {
                if (response.visible) {
                    btn.removeClass('btn-secondary').addClass('btn-success');
                } else {
                    btn.removeClass('btn-success').addClass('btn-secondary');
                }
            },
            error: function(xhr) {
                alert('Error toggling visibility');
            }
        });
    });
});
</script>
{% endblock %}

# Contents from: .\templates\review\decline_review.html
{% extends 'users/base.html' %}
{% load crispy_forms_tags %}

{% block title %}Decline Review Request{% endblock %}

{% block content %}
<div class="container mt-4">
    <div class="row">
        <div class="col-md-8 offset-md-2">
            <div class="card">
                <div class="card-header bg-danger text-white">
                    <h2 class="mb-0">Decline Review Request</h2>
                </div>
                <div class="card-body">
                    <!-- Review Details -->
                    <div class="alert alert-info">
                        <h5>Review Details</h5>
                        <p><strong>Submission:</strong> {{ review_request.submission.title }}</p>
                        <p><strong>Requested By:</strong> {{ review_request.requested_by.userprofile.full_name }}</p>
                        <p><strong>Deadline:</strong> {{ review_request.deadline|date:"F d, Y" }}</p>
                        {% if review_request.message %}
                        <p><strong>Original Request Message:</strong></p>
                        <div class="border-left pl-3">{{ review_request.message|linebreaks }}</div>
                        {% endif %}
                    </div>

                    <form method="post" novalidate>
                        {% csrf_token %}
                        
                        <!-- Reason -->
                        <div class="mb-3">
                            <label for="reason" class="form-label required">Reason for Declining</label>
                            <textarea class="form-control" 
                                      id="reason" 
                                      name="reason" 
                                      rows="4"
                                      required
                                      placeholder="Please provide a detailed reason for declining this review request..."></textarea>
                            <div class="form-text">This message will be sent to the requester and the primary investigator.</div>
                        </div>

                        <!-- Confirmation Checkbox -->
                        <div class="mb-3">
                            <div class="form-check">
                                <input class="form-check-input" 
                                       type="checkbox" 
                                       id="confirm" 
                                       required>
                                <label class="form-check-label" for="confirm">
                                    I confirm that I want to decline this review request
                                </label>
                            </div>
                        </div>

                        <!-- Submit Buttons -->
                        <div class="d-grid gap-2 d-md-flex justify-content-md-end">
                            <a href="{% url 'review:review_dashboard' %}" 
                               class="btn btn-secondary me-md-2">
                                <i class="fas fa-arrow-left"></i> Cancel
                            </a>
                            <button type="submit" 
                                    class="btn btn-danger" 
                                    id="submitBtn" 
                                    disabled>
                                <i class="fas fa-times"></i> Decline Review
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block page_specific_js %}
<script>
    document.addEventListener('DOMContentLoaded', function() {
        const form = document.querySelector('form');
        const reasonInput = document.getElementById('reason');
        const confirmCheckbox = document.getElementById('confirm');
        const submitBtn = document.getElementById('submitBtn');

        // Enable/disable submit button based on form state
        function updateSubmitButton() {
            submitBtn.disabled = !(
                reasonInput.value.trim().length >= 10 && 
                confirmCheckbox.checked
            );
        }

        reasonInput.addEventListener('input', updateSubmitButton);
        confirmCheckbox.addEventListener('change', updateSubmitButton);

        // Form validation
        form.addEventListener('submit', function(e) {
            if (!reasonInput.value.trim()) {
                e.preventDefault();
                alert('Please provide a reason for declining.');
                reasonInput.focus();
                return false;
            }

            if (!confirmCheckbox.checked) {
                e.preventDefault();
                alert('Please confirm that you want to decline this review.');
                return false;
            }

            if (reasonInput.value.trim().length < 10) {
                e.preventDefault();
                alert('Please provide a more detailed reason (at least 10 characters).');
                reasonInput.focus();
                return false;
            }
        });
    });
</script>
{% endblock %}

# Contents from: .\templates\review\forward_review.html
{# review/templates/review/forward_review.html #}
{% extends 'users/base.html' %}
{% load static %}

{% block title %}Forward Review Request{% endblock %}

{% block page_specific_css %}
<style>
    .review-chain {
        position: relative;
        margin-bottom: 2rem;
    }
    .chain-item {
        display: flex;
        align-items: center;
        margin-bottom: 1rem;
    }
    .chain-connector {
        position: absolute;
        left: 15px;
        top: 30px;
        bottom: 0;
        width: 2px;
        background-color: #dee2e6;
    }
    .chain-node {
        width: 32px;
        height: 32px;
        border-radius: 50%;
        background-color: #007bff;
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-right: 1rem;
        position: relative;
        z-index: 1;
    }
    .chain-content {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        flex-grow: 1;
    }
    .reviewer-select {
        min-height: 200px;
    }
    .selected-reviewers {
        margin-top: 1rem;
        padding: 1rem;
        background-color: #f8f9fa;
        border-radius: 0.5rem;
    }
    .selected-reviewer {
        display: inline-block;
        background-color: #e9ecef;
        padding: 0.25rem 0.5rem;
        border-radius: 0.25rem;
        margin: 0.25rem;
    }
</style>
{% endblock %}

{% block content %}
<div class="container mt-4">
    <div class="row">
        <div class="col-md-8">
            <!-- Main Forwarding Form -->
            <div class="card">
                <div class="card-header">
                    <h2>Forward Review Request</h2>
                </div>
                <div class="card-body">
                    <!-- Submission Info -->
                    <div class="alert alert-info">
                        <h5>Submission Details</h5>
                        <p><strong>Title:</strong> {{ review_request.submission.title }}</p>
                        <p><strong>Primary Investigator:</strong> 
                           {{ review_request.submission.primary_investigator.userprofile.full_name }}</p>
                        <p><strong>Study Type:</strong> 
                           {{ review_request.submission.study_type.name }}</p>
                        <p><strong>Current Status:</strong> 
                           <span class="badge bg-{{ review_request.submission.status|lower }}">
                               {{ review_request.submission.get_status_display }}
                           </span>
                        </p>
                    </div>

                    <form method="post" class="needs-validation" novalidate>
                        {% csrf_token %}
                        
                        <!-- Reviewer Selection -->
                        <div class="mb-3">
                            <label class="form-label required">Select Reviewers</label>
                            <select name="reviewers" multiple class="form-select reviewer-select" required>
                                {% for reviewer in available_reviewers %}
                                <option value="{{ reviewer.id }}">
                                    {{ reviewer.userprofile.full_name }} 
                                    ({{ reviewer.groups.first.name }})
                                </option>
                                {% endfor %}
                            </select>
                            <div class="form-text">
                                Hold Ctrl/Cmd to select multiple reviewers
                            </div>
                        </div>

                        <!-- Selected Reviewers Preview -->
                        <div class="selected-reviewers d-none">
                            <h6>Selected Reviewers:</h6>
                            <div id="selectedReviewersList"></div>
                        </div>

                        <!-- Deadline -->
                        <div class="mb-3">
                            <label for="deadline" class="form-label required">Review Deadline</label>
                            <input type="date" 
                                   class="form-control" 
                                   id="deadline" 
                                   name="deadline"
                                   min="{{ min_date }}"
                                   value="{{ suggested_date }}"
                                   required>
                        </div>

                        <!-- Message -->
                        <div class="mb-3">
                            <label for="message" class="form-label required">Message to Reviewers</label>
                            <textarea class="form-control" 
                                      id="message" 
                                      name="message" 
                                      rows="4"
                                      required></textarea>
                        </div>

                        <!-- Forward Permission -->
                        <div class="mb-3">
                            <div class="form-check">
                                <input class="form-check-input" 
                                       type="checkbox" 
                                       id="allow_forwarding" 
                                       name="allow_forwarding" 
                                       value="true">
                                <label class="form-check-label" for="allow_forwarding">
                                    Allow these reviewers to forward to others
                                </label>
                            </div>
                        </div>

                        <!-- Submit Buttons -->
                        <div class="d-grid gap-2 d-md-flex justify-content-md-end">
                            <button type="button" 
                                    class="btn btn-secondary me-md-2" 
                                    onclick="history.back()">
                                Cancel
                            </button>
                            <button type="submit" class="btn btn-primary">
                                Forward Review Request
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>

        <div class="col-md-4">
            <!-- Review Chain Visualization -->
            <div class="card">
                <div class="card-header">
                    <h5 class="card-t

# Contents from: .\templates\review\irb_dashboard.html
{% extends 'base.html' %}
{% load static %}
{% load review_tags %}

{% block extra_css %}
<link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.10.24/css/dataTables.bootstrap4.min.css">
<link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/buttons/2.2.3/css/buttons.bootstrap4.min.css">
<style>
    .btn-green {
        background-color: #28a745;
        border-color: #28a745;
        color: #fff;
    }
    .btn-green:hover {
        background-color: #218838;
        border-color: #1e7e34;
        color: #fff;
    }
</style>
{% endblock %}

{% block content %}
<div class="container">
    <h2 class="mb-4">IRB Dashboard</h2>
    
    <!-- IRB Review Queue -->
    <div class="card mb-4">
        <div class="card-header">
            <h3 class="card-title mb-0">IRB Review Queue</h3>
        </div>
        <div class="card-body">
            {% if irb_submissions %}
                <div class="table-responsive">
                    <table id="irbSubmissionsTable" class="table table-hover">
                        <thead>
                            <tr>
                                <th>Title</th>
                                <th>Submission Date</th>
                                <th>Primary Investigator</th>
                                <th>Study Type</th>
                                <th>Status</th>
                                <th>Visibility</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for submission in irb_submissions %}
                            <tr>
                                <td>{{ submission.title }}</td>
                                <td>{{ submission.date_submitted|date:"Y-m-d" }}</td>
                                <td>{{ submission.primary_investigator.userprofile.full_name }}</td>
                                <td>{{ submission.study_type }}</td>
                                <td>{{ submission.get_status_display }}</td>
                                <td>
                                    <button class="toggle-visibility-btn btn {% if submission.show_in_irb %}btn-success{% else %}btn-secondary{% endif %}"
                                            data-submission-id="{{ submission.id }}"
                                            data-toggle-type="irb">
                                        Toggle IRB
                                    </button>
                                    <button class="toggle-visibility-btn btn {% if submission.show_in_rc %}btn-success{% else %}btn-secondary{% endif %}"
                                            data-submission-id="{{ submission.id }}"
                                            data-toggle-type="rc">
                                        Toggle RC
                                    </button>
                                </td>
                                <td>
                                    <a href="{% url 'review:review_summary' submission.pk %}" 
                                       class="btn btn-success btn-sm">View Details</a>
                                    {% if submission.status == 'under_review' %}
                                        <a href="{% url 'review:process_decision' submission.pk %}" 
                                           class="btn btn-primary btn-sm">Make Decision</a>
                                    {% endif %}
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            {% else %}
                <p class="mb-0">No submissions requiring IRB review.</p>
            {% endif %}
        </div>
    </div>

    <!-- Pending IRB Decisions -->
    <div class="card mb-4">
        <div class="card-header">
            <h3 class="card-title mb-0">Pending IRB Decisions</h3>
        </div>
        <div class="card-body">
            {% if pending_irb_decisions %}
                <div class="table-responsive">
                    <table id="pendingIRBDecisionsTable" class="table table-hover">
                        <thead>
                            <tr>
                                <th>Title</th>
                                <th>Submission Date</th>
                                <th>Primary Investigator</th>
                                <th>Study Type</th>
                                <th>Requests</th>
                                <th>Days</th>
                                <th>✅</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for submission in pending_irb_decisions %}
                            <tr>
                                <td>{{ submission.title }}</td>
                                <td>{{ submission.date_submitted|date:"Y-m-d" }}</td>
                                <td>{{ submission.primary_investigator.userprofile.full_name }}</td>
                                <td>{{ submission.study_type }}</td>
                                <td>
                                    {% if submission.review_requests.exists %}
                                        <ul class="list-unstyled mb-0">
                                        {% for request in submission.review_requests.all %}
                                            <li>
                                                <strong>
                                                    <a href="{% url 'messaging:compose' %}?recipient={{ request.requested_to.id }}&submission={{ submission.id }}" 
                                                       class="text-primary text-decoration-none">
                                                        {{ request.requested_to.get_full_name }}
                                                    </a>
                                                </strong>
                                            </li>
                                        {% endfor %}
                                        </ul>
                                    {% else %}
                                        No requests yet
                                    {% endif %}
                                </td>
                                <td>
                                    {% if submission.review_requests.exists %}
                                        <ul class="list-unstyled mb-0">
                                        {% for request in submission.review_requests.all %}
                                            <li>
                                                {% with days=request.created_at|timesince_in_days %}
                                                    {{ days }}
                                                {% endwith %}
                                            </li>
                                        {% endfor %}
                                        </ul>
                                    {% else %}
                                        -
                                    {% endif %}
                                </td>
                                <td>
                                    {% if submission.review_requests.exists %}
                                        <ul class="list-unstyled mb-0">
                                        {% for request in submission.review_requests.all %}
                                            <li>
                                                {% if request.status == 'completed' %}
                                                    <span class="text-success">✅</span>
                                                {% elif request.status == 'declined' %}
                                                    <span class="text-danger">❌</span>
                                                {% elif request.status == 'pending' %}
                                                    <span class="text-warning">⏳</span>
                                                {% else %}
                                                    <span class="text-secondary">-</span>
                                                {% endif %}
                                            </li>
                                        {% endfor %}
                                        </ul>
                                    {% else %}
                                        -
                                    {% endif %}
                                </td>
                                <td>
                                    <a href="{% url 'review:review_summary' submission.pk %}" class="btn btn-success btn-sm">Details</a>
                                    <a href="{% url 'review:process_decision' submission.pk %}" class="btn btn-primary btn-sm">Make Decision</a>
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            {% else %}
                <p class="mb-0">No submissions pending IRB decision.</p>
            {% endif %}
        </div>
    </div>

    <!-- My IRB Reviews -->
    <div class="card mb-4">
        <div class="card-header">
            <h3 class="card-title mb-0">My IRB Reviews</h3>
        </div>
        <div class="card-body">
            {% if irb_reviews %}
                <div class="table-responsive">
                    <table id="irbReviewsTable" class="table table-hover">
                        <thead>
                            <tr>
                                <th>Title</th>
                                <th>Primary Investigator</th>
                                <th>Requested By</th>
                                <th>Status</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for review in irb_reviews %}
                            <tr>
                                <td>{{ review.submission.title }}</td>
                                <td>{{ review.submission.primary_investigator.userprofile.full_name }}</td>
                                <td>{{ review.requested_by.userprofile.full_name }}</td>
                                <td>{{ review.get_status_display }}</td>
                                <td>
                                    {% if review.requested_to == user or review.requested_by == user %}
                                        <a href="{% url 'review:view_review' review.id %}" 
                                           class="btn btn-info btn-sm">View Review</a>
                                    {% endif %}
                                    {% if review.requested_to == user and review.status == 'pending' %}
                                        <a href="{% url 'review:submit_review' review.id %}" 
                                           class="btn btn-primary btn-sm">Submit Review</a>
                                    {% endif %}
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            {% else %}
                <p class="mb-0">No IRB reviews assigned.</p>
            {% endif %}
        </div>
    </div>
</div>
{% endblock %}

{% block page_specific_js %}
<script src="https://cdn.datatables.net/1.10.24/js/jquery.dataTables.min.js"></script>
<script src="https://cdn.datatables.net/1.10.24/js/dataTables.bootstrap4.min.js"></script>
<script src="https://cdn.datatables.net/buttons/2.2.3/js/dataTables.buttons.min.js"></script>
<script src="https://cdn.datatables.net/buttons/2.2.3/js/buttons.bootstrap4.min.js"></script>
<script>
$(document).ready(function() {
    // Initialize DataTables for all tables
    const tableConfigs = {
        irbSubmissionsTable: {
            order: [[1, 'desc']]
        },
        irbReviewsTable: {
            dom: 'Bfrtip',
            buttons: ['copy', 'excel', 'csv'],
            order: [[1, 'desc']]
        },
        pendingIRBDecisionsTable: {
            order: [[1, 'desc']]
        }
    };

    // Initialize all tables with their specific configurations
    Object.keys(tableConfigs).forEach(tableId => {
        const table = $(`#${tableId}`);
        if (table.length) {
            table.DataTable({
                processing: true,
                serverSide: false,
                pageLength: 10,
                ...tableConfigs[tableId]
            });
        }
    });

    // Handle toggle visibility buttons
    $('.toggle-visibility-btn').on('click', function(e) {
        e.preventDefault();
        
        const btn = $(this);
        const submissionId = btn.data('submission-id');
        const toggleType = btn.data('toggle-type');
        
        $.ajax({
            url: `/review/submission/${submissionId}/toggle-visibility/`,
            method: 'POST',
            data: {
                toggle_type: toggleType,
                csrfmiddlewaretoken: $('[name=csrfmiddlewaretoken]').val()
            },
            success: function(response) {
                if (response.visible) {
                    btn.removeClass('btn-secondary').addClass('btn-success');
                } else {
                    btn.removeClass('btn-success').addClass('btn-secondary');
                }
            },
            error: function(xhr) {
                alert('Error toggling visibility');
            }
        });
    });
});
</script>
{% endblock %}

# Contents from: .\templates\review\my_reviews.html
# templates/reviews/my_reviews.html
{% extends 'base.html' %}

{% block content %}
<div class="container mt-4">
    <h2>My Assigned Reviews</h2>
    {% if reviews %}
        <div class="list-group">
        {% for review in reviews %}
            <a href="{% url 'review_detail' review.review_id %}" class="list-group-item list-group-item-action">
                <div class="d-flex w-100 justify-content-between">
                    <h5 class="mb-1">{{ review.title }}</h5>
                    <small>Status: {{ review.status }}</small>
                </div>
                <small>Assigned: {{ review.created_at|date }}</small>
            </a>
        {% endfor %}
        </div>
    {% else %}
        <p>No reviews assigned yet.</p>
    {% endif %}
</div>
{% endblock %}

# Contents from: .\templates\review\osar_dashboard.html
{% extends 'base.html' %}
{% load static %}
{% load review_tags %}

{% block extra_css %}
<link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.10.24/css/dataTables.bootstrap4.min.css">
<link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/buttons/2.2.3/css/buttons.bootstrap4.min.css">
<style>
    .btn-green {
        background-color: #28a745;
        border-color: #28a745;
        color: #fff;
    }
    .btn-green:hover {
        background-color: #218838;
        border-color: #1e7e34;
        color: #fff;
    }
</style>
{% endblock %}

{% block content %}
<div class="container">
    <h2 class="mb-4">OSAR Dashboard</h2>

    <!-- Submissions Needing Review -->
    <div class="card mb-4">
        <div class="card-header">
            <h3 class="card-title mb-0">Submissions Needing Review</h3>
        </div>
        <div class="card-body">
            {% if osar_submissions %}
                <div class="table-responsive">
                    <table id="osarSubmissionsTable" class="table table-hover">
                        <thead>
                            <tr>
                                <th>Title</th>
                                <th>Submission Date</th>
                                <th>Primary Investigator</th>
                                <th>Study Type</th>
                                <th>Status</th>
                                <th>Visibility</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for submission in osar_submissions %}
                            <tr>
                                <td>{{ submission.title }}</td>
                                <td>{{ submission.date_submitted|date:"Y-m-d" }}</td>
                                <td>{{ submission.primary_investigator.userprofile.full_name }}</td>
                                <td>{{ submission.study_type }}</td>
                                <td>{{ submission.get_status_display }}</td>
                                <td>
                                    <button class="toggle-visibility-btn btn {% if submission.show_in_irb %}btn-success{% else %}btn-secondary{% endif %}"
                                            data-submission-id="{{ submission.id }}"
                                            data-toggle-type="irb">
                                        Toggle IRB
                                    </button>
                                    <button class="toggle-visibility-btn btn {% if submission.show_in_rc %}btn-success{% else %}btn-secondary{% endif %}"
                                            data-submission-id="{{ submission.id }}"
                                            data-toggle-type="rc">
                                        Toggle RC
                                    </button>
                                </td>
                                <td>
                                    <a href="{% url 'review:create_review_request' submission.pk %}" class="btn btn-primary btn-sm">Create Review Request</a>
                                    <a href="{% url 'review:review_summary' submission.pk %}" class="btn btn-success btn-sm">Details</a>
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            {% else %}
                <p class="mb-0">No submissions currently need review.</p>
            {% endif %}
        </div>
    </div>

    <!-- OSAR Reviews -->
    <div class="card mb-4">
        <div class="card-header">
            <h3 class="card-title mb-0">My OSAR Reviews</h3>
        </div>
        <div class="card-body">
            {% if osar_reviews %}
                <div class="table-responsive">
                    <table id="osarReviewsTable" class="table table-hover">
                        <thead>
                            <tr>
                                <th>Title</th>
                                <th>Primary Investigator</th>
                                <th>Requested By</th>
                                <th>Status</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for review in osar_reviews %}
                            <tr>
                                <td>{{ review.submission.title }}</td>
                                <td>{{ review.submission.primary_investigator.userprofile.full_name }}</td>
                                <td>{{ review.requested_by.userprofile.full_name }}</td>
                                <td>{{ review.get_status_display }}</td>
                                <td>
                                    {% if review.requested_to == user or review.requested_by == user %}
                                        <a href="{% url 'review:view_review' review.id %}" class="btn btn-info btn-sm">View Review</a>
                                    {% endif %}
                                    {% if review.requested_to == user and review.status == 'pending' %}
                                        <a href="{% url 'review:submit_review' review.id %}" class="btn btn-primary btn-sm">Submit Review</a>
                                    {% endif %}
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            {% else %}
                <p class="mb-0">No OSAR reviews assigned.</p>
            {% endif %}
        </div>
    </div>
</div>
{% endblock %}

{% block page_specific_js %}
<script src="https://cdn.datatables.net/1.10.24/js/jquery.dataTables.min.js"></script>
<script src="https://cdn.datatables.net/1.10.24/js/dataTables.bootstrap4.min.js"></script>
<script src="https://cdn.datatables.net/buttons/2.2.3/js/dataTables.buttons.min.js"></script>
<script src="https://cdn.datatables.net/buttons/2.2.3/js/buttons.bootstrap4.min.js"></script>
<script>
$(document).ready(function() {
    // Initialize DataTables
    $('#osarSubmissionsTable').DataTable({
        order: [[1, 'desc']],
        pageLength: 10
    });
    $('#osarReviewsTable').DataTable({
        order: [[1, 'desc']],
        pageLength: 10
    });

    // Handle toggle visibility buttons
    $('.toggle-visibility-btn').on('click', function(e) {
        e.preventDefault();
        const btn = $(this);
        const submissionId = btn.data('submission-id');
        const toggleType = btn.data('toggle-type');
        
        $.ajax({
            url: `/review/submission/${submissionId}/toggle-visibility/`,
            method: 'POST',
            data: {
                toggle_type: toggleType,
                csrfmiddlewaretoken: $('[name=csrfmiddlewaretoken]').val()
            },
            success: function(response) {
                if (response.visible) {
                    btn.removeClass('btn-secondary').addClass('btn-success');
                } else {
                    btn.removeClass('btn-success').addClass('btn-secondary');
                }
            },
            error: function(xhr) {
                alert('Error toggling visibility');
            }
        });
    });
});
</script>
{% endblock %}

# Contents from: .\templates\review\pdf\review_template.html
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body {
            font-family: Helvetica, Arial, sans-serif;
            font-size: 11px;
            line-height: 1.4;
        }
        .header {
            text-align: center;
            margin-bottom: 20px;
        }
        .title {
            font-size: 18px;
            font-weight: bold;
            margin: 10px 0;
        }
        .section {
            margin: 15px 0;
        }
        .section-title {
            font-size: 14px;
            font-weight: bold;
            margin-bottom: 10px;
        }
        .field {
            margin: 5px 0;
        }
        .field-label {
            font-weight: bold;
        }
        .footer {
            margin-top: 30px;
            font-size: 9px;
            text-align: center;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="title">Review Report</div>
    </div>

    <div class="section">
        <div class="section-title">Submission Information</div>
        <div class="field">
            <span class="field-label">Title:</span> {{ review.review_request.submission.title }}
        </div>
        <div class="field">
            <span class="field-label">Primary Investigator:</span> {{ review.review_request.submission.primary_investigator.userprofile.full_name }}
        </div>
        <div class="field">
            <span class="field-label">Study Type:</span> {{ review.review_request.submission.study_type }}
        </div>
        <div class="field">
            <span class="field-label">IRB Number:</span> {{ review.review_request.submission.irb_number|default:"Not provided" }}
        </div>
    </div>

    <div class="section">
        <div class="section-title">Review Details</div>
        <div class="field">
            <span class="field-label">Reviewer:</span> {{ review.reviewer.userprofile.full_name }}
        </div>
        <div class="field">
            <span class="field-label">Status:</span> {{ review.is_completed|yesno:"Completed,In Progress" }}
        </div>
        <div class="field">
            <span class="field-label">Date Submitted:</span> {{ review.date_submitted|date:"Y-m-d H:i"|default:"Not submitted" }}
        </div>
    </div>

    <div class="section">
        <div class="section-title">Form Responses</div>
        {% for form_response in review.formresponse_set.all %}
            <div class="field">
                <div class="field-label">{{ form_response.form.name }}</div>
                {% for field_name, value in form_response.response_data.items %}
                    <div style="margin-left: 20px;">
                        <strong>{{ field_name }}:</strong>
                        {% if value|length > 0 %}
                            {% if value|first|stringformat:"s"|first == "[" %}
                                {{ value|join:", " }}
                            {% else %}
                                {{ value }}
                            {% endif %}
                        {% else %}
                            No response
                        {% endif %}
                    </div>
                {% endfor %}
            </div>
        {% endfor %}
    </div>

    {% if review.comments %}
    <div class="section">
        <div class="section-title">Additional Comments</div>
        <div>{{ review.comments|linebreaks }}</div>
    </div>
    {% endif %}

    <div class="footer">
        iRN is a property of the Artificial Intelligence and Data Innovation (AIDI) office 
        in collaboration with the Office of Scientific Affairs (OSAR) office @ King Hussein 
        Cancer Center, Amman - Jordan. Keep this document confidential.
    </div>
</body>
</html> 

# Contents from: .\templates\review\process_decision.html
{% extends 'base.html' %}
{% load crispy_forms_tags %}

{% block title %}Process IRB Decision{% endblock %}

{% block content %}
<div class="container mt-4">
    <div class="row">
        <div class="col-md-8 offset-md-2">
            <div class="card">
                <!-- ... process decision content ... -->
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block page_specific_js %}
<script>
    // ... your JavaScript code ...
</script>
{% endblock %} 

# Contents from: .\templates\review\rc_dashboard.html
{% extends 'base.html' %}
{% load static %}
{% load review_tags %}

{% block extra_css %}
<link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.10.24/css/dataTables.bootstrap4.min.css">
<link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/buttons/2.2.3/css/buttons.bootstrap4.min.css">
<style>
    .btn-green {
        background-color: #28a745;
        border-color: #28a745;
        color: #fff;
    }
    .btn-green:hover {
        background-color: #218838;
        border-color: #1e7e34;
        color: #fff;
    }
</style>
{% endblock %}

{% block content %}
<div class="container">
    <h2 class="mb-4">RC Dashboard</h2>
    
    <!-- RC Review Queue -->
    <div class="card mb-4">
        <div class="card-header">
            <h3 class="card-title mb-0">RC Review Queue</h3>
        </div>
        <div class="card-body">
            {% if rc_submissions %}
                <div class="table-responsive">
                    <table id="rcSubmissionsTable" class="table table-hover">
                        <thead>
                            <tr>
                                <th>Title</th>
                                <th>Submission Date</th>
                                <th>Primary Investigator</th>
                                <th>Study Type</th>
                                <th>Status</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for submission in rc_submissions %}
                            <tr>
                                <td>{{ submission.title }}</td>
                                <td>{{ submission.date_submitted|date:"Y-m-d" }}</td>
                                <td>{{ submission.primary_investigator.userprofile.full_name }}</td>
                                <td>{{ submission.study_type }}</td>
                                <td>{{ submission.get_status_display }}</td>
                                <td>
                                    <a href="{% url 'review:review_summary' submission.pk %}" 
                                       class="btn btn-success btn-sm">View Details</a>
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            {% else %}
                <p class="mb-0">No submissions requiring RC review.</p>
            {% endif %}
        </div>
    </div>

    <!-- My Department's Submissions -->
    <div class="card mb-4">
        <div class="card-header">
            <h3 class="card-title mb-0">My Department's Submissions</h3>
        </div>
        <div class="card-body">
            {% if department_submissions %}
                <div class="table-responsive">
                    <table id="departmentSubmissionsTable" class="table table-hover">
                        <thead>
                            <tr>
                                <th>Title</th>
                                <th>Submission Date</th>
                                <th>Primary Investigator</th>
                                <th>Study Type</th>
                                <th>Requests</th>
                                <th>Days</th>
                                <th>✅</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for submission in department_submissions %}
                            <tr>
                                <td>{{ submission.title }}</td>
                                <td>{{ submission.date_submitted|date:"Y-m-d" }}</td>
                                <td>{{ submission.primary_investigator.userprofile.full_name }}</td>
                                <td>{{ submission.study_type }}</td>
                                <td>
                                    {% if submission.review_requests.exists %}
                                        <ul class="list-unstyled mb-0">
                                        {% for request in submission.review_requests.all %}
                                            <li>
                                                <strong>
                                                    <a href="{% url 'messaging:compose' %}?recipient={{ request.requested_to.id }}&submission={{ submission.id }}" 
                                                       class="text-primary text-decoration-none">
                                                        {{ request.requested_to.get_full_name }}
                                                    </a>
                                                </strong>
                                            </li>
                                        {% endfor %}
                                        </ul>
                                    {% else %}
                                        No requests yet
                                    {% endif %}
                                </td>
                                <td>
                                    {% if submission.review_requests.exists %}
                                        <ul class="list-unstyled mb-0">
                                        {% for request in submission.review_requests.all %}
                                            <li>
                                                {% with days=request.created_at|timesince_in_days %}
                                                    {{ days }}
                                                {% endwith %}
                                            </li>
                                        {% endfor %}
                                        </ul>
                                    {% else %}
                                        -
                                    {% endif %}
                                </td>
                                <td>
                                    {% if submission.review_requests.exists %}
                                        <ul class="list-unstyled mb-0">
                                        {% for request in submission.review_requests.all %}
                                            <li>
                                                {% if request.status == 'completed' %}
                                                    <span class="text-success">✅</span>
                                                {% elif request.status == 'declined' %}
                                                    <span class="text-danger">❌</span>
                                                {% elif request.status == 'pending' %}
                                                    <span class="text-warning">⏳</span>
                                                {% else %}
                                                    <span class="text-secondary">-</span>
                                                {% endif %}
                                            </li>
                                        {% endfor %}
                                        </ul>
                                    {% else %}
                                        -
                                    {% endif %}
                                </td>
                                <td>
                                    <a href="{% url 'review:review_summary' submission.pk %}" class="btn btn-success btn-sm">Details</a>
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            {% else %}
                <p class="mb-0">No submissions in your department.</p>
            {% endif %}
        </div>
    </div>

    <!-- My RC Reviews -->
    <div class="card mb-4">
        <div class="card-header">
            <h3 class="card-title mb-0">My RC Reviews</h3>
        </div>
        <div class="card-body">
            {% if rc_reviews %}
                <div class="table-responsive">
                    <table id="rcReviewsTable" class="table table-hover">
                        <thead>
                            <tr>
                                <th>Title</th>
                                <th>Primary Investigator</th>
                                <th>Requested By</th>
                                <th>Status</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for review in rc_reviews %}
                            <tr>
                                <td>{{ review.submission.title }}</td>
                                <td>{{ review.submission.primary_investigator.userprofile.full_name }}</td>
                                <td>{{ review.requested_by.userprofile.full_name }}</td>
                                <td>{{ review.get_status_display }}</td>
                                <td>
                                    {% if review.requested_to == user or review.requested_by == user %}
                                        <a href="{% url 'review:view_review' review.id %}" 
                                           class="btn btn-info btn-sm">View Review</a>
                                    {% endif %}
                                    {% if review.requested_to == user and review.status == 'pending' %}
                                        <a href="{% url 'review:submit_review' review.id %}" 
                                           class="btn btn-primary btn-sm">Submit Review</a>
                                    {% endif %}
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            {% else %}
                <p class="mb-0">No RC reviews assigned.</p>
            {% endif %}
        </div>
    </div>
</div>
{% endblock %}

{% block page_specific_js %}
<script src="https://cdn.datatables.net/1.10.24/js/jquery.dataTables.min.js"></script>
<script src="https://cdn.datatables.net/1.10.24/js/dataTables.bootstrap4.min.js"></script>
<script src="https://cdn.datatables.net/buttons/2.2.3/js/dataTables.buttons.min.js"></script>
<script src="https://cdn.datatables.net/buttons/2.2.3/js/buttons.bootstrap4.min.js"></script>
<script>
$(document).ready(function() {
    // Initialize DataTables for all tables
    const tableConfigs = {
        rcSubmissionsTable: {
            order: [[1, 'desc']]
        },
        departmentSubmissionsTable: {
            order: [[1, 'desc']]
        },
        rcReviewsTable: {
            dom: 'Bfrtip',
            buttons: ['copy', 'excel', 'csv'],
            order: [[1, 'desc']]
        }
    };

    // Initialize all tables with their specific configurations
    Object.keys(tableConfigs).forEach(tableId => {
        const table = $(`#${tableId}`);
        if (table.length) {
            table.DataTable({
                processing: true,
                serverSide: false,
                pageLength: 10,
                ...tableConfigs[tableId]
            });
        }
    });
});
</script>
{% endblock %}

# Contents from: .\templates\review\request_extension.html
{% extends 'users/base.html' %}
{% load crispy_forms_tags %}

{% block title %}Request Review Extension{% endblock %}

{% block content %}
<div class="container mt-4">
    <div class="row">
        <div class="col-md-8 offset-md-2">
            <div class="card">
                <div class="card-header">
                    <h2>Request Review Extension</h2>
                </div>
                <div class="card-body">
                    <!-- Review Details -->
                    <div class="alert alert-info">
                        <h5>Review Details</h5>
                        <p><strong>Submission:</strong> {{ review_request.submission.title }}</p>
                        <p><strong>Current Deadline:</strong> {{ review_request.deadline|date:"F d, Y" }}</p>
                        <p><strong>Days Remaining:</strong> {{ review_request.days_until_deadline }}</p>
                    </div>

                    <form method="post" novalidate>
                        {% csrf_token %}
                        
                        <!-- New Deadline -->
                        <div class="mb-3">
                            <label for="new_deadline" class="form-label">New Deadline</label>
                            <input type="date" 
                                   class="form-control" 
                                   id="new_deadline" 
                                   name="new_deadline"
                                   min="{{ min_date }}"
                                   max="{{ max_date }}"
                                   required>
                            <div class="form-text">Select a new deadline (maximum 30 days extension)</div>
                        </div>

                        <!-- Reason -->
                        <div class="mb-3">
                            <label for="reason" class="form-label">Reason for Extension</label>
                            <textarea class="form-control" 
                                      id="reason" 
                                      name="reason" 
                                      rows="4"
                                      required></textarea>
                            <div class="form-text">Please provide a detailed reason for requesting an extension</div>
                        </div>

                        <!-- Submit Buttons -->
                        <div class="d-grid gap-2 d-md-flex justify-content-md-end">
                            <a href="{% url 'review:review_dashboard' %}" 
                               class="btn btn-secondary me-md-2">
                                <i class="fas fa-times"></i> Cancel
                            </a>
                            <button type="submit" class="btn btn-primary">
                                <i class="fas fa-clock"></i> Request Extension
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block page_specific_js %}
<script>
    document.addEventListener('DOMContentLoaded', function() {
        // Validate form before submission
        document.querySelector('form').addEventListener('submit', function(e) {
            var newDeadline = document.getElementById('new_deadline').value;
            var reason = document.getElementById('reason').value;
            
            if (!newDeadline || !reason) {
                e.preventDefault();
                alert('Please fill in all required fields');
                return false;
            }
            
            var selectedDate = new Date(newDeadline);
            var currentDate = new Date();
            
            if (selectedDate <= currentDate) {
                e.preventDefault();
                alert('New deadline must be in the future');
                return false;
            }
        });
    });
</script>
{% endblock %}

# Contents from: .\templates\review\review_dashboard.html
<!-- Update links in your templates -->
<a href="{% url 'review:view_review' review_request.id %}" class="btn btn-primary">
    View Review
</a> 

# Contents from: .\templates\review\review_detail.html

# templates/reviews/review_detail.html
{% extends 'base.html' %}

{% block content %}
<div class="container mt-4">
    <h2>Review #{{ review.review_id }}</h2>
    <div class="card">
        <div class="card-header">
            <h3>{{ review.title }}</h3>
            <span class="badge badge-primary">{{ review.status }}</span>
        </div>
        <div class="card-body">
            <p>{{ review.content }}</p>
            <p><small>Last updated: {{ review.updated_at|date }}</small></p>
        </div>
    </div>
</div>
{% endblock %}

# Contents from: .\templates\review\review_summary.html
{# review/templates/review/review_summary.html #}
{% extends 'base.html' %}

{% block title %}Review Summary - {{ submission.title }}{% endblock %}

{% block content %}
<div class="container">
    <h2>Review Summary for {{ submission.title }}</h2>
    
    {% if review_requests %}
        <div class="card">
            <div class="card-header">
                <h3>Review Requests and Submissions</h3>
            </div>
            <div class="card-body">
                <table class="table" id="reviewSummaryTable">
                    <thead>
                        <tr>
                            <th>Reviewer</th>
                            <th>Requested By</th>
                            <th>Status</th>
                            <th>Submission Date</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for request in review_requests %}
                        <tr>
                            <td>{{ request.requested_to.userprofile.full_name }}</td>
                            <td>{{ request.requested_by.userprofile.full_name }}</td>
                            <td>{{ request.status }}</td>
                            <td>
                                {% if request.review_set.first %}
                                    {{ request.review_set.first.date_submitted }}
                                {% else %}
                                    Not submitted
                                {% endif %}
                            </td>
                            <td>
                                {% if request.review_set.first %}
                                    <a href="{% url 'review:view_review' review_request_id=request.id %}" 
                                       class="btn btn-info btn-sm">View Review</a>
                                    <a href="{% url 'review:download_review_pdf' review_request_id=request.id %}" 
                                       class="btn btn-primary btn-sm">
                                        <i class="fas fa-file-pdf"></i> PDF
                                    </a>
                                {% else %}
                                    <span class="text-muted">Review pending</span>
                                {% endif %}
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>

        <div class="card mt-4">
            <div class="card-header">
                <h3>Submission Versions</h3>
            </div>
            <div class="card-body">
                <table class="table" id="submissionVersionTable">
                    <thead>
                        <tr>
                            <th>Version</th>
                            <th>Submission Date</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for version in version_histories %}
                        <tr>
                            <td>{{ version.version }}</td>
                            <td>{{ version.date }}</td>
                            <td>
                                {% if can_download_pdf %}
                                    {% url 'submission:download_submission_pdf_version' submission_id=submission.temporary_id version=version.version as pdf_url %}
                                    {% if pdf_url %}
                                        <a href="{{ pdf_url }}" class="btn btn-primary btn-sm">
                                            <i class="fas fa-file-pdf"></i> Download PDF
                                        </a>
                                    {% else %}
                                        <button class="btn btn-secondary btn-sm" disabled>
                                            <i class="fas fa-file-pdf"></i> PDF Not Available
                                        </button>
                                    {% endif %}
                                {% else %}
                                    <button class="btn btn-secondary btn-sm" disabled>
                                        <i class="fas fa-lock"></i> No Permission
                                    </button>
                                {% endif %}
                            </td>
                        </tr>
                        {% empty %}
                        <tr>
                            <td colspan="3" class="text-center">No submission versions available.</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>

        {% if can_make_decision %}
            <div class="card mt-4">
                <div class="card-header">
                    <h3>Make IRB Decision</h3>
                </div>
                <div class="card-body">
                    <form method="post" action="{% url 'review:process_decision' submission.id %}">
                        {% csrf_token %}
                        <div class="form-group">
                            <label for="decision">Decision:</label>
                            <select name="decision" id="decision" class="form-control" required>
                                <option value="approved">Approved</option>
                                <option value="revision_required">Revision Required</option>
                                <option value="rejected">Rejected</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label for="comments">Comments:</label>
                            <textarea name="comments" id="comments" class="form-control" rows="4"></textarea>
                        </div>
                        <button type="submit" class="btn btn-primary">Submit Decision</button>
                    </form>
                </div>
            </div>
        {% endif %}
    {% else %}
        <p>No review requests have been created yet.</p>
    {% endif %}
</div>

{% block page_specific_js %}
<script>
$(document).ready(function() {
    $('#reviewSummaryTable').DataTable({
        pageLength: 10,
        order: [[1, 'desc']]
    });
    $('#submissionVersionTable').DataTable({
        pageLength: 10,
        order: [[1, 'desc']]
    });
});
</script>
{% endblock %}
{% endblock %}

# Contents from: .\templates\review\submission_detail.html
<!-- submission/templates/submission_detail.html -->
{% extends 'base.html' %}
{% block content %}
<h2>{{ submission.title }}</h2>
<p>Current Version: {{ submission.version }}</p>
<h3>All Versions</h3>
<ul>
    {% for version in versions %}
        <li>
            Version {{ version.version }} - {{ version.status }} on {{ version.date }}
            <a href="{% url 'submission:view_version' submission.id version.version %}">View</a>
            {% if not forloop.last %}
                <a href="{% url 'submission:compare_versions' submission.id version.version submission.version %}">Compare with Latest</a>
            {% endif %}
        </li>
    {% endfor %}
</ul>
{% endblock %}


# Contents from: .\templates\review\submission_versions.html
{% extends 'users/base.html' %}
{% block content %}
<div class="container mt-4">
    <h1>Review Versions for "{{ submission.title }}"</h1>
    <div class="mb-3">
        <a href="{% url 'review:review_dashboard' %}" class="btn btn-secondary">Back to Dashboard</a>
    </div>
    <table class="table table-striped">
        <thead>
            <tr>
                <th>Version</th>
                <th>Status</th>
                <th>Date</th>
                <th>Actions</th>
            </tr>
        </thead>
        <tbody>
            {% for history in histories %}
            <tr>
                <td>{{ history.version }}</td>
                <td>{{ history.get_status_display }}</td>
                <td>{{ history.date }}</td>
                <td>
                    <a href="{% url 'submission:download_submission_pdf_version' submission.temporary_id history.version %}" class="btn btn-sm btn-secondary">Download PDF</a>
                    {% if not forloop.last %}
                    <a href="{% url 'submission:compare_versions' submission.temporary_id history.version submission.version %}" class="btn btn-sm btn-primary">Compare with Latest</a>
                    {% endif %}
                </td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>
{% endblock %} 

# Contents from: .\templates\review\submit_review.html
<!-- review/templates/review/submit_review.html -->
{% extends 'base.html' %}
{% load crispy_forms_tags %}

{% block content %}
<div class="container mt-4">
    <div class="card mb-4">
        <div class="card-header">
            <h2>Submit Review for {{ review_request.submission.title }}</h2>
            <p class="text-muted">
                Primary Investigator: {{ review_request.submission.primary_investigator.userprofile.full_name }}
            </p>
        </div>
    </div>

    <form method="post" novalidate>
        {% csrf_token %}
        
        {% for form_data in forms_data %}
        <div class="card mb-4">
            <div class="card-header">
                <h3>{{ form_data.template.name }}</h3>
                {% if form_data.template.help_text %}
                <p class="text-muted">{{ form_data.template.help_text }}</p>
                {% endif %}
            </div>
            <div class="card-body">
                {{ form_data.form|crispy }}
            </div>
        </div>
        {% endfor %}

        <div class="card mb-4">
            <div class="card-header">
                <h3>Additional Comments</h3>
            </div>
            <div class="card-body">
                <textarea name="comments" class="form-control" rows="4" 
                          placeholder="Enter any additional comments about this review..."></textarea>
            </div>
        </div>

        <div class="d-grid gap-2 d-md-flex justify-content-md-end mb-4">
            <button type="submit" name="action" value="save_draft" class="btn btn-secondary me-md-2">
                <i class="fas fa-save"></i> Save Draft
            </button>
            <button type="submit" name="action" value="submit" class="btn btn-primary">
                <i class="fas fa-check"></i> Submit Review
            </button>
        </div>
    </form>
</div>
{% endblock %}


# Contents from: .\templates\review\view_review.html
{% extends 'users/base.html' %}
{% load crispy_forms_tags %}

{% block title %}Review Details{% endblock %}

{% block page_specific_css %}
<style>
    .status-badge {
        padding: 0.4em 0.8em;
        border-radius: 0.25rem;
        font-size: 0.875em;
    }
    .form-response {
        margin-bottom: 2rem;
        padding: 1rem;
        border: 1px solid #dee2e6;
        border-radius: 0.25rem;
    }
    .form-response h3 {
        color: #2c3e50;
        font-size: 1.25rem;
        margin-bottom: 1rem;
    }
    .response-field {
        margin-bottom: 1rem;
    }
    .response-field label {
        font-weight: bold;
        color: #495057;
    }
    .response-field .value {
        margin-left: 1rem;
    }
    .metadata {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.25rem;
        margin-bottom: 1rem;
    }
    .metadata-item {
        margin-bottom: 0.5rem;
    }
</style>
{% endblock %}

{% block content %}
<div class="container mt-4">
    <!-- Header Section -->
    <div class="card mb-4 shadow-sm">
        <div class="card-body">
            <div class="row">
                <div class="col-md-8">
                    <h2 class="text-primary mb-2">{{ submission.title }}</h2>
                    <div class="text-muted">
                        <strong>Primary Investigator:</strong> 
                        {{ submission.primary_investigator.get_full_name }}
                    </div>
                    <div class="mt-2">
                        <span class="badge bg-info">Version {{ submission.version }}</span>
                    </div>
                </div>
                <div class="col-md-4 text-md-end">
                    
                </div>
            </div>
        </div>
    </div>

    <!-- Review Header -->
    <div class="card mb-4">
        <div class="card-header">
            <div class="d-flex justify-content-between align-items-center">
                <h2 class="mb-0">Review Details</h2>
                <div>
                    {% if can_edit %}
                    <a href="{% url 'review:submit_review' review.id %}" class="btn btn-primary">
                        <i class="fas fa-edit"></i> Edit Review
                    </a>
                    {% endif %}
                    <a href="{% url 'review:review_dashboard' %}" class="btn btn-secondary">
                        <i class="fas fa-arrow-left"></i> Back to Dashboard
                    </a>
                </div>
            </div>
        </div>
        <div class="card-body">
            <!-- Metadata Section -->
            <div class="metadata">
                <div class="row">
                    <div class="col-md-6">
                        
                        <div class="metadata-item">
                            
                                <strong>Reviewed by: {{ review.reviewer.get_full_name }}</small><br>
                                                          
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="metadata-item">
                            <strong>Submitted:</strong> {{ review.date_submitted|date:"F d, Y H:i" }}
                        </div>
                        <div class="metadata-item">
                            <strong>Status:</strong> 
                            <span class="status-badge status-{{ review_request.status }}">
                                {{ review_request.get_status_display }}
                            </span>
                        </div>
                        <div class="metadata-item">
                            <strong>Requested By:</strong> {{ review_request.requested_by.userprofile.full_name }}
                        </div>
                        <div class="metadata-item">
                            <strong>Requested on:</strong> {{ review_request.created_at|date:"F d, Y" }}
                        </div>
                    </div>
                </div>
            </div>

            <!-- Form Responses -->
            {% if form_responses %}
                {% for response in form_responses %}
                <div class="form-response">
                    <h3>{{ response.form.name }}</h3>
                    {% for field_name, field_value in response.response_data.items %}
                    <div class="response-field">
                        <label>{{ field_name }}:</label>
                        <div class="value">
                            {% if field_value|length > 100 %}
                                <pre class="pre-scrollable">{{ field_value }}</pre>
                            {% else %}
                                {{ field_value }}
                            {% endif %}
                        </div>
                    </div>
                    {% endfor %}
                </div>
                {% endfor %}
            {% else %}
                <div class="alert alert-info">
                    No form responses found for this review.
                </div>
            {% endif %}

            <!-- Comments Section -->
            {% if review.comments %}
            <div class="card mt-4">
                <div class="card-header">
                    <h3 class="mb-0">Additional Comments</h3>
                </div>
                <div class="card-body">
                    {{ review.comments|linebreaks }}
                </div>
            </div>
            {% endif %}
        </div>
    </div>

    <!-- Action Buttons -->
    <div class="card">
        <div class="card-body">
            <div class="d-flex justify-content-between">
                <div>
                    {% if is_requester or is_pi %}
                    <a href="{% url 'messaging:compose_message' %}?related_review={{ review.id }}" 
                       class="btn btn-info">
                        <i class="fas fa-envelope"></i> Contact Reviewer
                    </a>
                    {% endif %}
                </div>
                <div>
                    {% if is_pi or is_requester %}
                    <a href="{% url 'submission:download_submission_pdf' submission.id review.submission_version %}" 
                       class="btn btn-secondary">
                        <i class="fas fa-file-pdf"></i> Download Submission Version
                    </a>
                    {% endif %}
                    <a href="{% url 'review:download_review_pdf' review.review_request.id %}" class="btn btn-primary">
                        <i class="fas fa-file-pdf"></i> Download Review PDF
                    </a>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}

# Contents from: .\__init__.py


# Contents from: .\admin.py
# review/admin.py

from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission
from submission.models import Submission
from .models import ReviewRequest, Review, FormResponse

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['review_id', 'reviewer', 'submission', 'date_submitted']
    search_fields = ['reviewer__username', 'submission__title']
    list_filter = ['date_submitted']

@admin.register(ReviewRequest)
class ReviewRequestAdmin(admin.ModelAdmin):
    list_display = ['submission', 'requested_by', 'requested_to', 'deadline', 'status']
    search_fields = ['submission__title', 'requested_by__username', 'requested_to__username']
    list_filter = ['status', 'deadline']

@admin.register(FormResponse)
class FormResponseAdmin(admin.ModelAdmin):
    list_display = ['review', 'form', 'date_submitted']
    search_fields = ['review__reviewer__username', 'form__name']
    list_filter = ['date_submitted']


# Contents from: .\apps.py
# review/apps.py

from django.apps import AppConfig


class ReviewConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "review"


# Contents from: .\combine.py
import os

def get_files_recursively(directory, extensions):
    """
    Recursively get all files with specified extensions from directory and subdirectories
    """
    file_list = []
    for root, dirs, files in os.walk(directory):
        # Skip migrations directories
        if 'migrations' in root:
            continue
        for file in files:
            # Skip the output file itself
            if file == 'combined.py':
                continue
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
# review/forms.py

from django import forms
from django.utils import timezone
from django.contrib.auth.models import User
from .models import ReviewRequest
from forms_builder.models import DynamicForm
from dal import autocomplete

from django import forms
from django.utils import timezone
from django.contrib.auth.models import User, Group
from django.db.models import Q
from .models import ReviewRequest
from forms_builder.models import DynamicForm
from dal import autocomplete

class ReviewRequestForm(forms.ModelForm):
    requested_to = forms.ModelChoiceField(
        queryset=User.objects.filter(is_active=True),
        widget=forms.Select(attrs={
            'class': 'form-select',
            'data-placeholder': 'Select a reviewer...',
        }),
        label="Select Reviewer",
        help_text="Choose a qualified reviewer for this submission"
    )

    class Meta:
        model = ReviewRequest
        fields = ['requested_to', 'deadline', 'message', 'selected_forms', 'can_forward']
        widgets = {
            'deadline': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'selected_forms': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'can_forward': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, study_type=None, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set up reviewer field to show full name
        self.fields['requested_to'].queryset = User.objects.filter(
            is_active=True
        ).select_related('userprofile').order_by('userprofile__full_name')
        
        self.fields['requested_to'].label_from_instance = lambda user: (
            f"{user.get_full_name() or user.username}"
        )

        # Filter forms for Evaluation study type
        form_queryset = DynamicForm.objects.filter(
            study_types__name='Evaluation'
        ).order_by('order', 'name')
            
        self.fields['selected_forms'].queryset = form_queryset
        self.fields['selected_forms'].widget.attrs.update({
            'class': 'form-control',
            'size': min(10, form_queryset.count()),  # Show up to 10 items
            'multiple': 'multiple'  # Enable multiple selection
        })

class ConflictOfInterestForm(forms.Form):
    conflict_of_interest = forms.ChoiceField(
        choices=[('no', 'No'), ('yes', 'Yes')],
        widget=forms.RadioSelect,
        label='Do you have a conflict of interest with this submission?'
    )
    conflict_details = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': 'Provide details (optional)'}),
        required=False,
        label='Conflict Details'
    )


# Contents from: .\management\commands\setup_review_groups.py
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group

class Command(BaseCommand):
    help = 'Creates required groups for review system'

    def handle(self, *args, **kwargs):
        required_groups = [
            'OSAR',
            'IRB Chair',
            'RC Chair',
            'AHARRP Head'
        ]
        
        for group_name in required_groups:
            group, created = Group.objects.get_or_create(name=group_name)
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully created {group_name} group')
                )
            else:
                self.stdout.write(f'{group_name} group already exists') 

# Contents from: .\models.py
from django.db import models
from django.contrib.auth.models import User
from submission.models import Submission, get_status_choices
from forms_builder.models import DynamicForm
from datetime import datetime
from django.core.cache import cache
from django.utils import timezone
from django.apps import apps
from iRN.constants import get_status_choices

######################
# Status Choice
######################

class StatusChoice(models.Model):
    """Model to store custom status choices."""
    code = models.CharField(max_length=50, unique=True)
    label = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
        verbose_name = 'Status Choice'
        verbose_name_plural = 'Status Choices'

    def __str__(self):
        return self.label

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        cache.delete('review_status_choices')

######################
# Review Request
######################

class ReviewRequest(models.Model):
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE,  related_name='review_requests' )
    submission_version = models.PositiveIntegerField(
        help_text="Version number of the submission being reviewed"
    )
    requested_by = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='review_requests_created'
    )
    requested_to = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='review_requests_received'
    )
    message = models.TextField(blank=True)
    deadline = models.DateField()
    status = models.CharField(
        max_length=50,
        choices=get_status_choices,
        default='pending'
    )
    selected_forms = models.ManyToManyField(DynamicForm)
    conflict_of_interest_declared = models.BooleanField(null=True)
    conflict_of_interest_details = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=1)
    extension_requested = models.BooleanField(default=False)
    proposed_deadline = models.DateField(null=True, blank=True)
    extension_reason = models.TextField(null=True, blank=True)
    
    parent_request = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='child_requests'
    )
    forwarding_chain = models.JSONField(
        default=list,
        help_text="List of users who forwarded this request"
    )
    can_forward = models.BooleanField(
        default=False,
        help_text="Whether this reviewer can forward to others"
    )

    @property
    def is_overdue(self):
        return self.deadline < timezone.now().date()

    @property
    def days_until_deadline(self):
        return (self.deadline - timezone.now().date()).days

    @property
    def has_forwarded_requests(self):
        """Check if this review request has any child requests (has been forwarded)"""
        return self.child_requests.exists()

    @property
    def forward_count(self):
        """Return the number of times this request has been forwarded"""
        return self.child_requests.count()

    def save(self, *args, **kwargs):
        # Ensure submission_version is an integer
        if isinstance(self.submission_version, datetime):
            self.submission_version = self.submission.version
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Review Request for {self.submission} (Version {self.submission_version})"

######################
# Review
######################

class Review(models.Model):
    review_id = models.AutoField(primary_key=True)
    review_request = models.ForeignKey(ReviewRequest, on_delete=models.CASCADE)
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE)
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE)
    submission_version = models.PositiveIntegerField()
    comments = models.TextField(blank=True)
    date_submitted = models.DateTimeField(auto_now_add=True)
    is_archived = models.BooleanField(default=False)

    class Meta:
        permissions = [
            ("view_any_review", "Can view any review regardless of assignment"),
            ("change_submission_status", "Can change submission status"),
        ]

    def __str__(self):
        return f"Review by {self.reviewer} for {self.submission}"

######################
# Form Response
######################

class FormResponse(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE)
    form = models.ForeignKey('forms_builder.DynamicForm', on_delete=models.CASCADE)
    response_data = models.JSONField()
    date_submitted = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Response to {self.form} for {self.review}"






# Contents from: .\tasks.py
# tasks.py
from celery import shared_task
from django.utils import timezone
from datetime import timedelta

@shared_task
def send_review_reminders():
    upcoming_deadlines = ReviewRequest.objects.filter(
        status='pending',
        deadline__lte=timezone.now() + timedelta(days=2)
    )
    for request in upcoming_deadlines:
        send_reminder_email(request)

# Contents from: .\templatetags\review_extras.py
from django import template
from django.utils import timezone
from datetime import datetime

register = template.Library()

@register.filter
def timesince_in_days(value):
    if not value:
        return 0
    
    if isinstance(value, str):
        value = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
    
    now = timezone.now()
    diff = now - value
    return diff.days 

# Contents from: .\templatetags\review_tags.py
# review/templatetags/review_tags.py

from django import template
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime

register = template.Library()

@register.filter
def get_user_name(user_id):
    """Get user's full name from ID."""
    try:
        user = User.objects.select_related('userprofile').get(id=user_id)
        return user.userprofile.full_name
    except User.DoesNotExist:
        return f"Unknown User ({user_id})"

@register.simple_tag
def get_reviewer_role(user):
    """Get primary role of a reviewer."""
    role_hierarchy = [
        'OSAR',
        'IRB Head',
        'Research Council Head',
        'AHARPP Head',
        'IRB Member',
        'Research Council Member',
        'AHARPP Reviewer'
    ]
    
    for role in role_hierarchy:
        if user.groups.filter(name=role).exists():
            return role
    return 'Unknown Role'

@register.filter
def timesince_in_days(value):
    if not value:
        return 0
    
    if isinstance(value, str):
        value = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
    
    now = timezone.now()
    diff = now - value
    return diff.days

# Contents from: .\tests\__init__.py


# Contents from: .\tests\test_forms.py
from django.test import TestCase
from django.contrib.auth.models import User, Group
from forms_builder.models import DynamicForm
from review.forms import ReviewRequestForm, ConflictOfInterestForm
from django.utils import timezone
from datetime import timedelta

class ReviewFormTests(TestCase):
    def setUp(self):
        self.reviewer = User.objects.create_user('reviewer', 'reviewer@test.com', 'password123')
        self.irb_group = Group.objects.create(name='IRB Member')
        self.reviewer.groups.add(self.irb_group)
        self.test_form = DynamicForm.objects.create(
            name='Test Form',
            description='Test form'
        )

    def test_review_request_form_validation(self):
        form_data = {
            'requested_to': self.reviewer.id,
            'message': 'Please review',
            'deadline': (timezone.now() + timedelta(days=7)).date(),
            'selected_forms': [self.test_form.id],
            'submission_version': 1
        }
        form = ReviewRequestForm(data=form_data)
        self.assertTrue(form.is_valid()) 

# Contents from: .\tests\test_models.py
from django.test import TestCase
from django.contrib.auth.models import User, Group
from django.utils import timezone
from datetime import timedelta
from submission.models import Submission, VersionHistory
from forms_builder.models import DynamicForm, StudyType
from review.models import ReviewRequest, Review

class ReviewModelTests(TestCase):
    def setUp(self):
        # Create test users
        self.reviewer = User.objects.create_user('reviewer', 'reviewer@test.com', 'password123')
        self.admin_user = User.objects.create_superuser('admin', 'admin@test.com', 'password123')
        
        # Create IRB Member group
        self.irb_group = Group.objects.create(name='IRB Member')
        self.reviewer.groups.add(self.irb_group)
        
        # Create test study type and submission
        self.study_type = StudyType.objects.create(name='Test Study')
        self.submission = Submission.objects.create(
            title='Test Submission',
            primary_investigator=self.admin_user,
            study_type=self.study_type,
            status='submitted',
            version=1
        )

    def test_review_request_creation(self):
        review_request = ReviewRequest.objects.create(
            submission=self.submission,
            requested_by=self.admin_user,
            requested_to=self.reviewer,
            submission_version=1,
            deadline=timezone.now().date() + timedelta(days=7),
            status='pending'
        )
        self.assertEqual(review_request.submission_version, 1)
        self.assertEqual(review_request.status, 'pending')

    def test_review_creation(self):
        review_request = ReviewRequest.objects.create(
            submission=self.submission,
            requested_by=self.admin_user,
            requested_to=self.reviewer,
            submission_version=1,
            deadline=timezone.now().date() + timedelta(days=7),
            status='pending'
        )
        
        review = Review.objects.create(
            review_request=review_request,
            reviewer=self.reviewer,
            submission=self.submission,
            submission_version=1,
            comments='Test review comments'
        )
        
        self.assertEqual(review.submission_version, 1)
        self.assertEqual(review.reviewer, self.reviewer)

# Contents from: .\tests\test_pdf_generator.py
from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from io import BytesIO
from django.db.models.signals import post_save
from django.test.utils import override_settings
from ..models import Review, ReviewRequest, Submission
from ..utils.pdf_generator import generate_review_dashboard_pdf
from submission.models import StudyType
from users.models import UserProfile
from users.signals import create_user_profile  # Import the signal handler

class PDFGeneratorTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Disconnect the signal temporarily
        post_save.disconnect(create_user_profile, sender=User)

        try:
            # Create test users without triggering signals
            cls.user = User.objects.create(
                username='testuser',
                email='test@example.com',
            )
            cls.pi_user = User.objects.create(
                username='pi_user',
                email='pi@example.com',
            )
            
            # Create user profiles manually
            UserProfile.objects.create(
                user=cls.user,
                full_name="Test User"
            )
            UserProfile.objects.create(
                user=cls.pi_user,
                full_name="PI User"
            )

            # Create study type
            cls.study_type = StudyType.objects.create(
                name="Test Study",
                description="Test Study Description"
            )

            # Create test submission
            cls.submission = Submission.objects.create(
                title="Test Submission",
                primary_investigator=cls.pi_user,
                study_type=cls.study_type,
                version=1
            )

        finally:
            # Reconnect the signal
            post_save.connect(create_user_profile, sender=User)

    def setUp(self):
        # Create review requests
        self.pending_review = ReviewRequest.objects.create(
            submission=self.submission,
            submission_version=1,
            requested_by=self.pi_user,
            requested_to=self.user,
            deadline=timezone.now().date() + timedelta(days=7),
            status='pending'
        )

        self.completed_review = ReviewRequest.objects.create(
            submission=self.submission,
            submission_version=1,
            requested_by=self.pi_user,
            requested_to=self.user,
            deadline=timezone.now().date() - timedelta(days=7),
            status='completed'
        )

        # Create completed review
        self.review = Review.objects.create(
            review_request=self.completed_review,
            reviewer=self.user,
            submission=self.submission,
            submission_version=1,
            date_submitted=timezone.now()
        )

    def test_generate_pdf_as_buffer(self):
        """Test PDF generation returns a BytesIO buffer"""
        pending_reviews = ReviewRequest.objects.filter(status='pending')
        completed_reviews = Review.objects.all()
        
        pdf_buffer = generate_review_dashboard_pdf(
            pending_reviews,
            completed_reviews,
            self.user,
            as_buffer=True
        )
        
        self.assertIsInstance(pdf_buffer, BytesIO)
        pdf_content = pdf_buffer.getvalue()
        self.assertTrue(pdf_content.startswith(b'%PDF'))

    def test_generate_pdf_as_response(self):
        """Test PDF generation returns an HTTP response"""
        pending_reviews = ReviewRequest.objects.filter(status='pending')
        completed_reviews = Review.objects.all()
        
        response = generate_review_dashboard_pdf(
            pending_reviews,
            completed_reviews,
            self.user,
            as_buffer=False
        )
        
        # Check response properties
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertEqual(
            response['Content-Disposition'],
            'attachment; filename="review_dashboard.pdf"'
        )
        self.assertTrue(response.content.startswith(b'%PDF'))

    def test_pdf_content_structure(self):
        """Test the structure of generated PDF content"""
        pending_reviews = ReviewRequest.objects.filter(status='pending')
        completed_reviews = Review.objects.all()
        
        pdf_buffer = generate_review_dashboard_pdf(
            pending_reviews,
            completed_reviews,
            self.user,
            as_buffer=True
        )
        
        # Convert PDF to text for content checking
        pdf_content = pdf_buffer.getvalue()
        
        # Basic size check
        self.assertGreater(len(pdf_content), 100)  # PDF should have reasonable size

    def test_empty_reviews(self):
        """Test PDF generation with empty review sets"""
        pending_reviews = ReviewRequest.objects.none()
        completed_reviews = Review.objects.none()
        
        pdf_buffer = generate_review_dashboard_pdf(
            pending_reviews,
            completed_reviews,
            self.user,
            as_buffer=True
        )
        
        # Check if PDF is still generated
        self.assertIsInstance(pdf_buffer, BytesIO)
        pdf_content = pdf_buffer.getvalue()
        self.assertTrue(pdf_content.startswith(b'%PDF')) 

# Contents from: .\tests\test_views.py
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User, Permission, Group
from django.utils import timezone
from datetime import timedelta
from submission.models import Submission, VersionHistory
from forms_builder.models import DynamicForm, StudyType
from review.models import ReviewRequest, Review

class ReviewViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        # Create test users
        self.reviewer = User.objects.create_user('reviewer', 'reviewer@test.com', 'password123')
        self.admin_user = User.objects.create_superuser('admin', 'admin@test.com', 'password123')
        
        # Create IRB Member group
        self.irb_group = Group.objects.create(name='IRB Member')
        self.reviewer.groups.add(self.irb_group)
        
        # Create test study type and submission
        self.study_type = StudyType.objects.create(name='Test Study')
        self.submission = Submission.objects.create(
            title='Test Submission',
            primary_investigator=self.admin_user,
            study_type=self.study_type,
            status='submitted',
            version=1
        )

    def test_review_dashboard_view(self):
        self.client.login(username='reviewer', password='password123')
        response = self.client.get(reverse('review:review_dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_create_review_request_view(self):
        self.client.login(username='admin', password='password123')
        response = self.client.get(
            reverse('review:create_review_request', 
            args=[self.submission.pk])
        )
        self.assertEqual(response.status_code, 200) 

# Contents from: .\urls.py
from django.urls import path
from .views import (
    ReviewDashboardView,
    IRBDashboardView,
    RCDashboardView,
    ToggleSubmissionVisibilityView,
    UpdateSubmissionStatusView,
    CreateReviewRequestView,
    SubmitReviewView,
    ViewReviewView,
    RequestExtensionView,
    DeclineReviewView,
    ReviewSummaryView,
    ProcessIRBDecisionView,
    SubmissionVersionsView,
    download_review_pdf,
    AssignIRBNumberView,
    osar_dashboard,
    irb_dashboard,
    rc_dashboard
)
from submission.views import user_autocomplete

app_name = 'review'

urlpatterns = [
    path('', ReviewDashboardView.as_view(), name='review_dashboard'),

    path(
        'submission/<int:submission_id>/toggle-visibility/',
        ToggleSubmissionVisibilityView.as_view(),
        name='toggle_visibility'
    ),
    path(
        'submission/<int:submission_id>/update-status/',
        UpdateSubmissionStatusView.as_view(),
        name='update_status'
    ),
    path('create/<int:submission_id>/', CreateReviewRequestView.as_view(), name='create_review_request'),
    path('submit/<int:review_request_id>/', SubmitReviewView.as_view(), name='submit_review'),
    path('review/<int:review_request_id>/', ViewReviewView.as_view(), name='view_review'),
    path('review/<int:review_request_id>/extension/', RequestExtensionView.as_view(), name='request_extension'),
    path('review/<int:review_request_id>/decline/', DeclineReviewView.as_view(), name='decline_review'),
    path('submission/<int:submission_id>/summary/', ReviewSummaryView.as_view(), name='review_summary'),
    path('submission/<int:submission_id>/decision/', ProcessIRBDecisionView.as_view(), name='process_decision'),
    path('user-autocomplete/', user_autocomplete, name='user-autocomplete'),
    path('submission/<int:submission_id>/versions/', SubmissionVersionsView.as_view(), name='submission_versions'),
    path('review/<int:review_request_id>/pdf/', download_review_pdf, name='download_review_pdf'),
    path('submission/<int:submission_id>/assign-irb/', AssignIRBNumberView.as_view(), name='assign_irb'),


    path('irb-dashboard/', irb_dashboard, name='irb_dashboard'),
    path('rc-dashboard/', rc_dashboard, name='rc_dashboard'),
    path('osar-dashboard/', osar_dashboard, name='osar_dashboard'),



]


# Contents from: .\utils.py
# review/utils.py

from messaging.models import Message
from django.contrib.auth import get_user_model

User = get_user_model()

def send_review_request_notification(review_request):
    sender = review_request.requested_by
    recipient = review_request.requested_to
    submission = review_request.submission
    subject = f"Review Request for '{submission.title}'"
    body = f"""
    Dear {recipient.get_full_name()},

    You have been requested to review the submission titled '{submission.title}' (Version {submission.version}).

    Please log in to the system to proceed with the review.

    Thank you,
    {sender.get_full_name()}
    """

    # Create the message
    message = Message.objects.create(
        sender=sender,
        subject=subject.strip(),
        body=body.strip(),
        related_submission=submission,
    )
    # Add the recipient
    message.recipients.add(recipient)
    message.save()


def send_conflict_of_interest_notification(review_request):
    sender = review_request.requested_to  # The reviewer who declared conflict
    recipient = review_request.requested_by  # The person who requested the review
    submission = review_request.submission
    subject = f"Conflict of Interest Declared for '{submission.title}'"
    body = f"""
    Dear {recipient.get_full_name()},

    The reviewer {sender.get_full_name()} has declared a conflict of interest for the submission titled '{submission.title}'.

    Please assign a new reviewer.

    Conflict Details:
    {review_request.conflict_of_interest_details or 'No additional details provided.'}

    Thank you,
    {sender.get_full_name()}
    """

    # Create the message
    message = Message.objects.create(
        sender=sender,
        subject=subject.strip(),
        body=body.strip(),
        related_submission=submission,
    )
    # Add the recipient
    message.recipients.add(recipient)
    message.save()


def send_review_completion_notification(review_request):
    sender = review_request.requested_to  # The reviewer
    recipient = review_request.requested_by  # The person who requested the review
    submission = review_request.submission
    subject = f"Review Completed for '{submission.title}'"
    body = f"""
    Dear {recipient.get_full_name()},

    The review for the submission titled '{submission.title}' has been completed by {sender.get_full_name()}.

    You can view the review by logging into the system.

    Thank you,
    {sender.get_full_name()}
    """

    # Create the message
    message = Message.objects.create(
        sender=sender,
        subject=subject.strip(),
        body=body.strip(),
        related_submission=submission,
    )
    # Add the recipient
    message.recipients.add(recipient)
    message.save()


# Contents from: .\utils\__init__.py


# Contents from: .\utils\notifications.py
from django.utils import timezone
from django.core.files.base import ContentFile
from django.utils.text import slugify
from messaging.models import Message, MessageAttachment
from submission.utils.pdf_generator import generate_submission_pdf
from review.utils.pdf_generator import generate_review_pdf
from users.utils import get_system_user
from django.template.loader import render_to_string


def send_review_request_notification(review_request):
    """Create notification message for new review requests."""
    submission_title = review_request.submission.title
    requester_name = review_request.requested_by.get_full_name()
    reviewer_name = review_request.requested_to.get_full_name()

    # Generate PDF of submission with the current version
    pdf_buffer = generate_submission_pdf(
        submission=review_request.submission,
        version=review_request.submission_version,  # Use the version from review request
        user=get_system_user(),  # Use system user for PDF generation
        as_buffer=True
    )

    message = Message.objects.create(
        sender=get_system_user(),
        subject=f'New Review Request - {submission_title}',
        body=f"""
Dear {reviewer_name},

You have received a new review request.

Submission: {submission_title}
Requested by: {requester_name}
Deadline: {review_request.deadline}

Please find the submission details attached to this message. Log in to the system to submit your review.

Best regards,
iRN System
        """.strip(),
        study_name=submission_title,
        related_submission=review_request.submission
    )

    # Add recipient
    message.recipients.add(review_request.requested_to)

    # Add CC recipient
    message.cc.add(review_request.requested_by)

    if pdf_buffer:
        try:
            # Create PDF attachment
            submission_title_slug = slugify(submission_title)
            date_str = timezone.now().strftime('%Y_%m_%d')
            filename = f"submission_{submission_title_slug}_{date_str}.pdf"

            MessageAttachment.objects.create(
                message=message,
                file=ContentFile(pdf_buffer.getvalue(), name=filename),
                filename=filename
            )
        finally:
            pdf_buffer.close()

    return message


def send_review_decline_notification(review_request, decliner, reason):
    """Create notification message for declined reviews."""
    message = Message.objects.create(
        sender=get_system_user(),
        subject=f'Review Request Declined - {review_request.submission.title}',
        body=render_to_string('review/decline_notification_email.txt', {
            'requested_by': review_request.requested_by.userprofile.full_name,
            'submission_title': review_request.submission.title,
            'decliner': decliner.userprofile.full_name,
            'reason': reason,
        }),
        study_name=review_request.submission.title,
        related_submission=review_request.submission
    )
    message.recipients.add(review_request.requested_by)
    return message


def send_extension_request_notification(review_request, new_deadline_date, reason, requester):
    """Create notification message for extension requests."""
    extension_days = (new_deadline_date - review_request.deadline).days
    
    message = Message.objects.create(
        sender=requester,
        subject=f'Extension Request for Review #{review_request.id}',
        body=f"""
Extension Request Details:
-------------------------
Review: {review_request.submission.title}
Current Deadline: {review_request.deadline}
Requested New Deadline: {new_deadline_date}
Extension Days: {extension_days} days
Reason: {reason}

Please review this request and respond accordingly.
        """.strip(),
        study_name=review_request.submission.title,
        related_submission=review_request.submission
    )
    message.recipients.add(review_request.requested_by)
    return message


def send_review_completion_notification(review, review_request, pdf_buffer):
    """Create notification message for completed reviews."""
    submission_title = review_request.submission.title
    reviewer_name = review.reviewer.get_full_name()
    
    message = Message.objects.create(
        sender=get_system_user(),
        subject=f'Review Completed - {submission_title}',
        body=f"""
Dear {review_request.requested_by.userprofile.full_name},

A review has been completed for this submission.

Submission: {submission_title}
Reviewer: {reviewer_name}
Date Completed: {timezone.now().strftime('%Y-%m-%d %H:%M')}

Please find the detailed review report attached to this message.

Best regards,
iRN System
        """.strip(),
        study_name=submission_title,
        related_submission=review_request.submission
    )
    
    # Add recipients
    message.recipients.add(review_request.requested_by)
    message.cc.add(review_request.requested_to)
    
    if pdf_buffer:
        # Create PDF attachment
        submission_title_slug = slugify(submission_title)
        reviewer_name_slug = slugify(reviewer_name)
        date_str = timezone.now().strftime('%Y_%m_%d')
        filename = f"review_{submission_title_slug}_{reviewer_name_slug}_{date_str}.pdf"
        
        MessageAttachment.objects.create(
            message=message,
            file=ContentFile(pdf_buffer.getvalue(), name=filename),
            filename=filename
        )
    
    return message


def send_irb_decision_notification(submission, decision, comments):
    """Create notification message for IRB decisions."""
    message = Message.objects.create(
        sender=get_system_user(),
        subject=f'IRB Decision - {submission.title}',
        body=f"""
Dear {submission.primary_investigator.userprofile.full_name},

The IRB has made a decision regarding your submission "{submission.title}".

Decision: {decision.replace('_', ' ').title()}

{comments if comments else ''}

{'Please review the comments and submit a revised version.' if decision == 'revision_required' else ''}

Best regards,
AIDI System
        """.strip(),
        study_name=submission.title,
        related_submission=submission
    )
    message.recipients.add(submission.primary_investigator)
    return message

# Contents from: .\utils\pdf_generator.py
# review/utils/pdf_generator.py

from django.template.loader import render_to_string
from django.http import HttpResponse
from django.conf import settings
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, 
    TableStyle, PageBreak
)
from io import BytesIO
import logging
from reportlab.lib.utils import simpleSplit
from django.utils import timezone

logger = logging.getLogger(__name__)

class ReviewPDFGenerator:
    def __init__(self, buffer, review, submission, form_responses):
        """Initialize the PDF generator with basic settings"""
        self.buffer = buffer
        self.review = review
        self.submission = submission
        self.form_responses = form_responses
        self.canvas = canvas.Canvas(buffer, pagesize=letter)
        self.y = 750  # Starting y position
        self.line_height = 20
        self.page_width = letter[0]
        self.left_margin = 100
        self.right_margin = 500
        self.min_y = 100  # Minimum y position before new page

    def add_header(self):
        """Add header to the current page"""
        self.canvas.setFont("Helvetica-Bold", 16)
        self.canvas.drawString(self.left_margin, self.y, "Intelligent Research Navigator (iRN) Review Report")
        self.y -= self.line_height * 1.5
        
        self.canvas.setFont("Helvetica-Bold", 14)
        self.canvas.drawString(self.left_margin, self.y, f"Review for: {self.submission.title}")
        self.y -= self.line_height * 1.5
        
        self.canvas.setFont("Helvetica", 10)
        self.canvas.drawString(self.left_margin, self.y, f"Date of printing: {timezone.now().strftime('%Y-%m-%d %H:%M')}")
        self.y -= self.line_height
        self.canvas.drawString(self.left_margin, self.y, f"Reviewer: {self.review.reviewer.get_full_name()}")
        self.y -= self.line_height * 2

    def add_footer(self):
        """Add footer to the current page"""
        footer_text = (
            "iRN is a property of the Artificial Intelligence and Data Innovation (AIDI) office "
            "in collaboration with the Office of Scientific Affairs (OSAR) office @ King Hussein "
            "Cancer Center, Amman - Jordan. Keep this document confidential."
        )
        
        self.canvas.setFont("Helvetica", 8)
        text_object = self.canvas.beginText()
        text_object.setTextOrigin(self.left_margin, 50)
        
        wrapped_text = simpleSplit(footer_text, "Helvetica", 8, self.right_margin - self.left_margin)
        for line in wrapped_text:
            text_object.textLine(line)
        
        self.canvas.drawText(text_object)

    def check_page_break(self):
        """Check if we need a new page and create one if necessary"""
        if self.y < self.min_y:
            self.add_footer()
            self.canvas.showPage()
            self.y = 750
            self.add_header()
            return True
        return False

    def write_wrapped_text(self, text, x_offset=0, bold=False):
        """Write text with word wrapping"""
        if bold:
            self.canvas.setFont("Helvetica-Bold", 10)
        else:
            self.canvas.setFont("Helvetica", 10)
            
        wrapped_text = simpleSplit(str(text), "Helvetica", 10, self.right_margin - (self.left_margin + x_offset))
        for line in wrapped_text:
            self.check_page_break()
            self.canvas.drawString(self.left_margin + x_offset, self.y, line)
            self.y -= self.line_height

    def add_section_header(self, text):
        """Add a section header"""
        self.check_page_break()
        self.y -= self.line_height
        self.canvas.setFont("Helvetica-Bold", 12)
        self.canvas.drawString(self.left_margin, self.y, text)
        self.y -= self.line_height

    def add_review_info(self):
        """Add basic review information"""
        self.add_section_header("Review Information")
        
        review_info = [
            f"Submission ID: {self.submission.temporary_id}",
            f"Submission Version: {self.review.submission_version}",
            f"Review Status: {self.review.review_request.get_status_display()}",
            f"Date Submitted: {self.review.date_submitted.strftime('%Y-%m-%d') if self.review.date_submitted else 'Not submitted'}",
            f"Reviewer: {self.review.reviewer.get_full_name()}",
            f"Requested By: {self.review.review_request.requested_by.get_full_name()}"
        ]

        for info in review_info:
            self.write_wrapped_text(info)

    def add_form_responses(self):
        """Add form responses"""
        for response in self.form_responses:
            self.add_section_header(f"Form: {response.form.name}")
            
            for field_name, field_value in response.response_data.items():
                self.write_wrapped_text(f"{field_name}:", bold=True)
                self.write_wrapped_text(str(field_value), x_offset=20)
                self.y -= self.line_height/2

    def add_comments(self):
        """Add reviewer comments"""
        if self.review.comments:
            self.add_section_header("Additional Comments")
            self.write_wrapped_text(self.review.comments)

    def generate(self):
        """Generate the complete PDF"""
        try:
            self.add_header()
            self.add_review_info()
            self.add_form_responses()
            self.add_comments()
            self.add_footer()
            self.canvas.save()
        except Exception as e:
            logger.error(f"Error generating review PDF: {str(e)}")
            logger.error("PDF generation error details:", exc_info=True)
            raise

def generate_review_pdf(review, submission, form_responses):
    """Generate PDF for a review"""
    try:
        logger.info(f"Generating PDF for review of submission {submission.temporary_id}")
        
        buffer = BytesIO()
        pdf_generator = ReviewPDFGenerator(buffer, review, submission, form_responses)
        pdf_generator.generate()
        
        buffer.seek(0)
        return buffer
            
    except Exception as e:
        logger.error(f"Error generating review PDF: {str(e)}")
        logger.error("PDF generation error details:", exc_info=True)
        return None

# Contents from: .\views.py
######################
# Imports
######################

from datetime import timedelta
import json
import logging

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.views import View
from django.views.generic import TemplateView, FormView
from django import forms
from django.http import HttpResponse
from django.utils.text import slugify
from datetime import datetime
from django.core.files.base import ContentFile
from messaging.models import Message, MessageAttachment
from users.utils import get_system_user

from .forms import ReviewRequestForm
from .models import ReviewRequest, Review, FormResponse
from .utils.notifications import send_review_request_notification, send_review_decline_notification, send_extension_request_notification, send_review_completion_notification, send_irb_decision_notification
from forms_builder.models import DynamicForm
from messaging.models import Message
from submission.models import Submission
from users.utils import get_system_user
from .utils.pdf_generator import generate_review_pdf
from submission.utils.pdf_generator import PDFGenerator, generate_submission_pdf
from django.http import JsonResponse
from django.contrib.auth import get_user_model



######################
# Review Dashboard
# URL: path('', ReviewDashboardView.as_view(), name='review_dashboard'),
######################

from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
from .models import ReviewRequest, Review
from submission.models import Submission

class ReviewDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'review/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Add group membership checks to context
        context.update({
            'is_osar_member': user.groups.filter(name='OSAR').exists(),
            'is_irb_member': user.groups.filter(name='IRB').exists(),
            'is_rc_member': user.groups.filter(name='RC').exists(),
            'is_aahrpp_member': user.groups.filter(name='AAHRPP').exists(),
        })

        # Get submissions needing review (for OSAR members)
        if context['is_osar_member']:
            submissions_needing_review = Submission.objects.filter(
                status='submitted'
            ).select_related(
                'primary_investigator__userprofile'
            )
            context['submissions_needing_review'] = submissions_needing_review

        # Get reviews that can be forwarded
        forwarded_reviews = ReviewRequest.objects.filter(
            Q(requested_to=user) | Q(requested_by=user),
            can_forward=True,
        ).select_related(
            'submission__primary_investigator__userprofile',
            'requested_by',
            'requested_to'
        )
        context['forwarded_reviews'] = forwarded_reviews

        # Get pending reviews where user is the reviewer
        pending_reviews = ReviewRequest.objects.select_related(
            'submission__primary_investigator__userprofile',
            'requested_by',
            'requested_to'
        ).filter(
            Q(requested_to=user) | Q(requested_by=user),
            status__in=['pending', 'overdue', 'extended']
        ).order_by('-created_at')
        context['pending_reviews'] = pending_reviews

        return context

class IRBDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'review/irb_dashboard.html'

    def test_func(self):
        return self.request.user.groups.filter(name='IRB').exists()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Get submissions marked for IRB review
        irb_submissions = Submission.objects.filter(
            show_in_irb=True
        ).select_related(
            'primary_investigator__userprofile',
            'study_type'
        )
        context['irb_submissions'] = irb_submissions

        # Get IRB-related review requests
        irb_reviews = ReviewRequest.objects.filter(
            Q(requested_to__groups__name='IRB') | Q(requested_by__groups__name='IRB'),
            Q(requested_to=user) | Q(requested_by=user)
        ).select_related(
            'submission__primary_investigator__userprofile',
            'submission__study_type',
            'requested_by',
            'requested_to'
        ).distinct()
        context['irb_reviews'] = irb_reviews

        return context

class RCDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'review/rc_dashboard.html'

    def test_func(self):
        return self.request.user.groups.filter(name='RC').exists()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Get submissions marked for RC review
        rc_submissions = Submission.objects.filter(
            show_in_rc=True
        ).select_related(
            'primary_investigator__userprofile',
            'study_type'
        )
        context['rc_submissions'] = rc_submissions

        # Get RC-related review requests
        rc_reviews = ReviewRequest.objects.filter(
            Q(requested_to__groups__name='RC') | Q(requested_by__groups__name='RC'),
            Q(requested_to=user) | Q(requested_by=user)
        ).select_related(
            'submission__primary_investigator__userprofile',
            'submission__study_type',
            'requested_by',
            'requested_to'
        ).distinct()
        context['rc_reviews'] = rc_reviews

        return context

######################
# Create Review Request
# URL: path('create/<int:submission_id>/', CreateReviewRequestView.as_view(), name='create_review_request'),
######################

class CreateReviewRequestView(LoginRequiredMixin, View):
    template_name = 'review/create_review_request.html'  # Make sure this exists
    
    def get(self, request, submission_id):
        submission = get_object_or_404(Submission, pk=submission_id)
        form = ReviewRequestForm(study_type=submission.study_type)
        return render(request, self.template_name, {
            'form': form,
            'submission': submission
        })

    def post(self, request, submission_id):
        try:
            submission = get_object_or_404(Submission, pk=submission_id)
            form = ReviewRequestForm(request.POST, study_type=submission.study_type)
            
            if form.is_valid():
                review_request = form.save(commit=False)
                review_request.submission = submission
                review_request.requested_by = request.user
                review_request.submission_version = submission.version
                review_request.save()
                
                messages.success(request, "Review request created successfully.")
                return redirect('review:review_dashboard')
            else:
                return render(request, self.template_name, {
                    'form': form,
                    'submission': submission
                })
                
        except Exception as e:
            messages.error(request, f"Error creating review request: {str(e)}")
            return redirect('review:review_dashboard')

######################
# Decline Review
# URL: path('review/<int:review_request_id>/decline/', DeclineReviewView.as_view(), name='decline_review'),
######################

class DeclineReviewView(LoginRequiredMixin, View):
    template_name = 'review/decline_review.html'

    def dispatch(self, request, *args, **kwargs):
        self.review_request = self.get_review_request(kwargs['review_request_id'], request.user)
        if not self.review_request:
            return redirect('review:review_dashboard')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {'review_request': self.review_request})

    def post(self, request, *args, **kwargs):
        reason = request.POST.get('reason')
        if not reason:
            messages.error(request, "Please provide a reason for declining the review.")
            return redirect('review:decline_review', review_request_id=self.review_request.id)

        try:
            with transaction.atomic():
                self.review_request.status = 'declined'
                self.review_request.conflict_of_interest_declared = True
                self.review_request.conflict_of_interest_details = reason
                self.review_request.save()

                send_review_decline_notification(self.review_request, request.user, reason)
                messages.success(request, "Review request declined successfully.")
                return redirect('review:review_dashboard')
        except Exception as e:
            messages.error(request, f"Error declining review: {str(e)}")
            return redirect('review:decline_review', review_request_id=self.review_request.id)

    def get_review_request(self, review_request_id, user):
        review_request = get_object_or_404(ReviewRequest, pk=review_request_id)
        if user != review_request.requested_to or review_request.status in ['completed', 'declined']:
            messages.error(self.request, "You don't have permission to decline this review.")
            return None
        return review_request


######################
# Request Extension
# URL: path('review/<int:review_id>/extension/', RequestExtensionView.as_view(), name='request_extension'),
######################

class RequestExtensionView(LoginRequiredMixin, FormView):
    template_name = 'review/request_extension.html'

    def get_review_request(self, review_request_id, user):
        review_request = get_object_or_404(ReviewRequest, pk=review_request_id)
        if user != review_request.requested_to or review_request.status not in ['pending', 'overdue', 'extended']:
            messages.error(self.request, "You don't have permission to request an extension for this review.")
            return None
        return review_request

    def dispatch(self, request, *args, **kwargs):
        self.review_request = self.get_review_request(kwargs['review_request_id'], request.user)
        if not self.review_request:
            return redirect('review:review_dashboard')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {'review_request': self.review_request})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['review_request'] = self.review_request
        context['min_date'] = (timezone.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        context['max_date'] = (timezone.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        return context

    def post(self, request, *args, **kwargs):
        new_deadline = request.POST.get('new_deadline')
        reason = request.POST.get('reason')
        if not new_deadline or not reason:
            messages.error(request, "Please provide all required fields.")
            return self.form_invalid(None)

        try:
            new_deadline_date = timezone.datetime.strptime(new_deadline, '%Y-%m-%d').date()
            if new_deadline_date <= self.review_request.deadline or new_deadline_date <= timezone.now().date():
                raise ValueError("Invalid new deadline.")

            with transaction.atomic():
                send_extension_request_notification(
                    self.review_request,
                    new_deadline_date,
                    reason,
                    request.user
                )

                self.review_request.extension_requested = True
                self.review_request.proposed_deadline = new_deadline_date
                self.review_request.extension_reason = reason
                self.review_request.save()

                messages.success(request, "Extension request submitted successfully.")
                return redirect('review:review_dashboard')
        except ValueError as e:
            messages.error(request, str(e))
            return self.form_invalid(None)


######################
# Submit Review
# URL: path('submit/<int:review_request_id>/', SubmitReviewView.as_view(), name='submit_review'),
######################

class SubmitReviewView(LoginRequiredMixin, View):
    template_name = 'review/submit_review.html'

    def dispatch(self, request, *args, **kwargs):
        self.review_request = get_object_or_404(
            ReviewRequest.objects.select_related(
                'submission',
                'requested_by__userprofile',
                'submission__primary_investigator'
            ),
            pk=kwargs['review_request_id']
        )
        if not self.can_submit_review(request.user, self.review_request):
            raise PermissionDenied("You don't have permission to submit this review.")
        return super().dispatch(request, *args, **kwargs)

    def can_submit_review(self, user, review_request):
        return user == review_request.requested_to and review_request.status in ['pending', 'overdue', 'extended']

    def get(self, request, *args, **kwargs):
        forms_data = self.get_forms_data()
        context = {
            'review_request': self.review_request,
            'forms_data': forms_data,
            'submission': self.review_request.submission,
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        action = request.POST.get('action', '')
        forms_data = self.get_forms_data(request.POST)
        is_valid = all(form_data['form'].is_valid() for form_data in forms_data)

        if not is_valid:
            messages.error(request, "Please correct the errors in the form.")
            context = {
                'review_request': self.review_request,
                'forms_data': forms_data,
                'submission': self.review_request.submission,
            }
            return render(request, self.template_name, context)

        try:
            with transaction.atomic():
                review, _ = Review.objects.get_or_create(
                    review_request=self.review_request,
                    defaults={
                        'reviewer': request.user,
                        'submission': self.review_request.submission,
                        'submission_version': self.review_request.submission_version
                    }
                )

                for form_data in forms_data:
                    form_template = form_data['template']
                    form_instance = form_data['form']
                    response_data = form_instance.cleaned_data

                    FormResponse.objects.update_or_create(
                        review=review,
                        form=form_template,
                        defaults={'response_data': response_data}
                    )

                comments = request.POST.get('comments', '').strip()
                if comments:
                    review.comments = comments

                if action == 'submit':
                    review.is_completed = True
                    review.completed_at = timezone.now()
                    self.review_request.status = 'completed'
                    self.review_request.save()

                    # Generate PDF and send notification
                    pdf_buffer = generate_review_pdf(review, self.review_request.submission, review.formresponse_set.all())
                    if pdf_buffer:
                        send_review_completion_notification(review, self.review_request, pdf_buffer)
                        pdf_buffer.close()

                    messages.success(request, "Review submitted successfully.")
                else:
                    messages.success(request, "Review saved as draft.")

                review.save()
                return redirect('review:review_dashboard')
        except Exception as e:
            messages.error(request, f"An unexpected error occurred: {str(e)}")
            context = {
                'review_request': self.review_request,
                'forms_data': forms_data,
                'submission': self.review_request.submission,
            }
            return render(request, self.template_name, context)

    def get_forms_data(self, data=None):
        forms_data = []
        for form_template in self.review_request.selected_forms.all():
            DynamicFormClass = self.generate_django_form(form_template)
            form_instance = DynamicFormClass(
                data=data,
                prefix=f'form_{form_template.id}'
            )
            forms_data.append({
                'template': form_template,
                'form': form_instance
            })
        return forms_data

    def generate_django_form(self, form_template):
        form_fields = {}
        field_map = {
            'text': forms.CharField,
            'email': forms.EmailField,
            'tel': forms.CharField,
            'number': forms.IntegerField,
            'date': forms.DateField,
            'textarea': forms.CharField,
            'checkbox': forms.MultipleChoiceField,
            'radio': forms.ChoiceField,
            'select': forms.ChoiceField,
            'choice': forms.MultipleChoiceField,
            'table': forms.CharField,
        }
        for field in form_template.fields.all():
            field_class = field_map.get(field.field_type, forms.CharField)
            field_kwargs = {
                'label': field.displayed_name,
                'required': field.required,
                'help_text': field.help_text,
                'initial': field.default_value,
            }
            if field.field_type in ['checkbox', 'radio', 'select', 'choice']:
                choices = [(choice.strip(), choice.strip())
                           for choice in field.choices.split(',')
                           if choice.strip()] if field.choices else []
                field_kwargs['choices'] = choices
            if field.max_length:
                field_kwargs['max_length'] = field.max_length
            if field.field_type == 'textarea':
                field_kwargs['widget'] = forms.Textarea(attrs={'rows': field.rows})
            form_fields[field.name] = field_class(**field_kwargs)
        return type(f'DynamicForm_{form_template.id}', (forms.Form,), form_fields)


######################
# View Review
# URL: path('review/<int:review_request_id>/', ViewReviewView.as_view(), name='view_review'),
######################

class ViewReviewView(LoginRequiredMixin, TemplateView):
    template_name = 'review/view_review.html'

    def dispatch(self, request, *args, **kwargs):
        # Get the review request using review_request_id from kwargs
        review_request = get_object_or_404(ReviewRequest, id=kwargs['review_request_id'])
        
        # Then get the associated review
        self.review = get_object_or_404(
            Review.objects.select_related(
                'review_request',
                'reviewer__userprofile',
                'submission',
                'submission__primary_investigator'
            ),
            review_request=review_request
        )
        
        if not self.has_permission(request.user, self.review):
            messages.error(request, "You don't have permission to view this review.")
            return redirect('review:review_dashboard')
        return super().dispatch(request, *args, **kwargs)

    def has_permission(self, user, review):
        return user in [
            review.reviewer,
            review.review_request.requested_by,
            review.submission.primary_investigator
        ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'review': self.review,
            'review_request': self.review.review_request,
            'submission': self.review.submission,
            'reviewer': self.review.reviewer,
            'form_responses': FormResponse.objects.filter(review=self.review)
        })
        return context


######################
# Review Summary
# URL: path('submission/<int:submission_id>/summary/', ReviewSummaryView.as_view(), name='review_summary'),
######################

class ReviewSummaryView(LoginRequiredMixin, TemplateView):
    template_name = 'review/review_summary.html'

    def dispatch(self, request, *args, **kwargs):
        self.submission = get_object_or_404(
            Submission.objects.prefetch_related('version_histories', 'review_requests'),
            pk=kwargs['submission_id']
        )
        if not self.has_permission(request.user, self.submission):
            messages.error(request, "You don't have permission to view this review summary.")
            return redirect('review:review_dashboard')
        return super().dispatch(request, *args, **kwargs)

    def has_permission(self, user, submission):
        # Check if user is primary investigator, requested_by, or requested_to on any review request
        is_pi = user == submission.primary_investigator
        is_requested_by = submission.review_requests.filter(requested_by=user).exists()
        is_requested_to = submission.review_requests.filter(requested_to=user).exists()
        is_irb_member = user.groups.filter(name='IRB').exists()
        
        return any([is_pi, is_requested_by, is_requested_to, is_irb_member])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        review_requests = ReviewRequest.objects.filter(
            submission=self.submission
        ).select_related(
            'requested_to__userprofile',
            'requested_by__userprofile'
        ).prefetch_related(
            'review_set',
            'review_set__formresponse_set__form'
        )

        # Get version histories ordered by version number
        version_histories = self.submission.version_histories.all().order_by('-version')

        # Check if user can download PDFs
        can_download_pdf = True

        context.update({
            'submission': self.submission,
            'review_requests': review_requests,
            'version_histories': version_histories,
            'can_make_decision': self.request.user.groups.filter(name='IRB Coordinator').exists(),
            'can_download_pdf': can_download_pdf
        })
        return context


######################
# Process IRB Decision
# URL: path('submission/<int:submission_id>/decision/', ProcessIRBDecisionView.as_view(), name='process_decision'),
######################

class ProcessIRBDecisionView(LoginRequiredMixin, FormView):
    template_name = 'review/process_decision.html'

    def dispatch(self, request, *args, **kwargs):
        self.submission = get_object_or_404(Submission, pk=kwargs['submission_id'])
        if not request.user.groups.filter(name='IRB Coordinator').exists():
            messages.error(request, "You don't have permission to make IRB decisions.")
            return redirect('submission:dashboard')
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        decision = request.POST.get('decision')
        comments = request.POST.get('comments')

        if decision not in ['approved', 'revision_required', 'rejected']:
            messages.error(request, "Invalid decision.")
            return self.form_invalid(None)

        try:
            with transaction.atomic():
                self.submission.status = decision
                self.submission.save()

                send_irb_decision_notification(self.submission, decision, comments)

                messages.success(request, "Decision recorded and PI has been notified.")
                return redirect('review:review_summary', submission_id=self.submission.id)
        except Exception as e:
            messages.error(request, f"Error processing decision: {str(e)}")
            return self.form_invalid(None)


######################
# Submission Versions
# URL: path('submission/<int:submission_id>/versions/', SubmissionVersionsView.as_view(), name='submission_versions'),
######################

class SubmissionVersionsView(LoginRequiredMixin, TemplateView):
    template_name = 'review/submission_versions.html'

    def get(self, request, *args, **kwargs):
        submission = get_object_or_404(Submission, pk=kwargs['submission_id'])
        histories = submission.version_histories.order_by('-version')
        return render(request, self.template_name, {
            'submission': submission,
            'histories': histories,
        })

def download_review_pdf(request, review_request_id):
    review_request = get_object_or_404(ReviewRequest, id=review_request_id)
    review = get_object_or_404(
        Review.objects.select_related(
            'review_request',
            'reviewer__userprofile',
            'submission',
            'submission__primary_investigator'
        ),
        review_request=review_request
    )
    
    submission = review.submission
    form_responses = review.formresponse_set.all()
    
    # Create snake_case filename
    submission_title = slugify(submission.title).replace('-', '_')
    reviewer_name = slugify(review.reviewer.get_full_name()).replace('-', '_')
    date_str = datetime.now().strftime('%Y_%m_%d')
    
    filename = f"{submission_title}_{reviewer_name}_{date_str}.pdf"
    
    buffer = generate_review_pdf(review, submission, form_responses)
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    response.write(buffer.getvalue())
    buffer.close()
    
    return response

class UserAutocompleteView(View):
    def get(self, request):
        term = request.GET.get('term', '')
        user_type = request.GET.get('user_type', '')
        
        if len(term) < 2:
            return JsonResponse([], safe=False)
            
        User = get_user_model()
        users = User.objects.filter(
            Q(first_name__icontains=term) | 
            Q(last_name__icontains=term) |
            Q(email__icontains=term)
        )
        
        # Add any additional filtering for reviewers here
        if user_type == 'reviewer':
            users = users.filter(groups__name='Reviewers')
            
        results = [
            {
                'id': user.id,
                'label': f"{user.get_full_name()} ({user.email})"
            }
            for user in users[:10]  # Limit to 10 results
        ]
        
        return JsonResponse(results, safe=False)


######################
# Assign IRB Number
# URL: path('submission/<int:submission_id>/assign-irb/', AssignIRBNumberView.as_view(), name='assign_irb'),
######################

class AssignIRBNumberView(LoginRequiredMixin, View):
    template_name = 'review/assign_irb_number.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.groups.filter(name='IRB').exists():
            messages.error(request, "You don't have permission to assign IRB numbers.")
            return redirect('review:review_dashboard')
        
        self.submission = get_object_or_404(Submission, pk=kwargs['submission_id'])
        if self.submission.irb_number:
            messages.warning(request, "This submission already has an IRB number.")
            return redirect('review:review_summary', submission_id=self.submission.id)
            
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        context = {
            'submission': self.submission,
            'suggested_irb': self._generate_irb_number()
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        irb_number = request.POST.get('irb_number', '').strip()
        
        if not irb_number:
            messages.error(request, "IRB number is required.")
            return redirect('review:assign_irb', submission_id=self.submission.temporary_id)

        # Check uniqueness
        if Submission.objects.filter(irb_number=irb_number).exists():
            messages.error(request, "This IRB number is already in use. Please try another.")
            return redirect('review:assign_irb', submission_id=self.submission.temporary_id)

        try:
            with transaction.atomic():
                self.submission.irb_number = irb_number
                self.submission.save()

                # Get all users who need to be notified
                users_to_notify = set([self.submission.primary_investigator])
                
                # Add research assistants with submit privilege
                users_to_notify.update(
                    self.submission.research_assistants.filter(
                        can_submit=True
                    ).values_list('user', flat=True)
                )
                
                # Add co-investigators with submit privilege
                users_to_notify.update(
                    self.submission.coinvestigators.filter(
                        can_submit=True
                    ).values_list('user', flat=True)
                )

                # Send notification to each user
                system_user = get_system_user()
                message_content = f"""
                An IRB number has been assigned to the submission "{self.submission.title}".
                IRB Number: {irb_number}
                """

                for user in users_to_notify:
                    print("Debug - System User:", system_user)
                    print("Debug - Users to notify:", users_to_notify)
                    print("Debug - Message fields available:", [field.name for field in Message._meta.get_fields()])
                    print("Debug - Message content:", message_content)
                    try:
                        print(f"Debug - Creating message for user: {user}")
                        message = Message.objects.create(
                            sender=system_user,
                            body=message_content,
                            subject=f"IRB Number Assigned - {self.submission.title}",
                            related_submission=self.submission
                        )
                        message.recipients.set([user])  # Use set() method for many-to-many relationship
                        print(f"Debug - Message created successfully: {message}")
                    except Exception as e:
                        print(f"Debug - Message creation error: {str(e)}")
                        print(f"Debug - Error type: {type(e)}")
                        raise  # Re-raise the exception to trigger the outer error handling

                messages.success(request, f"IRB number {irb_number} has been assigned successfully.")
                return redirect('review:review_summary', submission_id=self.submission.temporary_id)

        except Exception as e:
            messages.error(request, f"Error assigning IRB number: {str(e)}")
            return redirect('review:assign_irb', submission_id=self.submission.temporary_id)

    def _generate_irb_number(self):
        """Generate a suggested IRB number format: YYYY-XXX"""
        year = timezone.now().year
        
        # Get the highest number for this year
        latest_irb = Submission.objects.filter(
            irb_number__startswith=f"{year}-"
        ).order_by('-irb_number').first()

        if latest_irb and latest_irb.irb_number:
            try:
                number = int(latest_irb.irb_number.split('-')[1]) + 1
            except (IndexError, ValueError):
                number = 1
        else:
            number = 1

        return f"{year}-{number:03d}"

class ToggleSubmissionVisibilityView(LoginRequiredMixin, View):
    def post(self, request, submission_id):
        try:
            submission = get_object_or_404(Submission, id=submission_id)
            toggle_type = request.POST.get('toggle_type')
            
            if not toggle_type in ['irb', 'rc']:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Invalid toggle type'
                }, status=400)
            
            if toggle_type == 'irb':
                submission.show_in_irb = not getattr(submission, 'show_in_irb', False)
                visible = submission.show_in_irb
            else:  # toggle_type == 'rc'
                submission.show_in_rc = not getattr(submission, 'show_in_rc', False)
                visible = submission.show_in_rc
            
            submission.save()
            
            return JsonResponse({
                'status': 'success',
                'visible': visible,
                'message': f'Visibility toggled successfully'
            })
            
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.error(f"Error toggling visibility: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)

class UpdateSubmissionStatusView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.groups.filter(name__in=['IRB', 'RC', 'OSAR']).exists()

    def post(self, request, submission_id):
        try:
            submission = get_object_or_404(Submission, temporary_id=submission_id)
            new_status = request.POST.get('status')
            
            if not new_status:
                return JsonResponse({
                    'status': 'error',
                    'message': 'New status not provided'
                }, status=400)
            
            # Get available status choices
            valid_statuses = [choice[0] for choice in submission.get_status_choices()]
            
            if new_status not in valid_statuses:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Invalid status'
                }, status=400)
            
            # Update the status
            submission.status = new_status
            submission.save(update_fields=['status'])
            
            return JsonResponse({
                'status': 'success',
                'message': 'Status updated successfully',
                'new_status': new_status
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)

  


@login_required
def irb_dashboard(request):
    if not request.user.is_irb_member:
        return redirect('review:dashboard')
    context = {
        'irb_submissions': get_irb_submissions(),
        'pending_irb_decisions': get_pending_irb_decisions(),
        'irb_reviews': get_irb_reviews(request.user),
    }
    return render(request, 'review/irb_dashboard.html', context)

@login_required
def rc_dashboard(request):
    if not request.user.is_rc_member:
        return redirect('review:dashboard')
    context = {
        'rc_submissions': get_rc_submissions(),
        'department_submissions': get_department_submissions(request.user),
        'rc_reviews': get_rc_reviews(request.user),
    }
    return render(request, 'review/rc_dashboard.html', context)



@login_required
def osar_dashboard(request):
    if not request.user.groups.filter(name='OSAR').exists():
        return redirect('review:dashboard')
    context = {
        'osar_submissions': Submission.objects.filter(status='submitted'),
        'osar_reviews': ReviewRequest.objects.filter(
            Q(requested_to__groups__name='OSAR') | Q(requested_by__groups__name='OSAR'),
            Q(requested_to=request.user) | Q(requested_by=request.user)
        ).distinct(),
    }
    return render(request, 'review/osar_dashboard.html', context)