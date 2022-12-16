"""
Types to represent the DJ AST used as an intermediate representation for DJ operations
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, fields
from enum import Enum
from itertools import chain, zip_longest
from typing import (
    Any,
    Callable,
    Generic,
    Iterator,
    List,
    Optional,
    Set,
    Tuple,
    Type,
    TypeVar,
    Union,
)


from dj.sql.parsing.backends.exceptions import DJParseException


def flatten(maybe_iterables: Any) -> Iterator:
    """
    flattens `maybe_iterables` by descending into items that are Iterable
    """

    if not isinstance(maybe_iterables, (list, tuple, set, Iterator)):
        return iter([maybe_iterables])
    return chain.from_iterable(
        (flatten(maybe_iterable) for maybe_iterable in maybe_iterables)
    )


class DJEnum(Enum):
    """
    A DJ AST enum
    """

    def __repr__(self) -> str:
        return str(self)


TNode = TypeVar("TNode", bound="Node")


class Node(ABC):
    """Base class for all DJ AST nodes.

    DJ nodes are python dataclasses with the following patterns:
        - Attributes are either
            - primitives (int, float, str, bool, None)
            - iterable from (list, tuple, set)
            - Enum
            - descendant of `Node`
        - Attributes starting with '_' are "obfuscated" and are not included in `children`

    """

    _parents: Set[TNode]

    def __post_init__(self):
        self._parents = set()

    @property
    def parents(self) -> Set[TNode]:
        """get the parents of the node"""
        return self._parents

    def clear_parents(self) -> TNode:
        """remove all parents from the node"""
        self._parents = set()
        return self

    def add_parents(self: TNode, *parents: TNode) -> TNode:
        """add parents to the node"""
        self.parents.update(parents)
        return self

    def remove_parents(self: TNode, *parents: TNode) -> TNode:
        """remove potential parents if they belong to the node"""
        self._parents -= set(parents)
        return self

    def compile_parents(self: TNode) -> TNode:
        """recurse through ast and add parents to nodes

        Note: this function is useful for building asts by hand
        """
        self.apply(lambda node: (node.add_self_as_parent(), None)[1])
        return self

    def add_self_as_parent(self: TNode) -> TNode:
        """adds self as a parent to all children"""
        for child in self.children:
            child.add_parents(self)
        return self

    def flatten(self) -> Iterator["Node"]:
        """flatten the sub-ast of the node as an iterator"""
        return self.filter(lambda _: True)

    def fields(
        self,
        flat: bool = True,
        nodes_only: bool = True,
        obfuscated: bool = False,
        nones: bool = False,
    ) -> Iterator:
        """Returns an iterator over fields of a node with particular filters

        Args:
            flat: return a flattened iterator (if children are iterable)
            nodes_only: do not yield children that are not Nodes (trumped by `obfuscated`)
            obfuscated: yield fields that have leading underscores
                (typically accessed via a property)
            nones: yield values that are None
                (optional fields without a value); trumped by `nodes_only`
        Returns:
            Iterator: returns all children of a node given filters
                and optional flattening (by default Iterator[Node])
        """

        def make_child_generator():
            """makes a generator enclosing self to return not obfuscated fields (fields without starting `_`)"""
            for self_field in fields(self):
                if not self_field.name.startswith("_") if not obfuscated else True:
                    yield self.__dict__[self_field.name]

        # `iter`s used to satisfy mypy (`child_generator` type changes between generator, filter)
        child_generator = iter(make_child_generator())
        if flat:
            child_generator = iter(flatten(child_generator))

        if nodes_only:
            child_generator = iter(
                filter(
                    lambda child: isinstance(child, Node),
                    child_generator,
                ),
            )

        if not nones:
            child_generator = iter(
                filter(lambda child: child is not None, child_generator),
            )  # pylint: disable=C0301

        return child_generator

    @property
    def children(self) -> Iterator["Node"]:
        """returns an iterator of all nodes that are one step from the current node down including through iterables"""
        return self.fields(flat=True, nodes_only=True, obfuscated=False, nones=False)

    def filter(self, func: Callable[["Node"], bool]) -> Iterator["Node"]:
        """find all nodes that `func` returns `True` for"""
        if func(self):
            yield self
        for node in chain(*[child.filter(func) for child in self.children]):
            yield node

    def find_all(self, node_type: Type["Node"]) -> Iterator["Node"]:
        """find all nodes of a particular type in the node's sub-ast"""
        return self.filter(lambda n: isinstance(n, node_type))

    def apply(self, func: Callable[["Node"], None]):
        """
        traverse ast and apply func to each Node
        """
        func(self)
        for child in self.children:
            child.apply(func)

    def compare(self, other: "Node") -> bool:
        """a compare two ASTs"""

        return not self.diff(other)

    def diff(self, other: "Node") -> List[Tuple["Node", "Node"]]:
        """compare two ASTs for differences and return the pairs of differences"""

        def _diff(self, other: "Node"):
            if self != other:
                diffs.append((self, other))
            else:
                for child, other_child in zip_longest(self.children, other.children):
                    _diff(child, other_child)

        diffs: List[Tuple["Node", "Node"]] = []
        _diff(self, other)
        return diffs

    def __eq__(self, other) -> bool:
        """Compares two nodes for "top level" equality.

        Checks for type equality and primitive field types for full equality.
        Compares all others for type equality only. No recursing.
        Note: Does not check (sub)AST. See `Node.compare` for comparing (sub)ASTs.
        """
        primitives = {int, float, str, bool, type(None)}
        return type(self) == type(other) and all(  # pylint: disable=C0123
            s == o
            if type(s) in primitives  # pylint: disable=C0123
            else type(s) == type(o)  # pylint: disable=C0123
            for s, o in zip(
                (self.fields(False, False, False, True)),
                (other.fields(False, False, False, True)),
            )
        )

    @abstractmethod
    def __hash__(self) -> int:
        """hash a node"""


