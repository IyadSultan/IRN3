# Combined Python and HTML files
# Generated from directory: C:\Users\isult\Dropbox\AI\Projects\IRN3\submission
# Total files found: 75



# Contents from: .\pdf\decision_comments.html
{# templates/submission/pdf/decision_comments.html #}
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            margin: 30px;
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        .section {
            margin: 20px 0;
        }
        .section-title {
            font-weight: bold;
            margin-bottom: 10px;
        }
        .footer {
            margin-top: 50px;
            text-align: center;
            font-size: 0.9em;
            color: #666;
        }
        .decision {
            padding: 10px;
            margin: 20px 0;
            border-radius: 5px;
        }
        .comments {
            white-space: pre-wrap;
            margin: 20px 0;
            padding: 15px;
            background-color: #f8f9fa;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>Review Decision Details</h1>
        <p>Generated on: {{ decision_date|date:"F d, Y H:i" }}</p>
    </div>

    <div class="section">
        <div class="section-title">Submission Information</div>
        <p><strong>Title:</strong> {{ submission.title }}</p>
        <p><strong>Primary Investigator:</strong> {{ submission.primary_investigator.userprofile.full_name }}</p>
        <p><strong>Study Type:</strong> {{ submission.study_type }}</p>
        <p><strong>KHCC #:</strong> {{ submission.khcc_number|default:"Not assigned" }}</p>
    </div>

    <div class="section">
        <div class="section-title">Decision Information</div>
        <p><strong>Decision Date:</strong> {{ decision_date|date:"F d, Y H:i" }}</p>
        <p><strong>Decided By:</strong> {{ decided_by }}</p>
    </div>

    <div class="section">
        <div class="section-title">Comments</div>
        <div class="comments">
            {{ comments }}
        </div>
    </div>

    <div class="footer">
        Generated from iRN System - Confidential
    </div>
</body>
</html>

# Contents from: .\templates\submission\add_coinvestigator.html
{% extends 'users/base.html' %}
{% load crispy_forms_tags %}

{% block title %}Add Co-Investigator{% endblock %}

{% block page_specific_css %}
<style>
    /* Style for roles checkboxes */
    .roles-checkbox-group {
        max-height: 200px;
        overflow-y: auto;
        border: 1px solid #dee2e6;
        border-radius: 4px;
        padding: 10px;
    }

    .role-checkbox {
        display: block;
        margin-bottom: 8px;
    }

    .role-checkbox input[type="checkbox"] {
        margin-right: 8px;
    }

    .role-checkbox label {
        font-weight: normal;
        margin-bottom: 0;
        cursor: pointer;
    }

    /* Custom scrollbar for the roles container */
    .roles-checkbox-group::-webkit-scrollbar {
        width: 8px;
    }

    .roles-checkbox-group::-webkit-scrollbar-track {
        background: #f1f1f1;
    }

    .roles-checkbox-group::-webkit-scrollbar-thumb {
        background: #888;
        border-radius: 4px;
    }

    .roles-checkbox-group::-webkit-scrollbar-thumb:hover {
        background: #555;
    }
</style>
{% endblock %}

{% block content %}
<div class="container mt-4">
    <div class="row">
        <div class="col-md-8 offset-md-2">
            <div class="card">
                <div class="card-header">
                    <h2>Add Co-Investigator</h2>
                    <h6 class="text-muted">Submission ID: {{ submission.temporary_id }}</h6>
                </div>
                <div class="card-body">
                    {% if coinvestigators %}
                    <div class="mb-4">
                        <h5>Current Co-Investigators:</h5>
                        <table class="table">
                            <thead>
                                <tr>
                                    <th>Name</th>
                                    <th>Roles</th>
                                    <th>Permissions</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for co in coinvestigators %}
                                <tr>
                                    <td>{{ co.user.get_full_name }}</td>
                                    <td>
                                        {% for role in co.get_role_display %}
                                            <span class="badge bg-secondary me-1">{{ role }}</span>
                                        {% endfor %}
                                    </td>
                                    <td>
                                        {% if co.can_edit %}<span class="badge bg-success">Edit</span>{% endif %}
                                        {% if co.can_submit %}<span class="badge bg-info">Submit</span>{% endif %}
                                        {% if co.can_view_communications %}<span class="badge bg-warning">View Communications</span>{% endif %}
                                    </td>
                                    <td>
                                        <form method="post" style="display: inline;">
                                            {% csrf_token %}
                                            <input type="hidden" name="coinvestigator_id" value="{{ co.id }}">
                                            <button type="submit" name="action" value="delete_coinvestigator" 
                                                    class="btn btn-danger btn-sm"
                                                    onclick="return confirm('Are you sure you want to remove this co-investigator?')">
                                                <i class="fas fa-trash"></i>
                                            </button>
                                        </form>
                                    </td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                    {% endif %}

                    <form method="post" novalidate>
                        {% csrf_token %}
                        
                        {# Render investigator field with crispy #}
                        {{ form.investigator|as_crispy_field }}

                        {# Custom rendering for roles field #}
                        <div class="mb-3">
                            <label class="form-label">{{ form.roles.label }}</label>
                            <div class="roles-checkbox-group">
                                {% for choice in form.roles %}
                                    <div class="role-checkbox">
                                        {{ choice.tag }}
                                        <label for="{{ choice.id_for_label }}">{{ choice.choice_label }}</label>
                                    </div>
                                {% endfor %}
                            </div>
                            {% if form.roles.errors %}
                                <div class="alert alert-danger mt-2">
                                    {{ form.roles.errors }}
                                </div>
                            {% endif %}
                            {% if form.roles.help_text %}
                                <div class="form-text text-muted">
                                    {{ form.roles.help_text }}
                                </div>
                            {% endif %}
                        </div>

                        {# Render remaining fields with crispy #}
                        {{ form.can_edit|as_crispy_field }}
                        {{ form.can_submit|as_crispy_field }}
                        {{ form.can_view_communications|as_crispy_field }}

                        <div class="d-grid gap-2 d-md-flex justify-content-md-end mt-4">
                            <button type="submit" name="action" value="back" class="btn btn-secondary me-md-2" formnovalidate>
                                <i class="fas fa-arrow-left"></i> Back to Start
                            </button>
                            <button type="submit" name="action" value="exit_no_save" class="btn btn-danger me-md-2" formnovalidate>
                                <i class="fas fa-times"></i> Exit without Saving
                            </button>
                            <button type="submit" name="action" value="save_exit" class="btn btn-primary me-md-2">
                                <i class="fas fa-save"></i> Save and Exit
                            </button>
                            <button type="submit" name="action" value="save_continue" class="btn btn-success">
                                <i class="fas fa-arrow-right"></i> Save and Continue
                            </button>
                            <button type="submit" name="action" value="save_add_another" class="btn btn-info me-md-2">
                                <i class="fas fa-plus"></i> Add Co-investigator
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
    $(document).ready(function() {
        // Initialize investigator Select2 only
        $('#id_investigator').select2({
    theme: 'bootstrap4',
    ajax: {
        url: '{% url "submission:user-autocomplete" %}',
        dataType: 'json',
        delay: 250,
        data: function (params) {
            return {
                term: params.term,
                submission_id: '{{ submission.id }}',
                user_type: 'coinvestigator'
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
            placeholder: 'Search for co-investigator...',
            allowClear: true,
            width: '100%'
        });

        // Handle initial value for investigator if exists
        {% if form.investigator.initial %}
            var initialUser = {
                id: '{{ form.investigator.initial.id }}',
                text: '{{ form.investigator.initial.get_full_name|escapejs }}'
            };
            var initialOption = new Option(initialUser.text, initialUser.id, true, true);
            $('#id_investigator').append(initialOption).trigger('change');
        {% endif %}
    });
</script>
{% endblock %}

# Contents from: .\templates\submission\add_research_assistant.html
{# submission/add_research_assistant.html #}
{% extends 'users/base.html' %}
{% load crispy_forms_tags %}

{% block content %}
<div class="container mt-4">
    <div class="card">
        <div class="card-header">
            <h2>Add Research Assistant</h2>
            <h6 class="text-muted">Submission ID: {{ submission.temporary_id }}</h6>
        </div>
        <div class="card-body">
            {% if assistants %}
            <div class="mb-4">
                <h5>Current Research Assistants:</h5>
                <table class="table">
                    <thead>
                        <tr>
                            <th>Name</th>
                            <th>Permissions</th>
                            <th>Date Added</th>
                            {% if can_modify %}
                            <th>Actions</th>
                            {% endif %}
                        </tr>
                    </thead>
                    <tbody>
                        {% for ra in assistants %}
                        <tr>
                            <td>{{ ra.user.get_full_name }}</td>
                            <td>
                                {% if ra.can_edit %}<span class="badge bg-success">Edit</span>{% endif %}
                                {% if ra.can_submit %}<span class="badge bg-info">Submit</span>{% endif %}
                                {% if ra.can_view_communications %}<span class="badge bg-warning">View Communications</span>{% endif %}
                            </td>
                            <td>{{ ra.date_added|date:"M d, Y H:i" }}</td>
                            {% if can_modify %}
                            <td>
                                <form method="post" style="display: inline;">
                                    {% csrf_token %}
                                    <input type="hidden" name="assistant_id" value="{{ ra.id }}">
                                    <button type="submit" name="action" value="delete_assistant" 
                                            class="btn btn-danger btn-sm"
                                            onclick="return confirm('Are you sure you want to remove this research assistant?')">
                                        <i class="fas fa-trash"></i>
                                    </button>
                                </form>
                            </td>
                            {% endif %}
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
            {% endif %}

            {% if permission_history %}
            <div class="mb-4">
                <h5>Recent Permission Changes:</h5>
                <div class="table-responsive">
                    <table class="table table-sm">
                        <thead>
                            <tr>
                                <th>Date</th>
                                <th>User</th>
                                <th>Change</th>
                                <th>Changed By</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for log in permission_history %}
                            <tr>
                                <td>{{ log.change_date|date:"M d, Y H:i" }}</td>
                                <td>{{ log.user.get_full_name }}</td>
                                <td>{{ log.get_change_description }}</td>
                                <td>{{ log.changed_by.get_full_name }}</td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
            {% endif %}

            {% if can_modify %}
            <form method="post" novalidate>
                {% csrf_token %}
                {{ form|crispy }}
                <div class="d-grid gap-2 d-md-flex justify-content-md-end mt-4">
                    <button type="submit" name="action" value="back" class="btn btn-secondary me-md-2">
                        <i class="fas fa-arrow-left"></i> Back
                    </button>
                    <button type="submit" name="action" value="exit_no_save" class="btn btn-danger me-md-2">
                        <i class="fas fa-times"></i> Exit without Saving
                    </button>
                    <button type="submit" name="action" value="save_exit" class="btn btn-primary me-md-2">
                        <i class="fas fa-save"></i> Save and Exit
                    </button>
                    <button type="submit" name="action" value="save_add_another" class="btn btn-info me-md-2">
                        <i class="fas fa-plus"></i> Add RA
                    </button>
                    <button type="submit" name="action" value="save_continue" class="btn btn-success">
                        <i class="fas fa-arrow-right"></i> Save and Continue
                    </button>
                </div>
            </form>
            {% endif %}
        </div>
    </div>
</div>
{% endblock %}

{% block page_specific_js %}
<script>
    $(document).ready(function() {
        // Initialize Select2 for assistant field
        $('#id_assistant').select2({
    theme: 'bootstrap4',
    ajax: {
        url: '{% url "submission:user-autocomplete" %}',
        dataType: 'json',
        delay: 250,
        data: function (params) {
            return {
                term: params.term,
                submission_id: '{{ submission.id }}',
                user_type: 'assistant'
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
            placeholder: 'Search for research assistant...',
            allowClear: true,
            width: '100%'
        });

        // Handle initial value if it exists
        {% if form.assistant.initial %}
            var initialUser = {
                id: '{{ form.assistant.initial.id }}',
                text: '{{ form.assistant.initial.get_full_name|escapejs }}'
            };
            var initialOption = new Option(initialUser.text, initialUser.id, true, true);
            $('#id_assistant').append(initialOption).trigger('change');
        {% endif %}
    });
</script>
{% endblock %}

# Contents from: .\templates\submission\archived_dashboard.html
{% extends 'users/base.html' %}
{% load static %}

{% block title %}Archived Submissions{% endblock %}

{% block content %}
<div class="container mt-4">
    <h1 class="mb-4">Archived Submissions</h1>
    <div class="mb-3">
        <a href="{% url 'submission:dashboard' %}" class="btn btn-secondary">
            <i class="fas fa-arrow-left"></i> Back to Dashboard
        </a>
    </div>
    <div class="table-responsive">
        <table class="table table-striped">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>KHCC #</th>
                    <th>Title</th>
                    <th>Primary Investigator</th>
                    <th>Status</th>
                    <th>Version</th>
                    <th>Archived Date</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                {% for submission in submissions %}
                <tr>
                    <td>{{ submission.temporary_id }}</td>
                    <td>{{ submission.khcc_number|default:"N/A" }}</td>
                    <td>{{ submission.title }}</td>
                    <td>{{ submission.primary_investigator.get_full_name }}</td>
                    <td>{{ submission.get_status_display }}</td>
                    <td>{{ submission.version }}</td>
                    <td>{{ submission.archived_at|date:"M d, Y H:i" }}</td>
                    <td>
                        <button class="btn btn-sm btn-info unarchive-submission" 
                                data-submission-id="{{ submission.temporary_id }}"
                                title="Unarchive Submission">
                            <i class="fas fa-box-open"></i>
                        </button>
                        <!-- <a href="{% url 'submission:view_submission' submission.temporary_id %}" 
                           class="btn btn-sm btn-secondary" 
                           title="View Submission">
                            <i class="fas fa-eye"></i>
                        </a> -->
                        <a href="{% url 'submission:download_submission_pdf' submission.temporary_id %}" 
                           class="btn btn-sm btn-secondary" 
                           title="Download PDF">
                            <i class="fas fa-file-pdf"></i>
                        </a>
                    </td>
                </tr>
                {% empty %}
                <tr>
                    <td colspan="9" class="text-center">No archived submissions found.</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>
{% endblock %}

{% block page_specific_js %}
<script>
$(document).ready(function() {
    $('.unarchive-submission').click(function() {
        const submissionId = $(this).data('submission-id');
        if (confirm('Are you sure you want to unarchive this submission?')) {
            $.ajax({
                url: `/submission/unarchive/${submissionId}/`,
                type: 'POST',
                headers: {
                    'X-CSRFToken': '{{ csrf_token }}'
                },
                success: function(response) {
                    if (response.status === 'success') {
                        location.reload();
                    }
                },
                error: function(xhr, status, error) {
                    console.error('Error unarchiving submission:', error);
                    alert('Failed to unarchive submission. Please try again.');
                }
            });
        }
    });
});
</script>
{% endblock %}

# Contents from: .\templates\submission\compare_versions.html
{% extends 'users/base.html' %}
{% load static %}
{% block content %}
<div class="container mt-4">
    <div class="card">
        <div class="card-header">
            <h2>Version Changes</h2>
            <h4 class="text-muted">{{ submission.title }}</h4>
            <p>Changes from Version {{ previous_version }} to Version {{ version }}</p>
        </div>
        <div class="card-body">
            {% if comparison_data %}
                {% for form_data in comparison_data %}
                    <div class="mb-4">
                        <h5 class="border-bottom pb-2">{{ form_data.form_name }}</h5>
                        <div class="table-responsive">
                            <table class="table table-bordered">
                                <thead>
                                    <tr>
                                        <th style="width: 30%">Field</th>
                                        <th style="width: 35%">Current Version (v{{ previous_version }})</th>
                                        <th style="width: 35%">Previous Version (v{{ version }})</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {% for change in form_data.changes %}
                                        <tr>
                                            <td class="fw-bold">{{ change.field }}</td>
                                            <td class="bg-light-yellow">
                                                {% if change.previous_value != None %}
                                                    {{ change.previous_value|linebreaks }}
                                                {% else %}
                                                    <em>No value</em>
                                                {% endif %}
                                            </td>
                                            <td class="bg-light-green">
                                                {% if change.current_value != None %}
                                                    {{ change.current_value|linebreaks }}
                                                {% else %}
                                                    <em>No value</em>
                                                {% endif %}
                                            </td>
                                        </tr>
                                    {% endfor %}
                                </tbody>
                            </table>
                        </div>
                    </div>
                {% endfor %}
            {% else %}
                <div class="alert alert-info">
                    <i class="fas fa-info-circle"></i> No changes found between these versions.
                </div>
            {% endif %}

            <div class="mt-4">
                <a href="{% url 'submission:version_history' submission.temporary_id %}" class="btn btn-secondary">
                    <i class="fas fa-arrow-left"></i> Back to Version History
                </a>
            </div>
        </div>
    </div>
</div>

<style>
    .bg-light-yellow {
        background-color: #fff3cd;
    }
    .bg-light-green {
        background-color: #d4edda;
    }
    table td span[style*="background-color"] {
        padding: 2px 4px;
        border-radius: 2px;
        display: inline-block;
    }
</style>

{% endblock %}
{% block page_specific_js %}
<script src="{% static 'js/version-compare.js' %}"></script>
{% endblock %}

# Contents from: .\templates\submission\dashboard.html
{% extends 'users/base.html' %}
{% load static %}

{% block title %}Dashboard{% endblock %}

{% block content %}
<div class="container mt-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
        <h1>My Submissions</h1>
        <div class="btn-group">
            <a href="{% url 'submission:start_submission' %}" class="btn btn-primary">
                <i class="fas fa-plus"></i> Start New Submission
            </a>
            <a href="{% url 'submission:archived_dashboard' %}" class="btn btn-secondary">
                <i class="fas fa-archive"></i> View Archived
            </a>
        </div>
    </div>

    {% if submissions_with_pending_forms %}
    <div class="alert alert-warning alert-dismissible fade show mb-4" role="alert">
        <i class="fas fa-exclamation-triangle"></i> You have pending forms to complete in one or more submissions.
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    </div>
    {% endif %}

    <div class="card">
        <div class="card-body">
            <div class="table-responsive">
                <table id="submissionsTable" class="table table-hover">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>KHCC #</th>
                            <th>Title</th>
                            <th>Primary Investigator</th>
                            <th>Status</th>
                            <th>Version</th>
                            <th>Date Created</th>
                            <th>Last Modified</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for submission in submissions %}
                        <tr>
                            <td>{{ submission.temporary_id|default:"" }}</td>
                            <td>{{ submission.khcc_number|default:"N/A" }}</td>
                            <td>{{ submission.title|default:"" }}</td>
                            <td>{{ submission.primary_investigator.userprofile.full_name }}</td>
                            <td>
                                <span class="badge badge-{{ submission.status|slugify }}">
                                    {{ submission.get_status_display|default:"" }}
                                </span>
                            </td>
                            <td>{{ submission.actual_version }}</td>
                            <td data-order="{{ submission.date_created|date:'Y-m-d H:i:s' }}">
                                {{ submission.date_created|date:"M d, Y H:i"|default:"" }}
                            </td>
                            <td data-order="{{ submission.last_modified|date:'Y-m-d H:i:s' }}">
                                {{ submission.last_modified|date:"M d, Y H:i"|default:"" }}
                            </td>
                            <td>
                                <div class="btn-group">
                                    {% if submission.is_locked %}
                                        <a href="{% url 'submission:edit_submission' submission.temporary_id %}" 
                                           class="btn btn-sm btn-danger" 
                                           title="Submission Locked">
                                            <i class="fas fa-lock"></i>
                                        </a>
                                    {% else %}
                                        <a href="{% url 'submission:edit_submission' submission.temporary_id %}" 
                                           class="btn btn-sm btn-success" 
                                           title="Edit Submission">
                                            <i class="fas fa-edit"></i>
                                        </a>
                                    {% endif %}

                                    {% if submission.has_pending %}
                                    <a href="{% url 'submission:version_history' submission.temporary_id %}" 
                                       class="btn btn-sm btn-info position-relative" 
                                       title="Version History - Has Pending Forms">
                                        <i class="fas fa-history"></i>
                                        <span class="position-absolute top-0 start-100 translate-middle p-1 bg-danger rounded-circle">
                                            <span class="visually-hidden">Pending forms</span>
                                        </span>
                                    </a>
                                {% else %}
                                    <a href="{% url 'submission:version_history' submission.temporary_id %}" 
                                       class="btn btn-sm btn-info" 
                                       title="History">
                                        <i class="fas fa-history"></i>
                                    </a>
                                        {% endif %}

                                    <a href="{% url 'submission:submission_actions' submission.temporary_id %}" 
                                       class="btn btn-sm btn-primary" 
                                       title="Actions">
                                        <i class="fas fa-cogs"></i>
                                    </a>
                                    <a href="{% url 'submission:download_submission_pdf' submission.temporary_id %}" 
                                       class="btn btn-sm btn-secondary" 
                                       title="Download PDF">
                                        <i class="fas fa-file-pdf"></i>
                                    </a>
                                    <button class="btn btn-sm btn-warning archive-submission" 
                                            data-submission-id="{{ submission.temporary_id }}"
                                            title="Archive Submission">
                                        <i class="fas fa-archive"></i>
                                    </button>
                                </div>
                            </td>
                        </tr>
                        {% empty %}
                        <tr>
                            <td colspan="9" class="text-center">No submissions found.</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block page_specific_js %}
{{ block.super }}
<script src="https://cdn.datatables.net/1.10.24/js/jquery.dataTables.min.js"></script>
<script src="https://cdn.datatables.net/1.10.24/js/dataTables.bootstrap4.min.js"></script>
<script>
$(document).ready(function() {
    // Initialize DataTable
    $('#submissionsTable').DataTable({
        processing: true,
        serverSide: false,
        pageLength: 10,
        order: [[6, "desc"]],
        columnDefs: [
            { orderable: false, targets: 8 }
        ]
    });

    // Initialize all tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });

    // Archive submission handler
    $('.archive-submission').click(function() {
        const submissionId = $(this).data('submission-id');
        if (confirm('Are you sure you want to archive this submission?')) {
            $.ajax({
                url: `/submission/archive/${submissionId}/`,
                type: 'POST',
                headers: {
                    'X-CSRFToken': '{{ csrf_token }}'
                },
                success: function(response) {
                    if (response.status === 'success') {
                        location.reload();
                    }
                },
                error: function(xhr, status, error) {
                    console.error('Error archiving submission:', error);
                    alert('Failed to archive submission. Please try again.');
                }
            });
        }
    });
});
</script>
{% endblock %}



# Contents from: .\templates\submission\dynamic_actions.html
{# submission/dynamic_form.html #}
{% extends 'users/base.html' %}
{% load crispy_forms_tags %}

{% block content %}
<div class="container mt-4">
    <div class="card">
        <div class="card-header">
            <h2>{{ dynamic_form.name }}</h2>
            <h6 class="text-muted">{{ submission.title }}</h6>
        </div>
        <div class="card-body">
            <form method="post" novalidate>
                {% csrf_token %}
                {{ form|crispy }}
                <div class="d-grid gap-2 d-md-flex justify-content-md-start mt-4">
                    <button type="submit" name="action" value="exit_no_save" class="btn btn-danger me-md-2" formnovalidate>
                        <i class="fas fa-times"></i> Exit without Saving
                    </button>
                    <button type="submit" name="action" value="submit" class="btn btn-primary">
                        <i class="fas fa-check"></i> Submit
                    </button>
                </div>
            </form>
        </div>
    </div>
</div>
{% endblock %}

# Contents from: .\templates\submission\dynamic_form.html
{# submission/dynamic_form.html #}
{% extends 'users/base.html' %}
{% load crispy_forms_tags %}

{% block content %}
<div class="container mt-4">
    <div class="card">
        <div class="card-header">
            <h2>{{ dynamic_form.name }}</h2>
            {% if submission.version > 1 and not submission.is_locked %}
            <div class="alert alert-info">
                <i class="fas fa-info-circle"></i> This form has been pre-populated with data from the previous version.
            </div>
            {% endif %}
        </div>
        <div class="card-body">
            <form method="post" novalidate>
                {% csrf_token %}
                {{ form|crispy }}
                <div class="d-grid gap-2 d-md-flex justify-content-md-start mt-4">
                    <button type="submit" name="action" value="back" class="btn btn-secondary me-md-2">
                        <i class="fas fa-arrow-left"></i> 
                        {% if previous_form %}
                            Back to {{ previous_form.name }}
                        {% else %}
                            Back to Co-Investigators
                        {% endif %}
                    </button>
                    <button type="submit" name="action" value="exit_no_save" class="btn btn-danger me-md-2">
                        <i class="fas fa-times"></i> Exit without Saving
                    </button>
                    <button type="submit" name="action" value="save_exit" class="btn btn-primary me-md-2">
                        <i class="fas fa-save"></i> Save and Exit
                    </button>
                    <button type="submit" name="action" value="save_continue" class="btn btn-success">
                        <i class="fas fa-arrow-right"></i> Save and Continue
                    </button>
                </div>
            </form>
        </div>
    </div>
</div>
{% endblock %}

# Contents from: .\templates\submission\edit_submission.html
{% extends 'users/base.html' %}
{% load static %}

{% block title %}Edit Submission{% endblock %}

{% block content %}
<div class="container mt-4">
    <h2>Edit Submission</h2>
    
    {% if messages %}
    <div class="messages">
        {% for message in messages %}
        <div class="alert alert-{{ message.tags }}">
            {{ message }}
        </div>
        {% endfor %}
    </div>
    {% endif %}
    
    <form method="post">
        {% csrf_token %}
        {{ form.as_p }}
        <button type="submit" class="btn btn-primary">Save Changes</button>
        <a href="{% url 'submission:dashboard' %}" class="btn btn-secondary">Cancel</a>
    </form>
</div>
{% endblock %}

{% block extra_css %}
{{ block.super }}
<style>
    .form-group label {
        font-weight: 500;
    }
    .errorlist {
        color: #dc3545;
        list-style: none;
        padding-left: 0;
        margin-bottom: 0.5rem;
    }
    select, input {
        width: 100%;
        padding: 0.375rem 0.75rem;
        font-size: 1rem;
        line-height: 1.5;
        border: 1px solid #ced4da;
        border-radius: 0.25rem;
    }
    .select2-container {
        width: 100% !important;
    }
</style>
{% endblock %}

{% block extra_js %}
{{ block.super }}
{{ form.media }}
{% endblock %}


# Contents from: .\templates\submission\investigator_form.html

{# investigator_form.html #}
{% extends 'users/base.html' %}
{% load crispy_forms_tags %}

{% block content %}
<div class="container mt-4">
    <div class="card">
        <div class="card-header">
            <h2>{{ dynamic_form.name }}</h2>
            <h6 class="text-muted">Submission: {{ submission.title }}</h6>
        </div>
        <div class="card-body">
            <form method="post" novalidate>
                {% csrf_token %}
                {{ form|crispy }}
                <div class="d-grid gap-2 d-md-flex justify-content-md-end mt-4">
                    <a href="{% url 'submission:dashboard' %}" 
                       class="btn btn-secondary me-md-2">
                        <i class="fas fa-times"></i> Cancel
                    </a>
                    <button type="submit" 
                            name="action" 
                            value="submit_form" 
                            class="btn btn-primary">
                        <i class="fas fa-save"></i> Submit Form
                    </button>
                </div>
            </form>
        </div>
    </div>
</div>
{% endblock %}

# Contents from: .\templates\submission\review.html
{% extends 'users/base.html' %}
{% load crispy_forms_tags %}
{% block content %}
<div class="container mt-4">
    <h1>Submission Review</h1>
    <!-- Display missing documents -->
    {% if missing_documents %}
        <div class="alert alert-danger">
            <h4>Missing Documents:</h4>
            <ul>
                {% for key, value in missing_documents.items %}
                    <li>{{ key }} - {{ value.name }}
                        <ul>
                            {% for doc in value.documents %}
                                <li>{{ doc }}</li>
                            {% endfor %}
                        </ul>
                    </li>
                {% endfor %}
            </ul>
        </div>
    {% endif %}

    <!-- Display validation errors -->
    {% if validation_errors %}
        <div class="alert alert-danger">
            <h4>Form Validation Errors:</h4>
            <ul>
                {% for form_name, errors in validation_errors.items %}
                    <li>{{ form_name }}
                        <ul>
                            {% for field, error_list in errors.items %}
                                <li>{{ field }}: {{ error_list|join:", " }}</li>
                            {% endfor %}
                        </ul>
                    </li>
                {% endfor %}
            </ul>
        </div>
    {% endif %}

    <!-- Document Repository -->
    <h2>Document Repository</h2>
    <form method="post" enctype="multipart/form-data">
        {% csrf_token %}
        {{ doc_form|crispy }}
        <button type="submit" name="action" value="upload_document" class="btn btn-primary">Upload Document</button>
    </form>
    <table class="table mt-3">
        <thead>
            <tr>
                <th>Filename</th>
                <th>Description</th>
                <th>Uploaded By</th>
                <th>Uploaded At</th>
                <th>Actions</th>
            </tr>
        </thead>
        <tbody>
            {% for doc in documents %}
            <tr>
                <td>{{ doc.filename }}</td>
                <td>{{ doc.description }}</td>
                <td>{{ doc.uploaded_by.get_full_name }}</td>
                <td>{{ doc.uploaded_at }}</td>
                <td>
                    <a href="{{ doc.file.url }}" class="btn btn-sm btn-secondary">Download</a>
                    <a href="{% url 'submission:document_delete' submission.temporary_id doc.id %}" class="btn btn-sm btn-danger">Delete</a>
                </td>
            </tr>
            {% empty %}
            <tr>
                <td colspan="5">No documents uploaded.</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>

    <form method="post">
        {% csrf_token %}
        <div class="d-grid gap-2 d-md-flex justify-content-md-start mt-4">
            <button type="submit" name="action" value="back" class="btn btn-secondary me-md-2">
                <i class="fas fa-arrow-left"></i> Back
            </button>
            <button type="submit" name="action" value="exit_no_save" class="btn btn-danger me-md-2">
                <i class="fas fa-times"></i> Exit without Saving
            </button>
            <button type="submit" name="action" value="submit_final" class="btn btn-success">
                <i class="fas fa-check"></i> Submit Final
            </button>
        </div>
    </form>
</div>
{% endblock %}


# Contents from: .\templates\submission\review1.html
{% extends 'users/base.html' %}
{% block content %}
<div class="container mt-4">
    <div class="card">
        <div class="card-header">
            <h2>Version History</h2>
            <h4 class="text-muted">{{ submission.title }}</h4>
        </div>
        <div class="card-body">
            <div class="table-responsive">
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
                            <td>
                                <span class="status-badge {{ history.status|lower }}">
                                    <i class="fas {% if history.status == 'draft' %}fa-pencil-alt
                                                {% elif history.status == 'submitted' %}fa-paper-plane
                                                {% elif history.status == 'under_review' %}fa-search
                                                {% elif history.status == 'revision_requested' %}fa-edit
                                                {% elif history.status == 'under_revision' %}fa-pen
                                                {% elif history.status == 'approved' %}fa-check
                                                {% elif history.status == 'rejected' %}fa-times
                                                {% elif history.status == 'terminated' %}fa-ban
                                                {% elif history.status == 'suspended' %}fa-pause
                                                {% endif %}"></i>
                                    {{ history.get_status_display }}
                                </span>
                            </td>
                            <td>{{ history.date|date:"M d, Y H:i" }}</td>
                            <td>
                                <div class="btn-group" role="group">
                                    {% if not forloop.first %}
                                    <a href="{% url 'submission:compare_versions' submission.temporary_id history.version submission.version %}" 
                                       class="btn btn-sm btn-primary me-1" 
                                       title="Compare with Current Version">
                                        <i class="fas fa-code-compare"></i> Compare with Current
                                    </a>
                                    {% endif %}
                                    <a href="{% url 'submission:download_submission_pdf_version' submission.temporary_id history.version %}" 
                                       class="btn btn-sm btn-secondary" 
                                       title="Download PDF">
                                        <i class="fas fa-file-pdf"></i> Download
                                    </a>
                                </div>
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
            
            {% if submission.get_required_investigator_forms %}
            <div class="card mt-4">
                <div class="card-header d-flex justify-content-between align-items-center">
                    <h4 class="mb-0">Required Investigator Forms</h4>
                    {% if not submission.is_locked %}
                        <a href="#" id="refreshStatus" class="btn btn-sm btn-outline-primary">
                            <i class="fas fa-sync-alt"></i> Refresh Status
                        </a>
                    {% endif %}
                </div>
                <div class="card-body">
                    {% with form_status=submission.get_investigator_form_status %}
                    {% if form_status %}
                        {% for form_name, status in form_status.items %}
                        <h5 class="mb-3">{{ form_name }}</h5>
                        <div class="table-responsive">
                            <table class="table table-bordered table-hover">
                                <thead class="table-light">
                                    <tr>
                                        <th>Investigator</th>
                                        <th>Role</th>
                                        <th>Department</th>
                                        <th>Status</th>
                                        <th>Submission Date</th>
                                        <th>Actions</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {% for inv in status.investigators %}
                                    <tr>
                                        <td>
                                            {{ inv.user.get_full_name }}
                                            {% if inv.is_pi %}
                                            <span class="badge bg-info ms-1">PI</span>
                                            {% endif %}
                                        </td>
                                        <td>{{ inv.role }}</td>
                                        <td>{{ inv.user.userprofile.department|default:"Not specified" }}</td>
                                        <td>
                                            {% if inv.submitted %}
                                                <span class="badge bg-success">
                                                    <i class="fas fa-check"></i> Submitted
                                                </span>
                                            {% else %}
                                                <span class="badge bg-warning">
                                                    <i class="fas fa-clock"></i> Pending
                                                </span>
                                            {% endif %}
                                        </td>
                                        <td>
                                            {% if inv.submitted %}
                                                {{ inv.submitted|date:"M d, Y H:i" }}
                                            {% else %}
                                                -
                                            {% endif %}
                                        </td>
                                        <td>
                                            {% if inv.submitted %}
                                                <a href="{% url 'submission:download_submission_pdf_version' submission.temporary_id status.form.version %}" 
                                                   class="btn btn-sm btn-secondary">
                                                    <i class="fas fa-file-pdf"></i> View Response
                                                </a>
                                            {% elif user == inv.user and not submission.is_locked %}
                                                <a href="{% url 'submission:investigator_form' submission.temporary_id status.form.id %}" 
                                                   class="btn btn-sm btn-primary">
                                                    <i class="fas fa-edit"></i> Fill Form
                                                </a>
                                            {% else %}
                                                -
                                            {% endif %}
                                        </td>
                                    </tr>
                                    {% endfor %}
                                </tbody>
                            </table>
                        </div>

                        {% if forloop.last %}
                        <div class="alert {% if submission.are_all_investigator_forms_complete %}alert-success{% else %}alert-warning{% endif %} mt-3">
                            {% if submission.are_all_investigator_forms_complete %}
                                <i class="fas fa-check-circle"></i> All required forms have been submitted.
                            {% else %}
                                <i class="fas fa-exclamation-circle"></i> Some forms are still pending submission.
                            {% endif %}
                        </div>
                        {% endif %}
                        {% endfor %}
                    {% else %}
                        <div class="alert alert-info">
                            <i class="fas fa-info-circle"></i> No form submissions required for this version.
                        </div>
                    {% endif %}
                    {% endwith %}
                </div>
            </div>
            {% endif %}
            
            <div class="mt-4">
                <a href="{% url 'submission:dashboard' %}" class="btn btn-secondary">
                    <i class="fas fa-arrow-left"></i> Back to Dashboard
                </a>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block page_specific_js %}
<script>
$(document).ready(function() {
    // Handle refresh status button click
    $('#refreshStatus').click(function(e) {
        e.preventDefault();
        $.ajax({
            url: "{% url 'submission:check_form_status' submission.temporary_id %}",
            method: 'GET',
            success: function(response) {
                location.reload();
            },
            error: function(xhr, status, error) {
                console.error('Error refreshing status:', error);
                alert('Failed to refresh status. Please try again.');
            }
        });
    });
});
</script>
{% endblock %}

# Contents from: .\templates\submission\some_template.html
<a href="{% url 'submission:submission_review' temporary_id=submission.temporary_id %}">Review</a> 

# Contents from: .\templates\submission\start_submission.html
{% extends 'users/base.html' %}
{% load crispy_forms_tags %}

{% block title %}Start New Submission{% endblock %}

{% block page_specific_css %}
{% endblock %}

{% block content %}
<div class="container mt-4">
    <div class="row">
        <div class="col-md-8 offset-md-2">
            <div class="card">
                <div class="card-header">
                    <h2>Start New Submission</h2>
                </div>
                <div class="card-body">
                    <form method="post" novalidate>
                        {% csrf_token %}
                        {{ form|crispy }}
                        
                        <!-- Role Selection -->
                        <div id="role_selection_div" style="display: none;" class="mb-3">
                            <label for="user_role" class="form-label">What is your role in this submission?</label>
                            <select name="user_role" id="user_role" class="form-select" required>
                                <option value="">Select your role...</option>
                                <option value="coinvestigator">Co-Investigator</option>
                            </select>
                            
                            <!-- Co-Investigator specific roles (hidden by default) -->
                            <div id="coinvestigator_roles" style="display: none;" class="mt-3">
                                <label class="form-label">Select your role as Co-Investigator:</label>
                                <div class="form-check">
                                    <input type="checkbox" name="ci_roles" value="PI" class="form-check-input" id="role_pi">
                                    <label class="form-check-label" for="role_pi">Principal Investigator</label>
                                </div>
                                <div class="form-check">
                                    <input type="checkbox" name="ci_roles" value="CO_PI" class="form-check-input" id="role_co_pi">
                                    <label class="form-check-label" for="role_co_pi">Co-Principal Investigator</label>
                                </div>
                                <div class="form-check">
                                    <input type="checkbox" name="ci_roles" value="SUB_I" class="form-check-input" id="role_sub_i">
                                    <label class="form-check-label" for="role_sub_i">Sub-Investigator</label>
                                </div>
                                <div class="form-check">
                                    <input type="checkbox" name="ci_roles" value="DATA_MANAGER" class="form-check-input" id="role_data_manager">
                                    <label class="form-check-label" for="role_data_manager">Data Manager</label>
                                </div>
                                <div class="form-check">
                                    <input type="checkbox" name="ci_roles" value="STATISTICIAN" class="form-check-input" id="role_statistician">
                                    <label class="form-check-label" for="role_statistician">Statistician</label>
                                </div>
                                <div class="form-check">
                                    <input type="checkbox" name="ci_roles" value="CONSULTANT" class="form-check-input" id="role_consultant">
                                    <label class="form-check-label" for="role_consultant">Consultant</label>
                                </div>
                                <div class="form-check">
                                    <input type="checkbox" name="ci_roles" value="OTHER" class="form-check-input" id="role_other">
                                    <label class="form-check-label" for="role_other">Other</label>
                                </div>
                            </div>
                        </div>

                        <div class="d-grid gap-2 d-md-flex justify-content-md-end mt-4">
                            <button type="submit" name="action" value="exit_no_save" class="btn btn-danger me-md-2">
                                <i class="fas fa-times"></i> Exit without Saving
                            </button>
                            <button type="submit" name="action" value="save_exit" class="btn btn-primary me-md-2">
                                <i class="fas fa-save"></i> Save and Exit
                            </button>
                            <button type="submit" name="action" value="save_continue" class="btn btn-success">
                                <i class="fas fa-arrow-right"></i> Save and Continue
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
    $(document).ready(function() {
        // Initialize Select2 for primary investigator field
        $('#id_primary_investigator').select2({
            theme: 'bootstrap4',
            ajax: {
                url: '{% url "submission:user-autocomplete" %}',
                dataType: 'json',
                delay: 250,
                data: function (params) {
                    return {
                        term: params.term,
                        page: params.page
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
            placeholder: 'Search for investigators...',
            allowClear: true
        });

        // Handle initial value
        {% if form.primary_investigator.initial %}
        var initialUser = {
            id: {{ form.primary_investigator.initial.id }},
            text: '{{ form.primary_investigator.initial.get_full_name|escapejs }}'
        };
        var initialOption = new Option(initialUser.text, initialUser.id, true, true);
        $('#id_primary_investigator').append(initialOption).trigger('change');
        {% endif %}

        // Toggle PI field and role selection visibility
        function toggleFields() {
            if ($('#id_is_primary_investigator').is(':checked')) {
                $('#div_id_primary_investigator').hide();
                $('#role_selection_div').hide();
            } else {
                $('#div_id_primary_investigator').show();
                $('#role_selection_div').show();
            }
        }

        // Toggle co-investigator roles visibility
        $('#user_role').change(function() {
            if ($(this).val() === 'coinvestigator') {
                $('#coinvestigator_roles').show();
            } else {
                $('#coinvestigator_roles').hide();
            }
        });

        $('#id_is_primary_investigator').change(toggleFields);
        toggleFields();
    });
</script>
{% endblock %}

# Contents from: .\templates\submission\submission_actions.html
{% extends 'users/base.html' %}
{% block content %}
<div class="container mt-4">
    <div class="card">
        <div class="card-header">
            <h2>Study Actions</h2>
            <h6 class="text-muted">{{ submission.title }}</h6>
            <span class="badge bg-{{ submission.status|lower }} text-white">
                {{ submission.get_status_display }}
            </span>
        </div>
        <div class="card-body">
            {% if not can_submit %}
            <div class="alert alert-warning">
                <i class="fas fa-exclamation-triangle"></i> You don't have permission to perform study actions. Only users with submission rights can perform these actions.
            </div>
            {% endif %}


            <div class="row">
                <!-- Withdraw Study -->
                <div class="col-md-6 mb-4">
                    <div class="card h-100">
                        <div class="card-header bg-danger text-white">
                            <h5 class="mb-0"><i class="fas fa-times-circle"></i> Withdraw Study</h5>
                        </div>
                        <div class="card-body">
                            <p>Withdraw your study from the review process. This action:</p>
                            <ul>
                                <li>Permanently withdraws the study</li>
                                <li>Locks the submission</li>
                                <li>Notifies all team members</li>
                                <li>Cannot be undone</li>
                            </ul>
                            {% if not can_submit %}
                                <div class="alert alert-warning mt-3">
                                    <i class="fas fa-lock"></i> You need submission rights to withdraw the study
                                </div>
                          
                            {% else %}
                                <a href="{% url 'submission:study_withdrawal' submission.temporary_id %}" 
                                   class="btn btn-danger mt-3"
                                   onclick="return confirm('Are you sure you want to withdraw this study? This action cannot be undone.')">
                                    <i class="fas fa-times-circle"></i> Withdraw Study
                                </a>
                            {% endif %}
                        </div>
                    </div>
                </div>

                <!-- Progress Report -->
                <div class="col-md-6 mb-4">
                    <div class="card h-100">
                        <div class="card-header bg-info text-white">
                            <h5 class="mb-0"><i class="fas fa-chart-line"></i> Progress Report</h5>
                        </div>
                        <div class="card-body">
                            <p>Submit a progress report for your study. This will:</p>
                            <ul>
                                <li>Update OSAR on study progress</li>
                                <li>Be recorded in study history</li>
                                <li>Be available to all team members</li>
                                <li>Help maintain study compliance</li>
                            </ul>
                            {% if not can_submit %}
                                <div class="alert alert-warning mt-3">
                                    <i class="fas fa-lock"></i> You need submission rights to submit a progress report
                                </div>
                            {% else %}
                                <a href="{% url 'submission:progress_report' submission.temporary_id %}" 
                                   class="btn btn-info mt-3">
                                    <i class="fas fa-chart-line"></i> Submit Progress Report
                                </a>
                            {% endif %}
                        </div>
                    </div>
                </div>

                <!-- Study Amendment -->
                <div class="col-md-6 mb-4">
                    <div class="card h-100">
                        <div class="card-header bg-warning">
                            <h5 class="mb-0"><i class="fas fa-edit"></i> Study Amendment</h5>
                        </div>
                        <div class="card-body">
                            <p>Submit an amendment to your study. Use this to:</p>
                            <ul>
                                <li>Request changes to study protocol</li>
                                <li>Update study parameters</li>
                                <li>Modify study procedures</li>
                                <li>Request team member changes</li>
                            </ul>
                            {% if not can_submit %}
                                <div class="alert alert-warning mt-3">
                                    <i class="fas fa-lock"></i> You need submission rights to submit an amendment
                                </div>
                            {% else %}
                                <a href="{% url 'submission:study_amendment' submission.temporary_id %}" 
                                   class="btn btn-warning mt-3">
                                    <i class="fas fa-edit"></i> Submit Amendment
                                </a>
                            {% endif %}
                        </div>
                    </div>
                </div>

                <!-- Study Closure -->
                <div class="col-md-6 mb-4">
                    <div class="card h-100">
                        <div class="card-header bg-secondary text-white">
                            <h5 class="mb-0"><i class="fas fa-door-closed"></i> Study Closure</h5>
                        </div>
                        <div class="card-body">
                            <p>Close your completed study. This action:</p>
                            <ul>
                                <li>Marks the study as completed</li>
                                <li>Locks the submission</li>
                                <li>Notifies all team members</li>
                                <li>Cannot be undone</li>
                            </ul>
                            {% if not can_submit %}
                                <div class="alert alert-warning mt-3">
                                    <i class="fas fa-lock"></i> You need submission rights to close the study
                                </div>
                            {% else %}
                                <a href="{% url 'submission:study_closure' submission.temporary_id %}" 
                                   class="btn btn-secondary mt-3"
                                   onclick="return confirm('Are you sure you want to close this study? This action cannot be undone.')">
                                    <i class="fas fa-door-closed"></i> Close Study
                                </a>
                            {% endif %}
                        </div>
                    </div>
                </div>
            </div>

            <div class="mt-4">
                <a href="{% url 'submission:dashboard' %}" class="btn btn-secondary">
                    <i class="fas fa-arrow-left"></i> Back to Dashboard
                </a>
            </div>
        </div>
    </div>
</div>
{% endblock %}

# Contents from: .\templates\submission\submission_forms.html
{% extends 'base.html' %}
{% load crispy_forms_tags %}
{% block title %}Fill Submission Forms{% endblock %}
{% block content %}
<h1>Fill Submission Forms</h1>
<form method="post" novalidate>
    {% csrf_token %}
    {% for dynamic_form, form in forms_list %}
        <h2>{{ dynamic_form.name }}</h2>
        {{ form|crispy }}
    {% endfor %}
    <button type="submit" name="action" value="save_exit" class="btn btn-primary">Save and Exit</button>
    <button type="submit" name="action" value="save_continue" class="btn btn-primary">Save and Continue</button>
    <button type="submit" name="action" value="exit_no_save" class="btn btn-secondary">Exit without Saving</button>
</form>
{% endblock %}


# Contents from: .\templates\submission\submission_list.html
{% extends 'users/base.html' %}
{% load static %}

{% block title %}My Submissions{% endblock %}

{% block content %}
<div class="container mt-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
        <h1>My Submissions</h1>
        <a href="{% url 'submission:start_submission' %}" class="btn btn-primary">
            <i class="fas fa-plus"></i> New Submission
        </a>
    </div>

    {% if messages %}
        {% for message in messages %}
            <div class="alert alert-{{ message.tags }} alert-dismissible fade show" role="alert">
                {{ message }}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            </div>
        {% endfor %}
    {% endif %}

    {% if submissions %}
        <div class="table-responsive">
            <table class="table table-hover">
                <thead>
                    <tr>
                        <th>Title</th>
                        <th>Study Type</th>
                        <th>Primary Investigator</th>
                        <th>Status</th>
                        <th>Last Updated</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {% for submission in submissions %}
                        <tr>
                            <td>{{ submission.title }}</td>
                            <td>{{ submission.study_type }}</td>
                            <td>{{ submission.primary_investigator.get_full_name }}</td>
                            <td>
                                <span class="badge bg-{{ submission.get_status_color }}">
                                    {{ submission.get_status_display }}
                                </span>
                            </td>
                            <td>{{ submission.updated_at|date:"M d, Y" }}</td>
                            <td>
                                <a href="{% url 'submission:edit_submission' submission_id=submission.id %}" 
                                   class="btn btn-sm btn-outline-primary">
                                    <i class="fas fa-edit"></i> Edit
                                </a>
                            </td>
                        </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    {% else %}
        <div class="alert alert-info">
            <i class="fas fa-info-circle"></i> You don't have any submissions yet. 
            <a href="{% url 'submission:start_submission' %}" class="alert-link">Create your first submission</a>.
        </div>
    {% endif %}
</div>
{% endblock %} 

# Contents from: .\templates\submission\submission_pdf.html
<!DOCTYPE html>
<html>
<head>
    <title>Submission {{ submission.temporary_id }}</title>
    <style>
        /* Add styles for PDF */
    </style>
</head>
<body>
    <h1>Submission {{ submission.temporary_id }}</h1>
    <p>Title: {{ submission.title }}</p>
    <p>Primary Investigator: {{ submission.primary_investigator.get_full_name }}</p>
    <!-- Add more details as needed -->
    <h2>Form Data</h2>
    <div class="form-group">
        {% for entry in entries %}
            <h3>{{ entry.form.name }}</h3>
            <p class="form-control">{{ entry.field_name }}: {{ entry.value }}</p>
        {% endfor %}
    </div>
</body>
</html>


# Contents from: .\templates\submission\submission_review.html
{% extends 'users/base.html' %}
{% load crispy_forms_tags %}

{% block content %}
<div class="container mt-4">
    <div class="card">
        <div class="card-header">
            <h2>Submission Review</h2>
            <h4 class="text-muted">{{ submission.title }}</h4>
        </div>

        <div class="card-body">
            <!-- Primary Investigator Section -->
            <div class="card mb-4">
                <div class="card-header">
                    <h4>Primary Investigator Documents</h4>
                    <h6>{{ submission.primary_investigator.get_full_name }}</h6>
                </div>
                <div class="card-body">
                    {% with profile=submission.primary_investigator.userprofile %}
                    <ul class="list-group">
                        <li class="list-group-item {% if profile.has_valid_gcp %}list-group-item-success{% else %}list-group-item-danger{% endif %}">
                            <i class="fas {% if profile.has_valid_gcp %}fa-check{% else %}fa-times{% endif %}"></i>
                            GCP Certificate
                            {% if profile.is_gcp_expired %}
                            <span class="badge bg-danger">Expired</span>
                            {% endif %}
                        </li>
                        <li class="list-group-item {% if profile.has_cv %}list-group-item-success{% else %}list-group-item-danger{% endif %}">
                            <i class="fas {% if profile.has_cv %}fa-check{% else %}fa-times{% endif %}"></i>
                            CV
                        </li>
                        <li class="list-group-item {% if profile.has_qrc %}list-group-item-success{% else %}list-group-item-danger{% endif %}">
                            <i class="fas {% if profile.has_qrc %}fa-check{% else %}fa-times{% endif %}"></i>
                            QRC Certificate
                        </li>
                        <li class="list-group-item {% if profile.has_ctc %}list-group-item-success{% else %}list-group-item-danger{% endif %}">
                            <i class="fas {% if profile.has_ctc %}fa-check{% else %}fa-times{% endif %}"></i>
                            CTC Certificate
                        </li>
                    </ul>
                    {% endwith %}
                </div>
            </div>

            <!-- Co-Investigators Section -->
            {% if submission.coinvestigators.exists %}
            <div class="card mb-4">
                <div class="card-header">
                    <h4>Co-Investigators Documents</h4>
                </div>
                <div class="card-body">
                    {% for coinv in submission.coinvestigators.all %}
                    <div class="mb-4">
                        <h6>{{ coinv.user.get_full_name }} - {{ coinv.get_roles_display }}</h6>
                        {% with profile=coinv.user.userprofile %}
                        <ul class="list-group">
                            <li class="list-group-item {% if profile.has_valid_gcp %}list-group-item-success{% else %}list-group-item-danger{% endif %}">
                                <i class="fas {% if profile.has_valid_gcp %}fa-check{% else %}fa-times{% endif %}"></i>
                                GCP Certificate
                                {% if profile.is_gcp_expired %}
                                <span class="badge bg-danger">Expired</span>
                                {% endif %}
                            </li>
                            <li class="list-group-item {% if profile.has_cv %}list-group-item-success{% else %}list-group-item-danger{% endif %}">
                                <i class="fas {% if profile.has_cv %}fa-check{% else %}fa-times{% endif %}"></i>
                                CV
                            </li>
                            <li class="list-group-item {% if profile.has_qrc %}list-group-item-success{% else %}list-group-item-danger{% endif %}">
                                <i class="fas {% if profile.has_qrc %}fa-check{% else %}fa-times{% endif %}"></i>
                                QRC Certificate
                            </li>
                            <li class="list-group-item {% if profile.has_ctc %}list-group-item-success{% else %}list-group-item-danger{% endif %}">
                                <i class="fas {% if profile.has_ctc %}fa-check{% else %}fa-times{% endif %}"></i>
                                CTC Certificate
                            </li>
                        </ul>
                        {% endwith %}
                    </div>
                    {% endfor %}
                </div>
            </div>
            {% endif %}

            <!-- Missing Documents Alert -->
            {% if missing_documents %}
            <div class="alert alert-danger">
                <h4>Missing Documents:</h4>
                <ul>
                    {% for key, value in missing_documents.items %}
                    <li>{{ key }} - {{ value.name }}
                        <ul>
                            {% for doc in value.documents %}
                            <li>{{ doc }}</li>
                            {% endfor %}
                        </ul>
                    </li>
                    {% endfor %}
                </ul>
            </div>
            {% endif %}

            <!-- Validation Errors Alert -->
            {% if validation_errors %}
            <div class="alert alert-danger">
                <h4>Form Validation Errors:</h4>
                <ul>
                    {% for form_name, errors in validation_errors.items %}
                    <li><strong>{{ form_name }}</strong>
                        <ul>
                            {% for field, error_list in errors.items %}
                            <li>{{ field }}: {{ error_list|join:", " }}</li>
                            {% endfor %}
                        </ul>
                    </li>
                    {% endfor %}
                </ul>
            </div>
            {% endif %}

            <!-- Document Repository -->
            <div class="card mb-4">
                <div class="card-header">
                    <h4>Document Repository</h4>
                </div>
                <div class="card-body">
                    <form method="post" enctype="multipart/form-data" class="mb-4">
                        {% csrf_token %}
                        <div class="row">
                            <div class="col-md-6">
                                {{ doc_form.file|as_crispy_field }}
                            </div>
                            <div class="col-md-6">
                                <label for="{{ doc_form.description.id_for_label }}" class="form-label">Description *</label>
                                {{ doc_form.description }}
                                {% if doc_form.description.errors %}
                                <div class="invalid-feedback">
                                    {{ doc_form.description.errors }}
                                </div>
                                {% endif %}
                            </div>
                        </div>
                        <button type="submit" name="action" value="upload_document" class="btn btn-primary mt-3">
                            <i class="fas fa-upload"></i> Upload Document
                        </button>
                    </form>

                    <div class="table-responsive">
                        <table class="table">
                            <thead>
                                <tr>
                                    <th>Filename</th>
                                    <th>Description</th>
                                    <th>Uploaded By</th>
                                    <th>Uploaded At</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for doc in documents %}
                                <tr>
                                    <td>{{ doc.file.name|slice:"documents/" }}</td>
                                    <td>{{ doc.description }}</td>
                                    <td>{{ doc.uploaded_by.get_full_name }}</td>
                                    <td>{{ doc.uploaded_at|date:"M d, Y H:i" }}</td>
                                    <td>
                                        <div class="btn-group">
                                            <a href="{{ doc.file.url }}" class="btn btn-sm btn-secondary">
                                                <i class="fas fa-download"></i> Download
                                            </a>
                                            <a href="{% url 'submission:document_delete' submission.temporary_id doc.id %}" 
                                               class="btn btn-sm btn-danger"
                                               onclick="return confirm('Are you sure you want to delete this document?')">
                                                <i class="fas fa-trash"></i> Delete
                                            </a>
                                        </div>
                                    </td>
                                </tr>
                                {% empty %}
                                <tr>
                                    <td colspan="5" class="text-center">No documents uploaded.</td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            <!-- Action Buttons -->
            <form method="post" class="d-flex gap-2">
                {% csrf_token %}
                <button type="submit" name="action" value="back" class="btn btn-secondary">
                    <i class="fas fa-arrow-left"></i> Back
                </button>
                {% if can_submit %}
                <button type="submit" name="action" value="exit_no_save" class="btn btn-danger">
                    <i class="fas fa-times"></i> Exit without Saving
                </button>
                <button type="submit" name="action" value="submit_final" class="btn btn-success">
                    <i class="fas fa-check"></i> Submit Final
                </button>
                {% endif %}
            </form>

            <!-- Loading Indicator -->
            <div id="loadingIndicator" style="display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0, 0, 0, 0.5); z-index: 9999;">
                <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); background: white; padding: 20px; border-radius: 8px; text-align: center;">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                    <p class="mt-3 mb-0">Processing submission...</p>
                </div>
            </div>
        </div>
    </div>
</div>

{% block page_specific_js %}
<script>
document.addEventListener('DOMContentLoaded', function() {
    const finalSubmitForm = document.querySelector('form:last-of-type');
    finalSubmitForm.addEventListener('submit', function(e) {
        if (e.target.querySelector('button[name="action"]').value === 'submit_final') {
            const hasMissingDocs = {% if missing_documents %}true{% else %}false{% endif %};
            const hasValidationErrors = {% if validation_errors %}true{% else %}false{% endif %};
            const invalidCertificates = document.querySelectorAll('.list-group-item-danger');
            const hasInvalidCertificates = invalidCertificates.length > 0;

            if (hasInvalidCertificates) {
                e.preventDefault();
                alert('Cannot submit: All team members must have valid certificates before submission.');
                return false;
            }
            
            if (hasMissingDocs || hasValidationErrors) {
                e.preventDefault();
                alert('Cannot submit: Please ensure all mandatory fields are filled and required documents are uploaded.');
                return false;
            }

            document.getElementById('loadingIndicator').style.display = 'block';
        }
    });
});
</script>
{% endblock %}

{% endblock %}

# Contents from: .\templates\submission\version_history.html
{% extends 'users/base.html' %}
{% load submission_tags %}
{% block content %}
<div class="container mt-4">
    <div class="card">
        <div class="card-header">
            <h2>Version History</h2>
            <h4 class="text-muted">{{ submission.title }}</h4>
        </div>
        <div class="card-body">
            {% if pending_forms %}
                <div class="alert alert-warning">
                    <h5><i class="fas fa-exclamation-circle"></i> Required Forms</h5>
                    <p>You have pending forms to complete for this submission:</p>
                    <div class="mt-3">
                        {% for form in pending_forms %}
                            <a href="{% url 'submission:investigator_form' submission.temporary_id form.id %}" 
                               class="btn btn-primary mb-2 me-2">
                                <i class="fas fa-file-signature"></i> Fill {{ form.name }}
                            </a>
                        {% endfor %}
                    </div>
                </div>
            {% endif %}

            <!-- Version History Table -->
            <div class="table-responsive">
                <table class="table table-striped">
                    <thead>
                        <tr>
                            <th>Version</th>
                            <th>Status</th>
                            <th>Date</th>
                            <th>Submitted By</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for history in histories %}
                        <tr>
                            <td>{{ history.version }}</td>
                            <td>
                                <span class="badge badge-{{ history.status|lower }}">
                                    {{ history.get_status_display }}
                                </span>
                            </td>
                            <td>{{ history.date|date:"M d, Y H:i" }}</td>
                            <td>
                                {% if submission.submitted_by and history.version == submission.version %}
                                    {{ submission.submitted_by.get_full_name }}
                                {% endif %}
                            </td>
                            <td>
                                <div class="btn-group" role="group">
                                    <a href="{% url 'submission:download_submission_pdf_version' submission.temporary_id history.version %}" 
                                       class="btn btn-sm btn-secondary" 
                                       title="Download PDF">
                                        <i class="fas fa-file-pdf"></i> Download
                                    </a>
                                    
                                    {% if history.version > 1 %}
                                        <a href="{% url 'submission:compare_version' submission.temporary_id history.version history.version|add:"-1" %}" 
                                           class="btn btn-sm btn-info" 
                                           title="Compare with Previous Version">
                                            <i class="fas fa-code-compare"></i> Compare with v{{ history.version|add:"-1" }}
                                        </a>
                                    {% endif %}
                                    
                                    <!-- {% if history.version != submission.version %}
                                        <a href="{% url 'submission:compare_version' submission.temporary_id history.version submission.version %}" 
                                           class="btn btn-sm btn-primary" 
                                           title="Compare with Latest Version">
                                            <i class="fas fa-code-compare"></i> Compare with Latest
                                        </a>
                                    {% endif %} -->
                                </div>
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
            
            <!-- Required Investigator Forms -->
            {% if submission.get_required_investigator_forms %}
            <div class="card mt-4">
                <div class="card-header">
                    <h4 class="mb-0">Required Forms Status</h4>
                </div>
                <div class="card-body">
                    {% with form_status=submission.get_investigator_form_status %}
                    {% if form_status %}
                        {% for form_name, status in form_status.items %}
                        <h5 class="mb-3">{{ form_name }}</h5>
                        <div class="table-responsive">
                            <table class="table table-bordered table-hover">
                                <thead class="table-light">
                                    <tr>
                                        <th>Investigator</th>
                                        <th>Role</th>
                                        <th>Department</th>
                                        <th>Status</th>
                                        <th>Submission Date</th>
                                        <th>Actions</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {% for inv in status.investigators %}
                                    <tr>
                                        <td>
                                            {{ inv.user.get_full_name }}
                                            {% if inv.is_pi %}
                                            <span class="badge bg-info ms-1">PI</span>
                                            {% endif %}
                                        </td>
                                        <td>{{ inv.role }}</td>
                                        <td>{{ inv.user.userprofile.department|default:"Not specified" }}</td>
                                        <td>
                                            {% if inv.submitted %}
                                                <span class="badge bg-success">
                                                    <i class="fas fa-check"></i> Submitted
                                                </span>
                                            {% else %}
                                                <span class="badge bg-warning">
                                                    <i class="fas fa-clock"></i> Pending
                                                </span>
                                            {% endif %}
                                        </td>
                                        <td>
                                            {% if inv.submitted %}
                                                {{ inv.submitted|date:"M d, Y H:i" }}
                                            {% else %}
                                                -
                                            {% endif %}
                                            </td>
 <!-- In version_history.html -->
                                        <td>
                                            {% if inv.submitted %}
                                                <a href="{% url 'submission:investigator_form' submission.temporary_id status.form.id %}?view=true" 
                                                class="btn btn-sm btn-secondary">
                                                    <i class="fas fa-file"></i> View Form
                                                </a>
                                            {% elif user == inv.user and not submission.is_locked %}
                                                <a href="{% url 'submission:investigator_form' submission.temporary_id status.form.id %}" 
                                                class="btn btn-sm btn-warning">
                                                    <i class="fas fa-edit"></i> Submit Required Form
                                                </a>
                                            {% else %}
                                                -
                                            {% endif %}
                                        </td>
                                    </tr>
                                    {% endfor %}
                                </tbody>
                            </table>
                        </div>
                        {% endfor %}
                        
                        <div class="alert {% if submission.are_all_investigator_forms_complete %}alert-success{% else %}alert-warning{% endif %} mt-3">
                            {% if submission.are_all_investigator_forms_complete %}
                                <i class="fas fa-check-circle"></i> All required forms have been submitted.
                            {% else %}
                                <i class="fas fa-exclamation-circle"></i> Some team members still need to submit their forms.
                            {% endif %}
                        </div>
                    {% else %}
                        <div class="alert alert-info">
                            <i class="fas fa-info-circle"></i> No form submissions required for this version.
                        </div>
                    {% endif %}
                    {% endwith %}
                </div>
                {% endif %}
    
                <!-- Study Actions History Section -->
                <div class="card mb-4">
                    <div class="card-header">
                        <h4 class="mb-0">Actions History</h4>
                    </div>
                    <div class="card-body">
                        <div class="table-responsive">
                            <table class="table table-striped">
                                <thead>
                                    <tr>
                                        <th>Date</th>
                                        <th>Action</th>
                                        <th>Performed By</th>
                                        <th>Status</th>
                                        <th>Documents</th>
                                        <th>Actions</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {% for action in submission.study_actions.all %}
                                    <tr>
                                        <td>{{ action.date_created|date:"M d, Y H:i" }}</td>
                                        <td>
                                            <span class="badge {% if action.action_type == 'withdrawal' %}bg-danger
                                                             {% elif action.action_type == 'closure' %}bg-secondary
                                                             {% elif action.action_type == 'progress' %}bg-info
                                                             {% elif action.action_type == 'amendment' %}bg-warning
                                                             {% else %}bg-primary{% endif %}">
                                                {{ action.get_action_type_display }}
                                            </span>
                                        </td>
                                        <td>{{ action.performed_by.get_full_name }}</td>
                                        <td>
                                            <span class="badge {% if action.status == 'completed' %}bg-success
                                                             {% elif action.status == 'pending' %}bg-warning
                                                             {% else %}bg-secondary{% endif %}">
                                                {{ action.get_status_display }}
                                            </span>
                                        </td>
                                        <td>
                                            {% if action.documents.exists %}
                                                <div class="btn-group">
                                                    <button type="button" class="btn btn-sm btn-secondary dropdown-toggle" data-bs-toggle="dropdown">
                                                        <i class="fas fa-file"></i> Documents
                                                    </button>
                                                    <ul class="dropdown-menu">
                                                        {% for doc in action.documents.all %}
                                                        <li>
                                                            <a class="dropdown-item" href="{{ doc.file.url }}" target="_blank">
                                                                <i class="fas fa-download"></i> {{ doc.description|default:doc.filename }}
                                                            </a>
                                                        </li>
                                                        {% endfor %}
                                                    </ul>
                                                </div>
                                            {% else %}
                                                <span class="text-muted">No documents</span>
                                            {% endif %}
                                        </td>
                                        <td>
                                            <div class="btn-group" role="group">
                                                <a href="{% url 'submission:download_action_pdf' submission.temporary_id action.id %}" 
                                                   class="btn btn-sm btn-secondary" 
                                                   title="Download PDF">
                                                    <i class="fas fa-file-pdf"></i> Download
                                                </a>
                                                
                                                {% if action.action_type == 'amendment' %}
                                                <a href="{% url 'submission:compare_versions' submission.temporary_id action.version submission.version %}" 
                                                   class="btn btn-sm btn-primary" 
                                                   title="Compare with Previous Version">
                                                    <i class="fas fa-code-compare"></i> Compare Changes
                                                </a>
                                                {% endif %}
                                            </div>
                                        </td>
                                    </tr>
                                    {% empty %}
                                    <tr>
                                        <td colspan="6" class="text-center">
                                            <div class="alert alert-info mb-0">
                                                <i class="fas fa-info-circle"></i> No actions have been performed yet.
                                            </div>
                                        </td>
                                    </tr>
                                    {% endfor %}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
                
                <!-- Navigation -->
                <div class="mt-4">
                    <a href="{% url 'submission:dashboard' %}" class="btn btn-secondary">
                        <i class="fas fa-arrow-left"></i> Back to Dashboard
                    </a>
                </div>
            </div>
        </div>
    </div>
    
    {% block page_specific_js %}
    <script>
    $(document).ready(function() {
        // Initialize tooltips
        var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
        var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl)
        });
    
        // Auto-refresh status every 5 minutes if there are pending forms
        {% if not submission.are_all_investigator_forms_complete %}
        setInterval(function() {
            $.ajax({
                url: '{% url "submission:check_form_status" submission.temporary_id %}',
                method: 'GET',
                success: function(response) {
                    if (response.all_complete) {
                        location.reload();
                    }
                }
            });
        }, 300000); // 5 minutes
        {% endif %}
    });
    </script>
    {% endblock %}
    
    {% block extra_css %}
    <style>
        .btn-group {
            gap: 0.5rem;
        }
        
        .badge {
            padding: 0.5em 0.8em;
            font-size: 0.9em;
        }
    
        .table td {
            vertical-align: middle;
        }
    
        .btn-sm {
            padding: 0.25rem 0.5rem;
        }
    
        .alert-warning {
            border-left: 4px solid #ffc107;
        }
    
        .alert-success {
            border-left: 4px solid #28a745;
        }
    
        .alert-info {
            border-left: 4px solid #17a2b8;
        }
    
        .badge.badge-document_missing {
            background-color: #ffc107;
            color: #000;
        }
    
        .badge.badge-submitted {
            background-color: #28a745;
            color: #fff;
        }
    </style>
    {% endblock %}
    
    {% endblock %}

# Contents from: .\templates\submission\{# templates\submission\view_submission.html
{# templates/submission/view_submission.html #}
{% extends 'users/base.html' %}
{% load static %}

{% block title %}View Submission{% endblock %}

{% block content %}
<div class="container mt-4">
    <div class="card">
        <div class="card-header">
            <h2>{{ submission.title }}</h2>
            <h6 class="text-muted">ID: {{ submission.temporary_id }}</h6>
        </div>
        <div class="card-body">
            <div class="row">
                <div class="col-md-6">
                    <p><strong>KHCC #:</strong> {{ submission.khcc_number|default:"N/A" }}</p>
                    <p><strong>Status:</strong> {{ submission.get_status_display }}</p>
                    <p><strong>Version:</strong> {{ submission.version }}</p>
                    <p><strong>Primary Investigator:</strong> {{ submission.primary_investigator.get_full_name }}</p>
                </div>
                <div class="col-md-6">
                    <p><strong>Date Created:</strong> {{ submission.date_created|date:"M d, Y H:i" }}</p>
                    <p><strong>Last Modified:</strong> {{ submission.last_modified|date:"M d, Y H:i" }}</p>
                    {% if submission.is_archived %}
                    <p><strong>Archived Date:</strong> {{ submission.archived_at|date:"M d, Y H:i" }}</p>
                    {% endif %}
                </div>
            </div>

            {% if versions %}
            <div class="mt-4">
                <h4>Version History</h4>
                <table class="table table-striped">
                    <thead>
                        <tr>
                            <th>Version</th>
                            <th>Status</th>
                            <th>Date</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for version in versions %}
                        <tr>
                            <td>{{ version.version }}</td>
                            <td>{{ version.get_status_display }}</td>
                            <td>{{ version.date|date:"M d, Y H:i" }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
            {% endif %}
            
            <div class="mt-4">
                {% if submission.is_archived %}
                <a href="{% url 'submission:archived_dashboard' %}" class="btn btn-secondary">
                    <i class="fas fa-arrow-left"></i> Back to Archived
                </a>
                <button class="btn btn-info unarchive-submission" 
                        data-submission-id="{{ submission.temporary_id }}">
                    <i class="fas fa-box-open"></i> Unarchive Submission
                </button>
                {% else %}
                <a href="{% url 'submission:dashboard' %}" class="btn btn-secondary">
                    <i class="fas fa-arrow-left"></i> Back to Dashboard
                </a>
                {% endif %}
                <a href="{% url 'submission:download_submission_pdf' submission.temporary_id %}" 
                   class="btn btn-primary">
                    <i class="fas fa-file-pdf"></i> Download PDF
                </a>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block page_specific_js %}
{{ block.super }}
<script>
$(document).ready(function() {
    $('.unarchive-submission').click(function() {
        const submissionId = $(this).data('submission-id');
        if (confirm('Are you sure you want to unarchive this submission?')) {
            $.ajax({
                url: `/submission/unarchive/${submissionId}/`,
                type: 'POST',
                headers: {
                    'X-CSRFToken': '{{ csrf_token }}'
                },
                success: function(response) {
                    if (response.status === 'success') {
                        window.location.href = "{% url 'submission:dashboard' %}";
                    }
                },
                error: function(xhr, status, error) {
                    console.error('Error unarchiving submission:', error);
                    alert('Failed to unarchive submission. Please try again.');
                }
            });
        }
    });
});
</script>
{% endblock %}

# Contents from: .\__init__.py


# Contents from: .\admin.py
# submission/admin.py

from django.contrib import admin
from .models import (
    Submission,
    CoInvestigator,
    ResearchAssistant,
    FormDataEntry,
    Document,
    VersionHistory,
    StatusChoice,
    SystemSettings,
)
from .models import PermissionChangeLog



@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('temporary_id', 'title', 'primary_investigator', 'khcc_number', 'status', 'date_created', 'is_locked')
    search_fields = ('title', 'primary_investigator__username', 'khcc_number')
    list_filter = ('status', 'study_type', 'is_locked')
    ordering = ('-date_created',)
    fields = ('title', 'study_type', 'primary_investigator', 'khcc_number', 'status', 'date_created', 'last_modified', 'is_locked')
    readonly_fields = ('date_created', 'last_modified')

@admin.register(CoInvestigator)
class CoInvestigatorAdmin(admin.ModelAdmin):
    list_display = ['user', 'submission', 'get_roles', 'can_edit', 'can_submit', 'can_view_communications']
    list_filter = ['can_edit', 'can_submit', 'can_view_communications']
    search_fields = ['user__first_name', 'user__last_name', 'user__email']
    
    def get_roles(self, obj):
        return ", ".join([role.name for role in obj.roles.all()])
    get_roles.short_description = 'Roles'

@admin.register(ResearchAssistant)
class ResearchAssistantAdmin(admin.ModelAdmin):
    list_display = ('user', 'submission', 'can_submit', 'can_edit')
    list_filter = ('can_submit', 'can_edit', 'can_view_communications')
    search_fields = ('user__username', 'submission__title')

@admin.register(FormDataEntry)
class FormDataEntryAdmin(admin.ModelAdmin):
    list_display = ('submission', 'form', 'field_name', 'date_saved', 'version')
    list_filter = ('form', 'version')
    search_fields = ('submission__title', 'field_name', 'value')
    readonly_fields = ('date_saved',)

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('submission', 'filename', 'uploaded_by', 'uploaded_at')
    search_fields = ('submission__title', 'file', 'uploaded_by__username')
    list_filter = ('uploaded_at',)

@admin.register(VersionHistory)
class VersionHistoryAdmin(admin.ModelAdmin):
    list_display = ('submission', 'version', 'status', 'date')
    search_fields = ('submission__title',)
    list_filter = ('status', 'date')

@admin.register(SystemSettings)
class SystemSettingsAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return not SystemSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(StatusChoice)
class StatusChoiceAdmin(admin.ModelAdmin):
    list_display = ('code', 'label', 'is_active', 'order')
    list_editable = ('is_active', 'order')
    search_fields = ('code', 'label')
    ordering = ('order',)




@admin.register(PermissionChangeLog)
class PermissionChangeLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'permission_type', 'new_value', 'changed_by', 'change_date')
    list_filter = ('role', 'permission_type', 'change_date')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 
                    'changed_by__username', 'changed_by__first_name', 'changed_by__last_name')
    date_hierarchy = 'change_date'

# Contents from: .\apps.py
from django.apps import AppConfig


class SubmissionConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "submission"


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
# submission/forms.py

from django import forms
from django.contrib.auth.models import User
from .models import Submission, Document
from dal import autocomplete
from django.db.models import Q
from django import forms
from django.contrib.auth.models import User
from .models import ResearchAssistant, Submission  # Import all needed models

from django import forms
from django.contrib.auth.models import User
from users.models import Role
from .models import ResearchAssistant, CoInvestigator, Submission
# class MessageForm(forms.ModelForm):
#     recipients = forms.ModelMultipleChoiceField(
#         queryset=User.objects.all(),
#         required=True,
#         widget=forms.SelectMultiple(attrs={'class': 'select2'})
#     )
class SubmissionForm(forms.ModelForm):
    is_primary_investigator = forms.BooleanField(
        required=False,
        initial=False,
        label='Are you the primary investigator?'
    )
    primary_investigator = forms.ModelChoiceField(
        queryset=User.objects.all(),
        required=False,
        widget=forms.Select(attrs={
            'class': 'select2',
            'data-placeholder': 'Search for investigators...'
        })
    )

    class Meta:
        model = Submission
        fields = ['title', 'study_type']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'study_type': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            # Set initial value for primary_investigator if user is set
            self.fields['primary_investigator'].initial = user.id
            # Keep empty queryset initially - will be populated via AJAX
            self.fields['primary_investigator'].queryset = User.objects.none()
            
        # Filter out study types that start with IRB/irb or are Evaluation/Actions
        study_type_field = self.fields['study_type']
        study_type_field.queryset = study_type_field.queryset.exclude(
            Q(name__istartswith='irb') |
            Q(name__iexact='evaluation') |
            Q(name__iexact='actions')
        )



class ResearchAssistantForm(forms.ModelForm):
    assistant = forms.ModelChoiceField(
        queryset=User.objects.all(),
        required=True,
        label="Research Assistant",
        widget=forms.Select(attrs={
            'class': 'select2',
            'data-placeholder': 'Search for research assistant...'
        })
    )
    can_edit = forms.BooleanField(
        required=False, 
        label="Can Edit",
        initial=False
    )
    can_submit = forms.BooleanField(
        required=False, 
        label="Can Submit",
        initial=False
    )
    can_view_communications = forms.BooleanField(
        required=False, 
        label="Can View Communications",
        initial=False
    )

    class Meta:
        model = ResearchAssistant
        fields = ['assistant', 'can_edit', 'can_submit', 'can_view_communications']

    def __init__(self, *args, **kwargs):
        self.submission = kwargs.pop('submission', None)
        super().__init__(*args, **kwargs)

    def clean_assistant(self):
        assistant = self.cleaned_data.get('assistant')
        
        if not assistant:
            raise forms.ValidationError("Please select a research assistant.")

        if self.submission:
            # Check if user is primary investigator
            if self.submission.primary_investigator == assistant:
                raise forms.ValidationError(
                    "This user is already the primary investigator of this submission."
                )

            # Check if user is a co-investigator
            if CoInvestigator.objects.filter(submission=self.submission, user=assistant).exists():
                raise forms.ValidationError(
                    "This user is already a co-investigator of this submission."
                )

            # Check if user is already a research assistant
            if ResearchAssistant.objects.filter(submission=self.submission, user=assistant).exists():
                raise forms.ValidationError(
                    "This user is already a research assistant of this submission."
                )

        return assistant

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.user = self.cleaned_data['assistant']
        if self.submission:
            instance.submission = self.submission
        if commit:
            instance.save()
        return instance


from iRN.constants import COINVESTIGATOR_ROLES

class CoInvestigatorForm(forms.ModelForm):
    investigator = forms.ModelChoiceField(
        queryset=User.objects.all(),
        required=True,
        label="Co-Investigator",
        widget=forms.Select(attrs={
            'class': 'select2',
            'data-placeholder': 'Search for co-investigator...'
        })
    )
    roles = forms.MultipleChoiceField(
        choices=COINVESTIGATOR_ROLES,
        required=True,
        label="Roles",
        widget=forms.CheckboxSelectMultiple,
        help_text="Select all applicable roles"
    )
    can_edit = forms.BooleanField(
        required=False, 
        label="Can Edit",
        initial=False
    )
    can_submit = forms.BooleanField(
        required=False, 
        label="Can Submit",
        initial=False
    )
    can_view_communications = forms.BooleanField(
        required=False, 
        label="Can View Communications",
        initial=False
    )

    class Meta:
        model = CoInvestigator
        fields = ['investigator', 'roles', 'can_edit', 'can_submit', 'can_view_communications']

    def __init__(self, *args, **kwargs):
        self.submission = kwargs.pop('submission', None)
        super().__init__(*args, **kwargs)

    def clean_investigator(self):
        investigator = self.cleaned_data.get('investigator')
        
        if not investigator:
            raise forms.ValidationError("Please select a co-investigator.")

        if self.submission:
            if self.submission.primary_investigator == investigator:
                raise forms.ValidationError(
                    "This user is already the primary investigator of this submission."
                )

            if self.submission.research_assistants.filter(user=investigator).exists():
                raise forms.ValidationError(
                    "This user is already a research assistant of this submission."
                )

            if self.submission.coinvestigators.filter(user=investigator).exists():
                raise forms.ValidationError(
                    "This user is already a co-investigator of this submission."
                )

        return investigator

    def clean_roles(self):
        roles = self.cleaned_data.get('roles')
        if not roles:
            raise forms.ValidationError("Please select at least one role.")
        return roles

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.user = self.cleaned_data['investigator']
        if self.submission:
            instance.submission = self.submission
        if commit:
            instance.save()
            # Save roles as a list in the JSONField
            instance.roles = list(self.cleaned_data['roles'])
            instance.save()
        return instance

def generate_django_form(dynamic_form):
    from django import forms

    # Create a form class dynamically
    class DynamicModelForm(forms.Form):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            # Add any custom initialization here if needed

    # Create the form fields dictionary
    fields = {}
    for field in dynamic_form.fields.all():
        label = f"{field.displayed_name}{'*' if field.required else ''}"
        field_attrs = {
            'required': field.required,
            'label': label,
            'help_text': field.help_text,
            'initial': field.default_value,
        }
        widget_attrs = {'class': 'form-control'}

        if field.field_type == 'text':
            fields[field.name] = forms.CharField(
                max_length=field.max_length or 255,
                widget=forms.TextInput(attrs=widget_attrs),
                **field_attrs
            )
        elif field.field_type == 'email':
            fields[field.name] = forms.EmailField(
                max_length=field.max_length or 255,
                widget=forms.EmailInput(attrs=widget_attrs),
                **field_attrs
            )
        elif field.field_type == 'tel':
            fields[field.name] = forms.CharField(
                max_length=field.max_length or 15,
                widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'tel'}),
                **field_attrs
            )
        elif field.field_type == 'textarea':
            fields[field.name] = forms.CharField(
                max_length=field.max_length or 500,
                widget=forms.Textarea(attrs=widget_attrs),
                **field_attrs
            )
        elif field.field_type == 'checkbox':
            choices = [(choice.strip(), choice.strip())
                       for choice in field.choices.split(',') if choice.strip()]
            fields[field.name] = forms.MultipleChoiceField(
                choices=choices,
                widget=forms.CheckboxSelectMultiple(attrs={
                    'class': 'form-check-input'
                }),
                required=field.required
            )
        elif field.field_type == 'radio':
            choices = [(choice.strip(), choice.strip())
                       for choice in field.choices.split(',') if choice.strip()]
            fields[field.name] = forms.ChoiceField(
                choices=choices,
                widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
                **field_attrs
            )
        elif field.field_type == 'select':
            choices = [(choice.strip(), choice.strip())
                       for choice in field.choices.split(',') if choice.strip()]
            fields[field.name] = forms.ChoiceField(
                choices=[('', '-- Select --')] + choices,
                widget=forms.Select(attrs=widget_attrs),
                **field_attrs
            )
        elif field.field_type == 'number':
            fields[field.name] = forms.IntegerField(
                widget=forms.NumberInput(attrs=widget_attrs),
                **field_attrs
            )
        elif field.field_type == 'date':
            fields[field.name] = forms.DateField(
                widget=forms.DateInput(attrs={'type': 'date', **widget_attrs}),
                **field_attrs
            )
        # Add other field types as necessary

    # Add the fields to the form class
    DynamicModelForm.base_fields = fields

    return DynamicModelForm

class DocumentForm(forms.ModelForm):
    description = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Document
        fields = ['file', 'description']

# Contents from: .\gpt_analysis.py
# gpt_analysis.py

from openai import OpenAI
from django.conf import settings
from django.core.cache import cache
import json
from io import StringIO
import logging
import markdown2
from django.utils.safestring import mark_safe

logger = logging.getLogger(__name__)

class ResearchAnalyzer:
    def __init__(self, submission, version):
        """Initialize the analyzer with basic settings"""
        if version is None:
            raise ValueError("Version must be specified")
            
        self.submission = submission
        self.version = version
        self.client = OpenAI()

    def get_analysis_prompt(self):
        """Generate the analysis prompt from submission data"""
        # Get form data for the current version
        form_entries = self.submission.form_data_entries.filter(version=self.version)
        
        # Build prompt from form data
        prompt = (
            """
            Please analyze the following research submission and provide detailed suggestions to enhance the project, focusing on methodology, inclusion and exclusion criteria, objectives, endpoints, statistical analysis, and any other relevant issues.

            Format your response in markdown with the following structure:

            Use # for the main title
            Use ## for section headers
            Use bold for emphasis
            Use - for bullet points
            Include sections for:
            Study Type
                Principal Investigator
                Objectives
                Methods
                Inclusion Criteria
                Exclusion Criteria
                Endpoints
                Statistical Analysis
                Other Relevant Issues
                Provide specific recommendations for improvement in each section
                End with a Summary section highlighting key suggestions and overall recommendations
                Study Information:
                """
        )
        prompt += f"Study Type: {self.submission.study_type.name}\n\n"
        
        # Group entries by form
        for form in self.submission.study_type.forms.all():
            form_data = form_entries.filter(form=form)
            if form_data:
                prompt += f"{form.name}:\n"
                for entry in form_data:
                    prompt += f"- {entry.field_name}: {entry.value}\n"
                prompt += "\n"
                
        return prompt

    def analyze_submission(self):
        """Send to GPT and get analysis"""
        cache_key = f'gpt_analysis_{self.submission.temporary_id}_{self.version}'
        cached_response = cache.get(cache_key)
        
        if cached_response:
            # Convert markdown to HTML
            html_content = markdown2.markdown(cached_response, extras=['fenced-code-blocks'])
            return mark_safe(html_content)
            
        try:
            prompt = self.get_analysis_prompt()
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system", 
                        "content": (
                            "You are KHCC Brain, an AI research advisor specializing in medical research analysis. "
                            "Provide your analysis in clear, structured markdown format. "
                            "Use proper markdown syntax and ensure the output is well-organized and professional."
                        )
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            analysis = response.choices[0].message.content
            
            # Cache the raw markdown response
            cache.set(cache_key, analysis, 3600)
            
            # Convert markdown to HTML
            html_content = markdown2.markdown(analysis, extras=['fenced-code-blocks'])
            return mark_safe(html_content)
            
        except Exception as e:
            logger.error(f"Error in GPT analysis: {str(e)}")
            return "Error in generating analysis. Please try again later."

# Contents from: .\management\commands\cleanup_version_history.py
 

# Contents from: .\middleware.py
# submission/middleware.py
import logging
from django.utils import timezone

logger = logging.getLogger(__name__)

class SubmissionAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Log submission access
        if request.path.startswith('/submission/') and request.user.is_authenticated:
            try:
                submission_id = request.resolver_match.kwargs.get('submission_id')
                if submission_id:
                    logger.info(
                        f"User {request.user.username} accessed submission {submission_id} "
                        f"at {timezone.now()}"
                    )
            except Exception as e:
                logger.error(f"Error in SubmissionAccessMiddleware: {str(e)}")
                
        return response

# Contents from: .\migrations\0001_initial.py
# Generated by Django 5.1.2 on 2024-11-04 01:29

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        (
            "forms_builder",
            "0002_alter_dynamicform_options_alter_formfield_options_and_more",
        ),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
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
            ],
            options={
                "verbose_name": "System Settings",
                "verbose_name_plural": "System Settings",
            },
        ),
        migrations.CreateModel(
            name="Submission",
            fields=[
                ("temporary_id", models.AutoField(primary_key=True, serialize=False)),
                ("irb_number", models.CharField(blank=True, max_length=20, null=True)),
                ("title", models.CharField(max_length=255)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("draft", "Draft"),
                            ("submitted", "Submitted"),
                            ("revision_requested", "Revision Requested"),
                            ("under_revision", "Under Revision"),
                            ("accepted", "Accepted"),
                            ("suspended", "Suspended"),
                            ("finished", "Finished"),
                            ("terminated", "Terminated"),
                        ],
                        default="draft",
                        max_length=20,
                    ),
                ),
                ("date_created", models.DateTimeField(auto_now_add=True)),
                ("last_modified", models.DateTimeField(auto_now=True)),
                ("date_submitted", models.DateTimeField(blank=True, null=True)),
                ("version", models.PositiveIntegerField(default=1)),
                ("is_locked", models.BooleanField(default=False)),
                (
                    "primary_investigator",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="primary_investigations",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "study_type",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="forms_builder.studytype",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ResearchAssistant",
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
                ("can_submit", models.BooleanField(default=False)),
                ("can_edit", models.BooleanField(default=False)),
                ("can_view_communications", models.BooleanField(default=False)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "submission",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="research_assistants",
                        to="submission.submission",
                    ),
                ),
            ],
        ),
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
                ("file", models.FileField(upload_to="documents/")),
                ("description", models.CharField(blank=True, max_length=255)),
                ("uploaded_at", models.DateTimeField(auto_now_add=True)),
                (
                    "uploaded_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "submission",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="documents",
                        to="submission.submission",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="CoInvestigator",
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
                ("role_in_study", models.CharField(max_length=255)),
                ("can_submit", models.BooleanField(default=False)),
                ("can_edit", models.BooleanField(default=False)),
                ("can_view_communications", models.BooleanField(default=False)),
                ("order", models.PositiveIntegerField(default=0)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "submission",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="coinvestigators",
                        to="submission.submission",
                    ),
                ),
            ],
            options={
                "ordering": ["order"],
            },
        ),
        migrations.CreateModel(
            name="VersionHistory",
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
                ("version", models.PositiveIntegerField()),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("draft", "Draft"),
                            ("submitted", "Submitted"),
                            ("revision_requested", "Revision Requested"),
                            ("under_revision", "Under Revision"),
                            ("accepted", "Accepted"),
                            ("suspended", "Suspended"),
                            ("finished", "Finished"),
                            ("terminated", "Terminated"),
                        ],
                        max_length=20,
                    ),
                ),
                ("date", models.DateTimeField()),
                (
                    "submission",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="version_histories",
                        to="submission.submission",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="FormDataEntry",
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
                ("field_name", models.CharField(max_length=255)),
                ("value", models.TextField()),
                ("date_saved", models.DateTimeField(auto_now=True)),
                ("version", models.PositiveIntegerField(default=1)),
                (
                    "form",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="forms_builder.dynamicform",
                    ),
                ),
                (
                    "submission",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="form_data_entries",
                        to="submission.submission",
                    ),
                ),
            ],
            options={
                "indexes": [
                    models.Index(
                        fields=["submission", "form", "field_name"],
                        name="submission__submiss_3f0af5_idx",
                    )
                ],
            },
        ),
    ]


