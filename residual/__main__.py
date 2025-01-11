import argparse

from watchtower.watchtower import Watchtower
from watchtower.utils import validate_aa_sequence

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--sequences',
                        help='Path to sequence file, or list of sequences separated by commas.')
    parser.add_argument('-n', '--names',
                        help='(Optional) Names to give the sequences, separated by commas.')

    args = parser.parse_args()
    seq_input = parse_sequence_input(args.sequences)
    if args.names:
        args.names = args.names.split(',')

    wt = Watchtower()
    wt.load_seqs(seq_input, names=args.names)
    wt.run()

def parse_sequence_input(seq_input: str) -> list[str] | str:
    """
    Processes sequences argument into either a single filepath string or a list of sequences.

    :param seq_input: string input from argparse.
    :return: list of sequences or filepath
    """

    input_list = seq_input.split(',')

    try:
        list(validate_aa_sequence(frag) for frag in input_list)
        return input_list
    except ValueError:
        if len(input_list) == 1:
            return input_list[0]
        else:
            raise ValueError(f"Could not parse sequence input '{seq_input}'")

if __name__ == '__main__':
    main()