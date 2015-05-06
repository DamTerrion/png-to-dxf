from PIL import Image
from copy import deepcopy
# Функция глубокого копирования: копирует и список, и все его элементы;
#  при обычном копировании создаётся новый список со старыми ссылками.
from time import ctime, time as now

def mask (img, condition=None):
    '''
  Данная функция просматривает изображение и создаёт маску,
в которой каждому подходящему по условию "condition" пикселю
сопоставляется единица, а каждому неподходящему - ноль.
    '''
    matrix = []
    # Переменная matrix сохраняет целевую маску, массив единиц и нолей.
    pixels = 0
    # Переменная pixels сохраняет общее количество обработанных пикселей
    approved = 0
    # Переменная approved сохраняет количество "правильных" пикселей.
    pix = img.convert('L').load()
    for j in range(img.size[1]):
        matrix.append([])
        # Для каждой строчки изображения инициализируется пустая строка.
        for i in range(img.size[0]):
            pixels += 1
            # Счётчик общего числа пикселей.
            '''
            if (
                (condition != None and pix[i,j] == condition) or
                (condition == None and pix[i,j])):
                # Срабатывает, если пиксель удовлетворяет условию
                #  или он не пуст (не чёрный) при отсутствии условия.
                # Однако, если пиксель равен (0, 0, 0) в RGB, он не пуст
                matrix[j].append(1)
                # В матрицу маски заносится сопоставленная единица.
                approved += 1
                # Счётчик "правильных" пикселей, прошедших проверку.
            else:
                matrix[j].append(0)
                # Если есть условие, которому пиксель не удовлетворяет
                #  или же пиксель пустой (чёрный, равен "0").
            '''
            matrix[j].append(pix[i,j])
            if pix[i,j]: approved += 1
    return matrix, (pixels, approved)
    # Функция возвращает матрицу маски,
    #  а так же кортеж (всего пикселей, "правильных" пикселей).

def _compare (A, B=(0, 0)):
    '''
  Данная функция сравнивает два кортежа натуральных чисел.
В этой программе такие кортежи символизируют прямоугольники,
представленные в виде (W, H), где W и H - ширина и высота прямоугольника
    '''
    if (A[0]*A[1] > B[0]*B[1] or
        (A[0]*A[1] == B[0]*B[1] and
         A[0]+A[1] <= B[0]+B[1])):
        return True
        # Функция возвращает Истину, если:
        # - Площадь первого прямоугольника больше площади второго;
        # - Площади равны, но периметр первого прямоугольника меньше.
    else: return False
    # Работает это так:
    # - Истина соответствует выбору -первого- из прямоугольников;
    # -  Ложь  соответствует выбору =второго= из прямоугольников;
    #  Из прямоугольников 2х4 (S=8) и 3х3 (S=9) будет выбран 3х3.
    #  Из 2х6 (S=12, P=8) и 3х4 (S=12, P=7) будет выбран 3х4.
    #  Из прямоугольников 2х3 и 3х2 будет выбран 2х3. Почему бы и нет?

