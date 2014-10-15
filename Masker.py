# Python 2x & PIL required

from PIL import Image
from copy import deepcopy

def mask (img, condition=255):
    matrix = []
    pixels = 0
    approved = 0
    pix = img.load()
    if isinstance(condition, int) and condition < 256:
        condition = (condition,
                     condition,
                     condition)
    for j in range(img.size[1]):
        matrix.append([])
        for i in range(img.size[0]):
            pixels += 1
            if pix[i,j] == condition:
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

def cover (matrix):
    result = deepcopy(matrix)
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
                    for l in range(max_len):
                        
                        if (m < width and
                            matrix[n][m] ):
                            current[n-j] += 1
                            m += 1
                        else:
                            max_len = l
                            m = i
                            break
                    else: m = i
                    n += 1
                for l in range(len(current)):
                    if _compare((current[l], l+1), rectangle):
                        rectangle = (current[l], l+1)
            result[j][i] = rectangle
    return result

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
    old = matrix
    print count(old), 'elements in progress.'
    new = deepcopy(matrix)
    for j in range(len(new)):
        for i in range(len(new[j])):
            new[j][i] = (0, 0)
            
    while count(old):
        current = cover(old)
        rectangle = (0, 0)
        m, n = 0, 0
        for j in range(len(current)):
            for i in range(len(current[j])):
                if _compare(current[j][i], rectangle):
                    rectangle = current[j][i]
                    m, n = i, j
        new[n][m] = rectangle
        for j in range(rectangle[1]):
            for i in range(rectangle[0]):
                old[n+j][m+i] = 0
    return new

def printf (matrix):
    for string in matrix:
        print string
    print ''

def make_dxf (matrix, px_size=1, center=(0, 0), layer='RASTER'):
    if isinstance(matrix, str):
        if matrix = 'header':
            return ['  0', 'SECTION',
                    '  2', 'ENTITIES']
    counter = 0
    stack = 
    size = (px_size*len(matrix[0]),
            px_size*len(matrix))
    start = (center[0] - size[0]/2,
             center[0] + size[1]/2)
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
            current = matrix[j][i]
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
    stack.extend(['  0', 'ENDSEC',
                  '  0', 'EOF'])
    return stack, counter

def split (img, size=(100, 100)):
    stack = []
    if isinstance(size, int):
        size = (size, size)
    num = (img.size[0]//size[0]+1,
           img.size[1]//size[1]+1)
    residue = (img.size[0]%size[0],
               img.size[1]%size[1])
    box = size
    if num == (1, 1):
        return [(0, 0, img)]
    for j in range(num[1]):
        box[0] == size[0]
        if j == num[1]-1:
            box[1] = residue[1]
        for i in range(num[0]):
            if i == num[0]-1:
                box[0] = residue[0]
            stack.append((i, j, img.crop((i*size[0], j*size[1],
                                          i*size[0]+box[0],
                                          i*size[1]+box[1]))
                          ))
    return stack

def do (filename=None):
    if not filename: filename = input('Filename: ')
    img = Image.open(filename+'.png')
    print ' '.join(('File', filename+'.png', 'loaded with',
                    str(img.size[0])+'x'+str(img.size[1]), 'px.'))
    splitted = split(img)
    print 'Image was divided for', len(splitted), 'fragments.'
    full = []
    for rec in splitted:
        prepared, px_counter = mask(rec[2])
        print px_counter[1], 'from', px_counter[0], 'px founded in fragment.'
        print count(prepared), 'px prepared to processing.'
        result = purge(prepared)
        print count(result, ('deep', 'mult')), 'elements processed.'
        full.append((rec[0], rec[1], result))
        dxf_fragm, addition = make_dxf(result, 0.02,
                             (rec[0]*200, rec[1]*200),
                             filename)
    dxf_head = make_dxf('header')
    dxf_body, lines_counter = make_dxf(result, 0.02, (63.5, 63.5), filename)
    dxf_end = make_dxf('end')
    dxf_text = '\n'.join(dxf_head +
                         dxf_body +
                         dxf_end)
    print lines_counter, 'polylines created.'
    output = open(filename+'.dxf', 'w')
    output.write(dxf_text)
    output.close()
    print 'File saved.'

if __name__ == '__main__':
    do()
