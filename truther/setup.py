
import setuptools
with open('src/truther/version.py') as f:
    for line in f:
        if line.startswith('__version__'):
            _, _, version = line.replace("'", '').split()
            break

setuptools.setup(
    name='truther',
    version=version,
)