## Residual
An extensible package for gathering, collating and displaying analyses of protein sequences.

Note: this project is in the early stages of development

### Running

Residual can be run from within the project directory.

```commandline
python -m residual -f your_sequences.fasta -u your@email.com
```

It can also be run from within code by creating a surveyor instance.

```python
from residual import Surveyor

surv = Surveyor(user_email='your@email.com')

# Load from existing variables.
sequences: list[str] = ['MAGTT', 'MFHLI', 'MREAD'] # Sequence strings
names: list[str] = ['seq_A', 'seq_B', 'seq_C'] # Sequence names (optional)

surv.load_strings(sequences, names=names)
surv.run()

# Or, from a fasta file.
surv.load_fasta('path/to/sequences.fasta')
surv.run()
```

### Adding services

To create a new service, subclass the ```ServiceBaseClass``` from the ```residual.services``` module and implement the abstract methods. To add it to the run, attach the ```register_service``` class decorator. For example:

```python
from residual.protein_sequence import ProteinSequence
from residual.services import ServiceBaseClass, register_service

@register_service
class MyService(ServiceBaseClass):
    
    def run(self, inputs: Iterable[ProteinSequence]) -> list[ProteinSequence]:
        """
        Run the service, attaching new features to the ProteinSequences.
        """
```