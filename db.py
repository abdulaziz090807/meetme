"""
Database module - all SQLite operations.
"""

import sqlite3
from typing import Optional, List, Tuple
from datetime import datetime, timedelta
from config import config, DEFAULT_AGE_DIFF


def get_connection() -> sqlite3.Connection:
    """Create database connection."""
    conn = sqlite3.connect(config.database_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_database() -> None:
    """Initialize all tables."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT NOT NULL,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            age INTEGER NOT NULL,
            gender TEXT NOT NULL,
            course TEXT DEFAULT '',
            interests TEXT DEFAULT '',
            about_me TEXT DEFAULT '',
            media_file_id TEXT DEFAULT NULL,
            media_type TEXT DEFAULT NULL,
            approval_status TEXT DEFAULT 'pending',
            pairing_status TEXT DEFAULT 'inactive',
            partner_id INTEGER DEFAULT NULL,
            is_banned INTEGER DEFAULT 0,
            ban_reason TEXT DEFAULT NULL,
            preferred_gender TEXT DEFAULT 'any',
            preferred_age_min INTEGER DEFAULT 16,
            preferred_age_max INTEGER DEFAULT 100,
            search_expanded INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status_updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (partner_id) REFERENCES users(user_id)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS likes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            from_user_id INTEGER NOT NULL,
            to_user_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(from_user_id, to_user_id)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user1_id INTEGER NOT NULL,
            user2_id INTEGER NOT NULL,
            user1_confirmed INTEGER DEFAULT 0,
            user2_confirmed INTEGER DEFAULT 0,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            confirmed_at TIMESTAMP DEFAULT NULL
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rejection_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            partner_id INTEGER NOT NULL,
            reason TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            admin_comment TEXT DEFAULT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            resolved_at TIMESTAMP DEFAULT NULL
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS skips (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            from_user_id INTEGER NOT NULL,
            to_user_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(from_user_id, to_user_id)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pair_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user1_id INTEGER NOT NULL,
            user2_id INTEGER NOT NULL,
            paired_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            unpaired_at TIMESTAMP DEFAULT NULL
        )
    """)
    
    conn.commit()
    conn.close()
    print("Database initialized!")


# ==================== USER OPERATIONS ====================

def add_user(
    user_id: int, username: str, first_name: str, last_name: str,
    age: int, gender: str, course: str = "", interests: str = "",
    about_me: str = "", media_file_id: str = None, media_type: str = None,
    preferred_gender: str = "any", preferred_age_min: int = 16, preferred_age_max: int = 100
) -> bool:
    """Add or update user."""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT user_id, is_banned FROM users WHERE user_id = ?", (user_id,))
        existing = cursor.fetchone()
        
        if existing and existing["is_banned"]:
            return False
        
        if existing:
            cursor.execute("""
                UPDATE users SET
                    username=?, first_name=?, last_name=?, age=?, gender=?,
                    course=?, interests=?, about_me=?, media_file_id=?, media_type=?,
                    preferred_gender=?, preferred_age_min=?, preferred_age_max=?,
                    approval_status='pending', search_expanded=0,
                    status_updated_at=CURRENT_TIMESTAMP
                WHERE user_id=?
            """, (username, first_name, last_name, age, gender, course, interests,
                  about_me, media_file_id, media_type, preferred_gender,
                  preferred_age_min, preferred_age_max, user_id))
        else:
            cursor.execute("""
                INSERT INTO users (user_id, username, first_name, last_name, age, gender,
                    course, interests, about_me, media_file_id, media_type,
                    preferred_gender, preferred_age_min, preferred_age_max)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (user_id, username, first_name, last_name, age, gender, course,
                  interests, about_me, media_file_id, media_type,
                  preferred_gender, preferred_age_min, preferred_age_max))
        
        conn.commit()
        return True
    except Exception as e:
        print(f"DB error: {e}")
        return False
    finally:
        conn.close()


def get_user(user_id: int) -> Optional[sqlite3.Row]:
    """Get user by ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user


def get_all_users() -> List[sqlite3.Row]:
    """Get all non-banned users."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE is_banned = 0")
    users = cursor.fetchall()
    conn.close()
    return users


def get_pending_users() -> List[sqlite3.Row]:
    """Get users pending approval."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE approval_status = 'pending' AND is_banned = 0 ORDER BY created_at")
    users = cursor.fetchall()
    conn.close()
    return users


