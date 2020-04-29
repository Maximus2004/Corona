from django.shortcuts import render
import requests
import os
from corona.forms import SearchForm
from bs4 import BeautifulSoup

# open and read file
module_dir = os.path.dirname(__file__)
file_path = os.path.join(module_dir, 'information.txt')
data_file = open(file_path, 'r')
st = data_file.read()

# separate text from file with points
s = st.split('.')
# here's all the frases (results)
itog = set()
chislo = 0
true = set()
s1global = []


def main(request):
    form = SearchForm(request.GET)
    frases = []
    if form.is_valid() and form.cleaned_data["search"]:
        print("SearchText", form.cleaned_data["search"])
        sT = form.cleaned_data["search"]
        search(sT)
        global chislo
    return render(request, "main.html", {'form': form, 'frases': list(itog), 'chislo': chislo})


# ищет полученную стрингу в напарсенной инфе и возвращает фразы из неё
def searchFrases(sear):
    global s
    global true
    search = sear.split(" ")  # разбиваем полученную строку по пробелам
    s1 = []  # первый вариант массива фраз
    temp = []  # времнный массив строк
    for i in range(len(search) - 1):
        temp.append(search[i])

        # если содержатся такие символы, то их надо удалить
        first = temp[-1][0]
        if first == "(" or first == "«" or first == "[":
            temp[-1] = temp[-1][1:len(temp[-1])]

        # если встречаются такие знаки, то мы прерываем образование фразы и, либо записываем то, что полуилось в пред. фразу, либо создаём новую
        last = temp[-1][len(temp[-1]) - 1]
        if last == "." or last == "," or last == ";" or last == ":" or last == ")" or last == "»" or last == "]":
            temp[-1] = temp[-1][0:len(temp[-1]) - 1]
            if last == "." or last == "," or last == ";" or last == ":":
                print('last', last)
                if len(temp) < 2:
                    for g in range(len(temp)):
                        s1[-1].append(temp[g])
                else:
                    s1.append(temp)
            temp = []
        # условия прекращения формирования фразы
        elif len(temp) >= 3 and len(temp[-1]) > 3 and not search[i + 1][0].isupper():
            s1.append(temp)
            temp = []

        # если фраза не сформирована, но слова в тексте ещё остались, то надо добавить то, что осталось в отдельную последнюю фразу
        if i == len(search) - 2:
            temp.append(search[i + 1])
            for o in range(len(temp)):
                if len(s1) != 0:
                    s1[-1].append(temp[o])
                else:
                    s1.append([])
                    s1[-1].append(temp[o])
            temp = []

    # убираем посление 2 символа у всех слов, у которых больше 4-х символов
    for i in range(len(s1)):
        for j in range(len(s1[i])):
            if len(s1[i][j]) > 4:
                s1[i][j] = s1[i][j][0:len(s1[i][j]) - 2]
    print('The first variant of division into frases:', s1)

    global s1global # нужна для того, чтобы "снаружи" знали о том, сколько фраз получилось при разбиении
    s1global = s1
    global itog
    for i in range(len(s1)):
        for g in range(len(s)):
            # print(s[g])
            indexSearch = 0
            if indexSearch < len(s1[i]) and s1[i][indexSearch] in s[g]:
                temp = s[g].split(' ')
                # print('temp', temp)
                indexParse = len(temp)
                for q in range(len(temp)):
                    if s1[i][indexSearch] in temp[q] and abs(len(s1[i][indexSearch]) - len(temp[q])) < 5:
                        print('Нашёл слово в напарсенной стринге:', temp[q], abs(len(s1[i][indexSearch]) - len(temp[q])))
                        indexParse = q
                count = 0
                while indexParse < len(temp) and indexSearch < len(s1[i]) and s1[i][indexSearch] in temp[
                    indexParse] and abs(len(temp[indexParse]) - len(s1[i][indexSearch])) < 5:
                    print(s1[i][indexSearch], 'содержится в', temp[indexParse], count)
                    indexSearch += 1
                    count += 1
                    indexParse += 1
                if count == len(s1[i]):
                    # print(s[g])
                    true.add(i) # добалвяем индекс найденной фразы
                    itog.add(s[g])
                    print('Add string', s[g])
                    g += 1


def search(sT):
    searchText = sT.split(' ')  # разбиение того, что ищет пользователь (sT) на слова
    syns = []
    for i in searchText:
        syns.append([])
        if len(i) > 2:
            SYNS = 'https://synonymonline.ru/' + i[0].upper() + '/' + i.lower()
            full_page = requests.get(SYNS)

            soup = BeautifulSoup(full_page.content, 'html.parser')
            convert = soup.findAll('li', {'class': 'col-sm-4 col-xs-6'})
            if len(convert) > 3:
                for j in range(3):
                    syns[-1].append(convert[j].text)
            else:
                for j in range(len(convert)):
                    syns[-1].append(convert[j].text)
    print('Massive of synonyms:', syns)

    masTexts = []
    for i in range(3):
        string = ''
        for j in range(len(syns)):
            if len(syns[j]) != 0 and i < len(syns[j]):
                string += syns[j][i] + ' '
            else:
                string += searchText[j] + ' '
        masTexts.append(string[:-1])
    print(masTexts)

    searchFrases(sT)
    for i in range(len(masTexts)):
        searchFrases(masTexts[i])
    # print('true', true)
    print()
    global chislo
    chislo = round(len(list(true)) / len(s1global) * 100)
    print('Новость достоверна на:', round(len(list(true)) / len(s1global) * 100), '%')
    print(itog)