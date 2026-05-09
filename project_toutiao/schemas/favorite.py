from pydantic import BaseModel, Field


class FavoriteNewsRequest(BaseModel):
    news_id: int = Field(..., alias="newsId")

    model_config = {"populate_by_name": True}
