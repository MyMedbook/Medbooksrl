# api/views/base.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import NotFound, ValidationError
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class BasePatientView(APIView):
    """Base view for handling patient-related records"""
    model = None
    serializer_class = None

    def validate_paziente_id(self, paziente_id):
        """Validate and convert paziente_id to integer"""
        try:
            pid = int(paziente_id)
            if pid <= 0:
                raise ValidationError("paziente_id must be positive")
            return pid
        except ValueError:
            raise ValidationError("paziente_id must be a valid integer")

    def get_object(self, paziente_id):
        """Get object with validated paziente_id"""
        pid = self.validate_paziente_id(paziente_id)
        try:
            return self.model.objects(paziente_id=pid).first()
        except Exception as e:
            logger.error(f"Error fetching {self.model.__name__}: {str(e)}")
            raise

    def check_exists(self, paziente_id):
        """Check if record exists for patient"""
        return self.model.objects(paziente_id=paziente_id).count() > 0

    def get(self, request, paziente_id):
        """Get record"""
        try:
            instance = self.get_object(paziente_id)
            if not instance:
                raise NotFound(f"{self.model.__name__} not found for patient {paziente_id}")
                
            serializer = self.serializer_class(instance)
            return Response(serializer.data)
        except (ValidationError, NotFound) as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error in GET: {str(e)}")
            return Response(
                {"error": "Internal server error"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def put(self, request, paziente_id):
        """Create or update record"""
        try:
            pid = self.validate_paziente_id(paziente_id)
            instance = self.get_object(pid)
            
            # Prepare data
            data = request.data.copy()
            data['paziente_id'] = pid
            
            if instance:
                # Update existing record
                serializer = self.serializer_class(instance, data=data)
            else:
                # Create new record
                serializer = self.serializer_class(data=data)
                
            if not serializer.is_valid():
                return Response(
                    serializer.errors, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Create or update instance
            if instance:
                for key, value in serializer.validated_data.items():
                    setattr(instance, key, value)
                instance.save()
            else:
                instance = self.model(**serializer.validated_data)
                instance.save()
            
            return Response(
                self.serializer_class(instance).data,
                status=status.HTTP_200_OK if instance else status.HTTP_201_CREATED
            )
            
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error in PUT: {str(e)}")
            return Response(
                {"error": "Internal server error"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )