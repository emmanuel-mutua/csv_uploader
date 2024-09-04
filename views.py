# views.py
import pandas as pd
from django.http import JsonResponse
from django.shortcuts import render
from .models import create_dynamic_model, map_column_to_field
from .db import create_table, save_data
import logging

logger = logging.getLogger(__name__)

def upload_csv(request):
    if request.method == 'POST':
        try:
            file = request.FILES['csv_file']
            df = pd.read_csv(file)

            model_name = "DynamicModel" 
            fields = {}

            # Mapping of pandas dtypes to Django model fields
            dtype_mapping = {
                'int64': models.IntegerField, 'float64': models.FloatField, 'object': models.CharField,'bool': models.BooleanField, 'datetime64[ns]': models.DateTimeField,
            }
            # Create fields for the model dynamically
            for column in df.columns:
                fields[column] = map_column_to_field(dtype_mapping, column, df)

            DynamicModel = create_dynamic_model(model_name, fields)
            create_table(DynamicModel)
            save_data(DynamicModel, df)

            return JsonResponse({'status': 'success', 'message': 'Data saved successfully.'})

        except Exception as e:
            logger.error(f"Unhandled error: {e}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
    return JsonResponse({'status': 'fail', 'message': 'Only POST method allowed'}, status=405)

def upload_form(request):
    return render(request, 'upload.html')
