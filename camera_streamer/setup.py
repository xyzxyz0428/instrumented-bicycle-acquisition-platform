from setuptools import setup

package_name = 'camera_streamer'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Xinyu Zhang',
    maintainer_email='zhangxinyu0428@gmail.com',
    description='Camera acquisition package for the instrumented-bicycle platform',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
        'camera_publisher = camera_streamer.camera_publisher:main',
        ],
    },
)
