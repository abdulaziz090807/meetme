"""
All bot messages stored here for easy updates.
Creative, playful, and romantic style with emojis.
"""

# ==================== WELCOME & START ====================

WELCOME_NEW = """
✨ *Welcome to Meet Me - Waltz Partner Finder!* ✨

💃 Find your perfect dance partner for the Winter Waltz night! 🕺

Let's create your magical profile!
Please enter your *first name* 💫
"""

WELCOME_BACK = """
💖 *Welcome back, {name}!* 💖

🌟 Profile: {approval_status}
💫 Status: {pairing_status}

Ready to find your waltz partner? ✨
"""

USERNAME_REQUIRED = """
⚠️ *Username Required*

To join the dance, you need a Telegram username! 💫

Set one up in:
Settings → Edit Profile → Username

Then tap /start again! 🎭
"""

BANNED_MESSAGE = """
🚫 *Access Denied*

You've been restricted from the dance floor.
Reason: {reason}

Contact admin if you believe this is a mistake. 💔
"""

# ==================== REGISTRATION ====================

REG_FIRST_NAME = """
✨ Lovely, *{name}*! 

Now tell me your *last name* 📝
"""

REG_AGE = """
🎂 How old are you? ({min_age}-{max_age})

Enter your age to find the perfect match! 💕
"""

REG_GENDER = """
💫 What's your gender?

This helps us find your perfect waltz partner! 💃🕺
"""

REG_COURSE = """
🎓 What do you study?

Select your course/faculty to connect with fellow students! 📚
"""

REG_INTERESTS = """
💝 What are your interests?

Share your hobbies (comma-separated):
*Example:* dancing, music, books, sports

This helps us find someone special who shares your passions! ✨

Or tap Skip 👇
"""

REG_MEDIA = """
📸 *Show yourself!*

Send a photo or short video (max 1 min) 🎬
Let your future partner see the real you! 💫

Or tap Skip if you're feeling shy 🙈
"""

REG_ABOUT = """
💭 *Tell us about yourself!*

What makes you unique? What are you looking for in a dance partner? 💃

Share a bit about yourself (or Skip) ✨
"""

REG_PREF_GENDER = """
💕 *Who are you looking for?*

What gender would you like your waltz partner to be? 🌹
"""

REG_PREF_AGE = """
🎯 *Age preference*

Enter preferred age range (e.g., 18-22)
Or Skip for default ({min_age}-{max_age}) 💫
"""

REG_PREVIEW = """
✨ *Profile Preview* ✨

👤 *{first_name} {last_name}*
🆔 ID: `{user_id}`
🎂 Age: {age}
{gender_emoji} Gender: {gender}
{course_line}
{interests_line}
{about_line}

🎯 *Looking for:* {pref_gender}, {pref_age_min}-{pref_age_max} y/o

Ready to join the dance? 💃🕺
"""

REG_SUCCESS = """
🎉 *Profile Submitted!* 🎉

Your profile is awaiting admin approval 💫
We'll notify you once you're ready to dance! 💃

Stay tuned... ✨
"""

REG_CANCELLED = """
😢 Registration cancelled.

Tap /start whenever you're ready to dance! 💃
"""

# ==================== PROFILE ====================

PROFILE_VIEW = """
✨ *Your Profile* ✨

👤 *{first_name} {last_name}*
🆔 ID: `{user_id}`
📱 @{username}
🎂 Age: {age}
{gender_emoji} Gender: {gender}
{course_line}
{interests_line}
{about_line}

📊 *Status:*
✅ Profile: {approval_status}
💫 Pairing: {pairing_status}

🎯 *Filters:* {pref_gender}, {pref_age_min}-{pref_age_max} y/o
"""

FILTERS_VIEW = """
🎯 *Your Match Filters*

{gender_emoji} Preferred gender: {pref_gender}
🎂 Age range: {pref_age_min} - {pref_age_max}

To change filters, use Edit Profile 💫
"""

# ==================== MATCHING ====================

FINDING_PARTNER = """
💕 *Potential Match* 💕
"""

PARTNER_CARD = """
✨ *{first_name}, {age}* ✨

{gender_emoji} {gender}
{username_line}
{course_line}
{interests_line}
{about_line}
"""

NO_PARTNERS = """
😔 *No matches available right now*

Try adjusting your filters or check back later!
Your perfect partner might be just around the corner 💫
"""

NO_MORE_PARTNERS = """
🔍 *You've seen everyone!*

We've expanded your age range to show more options.
Keep swiping to find your perfect match! 💕
"""

ALL_SEEN = """
✨ *That's everyone for now!*

Check back later - new dancers join every day! 💃
"""

# ==================== MATCH FOUND ====================

MATCH_FOUND = """
💖 *It's a Match!* 💖

You and *{name}* both liked each other! 🎉

Use 'View Match' to decide if you want to be waltz partners! 💃🕺
"""

MATCH_VIEW = """
💕 *Your Match* 💕

Do you want to dance the waltz with this person? 🌹
"""

