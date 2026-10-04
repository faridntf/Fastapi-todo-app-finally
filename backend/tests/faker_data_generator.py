from faker import Faker
from core import SessionLocal
from sqlalchemy.orm import Session
from users import UserModel
from profiles import ProfileModel
from tasks import TaskModel

db1 = SessionLocal()

faker = Faker()

#create fake user
def seed_users(db: Session):
    new_users = []
    for _ in range(2):
        user = UserModel(
            username = faker.user_name(),
            email = faker.email(),
            phone_number = faker.random_digit()
        )
        user.set_password(faker.password(5))
        new_users.append(user)
    db.add_all(new_users)
    db.commit()


# create task
def seed_tasks(db:Session):
    new_tasks = []
    for _ in range(10):
        task = TaskModel(
            title = faker.text(100),
            description = faker.text(500),
            category_id_fk = 1
        )
        new_tasks.append(task)
    db.add_all(new_tasks)
    
    db.commit()



def main():
    seed_users(db=db1)
    seed_tasks(db=db1)


if __name__ == "__main__":
    main()