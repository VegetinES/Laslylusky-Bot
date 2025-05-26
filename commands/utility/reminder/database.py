import motor.motor_asyncio
import datetime
from datetime import timezone
import uuid
from bson import ObjectId
from pymongo.errors import ConnectionFailure

client = motor.motor_asyncio.AsyncIOMotorClient('mongodb://localhost:27017')
db = client.reminders_db
reminders_collection = db.reminders

async def save_reminder(user_id, title, description, reminder_time, user_timezone="+00:00"):
    if reminder_time.tzinfo is None:
        reminder_time = reminder_time.replace(tzinfo=datetime.timezone.utc)
    else:
        reminder_time = reminder_time.astimezone(datetime.timezone.utc)
    
    reminder_id = str(uuid.uuid4())
    reminder = {
        "_id": reminder_id,
        "user_id": user_id,
        "title": title,
        "description": description,
        "reminder_time": reminder_time,
        "user_timezone": user_timezone,
        "created_at": datetime.datetime.now(timezone.utc),
        "sent": False
    }
    
    await reminders_collection.insert_one(reminder)
    return reminder_id

async def update_reminder(reminder_id, user_id, title, description, reminder_time, user_timezone="+00:00"):
    result = await reminders_collection.update_one(
        {"_id": reminder_id, "user_id": user_id},
        {"$set": {
            "title": title,
            "description": description,
            "reminder_time": reminder_time,
            "user_timezone": user_timezone,
            "updated_at": datetime.datetime.now(timezone.utc),
            "sent": False
        }}
    )
    
    return result.modified_count > 0

async def delete_reminder(reminder_id, user_id):
    result = await reminders_collection.delete_one(
        {"_id": reminder_id, "user_id": user_id}
    )
    
    return result.deleted_count > 0

async def get_upcoming_reminders(user_id):
    now = datetime.datetime.now(timezone.utc)
    cursor = reminders_collection.find(
        {"user_id": user_id, "reminder_time": {"$gte": now}}
    ).sort("reminder_time", 1)
    
    reminders = await cursor.to_list(length=100)
    
    for reminder in reminders:
        if reminder['reminder_time'].tzinfo is None:
            reminder['reminder_time'] = reminder['reminder_time'].replace(tzinfo=datetime.timezone.utc)
        
        if 'created_at' in reminder and reminder['created_at'].tzinfo is None:
            reminder['created_at'] = reminder['created_at'].replace(tzinfo=datetime.timezone.utc)
    
    return reminders

async def get_past_reminders(user_id):
    now = datetime.datetime.now(timezone.utc)
    cursor = reminders_collection.find(
        {"user_id": user_id, "reminder_time": {"$lt": now}}
    ).sort("reminder_time", -1)
    
    reminders = await cursor.to_list(length=100)
    
    for reminder in reminders:
        if reminder['reminder_time'].tzinfo is None:
            reminder['reminder_time'] = reminder['reminder_time'].replace(tzinfo=datetime.timezone.utc)
        
        if 'created_at' in reminder and reminder['created_at'].tzinfo is None:
            reminder['created_at'] = reminder['created_at'].replace(tzinfo=datetime.timezone.utc)
    
    return reminders

async def get_reminder_by_id(reminder_id, user_id):
    reminder = await reminders_collection.find_one(
        {"_id": reminder_id, "user_id": user_id}
    )
    
    if reminder:
        if reminder['reminder_time'].tzinfo is None:
            reminder['reminder_time'] = reminder['reminder_time'].replace(tzinfo=datetime.timezone.utc)
        
        if 'created_at' in reminder and reminder['created_at'].tzinfo is None:
            reminder['created_at'] = reminder['created_at'].replace(tzinfo=datetime.timezone.utc)
    
    return reminder

async def mark_reminder_as_sent(reminder_id):
    result = await reminders_collection.update_one(
        {"_id": reminder_id},
        {"$set": {"sent": True}}
    )
    
    return result.modified_count > 0

async def get_pending_reminders():
    now = datetime.datetime.now(timezone.utc)
    cursor = reminders_collection.find(
        {"reminder_time": {"$lte": now}, "sent": False}
    )
    
    reminders = await cursor.to_list(length=None)
    return reminders

async def check_db_connection():
    try:
        await client.admin.command('ping')
        return True
    except ConnectionFailure:
        return False

async def setup(bot):
    pass