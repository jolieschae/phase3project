# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\unittest\test\testmock\testsealable.py
# Compiled at: 2018-06-26 23:07:36
# Size of source mod 2**32: 5276 bytes
import unittest
from unittest import mock

class SampleObject:

    def __init__(self):
        self.attr_sample1 = 1
        self.attr_sample2 = 1

    def method_sample1(self):
        pass

    def method_sample2(self):
        pass


class TestSealable(unittest.TestCase):

    def test_attributes_return_more_mocks_by_default(self):
        m = mock.Mock()
        self.assertIsInstance(m.test, mock.Mock)
        self.assertIsInstance(m.test(), mock.Mock)
        self.assertIsInstance(m.test().test2(), mock.Mock)

    def test_new_attributes_cannot_be_accessed_on_seal(self):
        m = mock.Mock()
        mock.seal(m)
        with self.assertRaises(AttributeError):
            m.test
        with self.assertRaises(AttributeError):
            m()

    def test_new_attributes_cannot_be_set_on_seal(self):
        m = mock.Mock()
        mock.seal(m)
        with self.assertRaises(AttributeError):
            m.test = 1

    def test_existing_attributes_can_be_set_on_seal(self):
        m = mock.Mock()
        m.test.test2 = 1
        mock.seal(m)
        m.test.test2 = 2
        self.assertEqual(m.test.test2, 2)

    def test_new_attributes_cannot_be_set_on_child_of_seal(self):
        m = mock.Mock()
        m.test.test2 = 1
        mock.seal(m)
        with self.assertRaises(AttributeError):
            m.test.test3 = 1

    def test_existing_attributes_allowed_after_seal(self):
        m = mock.Mock()
        m.test.return_value = 3
        mock.seal(m)
        self.assertEqual(m.test(), 3)

    def test_initialized_attributes_allowed_after_seal(self):
        m = mock.Mock(test_value=1)
        mock.seal(m)
        self.assertEqual(m.test_value, 1)

    def test_call_on_sealed_mock_fails(self):
        m = mock.Mock()
        mock.seal(m)
        with self.assertRaises(AttributeError):
            m()

    def test_call_on_defined_sealed_mock_succeeds(self):
        m = mock.Mock(return_value=5)
        mock.seal(m)
        self.assertEqual(m(), 5)

    def test_seals_recurse_on_added_attributes(self):
        m = mock.Mock()
        m.test1.test2().test3 = 4
        mock.seal(m)
        self.assertEqual(m.test1.test2().test3, 4)
        with self.assertRaises(AttributeError):
            m.test1.test2().test4
        with self.assertRaises(AttributeError):
            m.test1.test3

    def test_seals_recurse_on_magic_methods(self):
        m = mock.MagicMock()
        m.test1.test2['a'].test3 = 4
        m.test1.test3[2:5].test3 = 4
        mock.seal(m)
        self.assertEqual(m.test1.test2['a'].test3, 4)
        self.assertEqual(m.test1.test2[2:5].test3, 4)
        with self.assertRaises(AttributeError):
            m.test1.test2['a'].test4
        with self.assertRaises(AttributeError):
            m.test1.test3[2:5].test4

    def test_seals_dont_recurse_on_manual_attributes(self):
        m = mock.Mock(name='root_mock')
        m.test1.test2 = mock.Mock(name='not_sealed')
        m.test1.test2.test3 = 4
        mock.seal(m)
        self.assertEqual(m.test1.test2.test3, 4)
        m.test1.test2.test4
        m.test1.test2.test4 = 1

    def test_integration_with_spec_att_definition(self):
        m = mock.Mock(SampleObject)
        m.attr_sample1 = 1
        m.attr_sample3 = 3
        mock.seal(m)
        self.assertEqual(m.attr_sample1, 1)
        self.assertEqual(m.attr_sample3, 3)
        with self.assertRaises(AttributeError):
            m.attr_sample2

    def test_integration_with_spec_method_definition(self):
        m = mock.Mock(SampleObject)
        m.method_sample1.return_value = 1
        mock.seal(m)
        self.assertEqual(m.method_sample1(), 1)
        with self.assertRaises(AttributeError):
            m.method_sample2()

    def test_integration_with_spec_method_definition_respects_spec(self):
        m = mock.Mock(SampleObject)
        with self.assertRaises(AttributeError):
            m.method_sample3.return_value = 3

    def test_sealed_exception_has_attribute_name(self):
        m = mock.Mock()
        mock.seal(m)
        with self.assertRaises(AttributeError) as (cm):
            m.SECRETE_name
        self.assertIn('SECRETE_name', str(cm.exception))

    def test_attribute_chain_is_maintained(self):
        m = mock.Mock(name='mock_name')
        m.test1.test2.test3.test4
        mock.seal(m)
        with self.assertRaises(AttributeError) as (cm):
            m.test1.test2.test3.test4.boom
        self.assertIn('mock_name.test1.test2.test3.test4.boom', str(cm.exception))

    def test_call_chain_is_maintained(self):
        m = mock.Mock()
        m.test1().test2.test3().test4
        mock.seal(m)
        with self.assertRaises(AttributeError) as (cm):
            m.test1().test2.test3().test4()
        self.assertIn('mock.test1().test2.test3().test4', str(cm.exception))


if __name__ == '__main__':
    unittest.main()