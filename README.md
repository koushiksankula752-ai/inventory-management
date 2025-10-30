# Inventory Management System

A comprehensive inventory management system built with Flask (backend) and Streamlit (frontend UI), featuring user authentication, CRUD operations, audit logging, and a REST API.

## Features

- **User Authentication**: Simple login system (admin/password)
- **Inventory Management**:
  - View all inventory items
  - Add new items
  - Edit existing items
  - Delete items
- **Audit Logging**: Tracks all create, update, and delete operations
- **Dual Interfaces**:
  - Web UI via Flask with HTML templates
  - Modern UI via Streamlit
- **REST API**: JSON endpoints for programmatic access
- **Database**: SQLite with SQLAlchemy ORM

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

## Installation

1. **Clone or download the project**:
   ```bash
   cd /path/to/your/project
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**:
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Database Setup

The application uses SQLite. The database file (`inventory.db`) will be created automatically when you first run the application.

## Running the Application

### Option 1: Streamlit UI (Recommended for modern interface)

```bash
streamlit run streamlit_app.py
```

Access the application at: http://localhost:8506

### Option 2: Flask Web UI

```bash
python app.py
```

Access the application at: http://localhost:5000

### Option 3: Flask API Only

The Flask app also serves as an API server. Run it as above and use tools like curl or Postman to interact with the API endpoints.

## Usage

### Login Credentials
- Username: `admin`
- Password: `password`

### Streamlit Interface
- Navigate through the sidebar menu
- View inventory in a table format
- Add, edit, or delete items using forms
- Check audit logs for activity history

### Flask Web Interface
- Login at the main page
- View items in a list
- Add new items via form
- Edit or delete items from the list view

## API Endpoints

### Get All Items
```http
GET /api/items
```

### Get Specific Item
```http
GET /api/items/{item_id}
```

### Create New Item
```http
POST /api/items
Content-Type: application/json

{
  "product_name": "Example Product",
  "sku": "EX123",
  "category": "Electronics",
  "quantity": 10,
  "supplier": "Example Supplier",
  "price": 29.99,
  "location": "Warehouse A"
}
```

### Update Item
```http
PUT /api/items/{item_id}
Content-Type: application/json

{
  "quantity": 15,
  "price": 34.99
}
```

### Delete Item
```http
DELETE /api/items/{item_id}
```

## Project Structure

```
inventory-project/
├── app.py                 # Flask application
├── streamlit_app.py       # Streamlit application
├── models.py              # Database models
├── forms.py               # WTForms definitions
├── requirements.txt       # Python dependencies
├── inventory.db           # SQLite database (created automatically)
├── templates/             # Flask HTML templates
│   ├── base.html
│   ├── login.html
│   ├── list.html
│   ├── add.html
│   └── edit.html
├── static/                # Static files (CSS, JS, images)
│   └── style.css
├── venv/                  # Virtual environment (created during setup)
└── README.md              # This file
```

## Development

To modify the application:

1. Edit the relevant Python files
2. Restart the application
3. For database changes, update `models.py` and recreate the database (delete `inventory.db` and rerun)

## Security Notes

- This is a demo application with hardcoded credentials
- For production use, implement proper authentication and authorization
- Change the SECRET_KEY in `app.py` for production
- Use environment variables for sensitive data

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the MIT License.
