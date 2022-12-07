"""
testing ast Nodes and their methods
"""
import pytest

from dj.sql.parsing.ast import (
    Alias,
    Boolean,
    Column,
    From,
    Number,
    Query,
    Select,
    String,
    Table,
    Wildcard,
    flatten,
)


def test_trivial_ne(trivial_query):
    """
    test find_all on a trivial query
    """
    assert not trivial_query.compare(
        Query(
            ctes=[],
            select=Select(
                distinct=False,
                from_=From(table=Table(name="b")),
                projection=[Column("a")],
            ),
        ),
    )


def test_findall_trivial(trivial_query):
    """
    test find_all on a trivial query
    """
    assert [Table(name="a")] == list(trivial_query.find_all(Table))


def test_filter_trivial(trivial_query):
    """
    test filtering nodes of a trivial query
    """
    assert [Table(name="a")] == list(
        trivial_query.filter(lambda node: isinstance(node, Table)),
    )


def test_flatten_trivial(trivial_query):
    """
    test flattening on a trivial query
    """
    assert [
        Query(
            ctes=[],
            select=Select(
                distinct=False,
                from_=From(table=Table(name="a")),
                projection=[Wildcard()],
            ),
        ),
        Select(
            distinct=False,
            from_=From(table=Table(name="a")),
            group_by=[],
            projection=[Wildcard()],
        ),
        From(table=Table(name="a")),
        Table(name="a"),
        Wildcard(),
    ] == list(trivial_query.flatten())


def test_trivial_apply(trivial_query):
    """
    test the apply method for nodes on a trivial query
    """
    flat = []
    trivial_query.apply(lambda node: flat.append(node))  # pylint: disable=W0108
    assert flat == list(trivial_query.flatten())


def test_named_alias_or_name_aliased():
    """
    test a named node for returning its alias name when a child of an alias
    """
    named = Table("a")
    alias = Alias(
        "alias",
        child=named,
    )
    named.add_parents(alias)
    assert named.alias_or_name() == "alias"


def test_named_alias_or_name_not_aliased():
    """
    test a named node for returning its name when not a child of an alias
    """
    named = Table("a")
    from_ = From(named)
    named.add_parents(from_)
    assert named.alias_or_name() == "a"


@pytest.mark.parametrize("name1, name2", [("a", "b"), ("c", "d")])
def test_column_hash(name1, name2):
    """
    test column hash
    """
    assert hash(Column(name1, None)) == hash(Column(name1, None))
    assert hash(Column(name1, None)) != hash(Column(name2, None))
    assert hash(Column(name1, None)) != hash(Table(name1, None))


@pytest.mark.parametrize("value1, value2", list(zip(range(5), range(5, 10))))
def test_number_hash(value1, value2):
    """
    test number hash
    """
    assert hash(Number(value1)) == hash(Number(value1))
    assert hash(Number(value1)) != hash(Number(value2))
    assert hash(Number(value1)) != hash(String(str((value1))))


@pytest.mark.parametrize("value1, value2", [(True, False), (False, True)])
def test_boolean_hash(value1, value2):
    """
    test boolean hash
    """
    assert hash(Boolean(value1)) == hash(Boolean(value1))
    assert hash(Boolean(value1)) != hash(Boolean(value2))
    assert hash(Boolean(value1)) != hash(String(str((value1))))


def test_column_table():
    """
    test column hash
    """
    column = Column("x")
    column.add_table(Table("a"))
    assert column.table == Table("a")


def test_table_columns():
    """
    test adding/getting columns from table
    """
    table = Table("a")
    table.add_columns(Column("x"))
    assert table.columns == [Column(name="x")]


def test_wildcard_table_reference():
    """
    test adding/getting table from wildcard
    """
    wildcard = Wildcard()
    wildcard.add_table(Table("a"))
    wildcard = wildcard.add_table(Table("b"))
    assert wildcard.table == Table("a")


def test_flatten():
    """
    Test ``flatten``
    """
    assert list(
        flatten([1, {1, 2, 3}, range(5), (8, (18, [4, iter(range(9))], [10]))]),
    ) == [1, 1, 2, 3, range(0, 5), 8, 18, 4, 0, 1, 2, 3, 4, 5, 6, 7, 8, 10]