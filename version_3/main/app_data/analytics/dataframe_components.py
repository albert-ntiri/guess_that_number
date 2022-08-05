"""
The dataframe_components.py module is part of the analytics package.  It consists of a set of classes
that serve as building blocks for the classes in the dataframes.py module.

Classes:
    DFCreator
    DFFormatter
    Dataframe
"""


import pandas as pd



class DFCreator:
    """
    The DFCreator class defines different ways of creating a pandas dataframe.  In this application, dataframes
    are either created from a query, by subsetting another dataframe, or from a pivot table.
    """
    
    def __init__(self, db):
        self._db = db
    
    @staticmethod
    def create_df_from_subset(base_df, condition, cols=None):
        if cols:
            df = base_df.loc[condition, cols].copy()
        else:
            df = base_df[condition].copy()
        
        return df
    
    @staticmethod
    def create_df_from_pivot_table(base_df, index, values, aggfunc):
        df = base_df.pivot_table(index=index, values=values, aggfunc=aggfunc)
        
        return df
    
    def create_df_from_query(self, query, cols):
        data = self._db.run_query(query, fetch='all')
        df = pd.DataFrame(data, columns=cols)
        
        return df



class DFFormatter:
    """
    The DFFormatter class defines different ways of formatting a pandas dataframe and its columns.
    """
    
    @staticmethod
    def add_col(df, new_col, formula, insert=False, index=None):
        if insert:
            df.insert(index, new_col, formula)
        else:
            df[new_col] = df.index.map(formula)
        
        return df
    
    @staticmethod
    def transform_col(df, col, transform_type, datatype=None):
        if transform_type == "date":
            df[col] = pd.to_datetime(df[col])
        elif transform_type == "cast":
            df[col] = df[col].astype(datatype)
        elif transform_type == "convert to seconds":
            df[col] = df[col].dt.total_seconds()
        elif transform_type == "fill na":
            df[col].fillna(0, inplace=True)
        
        return df
    
    @staticmethod
    def format_df(df, format_type, col=None, col_list=None, col_order=None, col_names_dict=None):
        if format_type == "drop null":
            df = df[df[col].notna()].copy()
        elif format_type == "keep null":
            df = df[df[col].isna()].copy()
        elif format_type == "set columns":
            df = df[col_list].copy()
        elif format_type == "reorder columns":
            df = df.iloc[:, col_order]
        elif format_type == "rename columns":
            df.rename(columns=col_names_dict, inplace=True)
        
        return df



class Dataframe:
    """
    The Dataframe class is composed with objects of the DFCreator and DFFormatter classes.  It is the
    base class for creating and formatting pandas dataframes representing historical data from the app.
    It has a method to create a dataframe, which it delegates to its subclasses to implement.  The init
    method runs that method to create the dataframe and saves it as an attribute.
    """
    
    def __init__(self, db, base_df=None, cols=None):
        self._creator = DFCreator(db)
        self._formatter = DFFormatter()
        
        if base_df is not None:
            self._base_df = base_df
        if cols:
            self._cols = cols
        self._df = self._create_df()
    
    def _create_df(self):
        pass