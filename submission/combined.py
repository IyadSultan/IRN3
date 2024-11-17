# Combined Python and HTML files
# Generated from directory: C:\Users\USER\Documents\IRN3\submission
# Total files found: 53



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
                                <i class="fas fa-arrow-left"></i> Back
                            </button>
                            <button type="submit" name="action" value="exit_no_save" class="btn btn-danger me-md-2" formnovalidate>
                                <i class="fas fa-times"></i> Exit without Saving
                            </button>
                            <button type="submit" name="action" value="save_exit" class="btn btn-primary me-md-2">
                                <i class="fas fa-save"></i> Save and Exit
                            </button>
                            <button type="submit" name="action" value="save_add_another" class="btn btn-info me-md-2">
                                <i class="fas fa-plus"></i> Add Co-investigator
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
{% extends 'users/base.html' %}
{% load crispy_forms_tags %}

{% block title %}Add Research Assistant{% endblock %}

{% block page_specific_css %}
<style>
    /* Any additional page-specific styles */
    .badge {
        margin-right: 5px;
    }
    
    .table td {
        vertical-align: middle;
    }
</style>
{% endblock %}

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
                            <th>Actions</th>
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
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
            {% endif %}

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
                    <th>IRB Number</th>
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
                    <td>{{ submission.irb_number|default:"N/A" }}</td>
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
                        <a href="{% url 'submission:view_submission' submission.temporary_id %}" 
                           class="btn btn-sm btn-secondary" 
                           title="View Submission">
                            <i class="fas fa-eye"></i>
                        </a>
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
                                        <th style="width: 35%">Previous Value (v{{ previous_version }})</th>
                                        <th style="width: 35%">Current Value (v{{ version }})</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {% for change in form_data.changes %}
                                        <tr>
                                            <td class="fw-bold">{{ change.field }}</td>
                                            <td class="bg-light-yellow">
                                                {{ change.previous_value }}
                                            </td>
                                            <td class="bg-light-green">
                                                {{ change.current_value }}
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
</style>
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

    <div class="card">
        <div class="card-body">
            <div class="table-responsive">
                <table id="submissionsTable" class="table table-hover">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>IRB Number</th>
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
                            <td>{{ submission.irb_number|default:"N/A" }}</td>
                            <td>{{ submission.title|default:"" }}</td>
                            <td>{{ submission.primary_investigator.userprofile.full_name }}</td>
                            <td>
                                <span class="badge badge-{{ submission.status|lower }}">
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
                                    <a href="{% url 'submission:version_history' submission.temporary_id %}" 
                                       class="btn btn-sm btn-info" 
                                       title="Version History">
                                        <i class="fas fa-history"></i>
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

{% block extra_css %}
<style>
    .btn-group {
        gap: 0.5rem;
    }
    
    .status-badge {
        padding: 5px 10px;
        border-radius: 15px;
        font-size: 0.9em;
    }
    
    .status-badge i {
        margin-right: 5px;
    }

    .table td {
        vertical-align: middle;
    }

    .btn-sm {
        padding: 0.25rem 0.5rem;
    }
</style>
{% endblock %}

# Contents from: .\templates\submission\dynamic_form.html
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
                <!-- Or use {{ form.as_p }} if not using crispy_forms -->
                <div class="d-grid gap-2 d-md-flex justify-content-md-start mt-4">
                    {% if previous_form %}
                    <button type="submit" name="action" value="back" class="btn btn-secondary me-md-2">
                        <i class="fas fa-arrow-left"></i> Back
                    </button>
                    {% endif %}
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
{% if missing_documents %}
<div class="alert alert-warning">
    <h4 class="alert-heading">Missing or Expired Documents</h4>
    {% for role, info in missing_documents.items %}
    <div class="mb-3">
        <strong>{{ role }}: {{ info.name }}</strong>
        <ul>
            {% for doc in info.documents %}
            <li>{{ doc }}</li>
            {% endfor %}
        </ul>
    </div>
    {% endfor %}
</div>
{% endif %} 

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

        // Toggle PI field visibility
        function togglePIField() {
            if ($('#id_is_primary_investigator').is(':checked')) {
                $('#div_id_primary_investigator').hide();
            } else {
                $('#div_id_primary_investigator').show();
            }
        }

        $('#id_is_primary_investigator').change(togglePIField);
        togglePIField();
    });
</script>
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
<!-- submission/review.html -->

{% extends 'users/base.html' %}
{% load crispy_forms_tags %}

