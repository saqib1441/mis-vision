from enum import Enum
from bson import ObjectId
from pydantic import BaseModel, ConfigDict, field_serializer
from pydantic_core import core_schema


class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler):
        def objectid_validator(v: str | ObjectId) -> ObjectId:
            if isinstance(v, ObjectId):
                return v

            if not isinstance(v, str):
                raise TypeError("ObjectId must be a string or ObjectId")

            if not ObjectId.is_valid(v):
                raise ValueError(f"Invalid ObjectId: {v}")

            return ObjectId(v)

        return core_schema.no_info_plain_validator_function(objectid_validator)

    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema, handler):
        return {
            "type": "string",
            "title": "ObjectId",
            "pattern": "^[0-9a-fA-F]{24}$",
            "examples": ["507f1f77bcf86cd799439011"],
        }


class BaseSchema(BaseModel):
    model_config = ConfigDict(
        extra="ignore",
        populate_by_name=True,
        str_strip_whitespace=True,
        use_enum_values=True,
    )

    @field_serializer("*", when_used="json")
    def serialize_object_ids(self, v):
        if isinstance(v, ObjectId):
            return str(v)
        return v


class TaskStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ModelType(str, Enum):
    DEFAULT_MODEL = "default_model"
    MULTILINGUAL_MODEL = "multilingual_model"
    TURBO_MODEL = "turbo_model"


class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class Role(str, Enum):
    ADMIN = "admin"
    USER = "user"


class Plans(str, Enum):
    FREE = "FREE"
    BASIC = "BASIC"
    STANDARD = "STANDARD"
    PREMIUM = "PREMIUM"


class VoiceLanguages(str, Enum):
    ARABIC = "ar"
    DANISH = "da"
    GERMAN = "de"
    GREEK = "el"
    ENGLISH = "en"
    SPANISH = "es"
    FINNISH = "fi"
    FRENCH = "fr"
    HEBREW = "he"
    HINDI = "hi"
    ITALIAN = "it"
    JAPANESE = "ja"
    KOREAN = "ko"
    MALAY = "ms"
    DUTCH = "nl"
    NORWEGIAN = "no"
    POLISH = "pl"
    PORTUGUESE = "pt"
    RUSSIAN = "ru"
    SWEDISH = "sv"
    SWAHILI = "sw"
    TURKISH = "tr"


