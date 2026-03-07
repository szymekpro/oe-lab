## How to run the Flask backend

1. Go to the backend directory:
   ```powershell
   cd oe-backend
   ```
2. Create and activate a virtual environment:
   ```powershell
   python -m venv venv
   .\venv\Scripts\activate
   ```
3. Install the required dependencies:
   ```powershell
   pip install -r requirements.txt
   ```
4. Run the Flask application:
   ```powershell
   python app.py
   ```

## API INFO

The application will be available by default at: http://127.0.0.1:5000/


After starting the Flask backend, open your web browser and go to:

```
http://127.0.0.1:5000/api/docs
```

This page contains the interactive API documentation (Swagger UI) for testing and exploring the available endpoints.
