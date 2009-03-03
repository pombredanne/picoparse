import unittest

from functools import partial as p
from picoparse import run_parser, NoMatch
from picoparse import any_token, one_of, not_one_of, satisfies
from picoparse import many, many1, many_until, many_until1, n_of

from utils import run, runp, ParserTestCase

# some simple parsers
nothing = p(one_of, '')
everything= p(not_one_of, '')
one_a = p(one_of, 'a')
not_a = p(not_one_of, 'a')
one_a_or_b = p(one_of, 'ab')
not_a_or_b = p(not_one_of, 'ab')

always_satisfies = p(satisfies, lambda i: True)
never_satisfies = p(satisfies, lambda i: False)
one_b_to_d = p(satisfies, lambda i: 'b' <= i <= 'd')

class TestTokenConsumers(ParserTestCase):
    """This TestCase checks that all the primative token consumers work as expected.
    """
    def testany_token(self):
        self.assertEquals(run(any_token, 'a'), 'a')
        self.assertEquals(run(any_token, 'b'), 'b')
        self.assertEquals(run(any_token, 'ab'), 'a')
                
        self.assertRaises(NoMatch, runp(any_token, ''))
    
    def testone_of(self):
        # matches
        self.assertEquals(run(one_a, 'a'), 'a')
        self.assertEquals(run(one_a_or_b, 'a'), 'a')
        self.assertEquals(run(one_a_or_b, 'b'), 'b')
        self.assertEquals(run(one_a, 'ac'), 'a')
        self.assertEquals(run(one_a_or_b, 'ac'), 'a')
        self.assertEquals(run(one_a_or_b, 'bc'), 'b')
        
        # no match
        self.assertNoMatch(one_a, 'b')
        self.assertNoMatch(one_a_or_b, 'c')
        self.assertNoMatch(one_a, '')
        self.assertNoMatch(one_a_or_b, '')
        self.assertNoMatch(nothing, 'a')
        
    def testnot_one_of(self):
        # matches
        self.assertEquals(run(not_a, 'b'), 'b')
        self.assertEquals(run(not_a_or_b, 'c'), 'c')
        self.assertEquals(run(everything, 'a'), 'a')
        self.assertEquals(run(everything, 'b'), 'b')
        self.assertEquals(run(everything, 'ab'), 'a')
        
        # no match
        self.assertNoMatch(not_a, 'a')
        self.assertNoMatch(not_a_or_b, 'a')
        self.assertNoMatch(not_a_or_b, 'b')
    
    def testsatisfies(self):
        self.assertEquals(run(always_satisfies, 'a'), 'a')
        self.assertEquals(run(always_satisfies, 'b'), 'b')
        self.assertNoMatch(always_satisfies, '')

        self.assertNoMatch(never_satisfies, 'a')
        self.assertNoMatch(never_satisfies, 'b')
        self.assertNoMatch(never_satisfies, '')

        self.assertEquals(run(one_b_to_d, 'b'), 'b')
        self.assertEquals(run(one_b_to_d, 'c'), 'c')
        self.assertEquals(run(one_b_to_d, 'd'), 'd')
        self.assertEquals(run(one_b_to_d, 'bc'), 'b')
        self.assertNoMatch(one_b_to_d, '')
        self.assertNoMatch(one_b_to_d, 'a')
        self.assertNoMatch(one_b_to_d, 'e')


many_as = p(many, one_a)
at_least_one_a = p(many1, one_a)
one_b = p(one_of, 'b')
some_as_then_b = p(many_until, one_a, one_b)
at_least_one_a_then_b = p(many_until1, one_a, one_b)
three_as = p(n_of, one_a, 3)

class TestManyCombinators(ParserTestCase):
    """Tests the simple many* parser combinators.
    """
    
    def testmany(self):
        self.assertEquals(run(many_as, ''), [])
        self.assertEquals(run(many_as, 'a'), ['a'])
        self.assertEquals(run(many_as, 'aa'), ['a','a'])
        self.assertEquals(run(many_as, 'aaa'), ['a','a', 'a'])
    
        self.assertEquals(run(many_as, 'b'), [])
        self.assertEquals(run(many_as, 'ab'), ['a'])
        self.assertEquals(run(many_as, 'aab'), ['a','a'])
        self.assertEquals(run(many_as, 'aaab'), ['a','a','a'])

    def testmany1(self):
        self.assertNoMatch(at_least_one_a, '')
        self.assertEquals(run(at_least_one_a, 'a'), ['a'])
        self.assertEquals(run(at_least_one_a, 'aa'), ['a','a'])
        self.assertEquals(run(at_least_one_a, 'aaa'), ['a','a','a'])

        self.assertNoMatch(at_least_one_a, 'b')
        self.assertEquals(run(at_least_one_a, 'ab'), ['a'])
        self.assertEquals(run(at_least_one_a, 'aab'), ['a','a'])
        self.assertEquals(run(at_least_one_a, 'aaab'), ['a','a','a'])
    
    def testmany_until(self):
        self.assertEquals(run(some_as_then_b, 'b'), ([], 'b'))
        self.assertEquals(run(some_as_then_b, 'ab'), (['a'], 'b'))
        self.assertEquals(run(some_as_then_b, 'aab'), (['a','a'], 'b'))
        self.assertEquals(run(some_as_then_b, 'aaab'), (['a','a','a'], 'b'))
        
        self.assertNoMatch(some_as_then_b, '')
        self.assertNoMatch(some_as_then_b, 'a')
        self.assertNoMatch(some_as_then_b, 'aa')
        
    def testmany_until1(self):
        self.assertNoMatch(at_least_one_a_then_b, 'b')
        self.assertEquals(run(at_least_one_a_then_b, 'ab'), (['a'], 'b'))
        self.assertEquals(run(at_least_one_a_then_b, 'aab'), (['a','a'], 'b'))
        self.assertEquals(run(at_least_one_a_then_b, 'aaab'), (['a','a','a'], 'b'))

        self.assertNoMatch(at_least_one_a_then_b, '')
        self.assertNoMatch(at_least_one_a_then_b, 'a')
        self.assertNoMatch(at_least_one_a_then_b, 'aa')
    
    def testn_of(self):
        self.assertNoMatch(three_as, '')
        self.assertNoMatch(three_as, 'a')
        self.assertNoMatch(three_as, 'aa')
        self.assertEquals(run(three_as, 'aaa'), ['a','a','a'])
        self.assertEquals(run(three_as, 'aaaa'), ['a', 'a', 'a'])
        
        self.assertNoMatch(three_as, 'b')        
        self.assertNoMatch(three_as, 'ab')
        self.assertNoMatch(three_as, 'aab')

if __name__ == '__main__':
    unittest.main()

__all__ = ['TestTokenConsumers', 'TestManyCombinators', ]
