
bin_express = dict()
unary_express = dict()

bin_express["+"] = (lambda x, y: x + y)
bin_express["-"] = (lambda x, y: x - y)
bin_express["/"] = (lambda x, y: x / y)
bin_express["*"] = (lambda x, y: x * y)

bin_express[">"] = (lambda x, y: x > y)
bin_express["<"] = (lambda x, y: x < y)
bin_express[">="] = (lambda x, y: x >= y)
bin_express["<="] = (lambda x, y: x <= y)
bin_express["=="] = (lambda x, y: x == y)
bin_express["!="] = (lambda x, y: x != y)

bin_express[">>"] = (lambda x, y: x >> y)
bin_express["<<"] = (lambda x, y: x << y)
bin_express["%"] = (lambda x, y: x % y)

bin_express["&&"] = (lambda x, y: x and y)
bin_express["||"] = (lambda x, y: x or y)


unary_express["-"] = (lambda x: -x)
unary_express["!"] = (lambda x: not x)

if __name__ == '__main__':
    print(33 + unary_express["!"] (False))