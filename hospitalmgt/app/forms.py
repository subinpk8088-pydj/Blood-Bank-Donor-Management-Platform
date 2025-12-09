# forms.py
# forms.py
from django import forms
from .models import CustomUser

class DonorForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'phone', 'blood_group']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make fields required
        for field_name, field in self.fields.items():
            field.required = True
            field.widget.attrs.update({
                'class': 'form-control',
                'style': 'width: 100%; padding: 10px; border-radius: 5px; border: 1px solid #ccc;'
            })