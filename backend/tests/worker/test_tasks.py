import pytest
from unittest.mock import patch, MagicMock, ANY

from worker.tasks import process_pdf_task
from app.models import Job, JobStatus, VoiceProvider, ConversionMode


@patch("worker.tasks.StorageService")
@patch("worker.tasks.JobService")
@patch("worker.tasks.SessionLocal")
@patch("worker.tasks.pipeline")
def test_process_pdf_task_success(
    mock_pipeline, MockSessionLocal, MockJobService, MockStorageService
):
    # Arrange
    mock_db = MagicMock()
    MockSessionLocal.return_value = mock_db

    mock_job_service = MockJobService.return_value
    mock_storage_service = MockStorageService.return_value

    job = Job(
        id=1,
        pdf_s3_key="test.pdf",
        voice_provider=VoiceProvider.openai,
        voice_type="default",
        reading_speed=1.0,
        include_summary=False,
        conversion_mode=ConversionMode.full,
        user_id=1,
    )
    mock_db.query.return_value.filter.return_value.first.return_value = job
    mock_storage_service.download_file.return_value = b"%PDF"
    mock_pipeline.process_pdf.return_value = ("audio_path", 0.05, {"chars": 1000, "tokens": 50})
    mock_storage_service.upload_large_file.return_value = "http://s3.com/audio.mp3"

    # Act
    result = process_pdf_task(1)

    # Assert
    assert result["status"] == "completed"
    # final_cost = 0.05 + (50 / 1_000_000) * 2.0 = 0.0501
    mock_job_service.update_job_status.assert_any_call(1, JobStatus.processing, 0)
    mock_job_service.update_job_status.assert_any_call(1, JobStatus.completed, 100, estimated_cost=ANY, chars_processed=1000, tokens_used=50)
    mock_storage_service.download_file.assert_called_with("test.pdf")
    mock_pipeline.process_pdf.assert_called_once_with(
        pdf_path=ANY,
        voice_provider=VoiceProvider.openai,
        voice_type="default",
        reading_speed=1.0,
        include_summary=False,
        conversion_mode=ConversionMode.full,
        progress_callback=ANY,
        work_dir=ANY
    )
    mock_storage_service.upload_large_file.assert_called_with(
        "audio_path", "audio/1/1.mp3", "audio/mpeg"
    )


@patch("worker.tasks.StorageService")
@patch("worker.tasks.JobService")
@patch("worker.tasks.SessionLocal")
@patch("worker.tasks.pipeline")
def test_process_pdf_task_success_summary_explanation(
    mock_pipeline, MockSessionLocal, MockJobService, MockStorageService
):
    # Arrange
    mock_db = MagicMock()
    MockSessionLocal.return_value = mock_db

    mock_job_service = MockJobService.return_value
    mock_storage_service = MockStorageService.return_value

    job = Job(
        id=2,
        pdf_s3_key="science.pdf",
        voice_provider=VoiceProvider.openai,
        voice_type="default",
        reading_speed=1.0,
        include_summary=False,
        conversion_mode=ConversionMode.summary_explanation,
        user_id=1,
    )
    mock_db.query.return_value.filter.return_value.first.return_value = job
    mock_storage_service.download_file.return_value = b"%PDF"
    mock_pipeline.process_pdf.return_value = ("audio_path", 0.12, {"chars": 8000, "tokens": 500})
    mock_storage_service.upload_large_file.return_value = "http://s3.com/summary.mp3"

    # Act
    result = process_pdf_task(2)

    # Assert
    assert result["status"] == "completed"
    # final_cost = 0.12 + (500 / 1_000_000) * 2.0 = 0.121
    mock_job_service.update_job_status.assert_any_call(2, JobStatus.processing, 0)
    mock_job_service.update_job_status.assert_any_call(2, JobStatus.completed, 100, estimated_cost=ANY, chars_processed=8000, tokens_used=500)
    mock_storage_service.download_file.assert_called_with("science.pdf")
    mock_pipeline.process_pdf.assert_called_once_with(
        pdf_path=ANY,
        voice_provider=VoiceProvider.openai,
        voice_type="default",
        reading_speed=1.0,
        include_summary=False,
        conversion_mode=ConversionMode.summary_explanation,
        progress_callback=ANY,
        work_dir=ANY
    )
    mock_storage_service.upload_large_file.assert_called_with(
        "audio_path", "audio/1/2.mp3", "audio/mpeg"
    )


from datetime import datetime, timedelta
from worker.tasks import cleanup_old_files


@patch("worker.tasks.StorageService")
@patch("worker.tasks.SessionLocal")
def test_cleanup_old_files(MockSessionLocal, MockStorageService):
    # Arrange
    mock_db = MagicMock()
    MockSessionLocal.return_value = mock_db
    mock_storage_service = MockStorageService.return_value

    old_job = Job(
        id=1,
        pdf_s3_key="old.pdf",
        audio_s3_key="old.mp3",
        status=JobStatus.completed,
        completed_at=datetime.now() - timedelta(days=31),
    )
    new_job = Job(
        id=2,
        pdf_s3_key="new.pdf",
        audio_s3_key="new.mp3",
        status=JobStatus.completed,
        completed_at=datetime.now() - timedelta(days=1),
    )
    mock_db.query.return_value.filter.return_value.all.return_value = [old_job]

    # Act
    result = cleanup_old_files()

    # Assert
    assert result == "Cleaned up 1 old jobs"
    mock_storage_service.delete_file.assert_any_call("old.pdf")
    mock_storage_service.delete_file.assert_any_call("old.mp3")
    mock_db.delete.assert_called_with(old_job)
    mock_db.commit.assert_called_once()
