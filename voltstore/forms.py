from django import forms
from django.contrib.auth.models import User


class LoginForm(forms.Form):
    email = forms.EmailField(
        label='E-mail',
        widget=forms.EmailInput(attrs={'placeholder': 'seu@email.com'})
    )
    senha = forms.CharField(
        label='Senha',
        widget=forms.PasswordInput(attrs={'placeholder': '••••••••'}),
        min_length=6,
    )


class CadastroForm(forms.ModelForm):
    email = forms.EmailField(
        label='E-mail',
        widget=forms.EmailInput(attrs={'placeholder': 'seu@email.com'})
    )
    senha = forms.CharField(
        label='Senha',
        widget=forms.PasswordInput(attrs={'placeholder': 'Mínimo 6 caracteres'}),
        min_length=6,
    )
    confirmar_senha = forms.CharField(
        label='Confirmar senha',
        widget=forms.PasswordInput(attrs={'placeholder': 'Repita a senha'}),
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email']
        labels = {
            'first_name': 'Nome',
            'last_name': 'Sobrenome',
            'username': 'Nome de usuário',
        }
        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': 'Seu nome'}),
            'last_name':  forms.TextInput(attrs={'placeholder': 'Seu sobrenome'}),
            'username':   forms.TextInput(attrs={'placeholder': 'ex: joao123'}),
        }

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Este e-mail já está cadastrado.')
        return email

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('senha') != cleaned.get('confirmar_senha'):
            self.add_error('confirmar_senha', 'As senhas não coincidem.')
        return cleaned


class CheckoutForm(forms.Form):
    nome_completo = forms.CharField(
        label='Nome completo',
        widget=forms.TextInput(attrs={'placeholder': 'Seu nome completo'}),
        max_length=200,
    )
    endereco = forms.CharField(
        label='Endereço',
        widget=forms.TextInput(attrs={'placeholder': 'Rua, número'}),
        max_length=300,
    )
    cidade = forms.CharField(
        label='Cidade',
        widget=forms.TextInput(attrs={'placeholder': 'Sua cidade'}),
        max_length=100,
    )
    estado = forms.CharField(
        label='Estado',
        widget=forms.TextInput(attrs={'placeholder': 'ex: SP'}),
        max_length=2,
    )
    cep = forms.CharField(
        label='CEP',
        widget=forms.TextInput(attrs={'placeholder': '00000-000'}),
        max_length=9,
    )
    frete = forms.ChoiceField(
        label='Frete',
        choices=[
            ('economico', 'Econômico — R$ 20,00'),
            ('expresso',  'Expresso — R$ 40,00'),
            ('retirada',  'Retirar na loja — Grátis'),
        ]
    )

    def clean_cep(self):
        cep = self.cleaned_data['cep'].replace('-', '').replace(' ', '')
        if len(cep) != 8 or not cep.isdigit():
            raise forms.ValidationError('CEP inválido. Use o formato 00000-000.')
        return cep