def update_approval_status(user_id: int, status: str) -> bool:
    """Update approval status."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        if status == "approved":
            cursor.execute("""
                UPDATE users SET approval_status=?, pairing_status='active_finding',
                    status_updated_at=CURRENT_TIMESTAMP WHERE user_id=?
            """, (status, user_id))
        else:
            cursor.execute("""
                UPDATE users SET approval_status=?, status_updated_at=CURRENT_TIMESTAMP
                WHERE user_id=?
            """, (status, user_id))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()


def update_pairing_status(user_id: int, status: str, partner_id: int = None) -> bool:
    """Update pairing status."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE users SET pairing_status=?, partner_id=?,
                status_updated_at=CURRENT_TIMESTAMP WHERE user_id=?
        """, (status, partner_id, user_id))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()


def set_search_expanded(user_id: int, expanded: bool) -> bool:
    """Set search expanded flag."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE users SET search_expanded=? WHERE user_id=?", (1 if expanded else 0, user_id))
        conn.commit()
        return True
    finally:
        conn.close()


def ban_user(user_id: int, reason: str) -> bool:
    """Ban a user."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT partner_id FROM users WHERE user_id = ?", (user_id,))
        user = cursor.fetchone()
        
        if user and user["partner_id"]:
            cursor.execute("""
                UPDATE users SET pairing_status='active_finding', partner_id=NULL,
                    status_updated_at=CURRENT_TIMESTAMP WHERE user_id=?
            """, (user["partner_id"],))
        
        cursor.execute("""
            UPDATE users SET is_banned=1, ban_reason=?, pairing_status='inactive',
                partner_id=NULL, status_updated_at=CURRENT_TIMESTAMP WHERE user_id=?
        """, (reason, user_id))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()


def unban_user(user_id: int) -> bool:
    """Unban a user."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE users SET is_banned=0, ban_reason=NULL, approval_status='pending',
                status_updated_at=CURRENT_TIMESTAMP WHERE user_id=?
        """, (user_id,))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()


def delete_user_account(user_id: int) -> Tuple[bool, int]:
    """
    Completely delete user account and all associated data.
    Returns (success, partner_id if user had a partner).
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Check if user has a partner
        cursor.execute("SELECT partner_id FROM users WHERE user_id = ?", (user_id,))
        user = cursor.fetchone()
        partner_id = user["partner_id"] if user and user["partner_id"] else 0
        
        # If user has a partner, unpair them
        if partner_id:
            cursor.execute("""
                UPDATE users SET pairing_status='active_finding', partner_id=NULL,
                    status_updated_at=CURRENT_TIMESTAMP WHERE user_id=?
            """, (partner_id,))
            
            # Update pair history
            user1, user2 = min(user_id, partner_id), max(user_id, partner_id)
            cursor.execute("""
                UPDATE pair_history SET unpaired_at=CURRENT_TIMESTAMP
                WHERE user1_id=? AND user2_id=? AND unpaired_at IS NULL
            """, (user1, user2))
        
        # Delete from all tables
        cursor.execute("DELETE FROM likes WHERE from_user_id = ? OR to_user_id = ?", (user_id, user_id))
        cursor.execute("DELETE FROM skips WHERE from_user_id = ? OR to_user_id = ?", (user_id, user_id))
        cursor.execute("DELETE FROM matches WHERE user1_id = ? OR user2_id = ?", (user_id, user_id))
        cursor.execute("DELETE FROM rejection_requests WHERE user_id = ? OR partner_id = ?", (user_id, user_id))
        cursor.execute("DELETE FROM pair_history WHERE user1_id = ? OR user2_id = ?", (user_id, user_id))
        cursor.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
        
        conn.commit()
        return True, partner_id
    except Exception as e:
        print(f"Delete user error: {e}")
        return False, 0
    finally:
        conn.close()


