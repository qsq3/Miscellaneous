#!usr/bin/env python
#coding=utf-8

import numpy as np  
import math
import disposeWav

pi = math.pi

def MCLT(x):
    M = len(x)/2
    #M = 8192
    h = (2*M)*[0]
    for n in range(M):
        h[n] = -math.sin((2.0*n+1.0)*math.pi/(4.0*M))
        h[2*M-n-1] = h[n]
    
    X = []
    for k in range(M):
        X.append(0)
        for n in range(2*M):
            pc = math.sqrt(2.0/M) * h[n] * math.cos( (2.0*n+1.0+M)*(2.0*k+1)*pi/(4.0*M) )
            ps = math.sqrt(2.0/M) * h[n] * math.sin( (2.0*n+1.0+M)*(2.0*k+1)*pi/(4.0*M) )
            p  = pc + 1j*ps
            X[k] += x[n]*p
    
    return X

def IMCLT(X):
    M = len(X)
    #M = 8192
    h = (2*M)*[0]
    for n in range(M):
        h[n] = -math.sin((2.0*n+1.0)*math.pi/(4.0*M))
        h[2*M-n-1] = h[n]
    
    y = []
    Bc = 1.0/2
    Bs = 1.0-Bc  #Bc+Bs = 1即可
    for n in range(2*M):
        y.append(0)
        for k in range(M):
            pc = math.sqrt(2.0/M) * h[n] * math.cos( (2.0*n+1.0+M)*(2.0*k+1)*pi/(4.0*M) )
            ps = math.sqrt(2.0/M) * h[n] * math.sin( (2.0*n+1.0+M)*(2.0*k+1)*pi/(4.0*M) )
            #p  = pc + 1j*ps
            y[n] += (Bc*X[k].real*pc + Bs*X[k].imag*ps)
    
    return y

def W(M,r):     #Local function: complex exponential
        e = math.e
        w = e ** (-1j*2.0*pi*r/M)
        return w

def FastMCLT(audio):
    # determine subbands, M
    L = len(audio)
    M = L/2

    # normalized FFT of input
    U = []
    for f in np.fft.fft(audio):
        U.append(math.sqrt(1/(2.0*M)) * f)
    
    # compute modulation function 
    c = []
    for i in range(M+1):
        c.append( W(8.0,2*i+1.0) * W(4.0*M,i) )
    
    # modulate U into V
    V = []
    for i in range(M+1):
        V.append( c[i] * U[i])
        
    X = []
    # compute MCLT coefficients 
    for each in range(M):
        X.append( 1j * V[each] + V[each+1] )
    
    return X
    
def FastIMCLT(X):
    # determine subbands, M 
    M = len(X)
    # compute modulation function 
    c = []
    for i in range(M-1):
        k = i+1
        c.append( W(8,2*k+1) * W(4*M,k) )
    
    # allocate vector Y  
    Y = (2*M)*[0]
    # map X into Y
    for j in range(M-1):
        i = j+1
        Y[i] = 1.0/4 * c[j].conjugate() * (X[j] - 1j * X[j+1])
    
    # determine first and last Y values 
    Y[0] = math.sqrt(1.0/8) * (X[0].real + X[0].imag)
    Y[M] = -math.sqrt(1.0/8) * (X[M-1].real + X[M-1].imag)
    # complete vector Y via conjugate symmetry property for the 
    # FFT of a real vector (not needed if the inverse FFT 
    # routine is a "real FFT", which should take only as input 
    # only M+1 coefficients)
    for i in range(M-1):
        Y[i+M+1] = Y[M-i-1].conjugate()
    # inverse normalized FFT to compute the output vector 
    # output of ifft should have zero imaginary part; but 
    # by calling real(.) we remove the small rounding noise 
    # that's present in the imaginary part
    yt = []
    for i in Y:
       yt.append( math.sqrt(2*M) * i )

    y = (np.fft.ifft(yt)).real
    
    return y
    
def test():
    nchannels, sampwidth, framerate, nframes, wave_data, time = disposeWav.read_wave_data("../wavFile/test1.wav")
    x = [4000]*16
    X = MCLT(x)
    y = IMCLT(X)
    print X,"\n\n",y
    X = FastMCLT(x)
    y = FastIMCLT(X)
    print X,"\n\n",y
    
if __name__ == "__main__":
    test()