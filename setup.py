#!/usr/bin/env python
# coding=utf-8

from setuptools import setup, find_packages

setup(
        name='RLA',
        version="0.6.3",
        description=(
            'RL assistant'
        ),
        packages=[package for package in find_packages()
                        if package.startswith("RLA")],
        platforms=["all"],
        install_requires=[
            "pyyaml",
            "argparse",
            "dill",
            "seaborn",
            "pathspec",
            'tensorboardX', 
            'pysftp',
            'typing',
            'matplotlib>=3.4', # for supylabel and supxlabel
            'omegaconf>=2.0.6',
        ]
    )