# ==================== MATCHING ====================

def get_potential_partners(user_id: int, expanded: bool = False) -> List[sqlite3.Row]:
    """Get potential partners with smart filtering."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    if not user:
        conn.close()
        return []
    
    # Base query
    query = """
        SELECT * FROM users 
        WHERE user_id != ?
        AND approval_status = 'approved'
        AND pairing_status = 'active_finding'
        AND is_banned = 0
        AND user_id NOT IN (SELECT to_user_id FROM likes WHERE from_user_id = ?)
        AND user_id NOT IN (SELECT to_user_id FROM skips WHERE from_user_id = ?)
        AND user_id NOT IN (
            SELECT CASE WHEN user1_id = ? THEN user2_id ELSE user1_id END
            FROM pair_history WHERE user1_id = ? OR user2_id = ?
        )
    """
    params = [user_id, user_id, user_id, user_id, user_id, user_id]
    
    # Gender filter (opposite gender by default)
    if user["preferred_gender"] != "any":
        query += " AND gender = ?"
        params.append(user["preferred_gender"])
    else:
        # Default to opposite gender
        opposite = "female" if user["gender"] == "male" else "male"
        query += " AND gender = ?"
        params.append(opposite)
    
    # Age filter
    if expanded:
        # Expanded: use user's full preferred range
        query += " AND age >= ? AND age <= ?"
        params.extend([user["preferred_age_min"], user["preferred_age_max"]])
    else:
        # Strict: within DEFAULT_AGE_DIFF (1 year)
        query += " AND age >= ? AND age <= ?"
        params.extend([user["age"] - DEFAULT_AGE_DIFF, user["age"] + DEFAULT_AGE_DIFF])
    
    # Prioritize by shared interests
    query += " ORDER BY "
    if user["interests"]:
        interests = user["interests"].lower().split(",")
        interest_conditions = []
        for interest in interests[:3]:
            interest = interest.strip()
            if interest:
                interest_conditions.append(f"LOWER(interests) LIKE '%{interest}%'")
        if interest_conditions:
            query += f"({' + '.join(interest_conditions)}) DESC, "
    
    query += "RANDOM() LIMIT 1"
    
    cursor.execute(query, params)
    users = cursor.fetchall()
    conn.close()
    return users


def has_more_partners(user_id: int, expanded: bool) -> bool:
    """Check if there are more potential partners."""
    partners = get_potential_partners(user_id, expanded)
    return len(partners) > 0


def add_like(from_user_id: int, to_user_id: int) -> Tuple[bool, bool]:
    """Add like and check for match."""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("INSERT OR IGNORE INTO likes (from_user_id, to_user_id) VALUES (?, ?)",
                      (from_user_id, to_user_id))
        
        cursor.execute("SELECT id FROM likes WHERE from_user_id = ? AND to_user_id = ?",
                      (to_user_id, from_user_id))
        mutual = cursor.fetchone() is not None
        
        if mutual:
            user1 = min(from_user_id, to_user_id)
            user2 = max(from_user_id, to_user_id)
            cursor.execute("INSERT OR IGNORE INTO matches (user1_id, user2_id) VALUES (?, ?)",
                          (user1, user2))
            cursor.execute("""
                UPDATE users SET pairing_status='pending_pair', status_updated_at=CURRENT_TIMESTAMP
                WHERE user_id IN (?, ?)
            """, (from_user_id, to_user_id))
        
        conn.commit()
        return True, mutual
    finally:
        conn.close()


def add_skip(from_user_id: int, to_user_id: int) -> bool:
    """Add skip."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT OR IGNORE INTO skips (from_user_id, to_user_id) VALUES (?, ?)",
                      (from_user_id, to_user_id))
        conn.commit()
        return True
    finally:
        conn.close()


