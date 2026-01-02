"""
Uses pandas library to read a csv list into a pandas.DataFrame object for further processing


"""
import json
import pandas as pd
from pathlib import Path


class AttendanceListException(Exception):
    """ Custom Exception for thing wrong with this data pipeline """


class AttendanceList:
    """
    Read in the attendance list in the forms of a comma separated values.

    Attendance List Headers Standard from Golden Google Form
        -

    Store the data into three main vehicles:
        - Pandas Dataframe
        - Python Dictionary
        - Json Object

    Goal to provide further extensibility if needed.
    """

    def __init__(self) -> None:
        self._df: pd.DataFrame = pd.DataFrame()
        self._attendance_dict: dict[str,...] = dict()
        self._attendance_json: json = None



    def __str__(self):
        pass

    def __repr__(self):
        pass

    def __post_init__(self) -> None:
        if self._df is None:
            raise AttendanceListException("")

        pass

    @property
    def attendance_dataframe(self):
        return self._df


    def _read_attendance_csv_df(self, csv_file: Path) -> pd.DataFrame:
        """ Read in the contents of a csv file into the Attendance Dataframe """
        return self._df.read_csv(filepath_or_buffer=csv_file)

    def _fill_attendance_dict(self) -> dict[str,...]:
        """ Create a """
        pass
        # return self


if __name__ == '__main__':
    FILE: Path = Path("attendance_dec16.csv")
    pass