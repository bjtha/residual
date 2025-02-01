class AminoAcidSequence:

    ALLOWED_SYMBOLS = set('ACDEFGHIKLMNPQRSTVWY')  # Valid amino acid symbols

    def __set_name__(self, owner, name):
        self.name = name

    def __set__(self, instance, value):
        self.validate_aa_sequence(value)
        instance.__dict__[self.name] = value

    def __get__(self, instance, owner):
        return instance.__dict__[self.name]

    def validate_aa_sequence(self, seq: str) -> None:
        if disallowed := (set(seq) - self.ALLOWED_SYMBOLS):
            raise ValueError(f'Invalid sequence characters: {" ".join(str(i) for i in disallowed)}')