def get_match_partner(user_id: int) -> Optional[sqlite3.Row]:
    """Get partner from pending match."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM matches WHERE (user1_id = ? OR user2_id = ?)
        AND status = 'pending' ORDER BY created_at DESC LIMIT 1
    """, (user_id, user_id))
    match = cursor.fetchone()
    
    if not match:
        conn.close()
        return None
    
    partner_id = match["user2_id"] if match["user1_id"] == user_id else match["user1_id"]
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (partner_id,))
    partner = cursor.fetchone()
    conn.close()
    return partner


def confirm_pair(user_id: int) -> Tuple[bool, bool]:
    """Confirm pairing."""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT * FROM matches WHERE (user1_id = ? OR user2_id = ?) AND status = 'pending'
        """, (user_id, user_id))
        match = cursor.fetchone()
        
        if not match:
            return False, False
        
        if match["user1_id"] == user_id:
            cursor.execute("UPDATE matches SET user1_confirmed = 1 WHERE id = ?", (match["id"],))
            other_confirmed = match["user2_confirmed"]
        else:
            cursor.execute("UPDATE matches SET user2_confirmed = 1 WHERE id = ?", (match["id"],))
            other_confirmed = match["user1_confirmed"]
        
        both = other_confirmed == 1
        
        if both:
            cursor.execute("""
                UPDATE matches SET status='confirmed', confirmed_at=CURRENT_TIMESTAMP WHERE id=?
            """, (match["id"],))
            
            cursor.execute("""
                UPDATE users SET pairing_status='have_pair', partner_id=?,
                    status_updated_at=CURRENT_TIMESTAMP WHERE user_id=?
            """, (match["user2_id"], match["user1_id"]))
            
            cursor.execute("""
                UPDATE users SET pairing_status='have_pair', partner_id=?,
                    status_updated_at=CURRENT_TIMESTAMP WHERE user_id=?
            """, (match["user1_id"], match["user2_id"]))
            
            cursor.execute("INSERT INTO pair_history (user1_id, user2_id) VALUES (?, ?)",
                          (match["user1_id"], match["user2_id"]))
        
        conn.commit()
        return True, both
    finally:
        conn.close()


def reject_match(user_id: int) -> Tuple[bool, int]:
    """Reject match."""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT * FROM matches WHERE (user1_id = ? OR user2_id = ?) AND status = 'pending'
        """, (user_id, user_id))
        match = cursor.fetchone()
        
        if not match:
            return False, 0
        
        partner_id = match["user2_id"] if match["user1_id"] == user_id else match["user1_id"]
        
        cursor.execute("UPDATE matches SET status = 'rejected' WHERE id = ?", (match["id"],))
        cursor.execute("""
            UPDATE users SET pairing_status='active_finding', partner_id=NULL,
                status_updated_at=CURRENT_TIMESTAMP WHERE user_id IN (?, ?)
        """, (match["user1_id"], match["user2_id"]))
        
        cursor.execute("INSERT OR IGNORE INTO skips (from_user_id, to_user_id) VALUES (?, ?)",
                      (match["user1_id"], match["user2_id"]))
        cursor.execute("INSERT OR IGNORE INTO skips (from_user_id, to_user_id) VALUES (?, ?)",
                      (match["user2_id"], match["user1_id"]))
        
        conn.commit()
        return True, partner_id
    finally:
        conn.close()


# ==================== REJECTION REQUESTS ====================

def create_rejection_request(user_id: int, partner_id: int, reason: str) -> bool:
    """Create unpair request."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO rejection_requests (user_id, partner_id, reason) VALUES (?, ?, ?)",
                      (user_id, partner_id, reason))
        cursor.execute("""
            UPDATE users SET pairing_status='rejection_pending', status_updated_at=CURRENT_TIMESTAMP
            WHERE user_id=?
        """, (user_id,))
        conn.commit()
        return True
    finally:
        conn.close()


def cancel_rejection_request(user_id: int) -> bool:
    """Cancel pending rejection."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE rejection_requests SET status='cancelled' WHERE user_id=? AND status='pending'",
                      (user_id,))
        cursor.execute("""
            UPDATE users SET pairing_status='have_pair', status_updated_at=CURRENT_TIMESTAMP
            WHERE user_id=?
        """, (user_id,))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()


