text = """это совсем несложно! вот вам пример текста, выполненного по вашему запросу: начинайте читать внимательно — и убедитесь сами!
хороший писатель должен уметь удивлять читателя необычными стилистическими приёмами... ведь правда?
например, попробуйте написать рассказ, используя всего один тип знаков препинания — скажем, только точки или запятые
или ещё лучше — попробуйте сочинить историю вообще без заглавных букв! представляете себе такую книгу?
так что дерзайте, друзья мои, экспериментируйте смело — и пусть ваш талант раскроется во всей красе!
"""
# prep = [".", "!", "?"]
cleared_text = []
# \n - симвод новой строки
for token in text.split("\n"):
    if token != '':
        if token.find("!") != -1:
            #cleared_text.extend(token.split("!"))
            tmp = token.split("!")
            tmp_c = []
            for t in tmp:
                if t.startswith(' '):
                    tmp_c.append(t[0:1].replace(' ', ''))
                else:
                    tmp_c.append(t)
            tmp_c = [t.capitalize() for t in tmp_c]
            tmp_c = [t for t in tmp_c if t != '']
            tmp_c.append(" ")
            cleared_text.append("?".join(tmp_c))
        elif  token.find("?") != -1:
            # cleared_text.extend(token.split("?"))
            tmp = token.split("?")
            tmp_c = []
            for t in tmp:
                if t.startswith(' '):
                    tmp_c.append(t[0:1].replace(' ', ''))
                else:
                    tmp_c.append(t)
            tmp_c = [t.capitalize() for t in tmp_c]
            tmp_c = [t for t in tmp_c if t != '']
            tmp_c.append(" ")
            cleared_text.append("?".join(tmp_c))
        elif  token.find(".") != -1:
            tmp = token.split(".")
            tmp_c = []
            for t in tmp:
                if t.startswith(' '):
                    tmp_c.append(t[0:1].replace(' ', ''))
                else:
                    tmp_c.append(t)
            tmp_c = [t.capitalize() for t in tmp_c]
            tmp_c.append(" ")
            tmp_c = [t for t in tmp_c if t != '']
            
            # str.join([str])
            # Пример "".join(["Hello", "World"]) -> "Hello World"
            # отфильтровать массив пустых строк по аналогии с примером
            # Пример tmp_c = [t for t in tmp_c if t != '']
            # В примере мы оставляем в массиве только те строки что не равны пустой строке
            cleared_text.append(".".join(tmp_c))
        else:
            cleared_text.append(token.capitalize())
    #    for p in prep:
    #        if p in token:
    #            token.split(p)
        
cleared_text = "".join(cleared_text)
print(cleared_text)
