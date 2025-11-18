# CP360 API Documentation

## Base URL
```
http://localhost:8000/api
```

## Authentication
All authenticated endpoints require JWT token in the Authorization header:
```
Authorization: Bearer <access_token>
```

## Response Format
All API responses follow this structure:
```json
{
  "message": "Success message",
  "data": { ... },
  "tokens": { ... }  // Only for login
}
```

Error responses:
```json
{
  "detail": "Error message",
  "errors": { ... }  // Validation errors
}
```

---

## Authentication Endpoints

### 1. Register User
**POST** `/api/users/register/`

Register a new user account. Only admins can create admin users.

**Request Body:**
```json
{
  "email": "user@example.com",
  "username": "johndoe",
  "phone": "1234567890",
  "password": "password123",
  "first_name": "John",
  "last_name": "Doe",
  "role": "end_user"  // Optional: "end_user", "staff", "admin" (admin only)
}
```

**Response:** `201 Created`
```json
{
  "message": "User registered successfully.",
  "data": {
    "id": 1,
    "email": "user@example.com",
    "username": "johndoe",
    "phone": "1234567890",
    "first_name": "John",
    "last_name": "Doe",
    "role": "end_user",
    "is_active": true,
    "is_verified": false,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
}
```

**Validation Rules:**
- Email: Valid email format, unique
- Username: 1-50 chars, alphanumeric with .-_ allowed, unique
- Phone: 8-12 digits, unique
- Password: 6-50 characters
- First/Last name: Letters only, max 50 chars
- Role: Only admins can create admin users

---

### 2. Login
**POST** `/api/users/login/`

Login for all user roles (Admin, Staff, End User).

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:** `200 OK`
```json
{
  "message": "Login successful. Welcome johndoe.",
  "data": {
    "id": 1,
    "email": "user@example.com",
    "username": "johndoe",
    "phone": "1234567890",
    "first_name": "John",
    "last_name": "Doe",
    "role": "end_user",
    "is_active": true,
    "is_verified": true,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  },
  "tokens": {
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }
}
```

**Error Responses:**
- `400 Bad Request`: Invalid credentials
- `400 Bad Request`: Email not verified
- `400 Bad Request`: Account disabled

---

### 3. Get Profile
**GET** `/api/users/profile/`

Get current user's profile information.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "johndoe",
  "phone": "1234567890",
  "first_name": "John",
  "last_name": "Doe",
  "role": "end_user",
  "is_active": true,
  "is_verified": true,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

---

### 4. Update Profile
**PATCH** `/api/users/profile/`

Update current user's profile. Users can update their own profile.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "email": "newemail@example.com",
  "username": "newusername",
  "phone": "9876543210",
  "first_name": "Jane",
  "last_name": "Smith"
}
```

**Response:** `200 OK`
```json
{
  "message": "Profile updated successfully.",
  "data": {
    "id": 1,
    "email": "newemail@example.com",
    "username": "newusername",
    ...
  }
}
```

**Note:** Role cannot be changed by users.

---

### 5. Change Password
**POST** `/api/users/profile/password/`

Change current user's password.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "old_password": "oldpassword123",
  "new_password": "newpassword456"
}
```

**Response:** `200 OK`
```json
{
  "message": "Password updated successfully."
}
```

**Error Responses:**
- `400 Bad Request`: Old password is incorrect

---

## Admin User Management Endpoints

### 6. Get/Update User (Admin)
**GET/PATCH** `/api/users/admin/users/<user_id>/`

Admin can view and update any user's profile (except other admins).

**Headers:**
```
Authorization: Bearer <admin_access_token>
```

**PATCH Request Body:**
```json
{
  "email": "updated@example.com",
  "username": "updateduser",
  "phone": "1111111111",
  "first_name": "Updated",
  "last_name": "Name",
  "role": "staff",
  "is_active": true
}
```

**Response:** `200 OK`
```json
{
  "id": 2,
  "email": "updated@example.com",
  "username": "updateduser",
  ...
}
```

**Error Responses:**
- `403 Forbidden`: Cannot modify another admin user

---

### 7. Update User Status (Admin)
**PATCH** `/api/users/admin/users/<user_id>/status/`

Admin can activate/deactivate users (except other admins).

