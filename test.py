import unittest
from lighthouse import format_data_list, reed_file_xlsx


class DetailFuncTestCase(unittest.TestCase):
    def test_result_func__format_data_list(self):
        arr = [['qwe', '1234', '!@#;']]
        result = format_data_list(arr)
        self.assertEqual(result, 'qwe  1234  !@#;\n\n')

    def test_result_func__reed_file_xlsx(self):
        result = reed_file_xlsx('boginskiy_di', 'test.xlsx')
        for i in result:
            self.assertIn(i[0], ['Еда', 'Мука', 'Орехи', 'Кофе', 'Сыр'])


if __name__ == '__main__':
    unittest.main()