def get_pending_rejections() -> List[sqlite3.Row]:
    """Get pending rejections."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT r.*, u1.first_name as requester_name, u1.username as requester_username,
               u2.first_name as partner_name, u2.username as partner_username
        FROM rejection_requests r
        JOIN users u1 ON r.user_id = u1.user_id
        JOIN users u2 ON r.partner_id = u2.user_id
        WHERE r.status = 'pending' ORDER BY r.created_at
    """)
    requests = cursor.fetchall()
    conn.close()
    return requests


def approve_rejection(request_id: int, comment: str = None) -> Tuple[bool, int, int]:
    """Approve rejection."""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT * FROM rejection_requests WHERE id = ? AND status = 'pending'", (request_id,))
        req = cursor.fetchone()
        if not req:
            return False, 0, 0
        
        user_id, partner_id = req["user_id"], req["partner_id"]
        
        cursor.execute("""
            UPDATE rejection_requests SET status='approved', admin_comment=?,
                resolved_at=CURRENT_TIMESTAMP WHERE id=?
        """, (comment, request_id))
        
        cursor.execute("""
            UPDATE users SET pairing_status='active_finding', partner_id=NULL,
                status_updated_at=CURRENT_TIMESTAMP WHERE user_id IN (?, ?)
        """, (user_id, partner_id))
        
        user1, user2 = min(user_id, partner_id), max(user_id, partner_id)
        cursor.execute("""
            UPDATE pair_history SET unpaired_at=CURRENT_TIMESTAMP
            WHERE user1_id=? AND user2_id=? AND unpaired_at IS NULL
        """, (user1, user2))
        
        conn.commit()
        return True, user_id, partner_id
    finally:
        conn.close()


def deny_rejection(request_id: int, comment: str = None) -> Tuple[bool, int]:
    """Deny rejection."""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT user_id FROM rejection_requests WHERE id = ? AND status = 'pending'",
                      (request_id,))
        req = cursor.fetchone()
        if not req:
            return False, 0
        
        cursor.execute("""
            UPDATE rejection_requests SET status='denied', admin_comment=?,
                resolved_at=CURRENT_TIMESTAMP WHERE id=?
        """, (comment, request_id))
        
        cursor.execute("""
            UPDATE users SET pairing_status='have_pair', status_updated_at=CURRENT_TIMESTAMP
            WHERE user_id=?
        """, (req["user_id"],))
        
        conn.commit()
        return True, req["user_id"]
    finally:
        conn.close()


def force_unpair(user_id: int) -> Tuple[bool, int]:
    """Force unpair."""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT partner_id FROM users WHERE user_id = ?", (user_id,))
        user = cursor.fetchone()
        if not user or not user["partner_id"]:
            return False, 0
        
        partner_id = user["partner_id"]
        
        cursor.execute("""
            UPDATE users SET pairing_status='active_finding', partner_id=NULL,
                status_updated_at=CURRENT_TIMESTAMP WHERE user_id IN (?, ?)
        """, (user_id, partner_id))
        
        user1, user2 = min(user_id, partner_id), max(user_id, partner_id)
        cursor.execute("""
            UPDATE pair_history SET unpaired_at=CURRENT_TIMESTAMP
            WHERE user1_id=? AND user2_id=? AND unpaired_at IS NULL
        """, (user1, user2))
        
        cursor.execute("""
            UPDATE rejection_requests SET status='force_resolved'
            WHERE (user_id=? OR partner_id=?) AND status='pending'
        """, (user_id, user_id))
        
        conn.commit()
        return True, partner_id
    finally:
        conn.close()


# ==================== TIMEOUTS ====================

