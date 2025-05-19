# Shopping Mall Project

This project is an application for managing an online store (shopping mall) developed with the Django Framework.

## Installation

Follow these steps to set up the development environment for the project:

1.  **Create and Activate a Virtual Environment:**
    It is recommended to use a virtual environment to manage project dependencies.

    *   Open your Terminal or Command Prompt.
    *   Navigate to the directory where you want to create the project.
    *   Create a virtual environment (named `venv` in this example):
        ```bash
        python -m venv venv
        ```
    *   Activate the virtual environment:
        *   **On Windows:**
            ```bash
            venv\Scripts\activate
            ```
        *   **On macOS and Linux:**
            ```bash
            source venv/bin/activate
            ```
        You will see the virtual environment's name (e.g., `(venv)`) appear at the beginning of your prompt.

2.  **Install Django and Other Dependencies:**
    Once the virtual environment is activated, use `pip` to install Django and any other necessary dependencies for the project (if a `requirements.txt` file exists):

    *   Install Django:
        ```bash
        pip install django
        ```
    *   (If applicable) Install dependencies from `requirements.txt`:
        ```bash
        pip install -r requirements.txt
        ```

3.  **Set up the Django Project (if necessary):**
    *   Apply database migrations:
        ```bash
        python manage.py migrate
        ```
    *   Create a superuser (for accessing the admin panel):
        ```bash
        python manage.py createsuperuser
        ```

4.  **Run the Development Server:**
    ```bash
    python manage.py runserver
    ```
    Then, open your web browser and navigate to `http://127.0.0.1:8000/`.

- Aoranun Rojsatitpong