{% block content %}
<div class="container mt-4">
    <h1>Submission Review</h1>

    <!-- Primary Investigator Documents Check -->
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

    <!-- Co-Investigators Documents Check -->
    {% if submission.coinvestigator_set.exists %}
    <div class="card mb-4">
        <div class="card-header">
            <h4>Co-Investigators Documents</h4>
        </div>
        <div class="card-body">
            {% for coinv in submission.coinvestigator_set.all %}
            <div class="mb-4">
                <h6>{{ coinv.user.get_full_name }} - {{ coinv.role_in_study }}</h6>
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
                    {% if profile.role == 'KHCC investigator' %}
                    <li class="list-group-item {% if profile.has_qrc %}list-group-item-success{% else %}list-group-item-danger{% endif %}">
                        <i class="fas {% if profile.has_qrc %}fa-check{% else %}fa-times{% endif %}"></i>
                        QRC Certificate
                    </li>
                    <li class="list-group-item {% if profile.has_ctc %}list-group-item-success{% else %}list-group-item-danger{% endif %}">
                        <i class="fas {% if profile.has_ctc %}fa-check{% else %}fa-times{% endif %}"></i>
                        CTC Certificate
                    </li>
                    {% endif %}
                </ul>
                {% endwith %}
            </div>
            {% endfor %}
        </div>
    </div>
    {% endif %}

    <!-- Research Assistants Documents Check -->
    {% if submission.researchassistant_set.exists %}
    <div class="card mb-4">
        <div class="card-header">
            <h4>Research Assistants Documents</h4>
        </div>
        <div class="card-body">
            {% for ra in submission.researchassistant_set.all %}
            <div class="mb-4">
                <h6>{{ ra.user.get_full_name }}</h6>
                {% with profile=ra.user.userprofile %}
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
                    {% if profile.role == 'Research Assistant/Coordinator' %}
                    <li class="list-group-item {% if profile.has_ctc %}list-group-item-success{% else %}list-group-item-danger{% endif %}">
                        <i class="fas {% if profile.has_ctc %}fa-check{% else %}fa-times{% endif %}"></i>
                        CTC Certificate
                    </li>
                    {% endif %}
                </ul>
                {% endwith %}
            </div>
            {% endfor %}
        </div>
    </div>
    {% endif %}

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
                <td>{{ doc.file.name|slice:"documents/" }}</td>
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

    <!-- Action Buttons -->
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

    <!-- Loading Indicator -->
    <div id="loadingIndicator" style="display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0, 0, 0, 0.5); z-index: 9999;">
        <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); background: white; padding: 20px; border-radius: 8px; text-align: center;">
            <div class="spinner-border text-primary" role="status" style="width: 3rem; height: 3rem;">
                <span class="visually-hidden">Loading...</span>
            </div>
            <p class="mt-3 mb-0">I am thinking...</p>
        </div>
    </div>
    <p></p>
    <!-- KHCC Brain Analysis -->
    <div class="card mb-4">
        <div class="card-header">
            <h4>KHCC Brain Analysis</h4>
        </div>
        <div class="card-body">
            <form method="post" id="analysisForm">
                {% csrf_token %}
                <button type="submit" name="action" value="analyze_submission" class="btn btn-primary mb-3">
                    <i class="fas fa-brain"></i> Analyze Submission
                </button>
            </form>
            
            {% if gpt_analysis %}
            <div class="analysis-result markdown-body">
                {{ gpt_analysis|safe }}
            </div>
            {% endif %}
        </div>
    </div>
</div>

<script>
document.addEventListener('DOMContentLoaded', function() {
    const finalSubmitForm = document.querySelector('form:last-of-type');
    finalSubmitForm.addEventListener('submit', function(e) {
        if (e.target.querySelector('button[name="action"]').value === 'submit_final') {
            const hasMissingDocs = {% if missing_documents %}true{% else %}false{% endif %};
            const hasValidationErrors = {% if validation_errors %}true{% else %}false{% endif %};
            const invalidCertificates = document.querySelectorAll('.list-group-item-danger');
            const hasInvalidCertificates = invalidCertificates.length > 0;

            if (hasMissingDocs || hasValidationErrors || hasInvalidCertificates) {
                e.preventDefault();
                alert('Cannot submit: Please ensure all mandatory fields are filled and all certificates are valid.');
                return false;
            }
        }
    });

    // Loading indicator for analysis
    const analysisForm = document.getElementById('analysisForm');
    const loadingIndicator = document.getElementById('loadingIndicator');

    if (analysisForm && loadingIndicator) {
        analysisForm.addEventListener('submit', function(e) {
            console.log('Analysis form submitted');  // Debug log
            loadingIndicator.style.display = 'block';
        });
    } else {
        console.error('Analysis form or loading indicator not found');  // Debug log
    }
});
</script>

{% endblock %}

# Contents from: .\templates\submission\version_history.html
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
                                <span class="badge bg-{{ history.status|lower }}">
                                    {{ history.get_status_display }}
                                </span>
                            </td>
                            <td>{{ history.date|date:"M d, Y H:i" }}</td>
                            <td>
                                <div class="btn-group" role="group">
                                    <a href="{% url 'submission:download_submission_pdf_version' submission.temporary_id history.version %}" 
                                       class="btn btn-sm btn-secondary" 
                                       title="Download PDF">
                                        <i class="fas fa-file-pdf"></i> Download
                                    </a>
                                    
                                    {% if history.can_compare %}
                                    <a href="{% url 'submission:compare_version' submission.temporary_id history.version %}" 
                                       class="btn btn-sm btn-primary" 
                                       title="Compare with Previous Version">
                                        <i class="fas fa-code-compare"></i> Compare Changes
                                    </a>
                                    {% endif %}
                                </div>
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
            
            {% if submission.get_required_investigator_forms %}
            <div class="card mt-4">
                <div class="card-header">
                    <h4>Required Investigator Forms</h4>
                </div>
                <div class="card-body">
                    {% with form_status=submission.get_investigator_form_status %}
                    {% if form_status %}
                        {% for form_name, status in form_status.items %}
                        <h5 class="mb-3">{{ form_name }}</h5>
                        <table class="table table-striped">
                            <thead>
                                <tr>
                                    <th>Investigator</th>
                                    <th>Role</th>
                                    <th>Status</th>
                                    <th>Submission Date</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for inv in status.investigators %}
                                <tr>
                                    <td>{{ inv.user.get_full_name }}</td>
                                    <td>{{ inv.role }}</td>
                                    <td>
                                        {% if inv.submitted %}
                                            <span class="badge bg-success">
                                                <i class="fas fa-check"></i> Submitted
                                            </span>
                                        {% else %}
                                            <span class="badge bg-danger">
                                                <i class="fas fa-times"></i> Pending
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
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                        {% endfor %}
                    {% else %}
                        <p class="text-muted">No form submissions required for this version.</p>
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
                    <p><strong>IRB Number:</strong> {{ submission.irb_number|default:"N/A" }}</p>
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

