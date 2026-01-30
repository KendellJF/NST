# NST Giveaway App

A Flask-based event giveaway application with JWT authentication and random winner selection.

## Features

- Event check-in with attendee names and Instagram handles
- Admin panel with JWT authentication
- Random winner selection (4 winners)
- Animated winners display page
- CSV export of attendee data
- Responsive party-themed UI

## Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd NST
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set environment variables** (create `.env` file)
   ```
   SECRET_KEY=your-secret-key
   JWT_SECRET=your-jwt-secret
   ADMIN_USERNAME=admin
   ADMIN_PASSWORD=your-password
   FLASK_ENV=development
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

   The app will be available at `http://localhost:5000`

## Deployment on Render

### Option 1: Using render.yaml (Recommended)

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

2. **Create Render Account**
   - Go to https://render.com
   - Sign up with GitHub

3. **Deploy from GitHub**
   - Click "New +" → "Blueprint"
   - Connect your GitHub repository
   - Click "Apply"
   - Render will automatically deploy using `render.yaml`

4. **Set Environment Variables**
   - Go to your service settings in Render dashboard
   - Set the following variables:
     - `SECRET_KEY` - Generate a random string
     - `JWT_SECRET` - Generate a random string
     - `ADMIN_PASSWORD` - Your admin password
     - `DATABASE_URL` - Will be set automatically if using PostgreSQL

### Option 2: Manual Deployment

1. **Create new Web Service on Render**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Choose Python as the environment

2. **Configure Build & Deploy**
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn wsgi:app`

3. **Add Environment Variables**
   - Set all required env vars in the Render dashboard

4. **Deploy**
   - Click "Create Web Service"

## Usage

### Public Page (Check-in)
- Navigate to `/` to access the check-in form
- Enter first name, last name, and Instagram handle
- Click "CHECK IN" to join the giveaway

### Admin Panel
- Navigate to `/admin` to access the admin panel
- Login with your admin credentials
- Features:
  - **Run Draw**: Randomly select 4 winners
  - **Reset Selection**: Clear all selections to run another draw
  - **Attendee List**: View all entries with selection status
  - **Export CSV**: Download attendee data

### Winners Page
- Navigate to `/winners` to see the selected winners
- Page auto-updates every 5 seconds

## API Endpoints

### Public
- `GET /` - Check-in page
- `POST /submit` - Submit attendee entry
- `GET /winners` - Winners display page
- `GET /api/winners` - Get selected winners (JSON)
- `GET /healthz` - Health check

### Admin (JWT Protected)
- `GET /admin` - Admin panel
- `POST /admin/auth/login` - Login and get JWT token
- `POST /admin/draw` - Run the draw
- `POST /admin/reset` - Reset all selections
- `GET /admin/attendees` - Get all attendees (JSON)
- `GET /admin/export` - Export attendees as CSV

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Flask secret key | 'dev-secret' |
| `JWT_SECRET` | JWT signing secret | 'change-me' |
| `JWT_ALGORITHM` | JWT algorithm | 'HS256' |
| `JWT_EXP_MINUTES` | JWT expiration time in minutes | 60 |
| `ADMIN_USERNAME` | Admin login username | 'admin' |
| `ADMIN_PASSWORD` | Admin login password | 'password' |
| `DATABASE_URL` | Database connection URL | SQLite (local) |
| `FLASK_ENV` | Flask environment | 'development' |
| `PORT` | Server port | 5000 |
| `INITIAL_CSV_ON_STARTUP` | Import CSV on startup | '0' |

## Database

- **Development**: SQLite (`instance/app.db`)
- **Production**: PostgreSQL (recommended for Render)

## Technologies

- Flask 2.0+
- Flask-SQLAlchemy 3.0+
- PyJWT 2.6+
- Gunicorn 20.1+
- SQLite / PostgreSQL

## License

MIT
