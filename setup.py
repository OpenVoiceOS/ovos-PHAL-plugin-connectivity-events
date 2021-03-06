#!/usr/bin/env python3
from setuptools import setup

PLUGIN_ENTRY_POINT = 'ovos-phal-connectivity-events=ovos_phal_connectivity_events:ConnectivityEvents'
setup(
    name='ovos-phal-connectivity-events',
    version='0.0.1a1',
    description='A PHAL plugin for mycroft/ovos/neon',
    url='https://github.com/NeonGeckoCom/ovos-PHAL-plugin-connectivity-events',
    author='JarbasAi',
    author_email='jarbasai@mailfence.com',
    license='Apache-2.0',
    packages=['ovos_phal_connectivity_events'],
    install_requires=["ovos-plugin-manager>=0.0.1", "dbus-next"],
    zip_safe=True,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Text Processing :: Linguistic',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    entry_points={'ovos.plugin.phal': PLUGIN_ENTRY_POINT}
)
