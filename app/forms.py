from django import forms

class CalculoNIIF16Form(forms.Form):
    #campos iniciales
    superior_anual = forms.ChoiceField(
    choices=[('si', 'Sí'), ('no', 'No')],
    widget=forms.RadioSelect,
    required=False,
    initial='no',
    )
    valor_razonable = forms.ChoiceField(
        choices=[('si', 'Sí'), ('no', 'No')],
        widget=forms.RadioSelect,
        required=False,
        initial='no',
    )
    tasa_incremental = forms.DecimalField(
        max_digits=5,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={'placeholder': 'Digite el porcentaje %'}),
    )
    vp_vr_superior = forms.ChoiceField(
        choices=[('si', 'Sí'), ('no', 'No')],
        widget=forms.RadioSelect,
        initial='si',
    )
    opcion_compra = forms.ChoiceField(
        choices=[('si', 'Sí'), ('no', 'No')],
        widget=forms.RadioSelect,
        required=False,
    )

    #campos si la pregunta 2 es si
    canon_si = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={'placeholder': 'Es el valor mensual que paga por tener en arriendo el bien'}),
    )
    vlr_razonable_tasa_implicita_si = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={'placeholder': 'Ingrese el valor del inmueble'}),
    )
    tiempo_arrendamiento_si = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={'placeholder': 'El tiempo pactado en el contrato, por arrendar el activo'}),
    )
    tasa_implicita_porcentaje_si = forms.DecimalField(
        max_digits=20,
        decimal_places=10,
        required=False,
        widget=forms.NumberInput,
    )
    depreciacion_periodica_si = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={'placeholder': 'Este valor se calcula automáticamente'}),
    )
    #campos si la pregunta 2 es no
    canon_no = forms.IntegerField(
        required=False,
        widget=forms.NumberInput,
    )
    tasa_implicita_no = forms.DecimalField(
        max_digits=20,
        decimal_places=10,
        required=False,
        widget=forms.NumberInput(attrs={'placeholder': 'Digite el porcentaje %'}),
    )
    tiempo_arrendamiento_no = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={'placeholder': 'El tiempo pactado en el contrato, por arrendar el activo'}),
    )
    valor_presente_no = forms.IntegerField(
        required=False,
        widget=forms.NumberInput,
    )
    depreciacion_periodica_no = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={'placeholder': 'Este valor se calcula automáticamente'}),
    )
    #no es necesario
    tasa_incremental_no = forms.DecimalField(
        max_digits=20,
        decimal_places=10,
        required=False,
        widget=forms.NumberInput(attrs={'placeholder': 'Digite el porcentaje %'}),
    )