# Contents from: .\migrations\0002_researchassistant_date_added_and_more.py
# Generated by Django 5.1.2 on 2024-11-04 22:34

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("submission", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="researchassistant",
            name="date_added",
            field=models.DateTimeField(
                auto_now_add=True, default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="researchassistant",
            name="submission",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="submission.submission"
            ),
        ),
        migrations.AlterUniqueTogether(
            name="researchassistant",
            unique_together={("submission", "user")},
        ),
    ]


# Contents from: .\migrations\0003_alter_coinvestigator_order_and_more.py
# Generated by Django 5.1.2 on 2024-11-04 22:40

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("submission", "0002_researchassistant_date_added_and_more"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name="coinvestigator",
            name="order",
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name="coinvestigator",
            name="submission",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="submission.submission"
            ),
        ),
        migrations.AlterUniqueTogether(
            name="coinvestigator",
            unique_together={("submission", "user")},
        ),
    ]


# Contents from: .\migrations\0004_remove_coinvestigator_role_in_study_and_more.py
# Generated by Django 5.1.2 on 2024-11-05 19:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("submission", "0003_alter_coinvestigator_order_and_more"),
        ("users", "0005_alter_userprofile_full_name"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="coinvestigator",
            name="role_in_study",
        ),
        migrations.AddField(
            model_name="coinvestigator",
            name="roles",
            field=models.ManyToManyField(
                related_name="coinvestigators", to="users.role"
            ),
        ),
    ]


