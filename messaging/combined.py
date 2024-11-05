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
{% load messaging_extras %}

{% block title %}Archived Messages{% endblock %}

{% block extra_css %}
{{ block.super }}
<link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.10.24/css/dataTables.bootstrap4.min.css">
{% endblock %}

{% block content %}
<div class="container mt-4">
    <h1 class="mb-4">Archived Messages</h1>
    
    <div class="table-responsive">
        <table id="archived-messages-table" class="table table-striped table-hover">
            <thead class="thead-light">
                <tr>
                    <th>From</th>
                    <th>Subject</th>
                    <th>Study Name</th>
                    <th>Date</th>
                </tr>
            </thead>
            <tbody>
                {% for message in messages %}
                <tr>
                    <td>{{ message.sender.username }}</td>
                    <td><a href="{% url 'messaging:view_message' message.id %}">{{ message.subject }}</a></td>
                    <td>{{ message.study_name|default_if_none:"-" }}</td>
                    <td data-order="{{ message.sent_at|date:'Y-m-d H:i:s' }}">{{ message.sent_at|date:"M d, Y H:i" }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>
{% endblock %}

{% block extra_js %}
{{ block.super }}
<script type="text/javascript" src="https://cdn.datatables.net/1.10.24/js/jquery.dataTables.min.js"></script>
<script type="text/javascript" src="https://cdn.datatables.net/1.10.24/js/dataTables.bootstrap4.min.js"></script>
<script>
    $(document).ready(function() {
        $('#archived-messages-table').DataTable({
            "order": [[3, "desc"]]
        });
    });
</script>
{% endblock %}
{% extends 'users/base.html' %}
{% load i18n %}
{% load crispy_forms_tags %}

{% block extra_head %}
    <!-- Add Select2 CSS -->
    <link href="https://cdn.jsdelivr.net/npm/select2@4.1.0-rc.0/dist/css/select2.min.css" rel="stylesheet" />
    <style>
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
        
        .form-label {
            font-weight: 500;
            margin-bottom: 0.5rem;
            color: #495057;
        }
    </style>
{% endblock %}

{% block content %}
<div class="container mt-4">
    <h2>
        {% if is_reply %}Reply{% elif is_reply_all %}Reply All{% elif is_forward %}Forward{% else %}Compose Message{% endif %}
    </h2>
    <form method="post" enctype="multipart/form-data">
        {% csrf_token %}
        
        <!-- Subject Field -->
        <div class="mb-3">
            <label for="id_subject" class="form-label">Subject</label>
            {{ form.subject }}
        </div>

        <!-- Related Submission Field -->
        <div class="mb-4">
            <label for="id_related_submission" class="form-label">Related Study</label>
            {{ form.related_submission }}
            <small class="text-muted d-block mt-1">Search by study title or IRB number</small>
        </div>

        <!-- Recipients Fields -->
        <div class="mb-3">
            <label for="id_recipients" class="form-label">To</label>
            {{ form.recipients }}
        </div>
        <div class="mb-3">
            <label for="id_cc" class="form-label">CC</label>
            {{ form.cc }}
        </div>
        <div class="mb-3">
            <label for="id_bcc" class="form-label">BCC</label>
            {{ form.bcc }}
        </div>

        <!-- Message Body -->
        <div class="mb-3">
            <label for="id_body" class="form-label">Message</label>
            {{ form.body }}
        </div>

        <!-- Attachments -->
        <div class="mb-3">
            <label for="id_attachment" class="form-label">Attachment</label>
            {{ form.attachment }}
            <small class="text-muted">Select a file to attach</small>
        </div>

        <!-- Submit Buttons -->
        <div class="mt-4">
            <button type="submit" class="btn btn-primary">Send</button>
            <a href="{% url 'messaging:inbox' %}" class="btn btn-secondary">Cancel</a>
        </div>
    </form>
</div>
{% endblock %}

{% block extra_js %}
    <!-- Add Select2 JS -->
    <script src="https://cdn.jsdelivr.net/npm/select2@4.1.0-rc.0/dist/js/select2.min.js"></script>
    <script>
        $(document).ready(function() {
            // Initialize Select2 for recipients, cc, and bcc fields
            $('#id_recipients, #id_cc, #id_bcc').select2({
                theme: 'bootstrap4',
                ajax: {
                    url: '{% url "messaging:user_autocomplete" %}',
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
                placeholder: 'Search for users...',
                allowClear: true,
                multiple: true
            });

            // Initialize Select2 for submission field
            $('#id_related_submission').select2({
                theme: 'bootstrap4',
                ajax: {
                    url: '{% url "messaging:submission_autocomplete" %}',
                    dataType: 'json',
                    delay: 250,
                    data: function (params) {
                        return {
                            term: params.term,
                            page: params.page
                        };
                    },
                    processResults: function (data) {
                        return data;
                    },
                    cache: true
                },
                minimumInputLength: 2,
                placeholder: 'Search for a study...',
                allowClear: true,
                multiple: false,
                width: '100%',
                dropdownParent: $('#id_related_submission').parent()
            });

            // Optional: Show selected file name
            $('#id_attachment').on('change', function() {
                var fileName = $(this).val().split('\\').pop();
                $(this).next('.text-muted').text(fileName || 'Select a file to attach');
            });
        });
    </script>
{% endblock %}
{% extends 'users/base.html' %}
{% load messaging_extras %}

{% block title %}Inbox{% endblock %}

{% block extra_css %}
{{ block.super }}
<link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.10.24/css/dataTables.bootstrap4.min.css">
{% endblock %}

{% block content %}
<div class="container mt-4">
    <h1 class="mb-4">Inbox</h1>
    
    <form method="post" action="{% url 'messaging:archive_message' %}">
        {% csrf_token %}
        <div class="table-responsive">
            <table id="inbox-table" class="table table-striped table-hover">
                <thead class="thead-light">
                    <tr>
                        <th><input type="checkbox" id="select-all"></th>
                        <th>Status</th>
                        <th>From</th>
                        <th>Subject</th>
                        <th>Study Name</th>
                        <th>Date</th>
                    </tr>
                </thead>
                <tbody>
                    {% for message in messages %}
                    <tr>
                        <td><input type="checkbox" name="selected_messages" value="{{ message.id }}"></td>
                        <td>{% if message|get_read_status:request.user %}<span class="badge badge-secondary">Read</span>{% else %}<span class="badge badge-primary">Unread</span>{% endif %}</td>
                        <td>{{ message.sender.username }}</td>
                        <td><a href="{% url 'messaging:view_message' message.id %}">{{ message.subject }}</a></td>
                        <td>{{ message.study_name|default_if_none:"-" }}</td>
                        <td data-order="{{ message.sent_at|date:'Y-m-d H:i:s' }}">{{ message.sent_at|date:"M d, Y H:i" }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        <button type="submit" class="btn btn-warning mt-3">Archive Selected</button>
    </form>
</div>
{% endblock %}

{% block extra_js %}
{{ block.super }}
<script type="text/javascript" src="https://cdn.datatables.net/1.10.24/js/jquery.dataTables.min.js"></script>
<script type="text/javascript" src="https://cdn.datatables.net/1.10.24/js/dataTables.bootstrap4.min.js"></script>
<script>
    $(document).ready(function() {
        var table = $('#inbox-table').DataTable({
            "order": [[5, "desc"]],
            "columnDefs": [
                { "orderable": false, "targets": [0, 1] }
            ]
        });

        $('#select-all').on('click', function(){
            $('input[name="selected_messages"]').prop('checked', this.checked);
        });

        $('input[name="selected_messages"]').on('change', function(){
            $('#select-all').prop('checked', $('input[name="selected_messages"]:checked').length === $('input[name="selected_messages"]').length);
        });
    });
</script>
{% endblock %}
{% extends 'users/base.html' %}
{% load messaging_extras %}

{% block title %}Search Results{% endblock %}

{% block extra_css %}
{{ block.super }}
<link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.10.24/css/dataTables.bootstrap4.min.css">
{% endblock %}

{% block content %}
<div class="container mt-4">
    <h1 class="mb-4">Search Results for "{{ query }}"</h1>
    
    {% if messages %}
        <div class="table-responsive">
            <table id="search-results-table" class="table table-striped table-hover">
                <thead class="thead-light">
                    <tr>
                        <th>From</th>
                        <th>To</th>
                        <th>Subject</th>
                        <th>Study Name</th>
                        <th>Date</th>
                    </tr>
                </thead>
                <tbody>
                    {% for message in messages %}
                    <tr>
                        <td>{{ message.sender.username }}</td>
                        <td>{{ message.recipients.all|join:", " }}</td>
                        <td><a href="{% url 'messaging:view_message' message.id %}">{{ message.subject }}</a></td>
                        <td>{{ message.study_name|default_if_none:"-" }}</td>
                        <td data-order="{{ message.sent_at|date:'Y-m-d H:i:s' }}">{{ message.sent_at|date:"M d, Y H:i" }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    {% else %}
        <p>No messages found matching your search query.</p>
    {% endif %}
    
    <a href="{% url 'messaging:inbox' %}" class="btn btn-secondary mt-3">Back to Inbox</a>
</div>
{% endblock %}

{% block extra_js %}
{{ block.super }}
<script type="text/javascript" src="https://cdn.datatables.net/1.10.24/js/jquery.dataTables.min.js"></script>
<script type="text/javascript" src="https://cdn.datatables.net/1.10.24/js/dataTables.bootstrap4.min.js"></script>
<script>
    $(document).ready(function() {
        $('#search-results-table').DataTable({
            "order": [[4, "desc"]]
        });
    });
</script>
{% endblock %}
{% extends 'users/base.html' %}
{% load messaging_extras %}

{% block title %}Sent Messages{% endblock %}

{% block extra_css %}
{{ block.super }}
<link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.10.24/css/dataTables.bootstrap4.min.css">
{% endblock %}

{% block content %}
<div class="container mt-4">
    <h1 class="mb-4">Sent Messages</h1>
    
    <form method="post" action="{% url 'messaging:archive_message' %}">
        {% csrf_token %}
        <div class="table-responsive">
            <table id="sent-messages-table" class="table table-striped table-hover">
                <thead class="thead-light">
                    <tr>
                        <th><input type="checkbox" id="select-all"></th>
                        <th>To</th>
                        <th>Subject</th>
                        <th>Study Name</th>
                        <th>Date</th>
                    </tr>
                </thead>
                <tbody>
                    {% for message in messages %}
                    <tr>
                        <td><input type="checkbox" name="selected_messages" value="{{ message.id }}"></td>
                        <td>{{ message.recipients.all|join:", " }}</td>
                        <td><a href="{% url 'messaging:view_message' message.id %}">{{ message.subject }}</a></td>
                        <td>{{ message.study_name|default_if_none:"-" }}</td>
                        <td data-order="{{ message.sent_at|date:'Y-m-d H:i:s' }}">{{ message.sent_at|date:"M d, Y H:i" }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        <button type="submit" class="btn btn-warning mt-3">Archive Selected</button>
    </form>
</div>
{% endblock %}

{% block extra_js %}
{{ block.super }}
<script type="text/javascript" src="https://cdn.datatables.net/1.10.24/js/jquery.dataTables.min.js"></script>
<script type="text/javascript" src="https://cdn.datatables.net/1.10.24/js/dataTables.bootstrap4.min.js"></script>
<script>
    $(document).ready(function() {
        var table = $('#sent-messages-table').DataTable({
            "order": [[4, "desc"]],
            "columnDefs": [
                { "orderable": false, "targets": 0 }
            ]
        });

        $('#select-all').on('click', function(){
            $('input[name="selected_messages"]').prop('checked', this.checked);
        });

        $('input[name="selected_messages"]').on('change', function(){
            $('#select-all').prop('checked', $('input[name="selected_messages"]:checked').length === $('input[name="selected_messages"]').length);
        });
    });
</script>
{% endblock %}
{% extends 'users/base.html' %}
{% load messaging_extras %}

{% block title %}Threads Inbox{% endblock %}

{% block extra_css %}
{{ block.super }}
<link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.10.24/css/dataTables.bootstrap4.min.css">
{% endblock %}

{% block content %}
<div class="container mt-4">
    <h1 class="mb-4">Threads Inbox</h1>
    
    <div class="table-responsive">
        <table id="threads-table" class="table table-striped table-hover">
            <thead class="thead-light">
                <tr>
                    <th>From</th>
                    <th>Subject</th>
                    <th>Study Name</th>
                    <th>Thread Size</th>
                    <th>Started</th>
                    <th>Last Update</th>
                </tr>
            </thead>
            <tbody>
                {% for message in first_messages %}
                <tr>
                    <td>{{ message.sender.username }}</td>
                    <td><a href="{% url 'messaging:view_message' message.id %}">{{ message.subject }}</a></td>
                    <td>{{ message.study_name|default_if_none:"-" }}</td>
                    <td>{{ message.thread_size }}</td>
                    <td data-order="{{ message.sent_at|date:'Y-m-d H:i:s' }}">{{ message.sent_at|date:"M d, Y H:i" }}</td>
                    <td data-order="{{ message.last_update|date:'Y-m-d H:i:s' }}">{{ message.last_update|date:"M d, Y H:i" }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>
{% endblock %}

{% block extra_js %}
{{ block.super }}
<script type="text/javascript" src="https://cdn.datatables.net/1.10.24/js/jquery.dataTables.min.js"></script>
<script type="text/javascript" src="https://cdn.datatables.net/1.10.24/js/dataTables.bootstrap4.min.js"></script>
<script>
    $(document).ready(function() {
        $('#threads-table').DataTable({
            "order": [[5, "desc"]], // Sort by last update by default
            "pageLength": 25,
            "language": {
                "emptyTable": "No threads with more than one message found."
            }
        });
    });
</script>
{% endblock %}
{% extends 'users/base.html' %}
{% load static %}
{% block title %}View Message{% endblock %}

{% block extra_css %}
{{ block.super }}
<style>
    .message-header {
        background-color: #f8f9fa;
        border-bottom: 1px solid #dee2e6;
        padding: 15px;
    }
    .message-body {
        padding: 20px;
        white-space: pre-wrap;
    }
    .message-footer {
        background-color: #f8f9fa;
        border-top: 1px solid #dee2e6;
        padding: 15px;
    }
</style>
{% endblock %}

{% block content %}
<div class="container mt-4">
    <div class="card">
        <div class="card-header message-header">
            <h2 class="mb-3">{{ message.subject }}</h2>
            <div class="row">
                <div class="col-md-8">
                    <p><strong>From:</strong> {{ message.sender.get_full_name }}</p>
                    <p><strong>To:</strong>
                        {% for recipient in message.recipients.all %}
                            {{ recipient.get_full_name }}{% if not forloop.last %}, {% endif %}
                        {% endfor %}
                    </p>
                    {% if message.cc.all %}
                        <p><strong>CC:</strong>
                            {% for cc_recipient in message.cc.all %}
                                {{ cc_recipient.get_full_name }}{% if not forloop.last %}, {% endif %}
                            {% endfor %}
                        </p>
                    {% endif %}
                    {% if message.study_name %}
                        <p><strong>Study Name:</strong> {{ message.study_name }}</p>
                    {% endif %}
                    {% if message.related_submission %}
                        <p><strong>Related Submission:</strong>
                            <a href="{% url 'submission:submission_detail' message.related_submission.id %}">
                                {{ message.related_submission.title }}
                            </a>
                        </p>
                    {% endif %}
                    <p><strong>Sent At:</strong> {{ message.sent_at|date:"F d, Y H:i" }}</p>
                    {% if message.hashtags %}
                        <p><strong>Hashtags:</strong> {{ message.hashtags }}</p>
                    {% endif %}
                </div>
                <div class="col-md-4 text-md-right">
                    <!-- Additional info can be placed here if needed -->
                </div>
            </div>
        </div>
        <div class="card-body message-body">
            {{ message.body|linebreaks }}
        </div>
        <div class="card-footer message-footer">
            <div class="btn-group" role="group">
                <a href="{% url 'messaging:reply' message.id %}" class="btn btn-primary">Reply</a>
                <a href="{% url 'messaging:reply_all' message.id %}" class="btn btn-secondary">Reply All</a>
                <a href="{% url 'messaging:forward' message.id %}" class="btn btn-info">Forward</a>
                <form method="post" action="{% url 'messaging:archive_message' %}" style="display: inline;">
                    {% csrf_token %}
                    <input type="hidden" name="message_ids" value="{{ message.id }}">
                    <button type="submit" class="btn btn-warning" onclick="return confirm('Are you sure you want to archive this message?');">Archive</button>
                </form>
            </div>
        </div>
    </div>
    <a href="{% url 'messaging:inbox' %}" class="btn btn-secondary mt-3">Back to Inbox</a>
</div>
{% endblock %}
