from django import forms
from .models import StockChange

class StockChangeForm(forms.ModelForm):
    class Meta:
        model = StockChange
        fields = ['item', 'change_type', 'quantity', 'source_location', 'dest_location', 'note']
        widgets = {
            'note': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'item': forms.Select(attrs={'class': 'form-select'}),
            'change_type': forms.Select(attrs={'class': 'form-select'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'source_location': forms.Select(attrs={'class': 'form-select'}),
            'dest_location': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['source_location'].help_text = "Required for Outgoing and Internal Move."
        self.fields['dest_location'].help_text = "Required for Incoming and Internal Move."
        self.fields['source_location'].required = False
        self.fields['dest_location'].required = False