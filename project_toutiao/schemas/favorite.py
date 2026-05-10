from pydantic import BaseModel, ConfigDict, Field


class FavoriteNewsRequest(BaseModel):
    news_id: int = Field(..., alias="newsId")
    model_config = ConfigDict(populate_by_name=True)