@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('temporary_id', 'title', 'primary_investigator', 'irb_number', 'status', 'date_created', 'is_locked')
    search_fields = ('title', 'primary_investigator__username', 'irb_number')
    list_filter = ('status', 'study_type', 'is_locked')
    ordering = ('-date_created',)
    fields = ('title', 'study_type', 'primary_investigator', 'irb_number', 'status', 'date_created', 'last_modified', 'is_locked')
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
            
        # Filter out study types that start with IRB/irb
        study_type_field = self.fields['study_type']
        study_type_field.queryset = study_type_field.queryset.exclude(
            Q(name__istartswith='irb')
        )

from django import forms
from django.contrib.auth.models import User
from .models import ResearchAssistant, Submission  # Import all needed models

from django import forms
from django.contrib.auth.models import User
from users.models import Role
from .models import ResearchAssistant, CoInvestigator, Submission

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
    class Meta:
        model = Document
        fields = ['file', 'description']
        widgets = {
            'description': forms.TextInput(attrs={'class': 'form-control'}),
        }

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

import submission.models
from django.db import migrations, models


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
                choices=submission.models.get_status_choices,
                default="draft",
                max_length=50,
            ),
        ),
        migrations.AlterField(
            model_name="versionhistory",
            name="status",
            field=models.CharField(
                choices=submission.models.get_status_choices, max_length=50
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
                choices=submission.models.get_status_choices, max_length=50
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

def get_status_choices():
    DEFAULT_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        
        
    ]
    
    try:
        choices = cache.get('status_choices')
        if not choices:
            StatusChoice = apps.get_model('submission', 'StatusChoice')
            choices = list(StatusChoice.objects.filter(is_active=True).values_list('code', 'label'))
            if choices:
                cache.set('status_choices', choices)
        return choices or DEFAULT_CHOICES
    except (OperationalError, LookupError):
        return DEFAULT_CHOICES

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
    irb_number = models.CharField(max_length=20, blank=True, null=True, unique=True)
    title = models.CharField(max_length=255)
    primary_investigator = models.ForeignKey(
        User, related_name='primary_investigations', on_delete=models.CASCADE
    )
    study_type = models.ForeignKey(StudyType, on_delete=models.SET_NULL, null=True)
    status = models.CharField(
        max_length=50,
        choices=get_status_choices,
        default='draft'
    )
    date_created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    date_submitted = models.DateTimeField(blank=True, null=True)
    version = models.PositiveIntegerField(default=1)
    is_locked = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)
    archived_at = models.DateTimeField(null=True, blank=True)

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

    def __str__(self):
        return f"{self.title} (ID: {self.temporary_id}, Version: {self.version})"

    def increment_version(self):
        VersionHistory.objects.create(submission=self, version=self.version, status=self.status, date=timezone.now())
        self.version += 1

    def get_required_investigator_forms(self):
        """Get all forms that require per-investigator submission."""
        return self.study_type.forms.filter(requested_per_investigator=True)

    def get_pending_investigator_forms(self, user):
        """Get forms that still need to be filled by an investigator."""
        required_forms = self.get_required_investigator_forms()
        submitted_forms = InvestigatorFormSubmission.objects.filter(
            submission=self,
            investigator=user,
            version=self.version
        ).values_list('form_id', flat=True)
        return required_forms.exclude(id__in=submitted_forms)

    def get_investigator_form_status(self):
        """Get completion status of all investigator forms."""
        required_forms = self.get_required_investigator_forms()
        if not required_forms.exists():
            return {}

        investigators = list(self.coinvestigators.all())
        investigators.append({'user': self.primary_investigator, 'role': 'Primary Investigator'})

        status = {}
        for form in required_forms:
            form_submissions = InvestigatorFormSubmission.objects.filter(
                submission=self,
                form=form,
                version=self.version
            ).select_related('investigator')

            submitted_users = {sub.investigator_id: sub.date_submitted for sub in form_submissions}
            
            # For the PI, if they submitted the submission, consider their forms complete
            if self.date_submitted and self.status == 'submitted':
                submitted_users.setdefault(
                    self.primary_investigator.id, 
                    self.date_submitted
                )

            status[form.name] = {
                'form': form,
                'investigators': [
                    {
                        'user': inv['user'] if isinstance(inv, dict) else inv.user,
                        'role': inv['role'] if isinstance(inv, dict) else 'Co-Investigator',
                        'submitted': submitted_users.get(
                            inv['user'].id if isinstance(inv, dict) else inv.user.id
                        ),
                        'is_pi': (inv['user'] if isinstance(inv, dict) else inv.user) == self.primary_investigator
                    }
                    for inv in investigators
                ]
            }
        return status

    def are_all_investigator_forms_complete(self):
        """Check if all investigators have completed their required forms."""
        required_forms = self.get_required_investigator_forms()
        if not required_forms.exists():
            return True

        investigators = list(self.coinvestigators.all().values_list('user_id', flat=True))
        # Don't include PI in check as their forms are auto-completed
        
        for form in required_forms:
            submitted_users = InvestigatorFormSubmission.objects.filter(
                submission=self,
                form=form,
                version=self.version
            ).values_list('investigator_id', flat=True)
            if not set(investigators).issubset(set(submitted_users)):
                return False
        return True
        
        

