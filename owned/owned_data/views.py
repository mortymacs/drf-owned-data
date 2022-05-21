"""OwnedData views implementation."""
from ast import literal_eval
import operator
from distutils.sysconfig import customize_compiler
from typing import Any, Dict, Optional, Union, List, Tuple, Callable
from matplotlib.pyplot import isinteractive
from rest_framework import viewsets
import string
from enum import Enum
from abcmeta import ABC, abstractmethod
from django.contrib.auth import get_user_model
from django.db.models.query import QuerySet
from django.db.models import Q
from django.contrib.auth.models import AnonymousUser


class CollaborateType(Enum):
    GET = "get"
    POST = "post"
    PUT = "put"
    PATCH = "patch"
    DELETE = "delete"
    HEAD = "head"
    OPTIONS = "options"
    ALL_EXCEPT_GET = "all_except_get"


class BaseOwnedDataViewSet(ABC):
    """Base class for OwnedDataViewSet to fore implementing the required methods."""

    @abstractmethod
    def owned_data_collaborators_on_get(
        self, request: "Request", payload: Any, query: Dict, user: Optional["User"]
    ) -> bool:
        pass

    @abstractmethod
    def owned_data_collaborators_on_post(
        self, request: "Request", payload: Any, query: Dict, user: Optional["User"]
    ) -> bool:
        pass

    @abstractmethod
    def owned_data_collaborators_on_put(
        self, request: "Request", payload: Any, query: Dict, user: Optional["User"]
    ) -> bool:
        pass

    @abstractmethod
    def owned_data_collaborators_on_patch(
        self, request: "Request", payload: Any, query: Dict, user: Optional["User"]
    ) -> bool:
        pass

    @abstractmethod
    def owned_data_collaborators_on_delete(
        self, request: "Request", payload: Any, query: Dict, user: Optional["User"]
    ) -> bool:
        pass