**Headers:**
```
Authorization: Bearer <admin_access_token>
```

**Request Body:**
```json
{
  "is_active": false
}
```

**Response:** `200 OK`
```json
{
  "is_active": false
}
```

**Error Responses:**
- `403 Forbidden`: Cannot deactivate another admin user

---

## Category Endpoints

### 8. List Categories
**GET** `/api/categories/`

List all non-deleted categories. Supports pagination, filtering, and search.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 20)
- `search`: Search in category name
- `ordering`: Order by field (e.g., `-created_at`)

**Response:** `200 OK`
```json
{
  "count": 10,
  "next": "http://localhost:8000/api/categories/?page=2",
  "previous": null,
  "results": [
    {
      "category_id": "uuid-here",
      "name": "Electronics",
      "user": 1,
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z",
      "created_by": "admin@example.com",
      "updated_by": "admin@example.com",
      "products_count": 5,
      "is_deleted": false
    }
  ]
}
```

---

### 9. Create Category
**POST** `/api/categories/`

Create a new category. Requires Agent, Staff, or Admin role.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "name": "Electronics"
}
```

**Response:** `201 Created`
```json
{
  "category_id": "uuid-here",
  "name": "Electronics",
  "user": 1,
  ...
}
```

**Validation:**
- Name: Max 50 characters, required

---

### 10. Get Category Detail
**GET** `/api/categories/<category_id>/`

Get detailed information about a specific category.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:** `200 OK`
```json
{
  "category_id": "uuid-here",
  "name": "Electronics",
  "user": 1,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z",
  "created_by": "admin@example.com",
  "updated_by": "admin@example.com",
  "products_count": 5,
  "is_deleted": false
}
```

---

### 11. Update Category
**PATCH** `/api/categories/<category_id>/`

Update a category. Requires Agent, Staff, or Admin role.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "name": "Updated Electronics"
}
```

**Response:** `200 OK`
```json
{
  "category_id": "uuid-here",
  "name": "Updated Electronics",
  ...
}
```

---

### 12. Delete Category
**DELETE** `/api/categories/<category_id>/`

Soft delete a category and all its products. Requires Agent, Staff, or Admin role.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:** `204 No Content`

---

### 13. Restore Category
**POST** `/api/categories/<category_id>/restore/`

Restore a soft-deleted category. Requires Agent, Staff, or Admin role.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:** `200 OK`
```json
{
  "category_id": "uuid-here",
  "name": "Electronics",
  "is_deleted": false,
  ...
}
```

---

### 14. Export Categories
**GET** `/api/categories/export/`

Export categories to CSV format.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `include_products`: Include product data (true/false, default: false)
- `product_ids`: Filter specific products (comma-separated IDs)

**Response:** `200 OK` (CSV file)
```
category_id,name,user_email,created_at,updated_at
uuid-here,Electronics,admin@example.com,2024-01-01,2024-01-01
```

---

## Product Endpoints

### 15. List Products
**GET** `/api/products/`

List all non-deleted products. Supports pagination, filtering, and search.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `page`: Page number
- `page_size`: Items per page
- `search`: Search in title/description
- `status`: Filter by status (uploaded, rejected, success, cancelled)
- `category`: Filter by category ID
- `ordering`: Order by field

**Response:** `200 OK`
```json
{
  "count": 25,
  "next": "http://localhost:8000/api/products/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "category": 1,
      "title": "Product Name",
      "description": "Product description",
      "price": "99.99",
      "status": "uploaded",
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z",
      "created_by": "user@example.com",
      "updated_by": "user@example.com",
      "videos": [
        {
          "id": 1,
          "file": "http://localhost:8000/media/products/1/videos/video.mp4",
          "uploaded_at": "2024-01-01T00:00:00Z"
        }
      ],
      "is_deleted": false
    }
  ]
}
```

---

### 16. Create Product
**POST** `/api/products/`

