"""Admin routes - Full CRUD for all database tables."""
from typing import List, Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, EmailStr
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database.base import get_db
from app.database.cloud_models import (
    User,
    MedicineRegistry,
    Hospital,
    FamilyConnection,
    TriageHistory,
    CommunityPost,
    PostComment,
    PostLike,
    WorkoutSession,
    FitnessGoal,
)
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/admin", tags=["admin"])


# ============ User Management ============

class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    phone: Optional[str]
    full_name: str
    is_email_verified: bool
    is_phone_verified: bool
    is_active: bool
    account_type: str
    last_login: Optional[str]
    created_at: str

    class Config:
        from_attributes = True


class UserUpdateRequest(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None
    account_type: Optional[str] = None


@router.get("/users", response_model=List[UserResponse])
def list_users(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    is_active: Optional[bool] = None,
    account_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all users with pagination and filters"""
    if current_user.account_type != "admin":
        raise HTTPException(status_code=403, detail="Admin only")

    query = db.query(User)

    if search:
        query = query.filter(
            (User.username.ilike(f"%{search}%")) |
            (User.email.ilike(f"%{search}%")) |
            (User.full_name.ilike(f"%{search}%"))
        )

    if is_active is not None:
        query = query.filter(User.is_active == is_active)

    if account_type:
        query = query.filter(User.account_type == account_type)

    total = query.count()
    users = query.offset((page - 1) * limit).limit(limit).all()

    return users


@router.get("/users/{user_id}", response_model=UserResponse)
def get_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get user by ID"""
    if current_user.account_type != "admin":
        raise HTTPException(status_code=403, detail="Admin only")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


@router.patch("/users/{user_id}", response_model=UserResponse)
def update_user(
    user_id: str,
    data: UserUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update user"""
    if current_user.account_type != "admin":
        raise HTTPException(status_code=403, detail="Admin only")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(user, key, value)

    db.commit()
    db.refresh(user)
    return user


@router.delete("/users/{user_id}")
def delete_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete (deactivate) user"""
    if current_user.account_type != "admin":
        raise HTTPException(status_code=403, detail="Admin only")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_active = False
    db.commit()

    return {"message": "User deactivated"}


@router.get("/users/{user_id}/toggle-active")
def toggle_user_active(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Toggle user active status"""
    if current_user.account_type != "admin":
        raise HTTPException(status_code=403, detail="Admin only")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_active = not user.is_active
    db.commit()

    return {"is_active": user.is_active}


@router.get("/stats/users")
def get_user_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get user statistics"""
    if current_user.account_type != "admin":
        raise HTTPException(status_code=403, detail="Admin only")

    total = db.query(func.count(User.id)).scalar()
    active = db.query(func.count(User.id)).filter(User.is_active == True).scalar()
    verified = db.query(func.count(User.id)).filter(User.is_email_verified == True).scalar()

    return {
        "total": total,
        "active": active,
        "inactive": total - active,
        "email_verified": verified,
    }


# ============ Medicine Management ============

class MedicineResponse(BaseModel):
    reg_number: str
    name: str
    active_ingredient: Optional[str]
    dosage_form: Optional[str]
    strength: Optional[str]
    manufacturer: Optional[str]
    is_active: bool
    created_at: str

    class Config:
        from_attributes = True


class MedicineCreateRequest(BaseModel):
    reg_number: str
    name: str
    active_ingredient: Optional[str] = None
    dosage_form: Optional[str] = None
    strength: Optional[str] = None
    manufacturer: Optional[str] = None
    contraindications: Optional[str] = None
    side_effects: Optional[str] = None
    interactions: Optional[str] = None
    warnings: Optional[str] = None
    usage: Optional[str] = None
    storage: Optional[str] = None


class MedicineUpdateRequest(BaseModel):
    name: Optional[str] = None
    active_ingredient: Optional[str] = None
    dosage_form: Optional[str] = None
    strength: Optional[str] = None
    manufacturer: Optional[str] = None
    contraindications: Optional[str] = None
    side_effects: Optional[str] = None
    interactions: Optional[str] = None
    warnings: Optional[str] = None
    usage: Optional[str] = None
    storage: Optional[str] = None
    is_active: Optional[bool] = None


@router.get("/medicines", response_model=List[MedicineResponse])
def list_medicines(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all medicines"""
    if current_user.account_type != "admin":
        raise HTTPException(status_code=403, detail="Admin only")

    query = db.query(MedicineRegistry)

    if search:
        query = query.filter(MedicineRegistry.name.ilike(f"%{search}%"))

    if is_active is not None:
        query = query.filter(MedicineRegistry.is_active == is_active)

    medicines = query.offset((page - 1) * limit).limit(limit).all()
    return medicines


@router.get("/medicines/{reg_number}", response_model=MedicineResponse)
def get_medicine(
    reg_number: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get medicine by registration number"""
    if current_user.account_type != "admin":
        raise HTTPException(status_code=403, detail="Admin only")

    medicine = db.query(MedicineRegistry).filter(MedicineRegistry.reg_number == reg_number).first()
    if not medicine:
        raise HTTPException(status_code=404, detail="Medicine not found")

    return medicine


@router.post("/medicines", response_model=MedicineResponse)
def create_medicine(
    data: MedicineCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create new medicine"""
    if current_user.account_type != "admin":
        raise HTTPException(status_code=403, detail="Admin only")

    # Check if exists
    existing = db.query(MedicineRegistry).filter(MedicineRegistry.reg_number == data.reg_number).first()
    if existing:
        raise HTTPException(status_code=400, detail="Medicine already exists")

    medicine = MedicineRegistry(**data.model_dump())
    db.add(medicine)
    db.commit()
    db.refresh(medicine)
    return medicine


@router.patch("/medicines/{reg_number}", response_model=MedicineResponse)
def update_medicine(
    reg_number: str,
    data: MedicineUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update medicine"""
    if current_user.account_type != "admin":
        raise HTTPException(status_code=403, detail="Admin only")

    medicine = db.query(MedicineRegistry).filter(MedicineRegistry.reg_number == reg_number).first()
    if not medicine:
        raise HTTPException(status_code=404, detail="Medicine not found")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(medicine, key, value)

    db.commit()
    db.refresh(medicine)
    return medicine


@router.delete("/medicines/{reg_number}")
def delete_medicine(
    reg_number: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete medicine"""
    if current_user.account_type != "admin":
        raise HTTPException(status_code=403, detail="Admin only")

    medicine = db.query(MedicineRegistry).filter(MedicineRegistry.reg_number == reg_number).first()
    if not medicine:
        raise HTTPException(status_code=404, detail="Medicine not found")

    db.delete(medicine)
    db.commit()

    return {"message": "Medicine deleted"}


# ============ Hospital Management ============

class HospitalResponse(BaseModel):
    id: int
    name: str
    address: Optional[str]
    district: Optional[str]
    city: Optional[str]
    phone: Optional[str]
    website: Optional[str]
    latitude: Optional[str]
    longitude: Optional[str]
    specialties: Optional[str]
    accepts_bhyt: bool
    is_24h: bool
    has_emergency: bool
    hospital_type: Optional[str]

    class Config:
        from_attributes = True


class HospitalCreateRequest(BaseModel):
    name: str
    address: Optional[str] = None
    district: Optional[str] = None
    city: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    latitude: Optional[str] = None
    longitude: Optional[str] = None
    specialties: Optional[str] = None
    accepts_bhyt: bool = False
    is_24h: bool = False
    has_emergency: bool = False
    hospital_type: Optional[str] = None


class HospitalUpdateRequest(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    district: Optional[str] = None
    city: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    latitude: Optional[str] = None
    longitude: Optional[str] = None
    specialties: Optional[str] = None
    accepts_bhyt: Optional[bool] = None
    is_24h: Optional[bool] = None
    has_emergency: Optional[bool] = None
    hospital_type: Optional[str] = None


@router.get("/hospitals", response_model=List[HospitalResponse])
def list_hospitals(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    city: Optional[str] = None,
    district: Optional[str] = None,
    has_emergency: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all hospitals"""
    if current_user.account_type != "admin":
        raise HTTPException(status_code=403, detail="Admin only")

    query = db.query(Hospital)

    if search:
        query = query.filter(Hospital.name.ilike(f"%{search}%"))

    if city:
        query = query.filter(Hospital.city == city)

    if district:
        query = query.filter(Hospital.district == district)

    if has_emergency is not None:
        query = query.filter(Hospital.has_emergency == has_emergency)

    hospitals = query.offset((page - 1) * limit).limit(limit).all()
    return hospitals


@router.get("/hospitals/{hospital_id}", response_model=HospitalResponse)
def get_hospital(
    hospital_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get hospital by ID"""
    if current_user.account_type != "admin":
        raise HTTPException(status_code=403, detail="Admin only")

    hospital = db.query(Hospital).filter(Hospital.id == hospital_id).first()
    if not hospital:
        raise HTTPException(status_code=404, detail="Hospital not found")

    return hospital


@router.post("/hospitals", response_model=HospitalResponse)
def create_hospital(
    data: HospitalCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create new hospital"""
    if current_user.account_type != "admin":
        raise HTTPException(status_code=403, detail="Admin only")

    hospital = Hospital(**data.model_dump())
    db.add(hospital)
    db.commit()
    db.refresh(hospital)
    return hospital


@router.patch("/hospitals/{hospital_id}", response_model=HospitalResponse)
def update_hospital(
    hospital_id: int,
    data: HospitalUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update hospital"""
    if current_user.account_type != "admin":
        raise HTTPException(status_code=403, detail="Admin only")

    hospital = db.query(Hospital).filter(Hospital.id == hospital_id).first()
    if not hospital:
        raise HTTPException(status_code=404, detail="Hospital not found")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(hospital, key, value)

    db.commit()
    db.refresh(hospital)
    return hospital


@router.delete("/hospitals/{hospital_id}")
def delete_hospital(
    hospital_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete hospital"""
    if current_user.account_type != "admin":
        raise HTTPException(status_code=403, detail="Admin only")

    hospital = db.query(Hospital).filter(Hospital.id == hospital_id).first()
    if not hospital:
        raise HTTPException(status_code=404, detail="Hospital not found")

    db.delete(hospital)
    db.commit()

    return {"message": "Hospital deleted"}


# ============ Dashboard Stats ============

@router.get("/stats")
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get dashboard statistics"""
    if current_user.account_type != "admin":
        raise HTTPException(status_code=403, detail="Admin only")

    total_users = db.query(func.count(User.id)).scalar()
    active_users = db.query(func.count(User.id)).filter(User.is_active == True).scalar()
    total_medicines = db.query(func.count(MedicineRegistry.reg_number)).scalar()
    total_hospitals = db.query(func.count(Hospital.id)).scalar()

    return {
        "users": {
            "total": total_users,
            "active": active_users,
            "inactive": total_users - active_users,
        },
        "medicines": {
            "total": total_medicines,
        },
        "hospitals": {
            "total": total_hospitals,
        },
    }


# ══════════════════════════════════════════════════════════════
# COMMUNITY MANAGEMENT
# ══════════════════════════════════════════════════════════════


class CommunityPostResponse(BaseModel):
    id: int
    author_id: str
    author_name: Optional[str]
    content: str
    category: str
    tags: Optional[str]
    is_anonymous: bool
    status: str
    like_count: int
    comment_count: int
    has_medical_disclaimer: bool
    created_at: str

    class Config:
        from_attributes = True


class CommunityPostUpdateRequest(BaseModel):
    content: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[str] = None
    status: Optional[str] = None
    moderation_note: Optional[str] = None


@router.get("/posts", response_model=List[CommunityPostResponse])
def list_posts(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    status: Optional[str] = None,
    category: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all community posts"""
    if current_user.account_type != "admin":
        raise HTTPException(status_code=403, detail="Admin only")

    query = db.query(CommunityPost)

    if search:
        query = query.filter(CommunityPost.content.ilike(f"%{search}%"))

    if status:
        query = query.filter(CommunityPost.status == status)

    if category:
        query = query.filter(CommunityPost.category == category)

    posts = query.order_by(CommunityPost.created_at.desc()).offset((page - 1) * limit).limit(limit).all()
    return posts


@router.get("/posts/{post_id}", response_model=CommunityPostResponse)
def get_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get post by ID"""
    if current_user.account_type != "admin":
        raise HTTPException(status_code=403, detail="Admin only")

    post = db.query(CommunityPost).filter(CommunityPost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    return post


@router.patch("/posts/{post_id}", response_model=CommunityPostResponse)
def update_post(
    post_id: int,
    data: CommunityPostUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update post (moderate)"""
    if current_user.account_type != "admin":
        raise HTTPException(status_code=403, detail="Admin only")

    post = db.query(CommunityPost).filter(CommunityPost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(post, key, value)

    db.commit()
    db.refresh(post)
    return post


@router.delete("/posts/{post_id}")
def delete_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete post"""
    if current_user.account_type != "admin":
        raise HTTPException(status_code=403, detail="Admin only")

    post = db.query(CommunityPost).filter(CommunityPost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    post.status = "deleted"
    db.commit()

    return {"message": "Post deleted"}


@router.get("/stats/posts")
def get_post_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get community statistics"""
    if current_user.account_type != "admin":
        raise HTTPException(status_code=403, detail="Admin only")

    total = db.query(func.count(CommunityPost.id)).scalar()
    pending = db.query(func.count(CommunityPost.id)).filter(CommunityPost.status == "pending").scalar()
    approved = db.query(func.count(CommunityPost.id)).filter(CommunityPost.status == "approved").scalar()
    flagged = db.query(func.count(CommunityPost.id)).filter(CommunityPost.status == "flagged").scalar()

    return {
        "total": total,
        "pending": pending,
        "approved": approved,
        "flagged": flagged,
    }


# ══════════════════════════════════════════════════════════════
# WORKOUT/FITNESS MANAGEMENT
# ══════════════════════════════════════════════════════════════


class WorkoutSessionResponse(BaseModel):
    id: int
    user_id: str
    exercise_id: str
    exercise_name: str
    target_area: Optional[str]
    duration_seconds: int
    repetitions: Optional[int]
    sets: Optional[int]
    calories_burned: Optional[int]
    status: str
    difficulty_rating: Optional[str]
    created_at: str

    class Config:
        from_attributes = True


class FitnessGoalResponse(BaseModel):
    id: int
    user_id: str
    goal_type: str
    target_value: Optional[float]
    current_progress: float
    target_date: Optional[str]
    status: str
    created_at: str

    class Config:
        from_attributes = True


@router.get("/workouts", response_model=List[WorkoutSessionResponse])
def list_workouts(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    user_id: Optional[str] = None,
    exercise_id: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all workout sessions"""
    if current_user.account_type != "admin":
        raise HTTPException(status_code=403, detail="Admin only")

    query = db.query(WorkoutSession)

    if user_id:
        query = query.filter(WorkoutSession.user_id == user_id)

    if exercise_id:
        query = query.filter(WorkoutSession.exercise_id == exercise_id)

    if status:
        query = query.filter(WorkoutSession.status == status)

    workouts = query.order_by(WorkoutSession.created_at.desc()).offset((page - 1) * limit).limit(limit).all()
    return workouts


@router.get("/goals", response_model=List[FitnessGoalResponse])
def list_goals(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    user_id: Optional[str] = None,
    goal_type: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all fitness goals"""
    if current_user.account_type != "admin":
        raise HTTPException(status_code=403, detail="Admin only")

    query = db.query(FitnessGoal)

    if user_id:
        query = query.filter(FitnessGoal.user_id == user_id)

    if goal_type:
        query = query.filter(FitnessGoal.goal_type == goal_type)

    if status:
        query = query.filter(FitnessGoal.status == status)

    goals = query.order_by(FitnessGoal.created_at.desc()).offset((page - 1) * limit).limit(limit).all()
    return goals


@router.get("/stats/workouts")
def get_workout_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get workout statistics"""
    if current_user.account_type != "admin":
        raise HTTPException(status_code=403, detail="Admin only")

    total_workouts = db.query(func.count(WorkoutSession.id)).scalar()
    total_calories = db.query(func.sum(WorkoutSession.calories_burned)).scalar() or 0
    total_duration = db.query(func.sum(WorkoutSession.duration_seconds)).scalar() or 0

    active_goals = db.query(func.count(FitnessGoal.id)).filter(FitnessGoal.status == "active").scalar()
    achieved_goals = db.query(func.count(FitnessGoal.id)).filter(FitnessGoal.status == "achieved").scalar()

    return {
        "workouts": {
            "total": total_workouts,
            "total_calories": total_calories,
            "total_duration_seconds": total_duration,
        },
        "goals": {
            "active": active_goals,
            "achieved": achieved_goals,
        },
    }