from django.db import models
from django.contrib.auth.models import User
from users.models import Role  # Add this import

class CoInvestigator(models.Model):
    submission = models.ForeignKey(
        'Submission', 
        related_name='coinvestigators',
        on_delete=models.CASCADE
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    roles = models.JSONField(default=list)  # Changed from ManyToManyField to JSONField
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

from django.db import models
from django.contrib.auth.models import User

class ResearchAssistant(models.Model):
    submission = models.ForeignKey(
        'Submission',
        related_name='research_assistants',  # Add this related_name
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

class FormDataEntry(models.Model):
    submission = models.ForeignKey(
        Submission, related_name='form_data_entries', on_delete=models.CASCADE
    )
    form = models.ForeignKey(DynamicForm, on_delete=models.CASCADE)
    field_name = models.CharField(max_length=255)
    value = models.TextField()
    date_saved = models.DateTimeField(auto_now=True)
    version = models.PositiveIntegerField(default=1)

    class Meta:
        indexes = [
            models.Index(fields=['submission', 'form', 'field_name']),
        ]

    def __str__(self):
        return f"{self.submission} - {self.form.name} - {self.field_name}"

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
        Submission, related_name='version_histories', on_delete=models.CASCADE
    )
    version = models.PositiveIntegerField()
    status = models.CharField(
        max_length=50,
        choices=get_status_choices
    )
    date = models.DateTimeField()

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
            irb_number='IRB123',
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
    path('compare-version/<int:submission_id>/<int:version>/', views.compare_version, name='compare_version'),
    path('investigator-form/<int:submission_id>/<int:form_id>/', views.investigator_form, name='investigator_form'),
    path('check-form-status/<int:submission_id>/', views.check_form_status, name='check_form_status'),
    path('archived/', views.archived_dashboard, name='archived_dashboard'),
    path('archive/<int:submission_id>/', views.archive_submission, name='archive_submission'),
    path('unarchive/<int:submission_id>/', views.unarchive_submission, name='unarchive_submission'),
    path('view/<int:submission_id>/', views.view_submission, name='view_submission'),
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
    """Check if all required documents are present for researchers."""
    missing_documents = []
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
    return submission.study_type.forms.filter(
        order__lt=current_form.order
    ).order_by('-order').first()

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
            f"IRB Number: {self.submission.irb_number or 'Not provided'}",
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
            self.y -= self.line_height/2
            self.write_wrapped_text("Co-Investigators:")
            for ci in co_investigators:
                # Get all roles for this co-investigator
                roles = ", ".join([role.name for role in ci.roles.all()])
                
                # Add permissions to roles if they exist
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
                    co_inv_info += f" (Roles: {roles})"
                if permissions:
                    co_inv_info += f" [Permissions: {', '.join(permissions)}]"
                
                self.write_wrapped_text(co_inv_info, x_offset=20)

        # Research Assistants with their permissions
        research_assistants = self.submission.research_assistants.all()
        if research_assistants:
            self.y -= self.line_height/2
            self.write_wrapped_text("Research Assistants:")
            for ra in research_assistants:
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

    def generate(self):
        """Generate the complete PDF"""
        self.add_header()
        self.add_basic_info()
        self.add_research_team()
        self.add_dynamic_forms()
        self.add_documents()
        self.add_footer()
        self.canvas.save()


def generate_submission_pdf(submission, version, user, as_buffer=False):
    """Generate PDF for a submission"""
    try:
        if version is None:
            logger.error("Version cannot be None")
            return None
            
        logger.info(f"Generating PDF for submission {submission.temporary_id} version {version}")
        
        # Check if there's any form data for this version
        form_entries = FormDataEntry.objects.filter(
            submission=submission,
            version=version
        )
        
        if not form_entries.exists():
            logger.warning(f"No form entries found for submission {submission.temporary_id} version {version}")
        
        buffer = BytesIO()
        pdf_generator = PDFGenerator(buffer, submission, version, user)
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
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import HttpResponse, JsonResponse
from django.core.files.base import ContentFile
from dal import autocomplete
import json
from io import BytesIO
from .utils import PDFGenerator, has_edit_permission, check_researcher_documents, get_next_form, get_previous_form
from .utils.pdf_generator import generate_submission_pdf
from .gpt_analysis import ResearchAnalyzer
from django.core.cache import cache

from .models import (
    Submission,
    CoInvestigator,
    ResearchAssistant,
    FormDataEntry,
    Document,
    VersionHistory,
)
from .forms import (
    SubmissionForm,
    ResearchAssistantForm,
    CoInvestigatorForm,
    DocumentForm,
    generate_django_form,
)
from forms_builder.models import DynamicForm
from messaging.models import Message, MessageAttachment
from users.models import SystemSettings, UserProfile
from django import forms
import logging

logger = logging.getLogger(__name__)

from django.db.models import Q
from django.db import transaction
from django.contrib.auth.models import User
from django.urls import reverse

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
    from django.db.models import Max
    
    submissions = Submission.objects.filter(
        is_archived=False
    ).select_related(
        'primary_investigator__userprofile'
    ).order_by('-date_created')
    
    # Get the actual latest version for each submission from FormDataEntry
    for submission in submissions:
        latest_version = FormDataEntry.objects.filter(
            submission=submission
        ).values('version').aggregate(Max('version'))['version__max']
        submission.actual_version = latest_version or 1  # Use 1 if no entries found

    return render(request, 'submission/dashboard.html', {'submissions': submissions})

@login_required
def edit_submission(request, submission_id):
    """Redirect to start_submission with existing submission ID."""
    return redirect('submission:start_submission_with_id', submission_id=submission_id)

@login_required
def start_submission(request, submission_id=None):
    """Start or edit a submission."""
    if submission_id:
        submission = get_object_or_404(Submission, pk=submission_id)
        print(f"Found submission with PI: {submission.primary_investigator}")
        print(f"Current user: {request.user}")
        
        if submission.is_locked:
            messages.error(request, "This submission is locked and cannot be edited.")
            return redirect('submission:dashboard')
        if not has_edit_permission(request.user, submission):
            messages.error(request, "You do not have permission to edit this submission.")
            return redirect('submission:dashboard')
        
        # Only set initial data for primary_investigator, not is_primary_investigator
        initial_data = {
            'primary_investigator': submission.primary_investigator
        }
    else:
        submission = None
        initial_data = {}

    if request.method == 'POST':
        print(f"POST data: {request.POST}")
        form = SubmissionForm(request.POST, instance=submission)
        action = request.POST.get('action')
        
        if action == 'exit_no_save':
            return redirect('submission:dashboard')
            
        if form.is_valid():
            submission = form.save(commit=False)
            # Get is_pi directly from POST data instead of cleaned_data
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
                
            submission.save()
            messages.success(request, f'Temporary submission ID {submission.temporary_id} generated.')
            
            if action == 'save_exit':
                return redirect('submission:dashboard')
            elif action == 'save_continue':
                return redirect('submission:add_research_assistant', submission_id=submission.temporary_id)
    else:
        form = SubmissionForm(instance=submission, initial=initial_data)
        # Explicitly set is_primary_investigator based on current state
        if submission and submission.primary_investigator == request.user:
            form.fields['is_primary_investigator'].initial = True
        else:
            form.fields['is_primary_investigator'].initial = False

    return render(request, 'submission/start_submission.html', {
        'form': form,
        'submission': submission,
    })

from django import forms
from django.contrib.auth.models import User
from .models import ResearchAssistant  # Add this import

@login_required
def add_research_assistant(request, submission_id):
    """Add or manage research assistants for a submission."""
    submission = get_object_or_404(Submission, pk=submission_id)
    if submission.is_locked:
        messages.error(request, "This submission is locked and cannot be edited.")
        return redirect('submission:dashboard')

    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'delete_assistant':
            assistant_id = request.POST.get('assistant_id')
            if assistant_id:
                try:
                    assistant = ResearchAssistant.objects.get(id=assistant_id, submission=submission)
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
                ResearchAssistant.objects.create(
                    submission=submission,
                    user=assistant,
                    can_submit=form.cleaned_data.get('can_submit', False),
                    can_edit=form.cleaned_data.get('can_edit', False),
                    can_view_communications=form.cleaned_data.get('can_view_communications', False)
                )
                messages.success(request, 'Research assistant added successfully.')
                
                if action == 'save_exit':
                    return redirect('submission:dashboard')
                elif action == 'save_add_another':
                    return redirect('submission:add_research_assistant', submission_id=submission.temporary_id)
            else:
                messages.error(request, 'Please select a research assistant.')
    else:
        form = ResearchAssistantForm()

    assistants = ResearchAssistant.objects.filter(submission=submission)
    return render(request, 'submission/add_research_assistant.html', {
        'form': form,
        'submission': submission,
        'assistants': assistants
    })

@login_required
def add_coinvestigator(request, submission_id):
    """Add or manage co-investigators for a submission."""
    submission = get_object_or_404(Submission, pk=submission_id)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'delete_coinvestigator':
            coinvestigator_id = request.POST.get('coinvestigator_id')
            if coinvestigator_id:
                try:
                    coinvestigator = CoInvestigator.objects.get(id=coinvestigator_id, submission=submission)
                    coinvestigator.delete()
                    messages.success(request, 'Co-investigator removed successfully.')
                except CoInvestigator.DoesNotExist:
                    messages.error(request, 'Co-investigator not found.')
            return redirect('submission:add_coinvestigator', submission_id=submission.temporary_id)

        if action in ['back', 'exit_no_save', 'save_continue']:
            if action == 'back':
                return redirect('submission:add_research_assistant', submission_id=submission.temporary_id)
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
                # Create the coinvestigator instance
                coinvestigator = CoInvestigator.objects.create(
                    submission=submission,
                    user=investigator,
                    can_submit=form.cleaned_data.get('can_submit', False),
                    can_edit=form.cleaned_data.get('can_edit', False),
                    can_view_communications=form.cleaned_data.get('can_view_communications', False)
                )
                
                # Add the selected roles
                if selected_roles:
                    coinvestigator.roles.set(selected_roles)
                
                messages.success(request, 'Co-investigator added successfully.')
                
                if action == 'save_exit':
                    return redirect('submission:dashboard')
                elif action == 'save_add_another':
                    return redirect('submission:add_coinvestigator', submission_id=submission.temporary_id)
            else:
                messages.error(request, 'Please select a co-investigator and specify their roles.')
    else:
        form = CoInvestigatorForm()

    coinvestigators = CoInvestigator.objects.filter(submission=submission)
    return render(request, 'submission/add_coinvestigator.html', {
        'form': form,
        'submission': submission,
        'coinvestigators': coinvestigators
    })

@login_required
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
    action = request.POST.get('action')

    def process_field_value(value, field_type):
        """Helper function to process field values based on field type."""
        if field_type == 'checkbox':
            try:
                if isinstance(value, str):
                    if value.startswith('['):
                        return json.loads(value)
                    # Handle comma-separated string values
                    return [v.strip() for v in value.split(',') if v.strip()]
                return value
            except json.JSONDecodeError:
                return []
        return value

    if request.method == 'POST':
        # Handle navigation actions without form processing
        if action in ['back', 'exit_no_save']:
            if action == 'back':
                previous_form = get_previous_form(submission, dynamic_form)
                if previous_form:
                    return redirect('submission:submission_form', 
                                  submission_id=submission.temporary_id, 
                                  form_id=previous_form.id)
                return redirect('submission:add_coinvestigator', 
                              submission_id=submission.temporary_id)
            return redirect('submission:dashboard')

        # Create form instance without validation
        DynamicFormClass = generate_django_form(dynamic_form)
        
        # Save all form fields without validation
        for field_name, field in DynamicFormClass.base_fields.items():
            if isinstance(field, forms.MultipleChoiceField):
                # Handle multiple choice fields (including checkboxes)
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
    for entry in FormDataEntry.objects.filter(
        submission=submission,
        form=dynamic_form,
        version=submission.version
    ):
        field = DynamicFormClass.base_fields.get(entry.field_name)
        if field:
            if isinstance(field, forms.MultipleChoiceField):
                try:
                    current_data[entry.field_name] = process_field_value(
                        entry.value, 
                        getattr(dynamic_form.fields.get(name=entry.field_name), 'field_type', None)
                    )
                except json.JSONDecodeError:
                    current_data[entry.field_name] = []
            else:
                current_data[entry.field_name] = entry.value

    # If no current data and not version 1, get previous version's data
    if not current_data and submission.version > 1 and not submission.is_locked:
        for entry in FormDataEntry.objects.filter(
            submission=submission,
            form=dynamic_form,
            version=submission.version - 1
        ):
            field = DynamicFormClass.base_fields.get(entry.field_name)
            if field:
                if isinstance(field, forms.MultipleChoiceField):
                    try:
                        current_data[entry.field_name] = process_field_value(
                            entry.value,
                            getattr(dynamic_form.fields.get(name=entry.field_name), 'field_type', None)
                        )
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
        'previous_form': get_previous_form(submission, dynamic_form),
    }
    return render(request, 'submission/dynamic_form.html', context)