class Expression(Node):
    """an expression type simply for type checking"""


@dataclass(eq=False)
class Name(Node):
    """the string name specified in sql with quote style"""

    name: str
    quote_style: str = ""

    def __str__(self) -> str:
        return (
            f"{self.quote_style}{self.name}{self.quote_style}"  # pylint: disable=C0301
        )

    def to_column(self) -> "Column":
        """transform the name into a column"""
        return Column(self).add_self_as_parent()

    def to_table(self) -> "Table":
        """transform the name into a Table"""
        return Table(self).add_self_as_parent()

    def to_namespace(self) -> "Namespace":
        """transforms a single Name to a single item Identifier"""
        return Namespace([self]).add_self_as_parent()

    def __hash__(self) -> int:
        return hash(self.name + self.quote_style)


@dataclass(eq=False)
class Namespace(Node):
    """Represents a sequence of names prececeding some Table or Column"""

    names: List[Name]

    def to_column(self) -> "Column":
        """transform the namespace into a column whose name is the last name in the namespace

        if the namespace contains a single name,
            the created column will have no namespace
        otherwise, the remaining names for the column's namespace
        """
        if not self.names:
            raise DJParseException("Namespace is empty")
        col = Column(self.names.pop().clear_parents()).add_self_as_parent()
        if self.names:
            col.add_namespace(self)
        return col

    def to_table(self) -> "Table":
        """transform the namespace into a Table whose name is the last name in the namespace

        if the namespace contains a single name,
            the created table will have no namespace
        otherwise, the remaining names for the table's namespace
        """
        if not self.names:
            raise DJParseException("Namespace is empty")
        table = Table(self.names.pop().clear_parents()).add_self_as_parent()
        if self.names:
            table.add_namespace(self)
        return table

    def pop_self(self) -> Tuple[Name, "Namespace"]:
        """a utility function that returns the last name and the remaining namespace as a tuple

        useful for parsing compound identifiers and revealing
        the last name for another attribute
        """
        last = self.names.pop().clear_parents()
        return last, self

    def __str__(self) -> str:
        return ".".join(str(name) for name in self.names)

    def __hash__(self) -> int:
        return hash(Namespace)


@dataclass(eq=False)  # type: ignore
class Named(Expression):
    """An Expression that has a name"""

    name: Name

    _namespace: Optional[Namespace] = field(repr=False, default=None)

    @property
    def namespace(self) -> Optional[Namespace]:
        """return the preceding Namespace of the Named node if any"""
        return self._namespace

    def add_namespace(self, namespace: Optional[Namespace]) -> "Table":
        """add a namespace to the Table if one does not exist"""
        if self._namespace is None:
            self._namespace = namespace
        return self

    def alias_or_name(self) -> str:
        """get the alias name of a node if it is the descendant of an alias otherwise get its own name"""
        if len(self.parents) == 1:
            parent = tuple(self.parents)[0]
            if isinstance(parent, Alias):
                return parent.name
        return self.name


class Operation(Expression):
    """a type to overarch types that operate on other expressions"""


# pylint: disable=C0103
class UnaryOpKind(DJEnum):
    """the accepted unary operations"""

    Plus = "+"
    Minus = "-"
    Not = "NOT"


# pylint: enable=C0103


@dataclass(eq=False)
class UnaryOp(Operation):
    """an operation that operates on a single expression"""

    op: UnaryOpKind  # pylint: disable=C0103
    expr: Expression

    def __hash__(self) -> int:
        return hash((UnaryOp, self.op))


# pylint: disable=C0103
class BinaryOpKind(DJEnum):
    """the DJ AST accepted binary operations"""

    And = "AND"
    Or = "OR"
    Is = "IS"
    Eq = "="
    NotEq = "<>"
    Gt = ">"
    Lt = "<"
    GtEq = ">="
    LtEq = "<="
    BitwiseOr = "|"
    BitwiseAnd = "&"
    BitwiseXor = "^"
    Multiply = "*"
    Divide = "/"
    Plus = "+"
    Minus = "-"
    Modulo = "%"


# pylint: enable=C0103


