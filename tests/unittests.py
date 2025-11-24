import atheris
import sys
import fame_constants
from mining import constants as mining_constants


def fuzz_py_file_extension(data):
    try:
        # Fuzz fame_constants.PY_FILE_EXTENSION
        if data.decode("utf-8") == fame_constants.PY_FILE_EXTENSION:
            pass
    except Exception as e:
        print(f"Bug found in PY_FILE_EXTENSION: {e}")


def fuzz_time_format(data):
    try:
        # Fuzz fame_constants.TIME_FORMAT
        if data.decode("utf-8") == fame_constants.TIME_FORMAT:
            pass
    except Exception as e:
        print(f"Bug found in TIME_FORMAT: {e}")


def fuzz_utf_encoding(data):
    try:
        # Fuzz fame_constants.UTF_ENCODING
        if data.decode("utf-8") == fame_constants.UTF_ENCODING:
            pass
    except Exception as e:
        print(f"Bug found in UTF_ENCODING: {e}")


def fuzz_func_kw(data):
    try:
        # Fuzz mining_constants.FUNC_KW
        if data.decode("utf-8") == mining_constants.FUNC_KW:
            pass
    except Exception as e:
        print(f"Bug found in FUNC_KW: {e}")


def fuzz_logging_kw(data):
    try:
        # Fuzz mining_constants.LOGGING_KW
        if data.decode("utf-8") == mining_constants.LOGGING_KW:
            pass
    except Exception as e:
        print(f"Bug found in LOGGING_KW: {e}")


def main():
    atheris.Setup(sys.argv, atheris.instrument_all())
    atheris.Fuzz(
        lambda data: [
            fuzz_py_file_extension(data),
            fuzz_time_format(data),
            fuzz_utf_encoding(data),
            fuzz_func_kw(data),
            fuzz_logging_kw(data),
        ]
    )


if __name__ == "__main__":
    main()