# Contents from: .\migrations\0005_statuschoice_alter_submission_status_and_more.py
# Generated by Django 5.1.2 on 2024-11-05 20:45

from django.db import migrations, models

# Define the choices directly in the migration
SUBMISSION_STATUS_CHOICES = [
    ('draft', 'Draft'),
    ('submitted', 'Submitted'),
    ('under_review', 'Under Review'),
    ('rejected', 'Rejected'),
    ('accepted', 'Accepted'),
    ('revision_requested', 'Revision Requested'),
    ('closed', 'Closed'),
]

class Migration(migrations.Migration):

    dependencies = [
        ("submission", "0004_remove_coinvestigator_role_in_study_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="StatusChoice",
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
                ("code", models.CharField(max_length=50, unique=True)),
                ("label", models.CharField(max_length=100)),
                ("is_active", models.BooleanField(default=True)),
                ("order", models.PositiveIntegerField(default=0)),
            ],
            options={
                "verbose_name": "Status Choice",
                "verbose_name_plural": "Status Choices",
                "ordering": ["order"],
            },
        ),
        migrations.AlterField(
            model_name="submission",
            name="status",
            field=models.CharField(
                choices=SUBMISSION_STATUS_CHOICES,
                max_length=50
            ),
        ),
        migrations.AlterField(
            model_name="versionhistory",
            name="status",
            field=models.CharField(
                choices=SUBMISSION_STATUS_CHOICES,
                max_length=50
            ),
        ),
    ]


