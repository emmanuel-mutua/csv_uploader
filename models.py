from django.db import models

def create_dynamic_model(model_name, fields):
    fields['__module__'] = __name__  # Add the '__module__' attribute to indicate the model's location
    DynamicModel = type(model_name, (models.Model,), fields)
    return DynamicModel

def map_column_to_field(dtype_mapping, column, df): # Function to map pandas data types to Django model fields
    column_type = str(df[column].dtype)
    model_field = dtype_mapping.get(column_type, models.CharField)  # Default to CharField if type unknown
    return model_field(max_length=255) if model_field == models.CharField else model_field()
