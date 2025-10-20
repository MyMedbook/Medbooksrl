# api/serializers/anamnesi.py
from datetime import date
from rest_framework import serializers
from api.models import (
    Status, DislipidemiaType, FumoStatus, ObesitaType,
    DistiroidismoType, DoloreToracicoType, FrequenzaType,
    SincopeType, VerosimileType, SistemaNervosoType,
    OcchioType, OrecchioType, SistemaMuscoloscheletricoType,
    PelleType
)
from api.serializers.base import BaseSerializer as BaseAnamnesisSerializer

# preprocess data for serializers with associated beginning year
def preprocess_insorgenza(data):
    
    if not data.get("anni") and data.get("anno_insorgenza"):
        current_year = date.today().year
        data['anni'] = current_year - data['anno_insorgenza']
    
    return data

# preprocess data for serializers with associated beginning year
def preprocess_fumo(data):
    
    # current_year = date.today().year
    # inizio =  data.get('anno_inizio')
    # interruzione = data.get('anno_interruzione')

    # if inizio and not interruzione:
    #     if not data.get("anni"): 
    #         data['anni'] = current_year - inizio

    # if inizio and interruzione:
    #     if not data.get("anni"):
    #         data['anni'] = interruzione - inizio
    #     if not data.get("anni_smesso"): 
    #         data['anni_smesso'] = current_year - interruzione
    
    return data


# Embedded Document Serializers
class IpertensioneArteriosaSer(serializers.Serializer):
    presente = serializers.BooleanField(required=True)
    anno_insorgenza = serializers.IntegerField(min_value=0, required=False, allow_null=True)
    anni = serializers.IntegerField(min_value=0, required=False, allow_null=True)

    def to_internal_value(self, data):
            
        if data['presente']:
            data = preprocess_insorgenza(data)

        return super().to_internal_value(data)

class DislipidemiaSer(serializers.Serializer):
    tipo = serializers.ChoiceField(choices=[(x.value, x.value) for x in DislipidemiaType])
    anno_insorgenza = serializers.IntegerField(min_value=0, required=False, allow_null=True)
    anni = serializers.IntegerField(min_value=0, required=False, allow_null=True)

    def to_internal_value(self, data):


        if data['tipo'] == DislipidemiaType.NO and data.get('anno_insorgenza'):
            raise serializers.ValidationError(
                "Anno Insorgenza non deve essere inserito se Dislipidemia non è presente."
            )
            
        if not data['tipo'] == DislipidemiaType.NO:
            data = preprocess_insorgenza(data)

        return super().to_internal_value(data)

class DiabeteMellitoSer(serializers.Serializer):
    presente = serializers.BooleanField(required=True)
    anno_insorgenza = serializers.IntegerField(min_value=0, required=False, allow_null=True)
    anni = serializers.IntegerField(min_value=0, required=False, allow_null=True)

    def to_internal_value(self, data):

        if not data.get('presente') and data.get('anno_insorgenza'):
            raise serializers.ValidationError(
                "Anno Insorgenza non deve essere inserito se Diabete Mellito non è presente."
            )
        if data.get('presente'):
            data = preprocess_insorgenza(data)

        return super().to_internal_value(data)

class FumoSer(serializers.Serializer):
    stato = serializers.ChoiceField(choices=[(x.value, x.value) for x in FumoStatus])
    anno_inizio = serializers.IntegerField(min_value=0, required=False, allow_null=True)
    anno_interruzione = serializers.IntegerField(min_value=0, required=False, allow_null=True)
    anni = serializers.IntegerField(min_value=0, required=False, allow_null=True)
    anni_smesso = serializers.IntegerField(min_value=0, required=False, allow_null=True)

    def to_internal_value(self, data):


        if data['stato'] == FumoStatus.NO and data.get('anno_inizio'):
            raise serializers.ValidationError(
                "Anno Inizio non deve essere inserito se il/la paziente non è fumatore."
            )

        if data['stato'] != FumoStatus.PASSATO and data.get('anno_interruzione'):
            raise serializers.ValidationError(
                "Anno Interruzione non deve essere inserito se il/la paziente è ancora fumatore o non lo è mai stato."
            )
        
        data = preprocess_fumo(data)
        return super().to_internal_value(data)

