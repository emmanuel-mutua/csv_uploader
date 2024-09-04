import pandas as pd
from django.http import JsonResponse
from django.shortcuts import render
from django.db import models, connection
import logging

# Set up logging
logger = logging.getLogger(__name__)

def upload_csv(request):
    if request.method == 'POST':
        try:
            file = request.FILES['csv_file']
            df = pd.read_csv(file)

            # Generate a model dynamically
            model_name = "DynamicModel"  # Change this to a unique name if needed
            fields = {}

            # Map pandas dtypes to Django model fields
            dtype_mapping = {
                'int64': models.IntegerField,
                'float64': models.FloatField,
                'object': models.CharField,
                'bool': models.BooleanField,
                'datetime64[ns]': models.DateTimeField,
            }

            for column in df.columns:
                column_type = str(df[column].dtype)
                model_field = dtype_mapping.get(column_type, models.CharField)  # Default to CharField if type unknown
                fields[column] = model_field(max_length=255) if model_field == models.CharField else model_field()

            # Define a dynamic model with '__module__' attribute
            fields['__module__'] = __name__  # Important to set the __module__ attribute

            # Create the dynamic model
            DynamicModel = type(model_name, (models.Model,), fields)

            # Create the table in the database
            try:
                with connection.schema_editor() as schema_editor:
                    schema_editor.create_model(DynamicModel)
            except Exception as e:
                logger.error(f"Error creating the model: {e}")
                return JsonResponse({'status': 'error', 'message': f'Failed to create model: {str(e)}'}, status=500)

            # Save each row to the dynamic model
            try:
                for index, row in df.iterrows():
                    row_data = DynamicModel(**row.to_dict())
                    row_data.save()
            except Exception as e:
                logger.error(f"Error saving data to the model: {e}")
                return JsonResponse({'status': 'error', 'message': f'Failed to save data: {str(e)}'}, status=500)

            return JsonResponse({'status': 'success', 'message': 'Data saved successfully.'})

        except Exception as e:
            logger.error(f"Unhandled error: {e}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
    return JsonResponse({'status': 'fail', 'message': 'Only POST method allowed'}, status=405)

def upload_form(request):
    return render(request, 'upload.html')