def cover (matrix, exclude=(None,)):
    '''
  Данная функция определяет наибольшую область без пропусков,
начинающуюся с данной точки. Какая из областей является наибольшей,
определяется описанной выше функцией _compare.
    '''
    result = deepcopy(matrix)
    # Создаётся полная копия маски, чтобы все
    #  преобразования совершать над этой копией,
    #  а не над оригиналом маски.
    width = len(matrix[0])
    height = len(matrix)
    # Для последующих операций важно знать размер маски.
    # Т.к. маска прямоугольная, длина первой строки равна её длине.
    for j in range(height):
        for i in range(width):
            rectangle = (0, 0)
            colour = matrix[j][i]
            # Инициализируется прямоугольник нулевой величины.
            if colour not in exclude and matrix[j][i] == colour:
                # Срабатывает только для ячеек с единицей,
                #  ячейки с нулём пропускаются.
                m, n = i, j
                # Инициализируется второй край прямоугольника.
                current = []
                # Переменная current сохраняет список доступных
                #  площадей, описываемых так: номер элемента - высота,
                #  значение элемента - ширина.
                max_len = width - i
                # Переменная max_len хранит уменьшающуюся длину,
                #  чтобы не считывать лишние пиксели. (см. дальше)
                
                while (m < width  and
                       n < height and
                       matrix[n][m] == colour ):
                    # Цикл ограничен размерами маски. Это понадобится,
                    #  если вдоль границы идут только нужные пиксели.
                    current.append(0)
                    # Для новой просматриваемой строки создаётся ячейка.
                    for l in range(max_len):
                        # Цикл ограничен максимальной длиной строки.
                        if matrix[n][m] == colour: #(m < width and ...)
                            # Пока просматриваемая последовательность
                            #  не упрётся в край маски или пустую ячейку
                            current[n-j] += 1
                            # Ширина увеличивается с каждым пикселем.
                            m += 1
                            # Переход к следующему пикселю.
                        else:
                            max_len = l
                            # Кроме того, l всегда >= max_len,
                            #  так что max_len не увеличивается,
                            #  но может уменьшаться (как энтропия).
                            m = i
                            # Раз последовательность прервалась,
                            #  нужно сбросить координату по X.
                            break
                    else: m = i
                    # Если же последовательность достигла максимальной
                    #  длины, дальше идти не имеет смысла.
                    # Нужно сбросить координату, потому что этого
                    #  не произошло, раз не был найден пустой пиксель.
                    n += 1
                    # Переход на следующую строку и к следующей итерации
                    
                # Здесь поиск доступных площадей закончен,
                #  пора выбрать наибольшую из найденых.
                for l in range(len(current)):
                    # Проверяется список допустимых площадей.
                    if _compare((current[l], l+1), rectangle):
                        rectangle = (current[l], l+1)
                    # Результатом проверки является максимальная
                    #  из доступных площадей.
            result[j][i] = (rectangle, colour)
            # В ячейку записывается максимальная площадь (минимум 1х1),
            #  а иначе там так и остаётся ноль.
    return result
    # Функция возвращает матрицу с максимальными доступными площадями,
    #  рассчитанными на каждый пиксель исходной маски.

def count (matrix, mode='shallow', exclude=(None, False, 0)):
    '''
  Для того, чтобы определить, нужно ли ещё искать максимальные площади
для каких-либо ячеек маски, необходимо знать, есть ли там ещё что-то.
Именно эту задачу решает функция count, но её функционал шире, чем
требуется. В частности, она может не только посчитать количество
ненулевых элементов, но и их сумму всех их внутренностей, или даже
сумму произведений всех внутренностей.
    '''
    summ = 0
    for string in matrix:
        # Для каждой строки в маске...
        for item in string:
            # ...для каждой ячейки в строке...
            if item not in exclude:
                # ...если эта ячейка не пуста...
                if mode == 'shallow':
                    # ...просто сосчитать ячейку.
                    summ += 1
                if mode == ('deep', 'plus'):
                    # ...добавить к общей сумме сумму всей ячейки.
                    subsum = 0
                    for sub in item:
                        if isinstance(sub, int): subsum += sub
                        if isinstance(sub, list): subsum += sub[0]
                        if isinstance(sub, tuple): subsum += sub[0]
                    summ += subsum
                if mode == ('deep', 'mult'):
                    # ...добавить к общей сумме факториал ячейки.
                    subsum = 1
                    for sub in item:
                        if isinstance(sub, int): subsum *= sub
                        if isinstance(sub, list): subsum *= sub[0]
                        if isinstance(sub, tuple): subsum *= sub[0]
                    summ += abs(subsum)
    '''
  Это было сделано просто ради развлечения. Но, по крайней
мере, оно может позволить отследить, равна ли сумма частных площадей
сумме всех элементов изначальной маски.
    '''
    #print(summ)
    return summ

