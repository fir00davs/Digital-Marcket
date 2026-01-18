from django import forms
from .models import Category,  Delivery, Customer
from django_svg_image_form_field import SvgAndImageFormField
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        exclude = []
        field_classes = {
            'icon': SvgAndImageFormField,
        }


class LoginForm(AuthenticationForm):
    username = forms.CharField(label=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Имя пользователя'

    }))

    password = forms.CharField(label=False, widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Пароль'
    }))


class RegisterForm(UserCreationForm):
    username = forms.CharField(label=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Имя пользователя'
    }))

    password1 = forms.CharField(label=False, widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Создать пароль'
    }))

    password2 = forms.CharField(label=False, widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Подтвердить пароль'
    }))

    first_name = forms.CharField(label=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Ваше имя'
    }))

    last_name = forms.CharField(label=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Ваша фамилия'
    }))

    email = forms.EmailField(label=False, widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Почта'
    }))

    phone_number = forms.CharField(
        label=False,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Номер телефона'
        })
    )

    photo = forms.ImageField(
        label=False,
        required=False,
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control',
        })
    )

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2', 'first_name', 'last_name', 'email', 'phone_number', 'photo')



class DeliveryForm(forms.ModelForm):
    class Meta:
        model = Delivery
        fields = ('region', 'city', 'address', 'comment', 'phone', 'first_name', 'last_name', 'email')
        widgets = {
            'region': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Регион"}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Город"}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Адрес"}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'placeholder': "Коментарии к заказу"}),
            'phone': forms.TelInput(attrs={'class': 'form-control', 'placeholder': "Номер телефона"}),
            'first_name': forms.TelInput(attrs={'class': 'form-control', 'placeholder': "Имя"}),
            'last_name': forms.TelInput(attrs={'class': 'form-control', 'placeholder': "Фамилия"}),
            'email': forms.TelInput(attrs={'class': 'form-control', 'placeholder': "Почта"})
        }


class EditAccountForm(forms.ModelForm):
    username = forms.CharField(label=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Имя пользователя'
    }))

    first_name = forms.CharField(label=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Ваше имя'
    }))

    last_name = forms.CharField(label=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Ваша фамилия'
    }))

    email = forms.EmailField(label=False, widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Почта'
    }))

    # Поля пароля добавлены сюда
    old_password = forms.CharField(
        label=False,
        required=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Текущий пароль'
        })
    )
    new_password1 = forms.CharField(
        label=False,
        required=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Новый пароль'
        })
    )
    new_password2 = forms.CharField(
        label=False,
        required=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Подтвердить пароль'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        new_password1 = cleaned_data.get('new_password1')
        new_password2 = cleaned_data.get('new_password2')

        if new_password1 and new_password1 != new_password2:
            raise forms.ValidationError("Пароли не совпадают")
        if new_password1 and len(new_password1) < 8:
            raise forms.ValidationError("Пароль должен быть не менее 8 символов")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)

        old_password = self.cleaned_data.get('old_password')
        new_password1 = self.cleaned_data.get('new_password1')

        if old_password and new_password1:
            if user.check_password(old_password):
                user.set_password(new_password1)
                if commit:
                    user.save()
            else:
                raise forms.ValidationError("Неверный текущий пароль")

        if commit:
            user.save()
        return user

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email',
                  'old_password', 'new_password1', 'new_password2')


class EditCustomerForm(forms.ModelForm):
    phone_number = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': "Номер телефона"
    }))
    region = forms.CharField(
        label=False,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': "Регион"
        })
    )
    city = forms.CharField(
        label=False,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': "Город"
        })
    )
    address = forms.CharField(
        label=False,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': "Адресс"
        })
    )
    photo = forms.ImageField(
        label=False,
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'placeholder': "Фото профиля"
        })
    )

    class Meta:
        model = Customer
        fields = ('phone_number', 'region', 'city', 'address', 'photo')