class OwnedDataViewSet(viewsets.GenericViewSet):
    """OwnedData viewset implementation.

    There are two attributes which can be changed in any derived class:
    * owned_data_fields: contains the table fields that the logged-in user has access to.
    * owned_data_collaborators: contains the collaborators to the owned_data_fields.
    """

    # owned_data_fields contains the table fields that the logged-in user has access to.
    # The format can be List[str], for example: ["author", "publisher"] which means
    # >>> Model.objects.filter(author=request.user, publisher=request.user)
    # or it can be List[List[str]], for example: [["author"], ["publisher", "creator"]]
    # which means:
    # >>> Model.objects.filter(
    #   Q(author=request.user) | Q(publisher=request.user, creator=request.user)
    # )
    # So, you can use List[str] to run the "AND" statement, or List[List[str]] to the "OR"
    # statement.
    #
    # It also supports the Django magic methods, like: ["comment__post__author"] which means:
    # >>> Model.objects.filter(comment__post__author=request.user)
    #
    # Another type of value can be a fixed literal, like ["author", "is_draft=False"] which means:
    # >>> Model.objects.filter(author=request.user, is_draft=False)
    # Defaults to None.
    owned_data_fields: Optional[Union[List[str], List[List[str]]]] = None

    # owned_data_collaborators contains the collaborators to the owned_data_fields.
    # The format is like {HTTP method: collaborators + conditions}
    # collaborators must have a prefix:
    # | Prefix | Description | Sample                                               |
    # |--------|-------------|------------------------------------------------------|
    # | u:     | user        | `["u:admin", "u:test"]`                              |
    # | g:     | group       | `["g:editors", "g:customers"]`                       |
    # | p:     | permission  | `["p:change_user", "p:delete_session"]`              |
    # | f:     | function    | `["f:validate_permission", "f:Permission.validate"]` |
    # | *      | anyone      | `["*"]`                                              |
    # For example: {CollaborateType.DELETE: ["g:admin"]}
    #
    # To give permission to anyone, for example: {CollaborateType.GET: ["*"]}
    #
    # To have permission in a certain condition:
    # {CollaborateType.POST: {("g:bot", "g:platform"): ["status=in_progress"]}
    # Defaults to None.
    owned_data_collaborators: Optional[
        Dict[CollaborateType, Union[List[str], Dict[Tuple[str], List[str]]]]
    ] = None

    # Store temporary data based on the request.
    __owned_data_variables: Dict[str, Any] = {}

    def __setup_owned_data_variables(self):
        self.__owned_data_variables["request_user"] = get_user_model().objects.get(id=1)

    @staticmethod
    def __find_formatted_parameters(query_value: str):
        """Find formatted parameters in the text.

        Got the idea from: https://stackoverflow.com/a/46161774/2338672
        """
        return [d[1] for d in string.Formatter().parse(query_value) if d[1] is not None]

    def __parse_owned_data_field_value(
        self, field_value: str
    ) -> Optional[Tuple[str, Callable, Union[str, int, object]]]:
        """Parse and translate the field value.

        >>> __parse_owned_data_field_value("author")
        ("author", operator.eq, User<test>)
        >>> __parse_owned_data_field_value("is_draft!=False")
        ("is_draft", operator.ne, False)

        If user is not logged-in:
        >>> __parse_owned_data_field_value("author")
        ("author", operator.eq, None)

        Args:
            field_value (str): field value. e.g. "author", or "is_draft!=False".

        Returns:
            Optional[Tuple[str, Callable, Union[str, int, object]]]: parsed result: attribute, operator, and value.
        """
        if "!=" in field_value:
            attribute, value = field_value.split("!=", maxsplit=1)
            return attribute, operator.ne, literal_eval(value)
        elif "=" in field_value:
            attribute, value = field_value.split("!=", maxsplit=1)
            return attribute, operator.eq, literal_eval(value)
        else:
            # Ignore user data field if the user is not authenticated yet.
            if self.__owned_data_variables.get("request_user"):
                return (
                    field_value,
                    operator.eq,
                    self.__owned_data_variables["request_user"],
                )

    @classmethod
    def __validate_owned_data_fields_type(cls):
        """Validate owned data fields type.

        Raises: ValueError in case of invalid data type.
        """
        if cls.owned_data_fields is None:
            return

        first_owned_data_field = cls.owned_data_fields[0]
        if not isinstance(first_owned_data_field, (str, list)):
            raise ValueError(
                "invalid owned_data_fields data type! valid types: str, List[str], but it's %s"
                % type(first_owned_data_field)
            )

        for owned_data_field in cls.owned_data_fields:
            if not isinstance(owned_data_field, type(first_owned_data_field)):
                raise ValueError(
                    "owned_data_fields data types must be the same! %s != %s"
                    % (type(first_owned_data_field), type(owned_data_field))
                )

    def __filter_by_owned_data_fields_by_str_type(self, queryset: QuerySet) -> QuerySet:
        """Filter queryset based on the owned_data_fields: List[str] attribute.

        Args:
            queryset (QuerySet): queryset object.

        Returns:
            QuerySet: customized queryset.
        """
        query: Optional[Q] = None
        for owned_data_field in self.owned_data_fields:
            if parsed_field_value := self.__parse_owned_data_field_value(
                owned_data_field
            ):
                attribute, op, value = parsed_field_value
                if op == operator.eq:
                    query = (
                        query & Q(**{attribute: value})
                        if query
                        else Q(**{attribute: value})
                    )
                else:
                    query = (
                        query & ~Q(**{attribute: value})
                        if query
                        else ~Q(**{attribute: value})
                    )

        # If nothing parsed, then return.
        if query is None:
            return queryset

        return queryset.filter(query)

    def __filter_by_owned_data_fields_by_list_type(
        self, queryset: QuerySet
    ) -> QuerySet:
        """Filter queryset based on the owned_data_fields: List[List[str]] attribute.

        Args:
            queryset (QuerySet): queryset object.

        Returns:
            QuerySet: customized queryset.
        """
        queries: List[Q] = []
        for owned_data_field in self.owned_data_fields:

            # Iterate over sub owned data fields values
            query: Optional[Q] = None
            for sub_owned_data_field in owned_data_field:
                if parsed_field_value := self.__parse_owned_data_field_value(
                    sub_owned_data_field
                ):
                    attribute, op, value = parsed_field_value
                    if op == operator.eq:
                        query = (
                            query & Q(**{attribute: value})
                            if query
                            else Q(**{attribute: value})
                        )
                    else:
                        query = (
                            query & ~Q(**{attribute: value})
                            if query
                            else ~Q(**{attribute: value})
                        )

            if query is not None:
                queries.append(query)

        # If nothing parsed, then return.
        if not queries:
            return queryset

        # Make "OR" statement between all sub queries.
        query: Q = queries[0]
        for processed_query in queries[1:]:
            query |= processed_query

        return queryset.filter(query)

    def __filter_by_owned_data_fields(self, queryset: QuerySet) -> QuerySet:
        """Filter queryset based on the owned_data_fields attribute.

        Args:
            queryset (QuerySet): queryset object.

        Returns:
            QuerySet: customized queryset.
        """
        # Defining the filter type based on the first item of owned_data_fields.
        if isinstance(self.owned_data_fields[0], str):
            return self.__filter_by_owned_data_fields_by_str_type(queryset)
        return self.__filter_by_owned_data_fields_by_list_type(queryset)

    def get_queryset(self) -> QuerySet:
        """DRF built-in method.

        The starting point of the library.

        Returns:
            QuerySet: filtered queryset.
        """
        queryset = super().get_queryset()
        if not self.owned_data_fields:
            return queryset

        # Make sure the attributes contain the correct data types.
        self.__validate_owned_data_fields_type()

        # Prepare required variables for replacement.
        self.__setup_owned_data_variables()

        # Filter database records.
        customized_queryset = self.__filter_by_owned_data_fields(queryset)

        # Validate collaborators.
        # TODO

        return customized_queryset