def purge (matrix):
    '''
  Данная функция является ключевой. Она работает непосредственно с
исходной маской, учитывая наибольшую из имеющихся площадей и "стирая"
значение ячеек, охватываемых этой площадью. Данная процедура повторяется
до тех пор, пока все пиксели маски не обнулятся.
    '''
    old = matrix
    # print count(old), 'elements in progress.'
    new = list()
    for j in range(len(old)):
        new.append(list())
        for i in range(len(old[j])):
            new[j].append((0, 0))
    # Создаётся нулевая матрица, по размеру аналогичная исходной
            
    while count(old):
        # Цикл работает до тех пор, пока в матрице присутствуют пиксели.
        current = cover(old)
        # Итерация начинается с расчёта площадей для каждой ячейки маски
        rectangle = (0, 0)
        # Инициализируется нулевой прямоугольник.
        m, n = 0, 0
        for j in range(len(current)):
            for i in range(len(current[j])):
                '''
                if current[j][i][0] != (0, 0)j > 0:
                    for a in range(current[j][i][0][1]):

                '''
                if _compare(current[j][i][0], rectangle):
                    rectangle = current[j][i][0]
                    # Если текущая область больше заданной,
                    #  она заменяет заданную.
                    m, n = i, j
                    # Координаты такой области записываются.
        new[n][m] = (rectangle, current[n][m][1])
        # В новую обнулённую матрицу записывается наибольшая площадь.
        for j in range(rectangle[1]):
            for i in range(rectangle[0]):
                old[n+j][m+i] = None
        # В пределах записанной площади исходная маска обнуляется.
    return new
    # Возвращается матрица, в которой содержатся только бОльшие площади,
    #  подавившие меньшие и _не пересекающиеся_ между собой.

def make_dxf (matrix, px_size=1, center=(0, 0), layer='RASTER'):
    '''
  Как следует из названия, данная функция - ключ к генерации dxf-кода.
Если вы не знакомы с содержанием dxf-файлов, краткое описание заныкано
на дальнем-дальнем сервере, в дальнем-дальнем репозитории,
в дальней-предальней ветке с Особым Скриптом, в общем - недалеко отсюда:
https://github.com/DamTerrion/Lumenous/blob/nDXF/ndxf.py

  А если по сути, то у функции есть два режима.
Если на вход подаётся строка 'header' или 'end', то функция возвращает
либо "заголовок" (начало секции объектов), либо окончание файла.
Если же на вход приходит матрица маски, то генерируется код полилиний,
по одной на каждую область.
    '''
    if isinstance(matrix, str):
        if matrix == 'header':
            return ['  0', 'SECTION',
                    '  2', 'ENTITIES']
        if matrix == 'end':
            return ['  0', 'ENDSEC',
                    '  0', 'EOF']
    counter = 0
    stack = []
    size = (px_size*len(matrix[0]),
            px_size*len(matrix))
    start = (center[0] - size[0]/2,
             center[1] + size[1]/2)
    # Первым делом, правда, создаётся прямоугольник - рамка изображения
    stack.extend(['  0', 'POLYLINE',
                  '  8', str(layer)+'_b',
                  ' 66', '     1',
                  ' 40', '0.0',
                  ' 41', '0.0',
                  ' 70', '     1',
                  '  0', 'VERTEX',
                  '  8', str(layer)+'_b',
                  ' 10', str(start[0]),
                  ' 20', str(start[1]),
                  ' 30', '0.0',
                  '  0', 'VERTEX',
                  '  8', str(layer)+'_b',
                  ' 10', str(start[0]+size[0]),
                  ' 20', str(start[1]),
                  ' 30', '0.0',
                  '  0', 'VERTEX',
                  '  8', str(layer)+'_b',
                  ' 10', str(start[0]+size[0]),
                  ' 20', str(start[1]-size[1]),
                  ' 30', '0.0',
                  '  0', 'VERTEX',
                  '  8', str(layer)+'_b',
                  ' 10', str(start[0]),
                  ' 20', str(start[1]-size[1]),
                  ' 30', '0.0',
                  '  0', 'SEQEND',
                  '  8', str(layer)+'_b'])
    for j in range(len(matrix)):
        for i in range(len(matrix[j])):
            current = matrix[j][i][0]
            layer = matrix[j][i][1]
            if current and current != (0, 0):
                if current[0] > current[1]:
                    x_zero_shift = 0 # * current[0]
                    x_full_shift = current[0] # * 1
                    y_zero_shift = current[1] * 0.5
                    y_full_shift = current[1] * 0.5
                    line_width = current[1]
                else:
                    x_zero_shift = current[0] * 0.5
                    x_full_shift = current[0] * 0.5
                    y_zero_shift = 0 # * current[1]
                    y_full_shift = current[1] # * 1
                    line_width = current[0]
                stack.extend([
                    '  0', 'POLYLINE',
                    '  8', str(layer),
                    ' 66', '      1',
                    ' 62', '{:>6}'.format(layer),
                    ' 40', str(line_width*px_size),
                    ' 41', str(line_width*px_size),
                    '  0', 'VERTEX',
                    '  8', str(layer),
                    ' 10', str(start[0] + px_size*( i + x_zero_shift )),
                    ' 20', str(start[1] - px_size*( j + y_zero_shift )),
                    ' 30', '0.0',
                    '  0', 'VERTEX',
                    '  8', str(layer),
                    ' 10', str(start[0] + px_size*( i + x_full_shift )),
                    ' 20', str(start[1] - px_size*( j + y_full_shift )),
                    ' 30', '0.0',
                    '  0', 'SEQEND',
                    '  8', str(layer)
                    ])
                counter += 1
    return stack, counter
    # Функция возвращает список строк для dxf-файла
    # Список значительно проще редактировать, да и записать тоже

