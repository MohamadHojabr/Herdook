from core.srv.repos.models import Item
from core.srv.repos.repositories import ItemRepository

class ItemUseCases:
    @staticmethod
    def create_item(item: Item):
        return ItemRepository.create_item(item)

    @staticmethod
    def get_items():
        return ItemRepository.get_items()