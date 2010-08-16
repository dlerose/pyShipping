# coding: utf-8
# 20.7627530098 4903 2018 41.158474403

def packstrip(bin, packages):
    """Creates a Strip which fits into bin.
    
    Returns the Packages to be used in the strip, the dimensions of the strip as a 3-tuple
    and a list of "left over" packages.
    """
    strip = []
    stripsize = 0
    stripx = 0
    stripy = 0
    binsize = bin[0]
    rest = []
    while packages and stripsize <= binsize:
        nextpackage = packages.pop(0)
        if stripsize + nextpackage[0] < binsize:
            stripsize += nextpackage[0]
            strip.append(nextpackage)
            stripx = max([stripx, nextpackage[1]])
            stripy = max([stripy, nextpackage[2]])
        else:
            rest.append(nextpackage)
    return strip, (stripsize, stripx, stripy), sorted(rest+packages)


def packlayer(bin, packages):
    strips = []
    layersize = 0
    layerx = 0
    layery = 0
    binsize = bin[1]
    while packages:
        strip, (sizex, stripsize, sizez), rest = packstrip(bin, packages)
        if layersize + stripsize <= binsize:
            if not strip:
                # we were not able to pack anything
                break
            layersize += stripsize
            layerx = max([sizex, layerx])
            layery = max([sizez, layery])
            strips.extend(strip)
            packages = rest
        else:
            # Next Layer please
            rest = strip + rest
            break
    return strips, (layerx, layersize, layery), sorted(rest+packages)


def packbin(bin, packages):
    packages.sort()
    layers = []
    contentheigth = 0
    contentx = 0
    contenty = 0
    binsize = bin[2]
    while packages:
        layer, (sizex, sizey, layersize), rest = packlayer(bin, packages)
        if contentheigth + layersize <= binsize:
            if not layer:
                # we were not able to pack anything
                break
            contentheigth += layersize
            contentx = max([contentx, sizex])
            contenty = max([contenty, sizey])
            layers.extend(layer)
            packages = rest
        else:
            # Next Bin please
            rest = layer + rest
            break
    return layers, (contentx, contenty, contentheigth), sorted(rest+packages)


def packit(bin, originalpackages):
    packedbins = []
    packages = sorted(originalpackages)
    while packages:
        packagesinbin, (binx, biny, binz), rest = packbin(bin, packages)
        if not packagesinbin:
            # we were not able to pack anything
            break
        packedbins.append(packagesinbin)
        packages = rest
    # we now have a result, try to get a better result by rotating some bins
    
    return packedbins, rest


import itertools
import random

class Timeout(Exception):
    pass


def allpermutations_helper(permuted, todo, maxcounter, callback, bin, bestpack, counter):
    if not todo:
        return counter + callback(bin, permuted, bestpack)
    else:
        others = todo[1:]
        thispackage = todo[0]
        for dimensions in set(itertools.permutations((thispackage[0], thispackage[1], thispackage[2]))):
            thispackage = Package(dimensions, nosort=True)
            if thispackage in bin:
                counter = allpermutations_helper(permuted+[thispackage], others, maxcounter, callback, bin,
                                                 bestpack, counter)
            if counter > maxcounter:
                raise Timeout('more than %d iterations tries' % counter)
        return counter


def trypack(bin, packages, bestpack):
    bins, rest = packit(bin, packages)
    if len(bins) < bestpack['bincount']:
        bestpack['bincount'] = len(bins)
        bestpack['bins'] = bins
        bestpack['rest'] = rest
    if bestpack['bincount'] < 2:
        raise Timeout('optimal solution found')
    return len(packages)


def allpermutations(todo):
    bin = Package("600x400x400")
    random.seed(1)
    random.shuffle(todo)
    bestpack = dict(bincount=len(todo)+1)
    try:
        # First try unpermuted
        trypack(bin, todo, bestpack)
        # now try permutations
        allpermutations_helper([], packages, 1000, trypack, bin, bestpack, 0)
    except Timeout:
        pass
    return bestpack['bins'], bestpack['rest']


from pyshipping.package import Package
import time
fd = open('testdata.txt')
vorher = 0
nachher = 0
start = time.time()
for line in fd:
    packages = [Package(pack) for pack in line.strip().split()]
    if not packages:
        continue
    bins, rest = allpermutations(packages)
    if rest:
        print "invalid data", rest, line
    else:
        #print len(packages), len(bins)
        vorher += len(packages)
        nachher += len(bins)
print time.time() - start,
print vorher, nachher, float(nachher)/vorher*100