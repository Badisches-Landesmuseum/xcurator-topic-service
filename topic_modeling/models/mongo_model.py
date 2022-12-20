from datetime import datetime
from typing import Optional

from bson import ObjectId
from pydantic import BaseModel, BaseConfig, Field


class MongoModel(BaseModel):

    created_at: Optional[datetime] = Field(alias="createdAt")
    updated_at: Optional[datetime] = Field(alias="updatedAt")

    class Config(BaseConfig):
        use_enum_values = True
        allow_population_by_field_name = True
        json_encoders = {
            datetime: lambda dt: dt.isoformat(),
            ObjectId: lambda oid: str(oid),
        }

    @classmethod
    def from_mongo(cls, data: dict):
        """We must convert _id into "id". """
        if not data:
            return data
        id = data.pop('_id', None)
        return cls(**dict(data, id=id))

    def mongo(self, **kwargs):
        exclude_unset = kwargs.pop('exclude_unset', True)
        by_alias = kwargs.pop('by_alias', True)
        kwargs.pop('paragraphs', True)
        kwargs.pop('document_prediction', True)
        kwargs.pop('document_str', True)
        kwargs.pop('detected_topics', True)
        kwargs.pop('predictions_strings_accumulated_doc', True)
        kwargs.pop('topic_document_extracted', True)
        kwargs.pop('accumulated_topic_document_extracted', True)

        parsed = self.dict(
            exclude_unset=exclude_unset,
            by_alias=by_alias,
           # predictions_strings = str(predictions_strings),
            #detected_topics_results = str(detected_topics_results),
            **kwargs,
        )

        # Mongo uses `_id` as default key. We should stick to that as well.
        #if '_id' not in parsed and 'id' in parsed:
        #parsed['_id'] = parsed.pop('id')
        #parsed['_id'] = ObjectId(parsed['_id'])

        return parsed