def split (img, size=(100, 100)):
    '''
  Данная функция предназначена для того, чтобы делить изображение
на небольшие фрагменты. Большие изображения обрабатываются слишком
долго, поэтому их лучше делить и обрабатывать по частям.
    '''
    stack = []
    box = []
    border = (
        -img.size[0]/2,
        +img.size[1]/2
        )
    # Переменная border содержит угловую точку, начало координат маски.
    if isinstance(size, int):
        size = (size, size)
    num = [
        img.size[0]//size[0]+1,
        img.size[1]//size[1]+1
        ]
    # Переменная num содержит количество фрагментов.
    residue = [
        img.size[0]%size[0],
        img.size[1]%size[1]
        ]
    # Переменная residue содержит размер остатка,
    #  не влезшего в целые фрагменты.
    if residue[0] == 0:
        num[0] -= 1
        residue[0] = size[0]
    if residue[1] == 0:
        num[1] -= 1
        residue[1] = size[1]
    # Если остатка нет, то количество фрагментов возвращается к верному,
    #  а значение параметра residue по приравнивается к фрагменту.
    box.extend(size)
    # Переменная box содержит актуальный размер фрагмента,
    #  потому что фрагменты, расположенные на дальнем краю изображения
    #  очевидным образом могут быть меньше всех остальных.
    if num == (1, 1):
        return [(0, 0, img)]
    for j in range(num[1]):
        box[0] = size[0]
        if j == num[1]-1:
            box[1] = residue[1]
        for i in range(num[0]):
            if i == num[0]-1:
                box[0] = residue[0]
            x = (border[0]+i*size[0]+box[0]/2,
                 i*size[0],
                 i*size[0]+box[0])
            y = (border[1]-j*size[1]-box[1]/2,
                 j*size[1],
                 j*size[1]+box[1])
            stack.append((x[0], y[0], img.crop((x[1], y[1], x[2], y[2]))
                          ))
            # Метод img.crop() возвращает изображение в прямоугольнике,
            #  задаваемом кортежем координат, как приведён в коде.
    return stack
    # Функция возвращает список фрагментов, на которые было разделено
    #  исходное изображение, каждый со своими координатами.

def test (img_name=False):
    '''
  Эта функция появилась, когда мне изображение начало выдавать
отсутствие правильных пикселей. Функция test возвращает количество
пикселей для каждого найденного в изображении цвета.
  Важно помнить: цвет 1 (белый) - не то же самое, что и (255, 255, 255).
    '''
    if not img_name: img_name = input('Filename: ')
    img = Image.open(img_name+'.png')
    hist = dict()
    for j in range(img.size[1]):
        for i in range(img.size[0]):
            pixel = img.getpixel((i, j))
            px_name = str(pixel)
            if px_name in hist:
                hist[px_name] += 1
            else:
                hist[px_name] = 1
    for item in hist:
        print (item, hist[item])

