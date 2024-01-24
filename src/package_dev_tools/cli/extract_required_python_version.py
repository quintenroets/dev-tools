from package_utils.cli import instantiate_from_cli_args

from package_dev_tools.utils.package import PackageInfo


def entry_point() -> None:
    package_info = instantiate_from_cli_args(PackageInfo)
    print(package_info.required_python_version)
