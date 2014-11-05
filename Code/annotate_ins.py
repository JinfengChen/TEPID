# usage:
# $ python annotate_ins.py a <accession_name> f <feature>
# where feature is gene or TE
# Finds insertion sites where there are reads at each end, refines insertion coordinates based on position of all reads
# Filters insertions that are at least 1 kb from reference position to reduce false positives
# Creates temporary insertions file to be integrated with split read data to find breakpoints

from sys import argv


def checkArgs(arg1, arg2):
    """
    arg1 is short arg, eg h
    arg2 is long arg, eg host
    """
    args = argv[1:]
    if arg1 in args:
        index = args.index(arg1)+1
        variable = args[index]
        return variable
    elif arg2 in args:
        index = args.index(arg2)+1
        variable = args[index]
        return variable
    else:
        variable = raw_input("\nEnter {arg2}: ".format(arg2=arg2))
        return variable


def get_len(infile):
    """returns number of lines in file and all lines as part of list"""
    lines = []
    for i, l in enumerate(infile):
        lines.append(l)
    return i, lines


def annotate(collapse_file, insertion_file, accession_name, max_len):
    """
    Find insertion coordinates and TE orientation. Adds unique ID: <accession_name>_<number>
    """
    with open(collapse_file, 'r') as infile, open(insertion_file, 'w+') as outfile:
        i, lines = get_len(infile)
        for x in range(i):
            line = lines[x]
            line = line.rsplit()
            chrom = int(line[0])
            start = int(line[1])
            stop = int(line[2])
            strand = line[3]
            te_name = line[4]
            mate = line[10]
            mate = mate.split(',')
            te_reads = line[9]
            te_reads = te_reads.split(',')
            reference = [line[5], line[6], line[7], line[8]]  # reference chrom, start, stop, strand
            l = int(reference[2]) - int(reference[1])
            midpoint = int(reference[1]) + int(0.5*l)
            diff = abs(start - midpoint)
            if chrom != int(reference[0]) or diff > (int(0.5*l)+max_len):  # filter insertions that are at least 3 sd away from reference
                pair = find_next(lines, i, x, chrom, strand, start, stop, te_name)
                if strand != reference[3]:
                    if reference[3] == '+':
                        orientation = '-'
                    else:
                        orientation = '+'
                else:
                    orientation = reference[3]
                if pair is False:
                    pass  # no reads at opposite end, do not include in annotation
                else:
                    pair_start = pair[0]
                    pair_mates = pair[2]
                    next_read_names = pair[1]
                    mate = pair_mates + mate
                    te_reads = next_read_names + te_reads
                    outfile.write('{chr}\t{start}\t{stop}\t{orient}\t{name}\t{ref}\t{reads}\t{mates}\n'.format(chr=chrom,
                                                                                                               start=stop,
                                                                                                               stop=pair_start,
                                                                                                               orient=orientation,
                                                                                                               name=te_name,
                                                                                                               ref='\t'.join(reference),
                                                                                                               reads='|'.join(te_reads),
                                                                                                               mates='|'.join(mate)))
            else:
                pass


# As file is processed top to bottom, sorted by coords, + will come up first. This will avoid identifying each insertion twice (once for each end)
def find_next(lines, i, x, chrom, strand, start, stop, te_name):
    """
    Find next read linked to same TE. Looks in 100 bp window.
    """
    while True:
        line = lines[x+1]
        line = line.rsplit()
        next_chrom = int(line[0])
        next_start = int(line[1])
        next_stop = int(line[2])
        next_strand = line[3]
        next_te_name = line[4]
        next_mate = line[10]
        next_mate = next_mate.split(',')
        next_te_reads = line[9]
        next_te_reads = next_te_reads.split(',')
        if strand != next_strand and te_name == next_te_name and chrom == next_chrom and stop <= next_start:
            return next_start, next_te_reads, next_mate
        elif stop + 100 < next_start:
            return False
        else:
            x += 1
            if x >= i:
                return False

accession = checkArgs('a', 'accession')
f = checkArgs('f', 'feature')
mn = int(checkArgs('m', 'mean'))
std = int(checkArgs('s', 'std'))
mx = (mn + (3*std))

annotate('merged_{feat}_{acc}.bed'.format(acc=accession, feat=f),
         'insertions_{feat}_{acc}_temp.bed'.format(acc=accession, feat=f),
         accession, mx)
