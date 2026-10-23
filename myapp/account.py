from django import forms
from django.contrib import messages
from django.contrib.auth import get_user_model, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import redirect, render


class ProfileForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ['first_name', 'last_name', 'email']
        labels = {'first_name': 'Ном', 'last_name': 'Насаб', 'email': 'Почтаи электронӣ'}
        widgets = {
            'first_name': forms.TextInput(attrs={'autocomplete': 'given-name'}),
            'last_name': forms.TextInput(attrs={'autocomplete': 'family-name'}),
            'email': forms.EmailInput(attrs={'autocomplete': 'email', 'placeholder': 'name@example.com'}),
        }


@login_required(login_url='login')
def profile(request):
    form = ProfileForm(request.POST if request.method == 'POST' else None, instance=request.user)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Маълумоти шумо нигоҳ дошта шуд.')
        return redirect('profile')
    return render(request, 'profile.html', {'form': form})


@login_required(login_url='login')
def password_change(request):
    form = PasswordChangeForm(request.user, request.POST if request.method == 'POST' else None)
    labels = {'old_password': 'Рамзи ҳозира', 'new_password1': 'Рамзи нав', 'new_password2': 'Такрори рамзи нав'}
    for name, label in labels.items():
        form.fields[name].label = label
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        update_session_auth_hash(request, user)
        messages.success(request, 'Рамзи шумо иваз шуд.')
        return redirect('profile')
    return render(request, 'password_change.html', {'form': form})
