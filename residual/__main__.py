import argparse

from residual.surveyor import Surveyor

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--fasta',
                        help='Path to sequence file, or list of sequences separated by commas.')
    parser.add_argument('-u', '--user_email',
                        help='Email to use as identification when interacting with APIs.')

    args = parser.parse_args()

    sv = Surveyor(args.user_email)
    sv.load_fasta(args.fasta)
    sv.run()

if __name__ == '__main__':
    main()