voices_data = [
    {
        "name": "Donald Trump",
        "gender": "male",
        "language": "en",
        "url": "/voices/donald-trump.wav",
    },
    {
        "name": "Imran Khan",
        "gender": "male",
        "language": "en",
        "url": "/voices/imran-khan.wav",
    },
    {
        "name": "Elon Musk",
        "gender": "male",
        "language": "en",
        "url": "/voices/elon-musk.wav",
    },
    {
        "name": "Adam",
        "gender": "male",
        "language": "en",
        "url": "/voices/adam.wav",
    },
    {
        "name": "James Miller",
        "gender": "male",
        "language": "en",
        "url": "/voices/james-miller.mp3",
    },
    {
        "name": "Robert Wilson",
        "gender": "male",
        "language": "en",
        "url": "/voices/robert-wilson.mp3",
    },
    {
        "name": "Michael Taylor",
        "gender": "male",
        "language": "en",
        "url": "/voices/michael-taylor.mp3",
    },
    {
        "name": "David Anderson",
        "gender": "male",
        "language": "en",
        "url": "/voices/david-anderson.mp3",
    },
    {
        "name": "William Thomas",
        "gender": "male",
        "language": "en",
        "url": "/voices/william-thomas.mp3",
    },
    {
        "name": "Christopher Moore",
        "gender": "male",
        "language": "en",
        "url": "/voices/christopher-moore.mp3",
    },
    {
        "name": "Mary Johnson",
        "gender": "female",
        "language": "en",
        "url": "/voices/mary-johnson.mp3",
    },
    {
        "name": "Linda Davis",
        "gender": "female",
        "language": "en",
        "url": "/voices/linda-davis.mp3",
    },
    {
        "name": "João Silva",
        "gender": "male",
        "language": "pt",
        "url": "/voices/joão-silva.mp3",
    },
    {
        "name": "Ricardo Santos",
        "gender": "male",
        "language": "pt",
        "url": "/voices/ricardo-santos.mp3",
    },
    {
        "name": "Ana Ferreira",
        "gender": "female",
        "language": "pt",
        "url": "/voices/ana-ferreira.mp3",
    },
    {
        "name": "Beatriz Costa",
        "gender": "female",
        "language": "pt",
        "url": "/voices/beatriz-costa.mp3",
    },
    {
        "name": "Layla Rashid",
        "gender": "female",
        "language": "ar",
        "url": "/voices/layla-rashid.mp3",
    },
    {
        "name": "Fatima Zayed",
        "gender": "female",
        "language": "ar",
        "url": "/voices/fatima-zayed.mp3",
    },
    {
        "name": "Ahmed Mansour",
        "gender": "male",
        "language": "ar",
        "url": "/voices/ahmed-mansour.mp3",
    },
    {
        "name": "Omar Hassan",
        "gender": "male",
        "language": "ar",
        "url": "/voices/omar-hassan.mp3",
    },
    {
        "name": "Kim Min-jun",
        "gender": "male",
        "language": "ko",
        "url": "/voices/kim-min-jun.mp3",
    },
    {
        "name": "Lee Do-hyun",
        "gender": "male",
        "language": "ko",
        "url": "/voices/lee-do-hyun.mp3",
    },
    {
        "name": "Park Seo-yeon",
        "gender": "female",
        "language": "ko",
        "url": "/voices/park-seo-yeon.mp3",
    },
    {
        "name": "Choi Ji-woo",
        "gender": "female",
        "language": "ko",
        "url": "/voices/choi-ji-woo.mp3",
    },
    {
        "name": "Hiroshi Tanaka",
        "gender": "male",
        "language": "ja",
        "url": "/voices/hiroshi-tanaka.mp3",
    },
    {
        "name": "Kenji Sato",
        "gender": "male",
        "language": "ja",
        "url": "/voices/kenji-sato.mp3",
    },
    {
        "name": "Takumi Watanabe",
        "gender": "male",
        "language": "ja",
        "url": "/voices/takumi-watanabe.mp3",
    },
    {
        "name": "Akiko Kobayashi",
        "gender": "female",
        "language": "ja",
        "url": "/voices/akiko-kobayashi.mp3",
    },
    {
        "name": "Yuki Nakamura",
        "gender": "female",
        "language": "ja",
        "url": "/voices/yuki-nakamura.mp3",
    },
    {
        "name": "Dmitry Ivanov",
        "gender": "male",
        "language": "ru",
        "url": "/voices/dmitry-ivanov.mp3",
    },
    {
        "name": "Artem Sokolov",
        "gender": "male",
        "language": "ru",
        "url": "/voices/artem-sokolov.mp3",
    },
    {
        "name": "Elena Petrova",
        "gender": "female",
        "language": "ru",
        "url": "/voices/elena-petrova.mp3",
    },
    {
        "name": "Svetlana Morozova",
        "gender": "female",
        "language": "ru",
        "url": "/voices/svetlana-morozova.mp3",
    },
    {
        "name": "Carlos Rodriguez",
        "gender": "male",
        "language": "es",
        "url": "/voices/carlos-rodriguez.mp3",
    },
    {
        "name": "Alejandro Gomez",
        "gender": "male",
        "language": "es",
        "url": "/voices/alejandro-gomez.mp3",
    },
    {
        "name": "Diego Lopez",
        "gender": "male",
        "language": "es",
        "url": "/voices/diego-lopez.mp3",
    },
    {
        "name": "Lucia Fernandez",
        "gender": "female",
        "language": "es",
        "url": "/voices/lucia-fernandez.mp3",
    },
    {
        "name": "Isabella Martinez",
        "gender": "female",
        "language": "es",
        "url": "/voices/isabella-martinez.mp3",
    },
    {
        "name": "Julien Bernard",
        "gender": "male",
        "language": "fr",
        "url": "/voices/julien-bernard.mp3",
    },
    {
        "name": "Nicolas Morel",
        "gender": "male",
        "language": "fr",
        "url": "/voices/nicolas-morel.mp3",
    },
    {
        "name": "Chloé Dubois",
        "gender": "female",
        "language": "fr",
        "url": "/voices/chloe-dubois.mp3",
    },
    {
        "name": "Léa Fontaine",
        "gender": "female",
        "language": "fr",
        "url": "/voices/lea-fontaine.mp3",
    },
    {
        "name": "Lukas Müller",
        "gender": "male",
        "language": "de",
        "url": "/voices/lukas-muller.mp3",
    },
    {
        "name": "Stefan Schmidt",
        "gender": "male",
        "language": "de",
        "url": "/voices/stefan-schmidt.mp3",
    },
    {
        "name": "Hanna Wagner",
        "gender": "female",
        "language": "de",
        "url": "/voices/hanna-wagner.mp3",
    },
    {
        "name": "Emma Fischer",
        "gender": "female",
        "language": "de",
        "url": "/voices/emma-fischer.mp3",
    },
]
