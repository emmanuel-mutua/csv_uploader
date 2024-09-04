from django.db import connection, transaction
import logging

logger = logging.getLogger(__name__)

def create_table(DynamicModel):
    try:
        with connection.schema_editor() as schema_editor:
            schema_editor.create_model(DynamicModel)
    except Exception as e:
        logger.error(f"Error creating the model: {e}")
        raise Exception(f"Failed to create model: {str(e)}")

def save_data(DynamicModel, df):
    try:
        # Save each row to the dynamic model
        with transaction.atomic():
            for index, row in df.iterrows():
                row_data = DynamicModel(**row.to_dict())
                row_data.save()
    except Exception as e:
        logger.error(f"Error saving data to the model: {e}")
        raise Exception(f"Failed to save data: {str(e)}")
