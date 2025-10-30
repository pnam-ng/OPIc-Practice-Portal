# Admin Features Guide

This document describes the admin panel features for managing users in the OPIc Practice Portal.

## Overview

The admin panel provides comprehensive user management capabilities including:
- View all users with detailed statistics
- Toggle admin privileges
- Reset user passwords
- Delete user accounts
- Export user data to CSV
- Filter and search users

## Access

**URL**: `/admin/users`

**Requirements**: 
- Must be logged in
- Must have admin privileges (`is_admin = True`)

## Features

### 1. User List View

The main admin dashboard displays all users in a table format with the following information:

| Column | Description |
|--------|-------------|
| **ID** | Unique user identifier |
| **User** | Username and full name (admin users have a crown icon 👑) |
| **Email** | User's email address |
| **Lang** | Target language (English, Korean, etc.) |
| **Streak** | Current practice streak count |
| **Responses** | Total number of responses submitted |
| **Surveys** | Total number of surveys completed |
| **Role** | User or Admin badge |
| **Created** | Account creation date |
| **Last Active** | Last activity date |
| **Actions** | Management buttons |

Admin users are highlighted with a special background color.

### 2. Search and Filter

**Search Bar**:
- Search by username, email, or full name
- Case-insensitive partial matching

**Language Filter**:
- Filter by target language (English, Korean, All)

**Sorting Options**:
- Sort by: Created date, Username, Email, Response count
- Order: Ascending or Descending

**Pagination**:
- 20 users per page (default)
- Navigate with page controls

### 3. Toggle Admin Privileges

**Button**: Green "Grant Admin" or Red "Revoke Admin"

**Function**:
- Promotes a regular user to admin
- Demotes an admin to regular user

**Restrictions**:
- Cannot change your own admin status
- Requires confirmation

**How to Use**:
1. Click the "Grant Admin" or "Revoke Admin" button
2. Confirm the action in the popup
3. The user's role will be updated immediately
4. The row will update to show the new status

### 4. Reset User Password

**Button**: Yellow key icon 🔑

**Function**:
- Reset any user's password to a new value
- Useful when users forget their passwords
- **Immediately invalidates the old password**

**How to Use**:
1. Click the yellow key icon button
2. Enter the new password in the prompt (minimum 6 characters)
3. Click OK to confirm
4. The password will be updated immediately
5. Old password becomes invalid instantly
6. User must log in with the new password

**Security Notes**:
- Minimum password length: 6 characters
- Password is hashed before storage
- Old password is immediately invalidated
- The system verifies the password change before confirming
- Database cache is cleared to ensure consistency
- Only admin can reset passwords
- No email notification (inform user separately)

**What Happens Internally**:
1. Old password hash is stored for verification
2. New password is hashed
3. System verifies hash changed
4. Changes are flushed to database
5. Database session cache is cleared
6. System re-queries user to verify
7. New password is tested before confirming
8. Only returns success if all steps pass

### 5. Delete User

**Button**: Red trash icon 🗑️

**Function**:
- Permanently delete a user account
- Cascades to delete all related data:
  - All responses
  - All surveys
  - All other user data

**Restrictions**:
- Cannot delete your own account
- Requires typing "DELETE" to confirm

**How to Use**:
1. Click the red trash icon button
2. Read the warning message
3. Type "DELETE" (exactly, case-sensitive)
4. Click OK to confirm
5. The user row will fade out and be removed

**⚠️ WARNING**: This action is permanent and cannot be undone!

### 6. Export to CSV

**Button**: "Export CSV" button at the top

**Function**:
- Export all users (or filtered users) to a CSV file
- Includes all user data and statistics

**CSV Format**:
```
id,username,email,name,target_language,is_admin,streak_count,responses_count,surveys_count,created_at,last_active_date
```

**How to Use**:
1. Apply any filters you want (optional)
2. Click "Export CSV" button
3. File will download automatically
4. Open in Excel, Google Sheets, or any CSV viewer

### 7. JSON API

**Endpoint**: `/admin/api/users`

**Method**: GET

**Parameters**:
- `page`: Page number (default: 1)
- `per_page`: Items per page (default: 20, max: 100)

**Response**:
```json
{
  "total": 100,
  "page": 1,
  "per_page": 20,
  "items": [
    {
      "id": 1,
      "username": "john_doe",
      "email": "john@example.com",
      "name": "John Doe",
      "target_language": "english",
      "is_admin": false,
      "streak_count": 5,
      "responses_count": 23,
      "surveys_count": 2,
      "created_at": "2024-01-15T10:30:00",
      "last_active_date": "2024-01-20"
    }
  ]
}
```

## User Interface

### Visual Indicators