# submission/views.py

@login_required
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
            if missing_documents or validation_errors:
                messages.error(request, 'Please resolve the missing documents and form errors before final submission.')
            else:
                try:
                    with transaction.atomic():
                        # Lock submission and update status
                        submission.is_locked = True
                        submission.status = 'submitted'
                        submission.date_submitted = timezone.now()
                        
                        # Create version history entry
                        VersionHistory.objects.create(
                            submission=submission,
                            version=submission.version,
                            status=submission.status,
                            date=timezone.now()
                        )
			# Generate PDF once and store in buffer
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

                        # Send confirmation to PI with PDF attachment
                        pi_message = Message.objects.create(
                            sender=system_user,
                            subject=f'Submission {submission.temporary_id} - Version {submission.version} Confirmation',
                            body=f"""
Dear {submission.primary_investigator.userprofile.full_name},

Your submission (ID: {submission.temporary_id}) has been successfully submitted.
Please find the attached PDF for your records.

Your submission will be reviewed by the OSAR who will direct it to the appropriate review bodies.

Best regards,
AIDI System
                            """.strip(),
                            related_submission=submission
                        )
                        pi_message.recipients.add(submission.primary_investigator)
                        
                        # Attach PDF to PI message
                        pi_attachment = MessageAttachment(message=pi_message)
                        pi_attachment.file.save(pdf_filename, ContentFile(buffer.getvalue()))

                        # Notify OSAR with PDF attachment
                        osar_coordinators = User.objects.filter(groups__name='OSAR')
                        osar_notification = Message.objects.create(
                            sender=system_user,
                            subject=f'New Submission For Review - {submission.title}',
                            body=f"""
A new research submission requires your initial review and forwarding.

Submission Details:
- ID: {submission.temporary_id}
- Title: {submission.title}
- PI: {submission.primary_investigator.userprofile.full_name}
- Study Type: {submission.study_type.name}
- Submitted: {timezone.now().strftime('%Y-%m-%d %H:%M')}

Please review the attached PDF and forward this submission to the appropriate review bodies.

Access the submission here: {request.build_absolute_uri(reverse('review:review_dashboard'))}

Best regards,
AIDI System
                            """.strip(),
                            related_submission=submission
                        )
                        
                        for coordinator in osar_coordinators:
                            osar_notification.recipients.add(coordinator)
                            
                        # Attach PDF to OSAR message
                        osar_attachment = MessageAttachment(message=osar_notification)
                        osar_attachment.file.save(pdf_filename, ContentFile(buffer.getvalue()))

                        # Notify co-investigators of required forms
                        notify_pending_forms(submission)

                        # Increment version AFTER everything else is done
                        submission.version += 1
                        submission.save()

                        messages.success(request, 'Submission has been finalized and sent to OSAR.')
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
        'gpt_analysis': cache.get(f'gpt_analysis_{submission.temporary_id}_{submission.version}')
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
    if not has_edit_permission(request.user, submission):
        messages.error(request, "You do not have permission to view this submission.")
        return redirect('submission:dashboard')
        
    # Get all versions from version history, ordered by version number descending
    histories = VersionHistory.objects.filter(
        submission=submission
    ).order_by('-version')
    
    # Add a flag to each history item indicating if it can be compared
    for history in histories:
        history.can_compare = history.version > 1
    
    return render(request, 'submission/version_history.html', {
        'submission': submission,
        'histories': histories,
    })

