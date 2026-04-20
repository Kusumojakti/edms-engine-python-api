from pydantic import AliasChoices, BaseModel, ConfigDict, Field

class MergeRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    no_reg: str = Field(
        ...,
        validation_alias=AliasChoices("noReg", "noAggr"),
        serialization_alias="noReg",
    )
    pin: str = Field(..., min_length=4)
