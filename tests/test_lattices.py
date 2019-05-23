# test_lattices.py

import pickle

import pytest

from concepts.contexts import Context


@pytest.fixture(scope='module')
def lattice():
    source = '''
       |+1|-1|+2|-2|+3|-3|+sg|+pl|-sg|-pl|
    1sg| X|  |  | X|  | X|  X|   |   |  X|
    1pl| X|  |  | X|  | X|   |  X|  X|   |
    2sg|  | X| X|  |  | X|  X|   |   |  X|
    2pl|  | X| X|  |  | X|   |  X|  X|   |
    3sg|  | X|  | X| X|  |  X|   |   |  X|
    3pl|  | X|  | X| X|  |   |  X|  X|   |
    '''
    context = Context.fromstring(source)
    return context.lattice


def test_pickling(lattice):
    result = pickle.loads(pickle.dumps(lattice))
    assert result._context, lattice._context
    assert [tuple(c) for c in result._concepts] == \
           [tuple(c) for c in lattice._concepts]


def test_len(lattice):
    assert len(lattice) == 22


def test_unicode(lattice):
    assert all(ord(c) < 128 for c in str(lattice))
    assert u'%s' % lattice == '%s' % lattice


@pytest.mark.parametrize('concepts, expected', [
    ([('+1',), ('+2',)], [('+1',), ('+2',),
                          ('-3',), ('-2',), ('-1',),
                          ()]),
])
def test_upset_union(lattice, concepts, expected):
    concepts, expected = ([lattice[a] for a in arg] for arg in (concepts, expected))
    assert list(lattice.upset_union(concepts)) == expected


@pytest.mark.parametrize('concepts, expected', [
    ([('+1',), ('+2',)], [('+1',), ('+2',),
                          ('+1', '+sg'), ('+1', '+pl'),
                          ('+2', '+sg'), ('+2', '+pl'),
                          ('+1', '-1', '+2', '-2', '+3', '-3', '+sg', '+pl', '-sg', '-pl')]),
])
def test_downset_union(lattice, concepts, expected):
    concepts, expected = ([lattice[a] for a in arg]
                          for arg in (concepts, expected))
    assert list(lattice.downset_union(concepts)) == expected


@pytest.mark.parametrize('concepts, expected', [
    ([('+1', '+sg'), ('+2', '+sg'), ('+3', '+sg')],
     [('+1', '+sg'), ('+2', '+sg'), ('+3', '+sg'),
      ('-3', '+sg'), ('-2', '+sg'), ('-1', '+sg'),
      ('+sg',)]),
])
def test_upset_generalization(lattice, concepts, expected):
    concepts, expected = ([lattice[a] for a in arg]
                          for arg in (concepts, expected))
    assert list(lattice.upset_generalization(concepts)) == expected


def test_minimal(lattice):
    assert lattice.infimum.minimal() == ('+1', '-1', '+2', '-2', '+3', '-3',
                                         '+sg', '+pl', '-sg', '-pl')


def test_minimum():
    l = Context(('spam',), ('ham',), [(True,)]).lattice
    assert len(l) == 1
    assert l.infimum is l.supremum
    assert l.atoms == ()


def test_trivial():
    l = Context(('spam',), ('ham',), [(False,)]).lattice
    assert len(l) == 2
    assert l.infimum is not l.supremum
    assert l.atoms == (l.supremum,)


def test_nonatomic():
    m = Context(('spam', 'eggs'), ('ham',), [(True,), (True,)]).lattice
    assert [tuple(c) for c in m] == [(('spam', 'eggs'), ('ham',))]
    t = Context(('spam', 'eggs'), ('ham',), [(False,), (False,)]).lattice
    assert [tuple(c) for c in t] == [((), ('ham',)), (('spam', 'eggs'), ())]
