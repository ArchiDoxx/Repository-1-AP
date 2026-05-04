# FastAPI Learning Project

This repository contains a learning project built with FastAPI, focusing on building RESTful APIs efficiently. Below you'll find instructions on setting up the project, details about the project structure, architectural insights, and examples of API usage.

## Table of Contents
- [Setup Instructions](#setup-instructions)
- [Project Structure](#project-structure)
- [Architecture Details](#architecture-details)
- [API Usage Examples](#api-usage-examples)

## Setup Instructions
1. **Clone the Repository**
   ```bash
   git clone https://github.com/ArchiDoxx/Repository-1-AP.git
   cd Repository-1-AP
   ```
2. **Create a Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate    # On Windows use `venv\Scripts\activate`
   ```
3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```
4. **Run the Application**
   ```bash
   uvicorn app.main:app --reload
   ```
   The API will be accessible at `http://127.0.0.1:8000`.

## Project Structure
```
Repository-1-AP/
│
├── app/
│   ├── main.py           # Entry point of the FastAPI application
│   ├── api/              # Directory for API route handlers
│   ├── models/           # Data models for Pydantic
│   ├── db/              # Database connection and models
│   └── services/         # Business logic
│
├── requirements.txt      # Project dependencies
└── README.md             # Project documentation
```

## Architecture Details
This project adopts a layered architecture approach:
- **API Layer**: Handles incoming requests and responses. Defined in the `api` directory.
- **Model Layer**: Contains Pydantic models for data validation. Found in the `models` directory.
- **Database Layer**: Responsible for database interactions. Models and connections are set up in the `db` directory.
- **Service Layer**: Contains the business logic and functions that are called by the API layer. Located in the `services` directory.

## API Usage Examples
- **Get All Items**
    - **Request**:  `GET /items`
    - **Response**:
      ```json
      [
        { "id": 1, "name": "Item 1" },
        { "id": 2, "name": "Item 2" }
      ]
      ```

- **Create a New Item**
    - **Request**: `POST /items`
    - **Body**:
      ```json
      { "name": "New Item" }
      ```
    - **Response**:
      ```json
      { "id": 3, "name": "New Item" }
      ```

- **Get Item by ID**
    - **Request**: `GET /items/{id}`
    - **Response**:
      ```json
      { "id": 1, "name": "Item 1" }
      ```

For more details, navigate to `http://127.0.0.1:8000/docs` for the automatically generated API documentation (Swagger UI).