@login_required
def compare_version(request, submission_id, version):
    """Compare a version with its previous version."""
    submission = get_object_or_404(Submission, pk=submission_id)
    if not has_edit_permission(request.user, submission):
        messages.error(request, "You do not have permission to view this submission.")
        return redirect('submission:dashboard')

    # Can't compare version 1 as it has no previous version
    if version <= 1:
        messages.error(request, "Version 1 cannot be compared as it has no previous version.")
        return redirect('submission:version_history', submission_id=submission_id)

    previous_version = version - 1
    comparison_data = []
    
    # Get all forms associated with this submission's study type
    forms = submission.study_type.forms.all()
    
    for form in forms:
        # Get entries for both versions
        entries_previous = FormDataEntry.objects.filter(
            submission=submission,
            form=form,
            version=previous_version
        ).select_related('form')
        
        entries_current = FormDataEntry.objects.filter(
            submission=submission,
            form=form,
            version=version
        ).select_related('form')

        # Convert entries to dictionaries for easier comparison
        data_previous = {entry.field_name: entry.value for entry in entries_previous}
        data_current = {entry.field_name: entry.value for entry in entries_current}

        # Get field display names from form definition
        field_definitions = {
            field.name: field.displayed_name 
            for field in form.fields.all()
        }

        # Compare fields
        form_changes = []
        all_fields = sorted(set(data_previous.keys()) | set(data_current.keys()))
        
        for field in all_fields:
            displayed_name = field_definitions.get(field, field)
            value_previous = data_previous.get(field, 'Not provided')
            value_current = data_current.get(field, 'Not provided')

            # Handle JSON array values (e.g., checkbox selections)
            try:
                if isinstance(value_previous, str) and value_previous.startswith('['):
                    value_previous_display = ', '.join(json.loads(value_previous))
                else:
                    value_previous_display = value_previous
                    
                if isinstance(value_current, str) and value_current.startswith('['):
                    value_current_display = ', '.join(json.loads(value_current))
                else:
                    value_current_display = value_current
            except json.JSONDecodeError:
                value_previous_display = value_previous
                value_current_display = value_current

            # Only add to changes if values are different
            if value_previous != value_current:
                form_changes.append({
                    'field': displayed_name,
                    'previous_value': value_previous_display,
                    'current_value': value_current_display
                })

        # Only add form to comparison data if it has changes
        if form_changes:
            comparison_data.append({
                'form_name': form.name,
                'changes': form_changes
            })

    return render(request, 'submission/compare_versions.html', {
        'submission': submission,
        'version': version,
        'previous_version': previous_version,
        'comparison_data': comparison_data,
    })

