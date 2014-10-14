# Python 2x & PIL required

from PIL import Image
from copy import deepcopy

def mask (img, condition=255):
    matrix = []
    pix = img.load()
    if isinstance(condition, int) and condition < 256:
        condition = (condition,
                     condition,
                     condition)
    for j in range(img.size[1]):
        matrix.append([])
        for i in range(img.size[0]):
            if pix[i,j] == condition:
                matrix[j].append(1)
            else:
                matrix[j].append(0)
    return matrix

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

def purge (matrix):
    def count (matrix):
        summ = 0
        for string in matrix:
            for item in string:
                if item:
                    summ += 1
        print summ
        return summ
    old = matrix
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

def printh (matrix):
    for string in matrix:
        print string
    print ''

def make_dxf (matrix, px_size=1, center=(0, 0)):
    stack = ['  0', 'SECTION',
             '  2', 'ENTITIES']
    size = (px_size*len(matrix[0]),
            px_size*len(matrix))
    start = (center[0] - size[0]/2,
             center[0] + size[1]/2)
    stack.extend(['  0', 'POLYLINE',
                  '  8', 'BOARD',
                  ' 66', '     1',
                  ' 40', '0.0',
                  ' 41', '0.0',
                  ' 70', '     1',
                  '  0', 'VERTEX',
                  '  8', 'BOARD',
                  ' 10', str(start[0]),
                  ' 20', str(start[1]),
                  ' 30', '0.0',
                  '  0', 'VERTEX',
                  '  8', 'BOARD',
                  ' 10', str(start[0]+size[0]),
                  ' 20', str(start[1]),
                  ' 30', '0.0',
                  '  0', 'VERTEX',
                  '  8', 'BOARD',
                  ' 10', str(start[0]+size[0]),
                  ' 20', str(start[1]-size[1]),
                  ' 30', '0.0',
                  '  0', 'VERTEX',
                  '  8', 'BOARD',
                  ' 10', str(start[0]),
                  ' 20', str(start[1]-size[1]),
                  ' 30', '0.0',
                  '  0', 'SEQEND',
                  '  8', 'BOARD'])
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
                    '  8', 'RASTER',
                    ' 66', '      1',
                    ' 40', str(current[1]*px_size),
                    ' 41', str(current[1]*px_size),
                    '  0', 'VERTEX',
                    '  8', 'RASTER',
                    ' 10', str(start[0] + px_size*( i           )),
                    ' 20', str(start[1] - px_size*( j + y_shift )),
                    ' 30', '0.0',
                    '  0', 'VERTEX',
                    '  8', 'RASTER',
                    ' 10', str(start[0] + px_size*( i+current[0])),
                    ' 20', str(start[1] - px_size*( j + y_shift )),
                    ' 30', '0.0',
                    '  0', 'SEQEND',
                    '  8', 'RASTER'
                    ])
    stack.extend(['  0', 'ENDSEC',
                  '  0', 'EOF'])
    return '\n'.join(stack)

name = input('Filename: ')
pix = Image.open(name+'.png')
print 'File loaded.'
prepared = mask(pix)
print 'Image prepared.'
#printf(prepared)
#printf(cover(prepared))
#'''
result = purge(prepared)
print 'image purged.'
#printf(result)
output = open(name+'.dxf', 'w')
output.write(make_dxf(result))
output.close()
print 'Done!'
#'''
