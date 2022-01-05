import os
import sys
import io
import pandas

def get_env() -> str:
    """Get the environment the app is running in, indicated by the
    :envvar:`PYJIMINY_ENV` environment variable. The default is
    ``'production'``.
    """
    return os.environ.get("PYJIMINY_ENV") or "production"

def convert_pandas_to_str(df: pandas) -> str:
    """Convert stdout of Pandas data frame into str

    Returns:
        str: stdout of pandas data frame
    """

    # Initialize IO stream of string
    with io.StringIO() as f:

        # Switch stdout to f 
        sys.stdout = f
        
        pandas.set_option('display.max_rows', 5)
        pandas.set_option('display.max_columns', 4)
        
        # Output pandas to stdout via print function
        print(df)

        # Get stdout as string
        text = f.getvalue()

        # Revert stdout to default
        sys.stdout = sys.__stdout__   
        
        return text