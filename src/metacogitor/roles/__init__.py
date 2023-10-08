"""Roles module"""
# -*- coding: utf-8 -*-


from metacogitor.roles.role import Role
from metacogitor.roles.architect import Architect
from metacogitor.roles.project_manager import ProjectManager
from metacogitor.roles.product_manager import ProductManager
from metacogitor.roles.engineer import Engineer
from metacogitor.roles.qa_engineer import QaEngineer
from metacogitor.roles.seacher import Searcher
from metacogitor.roles.sales import Sales
from metacogitor.roles.customer_service import CustomerService


__all__ = [
    "Role",
    "Architect",
    "ProjectManager",
    "ProductManager",
    "Engineer",
    "QaEngineer",
    "Searcher",
    "Sales",
    "CustomerService",
]