# Main Document Serializers
class FattoriRischioSer(BaseAnamnesisSerializer):
    ipertensione_arteriosa = IpertensioneArteriosaSer()
    dislipidemia = DislipidemiaSer()
    diabete_mellito = DiabeteMellitoSer()
    fumo = FumoSer()
    obesita = serializers.ChoiceField(choices=[(x.value, x.value) for x in ObesitaType])

class MalattiaRenaleCronicaSer(serializers.Serializer):
    presente = serializers.BooleanField(required=True)
    stadio = serializers.IntegerField(min_value=0, required=False)

class SteatosiEpaticaSer(serializers.Serializer):
    presente = serializers.BooleanField(required=True)
    grado = serializers.CharField(required=False)

class AnemiaSer(serializers.Serializer):
    presente = serializers.BooleanField(required=True)
    tipo = serializers.CharField(required=False)

class ComorbiditaSer(BaseAnamnesisSerializer):
    malattia_renale = MalattiaRenaleCronicaSer()
    bpco = serializers.BooleanField()
    steatosi_epatica = SteatosiEpaticaSer()
    anemia = AnemiaSer()
    distiroidismo = serializers.ChoiceField(choices=[(x.value, x.value) for x in DistiroidismoType])

class DoloreToracicoSer(serializers.Serializer):
    presente = serializers.BooleanField(required=True)
    tipo = serializers.ChoiceField(choices=[(x.value, x.value) for x in DoloreToracicoType], required=False)
    frequenza = serializers.ChoiceField(choices=[(x.value, x.value) for x in FrequenzaType], required=False)

class DispneaSer(serializers.Serializer):
    presente = serializers.BooleanField(required=True)
    classe_nyha = serializers.IntegerField(min_value=1, max_value=4, required=False)

class CardiopalmoSer(serializers.Serializer):
    presente = serializers.BooleanField(required=True)
    frequenza = serializers.ChoiceField(choices=[(x.value, x.value) for x in FrequenzaType], required=False)

class SincopeSer(serializers.Serializer):
    tipo = serializers.ChoiceField(choices=[(x.value, x.value) for x in SincopeType])
    verosimile = serializers.ChoiceField(choices=[(x.value, x.value) for x in VerosimileType], required=False)

class AltroSer(serializers.Serializer):
    presente = serializers.BooleanField(required=True)
    descrizione = serializers.CharField(required=False)

class SintomatologiaSer(BaseAnamnesisSerializer):
    dolore_toracico = DoloreToracicoSer()
    dispnea = DispneaSer()
    cardiopalmo = CardiopalmoSer()
    sincope = SincopeSer()
    altro = AltroSer()

class CoinvolgimentoMultisistemicoSer(BaseAnamnesisSerializer):
    sistema_nervoso = serializers.ChoiceField(choices=[(x.value, x.value) for x in SistemaNervosoType])
    occhio = serializers.ChoiceField(choices=[(x.value, x.value) for x in OcchioType])
    orecchio = serializers.ChoiceField(choices=[(x.value, x.value) for x in OrecchioType])
    sistema_muscoloscheletrico = serializers.ChoiceField(choices=[(x.value, x.value) for x in SistemaMuscoloscheletricoType])
    pelle = serializers.ChoiceField(choices=[(x.value, x.value) for x in PelleType])

class TerapiaFarmacologicaSer(BaseAnamnesisSerializer):
    farmaci = serializers.ListField(child=serializers.CharField())

class AnamnesiCompletaSer(serializers.Serializer):
    paziente_id = serializers.IntegerField(required=True)
    operatore_id = serializers.IntegerField(required=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    
    fattori_rischio = FattoriRischioSer(allow_null=True, required=False)
    comorbidita = ComorbiditaSer(allow_null=True, required=False)
    sintomatologia = SintomatologiaSer(allow_null=True, required=False)
    coinvolgimento_multisistemico = CoinvolgimentoMultisistemicoSer(allow_null=True, required=False)
    terapia_farmacologica = TerapiaFarmacologicaSer(allow_null=True, required=False)

    def validate_paziente_id(self, value):
        if value <= 0:
            raise serializers.ValidationError("paziente_id must be positive")
        return value

    def validate_operatore_id(self, value):
        if value <= 0:
            raise serializers.ValidationError("operatore_id must be positive")
        return value