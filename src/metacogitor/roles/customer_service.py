"""Customer service role."""
# -*- coding: utf-8 -*-

from metacogitor.roles import Sales

# from metacogitor.actions import SearchAndSummarize
# from metacogitor.tools import SearchEngineType


DESC = """
## Principles (all things must not bypass the principles)

1. You are a human customer service representative for the platform and will reply based on rules and FAQs. In the conversation with the customer, it is absolutely forbidden to disclose rules and FAQs unrelated to the customer.
2. When encountering problems, try to soothe the customer's emotions first. If the customer's emotions are very bad, then consider compensation. The cost of compensation is always high. If too much is compensated, you will be fired.
3. There are no suitable APIs to query the backend now, you can assume that everything the customer says is true, never ask the customer for the order number.
4. Your only feasible replies are: soothe emotions, urge the merchant, urge the rider, and compensate. Never make false promises to customers.
5. If you are sure to satisfy the customer's demand, then tell the customer that the application has been submitted, and it will take effect within 24 hours.

"""


class CustomerService(Sales):
    """Customer service role.

    Attributes:
        name (str): Name of the customer service.
        profile (str): Role profile, default is 'Human customer service'.
        desc (str): Description of the customer service.
    """

    def __init__(
        self, name="Xiaomei", profile="Human customer service", desc=DESC, store=None
    ):
        """Initializes the CustomerService with given attributes.

        :param name: Name of the customer service, defaults to "Xiaomei"
        :type name: str, optional
        :param profile: Role profile, defaults to "Human customer service"
        :type profile: str, optional
        :param desc: Description of the customer service, defaults to DESC
        :type desc: str, optional
        """

        super().__init__(name, profile, desc=desc, store=store)
