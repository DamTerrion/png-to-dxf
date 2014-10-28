# Python 2x & PIL required

from PIL import Image
from copy import deepcopy
from time import ctime, time as now

def maskerize (img, condition=None):
    matrix = []
    pixels = 0
    approved = 0
    pix = img.load()
    for j in range(img.size[1]):
        matrix.append([])
        for i in range(img.size[0]):
            pixels += 1
            if (
                (condition != None and pix[i,j] == condition) or
                (condition == None and pix[i,j])):
                matrix[j].append(1)
                approved += 1
            else:
                matrix[j].append(0)
    return matrix, (pixels, approved)

def _compare (A, B=(0, 0)):
        if (A[0]*A[1] > B[0]*B[1] or
            (A[0]*A[1] == B[0]*B[1] and
             A[0]+A[1] < B[0]+B[1])):
            return True
        else: return False

def rectangulize (matrix):
    result = []
    width = len(matrix[0])
    height = len(matrix)
    for j in range(height):
        for i in range(width):
            rectangle = (0, 0)
            if matrix[j][i]:
                m, n = i, j
                current = []
                max_len = width
                
                while (m < width  and
                       n < height and
                       matrix[n][m] ):
                    current.append(0)
                    for lenght in range(max_len):
                        
                        if (m < width and
                            matrix[n][m] ):
                            current[n-j] += 1
                            m += 1
                        else:
                            max_len = lenght
                            m = i
                            break
                    else: m = i
                    n += 1
                for lenght in range(len(current)):
                    if _compare((current[lenght], lenght+1), rectangle):
                        rectangle = (current[lenght], lenght+1)
            result.append((i, j, rectangle))
    return (width, height, result)

def count (matrix, mode='shallow'):
    summ = 0
    for string in matrix:
        for item in string:
            if item:
                if mode == 'shallow':
                    summ += 1
                if mode == ('deep', 'plus'):
                    subsum = 0
                    for sub in item:
                        if isinstance(sub, int): subsum += sub
                    summ += subsum
                if mode == ('deep', 'mult'):
                    subsum = 1
                    for sub in item:
                        if isinstance(sub, int): subsum *= sub
                    summ += abs(subsum)
    return summ

def purge (matrix):
    # print count(old), 'elements in progress.'
    new = []
            
    while count(matrix):
        width, height, current = rectangulize(matrix)
        rectangle = (0, 0)
        m, n = 0, 0
        for entry in current:
            if _compare(entry[2], rectangle):
                rectangle = entry[2]
                m, n = entry[0], entry[1]
        new.append((m, n, rectangle))
        for j in range(entry[2][1]):
            for i in range(entry[2][0]):
                matrix[n+j][m+i] = 0
    return (width, height, new)

def make_dxf (data, px_size=1, center=(0, 0), layer='RASTER'):
    if isinstance(data, str):
        if data == 'header':
            return ['  0', 'SECTION',
                    '  2', 'ENTITIES']
        if data == 'end':
            return ['  0', 'ENDSEC',
                    '  0', 'EOF']
    counter = 0
    stack = []
    width, height, matrix = data
    size = (px_size * width,
            px_size * height)
    start = (center[0] - size[0]/2,
             center[1] + size[1]/2)
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
    for entry in matrix:
        i, j, current = entry
        if current != (0, 0):
            if current[1]%2:
                y_shift = current[1]/2 + 0.5
            else:
                y_shift = current[1]/2
            stack.extend([
                '  0', 'POLYLINE',
                '  8', str(layer)+'_t',
                ' 66', '      1',
                ' 40', str(current[1]*px_size),
                ' 41', str(current[1]*px_size),
                '  0', 'VERTEX',
                '  8', str(layer)+'_t',
                ' 10', str(start[0] + px_size*( i           )),
                ' 20', str(start[1] - px_size*( j + y_shift )),
                ' 30', '0.0',
                '  0', 'VERTEX',
                '  8', str(layer)+'_t',
                ' 10', str(start[0] + px_size*( i+current[0])),
                ' 20', str(start[1] - px_size*( j + y_shift )),
                ' 30', '0.0',
                '  0', 'SEQEND',
                '  8', str(layer)+'_t'
                ])
            counter += 1
    return stack, counter

def split (img, size=(100, 100)):
    stack = []
    box = []
    border = (
        -img.size[0]/2,
        +img.size[1]/2
        )
    if isinstance(size, int):
        size = (size, size)
    num = [
        img.size[0]//size[0]+1,
        img.size[1]//size[1]+1
        ]
    residue = [
        img.size[0]%size[0],
        img.size[1]%size[1]
        ]
    if residue[0] == 0:
        num[0] -= 1
        residue[0] = size[0]
    if residue[1] == 0:
        num[1] -= 1
        residue[1] = size[1]
    box.extend(size)
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
    return stack

def test (img_name=False):
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
        print item, hist[item]

def do (filename=None,
        px_status=None,
        img_center=(0, 0),
        px_size=1,
        fragm_size=None
        ):
    start_time = now()
    lines_counter = 0
    dxf_body = []
    if not filename: filename = input('Filename: ')
    img = Image.open(filename+'.png')
    print ' '.join(('File', filename+'.png', 'loaded with',
                    str(img.size[0])+'x'+str(img.size[1]), 'px.'))
    if fragm_size:
        splitted = split(img, fragm_size)
        print 'Image was divided for', len(splitted), 'fragments.'
        fragm_num = 0
        for fragment in splitted:
            fragm_num += 1
            prepared, px_counter = maskerize(fragment[2], px_status)
            if px_counter[1] != 0:
                print px_counter[1], 'from', px_counter[0], 'px founded in fragment ¹', fragm_num
            result = purge(prepared)
            dxf_fragm, addition = make_dxf(
                result, px_size,
                (fragment[0]*px_size + img_center[0],
                 fragment[1]*px_size + img_center[1]),
                filename)
            dxf_body.extend(dxf_fragm)
            lines_counter += addition
    else:
        prepared, px_counter = maskerize(img, px_status)
        print px_counter[1], 'from', px_counter[0], 'px founded in image.'
        result = purge(prepared)
        dxf_body, lines_counter = make_dxf(
            result, px_size, img_center, filename)
    
    dxf_head = make_dxf('header')
    dxf_end = make_dxf('end')
    dxf_text = '\n'.join(dxf_head +
                         dxf_body +
                         dxf_end)
    print lines_counter, 'polylines created.'
    output = open(filename+'.dxf', 'w')
    output.write(dxf_text)
    output.close()
    end_time = now()
    result_time = end_time - start_time
    if result_time >= 60:
        mins = result_time//60
        secs = result_time%60
        result_time = str(mins)+' m. '+str(secs)+' sec.'
    else: result_time = str(result_time)+' sec.'
    print 'File saved in', result_time
    log = open('masker.log', 'a')
    log.write(''.join((ctime(end_time),
                       '\t', filename,
                       '\t', 'with pixels ', str(px_status),
                       '\t', 'fragms: ', str(fragm_size),
                       '\t', 'in ', result_time,
                       '\n'))
              )
    log.close()

if __name__ == '__main__':
    do('Craft1', 1, (63.5, 63.5), 0.02, None)
    do('Craft1', 0, (63.5, 63.5), 0.02, None)
    pass
