import codecs
#дозволяє обробляти кириличні символи
def NewLetter(let):
    lett = {
            'Е' : 'E',
            'І' : 'I',
            'О' : 'O',
            'Р' : 'P',
            'А' : 'A',
            'Н' : 'H',
            'К' : 'K',
            'Х' : 'X',
            'С' : 'C',
            'В' : 'B',
            'Т' : 'T',
            'М' : 'M'
    }
    resl = ""
    let = let.upper()
    for i in let:
        if i in lett:
            resl += lett[i]
        else:
            resl += i
    return resl
    