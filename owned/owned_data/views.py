"""OwnedData views implementation."""
from ast import literal_eval
from typing import Any, Dict, Optional, Union, List, Tuple
from rest_framework import viewsets
import string
from enum import Enum
from abcmeta import ABC, abstractmethod
from django.contrib.auth import get_user_model


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
    """OwnedData viewset implementation."""

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

    # Don't touch it!
    __template_variables: Dict[str, Any] = {}

    def _prepare_template_variables(self):
        self._template_variables["request_user_id"] = 1

    @staticmethod
    def _find_formatted_parameters(query_value: str):
        """Find formatted parameters in the text.

        Got the idea from: https://stackoverflow.com/a/46161774/2338672
        """
        return [d[1] for d in string.Formatter().parse(query_value) if d[1] is not None]

    def _parse_owner_field_by_str(self, filter_query: str):
        prepared_parameters: Dict[str, str] = {}
        if "=" in filter_query:
            query_field, query_value = filter_query.split("=", maxsplit=1)
            query_value_parameters = self._find_formatted_parameters(
                literal_eval(query_value)
            )
            if not query_value_parameters:
                prepared_parameters[query_field] = literal_eval(query_value)
            else:
                prepared_parameters[query_field] = query_value.format(
                    **self._template_variables
                )
        else:
            prepared_parameters[filter_query] = self._template_variables[
                "request_user_id"
            ]
        return prepared_parameters

    def filter_by_owner_fields(self, queryset):
        if not self.owner_fields:
            return queryset

        parsed_parameters: List[Dict[str, Any]] = []

        for owner_field in self.owner_fields:
            if isinstance(owner_field, str):
                parsed_parameters.append(self._parse_owner_field_by_str(owner_field))
            elif isinstance(owner_field, list):
                for sub_owner_field in owner_field:
                    parsed_parameters.append(
                        self._parse_owner_field_by_str(sub_owner_field)
                    )
            else:
                raise TypeError(
                    "invalid owner_fields type, it only accepts list or str, but it got %s"
                    % type(owner_field)
                )

        print(parsed_parameters)
        for parsed_parameter in parsed_parameters:
            queryset = queryset.filter(**parsed_parameter)

        return queryset

    def get_queryset(self):
        queryset = super().get_queryset()
        self._prepare_template_variables()
        return self.filter_by_owner_fields(queryset)
        # return queryset
