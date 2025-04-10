# VeeGo - Visa Assistant

VeeGo is an AI-powered visa assistant that helps users with visa-related queries and passport validity checks.

## Features

- AI-powered visa assistance
- Passport validity checker
- Interactive chat interface
- Modern and responsive design

## Local Development

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the application:
   ```bash
   python app.py
   ```

## Deployment on Render

1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Configure the following settings:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
   - Environment Variables:
     - Add any required environment variables from your `.env` file

## Project Structure

```
├── app.py              # Main application file
├── static/             # Static files (CSS, JS, images)
├── templates/          # HTML templates
├── requirements.txt    # Python dependencies
├── Procfile           # Process file for Render
└── README.md          # Project documentation
```

## License

MIT License 