# Contents from: .\migrations\0006_alter_coinvestigator_submission_and_more.py
# Generated by Django 5.1.2 on 2024-11-08 12:00

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("submission", "0005_statuschoice_alter_submission_status_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="coinvestigator",
            name="submission",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="coinvestigators",
                to="submission.submission",
            ),
        ),
        migrations.AlterField(
            model_name="researchassistant",
            name="submission",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="research_assistants",
                to="submission.submission",
            ),
        ),
    ]


# Contents from: .\migrations\0007_alter_submission_irb_number.py
# Generated by Django 5.1.2 on 2024-11-08 22:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("submission", "0006_alter_coinvestigator_submission_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="submission",
            name="irb_number",
            field=models.CharField(blank=True, max_length=20, null=True, unique=True),
        ),
    ]


# Contents from: .\migrations\0008_alter_versionhistory_options_and_more.py
# Generated by Django 5.1.2 on 2024-11-09 21:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("submission", "0007_alter_submission_irb_number"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="versionhistory",
            options={"ordering": ["-version"]},
        ),
        migrations.AlterField(
            model_name="versionhistory",
            name="date",
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name="versionhistory",
            name="status",
            field=models.CharField(max_length=20),
        ),
        migrations.AlterField(
            model_name="versionhistory",
            name="version",
            field=models.IntegerField(),
        ),
        migrations.AlterUniqueTogether(
            name="versionhistory",
            unique_together={("submission", "version")},
        ),
    ]


# Contents from: .\migrations\0009_alter_versionhistory_options_and_more.py
# Generated by Django 5.1.2 on 2024-11-09 21:43

import submission.models
from django.db import migrations, models
from iRN.constants import get_submission_status_choices


class Migration(migrations.Migration):

    dependencies = [
        ("submission", "0008_alter_versionhistory_options_and_more"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="versionhistory",
            options={},
        ),
        migrations.AlterUniqueTogether(
            name="versionhistory",
            unique_together=set(),
        ),
        migrations.AlterField(
            model_name="versionhistory",
            name="date",
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name="versionhistory",
            name="status",
            field=models.CharField(
                choices=get_submission_status_choices, max_length=50
            ),
        ),
        migrations.AlterField(
            model_name="versionhistory",
            name="version",
            field=models.PositiveIntegerField(),
        ),
    ]


# Contents from: .\migrations\0010_investigatorformsubmission.py
# Generated by Django 5.1.2 on 2024-11-10 02:17

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("forms_builder", "0003_merge_20241108_1706"),
        ("submission", "0009_alter_versionhistory_options_and_more"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="InvestigatorFormSubmission",
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
                ("date_submitted", models.DateTimeField(auto_now_add=True)),
                ("version", models.PositiveIntegerField()),
                (
                    "form",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="forms_builder.dynamicform",
                    ),
                ),
                (
                    "investigator",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "submission",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="investigator_form_submissions",
                        to="submission.submission",
                    ),
                ),
            ],
            options={
                "ordering": ["date_submitted"],
                "unique_together": {("submission", "form", "investigator", "version")},
            },
        ),
    ]


# Contents from: .\migrations\0011_submission_archived_at_submission_is_archived.py
# Generated by Django 5.1.2 on 2024-11-13 18:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("submission", "0010_investigatorformsubmission"),
    ]

    operations = [
        migrations.AddField(
            model_name="submission",
            name="archived_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="submission",
            name="is_archived",
            field=models.BooleanField(default=False),
        ),
    ]


# Contents from: .\migrations\0012_remove_coinvestigator_roles_coinvestigator_roles.py
# Generated by Django 5.1.2 on 2024-11-13 18:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("submission", "0011_submission_archived_at_submission_is_archived"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="coinvestigator",
            name="roles",
        ),
        migrations.AddField(
            model_name="coinvestigator",
            name="roles",
            field=models.JSONField(default=list),
        ),
    ]


# Contents from: .\migrations\0013_permissionchangelog.py
# Generated by Django 5.1.3 on 2024-11-17 02:21

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("submission", "0012_remove_coinvestigator_roles_coinvestigator_roles"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="PermissionChangeLog",
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
                    "permission_type",
                    models.CharField(
                        choices=[
                            ("edit", "Edit"),
                            ("submit", "Submit"),
                            ("view_communications", "View Communications"),
                        ],
                        max_length=50,
                    ),
                ),
                ("old_value", models.BooleanField()),
                ("new_value", models.BooleanField()),
                ("change_date", models.DateTimeField(auto_now_add=True)),
                (
                    "role",
                    models.CharField(
                        choices=[
                            ("co_investigator", "Co-Investigator"),
                            ("research_assistant", "Research Assistant"),
                        ],
                        max_length=50,
                    ),
                ),
                ("notes", models.TextField(blank=True, null=True)),
                (
                    "changed_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="permission_changes_made",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "submission",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="submission.submission",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="permission_changes_received",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Permission Change Log",
                "verbose_name_plural": "Permission Change Logs",
                "ordering": ["-change_date"],
            },
        ),
    ]


# Contents from: .\migrations\0014_submission_show_in_irb_submission_show_in_rc.py
# Generated by Django 5.1.3 on 2024-11-30 11:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("submission", "0013_permissionchangelog"),
    ]

    operations = [
        migrations.AddField(
            model_name="submission",
            name="show_in_irb",
            field=models.BooleanField(
                default=False, help_text="Toggle visibility for IRB members"
            ),
        ),
        migrations.AddField(
            model_name="submission",
            name="show_in_rc",
            field=models.BooleanField(
                default=False, help_text="Toggle visibility for RC members"
            ),
        ),
    ]


# Contents from: .\migrations\0015_rename_irb_number_submission_khcc_number.py
# Generated by Django 5.1.3 on 2024-11-30 19:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("submission", "0014_submission_show_in_irb_submission_show_in_rc"),
    ]

    operations = [
        migrations.RenameField(
            model_name="submission",
            old_name="irb_number",
            new_name="khcc_number",
        ),
    ]


# Contents from: .\migrations\0016_alter_submission_status.py
# Generated by Django 5.1.3 on 2024-11-30 19:40

import iRN.constants
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("submission", "0015_rename_irb_number_submission_khcc_number"),
    ]

    operations = [
        migrations.AlterField(
            model_name="submission",
            name="status",
            field=models.CharField(
                choices=iRN.constants.get_submission_status_choices,
                default="draft",
                max_length=50,
            ),
        ),
    ]


# Contents from: .\migrations\0017_studyaction_studyactiondocument.py
# Generated by Django 5.1.3 on 2024-12-01 18:13

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("submission", "0016_alter_submission_status"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="StudyAction",
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
                    "action_type",
                    models.CharField(
                        choices=[
                            ("withdrawal", "Study Withdrawal"),
                            ("progress", "Progress Report"),
                            ("amendment", "Study Amendment"),
                            ("closure", "Study Closure"),
                        ],
                        max_length=20,
                    ),
                ),
                ("date_created", models.DateTimeField(auto_now_add=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending"),
                            ("completed", "Completed"),
                            ("cancelled", "Cancelled"),
                        ],
                        default="pending",
                        max_length=20,
                    ),
                ),
                ("notes", models.TextField(blank=True)),
                (
                    "performed_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "submission",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="study_actions",
                        to="submission.submission",
                    ),
                ),
            ],
            options={
                "ordering": ["-date_created"],
            },
        ),
        migrations.CreateModel(
            name="StudyActionDocument",
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
                ("file", models.FileField(upload_to="study_actions/")),
                ("description", models.CharField(blank=True, max_length=255)),
                ("uploaded_at", models.DateTimeField(auto_now_add=True)),
                (
                    "action",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="documents",
                        to="submission.studyaction",
                    ),
                ),
            ],
        ),
    ]


# Contents from: .\migrations\0018_studyaction_version.py
# Generated by Django 5.1.3 on 2024-12-01 18:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("submission", "0017_studyaction_studyactiondocument"),
    ]

    operations = [
        migrations.AddField(
            model_name="studyaction",
            name="version",
            field=models.IntegerField(default=1),
        ),
    ]


# Contents from: .\migrations\0019_submission_submitted_by.py
# Generated by Django 5.1.3 on 2024-12-01 20:03

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("submission", "0018_studyaction_version"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="submission",
            name="submitted_by",
            field=models.ForeignKey(
                blank=True,
                help_text="User who submitted the submission",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="submitted_submissions",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]


# Contents from: .\migrations\0020_versionhistory_submitted_by.py
# Generated by Django 5.1.3 on 2024-12-01 20:08

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("submission", "0019_submission_submitted_by"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="versionhistory",
            name="submitted_by",
            field=models.ForeignKey(
                blank=True,
                help_text="User who submitted this version",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="version_submissions",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]


# Contents from: .\migrations\0021_remove_submission_submitted_by_and_more.py
# Generated by Django 5.1.3 on 2024-12-01 20:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("submission", "0020_versionhistory_submitted_by"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="submission",
            name="submitted_by",
        ),
        migrations.RemoveField(
            model_name="versionhistory",
            name="submitted_by",
        ),
    ]


# Contents from: .\migrations\0022_submission_submitted_by.py
# Generated by Django 5.1.3 on 2024-12-01 21:02

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("submission", "0021_remove_submission_submitted_by_and_more"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="submission",
            name="submitted_by",
            field=models.ForeignKey(
                blank=True,
                help_text="User who submitted the submission",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="submitted_submissions",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]


# Contents from: .\migrations\0023_versionhistory_submitted_by.py
# Generated by Django 5.1.3 on 2024-12-01 21:06

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("submission", "0022_submission_submitted_by"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="versionhistory",
            name="submitted_by",
            field=models.ForeignKey(
                blank=True,
                help_text="User who submitted this version",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="version_submissions",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]


# Contents from: .\migrations\0024_submission_forms_complete.py
# Generated by Django 5.1.3 on 2024-12-04 15:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("submission", "0023_versionhistory_submitted_by"),
    ]

    operations = [
        migrations.AddField(
            model_name="submission",
            name="forms_complete",
            field=models.BooleanField(default=False),
        ),
    ]


# Contents from: .\migrations\0025_remove_submission_forms_complete.py
# Generated by Django 5.1.3 on 2024-12-04 15:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("submission", "0024_submission_forms_complete"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="submission",
            name="forms_complete",
        ),
    ]


# Contents from: .\migrations\0026_formdataentry_study_action.py
# Generated by Django 5.1.3 on 2024-12-04 21:24

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("submission", "0025_remove_submission_forms_complete"),
    ]

    operations = [
        migrations.AddField(
            model_name="formdataentry",
            name="study_action",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="form_data_entries",
                to="submission.studyaction",
            ),
        ),
    ]


# Contents from: .\migrations\0027_alter_submission_options_and_more.py
# Generated by Django 5.1.3 on 2024-12-05 17:33

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("forms_builder", "0003_merge_20241108_1706"),
        ("submission", "0026_formdataentry_study_action"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="submission",
            options={"ordering": ["-date_created"]},
        ),
        migrations.AddIndex(
            model_name="submission",
            index=models.Index(fields=["status"], name="submission__status_832d62_idx"),
        ),
        migrations.AddIndex(
            model_name="submission",
            index=models.Index(
                fields=["khcc_number"], name="submission__khcc_nu_653cf0_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="submission",
            index=models.Index(
                fields=["primary_investigator"], name="submission__primary_7bae28_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="submission",
            index=models.Index(
                fields=["is_archived"], name="submission__is_arch_0823ea_idx"
            ),
        ),
    ]


# Contents from: .\migrations\0028_alter_submission_options_and_more.py
# Generated by Django 5.1.3 on 2024-12-05 17:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("submission", "0027_alter_submission_options_and_more"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="submission",
            options={},
        ),
        migrations.RemoveIndex(
            model_name="submission",
            name="submission__status_832d62_idx",
        ),
        migrations.RemoveIndex(
            model_name="submission",
            name="submission__khcc_nu_653cf0_idx",
        ),
        migrations.RemoveIndex(
            model_name="submission",
            name="submission__primary_7bae28_idx",
        ),
        migrations.RemoveIndex(
            model_name="submission",
            name="submission__is_arch_0823ea_idx",
        ),
    ]


# Contents from: .\migrations\__init__.py


# Contents from: .\models.py
# submission/models.py

from django.db import models
from django.contrib.auth.models import User
from forms_builder.models import StudyType, DynamicForm
from django.utils import timezone
from django.core.cache import cache
from django.db.utils import OperationalError
from django.apps import apps
from iRN.constants import get_submission_status_choices, COINVESTIGATOR_ROLES
import json

class StatusChoice(models.Model):
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
        cache.delete('status_choices')