@login_required
def download_submission_pdf(request, submission_id, version=None):
    """Generate and download PDF version of a submission."""
    try:
        submission = get_object_or_404(Submission, pk=submission_id)
        if not has_edit_permission(request.user, submission):
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
        Q(irb_number__icontains=term)
    ).distinct()[:10]

    results = []
    for submission in submissions:
        label = f"{submission.title}"
        if submission.irb_number:
            label += f" (IRB: {submission.irb_number})"
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


# views.py
@login_required
def investigator_form(request, submission_id, form_id):
    """Handle investigator form submission."""
    submission = get_object_or_404(Submission, pk=submission_id)
    form = get_object_or_404(DynamicForm, pk=form_id)
    
    # Check if user is allowed to submit this form
    if request.user != submission.primary_investigator and \
       not submission.coinvestigators.filter(user=request.user).exists():
        messages.error(request, "You are not authorized to submit this form.")
        return redirect('submission:dashboard')
        
    # Check if form is already submitted
    if InvestigatorFormSubmission.objects.filter(
        submission=submission,
        form=form,
        investigator=request.user,
        version=submission.version
    ).exists():
        messages.error(request, "You have already submitted this form.")
        return redirect('submission:dashboard')

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

                        # Check if all forms are complete
                        if submission.are_all_investigator_forms_complete():
                            # Notify all users who can submit
                            notify_form_completion(submission)

                        messages.success(request, f"Form '{form.name}' submitted successfully.")
                        return redirect('submission:dashboard')
                        
                except Exception as e:
                    logger.error(f"Error saving investigator form: {str(e)}")
                    messages.error(request, "An error occurred while saving your form.")
            else:
                messages.error(request, "Please correct the errors in the form.")
    else:
        form_class = generate_django_form(form)
        form_instance = form_class()

    return render(request, 'submission/investigator_form.html', {
        'form': form_instance,
        'dynamic_form': form,
        'submission': submission
    })

