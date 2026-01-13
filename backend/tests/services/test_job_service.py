import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta

from app.services.job import JobService
from app.models import Job, User, JobStatus, ConversionMode
from app.schemas import JobCreate, VoiceProvider

class TestJobService:
    def setup_method(self):
        self.db = MagicMock()
        self.job_service = JobService(self.db)

    def test_create_job(self):
        """Test creating a new job"""
        # Arrange
        user_id = 1
        job_data = JobCreate(
            original_filename="test.pdf",
            voice_provider=VoiceProvider.openai,
            voice_type="default",
            reading_speed=1.0,
            include_summary=False,
            conversion_mode=ConversionMode.full
        )
        pdf_s3_key = "pdfs/test.pdf"
        pdf_s3_url = "https://s3.amazonaws.com/bucket/pdfs/test.pdf"

        # Act
        job = self.job_service.create_job(user_id, job_data, pdf_s3_key, pdf_s3_url)

        # Assert
        assert job.user_id == user_id
        assert job.original_filename == job_data.original_filename
        assert job.pdf_s3_key == pdf_s3_key
        assert job.pdf_s3_url == pdf_s3_url
        assert job.voice_provider == job_data.voice_provider
        assert job.voice_type == job_data.voice_type
        assert job.reading_speed == job_data.reading_speed
        assert job.include_summary == job_data.include_summary
        assert job.conversion_mode == job_data.conversion_mode
        assert job.status == JobStatus.pending

        self.db.add.assert_called_once_with(job)
        self.db.commit.assert_called_once()

    def test_get_user_job_found(self):
        """Test getting a user's job when it exists"""
        # Arrange
        user_id = 1
        job_id = 123
        mock_job = MagicMock()
        self.db.query.return_value.filter.return_value.first.return_value = mock_job

        # Act
        result = self.job_service.get_user_job(user_id, job_id)

        # Assert
        assert result == mock_job
        self.db.query.assert_called_once_with(Job)
        self.db.query.return_value.filter.assert_called_once()

    def test_get_user_job_not_found(self):
        """Test getting a user's job when it doesn't exist"""
        # Arrange
        user_id = 1
        job_id = 123
        self.db.query.return_value.filter.return_value.first.return_value = None

        # Act
        result = self.job_service.get_user_job(user_id, job_id)

        # Assert
        assert result is None

    def test_get_user_jobs(self):
        """Test getting all jobs for a user"""
        # Arrange
        user_id = 1
        skip = 10
        limit = 20
        mock_jobs = [MagicMock(), MagicMock()]
        query_chain = self.db.query.return_value.filter.return_value.order_by.return_value.offset.return_value.limit
        query_chain.return_value.all.return_value = mock_jobs

        # Act
        result = self.job_service.get_user_jobs(user_id, skip, limit)

        # Assert
        assert result == mock_jobs
        self.db.query.assert_called_once_with(Job)
        self.db.query.return_value.filter.assert_called_once()
        self.db.query.return_value.filter.return_value.order_by.assert_called_once()
        self.db.query.return_value.filter.return_value.order_by.return_value.offset.assert_called_once_with(skip)
        self.db.query.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.assert_called_once_with(limit)

    def test_update_job_success(self):
        """Test updating a job successfully"""
        # Arrange
        job_id = 123
        job_update = {"status": JobStatus.completed, "progress_percentage": 100}
        mock_job = MagicMock()
        self.db.query.return_value.filter.return_value.first.return_value = mock_job

        # Act
        result = self.job_service.update_job(job_id, job_update)

        # Assert
        assert result == mock_job
        assert mock_job.status == JobStatus.completed
        assert mock_job.progress_percentage == 100
        self.db.commit.assert_called_once()
        self.db.refresh.assert_called_once_with(mock_job)

    def test_update_job_not_found(self):
        """Test updating a job that doesn't exist"""
        # Arrange
        job_id = 123
        job_update = {"status": JobStatus.completed}
        self.db.query.return_value.filter.return_value.first.return_value = None

        # Act
        result = self.job_service.update_job(job_id, job_update)

        # Assert
        assert result is None
        self.db.commit.assert_not_called()
        self.db.refresh.assert_not_called()

    @patch("app.services.job.datetime")
    def test_update_job_status_processing(self, mock_datetime):
        """Test updating job status to PROCESSING"""
        # Arrange
        job_id = 123
        status = JobStatus.processing
        progress = 50
        mock_job = MagicMock()
        mock_job.started_at = None
        mock_datetime.now.return_value = datetime(2024, 1, 1, 12, 0, 0)
        self.db.query.return_value.filter.return_value.first.return_value = mock_job

        # Act
        result = self.job_service.update_job_status(job_id, status, progress)

        # Assert
        assert result == mock_job
        assert mock_job.status == status
        assert mock_job.progress_percentage == progress
        assert mock_job.started_at == datetime(2024, 1, 1, 12, 0, 0)
        self.db.commit.assert_called_once()
        self.db.refresh.assert_called_once_with(mock_job)

    @patch("app.services.job.datetime")
    def test_update_job_status_completed(self, mock_datetime):
        """Test updating job status to COMPLETED"""
        # Arrange
        job_id = 123
        status = JobStatus.completed
        progress = None
        mock_job = MagicMock()
        mock_datetime.now.return_value = datetime(2024, 1, 1, 12, 0, 0)
        self.db.query.return_value.filter.return_value.first.return_value = mock_job

        # Act
        result = self.job_service.update_job_status(job_id, status, progress)

        # Assert
        assert result == mock_job
        assert mock_job.status == status
        assert mock_job.completed_at == datetime(2024, 1, 1, 12, 0, 0)
        assert mock_job.progress_percentage == 100
        self.db.commit.assert_called_once()
        self.db.refresh.assert_called_once_with(mock_job)

    def test_update_job_status_with_error_message(self):
        """Test updating job status with error message"""
        # Arrange
        job_id = 123
        status = JobStatus.failed
        error_message = "Processing failed"
        mock_job = MagicMock()
        self.db.query.return_value.filter.return_value.first.return_value = mock_job

        # Act
        result = self.job_service.update_job_status(job_id, status, error_message=error_message)

        # Assert
        assert result == mock_job
        assert mock_job.status == status
        assert mock_job.error_message == error_message
        self.db.commit.assert_called_once()
        self.db.refresh.assert_called_once_with(mock_job)