class Submission(models.Model):
    temporary_id = models.AutoField(primary_key=True)
    khcc_number = models.CharField(max_length=20, blank=True, null=True, unique=True)
    title = models.CharField(max_length=255)
    primary_investigator = models.ForeignKey(
        User, related_name='primary_investigations', on_delete=models.CASCADE
    )
    study_type = models.ForeignKey(StudyType, on_delete=models.SET_NULL, null=True)
    status = models.CharField(
        max_length=50,
        choices=get_submission_status_choices,
        default='draft'
    )
    date_created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    date_submitted = models.DateTimeField(blank=True, null=True)
    version = models.PositiveIntegerField(default=1)
    is_locked = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)
    archived_at = models.DateTimeField(null=True, blank=True)
    show_in_irb = models.BooleanField(default=False, help_text="Toggle visibility for IRB members")
    show_in_rc = models.BooleanField(default=False, help_text="Toggle visibility for RC members")
    # Add new field to track submitter
    submitted_by = models.ForeignKey(
        User,
        related_name='submitted_submissions',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="User who submitted the submission"
    )

    def submit(self, submitted_by):
        self.submitted_by = submitted_by
        self.date_submitted = timezone.now()
        self.is_locked = True
        # Create version history
        VersionHistory.objects.create(
            submission=self,
            version=self.version,
            status=self.status,
            date=timezone.now()
        )
        # Check for required investigator forms
        required_forms = self.study_type.forms.filter(requested_per_investigator=True)
        if required_forms.exists():
            all_investigators = [self.primary_investigator]  # Include PI
            all_investigators.extend([ci.user for ci in self.coinvestigators.all()])
            
            for form in required_forms:
                for investigator in all_investigators:
                    if not InvestigatorFormSubmission.objects.filter(
                        submission=self,
                        form=form,
                        investigator=investigator,
                        version=self.version
                    ).exists():
                        self.status = 'document_missing'
                        self.save()
                        return
        
        # If we reach here, all forms are complete
        if self.status == 'revision_requested':
            self.increment_version()
        self.status = 'submitted'
        self.save()



        
        # Check for required investigator forms
        required_forms = self.study_type.forms.filter(requested_per_investigator=True)
        if required_forms.exists():
            all_investigators = [self.primary_investigator]  # Include PI
            all_investigators.extend([ci.user for ci in self.coinvestigators.all()])
            
            for form in required_forms:
                for investigator in all_investigators:
                    if not InvestigatorFormSubmission.objects.filter(
                        submission=self,
                        form=form,
                        investigator=investigator,
                        version=self.version
                    ).exists():
                        self.status = 'document_missing'
                        self.save()
                        return
        
        self.status = 'submitted'
        self.save()
        


    def __str__(self):
        return f"{self.title} (ID: {self.temporary_id}, Version: {self.version})"

    def archive(self, user=None):
        """Archive the submission"""
        self.is_archived = True
        self.archived_at = timezone.now()
        self.save(update_fields=['is_archived', 'archived_at'])

    def unarchive(self, user=None):
        """Unarchive the submission"""
        self.is_archived = False
        self.archived_at = None
        self.save(update_fields=['is_archived', 'archived_at'])

    def increment_version(self):
        """Increment submission version and create history entry."""
        VersionHistory.objects.create(
            submission=self,
            version=self.version,
            status=self.status,
            date=timezone.now()
        )
        self.version += 1


    def get_required_investigator_forms(self):
        """Get all forms that require per-investigator submission."""
        return self.study_type.forms.filter(requested_per_investigator=True)

    def get_submitters(self):
        """Get all users who have submission rights."""
        submitters = [self.primary_investigator]
        submitters.extend([ci.user for ci in self.coinvestigators.filter(can_submit=True)])
        submitters.extend([ra.user for ra in self.research_assistants.filter(can_submit=True)])
        return submitters

    def get_non_submitters(self):
        """Get all users who don't have submission rights."""
        non_submitters = []
        non_submitters.extend([ci.user for ci in self.coinvestigators.filter(can_submit=False)])
        non_submitters.extend([ra.user for ra in self.research_assistants.filter(can_submit=False)])
        return non_submitters

    def get_research_team(self):
        """Get all research assistants and co-investigators."""
        team = []
        team.extend([ci.user for ci in self.coinvestigators.all()])
        team.extend([ra.user for ra in self.research_assistants.all()])
        return team

    def has_submitted_form(self, user, form):
        """Check if a user has submitted a specific form."""
        # Direct submission check
        if InvestigatorFormSubmission.objects.filter(
            submission=self,
            form=form,
            investigator=user,
            version=self.version
        ).exists():
            return True

        # If user has submit rights and submission is submitted/pending, form is considered submitted
        if self.status in ['submitted', 'document_missing'] and user in self.get_submitters():
            return True

        return False

    def get_pending_investigator_forms(self, user):
        """Get forms that still need to be filled by an investigator."""
        if not (user == self.primary_investigator or 
                self.coinvestigators.filter(user=user).exists() or 
                self.research_assistants.filter(user=user).exists()):
            return []

        # If user has submit rights and submission is submitted/pending, no forms are pending
        if user in self.get_submitters() and self.status in ['submitted', 'document_missing']:
            return []

        required_forms = self.get_required_investigator_forms()
        submitted_forms = InvestigatorFormSubmission.objects.filter(
            submission=self,
            investigator=user,
            version=self.version
        ).values_list('form_id', flat=True)

        return list(required_forms.exclude(id__in=submitted_forms))

    def has_pending_forms(self, user):
        """Check if user has any pending forms for this submission."""
        return len(self.get_pending_investigator_forms(user)) > 0
    def get_investigator_form_status(self):
        """Get completion status of all investigator forms."""
        required_forms = self.get_required_investigator_forms()
        if not required_forms.exists():
            return {}

        # Get all team members
        submitters = self.get_submitters()
        non_submitters = self.get_non_submitters()
        all_investigators = [{'user': user, 'role': self.get_user_role(user)} 
                           for user in submitters + non_submitters]

        status = {}
        for form in required_forms:
            # Get direct form submissions
            form_submissions = InvestigatorFormSubmission.objects.filter(
                submission=self,
                form=form,
                version=self.version
            ).select_related('investigator')
            
            # Create base submission dict
            submitted_users = {sub.investigator_id: sub.date_submitted for sub in form_submissions}
            
            # For users with submit rights, mark as submitted if submission is submitted
            if self.status in ['submitted', 'document_missing'] and self.date_submitted:
                for user in submitters:
                    submitted_users.setdefault(user.id, self.date_submitted)

            status[form.name] = {
                'form': form,
                'investigators': [
                    {
                        'user': inv['user'],
                        'role': inv['role'],
                        'submitted': submitted_users.get(inv['user'].id),
                        'is_pi': inv['user'] == self.primary_investigator
                    }
                    for inv in all_investigators
                ]
            }
        return status

    def are_all_investigator_forms_complete(self):
        """Check if all investigators have completed their required forms."""
        required_forms = self.get_required_investigator_forms()
        if not required_forms.exists():
            return True

        # Get non-submitters - they always need to submit forms
        non_submitters = self.get_non_submitters()
        
        # For new submissions, include submitters in check
        if self.status not in ['submitted', 'document_missing']:
            non_submitters.extend(self.get_submitters())

        # Check each form
        for form in required_forms:
            submitted_users = [
                user.id for user in non_submitters
                if self.has_submitted_form(user, form)
            ]
            if len(submitted_users) < len(non_submitters):
                return False

        return True

    def can_user_edit(self, user):
        """Check if user can edit the submission."""
        if user == self.primary_investigator:
            return True
        return (self.coinvestigators.filter(user=user, can_edit=True).exists() or
                self.research_assistants.filter(user=user, can_edit=True).exists())

    def can_user_submit(self, user):
        """Check if user can submit the submission."""
        return user in self.get_submitters()

    def can_user_view_communications(self, user):
        """Check if user can view submission communications."""
        if user == self.primary_investigator:
            return True
        return (self.coinvestigators.filter(user=user, can_view_communications=True).exists() or
                self.research_assistants.filter(user=user, can_view_communications=True).exists())

    def get_user_role(self, user):
        """Get user's role in the submission."""
        if user == self.primary_investigator:
            return 'Primary Investigator'
        if self.coinvestigators.filter(user=user).exists():
            return 'Co-Investigator'
        if self.research_assistants.filter(user=user).exists():
            return 'Research Assistant'
        return None

    def can_user_view(self, user):
        """Determine if a user can view this submission."""
        if self.can_user_edit(user) or self.can_user_submit(user):
            return True
        if user.groups.filter(name='OSAR').exists():
            return True
        if self.show_in_irb and user.groups.filter(name='IRB').exists():
            return True
        if self.show_in_rc and user.groups.filter(name='RC').exists():
            return True
        return False

    @classmethod
    def get_visible_submissions_for_user(cls, user):
        """Get all submissions visible to a specific user."""
        if user.groups.filter(name='OSAR').exists():
            return cls.objects.all()
        
        return cls.objects.filter(
            models.Q(primary_investigator=user) |
            models.Q(coinvestigators__user=user) |
            models.Q(research_assistants__user=user) |
            models.Q(show_in_irb=True, primary_investigator__groups__name='IRB') |
            models.Q(show_in_rc=True, primary_investigator__groups__name='RC')
        ).distinct()

class CoInvestigator(models.Model):
    submission = models.ForeignKey(
        'Submission', 
        related_name='coinvestigators',
        on_delete=models.CASCADE
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    roles = models.JSONField(default=list)
    can_edit = models.BooleanField(default=False)
    can_submit = models.BooleanField(default=False)
    can_view_communications = models.BooleanField(default=False)
    order = models.IntegerField(default=0)

    class Meta:
        unique_together = ['submission', 'user']
        ordering = ['order']

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.submission.temporary_id}"

    def get_role_display(self):
        """Return human-readable role names"""
        role_dict = dict(COINVESTIGATOR_ROLES)
        return [role_dict.get(role, role) for role in (self.roles or [])]

    def log_permission_changes(self, changed_by, is_new=False):
        """Log changes to permissions."""
        if is_new:
            # Log initial permissions
            for perm in ['can_edit', 'can_submit', 'can_view_communications']:
                if getattr(self, perm):
                    PermissionChangeLog.objects.create(
                        submission=self.submission,
                        user=self.user,
                        changed_by=changed_by,
                        permission_type=perm.replace('can_', ''),
                        old_value=False,
                        new_value=True,
                        role='co_investigator',
                        notes='Initial permission setting'
                    )
            # Log initial roles
            if self.roles:
                role_names = ', '.join(self.get_role_display())
                PermissionChangeLog.objects.create(
                    submission=self.submission,
                    user=self.user,
                    changed_by=changed_by,
                    permission_type='roles',
                    old_value=False,
                    new_value=True,
                    role='co_investigator',
                    notes=f'Initial roles assigned: {role_names}'
                )
        else:
            # Get the previous state
            old_instance = CoInvestigator.objects.get(pk=self.pk)
            
            # Check for permission changes
            for perm in ['can_edit', 'can_submit', 'can_view_communications']:
                old_value = getattr(old_instance, perm)
                new_value = getattr(self, perm)
                
                if old_value != new_value:
                    PermissionChangeLog.objects.create(
                        submission=self.submission,
                        user=self.user,
                        changed_by=changed_by,
                        permission_type=perm.replace('can_', ''),
                        old_value=old_value,
                        new_value=new_value,
                        role='co_investigator'
                    )
            
            # Check for role changes
            if set(old_instance.roles) != set(self.roles):
                old_roles = ', '.join([dict(COINVESTIGATOR_ROLES).get(r, r) for r in (old_instance.roles or [])])
                new_roles = ', '.join([dict(COINVESTIGATOR_ROLES).get(r, r) for r in (self.roles or [])])
                PermissionChangeLog.objects.create(
                    submission=self.submission,
                    user=self.user,
                    changed_by=changed_by,
                    permission_type='roles',
                    old_value=False,
                    new_value=True,
                    role='co_investigator',
                    notes=f'Roles changed from: {old_roles} to: {new_roles}'
                )

class ResearchAssistant(models.Model):
    submission = models.ForeignKey(
        'Submission',
        related_name='research_assistants',
        on_delete=models.CASCADE
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    can_edit = models.BooleanField(default=False)
    can_submit = models.BooleanField(default=False)
    can_view_communications = models.BooleanField(default=False)
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['submission', 'user']

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.submission.temporary_id}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def log_permission_changes(self, changed_by, is_new=False):
        """Log changes to permissions."""
        if is_new:
            # Log initial permissions
            for perm in ['can_edit', 'can_submit', 'can_view_communications']:
                if getattr(self, perm):
                    PermissionChangeLog.objects.create(
                        submission=self.submission,
                        user=self.user,
                        changed_by=changed_by,
                        permission_type=perm.replace('can_', ''),
                        old_value=False,
                        new_value=True,
                        role='research_assistant',
                        notes='Initial permission setting'
                    )
        else:
            # Get the previous state
            old_instance = ResearchAssistant.objects.get(pk=self.pk)
            
            # Check for permission changes
            for perm in ['can_edit', 'can_submit', 'can_view_communications']:
                old_value = getattr(old_instance, perm)
                new_value = getattr(self, perm)
                
                if old_value != new_value:
                    PermissionChangeLog.objects.create(
                        submission=self.submission,
                        user=self.user,
                        changed_by=changed_by,
                        permission_type=perm.replace('can_', ''),
                        old_value=old_value,
                        new_value=new_value,
                        role='research_assistant'
                    )

    def get_permissions_display(self):
        """Get a list of current permissions for display."""
        permissions = []
        if self.can_edit:
            permissions.append('Can Edit')
        if self.can_submit:
            permissions.append('Can Submit')
        if self.can_view_communications:
            permissions.append('Can View Communications')
        return permissions if permissions else ['No special permissions']

    def has_any_permissions(self):
        """Check if the research assistant has any permissions."""
        return any([self.can_edit, self.can_submit, self.can_view_communications])

class FormDataEntry(models.Model):
    submission = models.ForeignKey(Submission, related_name='form_data_entries', on_delete=models.CASCADE)
    form = models.ForeignKey(DynamicForm, on_delete=models.CASCADE)
    field_name = models.CharField(max_length=255)
    value = models.TextField()
    date_saved = models.DateTimeField(auto_now=True)
    version = models.PositiveIntegerField(default=1)
    study_action = models.ForeignKey(
        'StudyAction', 
        null=True, 
        blank=True, 
        on_delete=models.CASCADE,
        related_name='form_data_entries'
    )

    class Meta:
        indexes = [
            models.Index(fields=['submission', 'form', 'field_name']),
        ]

    def __str__(self):
        return f"{self.submission} - {self.form.name} - {self.field_name}"

    @classmethod
    def get_version_data(cls, submission, version):
        """Get all form data for a specific version of a submission."""
        entries = cls.objects.filter(
            submission=submission,
            version=version
        ).select_related('form')

        # Group data by form
        form_data = {}
        for entry in entries:
            if entry.form_id not in form_data:
                form_data[entry.form_id] = {
                    'form': entry.form,
                    'fields': {}
                }

            # Handle JSON values
            try:
                if isinstance(entry.value, str) and entry.value.startswith('['):
                    value = ', '.join(json.loads(entry.value))
                else:
                    value = entry.value
            except (json.JSONDecodeError, TypeError):
                value = entry.value

            form_data[entry.form_id]['fields'][entry.field_name] = value

        return form_data
    
    
class Document(models.Model):
    submission = models.ForeignKey(
        Submission, related_name='documents', on_delete=models.CASCADE
    )
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to='documents/')
    description = models.CharField(max_length=255, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    ALLOWED_EXTENSIONS = ['pdf', 'png', 'jpeg', 'jpg', 'doc', 'docx', 'txt']

    def __str__(self):
        return f"{self.file.name}"

    def filename(self):
        return self.file.name.split('/')[-1]

class VersionHistory(models.Model):
    submission = models.ForeignKey(
        Submission, 
        related_name='version_histories', 
        on_delete=models.CASCADE
    )
    version = models.PositiveIntegerField()
    status = models.CharField(
        max_length=50,
        choices=get_submission_status_choices
    )
    date = models.DateTimeField()
    submitted_by = models.ForeignKey(  # New field
        User,
        related_name='version_submissions',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="User who submitted this version"
    )

    def __str__(self):
        return f"Submission {self.submission.temporary_id} - Version {self.version}" 

from django.db import models
from django.core.cache import cache

class SystemSettings(models.Model):
    system_email = models.EmailField(
        default='aidi@khcc.jo',
        help_text='System email address used for automated messages'
    )
    
    class Meta:
        verbose_name = 'System Settings'
        verbose_name_plural = 'System Settings'

    def save(self, *args, **kwargs):
        cache.delete('system_settings')
        super().save(*args, **kwargs)

    @staticmethod
    def get_system_email():
        """Get the system email from settings or return default."""
        try:
            settings = SystemSettings.objects.first()
            return settings.system_email if settings else 'aidi@khcc.jo'
        except Exception:
            return 'aidi@khcc.jo'


class InvestigatorFormSubmission(models.Model):
    submission = models.ForeignKey(
        'Submission', 
        on_delete=models.CASCADE,
        related_name='investigator_form_submissions'
    )
    form = models.ForeignKey(
        'forms_builder.DynamicForm',
        on_delete=models.CASCADE
    )
    investigator = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE
    )
    date_submitted = models.DateTimeField(auto_now_add=True)
    version = models.PositiveIntegerField()

    class Meta:
        unique_together = ['submission', 'form', 'investigator', 'version']
        ordering = ['date_submitted']

    def __str__(self):
        return f"{self.investigator.get_full_name()} - {self.form.name} (v{self.version})"
    

class PermissionChangeLog(models.Model):
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE)
    user = models.ForeignKey(
        'auth.User', 
        on_delete=models.CASCADE,
        related_name='permission_changes_received'
    )
    changed_by = models.ForeignKey(
        'auth.User', 
        on_delete=models.CASCADE, 
        related_name='permission_changes_made'
    )
    permission_type = models.CharField(
        max_length=50,
        choices=[
            ('edit', 'Edit'),
            ('submit', 'Submit'),
            ('view_communications', 'View Communications')
        ]
    )
    old_value = models.BooleanField()
    new_value = models.BooleanField()
    change_date = models.DateTimeField(auto_now_add=True)
    role = models.CharField(
        max_length=50,
        choices=[
            ('co_investigator', 'Co-Investigator'),
            ('research_assistant', 'Research Assistant')
        ]
    )
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-change_date']
        verbose_name = 'Permission Change Log'
        verbose_name_plural = 'Permission Change Logs'

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.permission_type} - {self.change_date}"

    def get_change_description(self):
        """Get a human-readable description of the change."""
        action = 'granted' if self.new_value else 'removed'
        return f"{self.permission_type.title()} permission {action} for {self.user.get_full_name()} " \
               f"as {self.get_role_display()} by {self.changed_by.get_full_name()}"