1. **Admin Users**:
   - Highlighted row background (yellow/amber)
   - Crown icon (👑) next to username
   - Green "Admin" badge
   - Special border on the left

2. **Regular Users**:
   - Normal row background
   - Gray "User" badge

3. **Current User**:
   - Shows "🔒 You" instead of action buttons
   - Cannot modify own account

### Responsive Design

The admin panel is fully responsive:

**Desktop**:
- All columns visible
- Full button text
- Horizontal action buttons

**Tablet**:
- Condensed columns
- Icon-based buttons
- Horizontal scrolling if needed

**Mobile**:
- Smaller fonts
- Icon-only buttons
- Vertical scrolling
- Touch-friendly buttons

## Security Features

1. **Authentication Required**: Must be logged in to access

2. **Authorization Required**: Must have `is_admin = True`

3. **Self-Protection**: Cannot delete or demote yourself

4. **Confirmation Required**: All destructive actions require confirmation

5. **Audit Trail**: Flash messages show success/failure of actions

6. **Password Security**: Passwords are hashed using Werkzeug's secure methods

7. **CSRF Protection**: All POST requests are protected (via Flask-WTF)

## Best Practices

### For Admins

1. **Creating Admins**:
   - Only grant admin to trusted users
   - Review admin list regularly
   - Use the toggle feature to quickly revoke if needed

2. **Resetting Passwords**:
   - Use strong passwords (8+ characters recommended)
   - Include letters, numbers, and symbols
   - Inform users of their new password securely (not via email)
   - Advise users to change password after first login

3. **Deleting Users**:
   - Export user data first (if needed for records)
   - Confirm user is truly inactive/problematic
   - Type "DELETE" carefully (case-sensitive)
   - Verify correct user before deleting

4. **Regular Maintenance**:
   - Review inactive users monthly
   - Export user data for backup
   - Monitor response/survey counts for anomalies

### For Developers

1. **Adding New Admin Features**:
   - Use `@admin_required` decorator
   - Add proper error handling
   - Return JSON for AJAX actions
   - Update this guide

2. **Database Changes**:
   - User model has cascade delete configured
   - Changes propagate to responses and surveys
   - Test cascades carefully

3. **Security Considerations**:
   - Always check `current_user.id != user_id` for self-actions
   - Validate all inputs (especially passwords)
   - Use database transactions for multi-step operations
   - Log admin actions (future enhancement)

## Troubleshooting

### Problem: "403 Forbidden" error
**Solution**: Ensure your account has `is_admin = True` in the database

### Problem: Cannot see admin panel
**Solution**: Navigate to `/admin/users` while logged in as admin

### Problem: Delete not working
**Solution**: Make sure you type "DELETE" exactly (case-sensitive)

### Problem: Old password still works after reset
**Solution**: This should NOT happen with the current implementation. If it does:
1. Check the Flask logs for any error messages
2. Verify the database is not read-only
3. Run the test script: `python scripts/test_password_reset.py`
4. Check if SQLAlchemy is properly configured
5. Ensure the database file is writable
6. Try restarting the Flask application

**The fix includes**:
- Hash verification before commit
- Database flush to ensure write
- Session cache clearing (`expire_all`)
- Re-query from database to verify
- Password test before confirming success

### Problem: Password reset not working
**Solution**: 
- Ensure password is at least 6 characters long
- Check if you get a specific error message
- Verify the user account exists
- Check Flask logs for detailed error

### Problem: Changes not showing
**Solution**: Refresh the page or check browser console for errors

## API Endpoints Summary

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/admin/users` | View user list (HTML) |
| GET | `/admin/users.csv` | Export users to CSV |
| GET | `/admin/api/users` | Get users as JSON |
| POST | `/admin/users/<id>/toggle-admin` | Toggle admin status |
| POST | `/admin/users/<id>/reset-password` | Reset user password |
| POST | `/admin/users/<id>/delete` | Delete user account |

## Future Enhancements

Potential improvements for future versions:

1. **Audit Log**: Track all admin actions with timestamps
2. **Bulk Actions**: Delete/modify multiple users at once
3. **User Roles**: More granular permissions beyond admin/user
4. **Email Notifications**: Notify users of password resets
5. **Advanced Filters**: Filter by date range, streak count, etc.
6. **User Activity**: View detailed activity logs per user
7. **Two-Factor Auth**: Require 2FA for admin actions
8. **Password Policy**: Enforce complex password requirements

## Related Files

- **Backend**: `app/blueprints/admin.py`
- **Template**: `templates/admin/user_list.html`
- **Models**: `app/models.py` (User, Response, Survey)
- **Base Template**: `templates/base.html`

## Support

For issues or questions about the admin panel:
1. Check this guide
2. Review the browser console for JavaScript errors
3. Check Flask logs for backend errors
4. Ensure database migrations are up to date


