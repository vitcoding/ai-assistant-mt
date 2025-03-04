import typer

from db.postgres import sync_session
from models.user import User
from schemas.user import AdminCreate
from services.auth import AuthPasswordService

app = typer.Typer()


@app.command()
def create_superuser(login: str, password: str):
    try:
        user_create = AdminCreate(
            login=login,
            password=password,
            first_name="admin",
            last_name="admin",
            role="admin",
        )
        admin = user_create.model_dump()
        hashed_password = AuthPasswordService.get_password_hash(
            admin["password"]
        )
        admin["password"] = hashed_password
        user_db = User(**admin)
        with sync_session() as session:
            session.add(user_db)
            session.commit()
            print(f"Admin user {login} created successfully")
    except Exception as e:
        print(f"Failed to create admin user {login}. Error: {str(e)}")


if __name__ == "__main__":
    app()