class StudyAction(models.Model):
    ACTION_TYPES = [
        ('withdrawal', 'Study Withdrawal'),
        ('progress', 'Progress Report'),
        ('amendment', 'Study Amendment'),
        ('closure', 'Study Closure'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    submission = models.ForeignKey(
        'Submission', 
        on_delete=models.CASCADE,
        related_name='study_actions'
    )
    action_type = models.CharField(max_length=20, choices=ACTION_TYPES)
    performed_by = models.ForeignKey(User, on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES,
        default='pending'
    )
    notes = models.TextField(blank=True)
    version = models.IntegerField(default=1)

    class Meta:
        ordering = ['-date_created']

    def __str__(self):
        return f"{self.get_action_type_display()} - {self.submission.title}"

    def save(self, *args, **kwargs):
        if not self.version:
            self.version = self.submission.version
        super().save(*args, **kwargs)

class StudyActionDocument(models.Model):
    action = models.ForeignKey(
        StudyAction,
        on_delete=models.CASCADE,
        related_name='documents'
    )
    file = models.FileField(upload_to='study_actions/')
    description = models.CharField(max_length=255, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def filename(self):
        return self.file.name.split('/')[-1]

# Contents from: .\templatetags\__init__.py
# Empty file, but needs to exist


# Contents from: .\templatetags\form_tags.py
from django import template

register = template.Library()

@register.filter
def multiply(value, arg):
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return ''

@register.filter
def divide(value, arg):
    try:
        return float(value) / float(arg)
    except (ValueError, TypeError, ZeroDivisionError):
        return '' 

# Contents from: .\templatetags\submission_tags.py
from django import template

register = template.Library()

@register.filter
def next(value, arg):
    """
    Returns the next item from a list
    """
    try:
        return value[int(arg) + 1]
    except:
        return None

@register.filter
def attr(obj, attr):
    """
    Gets an attribute of an object dynamically
    """
    try:
        return getattr(obj, attr)
    except:
        return None


# Contents from: .\tests\__init__.py


# Contents from: .\tests\test_pdf_generator.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from io import BytesIO
import json
from datetime import datetime, timedelta

from submission.models import Submission, FormDataEntry, DynamicForm, StudyType, CoInvestigator
from users.models import Role  # Add this import
from submission.utils.pdf_generator import PDFGenerator, generate_submission_pdf

User = get_user_model()

class TestPDFGenerator(TestCase):
    def setUp(self):
        # Create test users
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        
        self.pi_user = User.objects.create_user(
            username='pi_user',
            email='pi@example.com',
            password='testpass123',
            first_name='Primary',
            last_name='Investigator'
        )

        # Create co-investigator user
        self.co_investigator = User.objects.create_user(
            username='co_investigator',
            email='co@example.com',
            password='testpass123',
            first_name='Co',
            last_name='Investigator'
        )

        # Create test roles
        self.role1 = Role.objects.create(
            name='Principal Investigator',
            description='Lead researcher'
        )
        self.role2 = Role.objects.create(
            name='Data Analyst',
            description='Analyzes research data'
        )

        # Create study type first
        self.study_type = StudyType.objects.create(
            name='Retrospective'
        )

        # Create a test submission with numeric temporary_id
        self.submission = Submission.objects.create(
            temporary_id=12345,
            title='Test Submission',
            study_type=self.study_type,
            khcc_number='IRB123',
            status='draft',
            primary_investigator=self.pi_user,
            date_created=timezone.now(),
            date_submitted=timezone.now()
        )

        # Add co-investigator to submission with multiple roles
        self.co_investigator_relation = CoInvestigator.objects.create(
            submission=self.submission,
            user=self.co_investigator,
            can_edit=True,
            can_submit=True,
            can_view_communications=True
        )
        # Add roles to the co-investigator
        self.co_investigator_relation.roles.add(self.role1, self.role2)

        # Create test dynamic form
        self.dynamic_form = DynamicForm.objects.create(
            name='Test Form'
        )

        # Create test form data entry
        self.form_entry = FormDataEntry.objects.create(
            submission=self.submission,
            form=self.dynamic_form,
            field_name='test_field',
            value='Test Value',
            version=1
        )

    def test_initialization(self):
        """Test PDF generator initialization"""
        buffer = BytesIO()
        pdf_gen = PDFGenerator(buffer, self.submission, 1, self.user)
        
        self.assertEqual(pdf_gen.submission, self.submission)
        self.assertEqual(pdf_gen.version, 1)
        self.assertEqual(pdf_gen.user, self.user)

    def test_version_validation(self):
        """Test that PDFGenerator requires a version"""
        buffer = BytesIO()
        with self.assertRaises(ValueError):
            PDFGenerator(buffer, self.submission, None, self.user)

    def test_field_value_formatting(self):
        """Test field value formatting"""
        buffer = BytesIO()
        pdf_gen = PDFGenerator(buffer, self.submission, 1, self.user)
        
        # Test various input types
        self.assertEqual(pdf_gen.format_field_value(None), "Not provided")
        self.assertEqual(pdf_gen.format_field_value(""), "Not provided")
        self.assertEqual(pdf_gen.format_field_value("test"), "test")
        
        # Test JSON array formatting
        json_array = json.dumps(['item1', 'item2'])
        self.assertEqual(pdf_gen.format_field_value(json_array), "item1, item2")

    def test_pdf_generation(self):
        """Test PDF generation function"""
        try:
            # Verify co-investigators are set up correctly
            co_investigators = CoInvestigator.objects.filter(submission=self.submission)
            self.assertTrue(co_investigators.exists(), "No co-investigators found for submission")
            
            # Verify roles are set up correctly
            co_investigator = co_investigators.first()
            self.assertEqual(co_investigator.roles.count(), 2, "Co-investigator should have 2 roles")
            
            # Test with buffer return
            pdf_buffer = generate_submission_pdf(
                self.submission, 
                version=1, 
                user=self.user, 
                as_buffer=True
            )
            self.assertIsInstance(pdf_buffer, BytesIO)
            
            # Additional verification of PDF content could be added here
            
        except Exception as e:
            import traceback
            self.fail(f"PDF generation failed with error: {str(e)}\nTraceback:\n{traceback.format_exc()}")

# Contents from: .\tests\test_views.py
# submission/tests/test_views.py

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from submission.models import Submission, StudyType
from django.utils import timezone


class SubmissionViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='testpass'
        )
        self.study_type = StudyType.objects.create(name='Retrospective')
        self.submission = Submission.objects.create(
            title='Test Submission',
            study_type=self.study_type,
            primary_investigator=self.user,
            status='draft',
            date_created=timezone.now(),
        )

    def test_dashboard_view(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('submission:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Submission')

    def test_start_submission_view_get(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('submission:start_submission'))
        self.assertEqual(response.status_code, 200)

    def test_start_submission_view_post(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(
            reverse('submission:start_submission'),
            {
                'title': 'New Submission',
                'study_type': self.study_type.id,
                'is_primary_investigator': 'on',
                'action': 'save_continue',
            },
        )
        self.assertEqual(response.status_code, 302)
        new_submission = Submission.objects.get(title='New Submission')
        self.assertEqual(new_submission.primary_investigator, self.user)

    def test_edit_submission_no_permission(self):
        other_user = User.objects.create_user(
            username='otheruser', password='testpass'
        )
        self.client.login(username='otheruser', password='testpass')
        response = self.client.get(
            reverse('submission:edit_submission', args=[self.submission.id])
        )
        self.assertEqual(response.status_code, 302)
        messages = list(response.wsgi_request._messages)
        self.assertEqual(str(messages[0]), 'You do not have permission to edit this submission.')


# Contents from: .\tests\tests_models.py
# submission/tests/test_models.py

from django.test import TestCase
from django.contrib.auth.models import User
from submission.models import (
    Submission,
    CoInvestigator,
    ResearchAssistant,
    FormDataEntry,
    Document,
    VersionHistory,
    SystemSettings,
    StatusChoice,
)
from forms_builder.models import StudyType, DynamicForm
from users.models import Role
from django.utils import timezone


class SubmissionModelsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser')
        self.study_type = StudyType.objects.create(name='Retrospective')
        self.submission = Submission.objects.create(
            title='Test Submission',
            study_type=self.study_type,
            primary_investigator=self.user,
            status='draft',
            date_created=timezone.now(),
        )
        self.role = Role.objects.create(name='Data Analyst')
        self.coinvestigator_user = User.objects.create_user(username='coinvestigator')
        self.coinvestigator = CoInvestigator.objects.create(
            submission=self.submission,
            user=self.coinvestigator_user,
            can_edit=True,
        )
        self.coinvestigator.roles.add(self.role)

    def test_submission_str(self):
        self.assertEqual(
            str(self.submission),
            f"{self.submission.title} (ID: {self.submission.temporary_id}, Version: {self.submission.version})",
        )

    def test_coinvestigator_str(self):
        self.assertEqual(
            str(self.coinvestigator),
            f"{self.coinvestigator_user.get_full_name()} - {self.submission.temporary_id}",
        )

    def test_increment_version(self):
        old_version = self.submission.version
        self.submission.increment_version()
        self.assertEqual(self.submission.version, old_version + 1)
        self.assertTrue(
            VersionHistory.objects.filter(
                submission=self.submission, version=self.submission.version
            ).exists()
        )

    def test_system_settings_email(self):
        SystemSettings.objects.create(system_email='system@example.com')
        self.assertEqual(SystemSettings.get_system_email(), 'system@example.com')

    def test_status_choice_caching(self):
        StatusChoice.objects.create(code='approved', label='Approved')
        choices = get_status_choices()
        self.assertIn(('approved', 'Approved'), choices)


# Contents from: .\urls.py
# submission/urls.py

from django.urls import path
from . import views

app_name = 'submission'

urlpatterns = [
    path('start-submission/<int:submission_id>/', views.start_submission, name='start_submission_with_id'),
    path('start-submission/', views.start_submission, name='start_submission'),
    path('edit-submission/<int:submission_id>/', views.edit_submission, name='edit_submission'),
    path('add-research-assistant/<int:submission_id>/', views.add_research_assistant, name='add_research_assistant'),
    path('add-coinvestigator/<int:submission_id>/', views.add_coinvestigator, name='add_coinvestigator'),
    path('submission-form/<int:submission_id>/<int:form_id>/', views.submission_form, name='submission_form'),
    path('submission-review/<int:submission_id>/', views.submission_review, name='submission_review'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('user-autocomplete/', views.user_autocomplete, name='user-autocomplete'),
    path('download-pdf/<int:submission_id>/', views.download_submission_pdf, name='download_submission_pdf'),
    path('download-pdf/<int:submission_id>/<int:version>/', views.download_submission_pdf, name='download_submission_pdf_version'),
    path('update-coinvestigator-order/<int:submission_id>/', views.update_coinvestigator_order, name='update_coinvestigator_order'),
    path('document-delete/<int:submission_id>/<int:document_id>/', views.document_delete, name='document_delete'),
    path('version-history/<int:submission_id>/', views.version_history, name='version_history'),
    path('<int:submission_id>/', views.submission_detail, name='submission_detail'),
    path('<int:submission_id>/version/<int:version_number>/', views.view_version, name='view_version'),
    path('compare-version/<int:submission_id>/<int:version1>/<int:version2>/', 
         views.compare_version, 
         name='compare_version'),
    path('investigator-form/<int:submission_id>/<int:form_id>/', views.investigator_form, name='investigator_form'),
    path('check-form-status/<int:submission_id>/', views.check_form_status, name='check_form_status'),
    path('archived/', views.archived_dashboard, name='archived_dashboard'),
    path('archive/<int:submission_id>/', views.archive_submission, name='archive_submission'),
    path('unarchive/<int:submission_id>/', views.unarchive_submission, name='unarchive_submission'),
    path('view/<int:submission_id>/', views.view_submission, name='view_submission'),
    path('submission/<int:submission_id>/withdraw/', views.study_withdrawal, name='study_withdrawal'),
    path('submission/<int:submission_id>/progress/', views.progress_report, name='progress_report'),
    path('submission/<int:submission_id>/amendment/', views.study_amendment, name='study_amendment'),
    path('submission/<int:submission_id>/closure/', views.study_closure, name='study_closure'),
    path('submission/<int:submission_id>/actions/', views.submission_actions, name='submission_actions'),
    path('download-action-pdf/<int:submission_id>/<int:action_id>/', 
         views.download_action_pdf, 
         name='download_action_pdf'),

    # urls.py
    path('action/<int:action_id>/pdf/', 
         views.download_action_pdf, 
         name='download_action_pdf'),
]



# Contents from: .\utils.py
# submission/utils.py

from users.models import UserProfile
from .models import CoInvestigator, ResearchAssistant, FormDataEntry
from forms_builder.models import DynamicForm
from django.db.models import Q
from django.utils import timezone


def has_edit_permission(user, submission):
    # Check if user is primary investigator
    if user == submission.primary_investigator:
        return True

    # Check if user is a co-investigator with edit permission
    if submission.coinvestigators.filter(user=user, can_edit=True).exists():
        return True

    # Check if user is a research assistant with edit permission
    if submission.research_assistants.filter(user=user, can_edit=True).exists():
        return True

    return False


def check_researcher_documents(submission):
    """Check documents for all researchers involved in the submission"""
    missing_documents = {}

    # Check primary investigator's documents
    pi_profile = submission.primary_investigator.userprofile
    pi_missing = []
    if pi_profile.is_gcp_expired:
        pi_missing.append('GCP Certificate (Expired or Missing)')
    if pi_profile.is_qrc_missing:
        pi_missing.append('QRC Certificate')
    if pi_profile.is_ctc_missing:
        pi_missing.append('CTC Certificate')
    if pi_profile.is_cv_missing:
        pi_missing.append('CV')
    if pi_missing:
        missing_documents['Primary Investigator'] = {
            'name': pi_profile.full_name,
            'documents': pi_missing
        }

    # Check co-investigators' documents
    for coinv in submission.coinvestigators.all():
        coinv_profile = coinv.user.userprofile
        coinv_missing = []
        if coinv_profile.is_gcp_expired:
            coinv_missing.append('GCP Certificate (Expired or Missing)')
        if coinv_profile.is_qrc_missing:
            coinv_missing.append('QRC Certificate')
        if coinv_profile.is_ctc_missing:
            coinv_missing.append('CTC Certificate')
        if coinv_profile.is_cv_missing:
            coinv_missing.append('CV')
        if coinv_missing:
            missing_documents[f'Co-Investigator: {coinv.role_in_study}'] = {
                'name': coinv_profile.full_name,
                'documents': coinv_missing
            }

    # Check research assistants' documents
    for ra in submission.research_assistants.all():
        ra_profile = ra.user.userprofile
        ra_missing = []
        if ra_profile.is_gcp_expired:
            ra_missing.append('GCP Certificate (Expired or Missing)')
        if ra_profile.is_qrc_missing:
            ra_missing.append('QRC Certificate')
        if ra_profile.is_ctc_missing:
            ra_missing.append('CTC Certificate')
        if ra_profile.is_cv_missing:
            ra_missing.append('CV')
        if ra_missing:
            missing_documents[f'Research Assistant'] = {
                'name': ra_profile.full_name,
                'documents': ra_missing
            }

    return missing_documents


def get_next_form(submission, current_form):
    dynamic_forms = list(submission.study_type.forms.order_by('order'))
    try:
        index = dynamic_forms.index(current_form)
        return dynamic_forms[index + 1] if index + 1 < len(dynamic_forms) else None
    except ValueError:
        return None


def get_previous_form(submission, current_form):
    dynamic_forms = list(submission.study_type.forms.order_by('order'))
    try:
        index = dynamic_forms.index(current_form)
        return dynamic_forms[index - 1] if index - 1 >= 0 else None
    except ValueError:
        return None

def compare_versions(submission, version1, version2):
    data_v1 = FormDataEntry.objects.filter(submission=submission, version=version1)
    data_v2 = FormDataEntry.objects.filter(submission=submission, version=version2)
    data = []
    fields = set(data_v1.values_list('field_name', flat=True)) | set(data_v2.values_list('field_name', flat=True))
    for field in fields:
        value1 = data_v1.filter(field_name=field).first()
        value2 = data_v2.filter(field_name=field).first()
        data.append({
            'field_name': field,
            'value1': value1.value if value1 else '',
            'value2': value2.value if value2 else '',
            'changed': (value1.value if value1 else '') != (value2.value if value2 else '')
        })
    return data

from django.contrib.auth.models import User
from .models import SystemSettings

def get_system_user():
    """Get or create the system user for automated messages"""
    system_email = SystemSettings.get_system_email()
    system_user, created = User.objects.get_or_create(
        username='system',
        defaults={
            'email': system_email,
            'is_active': False,  # System user can't login
            'first_name': 'AIDI',
            'last_name': 'System'
        }
    )
    # Update email if it changed in settings
    if system_user.email != system_email:
        system_user.email = system_email
        system_user.save()
    return system_user

# Contents from: .\utils\__init__.py
# submission/utils/__init__.py

from .pdf_generator import PDFGenerator
from .helpers import (
    has_edit_permission,
    check_researcher_documents,
    get_next_form,
    get_previous_form,
)

__all__ = [
    'PDFGenerator',
    'has_edit_permission',
    'check_researcher_documents',
    'get_next_form',
    'get_previous_form',
]

# Contents from: .\utils\forms.py
# submission/utils/forms.py

from django import forms
import json


def generate_django_form(dynamic_form):
    """
    Dynamically generate a Django form class based on a DynamicForm instance.
    """
    class DynamicModelForm(forms.Form):
        pass

    fields = {}
    for field in dynamic_form.fields.all():
        label = f"{field.displayed_name}{'*' if field.required else ''}"
        field_attrs = {
            'required': field.required,
            'label': label,
            'help_text': field.help_text,
            'initial': field.default_value,
        }
        widget_attrs = {'class': 'form-control'}

        if field.field_type == 'text':
            fields[field.name] = forms.CharField(
                max_length=field.max_length or 255,
                widget=forms.TextInput(attrs=widget_attrs),
                **field_attrs,
            )
        elif field.field_type == 'email':
            fields[field.name] = forms.EmailField(
                max_length=field.max_length or 255,
                widget=forms.EmailInput(attrs=widget_attrs),
                **field_attrs,
            )
        elif field.field_type == 'tel':
            fields[field.name] = forms.CharField(
                max_length=field.max_length or 15,
                widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'tel'}),
                **field_attrs,
            )
        elif field.field_type == 'textarea':
            fields[field.name] = forms.CharField(
                max_length=field.max_length or 500,
                widget=forms.Textarea(attrs=widget_attrs),
                **field_attrs,
            )
        elif field.field_type == 'checkbox':
            choices = [
                (choice.strip(), choice.strip())
                for choice in field.choices.split(',')
                if choice.strip()
            ]
            fields[field.name] = forms.MultipleChoiceField(
                choices=choices,
                widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
                required=field.required,
            )
        elif field.field_type == 'radio':
            choices = [
                (choice.strip(), choice.strip())
                for choice in field.choices.split(',')
                if choice.strip()
            ]
            fields[field.name] = forms.ChoiceField(
                choices=choices,
                widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
                **field_attrs,
            )
        elif field.field_type == 'select':
            choices = [
                (choice.strip(), choice.strip())
                for choice in field.choices.split(',')
                if choice.strip()
            ]
            fields[field.name] = forms.ChoiceField(
                choices=[('', '-- Select --')] + choices,
                widget=forms.Select(attrs=widget_attrs),
                **field_attrs,
            )
        elif field.field_type == 'number':
            fields[field.name] = forms.IntegerField(
                widget=forms.NumberInput(attrs=widget_attrs), **field_attrs
            )
        elif field.field_type == 'date':
            fields[field.name] = forms.DateField(
                widget=forms.DateInput(attrs={'type': 'date', **widget_attrs}),
                **field_attrs,
            )
        # Add other field types as necessary

    DynamicModelForm.base_fields = fields
    return DynamicModelForm


# Contents from: .\utils\helpers.py
# submission/utils/helpers.py

def has_edit_permission(user, submission):

    """Check if user has permission to edit the submission."""
    if user == submission.primary_investigator:
        return True
        
    # Check if user is a co-investigator with edit permission
    if submission.coinvestigators.filter(user=user, can_edit=True).exists():
        return True
        
    # Check if user is a research assistant with edit permission
    if submission.research_assistants.filter(user=user, can_edit=True).exists():
        return True
    
    # Check if user is the one who requested the review
    if submission.review_requests.filter(requested_by=user).first() or\
    submission.review_requests.filter(requested_to=user).first():
        return True

        
    return False
def check_researcher_documents(submission):
    """Check documents for all researchers involved in the submission"""
    missing_documents = {}

    def check_user_documents(profile, role_key, user_name):
        """Helper function to check documents for a user"""
        missing = []
        if not profile.has_valid_gcp:
            missing.append('GCP Certificate (Expired or Missing)')
        if not profile.has_qrc:
            missing.append('QRC Certificate')
        if not profile.has_ctc:
            missing.append('CTC Certificate')
        if not profile.has_cv:
            missing.append('CV')
        if missing:
            # Use a unique key for each user by combining role and name
            key = f"{role_key}: {user_name}"
            missing_documents[key] = {
                'name': user_name,
                'documents': missing
            }

    # Check primary investigator's documents
    pi_profile = submission.primary_investigator.userprofile
    check_user_documents(pi_profile, 'Primary Investigator', pi_profile.full_name)

    # Check co-investigators' documents
    for coinv in submission.coinvestigators.all():
        coinv_profile = coinv.user.userprofile
        check_user_documents(coinv_profile, 'Co-Investigator', coinv_profile.full_name)

    # Check research assistants' documents
    for ra in submission.research_assistants.all():
        ra_profile = ra.user.userprofile
        check_user_documents(ra_profile, 'Research Assistant', ra_profile.full_name)

    return missing_documents


def get_next_form(submission, current_form):
    dynamic_forms = list(submission.study_type.forms.order_by('order'))
    try:
        index = dynamic_forms.index(current_form)
        return dynamic_forms[index + 1] if index + 1 < len(dynamic_forms) else None
    except ValueError:
        return None


def get_previous_form(submission, current_form):
    """Get the previous form in the submission process."""
    # Get all forms for this study type in correct order
    study_forms = list(submission.study_type.forms.order_by('order'))
    
    try:
        # Find current form's index
        current_index = study_forms.index(current_form)
        
        # If we're not at the first form, return the previous one
        if current_index > 0:
            return study_forms[current_index - 1]
    except ValueError:
        pass
        
    return None

# Contents from: .\utils\pdf_generator.py
import os
import sys
import django
from pathlib import Path

# Get the project root directory and add it to Python path
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent.parent
sys.path.append(str(project_root))

# Setup Django environment - Note the corrected case for iRN
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'iRN.settings')
django.setup()

# Now we can import Django-related modules
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import simpleSplit
from django.utils import timezone
import json
from submission.models import FormDataEntry, Submission, CoInvestigator
from io import BytesIO
from django.http import HttpResponse
import logging

logger = logging.getLogger(__name__)


class PDFGenerator:
    def __init__(self, buffer, submission, version, user):
        """Initialize the PDF generator with basic settings"""
        if version is None:
            raise ValueError("Version must be specified")
            
        self.buffer = buffer
        self.submission = submission
        self.version = version
        self.user = user
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
        self.canvas.drawString(self.left_margin, self.y, "Intelligent Research Navigator (iRN) Report")
        self.y -= self.line_height * 1.5
        
        self.canvas.setFont("Helvetica-Bold", 14)
        self.canvas.drawString(self.left_margin, self.y, f"{self.submission.title} - Version {self.version}")
        self.y -= self.line_height * 1.5

    def add_footer(self):
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

    def add_basic_info(self):
        """Add basic submission information"""
        self.add_section_header("Basic Information")
        
        basic_info = [
            f"Submission ID: {self.submission.temporary_id}",
            f"Study Type: {self.submission.study_type}",
            f"KHCC #: {self.submission.khcc_number or 'Not provided'}",
            f"Status: {self.submission.get_status_display()}",
            f"Date Created: {self.submission.date_created.strftime('%Y-%m-%d')}",
            f"Date Submitted: {self.submission.date_submitted.strftime('%Y-%m-%d') if self.submission.date_submitted else 'Not submitted'}",
        ]

        for info in basic_info:
            self.write_wrapped_text(info)

    def add_research_team(self):
        """Add research team information"""
        self.add_section_header("Research Team")
        
        # Primary Investigator
        self.write_wrapped_text(f"Primary Investigator: {self.submission.primary_investigator.get_full_name()}")
        
        # Co-Investigators with their roles
        co_investigators = self.submission.coinvestigators.all()
        if co_investigators:
            self.y -= self.line_height / 2
            self.write_wrapped_text("Co-Investigators:")
            for ci in co_investigators:
                try:
                    # Get roles from JSONField
                    roles = ci.get_role_display()  # This uses the model method to get formatted roles
                    
                    # Add permissions
                    permissions = []
                    if ci.can_edit:
                        permissions.append("Can Edit")
                    if ci.can_submit:
                        permissions.append("Can Submit")
                    if ci.can_view_communications:
                        permissions.append("Can View Communications")
                    
                    # Combine name, roles and permissions
                    co_inv_info = f"- {ci.user.get_full_name()}"
                    if roles:
                        co_inv_info += f" (Roles: {', '.join(roles)})"
                    if permissions:
                        co_inv_info += f" [Permissions: {', '.join(permissions)}]"
                    
                    self.write_wrapped_text(co_inv_info, x_offset=20)
                    
                except Exception as e:
                    logger.error(f"Error processing co-investigator {ci.id}: {str(e)}")
                    # Add error indication in PDF
                    self.write_wrapped_text(
                        f"- {ci.user.get_full_name()} (Error loading roles)",
                        x_offset=20
                    )

        # Research Assistants with their permissions
        research_assistants = self.submission.research_assistants.all()
        if research_assistants:
            self.y -= self.line_height / 2
            self.write_wrapped_text("Research Assistants:")
            for ra in research_assistants:
                try:
                    # Collect permissions
                    permissions = []
                    if ra.can_edit:
                        permissions.append("Can Edit")
                    if ra.can_submit:
                        permissions.append("Can Submit")
                    if ra.can_view_communications:
                        permissions.append("Can View Communications")
                    
                    # Combine name and permissions
                    ra_info = f"- {ra.user.get_full_name()}"
                    if permissions:
                        ra_info += f" [Permissions: {', '.join(permissions)}]"
                    
                    self.write_wrapped_text(ra_info, x_offset=20)
                    
                except Exception as e:
                    logger.error(f"Error processing research assistant {ra.id}: {str(e)}")
                    self.write_wrapped_text(
                        f"- {ra.user.get_full_name()} (Error loading permissions)",
                        x_offset=20
                    )

    def format_field_value(self, value):
        """Format field value, handling special cases like JSON arrays"""
        print(f"Formatting value: {repr(value)}")  # Debug print
        
        if value is None:
            return "Not provided"
            
        if isinstance(value, str):
            if value.strip() == "":
                return "Not provided"
            if value.startswith('['):
                try:
                    value_list = json.loads(value)
                    return ", ".join(str(v) for v in value_list)
                except json.JSONDecodeError:
                    return value
        
        return str(value)

    def add_dynamic_forms(self):
        """Add dynamic form data"""
        logger.info(f"Adding dynamic forms for submission {self.submission.temporary_id} version {self.version}")
        
        form_entries = FormDataEntry.objects.filter(
            submission=self.submission,
            version=self.version
        )
        
        entry_count = form_entries.count()
        logger.info(f"Found {entry_count} form entries")
        
        if entry_count == 0:
            logger.warning(f"No form entries found for submission {self.submission.temporary_id} version {self.version}")
            self.write_wrapped_text("No form data available")
            return
            
        # Group entries by form for better organization
        entries_by_form = {}
        for entry in form_entries:
            if entry.form not in entries_by_form:
                entries_by_form[entry.form] = []
            entries_by_form[entry.form].append(entry)
        
        # Process each form
        for dynamic_form, entries in entries_by_form.items():
            logger.info(f"Processing form: {dynamic_form.name}")
            
            # Add form name as section header
            self.add_section_header(dynamic_form.name)
            
            # Get field definitions with proper display names
            field_definitions = {
                field.name: field.displayed_name 
                for field in dynamic_form.fields.all()
            }
            
            # Process each entry
            for entry in entries:
                try:
                    displayed_name = field_definitions.get(entry.field_name, entry.field_name)
                    formatted_value = self.format_field_value(entry.value)
                    
                    logger.debug(f"Writing field: {displayed_name} = {formatted_value}")
                    
                    self.write_wrapped_text(f"{displayed_name}:", bold=True)
                    if formatted_value:
                        self.write_wrapped_text(formatted_value, x_offset=20)
                    else:
                        self.write_wrapped_text("No value provided", x_offset=20)
                        
                except Exception as e:
                    logger.error(f"Error processing entry {entry.id}: {str(e)}")
                    continue

    def add_documents(self):
        """Add attached documents list"""
        self.add_section_header("Attached Documents")
        
        documents = self.submission.documents.all()
        if documents:
            for doc in documents:
                self.write_wrapped_text(
                    f"- {doc.file.name.split('/')[-1]} (Uploaded by: {doc.uploaded_by.get_full_name()})"
                )
        else:
            self.write_wrapped_text("No documents attached")

    def add_action_info(self, action_type, action_date):
        """Add action-specific information to the PDF"""
        self.add_section_header(f"{action_type.title()} Information")
        
        action_info = [
            f"Action Type: {action_type.title()}",
            f"Date: {action_date.strftime('%Y-%m-%d %H:%M')}",
        ]

        for info in action_info:
            self.write_wrapped_text(info)

    def add_dynamic_forms_for_action(self, form_entries):
        """Add dynamic form data specific to a study action"""
        logger.info(f"Adding dynamic forms for action")
        
        if not form_entries.exists():
            logger.warning("No form entries found for this action")
            self.write_wrapped_text("No form data available")
            return
            
        # Group entries by form for better organization
        entries_by_form = {}
        for entry in form_entries:
            if entry.form not in entries_by_form:
                entries_by_form[entry.form] = []
            entries_by_form[entry.form].append(entry)
        
        # Process each form
        for dynamic_form, entries in entries_by_form.items():
            logger.info(f"Processing form: {dynamic_form.name}")
            
            # Add form name as section header
            self.add_section_header(dynamic_form.name)
            
            # Get field definitions with proper display names
            field_definitions = {
                field.name: field.displayed_name 
                for field in dynamic_form.fields.all()
            }
            
            # Process each entry
            for entry in entries:
                try:
                    displayed_name = field_definitions.get(entry.field_name, entry.field_name)
                    formatted_value = self.format_field_value(entry.value)
                    
                    logger.debug(f"Writing field: {displayed_name} = {formatted_value}")
                    
                    self.write_wrapped_text(f"{displayed_name}:", bold=True)
                    if formatted_value:
                        self.write_wrapped_text(formatted_value, x_offset=20)
                    else:
                        self.write_wrapped_text("No value provided", x_offset=20)
                        
                except Exception as e:
                    logger.error(f"Error processing entry {entry.id}: {str(e)}")
                    continue

    def generate(self):
        """Generate the complete PDF"""
        self.add_header()
        self.add_basic_info()
        self.add_research_team()
        self.add_dynamic_forms()
        self.add_documents()
        self.add_footer()
        self.canvas.save()

    

def generate_submission_pdf(submission, version, user, as_buffer=False, action_type=None, action_date=None):
    """Generate PDF for a submission"""
    try:
        if version is None:
            logger.error("Version cannot be None")
            return None
            
        logger.info(f"Generating PDF for submission {submission.temporary_id} version {version}")
        
        buffer = BytesIO()
        pdf_generator = PDFGenerator(buffer, submission, version, user)
        
        # Add action-specific content if provided
        if action_type:
            pdf_generator.add_action_info(action_type, action_date)
            
        pdf_generator.generate()
        
        if as_buffer:
            buffer.seek(0)
            return buffer
        else:
            buffer.seek(0)
            response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="submission_{submission.temporary_id}_v{version}.pdf"'
            return response
            
    except Exception as e:
        logger.error(f"Error generating PDF: {str(e)}")
        logger.error("PDF generation error details:", exc_info=True)
        return None


def generate_action_pdf(submission, study_action, form_entries, user, as_buffer=False):
    """Generate PDF for a study action"""
    try:
        logger.info(f"Generating PDF for action {study_action.id} of submission {submission.temporary_id}")
        
        buffer = BytesIO()
        pdf_generator = PDFGenerator(buffer, submission, study_action.version, user)
        
        # Add header
        pdf_generator.add_header()
        
        # Add basic submission identifier
        pdf_generator.write_wrapped_text(f"Submission ID: {submission.temporary_id}")
        pdf_generator.write_wrapped_text(f"Title: {submission.title}")
        pdf_generator.y -= pdf_generator.line_height
        
        # Add action-specific information
        pdf_generator.add_section_header(f"{study_action.get_action_type_display()}")
        pdf_generator.write_wrapped_text(f"Date: {study_action.date_created.strftime('%Y-%m-%d %H:%M')}")
        pdf_generator.write_wrapped_text(f"Submitted by: {study_action.performed_by.get_full_name()}")
        pdf_generator.y -= pdf_generator.line_height
        
        # Add only the form entries for this action
        pdf_generator.add_section_header("Form Details")
        pdf_generator.add_dynamic_forms_for_action(form_entries)
        
        # Add any documents attached to this action
        action_documents = study_action.documents.all()
        if action_documents:
            pdf_generator.add_section_header("Attached Documents")
            for doc in action_documents:
                pdf_generator.write_wrapped_text(f"- {doc.filename()}")
        
        # Add footer
        pdf_generator.add_footer()
        pdf_generator.canvas.save()
        
        if as_buffer:
            buffer.seek(0)
            return buffer
        else:
            buffer.seek(0)
            response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
            response['Content-Disposition'] = (
                f'attachment; filename="submission_{submission.temporary_id}_'
                f'{study_action.action_type}_{study_action.date_created.strftime("%Y%m%d")}.pdf"'
            )
            return response
            
    except Exception as e:
        logger.error(f"Error generating action PDF: {str(e)}")
        logger.error("Action PDF generation error details:", exc_info=True)
        return None




if __name__ == "__main__":
    from django.contrib.auth import get_user_model

    def get_system_user():
        User = get_user_model()
        return User.objects.filter(is_superuser=True).first()

    def main():
        try:
            buffer = BytesIO()
            # Get submission with ID 88
            submission = Submission.objects.get(temporary_id=89)
            
            user = get_system_user()
            if not user:
                print("No superuser found!")
                return

            pdf_generator = PDFGenerator(buffer, submission, 1, user)
            pdf_generator.generate()
            
            # Save the PDF to a file
            buffer.seek(0)
            output_path = current_dir / "submission_88_output.pdf"
            with open(output_path, "wb") as f:
                f.write(buffer.getvalue())
            
            print(f"PDF generated successfully at: {output_path}")
            
        except Submission.DoesNotExist:
            print("Submission with ID 88 does not exist!")
        except Exception as e:
            print(f"Error generating PDF: {str(e)}")

    main()

    

# Contents from: .\utils\permissions.py
# submission/utils/permissions.py
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.core.exceptions import PermissionDenied

def check_submission_permission(action_type):
    """
    Decorator to check submission permissions for different action types.
    action_type can be: 'edit', 'submit', 'view_communications'
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, submission_id, *args, **kwargs):
            from submission.models import Submission
            
            try:
                submission = Submission.objects.get(pk=submission_id)
                
                # Primary Investigator has all permissions
                if request.user == submission.primary_investigator:
                    return view_func(request, submission_id, *args, **kwargs)
                
                # Check Co-Investigator permissions
                coinv = submission.coinvestigators.filter(user=request.user).first()
                if coinv:
                    if action_type == 'edit' and coinv.can_edit:
                        return view_func(request, submission_id, *args, **kwargs)
                    elif action_type == 'submit' and coinv.can_submit:
                        return view_func(request, submission_id, *args, **kwargs)
                    elif action_type == 'view_communications' and coinv.can_view_communications:
                        return view_func(request, submission_id, *args, **kwargs)
                
                # Check Research Assistant permissions
                ra = submission.research_assistants.filter(user=request.user).first()
                if ra:
                    if action_type == 'edit' and ra.can_edit:
                        return view_func(request, submission_id, *args, **kwargs)
                    elif action_type == 'submit' and ra.can_submit:
                        return view_func(request, submission_id, *args, **kwargs)
                    elif action_type == 'view_communications' and ra.can_view_communications:
                        return view_func(request, submission_id, *args, **kwargs)
                
                messages.error(request, f"You don't have permission to {action_type} this submission.")
                return redirect('submission:dashboard')
                
            except Submission.DoesNotExist:
                messages.error(request, "Submission not found.")
                return redirect('submission:dashboard')
                
        return _wrapped_view
    return decorator

# Contents from: .\utils\validation.py
# utils/validation.py

from django import forms
import json

def get_validation_errors(submission):
    """
    Validate all forms in the submission and return any errors.
    """
    validation_errors = {}
    
    # Get all forms for this study type
    for dynamic_form in submission.study_type.forms.order_by('order'):
        django_form_class = generate_django_form(dynamic_form)
        entries = FormDataEntry.objects.filter(
            submission=submission, 
            form=dynamic_form, 
            version=submission.version
        )
        saved_data = {
            f'form_{dynamic_form.id}-{entry.field_name}': entry.value
            for entry in entries
        }
        
        form_instance = django_form_class(data=saved_data, prefix=f'form_{dynamic_form.id}')
        is_valid = True
        errors = {}
        
        for field_name, field in form_instance.fields.items():
            field_key = f'form_{dynamic_form.id}-{field_name}'
            field_value = saved_data.get(field_key)
            
            if isinstance(field, forms.MultipleChoiceField):
                try:
                    if field.required and (not field_value or field_value == '[]'):
                        is_valid = False
                        errors[field_name] = ['This field is required']
                except json.JSONDecodeError:
                    is_valid = False
                    errors[field_name] = ['Invalid value']
            else:
                if field.required and not field_value:
                    is_valid = False
                    errors[field_name] = ['This field is required']

        if not is_valid:
            validation_errors[dynamic_form.name] = errors

    return validation_errors

def check_certifications(user_profile):
    """
    Check if a user's certifications are valid.
    """
    issues = []
    
    if not user_profile.has_valid_gcp:
        issues.append('GCP Certificate missing or expired')
    if not user_profile.has_cv:
        issues.append('CV missing')
    if user_profile.role == 'KHCC investigator':
        if not user_profile.has_qrc:
            issues.append('QRC Certificate missing')
        if not user_profile.has_ctc:
            issues.append('CTC Certificate missing')
    elif user_profile.role == 'Research Assistant/Coordinator':
        if not user_profile.has_ctc:
            issues.append('CTC Certificate missing')
            
    return issues

def check_team_certifications(submission):
    """
    Check certifications for the entire research team.
    """
    certification_issues = {}
    
    # Check PI certifications
    pi_issues = check_certifications(submission.primary_investigator.userprofile)
    if pi_issues:
        certification_issues['Primary Investigator'] = {
            'name': submission.primary_investigator.get_full_name(),
            'issues': pi_issues
        }
    
    # Check Co-Investigator certifications
    for coinv in submission.coinvestigators.all():
        coinv_issues = check_certifications(coinv.user.userprofile)
        if coinv_issues:
            certification_issues[f'Co-Investigator'] = {
                'name': coinv.user.get_full_name(),
                'issues': coinv_issues
            }
    
    # Check Research Assistant certifications
    for ra in submission.research_assistants.all():
        ra_issues = check_certifications(ra.user.userprofile)
        if ra_issues:
            certification_issues[f'Research Assistant'] = {
                'name': ra.user.get_full_name(),
                'issues': ra_issues
            }
    
    return certification_issues

# Contents from: .\views.py
# Django imports
from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.files.base import ContentFile
from django.db import IntegrityError, transaction
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

# Third party imports
from dal import autocomplete
from io import BytesIO
import json
import logging

# Local imports
from .forms import (
    CoInvestigatorForm,
    DocumentForm,
    ResearchAssistantForm,
    SubmissionForm,
    generate_django_form,
)
from forms_builder.models import DynamicForm
from messaging.models import Message, MessageAttachment
from .models import (
    CoInvestigator,
    Document,
    FormDataEntry,
    InvestigatorFormSubmission,
    PermissionChangeLog,
    ResearchAssistant,
    StudyAction,
    StudyActionDocument,
    Submission,
    VersionHistory,
)
from users.models import SystemSettings, UserProfile
from .utils import (
    PDFGenerator,
    check_researcher_documents,
    get_next_form,
    get_previous_form,
    has_edit_permission,
)
from .utils.pdf_generator import generate_submission_pdf, generate_action_pdf
from .utils.permissions import check_submission_permission
from .gpt_analysis import ResearchAnalyzer
from submission.utils.pdf_generator import PDFGenerator, generate_submission_pdf


logger = logging.getLogger(__name__)
def get_system_user():
    """Get or create the system user for automated messages."""
    try:
        with transaction.atomic():
            # First try to get existing system user
            try:
                system_user = User.objects.get(username='system')
            except User.DoesNotExist:
                # Create new system user if doesn't exist
                system_user = User.objects.create(
                    username='system',
                    email=SystemSettings.get_system_email(),
                    first_name='System',
                    last_name='User',
                    is_active=True
                )
            
            # Try to get or create UserProfile
            try:
                profile = UserProfile.objects.get(user=system_user)
            except UserProfile.DoesNotExist:
                profile = UserProfile.objects.create(
                    user=system_user,
                    full_name='System User',
                    phone_number='',
                    department='',
                    position='System'
                )
            
            return system_user
            
    except Exception as e:
        logger.error(f"Error in get_system_user: {str(e)}")
        logger.error("Error details:", exc_info=True)
        
        # Final fallback - just get or create the user without profile
        try:
            system_user = User.objects.get(username='system')
        except User.DoesNotExist:
            system_user = User.objects.create(
                username='system',
                email='aidi@khcc.jo',
                first_name='System',
                last_name='User',
                is_active=True
            )
        return system_user

@login_required
def dashboard(request):
    """Display user's submissions dashboard."""
    from django.db.models import Max, Prefetch
    
    # Get all active submissions for the user
    submissions = Submission.objects.filter(
        is_archived=False
    ).select_related(
        'primary_investigator__userprofile',
        'study_type'
    ).prefetch_related(
        'coinvestigators',
        'research_assistants'
    ).order_by('-date_created')
    
    # Process each submission
    for submission in submissions:
        # Get actual latest version
        latest_version = FormDataEntry.objects.filter(
            submission=submission
        ).values('version').aggregate(Max('version'))['version__max']
        submission.actual_version = latest_version or 1
        
        # Check for pending forms
        submission.has_pending = submission.has_pending_forms(request.user)
        
        # Get required forms for this user
        submission.pending_forms = submission.get_pending_investigator_forms(request.user)

    return render(request, 'submission/dashboard.html', {
        'submissions': submissions
    })
@login_required
def edit_submission(request, submission_id):
    """Redirect to start_submission with existing submission ID."""
    return redirect('submission:start_submission_with_id', submission_id=submission_id)

@login_required
def start_submission(request, submission_id=None):
    """Start or edit a submission."""
    if submission_id:
        submission = get_object_or_404(Submission, pk=submission_id)
        if submission.is_locked:
            messages.error(request, "This submission is locked and cannot be edited.")
            return redirect('submission:dashboard')
        if not has_edit_permission(request.user, submission):
            messages.error(request, "You do not have permission to edit this submission.")
            return redirect('submission:dashboard')
        
        initial_data = {
            'primary_investigator': submission.primary_investigator
        }
    else:
        submission = None
        initial_data = {}

    if request.method == 'POST':
        form = SubmissionForm(request.POST, instance=submission)
        action = request.POST.get('action')
        
        if action == 'exit_no_save':
            return redirect('submission:dashboard')
            
        if form.is_valid():
            try:
                with transaction.atomic():
                    submission = form.save(commit=False)
                    is_pi = request.POST.get('is_primary_investigator') == 'on'
                    
                    if is_pi:
                        submission.primary_investigator = request.user
                    else:
                        pi_user = form.cleaned_data.get('primary_investigator')
                        if not pi_user:
                            messages.error(request, 'Please select a primary investigator.')
                            return render(request, 'submission/start_submission.html', {
                                'form': form,
                                'submission': submission
                            })
                        submission.primary_investigator = pi_user

                    # Save the submission first
                    submission.save()
                    form.save_m2m()

                    # Handle user role if not PI
                    if request.user != submission.primary_investigator:
                        user_role = request.POST.get('user_role')
                        
                        if user_role == 'research_assistant':
                            ResearchAssistant.objects.create(
                                submission=submission,
                                user=request.user,
                                can_edit=True,
                                can_submit=True,
                                can_view_communications=True
                            )
                        elif user_role == 'coinvestigator':
                            # Get selected roles
                            ci_roles = request.POST.getlist('ci_roles')
                            if not ci_roles:
                                ci_roles = ['general']  # Default role if none selected
                                
                            CoInvestigator.objects.create(
                                submission=submission,
                                user=request.user,
                                can_edit=True,
                                can_submit=True,
                                can_view_communications=True,
                                roles=ci_roles
                            )
                        else:
                            messages.error(request, 'Please select your role in the submission.')
                            return render(request, 'submission/start_submission.html', {
                                'form': form,
                                'submission': submission
                            })

                    messages.success(request, 'Submission saved successfully.')
                    
                    if action == 'save_exit':
                        return redirect('submission:dashboard')
                    elif action == 'save_continue':
                         return redirect('submission:add_coinvestigator', submission_id=submission.temporary_id)

            except Exception as e:
                logger.error(f"Error in start_submission: {str(e)}")
                messages.error(request, f"An error occurred: {str(e)}")
                return render(request, 'submission/start_submission.html', {
                    'form': form,
                    'submission': submission
                })
    else:
        form = SubmissionForm(instance=submission, initial=initial_data)
        if submission and submission.primary_investigator == request.user:
            form.fields['is_primary_investigator'].initial = True

    return render(request, 'submission/start_submission.html', {
        'form': form,
        'submission': submission
    })



@login_required
def add_research_assistant(request, submission_id):
    """Add or manage research assistants for a submission."""
    submission = get_object_or_404(Submission, pk=submission_id)
    
    # Check if user has permission to modify research assistants
    if not submission.can_user_edit(request.user):
        messages.error(request, "You don't have permission to modify research assistants.")
        return redirect('submission:dashboard')

    if submission.is_locked:
        messages.error(request, "This submission is locked and cannot be edited.")
        return redirect('submission:dashboard')

    # Initialize form variable
    form = ResearchAssistantForm(submission=submission)

    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'delete_assistant':
            assistant_id = request.POST.get('assistant_id')
            if assistant_id:
                try:
                    assistant = ResearchAssistant.objects.get(id=assistant_id, submission=submission)
                    # Log the deletion
                    PermissionChangeLog.objects.create(
                        submission=submission,
                        user=assistant.user,
                        changed_by=request.user,
                        permission_type='removed',
                        old_value=True,
                        new_value=False,
                        role='research_assistant',
                        notes=f"Research Assistant removed from submission by {request.user.get_full_name()}"
                    )
                    assistant.delete()
                    messages.success(request, 'Research assistant removed successfully.')
                except ResearchAssistant.DoesNotExist:
                    messages.error(request, 'Research assistant not found.')
            return redirect('submission:add_research_assistant', submission_id=submission.temporary_id)

        if action in ['back', 'exit_no_save', 'save_continue']:
            if action == 'back':
                return redirect('submission:start_submission_with_id', submission_id=submission.temporary_id)
            elif action == 'exit_no_save':
                return redirect('submission:dashboard')
            elif action == 'save_continue':
                return redirect('submission:add_coinvestigator', submission_id=submission.temporary_id)

        form = ResearchAssistantForm(request.POST, submission=submission)
        if form.is_valid():
            assistant = form.cleaned_data.get('assistant')
            if assistant:
                try:
                    with transaction.atomic():
                        # Create new research assistant
                        ra = ResearchAssistant(
                            submission=submission,
                            user=assistant,
                            can_submit=form.cleaned_data.get('can_submit', False),
                            can_edit=form.cleaned_data.get('can_edit', False),
                            can_view_communications=form.cleaned_data.get('can_view_communications', False)
                        )
                        
                        # Save first
                        ra.save()
                        
                        # Then log permission changes
                        ra.log_permission_changes(changed_by=request.user, is_new=True)

                        # Create notification
                        Message.objects.create(
                            sender=get_system_user(),
                            subject=f'Added as Research Assistant to {submission.title}',
                            body=f"""
You have been added as a Research Assistant to:

Submission ID: {submission.temporary_id}
Title: {submission.title}
Principal Investigator: {submission.primary_investigator.get_full_name()}

Your permissions:
- Can Edit: {'Yes' if ra.can_edit else 'No'}
- Can Submit: {'Yes' if ra.can_submit else 'No'}
- Can View Communications: {'Yes' if ra.can_view_communications else 'No'}

Please log in to view the submission.
                            """.strip(),
                            related_submission=submission
                        ).recipients.add(assistant)

                        messages.success(request, 'Research assistant added successfully.')
                        
                        if action == 'save_exit':
                            return redirect('submission:dashboard')
                        elif action == 'save_add_another':
                            return redirect('submission:add_research_assistant', 
                                         submission_id=submission.temporary_id)

                except IntegrityError:
                    messages.error(request, 'This user is already a research assistant for this submission.')
                except Exception as e:
                    logger.error(f"Error saving research assistant: {str(e)}")
                    messages.error(request, f'Error adding research assistant: {str(e)}')

    # Get research assistants with permission information
    assistants = ResearchAssistant.objects.filter(submission=submission).select_related('user')
    
    # Get permission change history
    permission_history = PermissionChangeLog.objects.filter(
        submission=submission,
        role='research_assistant'
    ).select_related('user', 'changed_by').order_by('-change_date')[:10]

    return render(request, 'submission/add_research_assistant.html', {
        'form': form,
        'submission': submission,
        'assistants': assistants,
        'permission_history': permission_history,
        'can_modify': submission.can_user_edit(request.user)
    })

@login_required
def add_coinvestigator(request, submission_id):
    """Add or manage co-investigators for a submission."""
    submission = get_object_or_404(Submission, pk=submission_id)
    
    # Check if user has permission to modify co-investigators
    if not submission.can_user_edit(request.user):
        messages.error(request, "You don't have permission to modify co-investigators.")
        return redirect('submission:dashboard')

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'delete_coinvestigator':
            coinvestigator_id = request.POST.get('coinvestigator_id')
            if coinvestigator_id:
                try:
                    coinvestigator = CoInvestigator.objects.get(id=coinvestigator_id, submission=submission)
                    # Log the deletion
                    PermissionChangeLog.objects.create(
                        submission=submission,
                        user=coinvestigator.user,
                        changed_by=request.user,
                        permission_type='removed',
                        old_value=True,
                        new_value=False,
                        role='co_investigator',
                        notes=f"Co-investigator removed from submission by {request.user.get_full_name()}"
                    )
                    coinvestigator.delete()
                    messages.success(request, 'Co-investigator removed successfully.')
                except CoInvestigator.DoesNotExist:
                    messages.error(request, 'Co-investigator not found.')
            return redirect('submission:add_coinvestigator', submission_id=submission.temporary_id)

        if action in ['back', 'exit_no_save', 'save_continue']:
            if action == 'back':
                return redirect('submission:start_submission_with_id', submission_id=submission.temporary_id)
            elif action == 'exit_no_save':
                return redirect('submission:dashboard')
            elif action == 'save_continue':
                first_form = submission.study_type.forms.order_by('order').first()
                if first_form:
                    return redirect('submission:submission_form', 
                                  submission_id=submission.temporary_id,
                                  form_id=first_form.id)
                else:
                    return redirect('submission:submission_review', 
                                  submission_id=submission.temporary_id)

        form = CoInvestigatorForm(request.POST, submission=submission)
        if form.is_valid():
            investigator = form.cleaned_data.get('investigator')
            selected_roles = form.cleaned_data.get('roles')
            
            if investigator:
                try:
                    with transaction.atomic():
                        # Create new co-investigator
                        coinv = CoInvestigator(
                            submission=submission,
                            user=investigator,
                            can_submit=form.cleaned_data.get('can_submit', False),
                            can_edit=form.cleaned_data.get('can_edit', False),
                            can_view_communications=form.cleaned_data.get('can_view_communications', False)
                        )
                        
                        # Set roles (it's a list field, not M2M)
                        coinv.roles = list(selected_roles)
                        
                        # Save first
                        coinv.save()
                        
                        # Then log permission changes
                        coinv.log_permission_changes(changed_by=request.user, is_new=True)

                        # Create notification
                        Message.objects.create(
                            sender=get_system_user(),
                            subject=f'Added as Co-Investigator to {submission.title}',
                            body=f"""
You have been added as a Co-Investigator to:

Submission ID: {submission.temporary_id}
Title: {submission.title}
Principal Investigator: {submission.primary_investigator.get_full_name()}

Your roles: {', '.join(coinv.get_role_display())}

Your permissions:
- Can Edit: {'Yes' if coinv.can_edit else 'No'}
- Can Submit: {'Yes' if coinv.can_submit else 'No'}
- Can View Communications: {'Yes' if coinv.can_view_communications else 'No'}

Please log in to view the submission.
                            """.strip(),
                            related_submission=submission
                        ).recipients.add(investigator)

                        messages.success(request, 'Co-investigator added successfully.')
                        
                        if action == 'save_exit':
                            return redirect('submission:dashboard')
                        elif action == 'save_add_another':
                            return redirect('submission:add_coinvestigator', 
                                         submission_id=submission.temporary_id)

                except IntegrityError:
                    messages.error(request, 'This user is already a co-investigator for this submission.')
                except Exception as e:
                    logger.error(f"Error saving co-investigator: {str(e)}")
                    messages.error(request, f'Error adding co-investigator: {str(e)}')
            else:
                messages.error(request, 'Please select a co-investigator.')
    else:
        form = CoInvestigatorForm()

    coinvestigators = CoInvestigator.objects.filter(submission=submission)
    
    # Get permission change history
    permission_history = PermissionChangeLog.objects.filter(
        submission=submission,
        role='co_investigator'
    ).select_related('user', 'changed_by').order_by('-change_date')[:10]

    return render(request, 'submission/add_coinvestigator.html', {
        'form': form,
        'submission': submission,
        'coinvestigators': coinvestigators,
        'permission_history': permission_history,
        'can_modify': submission.can_user_edit(request.user)
    })


@login_required
@check_submission_permission('edit')
def submission_form(request, submission_id, form_id):
    """Handle dynamic form submission and display."""
    submission = get_object_or_404(Submission, temporary_id=submission_id)
    if not has_edit_permission(request.user, submission):
        messages.error(request, "You do not have permission to edit this submission.")
        return redirect('submission:dashboard')
    if submission.is_locked:
        messages.error(request, "This submission is locked and cannot be edited.")
        return redirect('submission:dashboard')

    dynamic_form = get_object_or_404(DynamicForm, pk=form_id)
    previous_form = get_previous_form(submission, dynamic_form)

    if request.method == 'POST':
        action = request.POST.get('action')

        # Handle navigation actions without form processing
        if action in ['back', 'exit_no_save']:
            if action == 'back':
                if previous_form:
                    return redirect('submission:submission_form', 
                                  submission_id=submission.temporary_id, 
                                  form_id=previous_form.id)
                return redirect('submission:add_coinvestigator', 
                              submission_id=submission.temporary_id)
            return redirect('submission:dashboard')

        # Create form instance
        DynamicFormClass = generate_django_form(dynamic_form)
        
        # Save form fields
        for field in dynamic_form.fields.all():
            field_name = field.name
            
            # Handle checkbox fields differently
            if field.field_type == 'checkbox':
                values = request.POST.getlist(f'form_{dynamic_form.id}-{field_name}')
                value = json.dumps(values) if values else '[]'
            else:
                value = request.POST.get(f'form_{dynamic_form.id}-{field_name}', '')
                
            FormDataEntry.objects.update_or_create(
                submission=submission,
                form=dynamic_form,
                field_name=field_name,
                version=submission.version,
                defaults={'value': value}
            )
        
        # Handle post-save navigation
        if action == 'save_exit':
            return redirect('submission:dashboard')
        elif action == 'save_continue':
            next_form = get_next_form(submission, dynamic_form)
            if next_form:
                return redirect('submission:submission_form', 
                              submission_id=submission.temporary_id, 
                              form_id=next_form.id)
            return redirect('submission:submission_review', 
                          submission_id=submission.temporary_id)
    
    # GET request handling
    DynamicFormClass = generate_django_form(dynamic_form)
    current_data = {}
    
    # Get current version's data
    entries = FormDataEntry.objects.filter(
        submission=submission,
        form=dynamic_form,
        version=submission.version
    )
    
    for entry in entries:
        field = dynamic_form.fields.get(name=entry.field_name)
        if field:
            if field.field_type == 'checkbox':
                try:
                    current_data[entry.field_name] = json.loads(entry.value)
                except json.JSONDecodeError:
                    current_data[entry.field_name] = []
            else:
                current_data[entry.field_name] = entry.value

    # If no current data and not version 1, get previous version's data
    if not current_data and submission.version > 1 and not submission.is_locked:
        previous_entries = FormDataEntry.objects.filter(
            submission=submission,
            form=dynamic_form,
            version=submission.version - 1
        )
        
        for entry in previous_entries:
            field = dynamic_form.fields.get(name=entry.field_name)
            if field:
                if field.field_type == 'checkbox':
                    try:
                        current_data[entry.field_name] = json.loads(entry.value)
                    except json.JSONDecodeError:
                        current_data[entry.field_name] = []
                else:
                    current_data[entry.field_name] = entry.value

    # Create form instance with processed data
    form_instance = DynamicFormClass(
        initial=current_data,
        prefix=f'form_{dynamic_form.id}'
    )

    context = {
        'form': form_instance,
        'submission': submission,
        'dynamic_form': dynamic_form,
        'previous_form': previous_form,
    }
    return render(request, 'submission/dynamic_form.html', context)


@login_required
@check_submission_permission('submit')
def submission_review(request, submission_id):
    submission = get_object_or_404(Submission, temporary_id=submission_id)
    
    if submission.is_locked and not has_edit_permission(request.user, submission):
        messages.error(request, "You do not have permission to edit this submission.")
        return redirect('submission:dashboard')

    missing_documents = check_researcher_documents(submission)
    validation_errors = {}
    
    # Validate all forms
    for dynamic_form in submission.study_type.forms.order_by('order'):
        django_form_class = generate_django_form(dynamic_form)
        entries = FormDataEntry.objects.filter(
            submission=submission, 
            form=dynamic_form, 
            version=submission.version
        )
        saved_data = {
            f'form_{dynamic_form.id}-{entry.field_name}': entry.value
            for entry in entries
        }
        
        form_instance = django_form_class(data=saved_data, prefix=f'form_{dynamic_form.id}')
        is_valid = True
        errors = {}
        
        for field_name, field in form_instance.fields.items():
            if isinstance(field, forms.MultipleChoiceField):
                field_key = f'form_{dynamic_form.id}-{field_name}'
                field_value = saved_data.get(field_key)
                if not field_value and field.required:
                    is_valid = False
                    errors[field_name] = ['Please select at least one option']
            else:
                field_value = form_instance.data.get(f'form_{dynamic_form.id}-{field_name}')
                if field.required and not field_value:
                    is_valid = False
                    errors[field_name] = ['This field is required']

        if not is_valid:
            validation_errors[dynamic_form.name] = errors

    documents = submission.documents.all()
    doc_form = DocumentForm()
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'submit_final':
            # Check for required certificates
            missing_certs = check_researcher_documents(submission)
            if missing_certs:
                messages.error(request, 'Cannot submit: All team members must have valid certificates uploaded in the system.')
                return redirect('submission:submission_review', submission_id=submission_id)
            
            # Check for missing documents or validation errors
            if missing_documents or validation_errors:
                messages.error(request, 'Please resolve the missing documents and form errors before final submission.')
                return redirect('submission:submission_review', submission_id=submission_id)

            try:
                with transaction.atomic():
                    # Submit the submission and track who submitted it
                    submission.submitted_by = request.user
                    submission.date_submitted = timezone.now()
                    submission.is_locked = True

                    # Check for pending forms from non-submitter team members
                    non_submitters = submission.get_non_submitters()
                    required_forms = submission.get_required_investigator_forms()
                    
                    has_pending_forms = False
                    for member in non_submitters:
                        for form in required_forms:
                            if not submission.has_submitted_form(member, form):
                                has_pending_forms = True
                                break
                        if has_pending_forms:
                            break

                    # Set appropriate status
                    submission.status = 'document_missing' if has_pending_forms else 'submitted'
                    submission.save()
                    
                    # Create version history entry with submitter info
                    VersionHistory.objects.create(
                        submission=submission,
                        version=submission.version,
                        status=submission.status,
                        date=timezone.now(),
                        submitted_by=request.user
                    )

                    # Generate submission PDF
                    buffer = generate_submission_pdf(
                        submission=submission,
                        version=submission.version,
                        user=request.user,
                        as_buffer=True
                    )

                    if not buffer:
                        raise ValueError("Failed to generate PDF for submission")

                    # Get system user for notifications
                    system_user = get_system_user()
                    pdf_filename = f"submission_{submission.temporary_id}_v{submission.version}.pdf"

                    # Send notification to PI
                    pi_message = Message.objects.create(
                        sender=system_user,
                        subject=f'Submission {submission.temporary_id} - Version {submission.version} {"Awaiting Forms" if has_pending_forms else "Confirmation"}',
                        body=f"""
Dear {submission.primary_investigator.userprofile.full_name},

Your submission (ID: {submission.temporary_id}) has been submitted by {request.user.get_full_name()}.

Status: {'Pending team member forms' if has_pending_forms else 'Complete submission'}

{'''Some team members still need to complete their required forms.
The submission will be forwarded for review once all forms are completed.''' if has_pending_forms else 'All forms are complete. Your submission will now be reviewed by OSAR.'}

Please find the attached PDF for your records.

Best regards,
AIDI System
                        """.strip(),
                        related_submission=submission
                    )
                    pi_message.recipients.add(submission.primary_investigator)
                    
                    # Attach PDF to PI message
                    pi_attachment = MessageAttachment(message=pi_message)
                    pi_attachment.file.save(pdf_filename, ContentFile(buffer.getvalue()))

                    if has_pending_forms:
                        # Notify team members about pending forms
                        notify_pending_forms(submission)
                    else:
                        # Notify OSAR only if all forms are complete
                        notify_osar_of_completion(submission)

                    # Increment version after everything is done
                    # submission.version += 1
                    # submission.save()

                    messages.success(
                        request, 
                        'Submission completed.' + 
                        (' Awaiting required forms from team members.' if has_pending_forms else ' Sent to OSAR for review.')
                    )
                    return redirect('submission:dashboard')

            except Exception as e:
                logger.error(f"Error in submission finalization: {str(e)}")
                messages.error(request, f"Error during submission: {str(e)}")
                return redirect('submission:dashboard')

        elif action == 'back':
                logger.error(f"Error in submission finalization: {str(e)}")
                messages.error(request, f"Error during submission: {str(e)}")
                return redirect('submission:dashboard')    
        if request.method == 'POST':
            action = request.POST.get('action')
            
        if action == 'submit_final':
            missing_certs = check_researcher_documents(submission)
            if missing_certs:
                messages.error(request, 'Cannot submit: All team members must have valid certificates uploaded in the system.')
                return redirect('submission:submission_review', submission_id=submission_id)
            
            if missing_documents or validation_errors:
                messages.error(request, 'Please resolve the missing documents and form errors before final submission.')
            else:
                try:
                    with transaction.atomic():
                        # Check for required investigator forms
                        required_forms = submission.study_type.forms.filter(requested_per_investigator=True)
                        team_members = []
                        team_members.extend([ci.user for ci in submission.coinvestigators.all()])
                        team_members.extend([ra.user for ra in submission.research_assistants.all()])
                        
                        # Check if there are pending forms for any team member
                        has_pending_forms = False
                        for member in team_members:
                            for form in required_forms:
                                if not InvestigatorFormSubmission.objects.filter(
                                    submission=submission,
                                    form=form,
                                    investigator=member,
                                    version=submission.version
                                ).exists():
                                    has_pending_forms = True
                                    break
                            if has_pending_forms:
                                break

                        # Set status based on pending forms
                        submission.is_locked = True
                        submission.status = 'document_missing' if has_pending_forms else 'submitted'
                        submission.date_submitted = timezone.now()
                        
                        # Create version history entry
                        VersionHistory.objects.create(
                            submission=submission,
                            version=submission.version,
                            status=submission.status,
                            date=timezone.now()
                        )

                        # Generate PDF
                        buffer = generate_submission_pdf(
                            submission=submission,
                            version=submission.version,
                            user=request.user,
                            as_buffer=True
                        )

                        if not buffer:
                            raise ValueError("Failed to generate PDF for submission")

                        # Get system user for automated messages
                        system_user = get_system_user()
                        
                        # Create PDF filename
                        pdf_filename = f"submission_{submission.temporary_id}_v{submission.version}.pdf"

                        # Send confirmation to PI with appropriate message
                        pi_message = Message.objects.create(
                            sender=system_user,
                            subject=f'Submission {submission.temporary_id} - Version {submission.version} {"Awaiting Forms" if has_pending_forms else "Confirmation"}',
                            body=f"""
Dear {submission.primary_investigator.userprofile.full_name},

Your submission (ID: {submission.temporary_id}) has been successfully received.
{'Note: The submission is pending required forms from team members.' if has_pending_forms else 'All required forms have been completed.'}

{'The submission will be forwarded for review once all team members complete their required forms.' if has_pending_forms else 'Your submission will now be reviewed by OSAR.'}

Please find the attached PDF for your records.

Best regards,
AIDI System
                            """.strip(),
                            related_submission=submission
                        )
                        pi_message.recipients.add(submission.primary_investigator)
                        
                        # Attach PDF to PI message
                        pi_attachment = MessageAttachment(message=pi_message)
                        pi_attachment.file.save(pdf_filename, ContentFile(buffer.getvalue()))

                        if has_pending_forms:
                            # Notify team members about pending forms
                            notify_pending_forms(submission)
                        else:
                            # Notify OSAR only if all forms are complete
                            notify_osar_of_completion(submission)

                        # Increment version after everything is done
                        # submission.version += 1
                        # submission.save()

                        messages.success(
                            request, 
                            'Submission completed.' + 
                            (' Awaiting required forms from team members.' if has_pending_forms else ' Sent to OSAR for review.')
                        )
                        return redirect('submission:dashboard')

                except Exception as e:
                    logger.error(f"Error in submission finalization: {str(e)}")
                    messages.error(request, f"Error during submission: {str(e)}")
                    return redirect('submission:dashboard')

        elif action == 'back':
            last_form = submission.study_type.forms.order_by('-order').first()
            if last_form:
                return redirect('submission:submission_form',
                              submission_id=submission.temporary_id,
                              form_id=last_form.id)
            return redirect('submission:add_coinvestigator',
                          submission_id=submission.temporary_id)

        elif action == 'exit_no_save':
            return redirect('submission:dashboard')

        elif action == 'upload_document':
            doc_form = DocumentForm(request.POST, request.FILES)
            if doc_form.is_valid():
                document = doc_form.save(commit=False)
                document.submission = submission
                document.uploaded_by = request.user
                
                ext = document.file.name.split('.')[-1].lower()
                if ext in Document.ALLOWED_EXTENSIONS:
                    document.save()
                    messages.success(request, 'Document uploaded successfully.')
                else:
                    messages.error(
                        request,
                        f'Invalid file type: .{ext}. Allowed types are: {", ".join(Document.ALLOWED_EXTENSIONS)}'
                    )
            else:
                messages.error(request, 'Please correct the errors in the document form.')

    context = {
        'submission': submission,
        'missing_documents': missing_documents,
        'validation_errors': validation_errors,
        'documents': documents,
        'doc_form': doc_form,
        'gpt_analysis': cache.get(f'gpt_analysis_{submission.temporary_id}_{submission.version}'),
        'can_submit': submission.can_user_submit(request.user),
    }

    return render(request, 'submission/submission_review.html', context)

@login_required
def document_delete(request, submission_id, document_id):
    """Delete a document from a submission."""
    submission = get_object_or_404(Submission, pk=submission_id)
    document = get_object_or_404(Document, pk=document_id, submission=submission)
    
    if request.user == document.uploaded_by or has_edit_permission(request.user, submission):
        document.file.delete()
        document.delete()
        messages.success(request, 'Document deleted successfully.')
    else:
        messages.error(request, 'You do not have permission to delete this document.')
    
    return redirect('submission:submission_review', submission_id=submission_id)

@login_required
def version_history(request, submission_id):
    """View version history of a submission."""
    submission = get_object_or_404(Submission, pk=submission_id)
    
    if not submission.can_user_view(request.user):
        messages.error(request, "You don't have permission to view this submission.")
        return redirect('submission:dashboard')

    # Get all versions from version history ordered by version number
    histories = list(VersionHistory.objects.filter(
        submission=submission
    ).order_by('-version'))
    
    # Add previous_version attribute to each history object
    for i in range(len(histories)):
        if i < len(histories) - 1:  # If not the last item
            histories[i].previous_version = histories[i + 1].version
        else:
            histories[i].previous_version = None
    
    # Check for pending forms for this user
    pending_forms = submission.get_pending_investigator_forms(request.user)
    show_form_alert = len(pending_forms) > 0
    
    # Get form status for all team members
    form_status = submission.get_investigator_form_status()
    
    # Get decision messages - using sent_at instead of created_at
    decision_messages = Message.objects.filter(
        related_submission=submission,
        message_type='decision'
    ).select_related(
        'sender__userprofile'
    ).order_by('-sent_at')  # Changed from created_at to sent_at

    return render(request, 'submission/version_history.html', {
        'submission': submission,
        'histories': histories,
        'pending_forms': pending_forms,
        'show_form_alert': show_form_alert,
        'form_status': form_status,
        'can_submit': submission.can_user_submit(request.user),
        'decision_messages': decision_messages
    })

@login_required
def compare_version(request, submission_id, version1, version2):
    """Compare two versions of a submission."""
    submission = get_object_or_404(Submission, temporary_id=submission_id)
    
    # Check permission
    if not submission.can_user_view(request.user):
        messages.error(request, "You don't have permission to view this submission.")
        return redirect('submission:dashboard')
    
    # Get data for both versions
    data_version1 = FormDataEntry.get_version_data(submission, version1)
    data_version2 = FormDataEntry.get_version_data(submission, version2)
    
    # Combine all form IDs from both versions
    all_form_ids = set(data_version1.keys()) | set(data_version2.keys())
    
    comparison_data = []
    for form_id in all_form_ids:
        form_v1 = data_version1.get(form_id, {'fields': {}})
        form_v2 = data_version2.get(form_id, {'fields': {}})
        
        # Get all fields from both versions
        all_fields = set(form_v1['fields'].keys()) | set(form_v2['fields'].keys())
        
        changes = []
        for field in sorted(all_fields):
            v1_value = form_v1['fields'].get(field, 'Not provided')
            v2_value = form_v2['fields'].get(field, 'Not provided')
            
            # Only include if values are different
            if v1_value != v2_value:
                changes.append({
                    'field': field,
                    'previous_value': v1_value,
                    'current_value': v2_value
                })
        
        if changes:
            form_name = (form_v1.get('form') or form_v2.get('form')).name
            comparison_data.append({
                'form_name': form_name,
                'changes': changes
            })
    
    return render(request, 'submission/compare_versions.html', {
        'submission': submission,
        'previous_version': version1,
        'version': version2,
        'comparison_data': comparison_data
    })


@login_required
def download_submission_pdf(request, submission_id, version=None):
    """Generate and download PDF version of a submission."""
    try:
        submission = get_object_or_404(Submission, pk=submission_id)
        
        # Check if user is OSAR/IRB/RC member or has direct permission
        is_admin = request.user.groups.filter(name__in=['OSAR', 'IRB', 'RC']).exists()
        has_permission = (
            is_admin or 
            has_edit_permission(request.user, submission)
        )
        
        if not has_permission:
            messages.error(request, "You do not have permission to view this submission.")
            return redirect('submission:dashboard')

        # If version is not specified, use version 1 for new submissions
        if version is None:
            # If submission.version is 2, it means we just submitted version 1
            version = submission.version 
            print(f"Version is {version}")
            
        logger.info(f"Generating PDF for submission {submission_id} version {version}")

        # Check if form entries exist for this version
        form_entries = FormDataEntry.objects.filter(
            submission=submission,
            version=version
        )
        
        if not form_entries.exists():
            logger.warning(f"No form entries found for version {version}, checking version 1")
            # Try version 1 as fallback
            version = 1
            form_entries = FormDataEntry.objects.filter(
                submission=submission,
                version=version
            )

        # Generate PDF
        response = generate_submission_pdf(
            submission=submission,
            version=version,
            user=request.user,
            as_buffer=False
        )
        
        if response is None:
            messages.error(request, "Error generating PDF. Please try again later.")
            logger.error(f"PDF generation failed for submission {submission_id} version {version}")
            return redirect('submission:dashboard')
            
        return response

    except Exception as e:
        logger.error(f"Error in download_submission_pdf: {str(e)}")
        logger.error("Error details:", exc_info=True)
        messages.error(request, "An error occurred while generating the PDF.")
        return redirect('submission:dashboard')

@login_required
def update_coinvestigator_order(request, submission_id):
    """Update the order of co-investigators in a submission."""
    if request.method == 'POST':
        submission = get_object_or_404(Submission, pk=submission_id)
        if not has_edit_permission(request.user, submission):
            return JsonResponse({'error': 'Permission denied'}, status=403)
        
        try:
            order = json.loads(request.POST.get('order', '[]'))
            for index, coinvestigator_id in enumerate(order):
                CoInvestigator.objects.filter(
                    id=coinvestigator_id,
                    submission=submission
                ).update(order=index)
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def user_autocomplete(request):
    term = request.GET.get('term', '').strip()
    submission_id = request.GET.get('submission_id')
    user_type = request.GET.get('user_type')  # 'investigator', 'assistant', or 'coinvestigator'
    
    if len(term) < 2:
        return JsonResponse([], safe=False)

    # Start with base user query
    users = User.objects.filter(
        Q(userprofile__full_name__icontains=term) |
        Q(first_name__icontains=term) |
        Q(last_name__icontains=term) |
        Q(email__icontains=term)
    )

    if submission_id:
        submission = get_object_or_404(Submission, pk=submission_id)
        
        # Exclude users already assigned to this submission in any role
        excluded_users = []
        
        # Exclude primary investigator
        if submission.primary_investigator:
            excluded_users.append(submission.primary_investigator.id)
        
        # Exclude research assistants
        assistant_ids = ResearchAssistant.objects.filter(
            submission=submission
        ).values_list('user_id', flat=True)
        excluded_users.extend(assistant_ids)
        
        # Exclude co-investigators
        coinvestigator_ids = CoInvestigator.objects.filter(
            submission=submission
        ).values_list('user_id', flat=True)
        excluded_users.extend(coinvestigator_ids)

        users = users.exclude(id__in=excluded_users)

    users = users.distinct()[:10]

    results = [
        {
            'id': user.id,
            'label': f"{user.userprofile.full_name or user.get_full_name()} ({user.email})"
        }
        for user in users
    ]

    return JsonResponse(results, safe=False)

@login_required
def submission_autocomplete(request):
    """View for handling submission autocomplete requests"""
    term = request.GET.get('term', '')
    user = request.user
    
    # Query submissions that the user has access to
    submissions = Submission.objects.filter(
        Q(primary_investigator=user) |
        Q(coinvestigators__user=user) |
        Q(research_assistants__user=user),
        Q(title__icontains=term) |
        Q(khcc_number__icontains=term)
    ).distinct()[:10]

    results = []
    for submission in submissions:
        label = f"{submission.title}"
        if submission.khcc_number:
            label += f" (IRB: {submission.khcc_number})"
        results.append({
            'id': submission.temporary_id,
            'text': label
        })

    return JsonResponse({'results': results}, safe=False)




@login_required
def submission_detail(request, submission_id):
    submission = get_object_or_404(Submission, id=submission_id)
    versions = submission.version_histories.all()
    return render(request, 'submission/submission_detail.html', {
        'submission': submission,
        'versions': versions
    })

@login_required
def view_version(request, submission_id, version_number):
    """View a specific version of a submission."""
    submission = get_object_or_404(Submission, pk=submission_id)
    
    # Check permissions
    if not has_edit_permission(request.user, submission):
        messages.error(request, "You do not have permission to view this submission.")
        return redirect('submission:dashboard')

    # Check if version exists
    version_history = get_object_or_404(
        VersionHistory, 
        submission=submission, 
        version=version_number
    )

    # Get form data for this version
    form_data = {}
    for form in submission.study_type.forms.all():
        entries = FormDataEntry.objects.filter(
            submission=submission,
            form=form,
            version=version_number
        ).select_related('form')
        
        form_data[form.name] = {
            'form': form,
            'entries': {entry.field_name: entry.value for entry in entries}
        }

    # Get documents that existed at this version
    # You might need to adjust this depending on how you track document versions
    documents = submission.documents.filter(
        uploaded_at__lte=version_history.date
    )

    context = {
        'submission': submission,
        'version_number': version_number,
        'version_history': version_history,
        'form_data': form_data,
        'documents': documents,
        'is_current_version': version_number == submission.version,
    }
    
    return render(request, 'submission/view_version.html', context)


@login_required
def investigator_form(request, submission_id, form_id):
    """Handle investigator form submission."""
    submission = get_object_or_404(Submission, pk=submission_id)
    form = get_object_or_404(DynamicForm, pk=form_id)
    
    # Check if user is part of the research team
    if not (request.user == submission.primary_investigator or 
            submission.coinvestigators.filter(user=request.user).exists() or
            submission.research_assistants.filter(user=request.user).exists()):
        messages.error(request, "You are not authorized to submit this form.")
        return redirect('submission:dashboard')
    
    # Check if form should be filled by this user
    if not form.requested_per_investigator:
        messages.error(request, "This form is not required for individual submission.")
        return redirect('submission:dashboard')
    
    # Check if form is already submitted for this version
    existing_submission = InvestigatorFormSubmission.objects.filter(
        submission=submission,
        form=form,
        investigator=request.user,
        version=submission.version
    ).first()

    if existing_submission and not request.GET.get('view'):
        messages.info(request, "You have already submitted this form for the current version.")
        return redirect('submission:version_history', submission_id=submission.temporary_id)

    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'submit_form':
            form_class = generate_django_form(form)
            form_instance = form_class(request.POST)
            
            if form_instance.is_valid():
                try:
                    with transaction.atomic():
                        # Save form data
                        for field_name, value in form_instance.cleaned_data.items():
                            FormDataEntry.objects.create(
                                submission=submission,
                                form=form,
                                field_name=field_name,
                                value=value,
                                version=submission.version
                            )
                        
                        # Record form submission
                        InvestigatorFormSubmission.objects.create(
                            submission=submission,
                            form=form,
                            investigator=request.user,
                            version=submission.version
                        )

                        # Check if all forms are complete and update status if needed
                        if submission.are_all_investigator_forms_complete():
                            # Update submission status if it was pending documents
                            if submission.status == 'document_missing':
                                submission.status = 'submitted'
                                submission.save()
                                notify_form_completion(submission)
                                notify_osar_of_completion(submission)

                        messages.success(request, f"Form '{form.name}' submitted successfully.")
                        return redirect('submission:version_history', submission_id=submission.temporary_id)
                        
                except Exception as e:
                    logger.error(f"Error saving investigator form: {str(e)}")
                    messages.error(request, "An error occurred while saving your form.")
            else:
                messages.error(request, "Please correct the errors in the form.")
        
        elif action == 'back':
            return redirect('submission:version_history', submission_id=submission.temporary_id)
    else:
        # If viewing existing submission, populate with saved data
        if existing_submission:
            initial_data = {}
            saved_entries = FormDataEntry.objects.filter(
                submission=submission,
                form=form,
                version=submission.version
            )
            for entry in saved_entries:
                initial_data[entry.field_name] = entry.value
            form_class = generate_django_form(form)
            form_instance = form_class(initial=initial_data)
            form_instance.is_viewing = True  # Flag to make form read-only in template
        else:
            form_class = generate_django_form(form)
            form_instance = form_class()

    context = {
        'form': form_instance,
        'dynamic_form': form,
        'submission': submission,
        'is_viewing': request.GET.get('view') == 'true' or (existing_submission and not form.allow_updates),
        'existing_submission': existing_submission
    }
    
    return render(request, 'submission/investigator_form.html', context)

def notify_form_completion(submission):
    """Notify research team when all forms are complete."""
    system_user = get_system_user()
    
    # Get all team members
    recipients = []
    recipients.append(submission.primary_investigator)
    recipients.extend([ci.user for ci in submission.coinvestigators.all()])
    recipients.extend([ra.user for ra in submission.research_assistants.all()])
    
    # Create notification message
    message = Message.objects.create(
        sender=system_user,
        subject=f'All Required Forms Completed - {submission.title}',
        body=f"""
All required investigator forms have been completed for:

Submission ID: {submission.temporary_id}
Title: {submission.title}

The submission status has been updated to "Submitted" and is now under review.

Best regards,
AIDI System
        """.strip(),
        related_submission=submission
    )
    
    # Add recipients
    for recipient in recipients:
        message.recipients.add(recipient)


@login_required
def check_form_status(request, submission_id):
    """AJAX endpoint to check form completion status."""
    submission = get_object_or_404(Submission, pk=submission_id)
    
    if not submission.can_user_view(request.user):
        return JsonResponse({'error': 'Permission denied'}, status=403)
        
    # Get pending forms for the current user
    pending_forms = submission.get_pending_investigator_forms(request.user)
    
    # Get overall form status
    form_status = submission.get_investigator_form_status()
    all_complete = submission.are_all_investigator_forms_complete()
    
    return JsonResponse({
        'pending_forms': [
            {'id': form.id, 'name': form.name} 
            for form in pending_forms
        ],
        'form_status': form_status,
        'all_complete': all_complete
    })

@login_required
def archive_submission(request, submission_id):
    """Archive a submission."""
    submission = get_object_or_404(Submission, temporary_id=submission_id)
    if request.method == 'POST':
        try:
            submission.is_archived = True
            submission.archived_at = timezone.now()
            submission.save(update_fields=['is_archived', 'archived_at'])
            messages.success(request, f'Submission "{submission.title}" has been archived.')
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)

@login_required
def unarchive_submission(request, submission_id):
    """Unarchive a submission."""
    submission = get_object_or_404(Submission, temporary_id=submission_id)
    if request.method == 'POST':
        try:
            submission.is_archived = False
            submission.archived_at = None
            submission.save(update_fields=['is_archived', 'archived_at'])
            messages.success(request, f'Submission "{submission.title}" has been unarchived.')
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)

