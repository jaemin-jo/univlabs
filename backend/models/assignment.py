"""
과제 모델 정의
"""

from datetime import datetime
from typing import List, Optional
from enum import Enum

class AssignmentStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUBMITTED = "submitted"
    GRADED = "graded"
    OVERDUE = "overdue"

class AssignmentPriority(Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class Assignment:
    def __init__(
        self,
        id: str,
        title: str,
        description: str,
        course_name: str,
        course_code: str,
        due_date: datetime,
        created_at: datetime,
        updated_at: datetime,
        status: AssignmentStatus,
        priority: AssignmentPriority,
        attachment_url: Optional[str] = None,
        submission_url: Optional[str] = None,
        tags: List[str] = None,
        is_new: bool = False,
        is_upcoming: bool = False,
        university: str = "",
        student_id: str = "",
    ):
        self.id = id
        self.title = title
        self.description = description
        self.course_name = course_name
        self.course_code = course_code
        self.due_date = due_date
        self.created_at = created_at
        self.updated_at = updated_at
        self.status = status
        self.priority = priority
        self.attachment_url = attachment_url
        self.submission_url = submission_url
        self.tags = tags or []
        self.is_new = is_new
        self.is_upcoming = is_upcoming
        self.university = university
        self.student_id = student_id
    
    def to_dict(self) -> dict:
        """딕셔너리로 변환"""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "course_name": self.course_name,
            "course_code": self.course_code,
            "due_date": self.due_date.isoformat(),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "status": self.status.value,
            "priority": self.priority.value,
            "attachment_url": self.attachment_url,
            "submission_url": self.submission_url,
            "tags": self.tags,
            "is_new": self.is_new,
            "is_upcoming": self.is_upcoming,
            "university": self.university,
            "student_id": self.student_id,
        }
    
    def days_until_due(self) -> int:
        """마감까지 남은 일수"""
        return (self.due_date - datetime.now()).days
    
    def is_due_soon(self) -> bool:
        """마감 임박 여부 (3일 이내)"""
        return 0 <= self.days_until_due() <= 3
    
    def is_overdue(self) -> bool:
        """마감 지남 여부"""
        return self.days_until_due() < 0
    
    def __str__(self):
        return f"Assignment(id={self.id}, title={self.title}, due_date={self.due_date})"
    
    def __repr__(self):
        return self.__str__()
