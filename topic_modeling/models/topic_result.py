from typing import List, Optional

from pydantic import BaseModel
from models.topic_collection import TopicCollection


class TopicResult(BaseModel):
    # List = float, List[str]
    #percentage: Optional[float]
    topics: Optional[List[TopicCollection]] = []
    results: Optional[List] = [0.0,[[0.0,'']]]


    class Config:
        arbitrary_types_allowed = True
        allow_population_by_alias = True


class TopTopicResult(BaseModel):
    results: Optional[List[List[List[str]]]] = [[['']]]

    class Config:
        arbitrary_types_allowed = True
        allow_population_by_alias = True


#class TopicResult:

  #  def __init__(self, combined_lda_xgboost: List[List]):
   #     self.results = combined_lda_xgboost


