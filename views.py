import pandas as pd
from django.http import JsonResponse
from django.shortcuts import render
from django.db import models, connection

def upload_csv(request):
    if request.method == 'POST':
        try:
            file = request.FILES['csv_file']
            df = pd.read_csv(file)

            # Check for null values
            if df.isnull().values.any():
                return JsonResponse({'status': 'error', 'message': 'CSV file contains null values.'}, status=400)

            # Generate a model dynamically
            model_name = "DynamicModel"  # Change this to a unique name if needed
            fields = {}

            # Map pandas dtypes to Django model fields
            dtype_mapping = {
                'int64': models.IntegerField,
                'float64': models.FloatField,
                'object': models.CharField,
                'bool': models.BooleanField,
                'datetime64': models.DateTimeField,
            }

            for column in df.columns:
                column_type = str(df[column].dtype)
                model_field = dtype_mapping.get(column_type, models.CharField)  # Default to CharField if type unknown
                fields[column] = model_field(max_length=255) if model_field == models.CharField else model_field()

            # Define a dynamic model
            DynamicModel = type(model_name, (models.Model,), fields)

            # Create the table in the database
            with connection.schema_editor() as schema_editor:
                schema_editor.create_model(DynamicModel)

            # Save each row to the dynamic model
            for index, row in df.iterrows():
                row_data = DynamicModel(**row.to_dict())
                row_data.save()

            return JsonResponse({'status': 'success', 'message': 'Data saved successfully.'})

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
    return JsonResponse({'status': 'fail', 'message': 'Only POST method allowed'}, status=405)

def upload_form(request):
    return render(request, 'upload.html')
