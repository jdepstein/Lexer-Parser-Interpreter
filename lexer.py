import sys
import lexer_info


class Lexer:
    def __init__(self, f_name: str):
        """
        :param f_name: The Name of the File we are looking at
        """
        try:
            self.f = open(f_name)
            self.info_dic = lexer_info.td
        except IOError:
            print("Can not open file", f_name)
            print("Exiting.")
            sys.exit(1)

    def token_generator(self):
        
        """
        This will yield a a the tokens for each line in a file 
        In each yield it will give the Token , a NamedTuple and the Line number of
        the certain Token
        """
        
        line_number = 0
        for line in self.f:
            line_number += 1
            
            # Organize out comments and Strings
            toks = (w for w in lexer_info.string_comment.split(line) if w)
            for to in toks:
                tokens = (w for w in lexer_info.split_patt.split(to) if w)

                # Read though the Tokens
                for t in tokens:

                    if t in self.info_dic:
                        yield t, self.info_dic[t], line_number

                    elif lexer_info.string_patt.search(t):
                        yield t, lexer_info.String_Lit, line_number

                    elif lexer_info.ident_patt.search(t):
                        yield t, lexer_info.IDENT, line_number

                    elif lexer_info.real_patt.search(t):
                        yield t, lexer_info.REAL, line_number

                    elif lexer_info.intlit_patt.search(t):
                        yield t, lexer_info.INTLIT, line_number

                    else:
                        yield t, lexer_info.ERROR, line_number

        yield "End Of File", lexer_info.EOF, line_number


if __name__ == "__main__":
    syargs = sys.argv
    lex = Lexer("test1.sluc")
    tg = lex.token_generator()
    print("{:20}{:53}{:15}".format("Token", "Name", "Line number"))
    print("*" * 95)
    while True:
        try:
            tok, name, lineNum = next(tg)
            if name != 30:
                print("{:24}{:45}{:15}".format(name.name, tok, lineNum))

        except StopIteration:
            print("Done")
            break
