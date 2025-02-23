from typing import Optional

from pydantic import BaseModel


class UpdateUser(BaseModel):
    email: Optional[str] = None
    fio: Optional[str] = None


def main():
    d = {
        "email": None,
    }

    u = UpdateUser(**d)
    print(u.model_dump(exclude_unset=True))


if __name__ == "__main__":
    main()
