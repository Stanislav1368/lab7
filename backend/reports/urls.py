from django.urls import path

from .views import ExportReportView, ReportSchemaView

urlpatterns = [
    path("schema/", ReportSchemaView.as_view(), name="report-schema"),
    path("export/", ExportReportView.as_view(), name="report-export"),
]