MATCH_CONFIRMED_WAIT = """
✅ *You confirmed!*

Waiting for *{name}* to decide... 💫
We'll notify you when they respond! 🔔
"""

MATCH_BOTH_CONFIRMED = """
🎉 *Congratulations!* 🎉

You and *{name}* are now waltz partners! 💃🕺

📱 Contact: @{username}

Time to practice your waltz steps! 💖✨
"""

MATCH_REJECTED = """
💔 You chose to keep searching.

Don't worry - your perfect match is out there! 
Use 'Find Partner' to continue 💕
"""

MATCH_REJECTED_PARTNER = """
💫 Your match decided to search for another partner.

Don't give up! Use 'Find Partner' to continue 💕
"""

MATCH_EXPIRED = """
⏰ *Match Expired*

No response within {hours} hours.
Both of you can continue searching! 💕
"""

# ==================== PARTNER VIEW ====================

PARTNER_VIEW = """
💖 *Your Waltz Partner* 💖
"""

# ==================== UNPAIR ====================

UNPAIR_CONFIRM = """
💔 *Request to Unpair*

You're currently paired with *{name}*.

Are you sure you want to request unpair?
This requires admin approval. 🎭
"""

UNPAIR_REASON = """
📝 *Why do you want to unpair?*

Please provide a reason (min 10 characters).
This will be reviewed by admin. 💫
"""

UNPAIR_SUBMITTED = """
📨 *Request Submitted*

Your unpair request is being reviewed.
We'll notify you of the decision! 💫
"""

UNPAIR_CANCELLED = """
💕 *Request Cancelled*

You remain paired with your partner! 💃🕺
"""

UNPAIR_APPROVED = """
✅ *Unpair Approved*

You're free to find a new waltz partner! 💃
Use 'Find Partner' to continue searching.
"""

UNPAIR_DENIED = """
❌ *Unpair Request Denied*

You remain paired with your current partner.
Try working things out! 💕
"""

UNPAIR_STATUS_PENDING = """
⏳ Your unpair request is still pending.

Please wait for admin decision! 💫
"""

UNPAIR_AUTO_APPROVED = """
⏰ *Auto-Unpaired*

Your request was auto-approved after {hours} hours.
You can now search for a new partner! 💃
"""

# ==================== ADMIN ====================

ADMIN_PANEL = """
🎛️ *Admin Control Panel* 🎛️

👥 Users: {total_users} (Banned: {banned})
📋 Pending: {pending_approval}
✅ Approved: {approved}

💃 Searching: {active_finding}
💕 Matched: {pending_pair}
💖 Paired: {have_pair}
🎭 Total Pairs: {total_pairs}

📨 Unpair Requests: {pending_rejections}
"""

ADMIN_STATS = """
📊 *Bot Statistics* 📊

👥 *Users:*
  Total: {total_users}
  Banned: {banned}
  Pending: {pending_approval}
  Approved: {approved}
  Rejected: {rejected}

💃 *Pairing:*
  Searching: {active_finding}
  Matched: {pending_pair}
  Paired: {have_pair}
  Unpair Pending: {rejection_pending}

📈 *Activity:*
  Total Pairs: {total_pairs}
  Pair History: {total_pair_history}
  Total Likes: {total_likes}
  Total Skips: {total_skips}
"""

ADMIN_PROFILE_REVIEW = """
📋 *Profile #{user_id}*

👤 {first_name} {last_name}
📱 @{username}
🎂 {age} y/o | {gender_emoji} {gender}
{course_line}
{interests_line}
{about_line}
"""

ADMIN_APPROVED = """
✅ *Profile Approved!*

You're ready to find your waltz partner! 💃
Use 'Find Partner' to start matching! 💕
"""

ADMIN_REJECTED = """
❌ *Profile Not Approved*

Please edit and resubmit with /start 💫
"""

ADMIN_BANNED_NOTIF = """
🚫 *You have been banned*

Reason: {reason}
"""

ADMIN_UNPAIR_REQUEST = """
📨 *Unpair Request #{id}*

From: {requester_name} (@{requester_username})
Partner: {partner_name} (@{partner_username})

📝 Reason: {reason}
"""

ADMIN_BROADCAST_ASK = """
📢 *Broadcast Message*

Send the message you want to broadcast to all users.
Or tap Cancel to abort.
"""

ADMIN_BROADCAST_CONFIRM = """
📢 *Confirm Broadcast*

Your message:
{message}

Send to {count} users?
"""

ADMIN_BROADCAST_SENT = """
✅ *Broadcast Sent!*

Message delivered to {success}/{total} users.
"""

ADMIN_DM_ASK = """
💬 *Direct Message*

Enter user ID to message:
"""

ADMIN_DM_MESSAGE = """
💬 *Message to User #{user_id}*

Enter your message:
"""

ADMIN_DM_SENT = """
✅ Message sent to user #{user_id}!
"""

ADMIN_BOT_STOPPING = """
🛑 *Bot is stopping...*

Use /start_bot to restart.
"""

ADMIN_BOT_RESTARTING = """
🔄 *Bot is restarting...*

Please wait a moment.
"""