def do (filename=None,
        img_center=(0, 0),  #mm
        px_size=1,          #mm
        fragm_size=None     #px
        ):
    '''
  Данная функция, по сути, собирает всё воедино, и выполняет всю работу.
Она считывает изображение, делит его на куски, обрабатывает полученные
фрагменты до потери пульса и потом сшивает всё в dxf-файл.
    '''
    start_time = now()
    # Хорошо бы отслеживать время работы скрипта, а для этого требуется
    #  записать временную отметку, когда работа начинается.
    lines_counter = 0
    # Переменная lines_counter сохраняет количество созданных полилиний.
    dxf_body = []
    # Инициируется тело dxf-файла в виде списка.
    while not filename:
        filename = input('Filename: ')
    img = Image.open(filename)
    # Если функция запущена без параметров, спрашивается имя файла
    #  для обработки. Затем открывается png-файл с этим именем.
    print (' '.join(('File', filename, 'loaded with',
                     str(img.size[0])+'x'+str(img.size[1]), 'px.')))
    # Комментарии по ходу работы программы - для отслеживания.
    if fragm_size:
        # Если задан размер фрагментов, изображение делится на куски.
        splitted = split(img, fragm_size)
        if len(splitted) > 1:
            print ('Image was divided for', len(splitted), 'fragments.')
        fragm_num = 0
        for fragment in splitted:
            fragm_num += 1
            prepared, px_counter = mask(fragment[2])
            if px_counter[1] != 0:
                print (px_counter[1], 'from', px_counter[0],
                       'px founded in fragment №', fragm_num)
            #prepared = fragment[2].load()
            result = purge(prepared)
            dxf_fragm, addition = make_dxf(
                result, px_size,
                (fragment[0]*px_size + img_center[0],
                 fragment[1]*px_size + img_center[1]),
                filename)
            dxf_body.extend(dxf_fragm)
            # dxf-код каждого из фрагментов последовательно записывается
            #  в общий список dxf-файла.
            lines_counter += addition
            # Счётчик линий увеличивается на возвращённое ранее число.
    else:
        # Если размер не задан, изображение обрабатывается целиком.
        prepared, px_counter = mask(img)
        print (px_counter[1], 'from', px_counter[0], 'px founded in image.')
        result = purge(prepared)
        dxf_body, lines_counter = make_dxf(
            result, px_size, img_center, filename)
    
    dxf_head = make_dxf('header')
    dxf_end = make_dxf('end')
    dxf_text = '\n'.join(dxf_head +
                         dxf_body +
                         dxf_end)
    # Конечный dxf-код собирается путём "обёртывания" кода линий
    #  в заголовок и окончание.
    print (lines_counter, 'polylines created.')
    output = open(filename+'.dxf', 'w')
    output.write(dxf_text)
    output.close()
    end_time = now()
    # dxf-код записывается в файл и записывается время окончания работы.
    result_time = end_time - start_time
    if result_time >= 60:
        mins = result_time//60
        secs = result_time%60
        result_time = '{} m. {:.2} sec.'.format(mins, secs)
    else: result_time = '{:.2} sec.'.format(result_time)
    print ('File saved in', result_time)
    log = open('masker.log', 'a')
    log.write(''.join((ctime(end_time),
                       '\t', filename,
                       '\t', 'fragms: ', str(fragm_size),
                       '\t', 'in ', result_time,
                       '\n'))
              )
    log.close()
    # Собирается и вносится в log-файл запись об изображении.

if __name__ == '__main__':
    do('test.png')
    pass
    '''
  Можно вписать сюда любые команды вроде указанной в комментарии,
чтобы они были обработаны сразу после запуска скрипта. Или оставить всё
как есть и вводить команду do() в командную строку вручную.
    '''
