from pydantic import BaseModel, Field

class MergeRequest(BaseModel):
    no_aggr: str = Field(..., alias="noAggr")
    pin: str = Field(..., min_length=4)