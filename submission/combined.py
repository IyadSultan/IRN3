#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "iRN.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
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
                    {% if coinvestigator %}
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
                                {% for co in coinvestigator %}
                                <tr>
                                    <td>{{ co.user.get_full_name }}</td>
                                    <td>
                                        {% for role in co.roles.all %}
                                            <span class="badge bg-secondary me-1">{{ role.name }}</span>
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
{% endblock %}{% extends 'users/base.html' %}
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
{% endblock %}{% extends 'users/base.html' %}

{% block content %}
<div class="container mt-4">
    <div class="card">
        <div class="card-header">
            <h2>Version Comparison</h2>
            <h4>{{ submission.title }}</h4>
            <p>Comparing Version {{ version1 }} with Version {{ version2 }}</p>
        </div>
        <div class="card-body">
            {% if comparison_data %}
                {% for form_data in comparison_data %}
                    <h5 class="mt-4">{{ form_data.form_name }}</h5>
                    <table class="table table-bordered">
                        <thead>
                            <tr>
                                <th>Field</th>
                                <th>Version {{ version1 }}</th>
                                <th>Version {{ version2 }}</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for change in form_data.changes %}
                                <tr>
                                    <td>{{ change.field }}</td>
                                    <td {% if change.old_value != change.new_value %}class="bg-light-yellow"{% endif %}>
                                        {{ change.old_value }}
                                    </td>
                                    <td {% if change.old_value != change.new_value %}class="bg-light-yellow"{% endif %}>
                                        {{ change.new_value }}
                                    </td>
                                </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                {% endfor %}
            {% else %}
                <div class="alert alert-info">
                    No differences found between these versions.
                </div>
            {% endif %}

            <div class="mt-4">
                <a href="{% url 'submission:submission_review' submission.temporary_id %}" class="btn btn-secondary">
                    <i class="fas fa-arrow-left"></i> Back to Review
                </a>
            </div>
        </div>
    </div>
</div>

<style>
    .bg-light-yellow {
        background-color: #fff3cd;
    }
</style>
{% endblock %}
{% extends 'users/base.html' %}
{% load static %}

{% block title %}Dashboard{% endblock %}

{% block content %}
<div class="container mt-4">
    <h1 class="mb-4">My Submissions</h1>
    <div class="mb-3">
        <a href="{% url 'submission:start_submission' %}" class="btn btn-primary">
            <i class="fas fa-plus"></i> Start New Submission
        </a>
    </div>
    <div class="table-responsive">
        <table id="submissions-table" class="table table-striped table-hover">
            <thead class="thead-light">
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
                        <span class="badge 
                            {% if submission.status == 'draft' %}
                                badge-warning
                            {% elif submission.status == 'submitted' %}
                                badge-info
                            {% elif submission.status == 'accepted' %}
                                badge-success
                            {% elif submission.status == 'revision_requested' or submission.status == 'under_revision' %}
                                badge-primary
                            {% else %}
                                badge-secondary
                            {% endif %}">
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
{% endblock %}

{% block page_specific_js %}
<script>
    $(document).ready(function() {
        $('#submissions-table').DataTable({
            "order": [[6, "desc"]],
            "columnDefs": [
                { "orderable": false, "targets": 8 }
            ]
        });
    });
</script>
{% endblock %}{% extends 'users/base.html' %}
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
{% endif %} <a href="{% url 'submission:submission_review' temporary_id=submission.temporary_id %}">Review</a> {% extends 'users/base.html' %}
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
{% endblock %}{% extends 'base.html' %}
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
{% endblock %} <!DOCTYPE html>
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

{% endblock %}{% extends 'users/base.html' %}
{% block content %}
<div class="container mt-4">
    <h1>Version History for "{{ submission.title }}"</h1>
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
