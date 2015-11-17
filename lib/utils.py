__author__ = 'odrulea'

import base64
import json
import numpy as np


def MatrixToBuffer(ndarray):
    """
    In order to get a numpy matrix (array of arrays) into a json serializable form, we have to do a base64 encode
    We will wrap the matrix in an envelope with 3 elements:
    1. type of the ndarray
    2. the entire ndarray encoded as a base64 blob
    3. a list describing the dimensions of the ndarray (2 element list: [rows, cols])

    borrowed from: http://stackoverflow.com/questions/13461945/dumping-2d-python-array-with-json
    :param ndarray:
    :return:
    """
    return [str(ndarray.dtype),base64.b64encode(ndarray),ndarray.shape]

def BufferToMatrix(jsonDump):
    """
    After retrieving the encoded json from the message queue buffer, we need to translate the 3 element json
    back into its original form.
    To do this, use the 0th element to cast correct type, and 2nd element to set correct dimensions.

    borrowed from: http://stackoverflow.com/questions/13461945/dumping-2d-python-array-with-json
    :param jsonDump:
    :return:
    """
    loaded = json.loads(jsonDump)
    dtype = np.dtype(loaded[0])
    arr = np.frombuffer(base64.decodestring(loaded[1]),dtype)
    if len(loaded) > 2:
        return arr.reshape(loaded[2])
    return arr

def matrixToCoords(input, typeSafe=False):
    """
    A matrix of scalar values (i.e. float) is a useful for performing fast calculations on data from many EEG channels.
    However, if you want to plot that data, many charting libraries expect the convention of [x,y] coordinates.
    This function is helpful for performing that conversion.

    Convert an incoming matrix of scalar values to a matrix of [x,y] coordinates
    loop through all points in a matrix and assign [x,y] coordinates based on
    x=row, y=scalar value of original input
    so for example, an input matrix like this:
    [[1 1 0 1]
     [2 1 1 1]
     [1 2 3 1]]

    will become this:
    [[[0, 1] [1, 1] [2, 0] [3, 1]]
     [[0, 2] [1, 1] [2, 1] [3, 1]]
     [[0, 1] [1, 2] [2, 3] [3, 1]]]

    Now any row can be used to plot time series for than channel on an x,y chart.

    Example usage:
    # matrix input
    matrix1 = np.matrix([[1,1,0,1],[2,1,1,1],[1,2,3,1]])
    print matrix1
    print
    foo = matrixToCoords(matrix1)
    print "Matrix input:"
    print foo

    # numpy array input
    np1 = np.array([[1,1,0,1],[2,1,1,1],[1,2,3,1]])
    foo2 = matrixToCoords(np1)
    print "Np.array input:"
    print foo2

    # list input
    list1 = [[1,1,0,1],[2,1,1,1],[1,2,3,1]]
    foo3 = matrixToCoords(list1, True)
    print "List input:"
    print foo3
    """

    # an optional param "typeSafe" can enforce input to be compatible data type, if passing in a raw list
    if(typeSafe):
        if type(input) == list:
            # it's a list, must convert to array
            input = np.array(input)
        if type(input) != np.ndarray and type(input) != np.matrix:
            return None

    # output matrix will be same size as input, but of dtype=list
    # since each value will be a coordinate [x,y]
    (rows,cols) = input.shape
    output = np.ndarray(shape=(rows,cols), dtype=list)

    # initalize row and col counters
    row = col = 0
    # loop through matrix by rows, then cols
    while col < cols:
        row=0
        while row < rows:
            # get the y value of the coordinate by looking at same [row,col]
            # location on the input matrix
            output[row,col] = [col,input[row,col]]
            row=row+1
        col = col+1

    return output