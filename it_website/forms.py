from django import forms

class ContactForm(forms.Form):
    name = forms.CharField(
        min_length=2,
        widget=forms.TextInput(
            attrs={'plaseholder': 'Ваше имя', 'class': 'form-control'}
            )
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'plaseholder': 'Ваше Email', 'class': 'form-control'})
    )
    massage = forms.CharField(
         min_length=10,
         widget = forms.Textarea(
             attrs={'plaseholder': 'Сообщение', 'cols': 30, 'rows': 6, 'class': 'form-control', 'id': "message"}
         )
    )