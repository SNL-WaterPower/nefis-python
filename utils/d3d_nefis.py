from nefis_utils import *

import numpy as np
import struct
import os, sys

class d3d_data(nef_data):
    #def __init__(self,filebase, ac_type='r', coding=' '):
    #    super(d3d_data,self).__init__(filebase, ac_type=ac_type, coding=coding)

    def get_xyzvel(self):

        # calculate x and y velocity
        #  ***** m,n velocityies go in with ghost cells
        #  ***** u,v, velocities returned with ghost cells trimed

        mvel = self.get_data('U1')
        nvel = self.get_data('V1')
        alpha = self.get_data('ALFAS')
        wvel = self.get_data('WPHY')

        # convert alpha from degrees to radians
        rad = alpha[1:-1, 1:-1]*np.pi/180.0

        if len(mvel.shape) == 3:  # dimensions are i,j,k
            mvel = np.tile(mvel,(1,1,1,1))  # add time dimension of one
            nvel = np.tile(nvel,(1,1,1,1))  # add time dimension of one
            wvel = np.tile(wvel,(1,1,1,1))  # add time dimension of one

        #                 t,   k,  i,   j
        utilde = ( mvel[:, :, :-1, 1:-1] + mvel[:, :, 1:, 1:-1] ) / 2.0
        vtilde = ( nvel[:, :, 1:-1, :-1] + nvel[:, :, 1:-1, 1:] ) / 2.0

        #             t, k,  i,  j
        uvel = utilde[:, :, :-1, :]*np.cos(rad) - vtilde[:, :, :, :-1]*np.sin(rad)
        vvel = utilde[:, :, :-1, :]*np.sin(rad) + vtilde[:, :, :, :-1]*np.cos(rad)

        # trim ghost cells off w velocity
        wvel = wvel[:, :, 1:-1, 1:-1]


        return uvel, vvel, wvel



    def get_zvals(self):

        thick = self.get_data('THICK')
        depth = self.get_data('DP0')
        height = self.get_data('S1')

        imax = len(depth[:,0])
        jmax = len(depth[0,:])
        kmax = len(thick)

        if len(height.shape) == 2:  # dimensions are i,j
            height = np.tile(height,(1,1,1))  # add time dimension of one

        ntimes = len(height[:,0,0])

        total_thick = 0.0
        frac=[]
        # go through thickness from bottom to top
        for val in thick[::-1]:
            # increment the total thickness
            total_thick += val
            # save the running total height fraction
            frac.append(total_thick)
        # reverse the fraction to go from top to bottom
        frac = frac[::-1]

        # trim ghost cells
        height = height[:, 1:-1, 1:-1]  # (t,i,j)
        depth = depth[1:-1, 1:-1]       # (i,j)

        # I "think" this is correct -- TODO check this
        zvals = np.multiply.outer(frac,(height+depth))   #  A[k] * B[t,i,k] = C[k,t,i,j]
        zvals = np.transpose(zvals,(1,0,2,3))      # [t,k,i,j]
        zvals -= np.tile(depth,(ntimes, kmax,1,1))

        return zvals

    def get_cell_locs(self):

        X1 = self.get_data('XZ')  # cell center values
        Y1 = self.get_data('YZ')

        # trim ghost cells off X and Y
        xvals = X1[ 1:-1, 1:-1]
        yvals = Y1[ 1:-1, 1:-1]

        return xvals, yvals

    def get_node_locs(self):

        X1 = self.get_data('XCOR')  # cell center values
        Y1 = self.get_data('YCOR')

        # trim ghost cells off X and Y
        xvals = X1[ 1:-1, 1:-1]
        yvals = Y1[ 1:-1, 1:-1]

        return xvals, yvals


    def get_turb(self):
        # get turbulence data, trim ghost cells

        turb = self.get_data('RTUR1')

        if len(turb.shape) == 4:  # dimensions are i,j,k
            turb = np.tile(turb,(1,1,1,1,1))  # add time dimension of one

        tke = turb [:, 0, 1:, 1:-1, 1:-1]
        tke = tke.clip(0,None)
        eps = turb [:, 1, 1:, 1:-1, 1:-1]

        return tke, eps


    def TreeInit(self,itime=-1):
        from scipy import spatial

        X1 = self.get_data('XZ')  # cell center values
        Y1 = self.get_data('YZ')

        # trim ghost cells off X and Y
        xvals = X1[    1:-1, 1:-1]
        yvals = Y1[    1:-1, 1:-1]

        # TODO maybe add option to search at different times -- currently it's using the last time step only
        zvals = self.get_zvals()[itime,:,:,:]

        kmax=len(zvals[:,0,0])

        # copy x and y values to each k-layer
        xvals2=np.tile(xvals,(kmax,1,1))
        yvals2=np.tile(yvals,(kmax,1,1))

        self.tree = spatial.KDTree(zip(xvals2.ravel(), yvals2.ravel(),zvals.ravel()))
        self.treetime = itime
        self.treeshape = np.shape(zvals)

    def TreeLookup(self,pts,itime=-1):   # single nearest engihbor lookup
        if not hasattr(self,'tree'):
            print 'tree not initialized.  Initializing'
            self.TreeInit(itime)
        if self.treetime != itime:
            print 'tree initialized as different time.  Re-Initializing'
            del self.tree
            self.TreeInit(itime)

        dists, idxs = self.tree.query(pts)

        if len(idxs) > 1:
            ijkdx = [np.unravel_index(ind,self.treeshape) for ind in idxs]
        else:
            ijdx = np.unravel_index(idxs,self.treeshape)

        return dists, ijkdx

    def TreeInterp(self,pts,npts,inpVals,itime=-1):
        if not hasattr(self,'tree'):
            print 'tree not initialized.  Initializing'
            self.TreeInit(itime)
        if self.treetime != itime:
            print 'tree initialized as different time.  Re-Initializing'
            del self.tree
            self.TreeInit(itime)

        for val in inpVals:
            if not np.shape(val) == np.shape(inpVals[0]):
                print 'Lookup arrays must all be the same size for Interpolation'
                return

        dists, idxs = self.tree.query(pts,npts)

        outvals=[]
        for i in range(len(pts)):     # loop through input location points

            if npts > 1:
                total_weight = sum(1.0/dists[i,:])
                weight = 1.0/dists[i,:]/total_weight
                ijkdx = [np.unravel_index(ind,self.treeshape) for ind in idxs[i,:]]

                #            sum ( U or V(i,j,k) * weight)  over number of neightbors
                outvaltmp = [sum([inp[ijk] for ijk in ijkdx]*weight) for inp in inpVals]
                outvals.append(outvaltmp)
            else:
                ijkdx = np.unravel_index(idxs[i],self.treeshape)

                outvaltmp = [inp[ijkdx] for inp in inpVals]
                outvals.append(outvaltmp)

        return map(np.array, zip(*outvals))  # transpose


    def TreeInterp_bar(self,pts,inpVals,itime=-1):

        if not hasattr(self,'tree'):
            print 'tree not initialized.  Initializing'
            self.TreeInit(itime)
        if self.treetime != itime:
            print 'tree initialized as different time.  Re-Initializing'
            del self.tree
            self.TreeInit(itime)

        for val in inpVals:
            if not np.shape(val) == np.shape(inpVals[0]):
                print 'Lookup arrays must all be the same size for Interpolation'
                return

        X1 = self.get_data('XZ')  # cell center values
        Y1 = self.get_data('YZ')

        # trim ghost cells off X and Y
        xvals = X1[    1:-1, 1:-1]
        yvals = Y1[    1:-1, 1:-1]
        zvals = self.get_zvals()[itime,:,:,:]

        imax=len(zvals[0,:,0])
        jmax=len(zvals[0,0,:])
        kmax=len(zvals[:,0,0])

        # copy x and y values to each k-layer
        xvals2=np.tile(xvals,(kmax,1,1))
        yvals2=np.tile(yvals,(kmax,1,1))

        dist, idx = self.tree.query(pts,1)

        outvals=[]
        for i in range(len(pts)):     # loop through input location points

            # first index is the nearest point
            idx1 = np.unravel_index(idx[i],self.treeshape)

            x1 = xvals2[idx1]
            y1 = yvals2[idx1]
            z1 = zvals[idx1]

            # following indices are incremented in i,j,k depending which side the point lies on
            if pts[i,0] > x1:
                idx2 = idx1 + np.array([0,1,0])
            else:
                idx2 = idx1 - np.array([0,1,0])
            if pts[i,1] > y1:
                idx3 = idx1 + np.array([0,0,1])
            else:                         
                idx3 = idx1 - np.array([0,0,1])
            #
            # Very confusing, but k counts downward (negative Z), therefore signs are reversed
            #
            if pts[i,2] < z1:
                idx4 = idx1 + np.array([1,0,0])
            else:                           
                idx4 = idx1 - np.array([1,0,0])

            # if any indices are out of bounds, reverse the direction
            if idx2[1] == -1:
                idx2[1] =  1
            if idx2[1] == imax:
                idx2[1] = imax-2
            if idx3[2] == -1:
                idx3[2] =  1
            if idx3[2] == jmax:
                idx3[2] = jmax-2
            if idx4[0] == -1:
                idx4[0] =  1
            if idx4[0] == kmax:
                idx4[0] = kmax-2
                
            idx2 = tuple(idx2) 
            idx3 = tuple(idx3) 
            idx4 = tuple(idx4) 

            r = pts[i]
            r1 = np.array([xvals2[idx1], yvals2[idx1], zvals[idx1]])
            r2 = np.array([xvals2[idx2], yvals2[idx2], zvals[idx2]])
            r3 = np.array([xvals2[idx3], yvals2[idx3], zvals[idx3]])
            r4 = np.array([xvals2[idx4], yvals2[idx4], zvals[idx4]])

            # start setting up barycentric points
            T = np.array([r1-r4, r2-r4, r3-r4]).transpose()

            Tinv = np.linalg.inv(T)
            weight=np.dot(Tinv,r-r4)

            weight = np.append(weight,1.0-sum(weight))

            outvaltmp = [ np.dot(np.array([inp[idx1],inp[idx2],inp[idx3],inp[idx4]]), weight) for inp in inpVals ]
 
            outvals.append(outvaltmp)

        return map(list, zip(*outvals))  # transpose