@login_required
def archived_dashboard(request):
    """Display archived submissions dashboard."""
    submissions = Submission.objects.filter(
        is_archived=True
    ).select_related(
        'primary_investigator__userprofile'
    ).order_by('-date_created')

    return render(request, 'submission/archived_dashboard.html', {
        'submissions': submissions,
    })

@login_required
def view_submission(request, submission_id):
    """View submission details."""
    submission = get_object_or_404(Submission, temporary_id=submission_id)
    if not has_edit_permission(request.user, submission):
        messages.error(request, "You do not have permission to view this submission.")
        return redirect('submission:dashboard')
        
    context = {
        'submission': submission,
        'versions': submission.version_histories.all().order_by('-version'),
    }
    return render(request, 'submission/view_submission.html', context)


# Add to views.py
# submission/views.py


@login_required
def handle_study_action_form(request, submission_id, form_name, action_type):
    """Generic handler for study action forms"""
    submission = get_object_or_404(Submission, pk=submission_id)
    
    # Check permissions
    if not (request.user == submission.primary_investigator or 
            submission.coinvestigators.filter(user=request.user, can_submit=True).exists() or
            submission.research_assistants.filter(user=request.user, can_submit=True).exists()):
        messages.error(request, "You don't have permission to perform this action.")
        return redirect('submission:version_history', submission_id=submission.temporary_id)
    
    # Get the dynamic form
    try:
        dynamic_form = DynamicForm.objects.get(name=form_name)
    except DynamicForm.DoesNotExist:
        messages.error(request, f"Required form '{form_name}' not found.")
        return redirect('submission:version_history', submission_id=submission.temporary_id)

    if request.method == 'POST':
        # Check for exit without save action first
        if request.POST.get('action') == 'exit_no_save':
            return redirect('submission:submission_actions', submission_id=submission.temporary_id)
            
        form_class = generate_django_form(dynamic_form)
        form = form_class(request.POST)
        
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Create study action record
                    study_action = StudyAction.objects.create(
                        submission=submission,
                        action_type=action_type,
                        performed_by=request.user,
                        status='completed'
                    )
                    
                    # Save form data and associate with the study action
                    for field_name, value in form.cleaned_data.items():
                        FormDataEntry.objects.create(
                            submission=submission,
                            form=dynamic_form,
                            field_name=field_name,
                            value=value,
                            version=submission.version,
                            study_action=study_action  # Associate with the action
                        )
                    
                    # Handle specific actions
                    if action_type == 'withdrawal':
                        submission.status = 'withdrawn'
                        submission.is_locked = True
                        action_msg = "Study has been withdrawn"
                    elif action_type == 'closure':
                        submission.status = 'closed'
                        submission.is_locked = True
                        action_msg = "Study has been closed"
                    elif action_type == 'progress':
                        action_msg = "Progress report submitted"
                    elif action_type == 'amendment':
                        action_msg = "Amendment submitted"
                    
                    submission.save()
                    
                    # Send notifications
                    system_user = get_system_user()
                    
                    # Notify OSAR
                    osar_message = Message.objects.create(
                        sender=system_user,
                        subject=f"{action_type.title()} - {submission.title}",
                        body=f"""
A {action_type} has been submitted for:

Submission ID: {submission.temporary_id}
Title: {submission.title}
PI: {submission.primary_investigator.get_full_name()}
Submitted by: {request.user.get_full_name()}

Please review the submitted {action_type} form.

Best regards,
AIDI System
                        """.strip(),
                        related_submission=submission
                    )
                    
                    # Add OSAR recipients
                    osar_users = User.objects.filter(groups__name='OSAR')
                    osar_message.recipients.add(*osar_users)
                    
                    # Notify research team
                    team_message = Message.objects.create(
                        sender=system_user,
                        subject=f"{action_type.title()} - {submission.title}",
                        body=f"""
A {action_type} has been submitted for:

Submission ID: {submission.temporary_id}
Title: {submission.title}
Submitted by: {request.user.get_full_name()}

Status: {action_msg}

Best regards,
AIDI System
                        """.strip(),
                        related_submission=submission
                    )
                    
                    # Add research team recipients
                    team_recipients = [submission.primary_investigator]
                    team_recipients += [ci.user for ci in submission.coinvestigators.all()]
                    team_recipients += [ra.user for ra in submission.research_assistants.all()]
                    team_message.recipients.add(*team_recipients)

                    messages.success(request, f"{action_msg} successfully.")
                    return redirect('submission:version_history', submission_id=submission.temporary_id)
                    
            except Exception as e:
                messages.error(request, f"Error processing {action_type}: {str(e)}")
                return redirect('submission:version_history', submission_id=submission.temporary_id)
    else:
        form_class = generate_django_form(dynamic_form)
        form = form_class()

    return render(request, 'submission/dynamic_actions.html', {
        'form': form,
        'submission': submission,
        'dynamic_form': dynamic_form,
    })


