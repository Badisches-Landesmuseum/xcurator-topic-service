from typing import List, Optional

from pydantic import BaseModel


class Topic(BaseModel):
    percentage: Optional[float]
    word: Optional[str]
