import cli
import pytest
from hypothesis import HealthCheck, given, settings, strategies

from package_dev_tools.models import Path
from package_dev_tools.pre_commit.check_coverage import (
    check_coverage,
    update_coverage_shield,
)

suppressed_checks = (HealthCheck.function_scoped_fixture,)


@given(value=strategies.floats(min_value=0, max_value=100))
@settings(suppress_health_check=suppressed_checks)
def test_update_coverage_badge(repository_path: Path, value: float) -> None:
    update_coverage_shield(value)
    readme_path = repository_path / Path.readme.name
    value_str = str(round(value))
    assert value_str in readme_path.text


@pytest.mark.usefixtures("repository_path_with_uncovered_files")
def test_not_covered_files_detected() -> None:
    message = "The following files are not covered by tests:"
    with pytest.raises(Exception, match=message):
        check_coverage()


@pytest.mark.usefixtures("repository_path_with_uncovered_files")
def test_insufficient_coverage_fraction_detected() -> None:
    with pytest.raises(cli.CalledProcessError):
        check_coverage(verify_all_files_tested=False)


@pytest.mark.usefixtures("repository_path")
def test_missing_results_detected() -> None:
    Path(".coverage").unlink()
    message = "No coverage results found."
    with pytest.raises(Exception, match=message):
        check_coverage()


def test_badge_missing_in_readme_indicated(repository_path: Path) -> None:
    (repository_path / Path.readme.name).text = ""
    with pytest.raises(Exception, match="README has no Coverage badge yet."):
        check_coverage(verify_all_files_tested=False)


@pytest.mark.usefixtures("repository_path")
def test_check_coverage_when_changed() -> None:
    verify_coverage_when_changed()


@pytest.mark.usefixtures("repository_path")
def test_check_coverage_when_unchanged() -> None:
    verify_all_files_tested = False
    with pytest.raises(SystemExit):
        check_coverage(verify_all_files_tested=verify_all_files_tested)
    with pytest.raises(SystemExit) as exception:
        check_coverage(verify_all_files_tested=verify_all_files_tested)
    assert exception.value.code == 0  # status code 0 if coverage not changed


def verify_coverage_when_changed() -> None:
    update_coverage_shield(-1)
    with pytest.raises(SystemExit) as exception:
        check_coverage(verify_all_files_tested=False)
    assert exception.value.code == 1


@given(
    value=strategies.floats(min_value=0, max_value=100),
    new_value=strategies.floats(min_value=0, max_value=100),
)
@settings(suppress_health_check=suppressed_checks)
@pytest.mark.usefixtures("repository_path")
def test_readme_content_preserved(value: float, new_value: float) -> None:
    update_coverage_shield(value)
    readme_length = len(Path.readme.text)
    readme_num_lines = len(Path.readme.lines)
    update_coverage_shield(new_value)
    new_readme_length = len(Path.readme.text)
    new_readme_num_lines = len(Path.readme.lines)
    length_change = readme_length - new_readme_length
    value_length_change = len(str(round(value))) - len(str(round(new_value)))
    assert length_change == value_length_change
    assert readme_num_lines == new_readme_num_lines
