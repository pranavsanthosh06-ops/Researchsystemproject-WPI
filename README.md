CS 3733 Term Project


Project Title: ResearchConnect


The application provides a centralized system for managing research-related information and workflows using a Flask-based backend, database integration, and a web interface.
1. Clone the repository
git clone https://github.com/pranavsanthosh06-ops/Researchsystemproject-WPI.git
Move into the project folder:
cd Researchsystemproject-WPI
2. Create a virtual environment
python3 -m venv venv
Activate it:
source venv/bin/activate
3. Install packages
pip install -r requirements.txt
4. Set up the database
Apply the existing database migrations:
flask db upgrade
5. Run the application
Start the Flask application:
flask run
Open the local address Can I udisplayed by Flask in your browser.
6. Run with Docker
Build the Docker image:
docker build -t researchconnect .
Run the container:
docker run -p 3001:3001 researchconnect
The application is configured to run on port:
3001

