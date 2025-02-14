
## Installation

1. Venv
    ```sh
    virtualenv .venv
    ```

2. Python requirements
    ```sh
    make install
    ```

3. DB container start and migrate:
    ```sh
    make restart
    make migrate
    ```

## Running the Application

1. **Start the development server:**
    ```sh
    make run
    ```

## Testing

1. **Run tests with coverage:**
    ```sh
    make test
    ```
2. **Run linters:**
   ```sh
   make isort-check
   make black-check
   make flake8
   ```