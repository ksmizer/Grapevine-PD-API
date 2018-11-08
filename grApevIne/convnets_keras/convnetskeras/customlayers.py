import numpy as np
import theano.tensor as T
#from keras.layers.core import  Lambda
from keras.layers import merge, Lambda
from keras.layers.convolutional import Convolution2D
from keras import backend as K

from keras.engine import Layer

def crosschannelnormalization(alpha = 1e-4, k=2, beta=0.75, n=5,**kwargs):
    """
    This is the function used for cross channel normalization in the original Alexnet
    combing the conventkeras and pylearn functions.
    erralves
    """
    def f(X):

        ch, r, c, b = X.shape
        half = n // 2
        sq = T.sqr(X)

        extra_channels = T.alloc(0., ch + 2*half, r, c, b)
        sq = T.set_subtensor(extra_channels[half:half+ch,:,:,:], sq)

        scale = k
        for i in range(n):
            scale += alpha * sq[i:i+ch,:,:,:]

        scale = scale ** beta
        return X / scale

    return Lambda(f, output_shape=lambda input_shape:input_shape,**kwargs)


def splittensor(axis=1, ratio_split=1, id_split=0,**kwargs):
    def f(X):
        div = X.shape[axis] // ratio_split

        if axis == 0:
            output =  X[id_split*div:(id_split+1)*div,:,:,:]
        elif axis == 1:
            output =  X[:, id_split*div:(id_split+1)*div, :, :]
        elif axis == 2:
            output = X[:,:,id_split*div:(id_split+1)*div,:]
        elif axis == 3:
            output = X[:,:,:,id_split*div:(id_split+1)*div]
        else:
            raise ValueError("This axis is not possible")

        return output

    def g(input_shape):
        output_shape=list(input_shape)
        output_shape[axis] = output_shape[axis] // ratio_split
        return tuple(output_shape)

    return Lambda(f,output_shape=lambda input_shape:g(input_shape),**kwargs)




def convolution2Dgroup(n_group, nb_filter, nb_row, nb_col, **kwargs):
    def f(input):
        return merge([
            Convolution2D(nb_filter//n_group,nb_row,nb_col)(
                splittensor(axis=1,
                            ratio_split=n_group,
                            id_split=i)(input))
            for i in range(n_group)
        ],mode='concat',concat_axis=1)

    return f


class Softmax4D(Layer):
    def __init__(self, axis=-1,**kwargs):
        self.axis=axis
        super(Softmax4D, self).__init__(**kwargs)

    def build(self,input_shape):
        pass

    def call(self, x,mask=None):
        e = K.exp(x - K.max(x, axis=self.axis, keepdims=True))
        s = K.sum(e, axis=self.axis, keepdims=True)
        return e / s

    def get_output_shape_for(self, input_shape):
        return input_shape
