from chromadb import db
from core.srv.repos.models import Item

class ItemRepository:
    collection = db["assistant"]

    @staticmethod
    def create_item(item: Item):
        item_dict = item.model_dump()
        res = ItemRepository.collection.insert_one(item_dict)
        return item

    @staticmethod
    def get_items():
        return list(ItemRepository.collection.find({}, {"_id": 0}))