def notify_form_completion(submission):
    """Notify relevant users when all forms are complete."""
    system_user = get_system_user()
    
    # Get all users who can submit
    recipients = []
    recipients.append(submission.primary_investigator)
    recipients.extend([
        ci.user for ci in submission.coinvestigators.filter(can_submit=True)
    ])
    recipients.extend([
        ra.user for ra in submission.research_assistants.filter(can_submit=True)
    ])
    
    # Create notification message
    message = Message.objects.create(
        sender=system_user,
        subject=f'All Required Forms Completed - {submission.title}',
        body=f"""
All investigators have completed their required forms for:

Submission ID: {submission.temporary_id}
Title: {submission.title}

The submission is now ready for review.

Best regards,
AIDI System
        """.strip(),
        related_submission=submission
    )
    
    # Add recipients
    for recipient in recipients:
        message.recipients.add(recipient)

def notify_pending_forms(submission):
    """Notify co-investigators of pending forms."""
    system_user = get_system_user()
    required_forms = submission.get_required_investigator_forms()
    
    if not required_forms.exists():
        return
        
    form_names = ", ".join([form.name for form in required_forms])
    
    # Create notification for all co-investigators
    message = Message.objects.create(
        sender=system_user,
        subject=f'Forms Required - {submission.title}',
        body=f"""
You need to complete the following forms for:

Submission ID: {submission.temporary_id}
Title: {submission.title}

Required Forms:
{form_names}

Please log in to the system and complete these forms at your earliest convenience.

Best regards,
AIDI System
        """.strip(),
        related_submission=submission
    )
    
    # Add all co-investigators as recipients
    for coinv in submission.coinvestigators.all():
        message.recipients.add(coinv.user)


@login_required
def check_form_status(request, submission_id):
    """AJAX endpoint to check form completion status."""
    submission = get_object_or_404(Submission, pk=submission_id)
    
    if not has_edit_permission(request.user, submission):
        return JsonResponse({'error': 'Permission denied'}, status=403)
        
    status = submission.get_investigator_form_status()
    all_complete = submission.are_all_investigator_forms_complete()
    
    return JsonResponse({
        'status': status,
        'all_complete': all_complete
    })


# if you don't want to allow submission withouth coauthors filling their forms.
# views.py

# @login_required
# def submission_review(request, submission_id):
#     """Existing submission review view - add this to the submit_final section"""
#     if request.method == 'POST':
#         action = request.POST.get('action')
        
#         if action == 'submit_final':
#             if missing_documents or validation_errors:
#                 messages.error(request, 'Please resolve the missing documents and form errors before final submission.')
#             else:
#                 try:
#                     with transaction.atomic():
#                         # ... existing submission code ...
                        
#                         # Add this after submission is created but before redirecting
#                         required_forms = submission.get_required_investigator_forms()
#                         if required_forms.exists():
#                             # Notify co-investigators of required forms
#                             notify_pending_forms(submission)
                        
#                         messages.success(request, 'Submission has been finalized and sent to OSAR.')
#                         return redirect('submission:dashboard')
                        
#                 except Exception as e:
#                     logger.error(f"Error in submission finalization: {str(e)}")
#                     messages.error(request, f"Error during submission: {str(e)}")
#                     return redirect('submission:dashboard')

# # Optional: Add periodic check for overdue forms
# @login_required
# def check_overdue_forms(request):
#     """Administrative view to check for overdue forms."""
#     if not request.user.is_staff:
#         messages.error(request, "Permission denied.")
#         return redirect('submission:dashboard')
        
#     overdue_submissions = Submission.objects.filter(
#         status='submitted'
#     ).exclude(
#         study_type__forms__requested_per_investigator=False
#     )
    
#     overdue_data = []
#     for submission in overdue_submissions:
#         if not submission.are_all_investigator_forms_complete():
#             overdue_data.append({
#                 'submission': submission,
#                 'status': submission.get_investigator_form_status()
#             })
    
#     return render(request, 'submission/overdue_forms.html', {
#         'overdue_data': overdue_data
#     })

# # Add this URL if you want the overdue forms check
# urlpatterns += [
#     path('check-overdue-forms/',
#          views.check_overdue_forms,
#          name='check_overdue_forms'),
# ]

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