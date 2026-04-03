import factory

from app.core.security import get_password_hash
from app.items.models import Comment, Item
from app.swaps.models import Swap
from app.users.models import User

# Pre-calculate to save test runtime
DEFAULT_PASSWORD = "testpassword123!"
DEFAULT_HASH = get_password_hash(DEFAULT_PASSWORD)


class BaseFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        abstract = True
        sqlalchemy_session = None  # Will be set in conftest.py or tests
        sqlalchemy_session_persistence = "commit"


class UserFactory(BaseFactory):
    class Meta:
        model = User

    email = factory.Sequence(lambda n: f"user{n}@example.com")
    hashed_password = DEFAULT_HASH
    full_name = factory.Faker("name")
    is_active = True
    is_admin = False


class ItemFactory(BaseFactory):
    class Meta:
        model = Item

    title = factory.Faker("sentence", nb_words=4)
    description = factory.Faker("paragraph")
    estimated_price = factory.Faker(
        "pyfloat", positive=True, min_value=10, max_value=1000
    )
    image_url = None
    city = "Cairo"
    category = "Electronics"
    transaction_type = "Swap"
    owner = factory.SubFactory(UserFactory)


class CommentFactory(BaseFactory):
    class Meta:
        model = Comment

    text = factory.Faker("sentence")
    item = factory.SubFactory(ItemFactory)
    author = factory.SubFactory(UserFactory)


class SwapFactory(BaseFactory):
    class Meta:
        model = Swap

    requester = factory.SubFactory(UserFactory)
    responder = factory.SubFactory(UserFactory)
    offered_item = factory.SubFactory(
        ItemFactory, owner=factory.SelfAttribute("..requester")
    )
    requested_item = factory.SubFactory(
        ItemFactory, owner=factory.SelfAttribute("..responder")
    )
    status = "Pending"


from app.chat.models import ChatRoom, Message


class ChatRoomFactory(BaseFactory):
    class Meta:
        model = ChatRoom

    swap = factory.SubFactory(SwapFactory, status="Accepted")


class MessageFactory(BaseFactory):
    class Meta:
        model = Message

    room = factory.SubFactory(ChatRoomFactory)
    sender = factory.SubFactory(UserFactory)
    content = factory.Faker("sentence")
