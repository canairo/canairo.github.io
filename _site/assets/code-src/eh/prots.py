def regex_protection(code: str):
    import re

    function_calls = [
        r'system',
        r'execve',
    ]

    for i in function_calls:
        reg = re.compile(i)
        for match in re.findall(reg, code):
            print(code, match)
            if match is not None: return False

    return True
        
if __name__ == "__main__":
    code = open('code.c', 'r').read()
    print(regex_protection(code))