@dataclass(eq=False)
class BinaryOp(Operation):
    """represents an operation that operates on two expressions"""

    left: Expression
    op: BinaryOpKind  # pylint: disable=C0103
    right: Expression

    def __hash__(self) -> int:
        return hash((BinaryOp, self.op))


@dataclass(eq=False)
class Between(Operation):
    """a between statement"""

    expr: Expression
    low: Expression
    high: Expression

    def __hash__(self) -> int:
        return hash((Between, self.low, self.high))


@dataclass(eq=False)
class Case(Expression):
    """a case statement of branches"""

    conditions: List[Expression] = field(default_factory=list)
    else_result: Optional[Expression] = None
    operand: Optional[Expression] = None
    results: List[Expression] = field(default_factory=list)

    def __hash__(self) -> int:
        return id(self)


@dataclass(eq=False)
class Function(Named, Operation):
    """represents a function used in a statement"""

    args: List[Expression] = field(default_factory=list)

    def __hash__(self) -> int:
        return hash(Function)


@dataclass(eq=False)
class IsNull(Operation):
    """class representing IS NULL"""

    expr: Expression

    def __hash__(self) -> int:
        return hash(IsNull)


@dataclass(eq=False)  # type: ignore
class Value(Expression):
    """base class for all values number, string, boolean"""

    value: Union[str, bool, float, int]


@dataclass(eq=False)
class Number(Value):
    """number value"""

    value: Union[float, int]

    def __post_init__(self):
        super().__post_init__()
        if type(self.value) not in (float, int):
            try:
                self.value = int(self.value)
            except ValueError:
                self.value = float(self.value)

    def __hash__(self) -> int:
        return hash((Number, self.value))


class String(Value):
    """string value"""

    value: str

    def __hash__(self) -> int:
        return hash((String, self.value))


class Boolean(Value):
    """boolean True/False value"""

    value: bool

    def __hash__(self) -> int:
        return hash((Boolean, self.value))


NodeType = TypeVar("NodeType", bound=Node)  # pylint: disable=C0103


@dataclass(eq=False)
class Alias(Named, Generic[NodeType]):
    """wraps node types with an alias"""

    child: Node = field(default_factory=Node)

    def __hash__(self) -> int:
        return hash((Alias, self.name))


@dataclass(eq=False)
class Column(Named):
    """column used in statements"""

    _table: Optional["Table"] = field(repr=False, default=None)

    @property
    def table(self) -> Optional["Table"]:
        """return the table the column was referenced from"""
        return self._table

    def add_table(self, table: "Table") -> "Column":
        """add a referenced table"""
        if self._table is None:
            self._table = table
        return self

    def __hash__(self) -> int:
        return hash((Column, self.name))


@dataclass(eq=False)
class Wildcard(Expression):
    """wildcard or '*' expression"""

    _table: Optional["Table"] = field(repr=False, default=None)

    @property
    def table(self) -> Optional["Table"]:
        """return the table the column was referenced from if there's one"""
        return self._table

    def add_table(self, table: "Table") -> "Wildcard":
        """add a referenced table"""
        if self._table is None:
            self._table = table
        return self

    def __hash__(self) -> int:  # pragma: no cover
        return id(Wildcard)


@dataclass(eq=False)
class Table(Named):
    """a type for tables"""

    _columns: List[Column] = field(repr=False, default_factory=list)

    @property
    def columns(self) -> List[Column]:
        """return the columns referenced from this table"""
        return self._columns

    def add_columns(self, *columns: Column) -> "Table":
        """add columns referenced from this table"""
        for column in columns:
            self._columns.append(column)
            column.add_table(self)
        return self

    def __hash__(self) -> int:
        return hash((Table, self.name))


# pylint: disable=C0103
class JoinKind(DJEnum):
    """the accepted kinds of joins"""

    Inner = "INNER JOIN"
    LeftOuter = "LEFT JOIN"
    RightOuter = "RIGHT JOIN"
    FullOuter = "FULL JOIN"
    CrossJoin = "CROSS JOIN"


# pylint: enable=C0103


@dataclass(eq=False)
class Join(Node):
    """a join between tables"""

    kind: JoinKind
    table: Union[Table, Alias]
    on: Expression  # pylint: disable=C0103

    def __hash__(self) -> int:
        return hash((Join, self.kind))


@dataclass(eq=False)
class From(Node):
    """a from that belongs to a select"""

    table: Union[Table, Alias[Table], Alias["Select"]]
    joins: List[Join] = field(default_factory=list)

    def __hash__(self) -> int:
        return id(self)


@dataclass(eq=False)
class Select(Node):
    """a single select statement type"""

    distinct: bool
    from_: From
    group_by: List[Expression] = field(default_factory=list)
    having: Optional[Expression] = None
    projection: List[Expression] = field(default_factory=list)
    where: Optional[Expression] = None
    limit: Optional[Number] = None

    def __hash__(self) -> int:
        return id(self)


@dataclass(eq=False)
class Query(Expression):
    """overarching query type"""

    select: "Select"
    ctes: List[Alias["Select"]] = field(default_factory=list)

    def __hash__(self):
        return id(self)
