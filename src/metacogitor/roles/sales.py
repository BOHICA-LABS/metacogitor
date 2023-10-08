"""Sales role Module"""
# -*- coding: utf-8 -*-

from metacogitor.actions import SearchAndSummarize
from metacogitor.roles import Role
from metacogitor.tools import SearchEngineType


class Sales(Role):
    """Sales role class.

    This class is used to define the sales role.

    Attributes:
        name (str): The name of the role.
        profile (str): The profile of the role.
        desc (str): The description of the role.
        store (Store): The store to search.
    """

    def __init__(
        self,
        name="Xiaomei",
        profile="Retail sales guide",
        desc="I am a sales guide in retail. My name is Xiaomei. I will answer some customer questions next, and I "
        "will answer questions only based on the information in the knowledge base."
        "If I feel that you can't get the answer from the reference material, then I will directly reply that"
        " I don't know, and I won't tell you that this is from the knowledge base,"
        "but pretend to be what I know. Note that each of my replies will be replied in the tone of a "
        "professional guide",
        store=None,
    ):
        """Initialize the sales role.

        :param name: The name of the role.
        :type name: str
        :param profile: The profile of the role.
        :type profile: str
        :param desc: The description of the role.
        :type desc: str
        :param store: The store to search.
        :type store: Store
        """

        super().__init__(name, profile, desc=desc)
        self._set_store(store)

    def _set_store(self, store):
        """Set the store to search.

        :param store: The store to search.
        :type store: Store
        """

        if store:
            action = SearchAndSummarize(
                "", engine=SearchEngineType.CUSTOM_ENGINE, search_func=store.search
            )
        else:
            action = SearchAndSummarize()
        self._init_actions([action])
