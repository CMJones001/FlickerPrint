from setuptools import setup
import json

def locked_requirements(section):
    """Look through the 'Pipfile.lock' to fetch requirements by section."""
    with open('Pipfile.lock') as pip_file:
        pipfile_json = json.load(pip_file)

    if section not in pipfile_json:
        print("{0} section missing from Pipfile.lock".format(section))
        return []

    return [package + detail.get('version', "")
            for package, detail in pipfile_json[section].items()]

setup(name='flickerprint',
      version=0.1,
      author='Carl Jones, Jack Law, Thomas Williamson, Fynn Wolf, Endre Tønnessen',
      maintainer='Thomas Williamson',
      python_requires=">=3.9, <3.12",
      install_requires=["numpy",
                        "python-javabridge>=4.0.4",
                        "python-bioformats>=4.1.0",
                        "matplotlib",
                        "scikit-image",
                        "pandas",
                        "seaborn",
                        "h5py>=3.11.1",
                        "tqdm",
                        "argh",
                        "wget",
                        "strictyaml>=1.7.3",
                        "tables>=3.10.1",
                        "opencv-python>=4.10.0.84",
                        "exifread>=3.0.0",
                        "tensorflow>=2.16.2",
                        "shiny==1.2.1",
                        "trieste",
                        "shinyswatch",
                        "jinja2",
                        "cmake"],
      entry_points={
        'console_scripts': ['flickerprint=flickerprint.workflow.manager:main'
        ]}
      )