@login_required
def study_withdrawal(request, submission_id):
    return handle_study_action_form(request, submission_id, 'withdrawal', 'withdrawal')

@login_required
def progress_report(request, submission_id):
    return handle_study_action_form(request, submission_id, 'progress', 'progress')

@login_required
def study_amendment(request, submission_id):
    return handle_study_action_form(request, submission_id, 'amendment', 'amendment')

@login_required
def study_closure(request, submission_id):
    return handle_study_action_form(request, submission_id, 'closure', 'closure')


@login_required
def submission_actions(request, submission_id):
    """Display available actions for a submission."""
    submission = get_object_or_404(Submission, pk=submission_id)
    
    # Check if user can submit
    can_submit = (
        request.user == submission.primary_investigator or
        submission.coinvestigators.filter(user=request.user, can_submit=True).exists() or
        submission.research_assistants.filter(user=request.user, can_submit=True).exists()
    )
    
    context = {
        'submission': submission,
        'can_submit': can_submit,
    }
    return render(request, 'submission/submission_actions.html', context)

# submission/views.py

@login_required
def download_action_pdf(request, submission_id, action_id):
    """Generate and download PDF for a specific study action."""
    try:
        submission = get_object_or_404(Submission, pk=submission_id)
        action = get_object_or_404(StudyAction, pk=action_id, submission=submission)
        
        # Check permissions
        if not submission.can_user_view(request.user):
            messages.error(request, "You do not have permission to view this submission.")
            return redirect('submission:dashboard')
        
        # Get form entries specifically for this action
        form_entries = FormDataEntry.objects.filter(
            submission=submission,
            version=action.version,
            study_action=action  # This is crucial - make sure entries are linked to this action
        ).select_related('form')
        
        logger.info(f"Found {form_entries.count()} form entries for action {action_id}")
        
        if form_entries.count() == 0:
            logger.warning(f"No form entries found for action {action_id}. Checking action details:")
            logger.warning(f"Action type: {action.action_type}")
            logger.warning(f"Action version: {action.version}")
            logger.warning(f"Action submission: {action.submission_id}")
        
        # Generate PDF
        response = generate_action_pdf(
            submission=submission,
            study_action=action,
            form_entries=form_entries,
            user=request.user
        )
        
        if response is None:
            messages.error(request, "Error generating PDF. Please try again later.")
            logger.error(f"PDF generation failed for action {action_id}")
            return redirect('submission:version_history', submission_id=submission_id)
                
        return response

    except Exception as e:
        logger.error(f"Error in download_action_pdf: {str(e)}")
        logger.error("Error details:", exc_info=True)
        messages.error(request, "An error occurred while generating the PDF.")
        return redirect('submission:version_history', submission_id=submission_id)


def notify_pending_forms(submission):
    """Notify team members of their pending forms."""
    system_user = get_system_user()
    required_forms = submission.get_required_investigator_forms()
    
    if not required_forms.exists():
        return
        
    # Get all team members who need to fill forms
    team_members = []
    team_members.extend([ci.user for ci in submission.coinvestigators.all()])
    team_members.extend([ra.user for ra in submission.research_assistants.all()])

    # For each team member, check their pending forms
    for member in team_members:
        pending_forms = []
        for form in required_forms:
            if not InvestigatorFormSubmission.objects.filter(
                submission=submission,
                form=form,
                investigator=member,
                version=submission.version
            ).exists():
                pending_forms.append(form.name)
        
        if pending_forms:
            # Create personalized notification for each member
            message = Message.objects.create(
                sender=system_user,
                subject=f'Required Forms for Submission - {submission.title}',
                body=f"""
Dear {member.get_full_name()},

You have pending forms to complete for:

Submission ID: {submission.temporary_id}
Title: {submission.title}
Primary Investigator: {submission.primary_investigator.get_full_name()}

Required Forms:
{chr(10).join('- ' + form for form in pending_forms)}

Please log in to complete these forms at your earliest convenience. The submission cannot proceed until all required forms are completed.

Best regards,
AIDI System
                """.strip(),
                related_submission=submission
            )
            message.recipients.add(member)

    # Notify PI about pending forms
    pi_message = Message.objects.create(
        sender=system_user,
        subject=f'Submission Status - {submission.title}',
        body=f"""
Dear {submission.primary_investigator.get_full_name()},

Your submission (ID: {submission.temporary_id}) has been processed, but some team members need to complete required forms.

The submission will be marked as "Submitted" and sent for review once all forms are completed.

Best regards,
AIDI System
        """.strip(),
        related_submission=submission
    )
    pi_message.recipients.add(submission.primary_investigator)

def notify_osar_of_completion(submission):
    """Notify OSAR when all forms are complete and submission is ready for review."""
    system_user = get_system_user()
    osar_members = User.objects.filter(groups__name='OSAR')
    
    if not osar_members.exists():
        logger.warning("No OSAR members found for notification")
        return
        
    # Generate PDF of the submission
    try:
        buffer = generate_submission_pdf(
            submission=submission,
            version=submission.version,
            user=None,  # You can specify a user if required
            as_buffer=True
        )
        if not buffer:
            raise ValueError("Failed to generate PDF for submission")
    except Exception as e:
        logger.error(f"Failed to generate PDF for submission {submission.temporary_id}: {str(e)}")
        buffer = None
        
    # Create notification message
    message = Message.objects.create(
        sender=system_user,
        subject=f'Submission Ready for Review - {submission.title}',
        body=f"""
A submission has completed all required forms and is ready for review:

Submission ID: {submission.temporary_id}
Title: {submission.title}
Primary Investigator: {submission.primary_investigator.get_full_name()}
Study Type: {submission.study_type.name}
Date Submitted: {timezone.now().strftime('%Y-%m-%d %H:%M')}

The submission is now ready for your review.

Best regards,
AIDI System
        """.strip(),
        related_submission=submission
    )
    
    # Attach PDF if generated successfully
    if buffer:
        pdf_filename = f"submission_{submission.temporary_id}_v{submission.version}.pdf"
        message_attachment = MessageAttachment(message=message)
        message_attachment.file.save(pdf_filename, ContentFile(buffer.getvalue()))
    
    # Add OSAR members as recipients
    for member in osar_members:
        message.recipients.add(member)

