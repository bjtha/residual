import argparse
from residual import Surveyor
from residual.services.loader import load_services

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--fasta',
                        help='Path to sequence file.')
    parser.add_argument('-u', '--user_email',
                        help='Email to use as identification for APIs.')
    parser.add_argument('-o', '--outfile',
                        help='File name to write results to.')

    args = parser.parse_args()
    sv = Surveyor(args.user_email)
    load_services()

    sv.load_fasta(args.fasta)
    sv.run(outfile=args.outfile)

if __name__ == '__main__':
    main()