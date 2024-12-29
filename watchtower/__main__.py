import sys

def main():
    print('Hello!')

    _, *args = sys.argv
    print(", ".join(args))

if __name__ == '__main__':
    main()