ADMIN_FROM_ADMIN = """
📬 *Message from Admin:*

{message}
"""

ADMIN_ALL_REVIEWED = """
✅ *All pending profiles reviewed!*

Great job! Check back later for new submissions. 💫
"""

# ==================== DELETE ACCOUNT ====================

DELETE_ACCOUNT_CONFIRM = """
⚠️ *Delete Account*

Are you sure you want to *permanently delete* your account?

This will:
• Delete all your profile data
• Remove you from any matches
• Delete all your likes and interactions
• This action *cannot be undone*

Type *DELETE* to confirm or tap Cancel.
"""

DELETE_ACCOUNT_SUCCESS = """
✅ *Account Deleted*

Your account and all data have been permanently deleted.

If you change your mind, you can always create a new account with /start

Goodbye! 👋
"""

DELETE_ACCOUNT_CANCELLED = """
💫 *Deletion Cancelled*

Your account is safe! Nothing was deleted.
"""

DELETE_ACCOUNT_PARTNER_NOTIF = """
💔 *Your partner deleted their account*

You've been unpaired and can search for a new partner.
"""

# ==================== ERRORS ====================

ERROR_GENERIC = """
😅 Oops! Something went wrong.

Please try again! 💫
"""

ERROR_NOT_REGISTERED = """
👋 You're not registered yet!

Tap /start to create your profile 💃
"""

ERROR_NOT_APPROVED = """
⏳ Your profile is pending approval.

Please wait for admin review! 💫
"""

ERROR_NOT_SEARCHING = """
🎭 You're not in search mode.

Check your current status! 💫
"""

ERROR_NO_PARTNER = """
💔 You don't have a partner yet.

Use 'Find Partner' to start matching! 💕
"""

ERROR_CANT_EDIT = """
⚠️ Can't edit profile while matched/paired.

Resolve your current status first! 💫
"""

# ==================== BUTTONS ====================

BTN_FIND_PARTNER = "💕 Find Partner"
BTN_MY_PROFILE = "👤 My Profile"
BTN_EDIT_PROFILE = "✏️ Edit Profile"
BTN_MY_FILTERS = "🎯 My Filters"
BTN_DELETE_ACCOUNT = "🗑️ Delete Account"
BTN_VIEW_MATCH = "💖 View Match"
BTN_MY_PARTNER = "💃 My Partner"
BTN_REQUEST_UNPAIR = "💔 Request Unpair"
BTN_CHECK_STATUS = "📋 Check Status"
BTN_CANCEL_REQUEST = "❌ Cancel Request"

BTN_LIKE = "💖 Like"
BTN_SKIP = "👋 Skip"
BTN_WANT_PAIR = "💃 I want to be paired!"
BTN_SEARCH_ANOTHER = "🔍 Search for another"

BTN_MALE = "🙋‍♂️ Male"
BTN_FEMALE = "🙋‍♀️ Female"
BTN_ANY = "💫 Any"
BTN_SKIP_SIMPLE = "⏭️ Skip"
BTN_SUBMIT = "✅ Submit"
BTN_CANCEL = "❌ Cancel"
BTN_YES_UNPAIR = "💔 Yes, request unpair"
BTN_NO_CANCEL = "💕 No, cancel"

# Admin buttons
BTN_ADMIN_PENDING = "📋 Pending Profiles"
BTN_ADMIN_REJECTIONS = "📨 Unpair Requests"
BTN_ADMIN_PAIRS = "💕 All Pairs"
BTN_ADMIN_STATS = "📊 Statistics"
BTN_ADMIN_BROADCAST = "📢 Broadcast"
BTN_ADMIN_DM = "💬 Direct Message"
BTN_ADMIN_BOT_CONTROL = "🎛️ Bot Control"

BTN_APPROVE = "✅ Approve"
BTN_REJECT = "❌ Reject"
BTN_BAN = "🚫 Ban"


# ==================== HELPER FUNCTIONS ====================

def get_gender_emoji(gender: str) -> str:
    """Get emoji for gender."""
    return "🙋‍♂️" if gender == "male" else "🙋‍♀️"


def get_gender_text(gender: str) -> str:
    """Get display text for gender."""
    return "Male" if gender == "male" else "Female"


def format_approval_status(status: str) -> str:
    """Format approval status with emoji."""
    statuses = {
        "pending": "⏳ Pending",
        "approved": "✅ Approved",
        "rejected": "❌ Rejected"
    }
    return statuses.get(status, status)


def format_pairing_status(status: str) -> str:
    """Format pairing status with emoji."""
    statuses = {
        "inactive": "💤 Inactive",
        "active_finding": "🔍 Searching",
        "pending_pair": "💕 Match Found!",
        "have_pair": "💖 Paired!",
        "rejection_pending": "⏳ Unpair Pending"
    }
    return statuses.get(status, status)


def build_optional_line(label: str, value: str, emoji: str = "") -> str:
    """Build optional profile line."""
    if value:
        return f"{emoji} {label}: {value}\n" if emoji else f"{label}: {value}\n"
    return ""