def get_timed_out_pending_pairs(timeout_hours: int) -> List[sqlite3.Row]:
    """Get timed out pending pairs."""
    conn = get_connection()
    cursor = conn.cursor()
    cutoff = datetime.now() - timedelta(hours=timeout_hours)
    cursor.execute("""
        SELECT * FROM users WHERE pairing_status = 'pending_pair' AND status_updated_at < ?
    """, (cutoff,))
    users = cursor.fetchall()
    conn.close()
    return users


def get_timed_out_rejections(timeout_hours: int) -> List[sqlite3.Row]:
    """Get timed out rejections."""
    conn = get_connection()
    cursor = conn.cursor()
    cutoff = datetime.now() - timedelta(hours=timeout_hours)
    cursor.execute("SELECT * FROM rejection_requests WHERE status = 'pending' AND created_at < ?",
                  (cutoff,))
    requests = cursor.fetchall()
    conn.close()
    return requests


def auto_expire_pending_match(user_id: int) -> Tuple[bool, int]:
    """Auto-expire pending match."""
    return reject_match(user_id)


def auto_approve_rejection(request_id: int) -> Tuple[bool, int, int]:
    """Auto-approve rejection."""
    return approve_rejection(request_id, "Auto-approved (timeout)")


# ==================== STATISTICS ====================

def get_statistics() -> dict:
    """Get comprehensive stats."""
    conn = get_connection()
    cursor = conn.cursor()
    
    stats = {
        "total_users": 0, "pending_approval": 0, "approved": 0, "rejected": 0,
        "banned": 0, "active_finding": 0, "pending_pair": 0, "have_pair": 0,
        "rejection_pending": 0, "total_pairs": 0, "total_pair_history": 0,
        "pending_rejections": 0, "total_likes": 0, "total_skips": 0
    }
    
    cursor.execute("SELECT COUNT(*) as c FROM users")
    stats["total_users"] = cursor.fetchone()["c"]
    
    cursor.execute("SELECT COUNT(*) as c FROM users WHERE is_banned = 1")
    stats["banned"] = cursor.fetchone()["c"]
    
    cursor.execute("SELECT approval_status, COUNT(*) as c FROM users WHERE is_banned = 0 GROUP BY approval_status")
    for row in cursor.fetchall():
        if row["approval_status"] == "pending":
            stats["pending_approval"] = row["c"]
        elif row["approval_status"] == "approved":
            stats["approved"] = row["c"]
        elif row["approval_status"] == "rejected":
            stats["rejected"] = row["c"]
    
    cursor.execute("""
        SELECT pairing_status, COUNT(*) as c FROM users
        WHERE approval_status = 'approved' AND is_banned = 0 GROUP BY pairing_status
    """)
    for row in cursor.fetchall():
        if row["pairing_status"] in stats:
            stats[row["pairing_status"]] = row["c"]
    
    cursor.execute("SELECT COUNT(*) as c FROM matches WHERE status = 'confirmed'")
    stats["total_pairs"] = cursor.fetchone()["c"]
    
    cursor.execute("SELECT COUNT(*) as c FROM pair_history")
    stats["total_pair_history"] = cursor.fetchone()["c"]
    
    cursor.execute("SELECT COUNT(*) as c FROM rejection_requests WHERE status = 'pending'")
    stats["pending_rejections"] = cursor.fetchone()["c"]
    
    cursor.execute("SELECT COUNT(*) as c FROM likes")
    stats["total_likes"] = cursor.fetchone()["c"]
    
    cursor.execute("SELECT COUNT(*) as c FROM skips")
    stats["total_skips"] = cursor.fetchone()["c"]
    
    conn.close()
    return stats


def get_all_pairs() -> List[sqlite3.Row]:
    """Get all pairs."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT u1.*, u2.user_id as partner_user_id, u2.first_name as partner_first_name,
               u2.last_name as partner_last_name, u2.username as partner_username
        FROM users u1 JOIN users u2 ON u1.partner_id = u2.user_id
        WHERE u1.pairing_status = 'have_pair' AND u1.user_id < u1.partner_id
    """)
    pairs = cursor.fetchall()
    conn.close()
    return pairs