Create a new product with optional video files. Videos are processed via Celery/RabbitMQ. Requires Agent, Staff, or Admin role.

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: multipart/form-data
```

**Request Body (Form Data):**
```
category: 1
title: Product Name
description: Product description
price: 99.99
status: uploaded
video_files: [file1.mp4, file2.mp4]
```

**Response:** `201 Created`
```json
{
  "id": 1,
  "category": 1,
  "title": "Product Name",
  "description": "Product description",
  "price": "99.99",
  "status": "uploaded",
  "videos": [
    {
      "id": 1,
      "file": "http://localhost:8000/media/products/1/videos/video.mp4",
      "uploaded_at": "2024-01-01T00:00:00Z"
    }
  ],
  ...
}
```

**Validation:**
- Title: Max 50 characters, required
- Description: Max 251 characters
- Price: Must be >= 0
- Status: Must be one of: uploaded, rejected, success, cancelled
- Video files: Each file max 20 MB, total max 20 MB per product

**Note:** Video files are automatically processed via Celery task after upload.

---

### 17. Get Product Detail
**GET** `/api/products/<product_id>/`

Get detailed information about a specific product.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "category": 1,
  "title": "Product Name",
  "description": "Product description",
  "price": "99.99",
  "status": "uploaded",
  "videos": [...],
  ...
}
```

---

### 18. Update Product
**PATCH** `/api/products/<product_id>/`

Update a product. Can add additional video files. Requires Agent, Staff, or Admin role.

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: multipart/form-data
```

**Request Body (Form Data):**
```
title: Updated Product Name
price: 149.99
video_files: [new_video.mp4]
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "title": "Updated Product Name",
  "price": "149.99",
  ...
}
```

---

### 19. Delete Product
**DELETE** `/api/products/<product_id>/`

Soft delete a product. Requires Agent, Staff, or Admin role.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:** `204 No Content`

---

### 20. Restore Product
**POST** `/api/products/<product_id>/restore/`

Restore a soft-deleted product. Requires Agent, Staff, or Admin role.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "is_deleted": false,
  ...
}
```

---

### 21. Approve Product
**POST** `/api/products/<product_id>/approve/`

Approve a product (changes status to "success"). Requires Staff or Admin role.

**Headers:**
```
Authorization: Bearer <staff_or_admin_access_token>
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "status": "success",
  ...
}
```

**Error Responses:**
- `403 Forbidden`: Not authorized (only Staff/Admin)

---

### 22. Reject Product
**POST** `/api/products/<product_id>/reject/`

Reject a product (changes status to "rejected"). Requires Staff or Admin role.

**Headers:**
```
Authorization: Bearer <staff_or_admin_access_token>
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "status": "rejected",
  ...
}
```

**Error Responses:**
- `403 Forbidden`: Not authorized (only Staff/Admin)

---

### 23. Export Products
**GET** `/api/products/export/`

Export products to CSV format.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `product_ids`: Filter specific products (comma-separated IDs)

**Response:** `200 OK` (CSV file)
```
id,category_id,title,description,price,status,created_at,updated_at
1,uuid-here,Product Name,Description,99.99,uploaded,2024-01-01,2024-01-01
```

---

## User Roles

- **end_user**: Regular user, can create/update own profile, create products
- **staff**: Can approve/reject products, manage categories
- **admin**: Full access, can create admin users, manage all users

---

## Status Codes

- `200 OK`: Request successful
- `201 Created`: Resource created successfully
- `204 No Content`: Request successful, no content to return
- `400 Bad Request`: Validation error or invalid request
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

---

## Video Processing

When products are created/updated with video files:
1. Videos are uploaded and saved to the database
2. Celery tasks are automatically dispatched to RabbitMQ
3. Videos are processed asynchronously (transcoding, thumbnails, metadata)
4. Processing happens in the background without blocking the API response

---

## Pagination

All list endpoints support pagination:
- Default page size: 20 items
- Use `page` query parameter to navigate
- Response includes `count`, `next`, `previous`, and `results`

---

## Filtering & Search

List endpoints support:
- **Search**: Use `search` parameter for text search
- **Filtering**: Use field-specific query parameters
- **Ordering**: Use `ordering` parameter (e.g., `-created_at` for descending)

---

## Notes

- All timestamps are in UTC
- Soft-deleted resources are excluded from list views but can be restored
- JWT tokens expire after 30 minutes (access) or 1 day (refresh)
- Video processing is asynchronous via Celery/RabbitMQ
- File uploads use multipart/form-data content type

